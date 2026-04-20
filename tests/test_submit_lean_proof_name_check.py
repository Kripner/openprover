"""Tests for the proof-name check in Prover._handle_submit_lean_proof.

The critical invariant: an openprover run may ONLY claim `proved` if
its submitted PROOF.lean declares every `theorem/lemma/def` name that
appears in the original THEOREM.lean. Otherwise the model has proved
some other statement it invented (renamed theorem, anonymous `example`,
unrelated lemma) and the benchmark task wasn't actually done, even if
Lean is happy.

These tests exercise the static extractor used by that check.
"""

import pytest

from openprover.prover import Prover


extract = Prover._extract_expected_theorem_names


# ── Extractor correctness ─────────────────────────────────────────────

def test_single_theorem():
    src = """
    import Mathlib
    theorem exercise_1_1a (x : ℝ) : x = x := by rfl
    """
    assert extract(src) == ["exercise_1_1a"]


def test_lemma_is_picked_up():
    src = "lemma foo : True := trivial"
    assert extract(src) == ["foo"]


def test_def_is_picked_up():
    # `def` is used in ProofNet for theorems whose conclusion is a structure
    src = "def exercise_2_1_21 (G : Type*) [Group G] : CommGroup G := ⟨⟩"
    assert extract(src) == ["exercise_2_1_21"]


def test_anonymous_example_returns_nothing():
    src = "example (x : ℝ) : x = x := by rfl"
    assert extract(src) == []


def test_multiple_declarations_preserves_order():
    src = """
    theorem helper_lemma : True := trivial
    theorem exercise_X : True := trivial
    """
    assert extract(src) == ["helper_lemma", "exercise_X"]


def test_apostrophe_in_name():
    # ProofNet uses names like exercise_3_22', exercise_3_1''
    src = "theorem exercise_3_22' : True := trivial"
    assert extract(src) == ["exercise_3_22'"]

    src2 = "theorem exercise_3_1'' : True := trivial"
    assert extract(src2) == ["exercise_3_1''"]


def test_line_comment_is_ignored():
    src = """
    -- theorem fake_name : False := sorry
    theorem real_name : True := trivial
    """
    assert extract(src) == ["real_name"]


def test_block_comment_is_ignored():
    src = """
    /- theorem commented_out : True := trivial -/
    theorem real_name : True := trivial
    """
    assert extract(src) == ["real_name"]


def test_multiline_block_comment_is_ignored():
    src = """
    /-
    theorem fake1 : True := trivial
    theorem fake2 : True := trivial
    -/
    theorem real : True := trivial
    """
    assert extract(src) == ["real"]


def test_empty_and_whitespace():
    assert extract("") == []
    assert extract("   \n\n\n") == []


def test_no_declarations_in_prose():
    src = """
    import Mathlib
    -- This file just has imports and comments
    """
    assert extract(src) == []


def test_theorem_must_be_line_start():
    # `theorem` appearing inside a string or deep in some expression
    # should NOT be picked up — the declaration must be at the start
    # of a line (after optional whitespace).
    src = '''
    theorem real_one : True := trivial
    -- the word theorem here doesn't count: theorem fake1 : True := trivial
    '''
    # after stripping the line comment, only real_one remains
    assert extract(src) == ["real_one"]


# ── The check's core logic ────────────────────────────────────────────
# Mirrors what _handle_submit_lean_proof computes: missing = [n for n in
# expected if n not in declared]. We exercise it directly without
# needing to construct a full Prover instance.

def _missing(theorem_text: str, proof_text: str) -> list[str]:
    expected = extract(theorem_text)
    declared = extract(proof_text)
    return [n for n in expected if n not in declared]


def test_matching_name_ok():
    theorem = "theorem exercise_1_1a (x : ℝ) : x = x := by sorry"
    proof = """
    import Mathlib
    theorem exercise_1_1a (x : ℝ) : x = x := by rfl
    """
    assert _missing(theorem, proof) == []


def test_renamed_theorem_is_rejected():
    theorem = "theorem exercise_3_9 : True := by sorry"
    proof = """
    import Mathlib
    theorem integral_log_sin_pi_x_zero_one : True := by trivial
    """
    assert _missing(theorem, proof) == ["exercise_3_9"]


def test_anonymous_example_is_rejected():
    theorem = "theorem exercise_2_12a : True := by sorry"
    proof = """
    import Mathlib
    example : True := by trivial
    """
    assert _missing(theorem, proof) == ["exercise_2_12a"]


def test_helper_lemmas_plus_original_is_ok():
    # Model may add helpers — as long as the expected theorem is still
    # declared, it's fine.
    theorem = "theorem exercise_X : True := by sorry"
    proof = """
    import Mathlib
    lemma helper_lemma_1 : True := trivial
    theorem some_intermediate : True := trivial
    theorem exercise_X : True := by trivial
    """
    assert _missing(theorem, proof) == []


def test_multiple_sorries_all_must_be_declared():
    theorem = """
    theorem exercise_A : True := by sorry
    theorem exercise_B : True := by sorry
    """
    # Missing exercise_B → rejected
    proof_a_only = """
    theorem exercise_A : True := by trivial
    """
    assert _missing(theorem, proof_a_only) == ["exercise_B"]

    # Both present → ok
    proof_both = """
    theorem exercise_A : True := by trivial
    theorem exercise_B : True := by trivial
    """
    assert _missing(theorem, proof_both) == []


def test_theorem_with_apostrophe():
    # ProofNet exercise_3_22' case
    theorem = "theorem exercise_3_22' : True := by sorry"
    # Model renames it (one of the real cases we observed)
    proof = "theorem baires_category_theorem : True := by trivial"
    assert _missing(theorem, proof) == ["exercise_3_22'"]
    # Correctly proved
    proof_ok = "theorem exercise_3_22' : True := by trivial"
    assert _missing(theorem, proof_ok) == []


def test_empty_theorem_text_skips_check():
    # If THEOREM.lean has no declarations (shouldn't happen in practice
    # for benchmarks, but just in case), the check is a no-op.
    assert _missing("", "whatever") == []
    assert _missing("-- just a comment", "whatever") == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
