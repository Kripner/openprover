#!/usr/bin/env python3
"""Flip silently-swallowed 'not_proved' entries to 'error' in a benchmark's
results.json, so that a subsequent --resume will actually retry them.

A silent error is an entry whose status is 'not_proved' but whose trace.log
shows that every LLM call failed (productive calls == 0 AND failed calls
>= 5). See scripts/audit_silent_errors.py for the same heuristic.
"""

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

ERROR_RE = re.compile(r"^\d\d:\d\d:\d\d\s+(Planner|Worker) error:", re.MULTILINE)
CALL_RE = re.compile(r"^\d\d:\d\d:\d\d\s+\[(planner|worker)_\S+\]\s+calling", re.MULTILINE)


def classify_trace(trace: str) -> tuple[str, dict]:
    calls = [m.start() for m in CALL_RE.finditer(trace)]
    errors = [m.start() for m in ERROR_RE.finditer(trace)]
    if not calls:
        return ("no_trace", {"calls": 0, "errors": len(errors)})

    failed_calls = 0
    for call_pos in calls:
        window = trace[call_pos:call_pos + 2000]
        if ERROR_RE.search(window):
            next_call_rel = CALL_RE.search(window[10:])
            err = ERROR_RE.search(window)
            if next_call_rel is None or err.start() < (next_call_rel.start() + 10):
                failed_calls += 1

    productive = len(calls) - failed_calls
    info = {"calls": len(calls), "errors": len(errors),
            "failed_calls": failed_calls, "productive_calls": productive}
    if productive == 0 and failed_calls >= 5:
        err_match = ERROR_RE.search(trace)
        if err_match:
            info["sample_error"] = trace[err_match.start():err_match.start() + 300].splitlines()[0]
        return ("silent_error", info)
    return ("ok", info)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bench_dir", type=Path)
    ap.add_argument("--apply", action="store_true",
                    help="actually write changes (default: dry-run)")
    args = ap.parse_args()

    bench = args.bench_dir.resolve()
    results_path = bench / "results.json"
    runs_dir = bench / "runs"
    if not results_path.is_file():
        sys.exit(f"no results.json in {bench}")
    if not runs_dir.is_dir():
        sys.exit(f"no runs/ in {bench}")

    data = json.load(open(results_path))
    silent = []

    for entry in data:
        if entry["status"] != "not_proved":
            continue
        trace = runs_dir / entry["name"] / "trace.log"
        if not trace.is_file():
            continue
        try:
            text = trace.read_text(errors="replace")
        except Exception:
            continue
        verdict, info = classify_trace(text)
        if verdict == "silent_error":
            silent.append((entry, info))

    print(f"Benchmark: {bench}")
    print(f"Silent-error entries found: {len(silent)}")
    for entry, info in silent:
        err = info.get("sample_error", "")[:100]
        print(f"  {entry['name']}: failed={info['failed_calls']}/{info['calls']} | {err}")

    if not silent:
        print("\nNothing to do.")
        return

    if not args.apply:
        print("\nDry-run only. Pass --apply to write changes.")
        return

    # Back up
    backup = results_path.with_suffix(".json.bak")
    if not backup.exists():
        shutil.copy2(results_path, backup)
        print(f"\nBackup: {backup}")
    else:
        print(f"\nBackup exists: {backup} (not overwriting)")

    # Flip status
    silent_names = {e["name"] for e, _ in silent}
    changed = 0
    for entry in data:
        if entry["name"] in silent_names:
            entry["status"] = "error"
            entry["error"] = (
                "silent LLM error (patched): every call failed; "
                "see runs/{}/trace.log".format(entry["name"])
            )
            changed += 1

    results_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"Patched {changed} entries in {results_path}")


if __name__ == "__main__":
    main()
