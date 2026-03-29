#!/usr/bin/env python3
"""Run openprover on PutnamBench problems."""

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


def _check_tool(name: str) -> None:
    if shutil.which(name) is None:
        print(f"Error: '{name}' not found on PATH.", file=sys.stderr)
        print(f"Install it first: https://docs.anthropic.com/en/docs/claude-cli", file=sys.stderr)
        sys.exit(1)


def _format_time(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.0f}s"
    m, s = divmod(int(seconds), 60)
    return f"{m}m{s:02d}s"


def _run_problem(problem_name: str, statement: str, lean_dir: Path,
                 args: argparse.Namespace) -> tuple[str, str, float, str]:
    """Run openprover on a single problem via subprocess.

    Returns (name, status, elapsed_seconds, error_message).
    Status is one of: "proved", "not_proved", "error".
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(f"{statement}\n")
        theorem_path = f.name

    cmd = ["openprover", "--theorem", theorem_path,
           "--model", args.model,
           "--max-time", args.max_time, "--headless",
           "-P", str(args.parallelism)]

    if args.planner_model:
        cmd.extend(["--planner-model", args.planner_model])
    if args.worker_model:
        cmd.extend(["--worker-model", args.worker_model])

    if not args.informal:
        lean_theorem_path = lean_dir / "src" / f"{problem_name}.lean"
        if lean_theorem_path.is_file():
            cmd.extend(["--lean-project", str(lean_dir)])
            cmd.extend(["--lean-theorem", str(lean_theorem_path)])

    hf_models = {"minimax-m2.5"}
    used_models = {args.model, args.planner_model, args.worker_model} - {None}
    if used_models & hf_models:
        cmd.extend(["--provider-url", args.provider_url])
    if args.isolation:
        cmd.append("--isolation")
    else:
        cmd.append("--no-isolation")
    start = time.monotonic()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        elapsed = time.monotonic() - start
        if result.returncode != 0:
            lines = result.stderr.strip().splitlines()[-3:] if result.stderr else ["unknown error"]
            return (problem_name, "error", elapsed, "\n".join(lines))
        if "[result] proved" in result.stdout:
            return (problem_name, "proved", elapsed, "")
        return (problem_name, "not_proved", elapsed, "")
    except Exception as e:
        return (problem_name, "error", time.monotonic() - start, str(e))
    finally:
        Path(theorem_path).unlink(missing_ok=True)


def _run_parallel(problems: dict[str, str], lean_dir: Path,
                  args: argparse.Namespace) -> None:
    """Run multiple problems concurrently with progress tracking."""
    total = len(problems)
    proved = 0
    not_proved = 0
    errors = 0
    completed = 0
    pad = len(str(total))
    name_width = max(len(n) for n in problems) if problems else 20

    planner = args.planner_model or args.model
    worker = args.worker_model or args.model
    model_label = planner if planner == worker else f"{planner}/{worker}"
    print(f"  Putnam Bench: {total} problems, problem_parallelism={args.problem_parallelism},"
          f" model={model_label}\n")

    with ThreadPoolExecutor(max_workers=args.problem_parallelism) as pool:
        futures = {
            pool.submit(_run_problem, name, stmt, lean_dir, args): name
            for name, stmt in problems.items()
        }

        for future in as_completed(futures):
            name, status, elapsed, error = future.result()
            completed += 1

            if status == "proved":
                proved += 1
            elif status == "not_proved":
                not_proved += 1
            else:
                errors += 1

            running = min(args.problem_parallelism, total - completed)
            elapsed_str = _format_time(elapsed)

            status_display = status.replace("_", " ")
            counts = f"P:{proved} F:{not_proved} E:{errors}"
            if running > 0:
                counts += f" R:{running}"

            print(f"  [{completed:>{pad}}/{total}]"
                  f"  {name:<{name_width}}"
                  f"  {status_display:<12}"
                  f"  {elapsed_str:>7}"
                  f"  ({counts})")

            if error:
                for line in error.strip().splitlines():
                    print(f"           {line}", file=sys.stderr)

    print(f"\n  Results: {proved} proved, {not_proved} not proved,"
          f" {errors} errors (of {total})")


def main():
    parser = argparse.ArgumentParser(description="Run openprover on Putnam problems")
    parser.add_argument("--repo-path", type=Path, default=Path("./PutnamBench"),
                        help="Path to cloned PutnamBench repository (default: ./PutnamBench)")
    parser.add_argument("--problem", help="Specific problem name to run (e.g., putnam_1962_a1)")
    parser.add_argument("--limit", type=int, help="Limit number of problems to run")
    parser.add_argument("--problem-parallelism", type=int, default=1,
                        help="Number of concurrent openprover instances (default: 1)")
    parser.add_argument("-P", "--parallelism", type=int, default=1,
                        help="Max parallel workers per spawn step inside openprover (default: 1)")
    model_choices = ["sonnet", "opus", "minimax-m2.5", "leanstral"]
    parser.add_argument("--model", default="sonnet", choices=model_choices)
    parser.add_argument("--planner-model", choices=model_choices, default=None,
                        help="Override model for planner (defaults to --model)")
    parser.add_argument("--worker-model", choices=model_choices, default=None,
                        help="Override model for worker (defaults to --model)")
    parser.add_argument("--provider-url", default="http://localhost:8000",
                        help="Server URL for local models (default: http://localhost:8000)")
    parser.add_argument("--max-time", default="4h", metavar="DURATION",
                        help="Wall-clock time budget per problem, e.g. '30m', '2h' (default: 4h)")
    parser.add_argument("--autonomous", action="store_true")
    parser.add_argument("--informal", action="store_true",
                        help="Skip Lean setup/verification; run openprover without formal checking")
    parser.add_argument("--isolation", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    repo_path = args.repo_path.resolve()
    lean_dir = repo_path / "lean4"

    if not args.informal:
        lake_dir = lean_dir / ".lake"
        if not lake_dir.is_dir():
            print(f"Error: {lake_dir} not found.", file=sys.stderr)
            print("The Lean 4 project must be built first.", file=sys.stderr)
            sys.exit(1)

    json_path = repo_path / "informal" / "putnam.json"
    if not json_path.is_file():
        print(f"Error: {json_path} not found.", file=sys.stderr)
        sys.exit(1)

    with open(json_path, "r", encoding="utf-8") as f:
        problems_data = json.load(f)

    problems = {}
    for p in problems_data:
        if "problem_name" in p and "informal_statement" in p:
            problems[p["problem_name"]] = p["informal_statement"]

    if not problems:
        print("Error: Could not parse problems from putnam.json.", file=sys.stderr)
        sys.exit(1)

    all_models = {args.model, args.planner_model, args.worker_model} - {None}
    if all_models & {"sonnet", "opus"}:
        _check_tool("claude")

    if args.problem:
        if args.problem not in problems:
            print(f"Error: unknown problem '{args.problem}'", file=sys.stderr)
            sys.exit(1)
        problems = {args.problem: problems[args.problem]}

    if args.limit is not None:
        problems = dict(list(problems.items())[:args.limit])

    if args.problem_parallelism > 1:
        _run_parallel(problems, lean_dir, args)
        return

    for problem_name, statement in problems.items():
        print(f"=== Running openprover on {problem_name} ===")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(f"{statement}\n")
            theorem_path = f.name

        cmd = ["openprover", "--theorem", theorem_path,
               "--model", args.model,
               "--max-time", args.max_time,
               "-P", str(args.parallelism)]

        if args.planner_model:
            cmd.extend(["--planner-model", args.planner_model])
        if args.worker_model:
            cmd.extend(["--worker-model", args.worker_model])

        if not args.informal:
            lean_theorem_path = lean_dir / "src" / f"{problem_name}.lean"
            if lean_theorem_path.is_file():
                cmd.extend(["--lean-project", str(lean_dir)])
                cmd.extend(["--lean-theorem", str(lean_theorem_path)])
            else:
                print(f"Warning: Lean theorem not found at {lean_theorem_path}."
                      " Running without formal verification.", file=sys.stderr)

        hf_models = {"minimax-m2.5"}
        used_models = {args.model, args.planner_model, args.worker_model} - {None}
        if used_models & hf_models:
            cmd.extend(["--provider-url", args.provider_url])
        if args.autonomous:
            cmd.append("--autonomous")
        if args.isolation:
            cmd.append("--isolation")
        else:
            cmd.append("--no-isolation")
        if args.verbose:
            cmd.append("--verbose")

        try:
            subprocess.run(cmd)
        finally:
            Path(theorem_path).unlink(missing_ok=True)
            print()


if __name__ == "__main__":
    main()
