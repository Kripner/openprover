#!/usr/bin/env python3
"""Audit existing benchmark runs for silently-swallowed LLM errors.

Scans every openprover run_dir that was recorded as "not_proved" and
checks its trace.log for sustained "Planner error:" / "Worker error:"
lines with no successful planner call in between. If every step was an
error, the entry was almost certainly a silent failure that should have
been reported as "error" (see the HTTP 403 "Key limit exceeded" bug).

Usage: audit_silent_errors.py ROOT [ROOT...]

ROOT can be a benchmarks/ dir, an individual benchmark dir, or results/.
"""

import argparse
import json
import re
import sys
from pathlib import Path

# "Planner error:" or "Worker error:" at start of a log line
ERROR_RE = re.compile(r"^\d\d:\d\d:\d\d\s+(Planner|Worker) error:", re.MULTILINE)
# A successful planner/worker call that finished (we see "calling" line first,
# but the telltale "success" is the presence of at least one "Step" log entry
# that wasn't immediately followed by an error.
STEP_RE = re.compile(r"^\d\d:\d\d:\d\d\s+Step\s+(\d+)\s+", re.MULTILINE)
CALL_RE = re.compile(r"^\d\d:\d\d:\d\d\s+\[(planner|worker)_\S+\]\s+calling", re.MULTILINE)


def classify_trace(trace: str) -> tuple[str, dict]:
    """Return ('silent_error', info) | ('ok', info) | ('no_trace', info).

    Heuristic: for each step (calling ... → next step boundary), did the
    planner/worker produce any non-error output? If *every* call resulted
    in an error with zero productive planner calls, it's a silent error.
    """
    calls = [m.start() for m in CALL_RE.finditer(trace)]
    errors = [m.start() for m in ERROR_RE.finditer(trace)]

    if not calls:
        return ("no_trace", {"calls": 0, "errors": len(errors)})

    # Count calls that were IMMEDIATELY followed by an error line (within
    # the next ~200 chars / few lines) -- those are failed calls.
    failed_calls = 0
    for call_pos in calls:
        window = trace[call_pos:call_pos + 2000]
        if ERROR_RE.search(window):
            # Check that the error is before the NEXT "calling" line (if any)
            next_call_rel = CALL_RE.search(window[10:])  # skip "calling" itself
            err = ERROR_RE.search(window)
            if next_call_rel is None or err.start() < (next_call_rel.start() + 10):
                failed_calls += 1

    productive = len(calls) - failed_calls
    info = {
        "calls": len(calls),
        "errors": len(errors),
        "failed_calls": failed_calls,
        "productive_calls": productive,
    }

    # Silent-error heuristic: zero productive calls AND at least 5 failed calls
    # (10 is the MAX_CONSECUTIVE_ERRORS threshold; we use 5 to catch cases
    # where the step budget was smaller, e.g. for small problems).
    if productive == 0 and failed_calls >= 5:
        # Sample the first error message for context
        err_match = ERROR_RE.search(trace)
        info["sample_error"] = (
            trace[err_match.start():err_match.start() + 300].splitlines()[0]
            if err_match else ""
        )
        return ("silent_error", info)

    return ("ok", info)


def iter_run_dirs(root: Path):
    """Yield (benchmark_dir, run_name, run_dir) tuples.

    Accepts:
      - a benchmarks/ parent dir (contains one-or-more benchmark dirs)
      - a single benchmark dir (contains results.json + runs/)
      - a results/ dir (contains multiple result dirs with runs/)
    """
    # Direct benchmark dir?
    if (root / "results.json").is_file() and (root / "runs").is_dir():
        for run in sorted((root / "runs").iterdir()):
            if run.is_dir():
                yield (root, run.name, run)
        return

    # Parent of benchmark dirs
    for bench in sorted(root.iterdir()):
        if not bench.is_dir():
            continue
        if (bench / "results.json").is_file() and (bench / "runs").is_dir():
            for run in sorted((bench / "runs").iterdir()):
                if run.is_dir():
                    yield (bench, run.name, run)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("roots", nargs="+", help="benchmarks/ or results/ dirs (or a single benchmark)")
    ap.add_argument("--only-not-proved", action="store_true",
                    help="only examine entries whose results.json status is 'not_proved' (default: on)")
    ap.add_argument("--all", action="store_true",
                    help="examine all entries, not just 'not_proved'")
    args = ap.parse_args()

    only_nprov = not args.all

    total_entries = 0
    checked = 0
    silent_errors = []  # list of (bench_dir, run_name, info)

    for root_str in args.roots:
        root = Path(root_str).resolve()
        if not root.is_dir():
            print(f"skipping {root}: not a directory", file=sys.stderr)
            continue

        # Load results.json per benchmark for status lookup
        results_cache = {}

        for bench, run_name, run_dir in iter_run_dirs(root):
            if bench not in results_cache:
                try:
                    data = json.load(open(bench / "results.json"))
                    results_cache[bench] = {r["name"]: r for r in data}
                except Exception as e:
                    print(f"skipping {bench}: {e}", file=sys.stderr)
                    results_cache[bench] = {}

            total_entries += 1

            entry = results_cache[bench].get(run_name)
            if entry is None:
                continue
            if only_nprov and entry["status"] != "not_proved":
                continue

            trace_path = run_dir / "trace.log"
            if not trace_path.is_file():
                continue

            try:
                trace = trace_path.read_text(errors="replace")
            except Exception:
                continue

            checked += 1
            verdict, info = classify_trace(trace)
            if verdict == "silent_error":
                silent_errors.append((bench, run_name, info))

    print(f"\nScanned {total_entries} entries across {len(args.roots)} root(s); "
          f"checked {checked} 'not_proved' traces.")
    print(f"Silent errors found: {len(silent_errors)}")
    print()

    if silent_errors:
        # Group by benchmark
        by_bench = {}
        for bench, name, info in silent_errors:
            by_bench.setdefault(bench, []).append((name, info))

        for bench in sorted(by_bench, key=str):
            names = by_bench[bench]
            print(f"\n{bench}  ({len(names)} silent-error entries)")
            for name, info in sorted(names):
                err = info.get("sample_error", "")[:120]
                print(f"  {name}: failed={info['failed_calls']}/{info['calls']} calls  | {err}")


if __name__ == "__main__":
    main()
