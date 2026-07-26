#!/usr/bin/env python3
"""Run an exact-scored O(3) irreps tensor-product benchmark."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATASET = ROOT / "examples" / "irreps_tensor_product.jsonl"
IRREP_RE = re.compile(r"^(0|[1-9][0-9]*)([eo])$")
PROBLEM_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
FINAL_ANSWER_RE = re.compile(
    r"^\s*(?:`|\*\*)?FINAL\s+ANSWER\s*:\s*(.*?)(?:`|\*\*)?\s*$",
    re.IGNORECASE | re.MULTILINE,
)
MODEL_CHOICES = [
    "sonnet",
    "opus",
    "minimax-m2.5",
    "leanstral",
    "glm-5",
    "kimi-k2.5",
    "minimax-m2.7",
]


def parse_irrep(text: str) -> tuple[int, str]:
    match = IRREP_RE.fullmatch(text)
    if match is None:
        raise ValueError(f"invalid irrep: {text!r}")
    degree, parity = match.groups()
    return int(degree), parity


def expected_decomposition(left: str, right: str) -> str:
    left_l, left_parity = parse_irrep(left)
    right_l, right_parity = parse_irrep(right)
    parity = "e" if left_parity == right_parity else "o"
    return " + ".join(
        f"{degree}{parity}"
        for degree in range(abs(left_l - right_l), left_l + right_l + 1)
    )


def load_problems(path: Path) -> list[dict]:
    problems: list[dict] = []
    seen: set[str] = set()
    for line_number, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        row = json.loads(line)
        missing = {"id", "split", "left", "right", "answer"} - set(row)
        if missing:
            raise ValueError(
                f"{path}:{line_number}: missing fields: {', '.join(sorted(missing))}"
            )
        if not all(
            isinstance(row[key], str)
            for key in ("id", "split", "left", "right", "answer")
        ):
            raise ValueError(f"{path}:{line_number}: all fields must be strings")
        if PROBLEM_ID_RE.fullmatch(row["id"]) is None:
            raise ValueError(f"{path}:{line_number}: unsafe problem id {row['id']!r}")
        if row["split"] not in {"easy", "medium", "hard"}:
            raise ValueError(f"{path}:{line_number}: invalid split {row['split']!r}")
        if row["id"] in seen:
            raise ValueError(f"{path}:{line_number}: duplicate id {row['id']!r}")
        expected = expected_decomposition(row["left"], row["right"])
        if row["answer"] != expected:
            raise ValueError(
                f"{path}:{line_number}: oracle mismatch for {row['id']}: "
                f"expected {expected!r}"
            )
        seen.add(row["id"])
        problems.append(row)
    if not problems:
        raise ValueError(f"{path}: no problems")
    return problems


def build_theorem(problem: dict) -> str:
    return f"""\
# O(3) irreducible-representation tensor product

Decompose the tensor product `{problem["left"]} x {problem["right"]}`.

Use the following rule:

- output every angular-momentum degree from `|l1-l2|` through `l1+l2`, inclusive;
- multiply parity using `e*e=e`, `e*o=o`, `o*e=o`, and `o*o=e`;
- write the decomposition in ascending e3nn-style notation.

Give a concise mathematical justification. End the submitted proof with exactly
one line of the following form:

`FINAL ANSWER: <canonical decomposition>`

Replace the placeholder with only the decomposition. The final line is scored
exactly, so do not put prose on that line.
"""


def parse_decomposition(text: str) -> tuple[tuple[int, str], ...]:
    pieces = [piece.strip() for piece in text.split("+")]
    if not pieces or any(not piece for piece in pieces):
        raise ValueError("empty decomposition term")
    return tuple(parse_irrep(piece) for piece in pieces)


def score_proof(proof: str, expected: str) -> dict:
    matches = FINAL_ANSWER_RE.findall(proof)
    if not matches:
        return {"score": 0.0, "category": "missing_final_answer", "prediction": None}
    if len(matches) != 1:
        return {
            "score": 0.0,
            "category": "ambiguous_final_answer",
            "prediction": None,
        }

    prediction = matches[0].strip()
    if prediction.startswith("`") and prediction.endswith("`"):
        prediction = prediction[1:-1].strip()
    try:
        predicted_terms = parse_decomposition(prediction)
        expected_terms = parse_decomposition(expected)
    except ValueError:
        return {
            "score": 0.0,
            "category": "malformed_syntax",
            "prediction": prediction,
        }

    if predicted_terms == expected_terms:
        return {"score": 1.0, "category": "correct", "prediction": prediction}

    category = "incorrect"
    if len(set(predicted_terms)) != len(predicted_terms):
        category = "duplicate_terms"
    elif [term[0] for term in predicted_terms] != sorted(
        term[0] for term in predicted_terms
    ):
        category = "wrong_order"
    elif any(predicted[1] != expected_terms[0][1] for predicted in predicted_terms):
        category = "wrong_parity"
    elif set(predicted_terms) < set(expected_terms):
        category = "missing_terms"
    elif set(predicted_terms) > set(expected_terms):
        category = "extra_terms"
    return {"score": 0.0, "category": category, "prediction": prediction}


def save_results(benchmark_dir: Path, results: list[dict]) -> None:
    temporary = benchmark_dir / "results.json.tmp"
    ordered = sorted(results, key=lambda result: result["name"])
    temporary.write_text(json.dumps(ordered, indent=2) + "\n")
    temporary.replace(benchmark_dir / "results.json")


def run_problem(problem: dict, benchmark_dir: Path, args: argparse.Namespace) -> dict:
    started = time.monotonic()
    run_dir = benchmark_dir / "runs" / problem["id"]
    run_dir.mkdir(parents=True, exist_ok=False)
    (run_dir / "THEOREM.md").write_text(build_theorem(problem))

    base = {
        "name": problem["id"],
        "split": problem["split"],
        "left": problem["left"],
        "right": problem["right"],
        "expected": problem["answer"],
    }
    if args.dry_run:
        return {
            **base,
            "status": "prepared",
            "score": None,
            "category": None,
            "prediction": None,
            "elapsed": 0.0,
        }

    command = [
        args.openprover_command,
        str(run_dir),
        "--model",
        args.model,
        "--headless",
        "--autonomous",
        "-P",
        str(args.max_workers),
        "--isolation",
        "--verifier" if args.verifier else "--no-verifier",
    ]
    if args.max_tokens:
        command.extend(["--max-tokens", str(args.max_tokens)])
    else:
        command.extend(["--max-time", args.max_time])
    if args.planner_model:
        command.extend(["--planner-model", args.planner_model])
    if args.worker_model:
        command.extend(["--worker-model", args.worker_model])
    if args.provider_url:
        command.extend(["--provider-url", args.provider_url])

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=args.hard_timeout,
        )
    except subprocess.TimeoutExpired:
        return {
            **base,
            "status": "error",
            "score": 0.0,
            "category": "hard_timeout",
            "prediction": None,
            "elapsed": time.monotonic() - started,
        }

    (run_dir / "openprover.log").write_text(
        completed.stdout
        + ("\n[stderr]\n" + completed.stderr if completed.stderr else "")
    )
    if completed.returncode != 0:
        return {
            **base,
            "status": "error",
            "score": 0.0,
            "category": "openprover_error",
            "prediction": None,
            "elapsed": time.monotonic() - started,
        }

    proof_path = run_dir / "PROOF.md"
    if not proof_path.is_file():
        return {
            **base,
            "status": "not_proved",
            "score": 0.0,
            "category": "missing_proof",
            "prediction": None,
            "elapsed": time.monotonic() - started,
        }

    score = score_proof(proof_path.read_text(), problem["answer"])
    return {
        **base,
        "status": "proved" if score["score"] == 1.0 else "incorrect",
        **score,
        "elapsed": time.monotonic() - started,
    }


def select_problems(
    problems: list[dict],
    split: str | None,
    problem_id: str | None,
    skip: int,
    limit: int | None,
) -> list[dict]:
    selected = [
        problem for problem in problems if split is None or problem["split"] == split
    ]
    if problem_id:
        selected = [problem for problem in selected if problem["id"] == problem_id]
        if not selected:
            raise ValueError(f"unknown problem: {problem_id}")
    selected = selected[skip:]
    if limit is not None:
        selected = selected[:limit]
    if not selected:
        raise ValueError("no problems selected")
    return selected


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the exact-scored O(3) irreps tensor-product benchmark."
    )
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--split", choices=["easy", "medium", "hard"])
    parser.add_argument("--problem")
    parser.add_argument("--skip", type=int, default=0)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--parallelism", type=int, default=1)
    parser.add_argument("-P", "--max-workers", type=int, default=1)
    parser.add_argument("--model", choices=MODEL_CHOICES, default="sonnet")
    parser.add_argument("--planner-model", choices=MODEL_CHOICES)
    parser.add_argument("--worker-model", choices=MODEL_CHOICES)
    parser.add_argument("--provider-url")
    budget = parser.add_mutually_exclusive_group()
    budget.add_argument("--max-time")
    budget.add_argument("--max-tokens", type=int)
    parser.add_argument("--hard-timeout", type=int, default=3600)
    parser.add_argument(
        "--verifier", action=argparse.BooleanOptionalAction, default=True
    )
    parser.add_argument("--name")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--openprover-command", default="openprover", help=argparse.SUPPRESS
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.max_time is None and args.max_tokens is None:
        args.max_time = "10m"
    if args.skip < 0 or (args.limit is not None and args.limit <= 0):
        raise ValueError("--skip must be non-negative and --limit must be positive")
    if args.parallelism <= 0 or args.max_workers <= 0 or args.hard_timeout <= 0:
        raise ValueError("parallelism, max-workers, and hard-timeout must be positive")

    problems = load_problems(args.dataset)
    if args.list:
        for problem in problems:
            print(
                f"{problem['id']:<16} [{problem['split']:<6}] "
                f"{problem['left']} x {problem['right']}"
            )
        return
    selected = select_problems(
        problems, args.split, args.problem, args.skip, args.limit
    )

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    benchmark_name = args.name or f"irreps-{args.model}-{timestamp}"
    benchmark_dir = Path("benchmarks") / benchmark_name
    if benchmark_dir.exists():
        raise FileExistsError(f"benchmark directory already exists: {benchmark_dir}")
    (benchmark_dir / "runs").mkdir(parents=True)
    config = {
        "dataset": str(args.dataset),
        "model": args.model,
        "planner_model": args.planner_model,
        "worker_model": args.worker_model,
        "max_time": args.max_time,
        "max_tokens": args.max_tokens,
        "parallelism": args.parallelism,
        "max_workers": args.max_workers,
        "split": args.split,
        "problem": args.problem,
        "skip": args.skip,
        "limit": args.limit,
        "dry_run": args.dry_run,
        "total_problems": len(selected),
        "scoring": "exact_final_answer",
    }
    (benchmark_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n")

    results: list[dict] = []
    save_results(benchmark_dir, results)
    with ThreadPoolExecutor(max_workers=args.parallelism) as pool:
        futures = {
            pool.submit(run_problem, problem, benchmark_dir, args): problem["id"]
            for problem in selected
        }
        for completed, future in enumerate(as_completed(futures), start=1):
            result = future.result()
            results.append(result)
            save_results(benchmark_dir, results)
            print(
                f"[{completed}/{len(selected)}] {result['name']}: "
                f"{result['status']} ({result['category']})"
            )

    if args.dry_run:
        print(f"\nPrepared {len(results)} problems (no model calls)")
    else:
        correct = sum(result["score"] == 1.0 for result in results)
        print(f"\nExact accuracy: {correct}/{len(results)}")
    print(f"Results: {benchmark_dir / 'results.json'}")


if __name__ == "__main__":
    main()
