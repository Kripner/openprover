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


# ── Signature extraction ─────────────────────────────────────────────
# The signature is binders + conclusion type — i.e. everything between
# `theorem <name>` and `:=`. Whitespace collapsed to single spaces.

sig = Prover._extract_theorem_signature


def test_sig_simple():
    src = "theorem foo (x : ℝ) : x = x := by rfl"
    assert sig(src, "foo") == "(x : ℝ) : x = x"


def test_sig_missing_returns_none():
    src = "theorem bar : True := trivial"
    assert sig(src, "foo") is None


def test_sig_multiline():
    # Real ProofNet layout: signature spans multiple lines
    src = """
    theorem exercise_1_1a
      (x : ℝ) (y : ℚ) :
      ( Irrational x ) -> Irrational ( x + y ) := by
      sorry
    """
    # Expected: whitespace normalized to single spaces
    assert sig(src, "exercise_1_1a") == "(x : ℝ) (y : ℚ) : ( Irrational x ) -> Irrational ( x + y )"


def test_sig_whitespace_normalization():
    # Tabs, multiple spaces, newlines all collapse to single spaces
    a = "theorem foo   (x : ℝ)  :   x = x := rfl"
    b = "theorem foo\n  (x : ℝ) :\n  x = x := rfl"
    assert sig(a, "foo") == sig(b, "foo")


def test_sig_comments_stripped_before_extraction():
    src = """
    theorem foo -- inline comment
      /- block comment -/ (x : ℝ) :
      x = x := by rfl
    """
    assert sig(src, "foo") == "(x : ℝ) : x = x"


def test_sig_apostrophe_name():
    src = "theorem exercise_3_22' (P : Prop) : P := sorry"
    assert sig(src, "exercise_3_22'") == "(P : Prop) : P"


def test_sig_def_form():
    src = "def exercise_2_1_21 (G : Type*) [Group G] : CommGroup G := ⟨⟩"
    assert sig(src, "exercise_2_1_21") == "(G : Type*) [Group G] : CommGroup G"


def test_sig_handles_term_mode_proof():
    # `:=` without `by` still starts the proof body
    src = "theorem foo : True := trivial"
    assert sig(src, "foo") == ": True"


def test_sig_no_name_clash_with_prefix():
    # `foo` declared, looking for `foo` — not `foobar`
    src = """
    theorem foobar : True := trivial
    theorem foo (x : ℕ) : x = x := rfl
    """
    assert sig(src, "foo") == "(x : ℕ) : x = x"
    assert sig(src, "foobar") == ": True"


# ── End-to-end: signature-mismatch detection ────────────────────────
# The exact check the fix performs.

def _check(theorem_text: str, proof_text: str) -> dict:
    """Return {'missing': [...], 'sig_mismatches': [(name, orig, sub), ...]}"""
    expected = extract(theorem_text)
    declared = extract(proof_text)
    missing = [n for n in expected if n not in declared]
    sig_mismatches = []
    for name in expected:
        if name in missing:
            continue
        orig = sig(theorem_text, name)
        submitted = sig(proof_text, name)
        if orig is not None and orig != submitted:
            sig_mismatches.append((name, orig, submitted))
    return {"missing": missing, "sig_mismatches": sig_mismatches}


def test_correct_name_and_signature_is_accepted():
    theorem = """
    theorem exercise_1_1a (x : ℝ) (y : ℚ) :
      (Irrational x) -> Irrational (x + y) := by sorry
    """
    proof = """
    import Mathlib
    theorem exercise_1_1a (x : ℝ) (y : ℚ) :
      (Irrational x) -> Irrational (x + y) := by
      intro h_irr
      exact h_irr.rat_add y
    """
    r = _check(theorem, proof)
    assert r["missing"] == []
    assert r["sig_mismatches"] == []


def test_correct_name_but_WRONG_signature_is_rejected():
    # The sneaky case: the model keeps the name but proves something trivial.
    # Before this fix, this was reported as proved.
    theorem = """
    theorem exercise_3_9 : (∫ x in (0:ℝ)..1, Real.log (Real.sin (Real.pi * x)))
      = -Real.log 2 := by sorry
    """
    proof = """
    import Mathlib
    theorem exercise_3_9 : True := by trivial
    """
    r = _check(theorem, proof)
    assert r["missing"] == []
    assert len(r["sig_mismatches"]) == 1
    name, orig, sub = r["sig_mismatches"][0]
    assert name == "exercise_3_9"
    assert "True" not in orig
    assert sub == ": True"


def test_alpha_renaming_is_flagged_as_mismatch():
    # Strict check: the model must preserve binder names verbatim.
    # Alpha-renaming (x→y) is mathematically equivalent but isn't
    # what the benchmark asked for.
    theorem = "theorem foo (x : ℝ) : x = x := by sorry"
    proof = """
    import Mathlib
    theorem foo (y : ℝ) : y = y := by rfl
    """
    r = _check(theorem, proof)
    assert r["missing"] == []
    assert len(r["sig_mismatches"]) == 1


def test_signature_whitespace_differences_ignored():
    theorem = "theorem foo (x : ℝ) : x = x := sorry"
    proof = """
    import Mathlib
    theorem foo   (x : ℝ)
         :
         x = x := rfl
    """
    r = _check(theorem, proof)
    assert r["missing"] == []
    assert r["sig_mismatches"] == []


def test_comments_in_signature_ignored():
    theorem = """
    theorem foo (x : ℝ) /- main binder -/ : x = x := sorry
    """
    proof = """
    theorem foo (x : ℝ) : -- copied from THEOREM.lean
      x = x := rfl
    """
    r = _check(theorem, proof)
    assert r["missing"] == []
    assert r["sig_mismatches"] == []


def test_multiple_theorems_all_signatures_checked():
    theorem = """
    theorem exercise_A (x : ℝ) : x = x := sorry
    theorem exercise_B (n : ℕ) : n + 0 = n := sorry
    """
    # exercise_B's signature changed
    proof = """
    import Mathlib
    theorem exercise_A (x : ℝ) : x = x := rfl
    theorem exercise_B : True := trivial
    """
    r = _check(theorem, proof)
    assert r["missing"] == []
    assert len(r["sig_mismatches"]) == 1
    assert r["sig_mismatches"][0][0] == "exercise_B"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
