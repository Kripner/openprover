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
from .llm import CodexClient, HFClient, LLMClient
from .prover import Prover, slugify
from .tui import TUI, HeadlessTUI

SUBCOMMANDS = {"inspect", "fetch-lean-data"}

RUN_CONFIG_FILE = "run_config.toml"
PROVIDER_CHOICES = ("claude", "codex", "local")
CLAUDE_MODELS = {"sonnet", "opus"}
CLAUDE_REASONING_EFFORTS = {"low", "medium", "high", "max"}
OPENAI_REASONING_EFFORTS = {"none", "minimal", "low", "medium", "high", "xhigh"}
HF_MODEL_MAP = {
    "minimax-m2.5": "MiniMaxAI/MiniMax-M2.5",
}
VLLM_MODELS = set(HF_MODEL_MAP)
PROVIDER_DEFAULT_MODELS = {
    "claude": "sonnet",
    "codex": "codex",
    "local": "minimax-m2.5",
}


def _cli_flag_given(*flags: str) -> bool:
    """Check if any of the given CLI flags were explicitly passed by the user."""
    return any(f in sys.argv for f in flags)


def _save_run_config(work_dir: Path, *, planner_model: str, worker_model: str,
                     planner_provider: str, worker_provider: str,
                     planner_reasoning_effort: str | None,
                     worker_reasoning_effort: str | None,
                     budget_mode: str, budget_limit: int,
                     conclude_after: float,
                     parallelism: int, give_up_ratio: float,
                     isolation: bool, autonomous: bool, mode: str,
                     lean_project_dir: Path | None, lean_items: bool,
                     lean_worker_tools: bool, provider_url: str,
                     answer_reserve: int, history_budget: int):
    """Save run configuration so it can be restored on resume."""
    lines = [
        f'version = "{__version__}"',
        f'planner_model = "{planner_model}"',
        f'worker_model = "{worker_model}"',
        f'planner_provider = "{planner_provider}"',
        f'worker_provider = "{worker_provider}"',
        f'planner_reasoning_effort = "{planner_reasoning_effort or ""}"',
        f'worker_reasoning_effort = "{worker_reasoning_effort or ""}"',
        f'budget_mode = "{budget_mode}"',
        f'budget_limit = {budget_limit}',
        f'conclude_after = {conclude_after}',
        f'parallelism = {parallelism}',
        f'give_up_ratio = {give_up_ratio}',
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


def _restore_saved_provider_model_args(args, saved: dict):
    """Restore saved provider/model settings unless CLI flags override them."""
    # Provider/model restoration is intentionally coupled: if the user
    # overrides either side on resume, leave both unset so downstream
    # resolution can choose a coherent pair for the new backend. The
    # shared --model/--provider flags intentionally trigger this for both
    # planner and worker roles, since they are shorthand for "re-resolve
    # the backend/model pair everywhere unless a per-role flag says
    # otherwise".
    if not _cli_flag_given("--planner-model", "--model",
                           "--planner-provider", "--provider"):
        args.planner_model = saved.get("planner_model", args.planner_model)
    if not _cli_flag_given("--worker-model", "--model",
                           "--worker-provider", "--provider"):
        args.worker_model = saved.get("worker_model", args.worker_model)
    if not _cli_flag_given("--planner-provider", "--provider",
                           "--planner-model", "--model"):
        args.planner_provider = saved.get("planner_provider", args.planner_provider)
    if not _cli_flag_given("--worker-provider", "--provider",
                           "--worker-model", "--model"):
        args.worker_provider = saved.get("worker_provider", args.worker_provider)


def _restore_saved_reasoning_effort_args(args, saved: dict):
    """Restore saved reasoning effort unless CLI/backend selection overrides it."""
    if not _cli_flag_given("--planner-reasoning-effort", "--reasoning-effort",
                           "--planner-model", "--model",
                           "--planner-provider", "--provider"):
        args.planner_reasoning_effort = (
            saved.get("planner_reasoning_effort") or args.planner_reasoning_effort
        )
    if not _cli_flag_given("--worker-reasoning-effort", "--reasoning-effort",
                           "--worker-model", "--model",
                           "--worker-provider", "--provider"):
        args.worker_reasoning_effort = (
            saved.get("worker_reasoning_effort") or args.worker_reasoning_effort
        )


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


def _split_provider_model_spec(model: str) -> tuple[str | None, str]:
    """Support shorthand like `codex:gpt-5.4` or `codex/gpt-5.4`."""
    for sep in (":", "/"):
        if sep not in model:
            continue
        provider, rest = model.split(sep, 1)
        if provider in PROVIDER_CHOICES and rest:
            return provider, rest
    return None, model


def _infer_provider_from_model(model: str) -> str | None:
    """Infer provider from legacy built-in model aliases."""
    if model in CLAUDE_MODELS:
        return "claude"
    if model in HF_MODEL_MAP:
        return "local"
    if model == "codex":
        return "codex"
    return None


def _provider_guidance(role: str) -> str:
    return (
        f"Use --{role}-provider/--provider or a prefixed model like "
        f"'codex:gpt-5.4'."
    )


def _default_model_for_provider(provider: str) -> str:
    return PROVIDER_DEFAULT_MODELS[provider]


def _resolve_provider_and_model(parser, *, provider: str | None,
                                model: str | None,
                                provider_explicit: bool,
                                model_explicit: bool,
                                role: str) -> tuple[str, str]:
    """Resolve provider/model pair for planner or worker."""
    if not model_explicit:
        if provider_explicit and provider is not None:
            return provider, _default_model_for_provider(provider)
        return "claude", _default_model_for_provider("claude")

    if not model:
        parser.error(
            f"{role} model cannot be empty. {_provider_guidance(role)}"
        )

    inline_provider, inline_model = _split_provider_model_spec(model)
    if provider and inline_provider and provider != inline_provider:
        parser.error(
            f"conflicting {role} provider/model settings: provider={provider!r} "
            f"but {role} model {model!r} encodes provider {inline_provider!r}"
        )
    provider = provider or inline_provider or _infer_provider_from_model(inline_model)
    if provider is None:
        parser.error(
            f"cannot infer provider for {role} model {inline_model!r}. "
            f"{_provider_guidance(role)}"
        )
    model = inline_model

    if provider == "claude":
        if model not in CLAUDE_MODELS:
            parser.error(
                f"{role} provider 'claude' requires one of: "
                f"{', '.join(sorted(CLAUDE_MODELS))}"
            )
        return provider, model

    if provider == "local":
        if model not in HF_MODEL_MAP:
            parser.error(
                f"{role} provider 'local' currently requires one of: "
                f"{', '.join(sorted(HF_MODEL_MAP))}"
            )
        return provider, model

    if model in CLAUDE_MODELS or model in HF_MODEL_MAP:
        parser.error(
            f"{role} provider 'codex' requires an actual Codex model name "
            f"(for example 'gpt-5.4') or bare 'codex' for the CLI default, "
            f"not the built-in alias {model!r}"
        )

    # Codex accepts any explicit model name; bare 'codex' means CLI default.
    return provider, model


def _display_model(provider: str, model: str) -> str:
    """Human-readable label for status/UI."""
    if provider == "claude":
        return model
    if provider == "codex":
        return "codex cli" if model == "codex" else f"codex {model}"
    return model


def _is_tool_capable(provider: str, model: str) -> bool:
    """Whether a worker backend can use lean worker tools."""
    return provider in {"claude", "codex"} or model in VLLM_MODELS


def _resolve_reasoning_effort(parser, *, provider: str,
                              reasoning_effort: str | None,
                              role: str) -> str | None:
    """Validate and normalize reasoning effort for a backend."""
    if reasoning_effort is None:
        return None
    effort = reasoning_effort.strip().lower()
    if not effort:
        parser.error(f"{role} reasoning effort cannot be empty")

    if provider == "claude":
        if effort not in CLAUDE_REASONING_EFFORTS:
            parser.error(
                f"{role} provider 'claude' requires one of: "
                f"{', '.join(sorted(CLAUDE_REASONING_EFFORTS))}"
            )
        return effort

    if provider == "local":
        parser.error(
            f"{role} provider 'local' does not support reasoning effort"
        )

    if effort not in OPENAI_REASONING_EFFORTS:
        parser.error(
            f"{role} provider 'codex' expects a reasoning effort like: "
            f"{', '.join(sorted(OPENAI_REASONING_EFFORTS))}"
        )
    return effort


def _cmd_prove():
    parser = argparse.ArgumentParser(
        prog="openprover",
        description="Theorem prover powered by language models",
    )
    parser.add_argument("run_dir", nargs="?", help="Working directory (resumes if it contains an existing run)")
    parser.add_argument("--theorem", metavar="FILE", help="Path to theorem statement file (.md)")
    parser.add_argument("--provider", choices=PROVIDER_CHOICES, default=None,
                        help="Backend provider for both planner and worker (default: infer from --model)")
    parser.add_argument("--planner-provider", choices=PROVIDER_CHOICES, default=None,
                        help="Override provider for planner (defaults to --provider)")
    parser.add_argument("--worker-provider", choices=PROVIDER_CHOICES, default=None,
                        help="Override provider for worker (defaults to --provider)")
    parser.add_argument("--model", default=None,
                        help="Model for both planner and worker. Examples: sonnet, minimax-m2.5, codex, codex:gpt-5.4, gpt-5.4 with --provider codex")
    parser.add_argument("--planner-model", default=None,
                        help="Override model for planner (defaults to --model)")
    parser.add_argument("--worker-model", default=None,
                        help="Override model for worker (defaults to --model)")
    parser.add_argument("--reasoning-effort", default=None,
                        help="Reasoning effort for both planner and worker. Claude: low/medium/high/max. Codex: none/minimal/low/medium/high/xhigh.")
    parser.add_argument("--planner-reasoning-effort", default=None,
                        help="Override reasoning effort for planner")
    parser.add_argument("--worker-reasoning-effort", default=None,
                        help="Override reasoning effort for worker")
    parser.add_argument("--provider-url", default="http://localhost:8000", help="Server URL for local OpenAI-compatible models (default: http://localhost:8000)")
    budget_group = parser.add_mutually_exclusive_group()
    budget_group.add_argument("--max-tokens", type=int, default=None, metavar="N", help="Output token budget (mutually exclusive with --max-time)")
    budget_group.add_argument("--max-time", type=str, default=None, metavar="DURATION", help="Wall-clock time budget, e.g. '30m', '2h' (default: 4h)")
    parser.add_argument("--conclude-after", type=float, default=0.99, metavar="RATIO", help="Fraction of budget that triggers conclusion (0.9-1.0, default: 0.99)")
    parser.add_argument("--autonomous", action="store_true", help="Start in autonomous mode (default: interactive)")
    parser.add_argument("--read-only", action="store_true", help="Inspect run without resuming")
    parser.add_argument("--isolation", action=argparse.BooleanOptionalAction, default=True, help="Disable web searches (no literature_search action)")
    parser.add_argument("-P", "--parallelism", type=int, default=1, help="Max parallel workers per spawn step (default: 1)")
    parser.add_argument("--give-up-after", type=float, default=0.5, metavar="RATIO", help="Fraction of budget before give_up action is allowed (default: 0.5)")
    parser.add_argument("--answer-reserve", type=int, default=4096, metavar="TOKENS", help="Tokens reserved for answer after thinking (default: 4096)")
    parser.add_argument("--history-budget", type=int, default=0, metavar="CHARS", help="Char budget for planner history (default: auto from model context)")
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
            _restore_saved_provider_model_args(args, saved)
            _restore_saved_reasoning_effort_args(args, saved)
            if not _cli_flag_given("--max-tokens", "--max-time"):
                args.max_tokens = saved.get("budget_limit") if saved.get("budget_mode") == "tokens" else None
                args.max_time = None
                args._saved_budget_mode = saved.get("budget_mode", "time")
                args._saved_budget_limit = saved.get("budget_limit", 3600)
            if not _cli_flag_given("--conclude-after"):
                args.conclude_after = saved.get("conclude_after", args.conclude_after)
            if not _cli_flag_given("-P", "--parallelism"):
                args.parallelism = saved.get("parallelism", args.parallelism)
            if not _cli_flag_given("--give-up-after"):
                args.give_up_after = saved.get("give_up_ratio", args.give_up_after)
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

    # Resolve effective planner/worker providers and models
    planner_provider, planner_model = _resolve_provider_and_model(
        parser,
        provider=args.planner_provider or args.provider,
        provider_explicit=(args.planner_provider is not None or args.provider is not None),
        model=args.planner_model or args.model,
        model_explicit=(args.planner_model is not None or args.model is not None),
        role="planner",
    )
    worker_provider, worker_model = _resolve_provider_and_model(
        parser,
        provider=args.worker_provider or args.provider,
        provider_explicit=(args.worker_provider is not None or args.provider is not None),
        model=args.worker_model or args.model,
        model_explicit=(args.worker_model is not None or args.model is not None),
        role="worker",
    )
    planner_reasoning_effort = _resolve_reasoning_effort(
        parser,
        provider=planner_provider,
        reasoning_effort=(args.planner_reasoning_effort or args.reasoning_effort),
        role="planner",
    )
    worker_reasoning_effort = _resolve_reasoning_effort(
        parser,
        provider=worker_provider,
        reasoning_effort=(args.worker_reasoning_effort or args.reasoning_effort),
        role="worker",
    )

    # Local HTTP-backed models have no web search capability - force isolation
    if planner_provider == "local" and not args.isolation:
        args.isolation = True

    if args.headless:
        args.autonomous = True
        tui = HeadlessTUI()
    else:
        tui = TUI()

    # Show early status so the user sees something immediately
    if not args.headless:
        label = "Resuming" if resuming else "Starting"
        _p = _display_model(planner_provider, planner_model)
        _w = _display_model(worker_provider, worker_model)
        _model_hint = _p if (_p == _w and planner_provider == worker_provider) else f"{_p}/{_w}"
        print(f"  {label} openprover ({_model_hint}) ...", end="", flush=True)

    # Resolve --lean-worker-tools default
    if args.lean_worker_tools is None:
        args.lean_worker_tools = (
            args.lean_project is not None
            and _is_tool_capable(worker_provider, worker_model)
        )
    if args.lean_worker_tools:
        if not args.lean_project:
            parser.error("--lean-worker-tools requires --lean-project")
        if not _is_tool_capable(worker_provider, worker_model):
            parser.error(
                "--lean-worker-tools requires a tool-capable worker backend "
                "(claude, codex, or local minimax-m2.5)"
            )
        # Auto-fetch Lean Explore data if not available
        from .lean.data import is_lean_data_available, fetch_lean_data
        if not is_lean_data_available():
            if not args.headless:
                print(" fetching lean data…", end="", flush=True)
            if not fetch_lean_data():
                print("Warning: lean_search will not be available")

    def _make_client(provider, model_alias, archive_dir, reasoning_effort):
        if provider == "local":
            return HFClient(HF_MODEL_MAP[model_alias], archive_dir,
                            base_url=args.provider_url, answer_reserve=args.answer_reserve,
                            vllm=model_alias in VLLM_MODELS)
        if provider == "codex":
            return CodexClient(model_alias, archive_dir,
                               answer_reserve=args.answer_reserve,
                               reasoning_effort=reasoning_effort)
        return LLMClient(model_alias, archive_dir,
                         reasoning_effort=reasoning_effort)

    def make_planner_llm(archive_dir):
        return _make_client(
            planner_provider,
            planner_model,
            archive_dir,
            planner_reasoning_effort,
        )

    def make_worker_llm(archive_dir):
        return _make_client(
            worker_provider,
            worker_model,
            archive_dir,
            worker_reasoning_effort,
        )

    _p = _display_model(planner_provider, planner_model)
    _w = _display_model(worker_provider, worker_model)
    model_label = _p if (_p == _w and planner_provider == worker_provider) else f"{_p}/{_w}"

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
        give_up_after=args.give_up_after,
    )

    # Save config on fresh start
    if not resuming:
        work_dir.mkdir(parents=True, exist_ok=True)
        _save_run_config(
            work_dir,
            planner_model=planner_model,
            worker_model=worker_model,
            planner_provider=planner_provider,
            worker_provider=worker_provider,
            planner_reasoning_effort=planner_reasoning_effort,
            worker_reasoning_effort=worker_reasoning_effort,
            budget_mode=budget_mode,
            budget_limit=budget_limit,
            conclude_after=args.conclude_after,
            parallelism=args.parallelism,
            give_up_ratio=args.give_up_after,
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
        parallelism=args.parallelism,
        lean_project_dir=args.lean_project,
        lean_theorem_text=lean_theorem_text,
        proof_md_text=proof_md_text,
        resumed=resuming and not inspect_mode,
        make_worker_llm=make_worker_llm,
        lean_items=args.lean_items,
        lean_worker_tools=args.lean_worker_tools,
        history_budget=args.history_budget,
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
        has_proof = ((prover.work_dir / "PROOF.md").exists()
                     or (prover.work_dir / "PROOF.lean").exists())
        from .budget import _fmt_tokens
        tok_str = _fmt_tokens(prover.budget.total_output_tokens)
        print(f"  {calls} calls · ${cost:.4f} · {tok_str} output tokens")
        if (prover.work_dir / "PROOF.md").exists():
            print(f"  PROOF.md  → {prover.work_dir / 'PROOF.md'}")
        if (prover.work_dir / "PROOF.lean").exists():
            print(f"  PROOF.lean → {prover.work_dir / 'PROOF.lean'}")
        print(f"  {prover.work_dir}")
        if args.headless:
            print(f"[result] {'proved' if has_proof else 'not_proved'}")
