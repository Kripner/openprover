import argparse
import json
from pathlib import Path

from scripts.run_irreps_tensor_product import (
    DEFAULT_DATASET,
    build_theorem,
    expected_decomposition,
    load_problems,
    run_problem,
    score_proof,
)


def test_expected_decomposition_examples():
    assert expected_decomposition("2e", "3o") == "1o + 2o + 3o + 4o + 5o"
    assert expected_decomposition("1o", "1o") == "0e + 1e + 2e"
    assert expected_decomposition("0e", "4o") == "4o"


def test_sample_dataset_matches_oracle():
    problems = load_problems(DEFAULT_DATASET)
    assert len(problems) == 12
    assert {problem["split"] for problem in problems} == {"easy", "medium", "hard"}


def test_theorem_does_not_include_expected_answer():
    problem = {
        "left": "2e",
        "right": "3o",
        "answer": "1o + 2o + 3o + 4o + 5o",
    }
    theorem = build_theorem(problem)
    assert "2e x 3o" in theorem
    assert "FINAL ANSWER:" in theorem
    assert problem["answer"] not in theorem


def test_exact_scorer_classifies_common_failures():
    expected = "1o + 2o + 3o"
    assert score_proof("FINAL ANSWER: 1o + 2o + 3o", expected)["category"] == "correct"
    assert score_proof("`FINAL ANSWER: 1o + 2o + 3o`", expected)["score"] == 1.0
    assert (
        score_proof("FINAL ANSWER: 1e + 2e + 3e", expected)["category"]
        == "wrong_parity"
    )
    assert score_proof("FINAL ANSWER: 1o + 2o", expected)["category"] == "missing_terms"
    assert (
        score_proof("no labelled answer", expected)["category"]
        == "missing_final_answer"
    )


def test_dataset_rejects_unsafe_problem_id(tmp_path: Path):
    dataset = tmp_path / "unsafe.jsonl"
    dataset.write_text(
        json.dumps(
            {
                "id": "../escape",
                "split": "easy",
                "left": "0e",
                "right": "0e",
                "answer": "0e",
            }
        )
        + "\n"
    )
    try:
        load_problems(dataset)
    except ValueError as error:
        assert "unsafe problem id" in str(error)
    else:
        raise AssertionError("unsafe problem id was accepted")


def test_run_problem_with_fake_openprover(tmp_path: Path):
    fake = tmp_path / "fake-openprover"
    fake.write_text(
        "#!/bin/sh\n"
        "run_dir=$1\n"
        "printf 'Proof.\\n\\nFINAL ANSWER: 1o + 2o + 3o + 4o + 5o\\n' "
        '> "$run_dir/PROOF.md"\n'
    )
    fake.chmod(0o755)
    benchmark_dir = tmp_path / "benchmark"
    (benchmark_dir / "runs").mkdir(parents=True)
    args = argparse.Namespace(
        dry_run=False,
        openprover_command=str(fake),
        model="sonnet",
        max_workers=1,
        verifier=True,
        max_tokens=1000,
        max_time=None,
        planner_model=None,
        worker_model=None,
        provider_url=None,
        hard_timeout=30,
    )
    problem = {
        "id": "example",
        "split": "easy",
        "left": "2e",
        "right": "3o",
        "answer": "1o + 2o + 3o + 4o + 5o",
    }

    result = run_problem(problem, benchmark_dir, args)

    assert result["status"] == "proved"
    assert result["score"] == 1.0
    assert json.loads(json.dumps(result))["category"] == "correct"
