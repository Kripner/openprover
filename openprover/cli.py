"""CLI entry point for OpenProver."""

import argparse
import atexit
import json
import re
import signal
import sys
from datetime import datetime
from pathlib import Path

from openprover import __version__
from .budget import Budget, parse_duration
from .llm import CodexClient, HFClient, LLMClient, MistralClient, QuotaExceeded
from .prover import Prover, _use_thinking_as_result, slugify
from . import prompts
from .tui import TUI, HeadlessTUI

SUBCOMMANDS = {"inspect", "fetch-lean-data", "reverify"}

RUN_CONFIG_FILE = "run_config.toml"
PROVIDER_CHOICES = ("claude", "codex", "local", "mistral")
CLAUDE_MODELS = {"sonnet", "opus"}
CLAUDE_REASONING_EFFORTS = {"low", "medium", "high", "max"}
OPENAI_REASONING_EFFORTS = {"none", "minimal", "low", "medium", "high", "xhigh"}
HF_MODEL_MAP = {
    "minimax-m2.5": "MiniMaxAI/MiniMax-M2.5",
}
VLLM_MODELS = set(HF_MODEL_MAP)
MISTRAL_MODEL_MAP = {
    "leanstral": "labs-leanstral-2603",
}
MISTRAL_MODELS = set(MISTRAL_MODEL_MAP)
PROVIDER_DEFAULT_MODELS = {
    "claude": "sonnet",
    "codex": "codex",
    "local": "minimax-m2.5",
    "mistral": "leanstral",
}


def _make_client(provider: str, model_alias: str, archive_dir: Path,
                 reasoning_effort: str | None, *, provider_url: str,
                 answer_reserve: int):
    """Construct an LLM client with consistent requested-model metadata."""
    if provider == "local":
        return HFClient(
            HF_MODEL_MAP[model_alias],
            archive_dir,
            base_url=provider_url,
            answer_reserve=answer_reserve,
            vllm=model_alias in VLLM_MODELS,
            requested_model=model_alias,
        )
    if provider == "codex":
        return CodexClient(
            model_alias,
            archive_dir,
            answer_reserve=answer_reserve,
            reasoning_effort=reasoning_effort,
            requested_model=model_alias,
        )
    if provider == "mistral":
        return MistralClient(
            MISTRAL_MODEL_MAP[model_alias],
            archive_dir,
            answer_reserve=answer_reserve,
            requested_model=model_alias,
        )
    return LLMClient(
        model_alias,
        archive_dir,
        reasoning_effort=reasoning_effort,
        requested_model=model_alias,
    )


def _cli_flag_given(*flags: str) -> bool:
    """Check if any of the given CLI flags were explicitly passed by the user."""
    return any(f in sys.argv for f in flags)


def _parse_version(version: str) -> tuple[int, ...]:
    """Parse dotted numeric version strings like '1.0.1'."""
    parts = []
    for token in version.split("."):
        if not token.isdigit():
            return ()
        parts.append(int(token))
    return tuple(parts)


def _save_run_config(work_dir: Path, *, planner_model: str, worker_model: str,
                     planner_provider: str, worker_provider: str,
                     planner_reasoning_effort: str | None,
                     worker_reasoning_effort: str | None,
                     budget_mode: str, budget_limit: int,
                     conclude_after: float,
                     parallelism: int,
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
    return _load_simple_kv_toml(path)


def _load_simple_kv_toml(path: Path) -> dict | None:
    """Load a simple flat key=value TOML file, or None if not found."""
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
        if cmd == "reverify":
            return _cmd_reverify()

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


def _call_with_optional_no_thinking(client, **kwargs):
    """Call a client, retrying without no_thinking for backends that reject it."""
    try:
        return client.call(**kwargs)
    except TypeError:
        kwargs.pop("no_thinking", None)
        return client.call(**kwargs)


def _run_standalone_verifier(client, *, task_description: str, worker_output: str,
                             label: str, archive_path: Path) -> dict:
    """Run one verifier call outside the main prover loop."""
    prompt = prompts.format_verifier_prompt(task_description, worker_output)
    system_prompt = prompts.verifier_system_prompt()
    resp = _use_thinking_as_result(_call_with_optional_no_thinking(
        client,
        prompt=prompt,
        system_prompt=system_prompt,
        label=label,
        archive_path=archive_path,
    ))

    if resp.get("finish_reason") not in ("length", "max_tokens"):
        return resp

    phase2_prompt = (
        f"{prompt}\n\n---\n\n"
        "Your previous verification was cut off. Based on your analysis so far, "
        "provide your final verdict now.\n\n"
        f"Previous output (last 2000 chars):\n```\n{(resp.get('result') or '')[-2000:]}\n```\n\n"
        "Respond with ONLY one of:\n"
        "VERDICT: CORRECT\n"
        "VERDICT: CRITICALLY FLAWED - <brief reason>\n"
        "VERDICT: NEEDS MINOR FIXES - <brief reason>"
    )
    resp2 = _use_thinking_as_result(_call_with_optional_no_thinking(
        client,
        prompt=phase2_prompt,
        system_prompt=system_prompt,
        label=f"{label}_phase2",
        archive_path=archive_path.parent / f"{archive_path.stem}_phase2.md",
        max_tokens=getattr(client, "answer_reserve", 4000) or 4000,
        no_thinking=True,
    ))
    return {
        **resp2,
        "result": ((resp.get("result") or "") + "\n\n" + (resp2.get("result") or "")).strip(),
        "cost": resp.get("cost", 0.0) + resp2.get("cost", 0.0),
        "duration_ms": resp.get("duration_ms", 0) + resp2.get("duration_ms", 0),
    }


def _run_standalone_repair(client, *, task_description: str, worker_output: str,
                           verifier_feedback: str, label: str,
                           archive_path: Path) -> dict:
    """Ask the model to repair a worker output using archived verifier feedback."""
    prompt = (
        f"# Original Task\n\n{task_description}\n\n"
        f"# Previous Worker Output\n\n{worker_output}\n\n"
        f"# Verifier Feedback\n\n{verifier_feedback or '(no verifier feedback archived)'}\n\n"
        "# Your Task\n\n"
        "Revise the previous worker output so it addresses the verifier feedback as well as possible. "
        "Preserve correct content, remove incorrect claims, and tighten gaps the verifier identified. "
        "Return only the revised worker output, with no preface."
    )
    system_prompt = (
        "You repair mathematical draft outputs using verifier feedback. "
        "Output only the revised worker result."
    )
    return _use_thinking_as_result(_call_with_optional_no_thinking(
        client,
        prompt=prompt,
        system_prompt=system_prompt,
        label=label,
        archive_path=archive_path,
    ))


def _find_reverify_targets(run_dir: Path, *, step_filter: set[int] | None,
                           worker_filter: set[int] | None) -> list[dict]:
    """Collect previously accepted worker outputs suitable for re-verification."""
    targets: list[dict] = []
    steps_dir = run_dir / "steps"
    if not steps_dir.exists():
        return targets

    for step_dir in sorted(
        d for d in steps_dir.iterdir()
        if d.is_dir() and d.name.startswith("step_")
    ):
        step_num = int(step_dir.name.removeprefix("step_"))
        if step_filter and step_num not in step_filter:
            continue
        workers_dir = step_dir / "workers"
        if not workers_dir.exists():
            continue
        for task_path in sorted(workers_dir.glob("task_*.md")):
            worker_idx = int(task_path.stem.removeprefix("task_"))
            if worker_filter and worker_idx not in worker_filter:
                continue
            result_path = workers_dir / f"result_{worker_idx}.md"
            verifier_result_path = workers_dir / f"verifier_result_{worker_idx}.md"
            if not result_path.exists():
                continue
            worker_output = result_path.read_text().strip()
            if not worker_output:
                continue
            if (
                not (workers_dir / f"worker_{worker_idx}_call.md").exists()
                and (workers_dir / "search_call.md").exists()
            ):
                continue
            original_verdict = ""
            if verifier_result_path.exists():
                original_verdict = prompts.extract_verdict(
                    verifier_result_path.read_text()
                )
            if original_verdict != "VERDICT: CORRECT":
                continue
            targets.append({
                "step_num": step_num,
                "worker_idx": worker_idx,
                "task_path": task_path,
                "result_path": result_path,
                "original_verifier_result": verifier_result_path,
                "original_verifier_call": workers_dir / f"verifier_{worker_idx}_call.md",
                "original_verdict": original_verdict,
            })
    return targets


def _encode_int_filter(values: set[int] | None) -> str:
    if not values:
        return ""
    return ",".join(str(v) for v in sorted(values))


def _write_reverify_outputs(out_dir: Path, *, run_dir: Path, provider: str,
                            model: str, reasoning_effort: str | None,
                            repair_broken: bool, step_filter: set[int] | None,
                            worker_filter: set[int] | None,
                            summary_rows: list[dict], target_count: int):
    summary_rows.sort(key=lambda row: (row["step"], row["worker"]))
    summary_md = [
        "# Reverify Summary",
        "",
        f"- Run: `{run_dir}`",
        f"- New verifier: `{provider}` / `{model}` / effort `{reasoning_effort or 'default'}`",
        f"- Repair broken: {'yes' if repair_broken else 'no'}",
        f"- Completed items: {len(summary_rows)} / {target_count}",
        "",
        "| Step | Worker | Original | Repair | New |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in summary_rows:
        original_label = " / ".join(
            part for part in [
                row["original_provider"],
                row["original_requested_model"] or row["original_model"],
                row["original_reasoning_effort"],
                row["original_verdict"],
            ] if part
        ) or "(no archived verifier metadata)"
        new_label = " / ".join(
            part for part in [
                row["new_provider"],
                row["new_requested_model"],
                row["new_reasoning_effort"],
                row["new_verdict"] or "(no verdict)",
            ] if part
        )
        repair_label = "repaired" if row["repaired"] else "-"
        summary_md.append(
            f"| {row['step']} | {row['worker']} | {original_label} | {repair_label} | {new_label} |"
        )
    (out_dir / "summary.md").write_text("\n".join(summary_md) + "\n")
    (out_dir / "summary.json").write_text(json.dumps(summary_rows, indent=2) + "\n")
    (out_dir / "reverify.toml").write_text(
        "\n".join([
            f'timestamp = "{datetime.now().isoformat()}"',
            f'provider = "{provider}"',
            f'model = "{model}"',
            f'reasoning_effort = "{reasoning_effort or ""}"',
            f'repair_broken = {str(repair_broken).lower()}',
            'target_policy = "accepted_only"',
            f'step_filter = "{_encode_int_filter(step_filter)}"',
            f'worker_filter = "{_encode_int_filter(worker_filter)}"',
            f'target_items = {target_count}',
            f'completed_items = {len(summary_rows)}',
        ]) + "\n"
    )


def _load_existing_reverify_rows(out_dir: Path, *, provider: str, model: str,
                                 reasoning_effort: str | None) -> list[dict]:
    rows_by_key: dict[tuple[int, int], dict] = {}
    summary_path = out_dir / "summary.json"
    if summary_path.exists():
        try:
            data = json.loads(summary_path.read_text())
            if isinstance(data, list):
                for row in data:
                    if not isinstance(row, dict):
                        continue
                    step = row.get("step")
                    worker = row.get("worker")
                    if isinstance(step, int) and isinstance(worker, int):
                        rows_by_key[(step, worker)] = row
        except json.JSONDecodeError:
            pass

    for step_dir in sorted(d for d in out_dir.glob("step_*") if d.is_dir()):
        try:
            step_num = int(step_dir.name.removeprefix("step_"))
        except ValueError:
            continue
        for worker_dir in sorted(d for d in step_dir.glob("worker_*") if d.is_dir()):
            try:
                worker_idx = int(worker_dir.name.removeprefix("worker_"))
            except ValueError:
                continue
            key = (step_num, worker_idx)
            if key in rows_by_key:
                continue
            repaired_result_path = worker_dir / "reverify_repaired_result.md"
            result_path = repaired_result_path if repaired_result_path.exists() else (worker_dir / "reverify_result.md")
            if not result_path.exists():
                continue
            original_verdict = ""
            original_result_path = worker_dir / "original_verifier_result.md"
            if original_result_path.exists():
                original_verdict = prompts.extract_verdict(original_result_path.read_text())
            rows_by_key[key] = {
                "step": step_num,
                "worker": worker_idx,
                "original_provider": "",
                "original_requested_model": "",
                "original_model": "",
                "original_reasoning_effort": "",
                "original_verdict": original_verdict,
                "new_provider": provider,
                "new_requested_model": model,
                "new_model": model,
                "new_reasoning_effort": reasoning_effort or "",
                "new_verdict": prompts.extract_verdict(result_path.read_text()),
                "initial_new_verdict": prompts.extract_verdict(
                    (worker_dir / "reverify_result.md").read_text()
                ) if (worker_dir / "reverify_result.md").exists() else "",
                "repaired": repaired_result_path.exists(),
                "path": str(worker_dir),
            }

    return sorted(rows_by_key.values(), key=lambda row: (row["step"], row["worker"]))


def _is_reverify_row_complete(row: dict, *, repair_broken: bool) -> bool:
    """Return whether a resumed reverify row should count as completed."""
    if not repair_broken:
        return True
    if row.get("repaired"):
        return True
    return row.get("new_verdict") == "VERDICT: CORRECT"


def _find_resumable_reverify_dir(run_dir: Path, *, provider: str, model: str,
                                 reasoning_effort: str | None,
                                 repair_broken: bool,
                                 step_filter: set[int] | None,
                                 worker_filter: set[int] | None) -> tuple[Path | None, list[dict]]:
    reverify_root = run_dir / "reverify"
    if not reverify_root.exists():
        return None, []

    expected_step_filter = _encode_int_filter(step_filter)
    expected_worker_filter = _encode_int_filter(worker_filter)
    for out_dir in sorted(
        (d for d in reverify_root.iterdir() if d.is_dir()),
        key=lambda d: d.name,
        reverse=True,
    ):
        saved = _load_simple_kv_toml(out_dir / "reverify.toml") or {}
        if saved.get("provider") != provider:
            continue
        if saved.get("model") != model:
            continue
        if (saved.get("reasoning_effort") or "") != (reasoning_effort or ""):
            continue
        target_policy = saved.get("target_policy")
        if not target_policy:
            target_policy = "accepted_only" if not bool(saved.get("repair_broken", False)) else "legacy_all"
        if target_policy != "accepted_only":
            continue
        saved_repair_broken = bool(saved.get("repair_broken", False))
        if saved_repair_broken != repair_broken:
            # Allow a repair-enabled run to continue from an earlier quick-audit
            # bundle with the same backend/settings.
            if not (repair_broken and not saved_repair_broken):
                continue
        if (saved.get("step_filter") or "") != expected_step_filter:
            continue
        if (saved.get("worker_filter") or "") != expected_worker_filter:
            continue
        rows = _load_existing_reverify_rows(
            out_dir,
            provider=provider,
            model=model,
            reasoning_effort=reasoning_effort,
        )
        return out_dir, rows

    return None, []


def _cmd_reverify():
    parser = argparse.ArgumentParser(
        prog="openprover reverify",
        description="Re-run verification over archived worker outputs from a run",
    )
    parser.add_argument("run_dir", nargs="?", help="Run directory (default: most recent in runs/)")
    parser.add_argument("--provider", choices=PROVIDER_CHOICES, default=None,
                        help="Verifier backend provider (defaults to the run's worker backend)")
    parser.add_argument("--model", default=None,
                        help="Verifier model. Examples: opus, codex, codex:gpt-5.4, gpt-5.4 with --provider codex")
    parser.add_argument("--reasoning-effort", default=None,
                        help="Verifier reasoning effort override")
    parser.add_argument("--provider-url", default="http://localhost:8000",
                        help="Server URL for local OpenAI-compatible models")
    parser.add_argument("--answer-reserve", type=int, default=4096, metavar="TOKENS",
                        help="Tokens reserved for answer after thinking")
    parser.add_argument("--step", action="append", type=int, default=None,
                        help="Only reverify a specific step number (repeatable)")
    parser.add_argument("--worker", action="append", type=int, default=None,
                        help="Only reverify a specific worker index (repeatable)")
    parser.add_argument("--repair-broken", action=argparse.BooleanOptionalAction, default=True,
                        help="If a previously accepted item fails re-verification, try to repair it and then re-verify the repaired text (default: enabled)")
    parser.add_argument("--resume", action=argparse.BooleanOptionalAction, default=True,
                        help="Resume the latest matching reverify bundle if present (default: enabled)")
    args = parser.parse_args(sys.argv[2:])

    run_dir = Path(args.run_dir) if args.run_dir else None
    if run_dir is None:
        from .inspect import find_latest_run
        run_dir = find_latest_run()
    if not run_dir.is_dir():
        parser.error(f"run directory not found: {run_dir}")

    saved = _load_run_config(run_dir) or {}
    if saved:
        saved = _migrate_compatible_run_config(parser, run_dir, saved)
        if not _cli_flag_given("--provider-url"):
            args.provider_url = saved.get("provider_url", args.provider_url)
        if not _cli_flag_given("--answer-reserve"):
            args.answer_reserve = saved.get("answer_reserve", args.answer_reserve)
    provider_input = args.provider or saved.get("worker_provider")
    model_input = args.model or saved.get("worker_model")
    provider_explicit = provider_input is not None
    model_explicit = model_input is not None
    if not provider_explicit and not model_explicit:
        parser.error(
            "could not infer verifier backend from the run; pass --provider/--model explicitly"
        )

    provider, model = _resolve_provider_and_model(
        parser,
        provider=provider_input,
        model=model_input,
        provider_explicit=provider_explicit,
        model_explicit=model_explicit,
        role="verifier",
    )
    reasoning_effort = _resolve_reasoning_effort(
        parser,
        provider=provider,
        reasoning_effort=args.reasoning_effort,
        role="verifier",
    )

    step_filter = set(args.step) if args.step else None
    worker_filter = set(args.worker) if args.worker else None
    targets = _find_reverify_targets(
        run_dir,
        step_filter=step_filter,
        worker_filter=worker_filter,
    )
    if not targets:
        parser.error("no archived worker outputs matched the requested filters")

    summary_rows: list[dict] = []
    if args.resume:
        out_dir, summary_rows = _find_resumable_reverify_dir(
            run_dir,
            provider=provider,
            model=model,
            reasoning_effort=reasoning_effort,
            repair_broken=args.repair_broken,
            step_filter=step_filter,
            worker_filter=worker_filter,
        )
    else:
        out_dir = None
    if out_dir is None:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        out_dir = run_dir / "reverify" / timestamp
        out_dir.mkdir(parents=True, exist_ok=True)

    completed = {
        (row["step"], row["worker"])
        for row in summary_rows
        if _is_reverify_row_complete(row, repair_broken=args.repair_broken)
    }
    remaining_targets = [
        target for target in targets
        if (target["step_num"], target["worker_idx"]) not in completed
    ]

    _write_reverify_outputs(
        out_dir,
        run_dir=run_dir,
        provider=provider,
        model=model,
        reasoning_effort=reasoning_effort,
        repair_broken=args.repair_broken,
        step_filter=step_filter,
        worker_filter=worker_filter,
        summary_rows=summary_rows,
        target_count=len(targets),
    )

    if args.resume and completed:
        print(
            f"  Resuming {out_dir.name}: {len(completed)} completed, "
            f"{len(remaining_targets)} remaining"
        )
    if not remaining_targets:
        print("  Reverify bundle already complete")
        print(f"  summary   → {out_dir / 'summary.md'}")
        print(f"  artifacts → {out_dir}")
        return

    client = _make_client(
        provider,
        model,
        out_dir,
        reasoning_effort,
        provider_url=args.provider_url,
        answer_reserve=args.answer_reserve,
    )

    print(f"  Re-verifying {len(remaining_targets)} archived worker output(s)")
    quota_hit = None
    try:
        from .inspect import _load_call

        for idx, target in enumerate(remaining_targets, start=1):
            step_num = target["step_num"]
            worker_idx = target["worker_idx"]
            item_dir = out_dir / f"step_{step_num:03d}" / f"worker_{worker_idx}"
            item_dir.mkdir(parents=True, exist_ok=True)
            prefix = f"  [{idx}/{len(remaining_targets)}] step {step_num} worker {worker_idx}"
            print(f"{prefix}: verifying original output", flush=True)

            task_text = target["task_path"].read_text()
            worker_text = target["result_path"].read_text()
            (item_dir / "task.md").write_text(task_text)
            (item_dir / "worker_output.md").write_text(worker_text)
            original_verifier_text = ""
            if target["original_verifier_result"].exists():
                original_verifier_text = target["original_verifier_result"].read_text()
                (item_dir / "original_verifier_result.md").write_text(
                    original_verifier_text
                )

            verify_input = worker_text
            repaired = False
            initial_result_text = ""
            repaired_result_text = ""

            resp = _run_standalone_verifier(
                client,
                task_description=task_text,
                worker_output=verify_input,
                label=f"reverify_{step_num}_{worker_idx}",
                archive_path=item_dir / "reverify_call.md",
            )
            initial_result_text = resp.get("result", "")
            (item_dir / "reverify_result.md").write_text(initial_result_text)
            initial_new_verdict = prompts.extract_verdict(initial_result_text)
            final_result_text = initial_result_text
            final_verdict = initial_new_verdict
            print(f"{prefix}: initial verdict {initial_new_verdict or '(no verdict)'}", flush=True)

            if args.repair_broken and initial_new_verdict != "VERDICT: CORRECT":
                print(f"{prefix}: repairing after failed reverify", flush=True)
                repair_resp = _run_standalone_repair(
                    client,
                    task_description=task_text,
                    worker_output=worker_text,
                    verifier_feedback=initial_result_text,
                    label=f"repair_{step_num}_{worker_idx}",
                    archive_path=item_dir / "repair_call.md",
                )
                repaired_text = (repair_resp.get("result") or "").strip()
                if repaired_text:
                    repaired = True
                    (item_dir / "repaired_worker_output.md").write_text(repaired_text)
                    repaired_resp = _run_standalone_verifier(
                        client,
                        task_description=task_text,
                        worker_output=repaired_text,
                        label=f"reverify_repaired_{step_num}_{worker_idx}",
                        archive_path=item_dir / "reverify_repaired_call.md",
                    )
                    repaired_result_text = repaired_resp.get("result", "")
                    (item_dir / "reverify_repaired_result.md").write_text(repaired_result_text)
                    final_result_text = repaired_result_text
                    final_verdict = prompts.extract_verdict(repaired_result_text)
                    print(f"{prefix}: repaired verdict {final_verdict or '(no verdict)'}", flush=True)
                else:
                    print(f"{prefix}: repair produced no output; keeping initial verdict", flush=True)

            original_call = _load_call(target["original_verifier_call"])
            original_verdict = target["original_verdict"]
            summary_rows.append({
                "step": step_num,
                "worker": worker_idx,
                "original_provider": (original_call or {}).get("provider", ""),
                "original_requested_model": (original_call or {}).get("requested_model", ""),
                "original_model": (original_call or {}).get("model", ""),
                "original_reasoning_effort": (original_call or {}).get("reasoning_effort", ""),
                "original_verdict": original_verdict,
                "new_provider": provider,
                "new_requested_model": model,
                "new_model": getattr(client, "model", model),
                "new_reasoning_effort": reasoning_effort or "",
                "initial_new_verdict": initial_new_verdict,
                "new_verdict": final_verdict,
                "repaired": repaired,
                "path": str(item_dir),
            })
            print(f"{prefix}: done", flush=True)
            _write_reverify_outputs(
                out_dir,
                run_dir=run_dir,
                provider=provider,
                model=model,
                reasoning_effort=reasoning_effort,
                repair_broken=args.repair_broken,
                step_filter=step_filter,
                worker_filter=worker_filter,
                summary_rows=summary_rows,
                target_count=len(targets),
            )
    except QuotaExceeded as e:
        quota_hit = e
    finally:
        client.cleanup()

    if quota_hit is not None:
        print("  stopped: provider quota or rate limit reached")
        print(f"  detail    → {quota_hit}")
        print("  rerun the same command to resume from saved progress")
        print(f"  summary   → {out_dir / 'summary.md'}")
        print(f"  artifacts → {out_dir}")
        return

    print(" done")
    print(f"  summary   → {out_dir / 'summary.md'}")
    print(f"  artifacts → {out_dir}")


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
    if model in MISTRAL_MODEL_MAP:
        return "mistral"
    if model == "codex":
        return "codex"
    return None


def _infer_legacy_saved_provider(saved_provider: str | None, saved_model: str) -> str | None:
    """Infer provider for legacy run configs with missing provider fields.

    OpenProver v1.0.0 could persist bare explicit Codex model names like
    ``gpt-5.4`` while omitting the corresponding provider field. We only use
    this fallback when reading saved run configs, not for fresh CLI input.
    """
    if saved_provider:
        return saved_provider
    inferred = _infer_provider_from_model(saved_model)
    if inferred is not None:
        return inferred
    if saved_model:
        return "codex"
    return None


def _provider_guidance(role: str) -> str:
    return (
        f"Use --{role}-provider/--provider or a prefixed model like "
        f"'codex:gpt-5.4'."
    )


def _default_model_for_provider(provider: str) -> str:
    return PROVIDER_DEFAULT_MODELS[provider]


def _migrate_compatible_run_config(parser, work_dir: Path, saved: dict) -> dict:
    """Upgrade known-compatible saved run configs in place.

    We only auto-migrate the explicit 1.0.0 -> 1.0.1 transition, where the
    on-disk run state is compatible and the main format change is added
    provider/reasoning fields in run_config.toml.
    """
    saved_version = saved.get("version", "")
    if not saved_version or saved_version == __version__:
        return saved

    if (_parse_version(saved_version), _parse_version(__version__)) != ((1, 0, 0), (1, 0, 1)):
        parser.error(
            f"Version mismatch: run was created with openprover "
            f"v{saved_version}, but current version is v{__version__}. "
            f"Cannot resume across different versions."
        )

    planner_model = saved.get("planner_model", "")
    worker_model = saved.get("worker_model", "")
    planner_provider = _infer_legacy_saved_provider(saved.get("planner_provider"), planner_model)
    worker_provider = _infer_legacy_saved_provider(saved.get("worker_provider"), worker_model)
    if not planner_provider or not worker_provider:
        parser.error(
            "Cannot migrate this v1.0.0 run automatically because its saved "
            "planner/worker provider cannot be inferred from the legacy model "
            "aliases in run_config.toml."
        )

    _save_run_config(
        work_dir,
        planner_model=planner_model,
        worker_model=worker_model,
        planner_provider=planner_provider,
        worker_provider=worker_provider,
        planner_reasoning_effort=saved.get("planner_reasoning_effort") or None,
        worker_reasoning_effort=saved.get("worker_reasoning_effort") or None,
        budget_mode=saved.get("budget_mode", "time"),
        budget_limit=saved.get("budget_limit", 3600),
        conclude_after=saved.get("conclude_after", 0.99),
        parallelism=saved.get("parallelism", 1),
        isolation=saved.get("isolation", True),
        autonomous=saved.get("autonomous", False),
        mode=saved.get("mode", "prove"),
        lean_project_dir=Path(lp) if (lp := saved.get("lean_project_dir", "")) else None,
        lean_items=saved.get("lean_items", False),
        lean_worker_tools=saved.get("lean_worker_tools", False),
        provider_url=saved.get("provider_url", "http://localhost:8000"),
        answer_reserve=saved.get("answer_reserve", 4096),
        history_budget=saved.get("history_budget", 0),
    )
    return _load_run_config(work_dir) or saved


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

    if provider == "mistral":
        if model not in MISTRAL_MODEL_MAP:
            parser.error(
                f"{role} provider 'mistral' currently requires one of: "
                f"{', '.join(sorted(MISTRAL_MODEL_MAP))}"
            )
        return provider, model

    if model in CLAUDE_MODELS or model in HF_MODEL_MAP or model in MISTRAL_MODEL_MAP:
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
    if provider == "mistral":
        return model
    return model


def _is_tool_capable(provider: str, model: str) -> bool:
    """Whether a worker backend can use lean worker tools."""
    return provider in {"claude", "codex", "mistral"} or model in VLLM_MODELS


def _default_reasoning_effort(provider: str, role: str) -> str | None:
    """Default reasoning effort by backend and role."""
    if provider in {"local", "mistral"}:
        return None
    if role == "verifier":
        return "xhigh" if provider == "codex" else "max"
    return "high"


def _resolve_reasoning_effort(parser, *, provider: str,
                              reasoning_effort: str | None,
                              role: str) -> str | None:
    """Validate and normalize reasoning effort for a backend."""
    if reasoning_effort is None:
        return _default_reasoning_effort(provider, role)
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

    if provider in {"local", "mistral"}:
        parser.error(
            f"{role} provider {provider!r} does not support configurable reasoning effort"
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
                        help="Reasoning effort for both planner and worker. Defaults to high for Claude/Codex; local models ignore it. Claude: low/medium/high/max. Codex: none/minimal/low/medium/high/xhigh.")
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
    parser.add_argument("--answer-reserve", type=int, default=4096, metavar="TOKENS", help="Tokens reserved for answer after thinking (default: 4096)")
    parser.add_argument("--history-budget", type=int, default=0, metavar="CHARS", help="Char budget for planner history (default: auto from model context)")
    parser.add_argument("--effort", choices=["low", "medium", "high", "max"], default=None,
                        help="Deprecated alias for --reasoning-effort on Claude backends")
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

    # ── On resume, load saved config and apply as defaults ──
    if resuming:
        saved = _load_run_config(work_dir)
        if saved:
            saved = _migrate_compatible_run_config(parser, work_dir, saved)
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

    if args.effort is not None and any(
        _cli_flag_given(flag) for flag in (
            "--reasoning-effort",
            "--planner-reasoning-effort",
            "--worker-reasoning-effort",
        )
    ):
        parser.error(
            "cannot combine --effort with --reasoning-effort, "
            "--planner-reasoning-effort, or --worker-reasoning-effort"
        )
    shared_reasoning_effort = args.reasoning_effort or args.effort

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
        reasoning_effort=(args.planner_reasoning_effort or shared_reasoning_effort),
        role="planner",
    )
    worker_reasoning_effort = _resolve_reasoning_effort(
        parser,
        provider=worker_provider,
        reasoning_effort=(args.worker_reasoning_effort or shared_reasoning_effort),
        role="worker",
    )
    verifier_reasoning_effort = _default_reasoning_effort(
        worker_provider,
        "verifier",
    )

    if args.effort is not None:
        non_claude = [
            role for role, provider in (
                ("planner", planner_provider),
                ("worker", worker_provider),
            )
            if provider != "claude"
        ]
        if non_claude:
            parser.error(
                f"--effort is only supported for Claude backends; "
                f"got non-Claude roles: {', '.join(non_claude)}"
            )

    # --on-budget-out is only meaningful for Claude models
    if _cli_flag_given("--on-budget-out"):
        non_claude = [
            role for role, provider in (
                ("planner", planner_provider),
                ("worker", worker_provider),
            )
            if provider != "claude"
        ]
        if non_claude:
            parser.error(
                f"--on-budget-out is only supported for Claude backends; "
                f"got non-Claude roles: {', '.join(non_claude)}"
            )

    # Local OpenAI-compatible and Mistral backends have no web search capability.
    if planner_provider in {"local", "mistral"} and not args.isolation:
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
                "(claude, codex, mistral, or local minimax-m2.5)"
            )
        # Auto-fetch Lean Explore data if not available
        from .lean.data import is_lean_data_available, fetch_lean_data
        if not is_lean_data_available():
            if not args.headless:
                print(" fetching lean data…", end="", flush=True)
            if not fetch_lean_data():
                print("Warning: lean_search will not be available")

    def make_planner_llm(archive_dir):
        return _make_client(
            planner_provider,
            planner_model,
            archive_dir,
            planner_reasoning_effort,
            provider_url=args.provider_url,
            answer_reserve=args.answer_reserve,
        )

    def make_worker_llm(archive_dir):
        return _make_client(
            worker_provider,
            worker_model,
            archive_dir,
            worker_reasoning_effort,
            provider_url=args.provider_url,
            answer_reserve=args.answer_reserve,
        )

    def make_verifier_llm(archive_dir):
        return _make_client(
            worker_provider,
            worker_model,
            archive_dir,
            verifier_reasoning_effort,
            provider_url=args.provider_url,
            answer_reserve=args.answer_reserve,
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
        make_verifier_llm=make_verifier_llm,
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
        prover.verifier_llm.cleanup()

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
        cost = (
            prover.planner_llm.total_cost
            + prover.worker_llm.total_cost
            + prover.verifier_llm.total_cost
        )
        calls = (
            prover.planner_llm.call_count
            + prover.worker_llm.call_count
            + prover.verifier_llm.call_count
        )
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
