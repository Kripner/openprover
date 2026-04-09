import json
from pathlib import Path

from openprover.budget import Budget
from openprover.prover import Prover
from openprover.tui.headless import HeadlessTUI


class _UnusedLLM:
    model = "fake-model"
    context_length = 200_000

    def call(self, **_kwargs):
        raise AssertionError("LLM should not be called in proof manifest test")

    def clear_interrupt(self):
        pass


def test_submit_proof_writes_dependency_manifest(tmp_path: Path):
    work_dir = tmp_path / "run"
    tui = HeadlessTUI()
    tui._sync_step_log_line = lambda *_args, **_kwargs: None

    prover = Prover(
        work_dir=work_dir,
        theorem_text="Test theorem",
        mode="prove",
        make_llm=lambda _wd: _UnusedLLM(),
        model_name="fake",
        budget=Budget("time", 3600),
        autonomous=True,
        verbose=False,
        tui=tui,
    )

    prover.repo.write_item(
        "lemmas/base",
        "Summary: Base lemma\n\nNo further dependencies.\n",
    )
    prover.repo.write_item(
        "lemmas/helper",
        "Summary: Helper lemma\n\nUses [[lemmas/base]].\n",
    )
    prover.repo.write_item(
        "bounds/main",
        "Summary: Main bound\n\nThis also depends on [[lemmas/base]].\n",
    )
    prover.repo.write_item(
        "proofs/final",
        "\n".join([
            "Summary: Final proof",
            "",
            "# Setup",
            "Apply [[lemmas/helper]] to initialize the argument.",
            "",
            "# Counting",
            "Finish by combining [[bounds/main]].",
            "",
        ]),
    )

    result = prover._handle_submit_proof({"proof_slug": "proofs/final"}, work_dir / "steps" / "step_001")

    assert result == "stop"
    assert (work_dir / "PROOF.md").exists()
    assert (work_dir / "PROOF_MANIFEST.json").exists()
    assert (work_dir / "PROOF_DEPENDENCIES.md").exists()

    manifest = json.loads((work_dir / "PROOF_MANIFEST.json").read_text())

    assert manifest["proof_slug"] == "proofs/final"
    assert manifest["direct_refs"] == ["lemmas/helper", "bounds/main"]
    assert manifest["all_refs"] == ["lemmas/helper", "lemmas/base", "bounds/main"]

    setup = next(section for section in manifest["sections"] if section["heading"] == "Setup")
    counting = next(section for section in manifest["sections"] if section["heading"] == "Counting")

    assert setup["direct_refs"] == ["lemmas/helper"]
    assert setup["all_refs"] == ["lemmas/helper", "lemmas/base"]
    assert counting["direct_refs"] == ["bounds/main"]
    assert counting["all_refs"] == ["bounds/main", "lemmas/base"]

    assert manifest["items"]["lemmas/helper"]["all_refs"] == ["lemmas/base"]
    assert manifest["reverse_index"]["lemmas/base"]["used_by_sections"] == ["Setup", "Counting"]
    assert manifest["reverse_index"]["lemmas/base"]["directly_used_by_sections"] == []

    deps_md = (work_dir / "PROOF_DEPENDENCIES.md").read_text()
    assert "[[lemmas/base]]" in deps_md
    assert "Setup" in deps_md
    assert "Counting" in deps_md


def test_proof_manifest_excludes_self_dependencies_from_cycles(tmp_path: Path):
    work_dir = tmp_path / "run"
    tui = HeadlessTUI()
    tui._sync_step_log_line = lambda *_args, **_kwargs: None

    prover = Prover(
        work_dir=work_dir,
        theorem_text="Test theorem",
        mode="prove",
        make_llm=lambda _wd: _UnusedLLM(),
        model_name="fake",
        budget=Budget("time", 3600),
        autonomous=True,
        verbose=False,
        tui=tui,
    )

    prover.repo.write_item(
        "lemmas/a",
        "Summary: A\n\nUses [[lemmas/b]].\n",
    )
    prover.repo.write_item(
        "lemmas/b",
        "Summary: B\n\nUses [[lemmas/a]].\n",
    )
    prover.repo.write_item(
        "proofs/final",
        "\n".join([
            "Summary: Final proof",
            "",
            "# Main",
            "Use [[lemmas/a]].",
            "",
        ]),
    )

    prover._handle_submit_proof({"proof_slug": "proofs/final"}, work_dir / "steps" / "step_001")
    manifest = json.loads((work_dir / "PROOF_MANIFEST.json").read_text())

    assert manifest["items"]["lemmas/a"]["all_refs"] == ["lemmas/b"]
    assert manifest["items"]["lemmas/b"]["all_refs"] == ["lemmas/a"]
    assert manifest["all_refs"] == ["lemmas/a", "lemmas/b"]
