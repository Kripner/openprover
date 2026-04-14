"""CLI entry point for OpenProver."""

import argparse
import atexit
import re
import signal
import sys
from datetime import datetime
from pathlib import Path

from openprover import __version__
from .budget import Budget, parse_duration
from .llm import LLMClient, HFClient, MistralClient
from .prover import Prover, slugify
from .tui import TUI, HeadlessTUI

SUBCOMMANDS = {"inspect", "fetch-lean-data"}

RUN_CONFIG_FILE = "run_config.toml"


def _cli_flag_given(*flags: str) -> bool:
    """Check if any of the given CLI flags were explicitly passed by the user."""
    return any(f in sys.argv for f in flags)


def _save_run_config(work_dir: Path, *, planner_model: str, worker_model: str,
                     budget_mode: str, budget_limit: int,
                     conclude_after: float,
                     max_workers: int,
                     isolation: bool, autonomous: bool, mode: str,
                     lean_project_dir: Path | None, lean_items: bool,
                     lean_worker_tools: bool, provider_url: str,
                     answer_reserve: int, history_budget: int):
    """Save run configuration so it can be restored on resume."""
    lines = [
        f'version = "{__version__}"',
        f'planner_model = "{planner_model}"',
        f'worker_model = "{worker_model}"',
        f'budget_mode = "{budget_mode}"',
        f'budget_limit = {budget_limit}',
        f'conclude_after = {conclude_after}',
        f'max_workers = {max_workers}',
        f'isolation = {str(isolation).lower()}',
        f'autonomous = {str(autonomous).lower()}',
        f'mode = "{mode}"',
        f'lean_project_dir = "{lean_project_dir}"' if lean_project_dir else 'lean_project_dir = ""',
        f'lean_items = {str(lean_items).lower()}',
        f'lean_worker_tools = {str(lean_worker_tools).lower()}',
        f'provider_url = "{provider_url}"',
        f'answer_reserve = {answer_reserve}',
        f'history_budget = {history_budget}',
    ]
    (work_dir / RUN_CONFIG_FILE).write_text("\n".join(lines) + "\n")


def _load_run_config(work_dir: Path) -> dict | None:
    """Load saved run configuration, or None if not found."""
    path = work_dir / RUN_CONFIG_FILE
    if not path.exists():
        return None
    text = path.read_text()
    config = {}
    for m in re.finditer(r'^(\w+)\s*=\s*(.+)$', text, re.MULTILINE):
        key, val = m.group(1), m.group(2).strip()
        if val.startswith('"') and val.endswith('"'):
            config[key] = val[1:-1]
        elif val == "true":
            config[key] = True
        elif val == "false":
            config[key] = False
        elif "." in val:
            config[key] = float(val)
        else:
            config[key] = int(val)
    return config


def main():
    if len(sys.argv) >= 2 and sys.argv[1] in SUBCOMMANDS:
        cmd = sys.argv[1]
        if cmd == "inspect":
            return _cmd_inspect()
        if cmd == "fetch-lean-data":
            return _cmd_fetch_lean_data()

    return _cmd_prove()


def _cmd_fetch_lean_data():
    from .lean.data import fetch_lean_data
    fetch_lean_data()


def _cmd_inspect():
    parser = argparse.ArgumentParser(
        prog="openprover inspect",
        description="Browse LLM prompts and outputs from an OpenProver run",
    )
    parser.add_argument("run_dir", nargs="?", help="Run directory (default: most recent in runs/)")
    args = parser.parse_args(sys.argv[2:])

    from .inspect import inspect_main
    inspect_main(args.run_dir)


def _resolve_inputs(parser, args):
    """Resolve theorem/lean-theorem/proof from flags and run_dir files.

    Returns (work_dir, theorem_text, lean_theorem_text, proof_md_text, mode,
             resumed, read_only).
    """
    run_dir = Path(args.run_dir) if args.run_dir else None
    input_flags = args.theorem or args.lean_theorem or args.proof
    read_only = args.read_only

    # Check existing state in run_dir
    has_whiteboard = run_dir and (run_dir / "WHITEBOARD.md").exists()
    has_theorem_file = run_dir and (run_dir / "THEOREM.md").exists()
    has_lean_theorem_file = run_dir and (run_dir / "THEOREM.lean").exists()
    has_proof_file = run_dir and (run_dir / "PROOF.md").exists()

    # Determine if this is a finished or in-progress run
    resuming = bool(has_whiteboard)

    if resuming and input_flags:
        parser.error(
            "cannot use --theorem/--lean-theorem/--proof when resuming an existing run"
        )

    if resuming:
        # Read everything from run_dir
        theorem_text = (run_dir / "THEOREM.md").read_text()
        lean_theorem_text = (run_dir / "THEOREM.lean").read_text() if has_lean_theorem_file else ""
        proof_md_text = (run_dir / "PROOF.md").read_text() if has_proof_file else ""
    else:
        # Fresh start - resolve each input, checking for conflicts

        # Theorem
        if args.theorem and has_theorem_file:
            parser.error(
                f"both --theorem and {run_dir}/THEOREM.md exist - "
                "remove one to resolve the conflict"
            )
        if args.theorem:
            theorem_path = Path(args.theorem)
            if not theorem_path.is_file():
                parser.error(f"--theorem not found: {args.theorem}")
            theorem_text = theorem_path.read_text()
        elif has_theorem_file:
            theorem_text = (run_dir / "THEOREM.md").read_text()
        else:
            parser.error(
                "theorem is required - use --theorem or provide a run dir "
                "containing THEOREM.md"
            )

        # Lean theorem
        if args.lean_theorem and has_lean_theorem_file:
            parser.error(
                f"both --lean-theorem and {run_dir}/THEOREM.lean exist - "
                "remove one to resolve the conflict"
            )
        if args.lean_theorem:
            if not args.lean_theorem.is_file():
                parser.error(f"--lean-theorem not found: {args.lean_theorem}")
            lean_theorem_text = args.lean_theorem.read_text()
        elif has_lean_theorem_file:
            lean_theorem_text = (run_dir / "THEOREM.lean").read_text()
        else:
            lean_theorem_text = ""

        # Proof
        if args.proof and has_proof_file:
            parser.error(
                f"both --proof and {run_dir}/PROOF.md exist - "
                "remove one to resolve the conflict"
            )
        if args.proof:
            if not args.proof.is_file():
                parser.error(f"--proof not found: {args.proof}")
            proof_md_text = args.proof.read_text()
        elif has_proof_file:
            proof_md_text = (run_dir / "PROOF.md").read_text()
        else:
            proof_md_text = ""

    # Determine mode from available inputs
    if lean_theorem_text and proof_md_text:
        mode = "formalize_only"
    elif lean_theorem_text:
        mode = "prove_and_formalize"
    else:
        mode = "prove"

    # Resolve work_dir (auto-generate if not provided)
    if run_dir:
        work_dir = run_dir
    else:
        first_line = theorem_text.strip().split("\n")[0][:40]
        slug = slugify(first_line) or "theorem"
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        work_dir = Path("runs") / f"{slug}-{timestamp}"
        # Avoid collisions when multiple runs start in the same second
        counter = 1
        while work_dir.exists():
            counter += 1
            work_dir = Path("runs") / f"{slug}-{timestamp}-{counter}"

    return work_dir, theorem_text, lean_theorem_text, proof_md_text, mode, resuming, read_only


def _is_finished(work_dir: Path, mode: str) -> bool:
    """Check if a run is already finished (has discussion or proof)."""
    has_discussion = (work_dir / "DISCUSSION.md").exists()
    has_proof_md = (work_dir / "PROOF.md").exists()
    has_proof_lean = (work_dir / "PROOF.lean").exists()
    if mode == "formalize_only":
        return has_proof_lean or has_discussion
    elif mode == "prove_and_formalize":
        return (has_proof_md and has_proof_lean) or has_discussion
    else:
        return has_proof_md or has_discussion


def _cmd_prove():
    parser = argparse.ArgumentParser(
        prog="openprover",
        description="Theorem prover powered by language models",
    )
    model_choices = ["sonnet", "opus", "minimax-m2.5", "leanstral"]
    parser.add_argument("run_dir", nargs="?", help="Working directory (resumes if it contains an existing run)")
    parser.add_argument("--theorem", metavar="FILE", help="Path to theorem statement file (.md)")
    parser.add_argument("--model", default="sonnet", choices=model_choices, help="Model to use for both planner and worker (default: sonnet)")
    parser.add_argument("--planner-model", choices=model_choices, default=None, help="Override model for planner (defaults to --model)")
    parser.add_argument("--worker-model", choices=model_choices, default=None, help="Override model for worker (defaults to --model)")
    parser.add_argument("--provider-url", default="http://localhost:8000", help="Server URL for local models (default: http://localhost:8000)")
    budget_group = parser.add_mutually_exclusive_group()
    budget_group.add_argument("--max-tokens", type=int, default=None, metavar="N", help="Output token budget (mutually exclusive with --max-time)")
    budget_group.add_argument("--max-time", type=str, default=None, metavar="DURATION", help="Wall-clock time budget, e.g. '30m', '2h' (default: 4h)")
    parser.add_argument("--conclude-after", type=float, default=0.99, metavar="RATIO", help="Fraction of budget that triggers conclusion (0.9-1.0, default: 0.99)")
    parser.add_argument("--autonomous", action="store_true", help="Start in autonomous mode (default: interactive)")
    parser.add_argument("--read-only", action="store_true", help="Inspect run without resuming")
    parser.add_argument("--isolation", action=argparse.BooleanOptionalAction, default=True, help="Disable web searches (no literature_search action)")
    parser.add_argument("-P", "--max-workers", type=int, default=1, help="Max parallel workers per spawn step (default: 1)")
    parser.add_argument("--answer-reserve", type=int, default=4096, metavar="TOKENS", help="Tokens reserved for answer after thinking (default: 4096)")
    parser.add_argument("--history-budget", type=int, default=0, metavar="CHARS", help="Char budget for planner history (default: auto from model context)")
    parser.add_argument("--effort", choices=["low", "medium", "high", "max"], default=None,
                        help="Claude reasoning effort level (default: max for opus, high for others; Claude models only)")
    parser.add_argument("--on-budget-out", choices=["backoff", "exit"], default="exit",
                        help="Action when spending/rate limit hit: backoff = exponential retry, exit = stop immediately (default: exit; Claude models only)")
    parser.add_argument("--on-rate-limited", choices=["backoff", "exit"], default="backoff",
                        help="Action on HTTP 429: backoff = exponential retry, exit = stop immediately (default: backoff)")
    parser.add_argument("--headless", action="store_true", help="Non-interactive mode (logs to stdout, errors to stderr)")
    parser.add_argument("--verbose", action="store_true", help="Show full LLM responses")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    # Lean verification
    parser.add_argument("--lean-project", type=Path, metavar="DIR",
                        help="Path to Lean project with lakefile (enables formal verification)")
    parser.add_argument("--lean-theorem", type=Path, metavar="FILE",
                        help="Path to THEOREM.lean file (requires --lean-project)")
    parser.add_argument("--proof", type=Path, metavar="FILE",
                        help="Path to existing PROOF.md (formalize-only mode, requires --lean-theorem)")
    parser.add_argument("--lean-items", action=argparse.BooleanOptionalAction, default=None,
                        help="Allow saving .lean items to the repo (auto-enabled with --lean-project)")
    parser.add_argument("--lean-worker-tools", action=argparse.BooleanOptionalAction, default=None,
                        help="Enable worker tool calls (lean_verify, lean_search) via MCP/vLLM (auto-enabled with --lean-project + capable worker)")
    parser.add_argument("--repl-dir", type=Path, metavar="DIR",
                        help="Path to lean-repl directory (reserved for future use)")

    args = parser.parse_args()

    # Positional arg: file → --theorem, directory → --run-dir
    if args.run_dir and not args.theorem:
        p = Path(args.run_dir)
        if p.is_file():
            args.theorem = args.run_dir
            args.run_dir = None
        elif not p.exists():
            # Non-existent path: create as new run directory
            p.mkdir(parents=True, exist_ok=True)

    if not args.run_dir and not args.theorem:
        parser.error("provide a run directory or --theorem to start a new run")

    # ── Resolve inputs ──────────────────────────────────────────

    (work_dir, theorem_text, lean_theorem_text, proof_md_text,
     mode, resuming, read_only) = _resolve_inputs(parser, args)

    # Map short model names to backend-specific model IDs
    HF_MODEL_MAP = {
        "minimax-m2.5": "MiniMaxAI/MiniMax-M2.5",
    }
    MISTRAL_MODEL_MAP = {
        "leanstral": "labs-leanstral-2603",
    }
    VLLM_MODELS = {"minimax-m2.5"}  # served via vLLM (standard OpenAI API)
    MISTRAL_MODELS = {"leanstral"}  # Mistral Conversations API
    CLAUDE_MODELS = {"sonnet", "opus"}
    TOOL_CAPABLE_MODELS = VLLM_MODELS | CLAUDE_MODELS | MISTRAL_MODELS

    # ── On resume, load saved config and apply as defaults ──
    if resuming:
        saved = _load_run_config(work_dir)
        if saved:
            saved_version = saved.get("version", "")
            if saved_version and saved_version != __version__:
                parser.error(
                    f"Version mismatch: run was created with openprover "
                    f"v{saved_version}, but current version is v{__version__}. "
                    f"Cannot resume across different versions."
                )
            # Restore settings from saved config; CLI flags override
            if not args.planner_model and not _cli_flag_given("--model"):
                args.model = saved.get("planner_model", args.model)
            if not args.planner_model:
                args.planner_model = saved.get("planner_model")
            if not args.worker_model:
                args.worker_model = saved.get("worker_model")
            if not _cli_flag_given("--max-tokens", "--max-time"):
                args.max_tokens = saved.get("budget_limit") if saved.get("budget_mode") == "tokens" else None
                args.max_time = None
                args._saved_budget_mode = saved.get("budget_mode", "time")
                args._saved_budget_limit = saved.get("budget_limit", 3600)
            if not _cli_flag_given("--conclude-after"):
                args.conclude_after = saved.get("conclude_after", args.conclude_after)
            if not _cli_flag_given("-P", "--max-workers"):
                args.max_workers = saved.get("max_workers", args.max_workers)
            if not _cli_flag_given("--isolation", "--no-isolation"):
                args.isolation = saved.get("isolation", args.isolation)
            if not _cli_flag_given("--autonomous"):
                args.autonomous = saved.get("autonomous", args.autonomous)
            if not _cli_flag_given("--lean-project"):
                lp = saved.get("lean_project_dir", "")
                if lp:
                    args.lean_project = Path(lp)
            if not _cli_flag_given("--lean-items", "--no-lean-items"):
                args.lean_items = saved.get("lean_items", args.lean_items)
            if not _cli_flag_given("--lean-worker-tools", "--no-lean-worker-tools"):
                args.lean_worker_tools = saved.get("lean_worker_tools", args.lean_worker_tools)
            if not _cli_flag_given("--provider-url"):
                args.provider_url = saved.get("provider_url", args.provider_url)
            if not _cli_flag_given("--answer-reserve"):
                args.answer_reserve = saved.get("answer_reserve", args.answer_reserve)
            if not _cli_flag_given("--history-budget"):
                args.history_budget = saved.get("history_budget", args.history_budget)

    # Lean flag validation (for fresh starts with explicit flags)
    if not resuming:
        if args.lean_theorem and not args.lean_project:
            parser.error("--lean-theorem requires --lean-project")
        if args.proof and not lean_theorem_text:
            parser.error("--proof requires a Lean theorem (--lean-theorem or THEOREM.lean in run dir)")
        if args.lean_project and not args.lean_project.is_dir():
            parser.error(f"--lean-project not found: {args.lean_project}")

    # Finished runs always enter inspect mode
    finished = resuming and _is_finished(work_dir, mode)
    inspect_mode = finished or read_only

    # Resolve --lean-items default
    if args.lean_items is None:
        args.lean_items = args.lean_project is not None
    if args.lean_items and not args.lean_project:
        parser.error("--lean-items requires --lean-project (verification needs a Lean project)")

    # Resolve effective planner/worker models
    planner_model = args.planner_model or args.model
    worker_model = args.worker_model or args.model

    # Validate and resolve --effort
    effort_given = _cli_flag_given("--effort")
    if effort_given:
        non_claude = [m for m in (planner_model, worker_model) if m not in CLAUDE_MODELS]
        if non_claude:
            parser.error(
                f"--effort is only supported for Claude models (sonnet, opus); "
                f"got: {', '.join(non_claude)}"
            )
        effective_effort = args.effort
    else:
        # Auto-default: highest level for the models in use
        claude_models_used = [m for m in (planner_model, worker_model) if m in CLAUDE_MODELS]
        if claude_models_used:
            effective_effort = "max" if any(m == "opus" for m in claude_models_used) else "high"
        else:
            effective_effort = None

    # --on-budget-out is only meaningful for Claude models
    if _cli_flag_given("--on-budget-out"):
        non_claude = [m for m in (planner_model, worker_model) if m not in CLAUDE_MODELS]
        if non_claude:
            parser.error(
                f"--on-budget-out is only supported for Claude models (sonnet, opus); "
                f"got: {', '.join(non_claude)}"
            )

    # Non-Claude models have no web search capability - force isolation
    non_claude_models = {"minimax-m2.5", "leanstral"}
    if planner_model in non_claude_models and not args.isolation:
        args.isolation = True

    if args.headless:
        args.autonomous = True
        tui = HeadlessTUI()
    else:
        tui = TUI()

    # Show early status so the user sees something immediately
    if not args.headless:
        label = "Resuming" if resuming else "Starting"
        _model_hint = planner_model if planner_model == worker_model else f"{planner_model}/{worker_model}"
        print(f"  {label} openprover ({_model_hint}) ...", end="", flush=True)

    # Resolve --lean-worker-tools default
    if args.lean_worker_tools is None:
        args.lean_worker_tools = (args.lean_project is not None and worker_model in TOOL_CAPABLE_MODELS)
    if args.lean_worker_tools:
        if not args.lean_project:
            parser.error("--lean-worker-tools requires --lean-project")
        if worker_model not in TOOL_CAPABLE_MODELS:
            parser.error("--lean-worker-tools requires a tool-capable worker model (sonnet, opus, minimax-m2.5, or leanstral)")
        # Auto-fetch Lean Explore data if not available
        from .lean.data import is_lean_data_available, fetch_lean_data
        if not is_lean_data_available():
            if not args.headless:
                print(" fetching lean data…", end="", flush=True)
            if not fetch_lean_data():
                print("Warning: lean_search will not be available")

    def _make_client(model_alias, archive_dir):
        if model_alias in MISTRAL_MODEL_MAP:
            return MistralClient(MISTRAL_MODEL_MAP[model_alias], archive_dir,
                                 answer_reserve=args.answer_reserve)
        if model_alias in HF_MODEL_MAP:
            return HFClient(HF_MODEL_MAP[model_alias], archive_dir,
                            base_url=args.provider_url, answer_reserve=args.answer_reserve,
                            vllm=model_alias in VLLM_MODELS)
        return LLMClient(model_alias, archive_dir, effort=effective_effort)

    def make_planner_llm(archive_dir):
        return _make_client(planner_model, archive_dir)

    def make_worker_llm(archive_dir):
        return _make_client(worker_model, archive_dir)

    MODEL_DISPLAY = {"sonnet": "sonnet 4.6", "opus": "opus 4.6", "leanstral": "leanstral"}
    _p = MODEL_DISPLAY.get(planner_model, planner_model)
    _w = MODEL_DISPLAY.get(worker_model, worker_model)
    model_label = _p if planner_model == worker_model else f"{_p}/{_w}"

    # ── Resolve budget ──────────────────────────────────────────
    if not (0.9 <= args.conclude_after <= 1.0):
        parser.error("--conclude-after must be between 0.9 and 1.0")

    if args.max_tokens is not None:
        budget_mode, budget_limit = "tokens", args.max_tokens
    elif args.max_time is not None:
        budget_mode, budget_limit = "time", parse_duration(args.max_time)
    elif hasattr(args, '_saved_budget_mode'):
        # Resumed without explicit budget flags - use saved config
        budget_mode = args._saved_budget_mode
        budget_limit = args._saved_budget_limit
    else:
        budget_mode, budget_limit = "time", parse_duration("4h")

    budget = Budget(
        mode=budget_mode,
        limit=budget_limit,
        conclude_after=args.conclude_after,
    )

    # Save config on fresh start
    if not resuming:
        work_dir.mkdir(parents=True, exist_ok=True)
        _save_run_config(
            work_dir,
            planner_model=planner_model,
            worker_model=worker_model,
            budget_mode=budget_mode,
            budget_limit=budget_limit,
            conclude_after=args.conclude_after,
            max_workers=args.max_workers,
            isolation=args.isolation,
            autonomous=args.autonomous,
            mode=mode,
            lean_project_dir=args.lean_project,
            lean_items=args.lean_items,
            lean_worker_tools=args.lean_worker_tools,
            provider_url=args.provider_url,
            answer_reserve=args.answer_reserve,
            history_budget=args.history_budget,
        )

    prover = Prover(
        work_dir=work_dir,
        theorem_text=theorem_text,
        mode=mode,
        make_llm=make_planner_llm,
        model_name=model_label,
        budget=budget,
        autonomous=args.autonomous,
        verbose=args.verbose,
        tui=tui,
        isolation=args.isolation,
        max_workers=args.max_workers,
        lean_project_dir=args.lean_project,
        lean_theorem_text=lean_theorem_text,
        proof_md_text=proof_md_text,
        resumed=resuming and not inspect_mode,
        make_worker_llm=make_worker_llm,
        lean_items=args.lean_items,
        lean_worker_tools=args.lean_worker_tools,
        history_budget=args.history_budget,
        on_budget_out=args.on_budget_out,
        on_rate_limited=args.on_rate_limited,
    )

    # Clear the early status line before TUI takes over
    if not args.headless:
        print("\r\033[K", end="", flush=True)

    # Inspect mode: browse history without running steps
    if inspect_mode:
        try:
            prover.inspect()
        finally:
            tui.cleanup()
            print(f"  {prover.work_dir}")
        return

    # Ensure LLM subprocesses (and their MCP servers) are killed on exit
    def _cleanup_llm_procs():
        prover.planner_llm.cleanup()
        prover.worker_llm.cleanup()

    atexit.register(_cleanup_llm_procs)

    # SIGTERM: clean up and exit (default SIGTERM would skip atexit)
    def handle_sigterm(signum, frame):
        _cleanup_llm_procs()
        sys.exit(1)

    signal.signal(signal.SIGTERM, handle_sigterm)

    # ctrl+c handling: TUI calls directly from bg thread; SIGINT for headless
    def handle_sigint(signum, frame):
        prover.request_interrupt()

    signal.signal(signal.SIGINT, handle_sigint)
    tui._ctrl_c_cb = prover.request_interrupt

    try:
        prover.run()
    finally:
        cost = prover.planner_llm.total_cost + prover.worker_llm.total_cost
        calls = prover.planner_llm.call_count + prover.worker_llm.call_count
        tui.cleanup()
        has_md = (prover.work_dir / "PROOF.md").exists()
        has_lean = (prover.work_dir / "PROOF.lean").exists()
        if prover.mode == "prove":
            has_proof = has_md
        elif prover.mode == "formalize_only":
            has_proof = has_lean
        else:  # prove_and_formalize
            has_proof = has_md and has_lean
        from .budget import _fmt_tokens
        tok_str = _fmt_tokens(prover.budget.total_output_tokens)
        print(f"  {calls} calls · ${cost:.4f} · {tok_str} output tokens")
        if has_md:
            print(f"  PROOF.md  → {prover.work_dir / 'PROOF.md'}")
        if has_lean:
            print(f"  PROOF.lean → {prover.work_dir / 'PROOF.lean'}")
        print(f"  {prover.work_dir}")
        if args.headless:
            if has_proof:
                print("[result] proved")
            elif prover._spending_limit_hit:
                print("[result] rate_limited")
            else:
                print("[result] not_proved")
