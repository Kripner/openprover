#!/usr/bin/env python3
"""Benchmark openprover (or baseline) against MiniF2F problems."""

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

VALID_URL = "https://raw.githubusercontent.com/google-deepmind/miniF2F/refs/heads/main/MiniF2F/Valid.lean"
TEST_URL = "https://raw.githubusercontent.com/google-deepmind/miniF2F/refs/heads/main/MiniF2F/Test.lean"

CLAUDE_MODELS = {"sonnet", "opus"}
RATE_LIMIT_WAIT = 600  # seconds to wait before retrying after rate limit

# Preamble that every extracted theorem file needs.
LEAN_PREAMBLE = """\
import MiniF2F.ProblemImports

open scoped Real
open scoped Nat
open scoped Topology
open scoped Polynomial

"""


# ── Helpers ──────────────────────────────────────────────────────────

def _check_tool(name: str) -> None:
    if shutil.which(name) is None:
        print(f"Error: '{name}' not found on PATH.", file=sys.stderr)
        sys.exit(1)


def _format_time(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.0f}s"
    m, s = divmod(int(seconds), 60)
    return f"{m}m{s:02d}s"


def _parse_duration(s: str) -> float:
    """Parse '10m', '2h', '1h30m' into seconds."""
    total = 0.0
    for match in re.finditer(r"(\d+(?:\.\d+)?)\s*([hms])", s):
        val, unit = float(match.group(1)), match.group(2)
        total += val * {"h": 3600, "m": 60, "s": 1}[unit]
    if total == 0:
        total = float(s)
    return total


# ── Theorem parsing ──────────────────────────────────────────────────

def _fetch_lean_file(split: str) -> str:
    url = VALID_URL if split == "valid" else TEST_URL
    print(f"  Fetching {split.capitalize()}.lean from GitHub...")
    with urllib.request.urlopen(url, timeout=30) as resp:
        return resp.read().decode()


def _parse_theorems(lean_source: str) -> dict[str, dict[str, str]]:
    """Parse theorem names, informal statements, and formal code.

    Returns {name: {"informal": ..., "formal": ...}}.
    """
    theorems: dict[str, dict[str, str]] = {}
    pattern = re.compile(
        r"(?:(?P<comment>/--.*?-/)\s*)?"
        r"^(?P<theorem>theorem\s+(?P<name>\S+).*?:=\s*by\s*\n\s*sorry)",
        re.MULTILINE | re.DOTALL,
    )
    for m in pattern.finditer(lean_source):
        name = m.group("name")
        comment = m.group("comment") or ""
        informal = re.sub(r"^/--\s*", "", comment)
        informal = re.sub(r"\s*-/$", "", informal).strip()
        theorems[name] = {"informal": informal, "formal": m.group("theorem")}
    return theorems


# ── Results tracking ─────────────────────────────────────────────────

def _save_results(bench_dir: Path, results: list[dict]) -> None:
    """Write results.json atomically."""
    tmp = bench_dir / "results.json.tmp"
    tmp.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n")
    tmp.rename(bench_dir / "results.json")


# ── OpenProver runner ────────────────────────────────────────────────

def _run_openprover(
    name: str, info: dict[str, str],
    lean_project: Path | None, bench_dir: Path,
    args: argparse.Namespace,
) -> dict:
    tmpfiles: list[str] = []
    start = time.monotonic()
    run_dir = bench_dir / "runs" / name
    run_dir.mkdir(parents=True, exist_ok=True)
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(f"{info['informal']}\n")
            theorem_path = f.name
            tmpfiles.append(f.name)

        cmd = [
            "openprover",
            str(run_dir),
            "--theorem", theorem_path,
            "--model", args.model,
            "--headless",
            "-P", str(args.max_workers),
        ]
        if args.max_tokens:
            cmd.extend(["--max-tokens", str(args.max_tokens)])
        else:
            cmd.extend(["--max-time", args.max_time or "4h"])
        if args.planner_model:
            cmd.extend(["--planner-model", args.planner_model])
        if args.worker_model:
            cmd.extend(["--worker-model", args.worker_model])

        if lean_project and not args.informal:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".lean", delete=False, dir=lean_project,
            ) as f:
                f.write(LEAN_PREAMBLE + info["formal"] + "\n")
                tmpfiles.append(f.name)
            cmd.extend(["--lean-project", str(lean_project)])
            cmd.extend(["--lean-theorem", f.name])

        hf_models: set[str] = set()
        used = {args.model, args.planner_model, args.worker_model} - {None}
        if used & hf_models:
            cmd.extend(["--provider-url", args.provider_url])
        cmd.append("--isolation" if args.isolation else "--no-isolation")
        cmd.append("--verifier" if args.verifier else "--no-verifier")

        # For Claude models: exit on rate limit so the benchmark can retry
        if used & CLAUDE_MODELS:
            cmd.extend(["--on-rate-limited", "exit"])

        # Hard timeout: time budget + 2 min grace, or 4h cap for token budgets
        if args.max_tokens:
            hard_timeout = 4 * 3600  # 4h wall-clock cap for token-based budgets
        else:
            hard_timeout = _parse_duration(args.max_time or "4h") + 120

        while True:
            try:
                result = subprocess.run(cmd, capture_output=True, text=True,
                                        timeout=hard_timeout)
            except subprocess.TimeoutExpired:
                elapsed = time.monotonic() - start
                return {"name": name, "status": "error", "elapsed": elapsed,
                        "error": f"hard timeout ({hard_timeout:.0f}s)"}

            elapsed = time.monotonic() - start

            if result.returncode != 0:
                err = "\n".join((result.stderr or "unknown").strip().splitlines()[-3:])
                return {"name": name, "status": "error", "elapsed": elapsed, "error": err}

            if "[result] rate_limited" in result.stdout:
                msg = (f"⚠️  WARNING: {name}: rate limited / spending limit hit, "
                       f"waiting {RATE_LIMIT_WAIT // 60}m before retry")
                print(msg, flush=True)
                print(msg, file=sys.stderr, flush=True)
                time.sleep(RATE_LIMIT_WAIT)
                continue  # retry the same problem

            status = "proved" if "[result] proved" in result.stdout else "not_proved"
            return {"name": name, "status": status, "elapsed": elapsed, "error": ""}

    except Exception as e:
        return {"name": name, "status": "error", "elapsed": time.monotonic() - start,
                "error": str(e)}
    finally:
        for p in tmpfiles:
            Path(p).unlink(missing_ok=True)


# ── Baseline runner ──────────────────────────────────────────────────

def _run_baseline(
    name: str, info: dict[str, str],
    lean_project: Path | None, bench_dir: Path,
    args: argparse.Namespace,
) -> dict:
    if lean_project is None:
        return {"name": name, "status": "error", "elapsed": 0,
                "error": "baseline requires --repo-path for Lean verification"}

    from baseline import run_baseline

    run_dir = bench_dir / "runs" / name
    if args.max_tokens:
        max_time = None
        max_tokens = args.max_tokens
    else:
        max_time = _parse_duration(args.max_time or "4h")
        max_tokens = None
    result = run_baseline(
        name=name,
        theorem_lean=LEAN_PREAMBLE + info["formal"],
        theorem_informal=info["informal"],
        lean_project_dir=lean_project,
        model=args.model,
        max_time=max_time,
        max_tokens=max_tokens,
        run_dir=run_dir,
        quiet=True,
    )
    return {
        "name": name,
        "status": result["status"],
        "elapsed": result["elapsed"],
        "turns": result.get("turns", 0),
        "verifications": result.get("verifications", 0),
        "tokens": result.get("tokens", 0),
        "error": result.get("error", ""),
    }


# ── Main loop ────────────────────────────────────────────────────────

def _run_all(
    problems: dict[str, dict[str, str]],
    lean_project: Path | None,
    bench_dir: Path,
    args: argparse.Namespace,
    carried: list[dict] | None = None,
) -> None:
    """Run problems and record results.

    `carried` is the list of result entries inherited from a resumed run;
    they're written into the new bench dir's results.json up front and
    counted toward the totals, so the harness output looks identical to
    a non-interrupted run.
    """
    carried = carried or []
    total = len(carried) + len(problems)
    proved = sum(1 for r in carried if r["status"] == "proved")
    not_proved = sum(1 for r in carried if r["status"] == "not_proved")
    errors = sum(1 for r in carried if r["status"] not in ("proved", "not_proved"))
    completed = len(carried)
    pad = len(str(total))
    name_width = max((len(n) for n in problems), default=20)
    name_width = max(name_width, max((len(r["name"]) for r in carried), default=0))

    planner = args.planner_model or args.model
    worker = args.worker_model or args.model
    model_label = planner if planner == worker else f"{planner}/{worker}"
    mode = "informal" if args.informal or lean_project is None else "formal"
    print(f"  MiniF2F {args.split}: {total} problems, method={args.method},"
          f" parallelism={args.parallelism},"
          f" model={model_label}, mode={mode}")
    if carried:
        print(f"  Resumed: {len(carried)} carried over, {len(problems)} to run")
    print(f"  Output: {bench_dir}\n")

    runner = _run_openprover if args.method == "openprover" else _run_baseline
    results: list[dict] = list(carried)
    _save_results(bench_dir, results)

    if not problems:
        # Nothing left to do (resumed run was already complete).
        print(f"\n  Results: {proved} proved, {not_proved} not proved,"
              f" {errors} errors (of {total})")
        print(f"  Saved to {bench_dir / 'results.json'}")
        return

    with ThreadPoolExecutor(max_workers=args.parallelism) as pool:
        futures = {
            pool.submit(runner, name, info, lean_project, bench_dir, args): name
            for name, info in problems.items()
        }

        for future in as_completed(futures):
            entry = future.result()
            completed += 1
            results.append(entry)
            _save_results(bench_dir, results)

            status = entry["status"]
            if status == "proved":
                proved += 1
            elif status == "not_proved":
                not_proved += 1
            else:
                errors += 1

            running = min(args.parallelism, total - completed)
            elapsed_str = _format_time(entry["elapsed"])
            counts = f"P:{proved} F:{not_proved} E:{errors}"
            if running > 0:
                counts += f" R:{running}"

            extra = ""
            if "verifications" in entry and entry["verifications"]:
                extra = f"  v={entry['verifications']}"
            if entry.get("tokens"):
                extra += f"  t={entry['tokens']}"

            print(f"  [{completed:>{pad}}/{total}]"
                  f"  {entry['name']:<{name_width}}"
                  f"  {status.replace('_', ' '):<12}"
                  f"  {elapsed_str:>7}"
                  f"  ({counts}){extra}")

            if entry.get("error"):
                for line in entry["error"].strip().splitlines():
                    print(f"           {line}", file=sys.stderr)

    print(f"\n  Results: {proved} proved, {not_proved} not proved,"
          f" {errors} errors (of {total})")
    print(f"  Saved to {bench_dir / 'results.json'}")


# ── Resume helpers ───────────────────────────────────────────────────

# Config keys carried forward when resuming a previous benchmark.
# Parallelism is intentionally excluded: it's a runtime/resource concern
# (doesn't affect which problems run or how they're evaluated), so users
# can tune it per-resume without triggering the conflict check.
_RESUME_CARRY_KEYS = (
    "method", "split", "model", "planner_model", "worker_model",
    "max_time", "max_tokens",
    "informal", "skip", "limit", "repo_path", "verifier",
)
# Keys that need to be coerced back to Path on load (config.json stores strings).
_RESUME_PATH_KEYS = ("repo_path",)


def _load_resume(parser, resume_dir: Path) -> tuple[dict, list[dict]]:
    """Load config + results from a previous benchmark directory."""
    if not resume_dir.is_dir():
        parser.error(f"--resume: {resume_dir} is not a directory")
    config_path = resume_dir / "config.json"
    if not config_path.is_file():
        parser.error(f"--resume: {config_path} not found")
    old_config = json.loads(config_path.read_text())
    results_path = resume_dir / "results.json"
    old_results: list[dict] = []
    if results_path.is_file():
        old_results = json.loads(results_path.read_text())
    return old_config, old_results


def _import_completed_runs(old_dir: Path, new_dir: Path,
                           completed_names: set[str]) -> None:
    """Symlink per-problem run directories from old benchmark into new one.

    The old runs are read-only — we just need them visible from the new
    bench dir so the resumed benchmark looks self-contained.
    """
    src_runs = old_dir / "runs"
    if not src_runs.is_dir():
        return
    dst_runs = new_dir / "runs"
    dst_runs.mkdir(exist_ok=True)
    for name in completed_names:
        src = (src_runs / name).resolve()
        if not src.exists():
            continue
        dst = dst_runs / name
        if dst.exists() or dst.is_symlink():
            continue
        dst.symlink_to(src)


# ── CLI ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Benchmark openprover or baseline against MiniF2F")
    parser.add_argument("split", nargs="?", default="valid",
                        choices=["valid", "test"],
                        help="Which MiniF2F split (default: valid)")
    parser.add_argument("--method", default="openprover",
                        choices=["openprover", "baseline"],
                        help="Proving method (default: openprover)")
    parser.add_argument("--repo-path", type=Path, default=None,
                        help="Path to cloned MiniF2F repository (Lean verification)")
    parser.add_argument("--problem",
                        help="Run a single theorem (e.g., amc12a_2019_p21)")
    parser.add_argument("--limit", type=int,
                        help="Limit number of problems")
    parser.add_argument("--skip", type=int, default=0,
                        help="Skip first N problems (resume interrupted runs)")
    parser.add_argument("--parallelism", type=int, default=1,
                        help="Concurrent problem instances (default: 1)")
    parser.add_argument("-P", "--max-workers", type=int, default=1,
                        help="Max parallel workers per openprover step "
                             "(default: 1). Only used with --method openprover.")

    model_choices = ["sonnet", "opus", "minimax-m2.5", "leanstral", "glm-5", "kimi-k2.5"]
    parser.add_argument("--model", default="sonnet", choices=model_choices)
    parser.add_argument("--planner-model", choices=model_choices, default=None)
    parser.add_argument("--worker-model", choices=model_choices, default=None)
    parser.add_argument("--provider-url", default="http://localhost:8000")
    budget = parser.add_mutually_exclusive_group()
    budget.add_argument("--max-time", default=None, metavar="DURATION",
                        help="Time budget per problem (e.g. '10m', '2h')")
    budget.add_argument("--max-tokens", type=int, default=None, metavar="N",
                        help="Output token budget per problem")
    parser.add_argument("--informal", action="store_true",
                        help="Skip Lean verification (informal only)")
    parser.add_argument("--isolation",
                        action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--verifier",
                        action=argparse.BooleanOptionalAction, default=True,
                        help="Run LLM verifier after each worker (default: enabled)")
    parser.add_argument("--name",
                        help="Custom benchmark name (default: auto-generated)")
    parser.add_argument("--resume", type=Path, metavar="DIR", default=None,
                        help="Resume from a previous benchmark directory: "
                             "inherits its config, skips problems already "
                             "proved/not_proved, retries errored problems, "
                             "and writes a fresh benchmark dir that links "
                             "back to the original.")
    args = parser.parse_args()

    # ── Resume: inherit config from a previous benchmark ──
    resume_dir: Path | None = None
    old_results: list[dict] = []
    if args.resume:
        resume_dir = args.resume.resolve()
        old_config, old_results = _load_resume(parser, resume_dir)
        # Carry forward run-shaping options from the old config; reject
        # any conflicting overrides on the CLI.
        for key in _RESUME_CARRY_KEYS:
            if key not in old_config:
                continue
            old_val = old_config[key]
            if key in _RESUME_PATH_KEYS and old_val is not None:
                old_val = Path(old_val)
            cli_val = getattr(args, key, None)
            cli_default = parser.get_default(key)
            if cli_val != cli_default and cli_val != old_val:
                parser.error(
                    f"--resume: cannot override --{key.replace('_', '-')} "
                    f"({cli_val!r}) — original run used {old_val!r}"
                )
            setattr(args, key, old_val)
        print(f"  Resuming from {resume_dir}")

    # ── Resolve Lean project ──
    lean_project: Path | None = None
    if args.repo_path:
        lean_project = args.repo_path.resolve()
        if not (lean_project / "lakefile.lean").is_file() \
                and not (lean_project / "lakefile.toml").is_file():
            print(f"Error: {lean_project} has no lakefile.", file=sys.stderr)
            sys.exit(1)
        if not (lean_project / ".lake").is_dir():
            print(f"Error: {lean_project / '.lake'} not found."
                  " Run `lake build` first.", file=sys.stderr)
            sys.exit(1)

    # ── Load theorems ──
    if args.repo_path:
        filename = "Valid.lean" if args.split == "valid" else "Test.lean"
        lean_path = lean_project / "MiniF2F" / filename
        if not lean_path.is_file():
            print(f"Error: {lean_path} not found.", file=sys.stderr)
            sys.exit(1)
        lean_source = lean_path.read_text()
    else:
        lean_source = _fetch_lean_file(args.split)

    problems = _parse_theorems(lean_source)
    if not problems:
        print("Error: No theorems found.", file=sys.stderr)
        sys.exit(1)
    print(f"  Parsed {len(problems)} theorems from MiniF2F {args.split}")

    # ── Check tools ──
    all_models = {args.model, args.planner_model, args.worker_model} - {None}
    if all_models & {"sonnet", "opus"}:
        _check_tool("claude")

    # ── Filter ──
    if args.problem:
        if args.problem not in problems:
            print(f"Error: unknown theorem '{args.problem}'", file=sys.stderr)
            matches = [n for n in problems if args.problem in n]
            if matches:
                print(f"  Did you mean: {', '.join(matches[:5])}",
                      file=sys.stderr)
            sys.exit(1)
        problems = {args.problem: problems[args.problem]}
    if args.skip > 0:
        problems = dict(list(problems.items())[args.skip:])
        print(f"  Skipping first {args.skip}, {len(problems)} remaining")
    if args.limit is not None:
        problems = dict(list(problems.items())[:args.limit])

    # ── Resume: filter out already-finished problems and carry results ──
    carried: list[dict] = []
    if resume_dir is not None:
        # `proved` and `not_proved` are final; `error` is retried since
        # the original benchmark may have crashed mid-attempt.
        final = {r["name"] for r in old_results
                 if r["status"] in ("proved", "not_proved")}
        carried = [r for r in old_results if r["name"] in final]
        before = len(problems)
        problems = {n: info for n, info in problems.items() if n not in final}
        print(f"  Carried over: {len(carried)} finished, "
              f"{before - len(problems)} skipped, {len(problems)} to run")

    # ── Create benchmark dir ──
    benchmarks_root = Path("benchmarks")
    benchmarks_root.mkdir(exist_ok=True)
    if args.name:
        bench_name = args.name
    else:
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        model_tag = args.model
        suffix = "-resumed" if resume_dir is not None else ""
        bench_name = f"{args.method}-{args.split}-{model_tag}{suffix}-{ts}"
    bench_dir = benchmarks_root / bench_name
    if bench_dir.exists():
        print(f"Error: {bench_dir} already exists. Use --name to pick a"
              " different name, or delete the existing directory.",
              file=sys.stderr)
        sys.exit(1)
    bench_dir.mkdir(parents=True)

    # Save config
    config = {
        "method": args.method,
        "split": args.split,
        "model": args.model,
        "planner_model": args.planner_model,
        "worker_model": args.worker_model,
        "max_time": args.max_time,
        "max_tokens": args.max_tokens,
        "parallelism": args.parallelism,
        "max_workers": args.max_workers,
        "informal": args.informal,
        "repo_path": str(args.repo_path) if args.repo_path else None,
        "total_problems": len(carried) + len(problems),
        "skip": args.skip,
        "limit": args.limit,
        "verifier": args.verifier,
    }
    if resume_dir is not None:
        config["resumed_from"] = str(resume_dir)
    (bench_dir / "config.json").write_text(
        json.dumps(config, indent=2) + "\n")

    # Symlink completed run dirs from the old benchmark so the new
    # bench dir is self-contained.
    if resume_dir is not None and carried:
        _import_completed_runs(resume_dir, bench_dir,
                               {r["name"] for r in carried})

    _run_all(problems, lean_project, bench_dir, args, carried=carried)


if __name__ == "__main__":
    main()
