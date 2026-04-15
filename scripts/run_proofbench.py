#!/usr/bin/env python3
"""Run openprover on a ProofBench problem."""

import argparse
import csv
import subprocess
import sys
import tempfile
from pathlib import Path

PROOFBENCH_CSV = Path(__file__).resolve().parent.parent / "examples" / "proofbench.csv"


def load_problems(csv_path: Path) -> dict[str, dict]:
    problems = {}
    with open(csv_path, newline="") as f:
        for row in csv.DictReader(f):
            problems[row["Problem ID"]] = row
    return problems


def main():
    parser = argparse.ArgumentParser(description="Run openprover on a ProofBench problem")
    parser.add_argument("problem", help="Problem ID (e.g. PB-Basic-001)")
    parser.add_argument("--list", action="store_true", help="List available problems and exit")
    parser.add_argument("--model", default="sonnet", choices=["sonnet", "opus", "minimax-m2.5"])
    parser.add_argument("--provider-url", default="http://localhost:8000",
                        help="Server URL for local models (default: http://localhost:8000)")
    parser.add_argument("--max-steps", type=int, default=50)
    parser.add_argument("--autonomous", action="store_true")
    parser.add_argument("--isolation", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    problems = load_problems(PROOFBENCH_CSV)

    if args.list:
        for pid, row in problems.items():
            stmt = row["Problem"][:80].replace("\n", " ")
            print(f"  {pid:20s} [{row['Category']}/{row['Level']}]  {stmt}...")
        sys.exit(0)

    if args.problem not in problems:
        print(f"Error: unknown problem '{args.problem}'", file=sys.stderr)
        print(f"Available: {', '.join(problems.keys())}", file=sys.stderr)
        sys.exit(1)

    row = problems[args.problem]
    statement = row["Problem"]

    # Write problem statement to a temp file and invoke openprover
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(f"# {args.problem}\n\n{statement}\n")
        theorem_path = f.name

    cmd = ["openprover", theorem_path, "--model", args.model, "--max-steps", str(args.max_steps)]
    if args.autonomous:
        cmd.append("--autonomous")
    if args.isolation:
        cmd.append("--isolation")
    if args.verbose:
        cmd.append("--verbose")

    try:
        subprocess.run(cmd)
    finally:
        Path(theorem_path).unlink(missing_ok=True)


if __name__ == "__main__":
    main()
