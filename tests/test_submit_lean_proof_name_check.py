"""Tests for the structural check in Prover._handle_submit_lean_proof.

The critical invariant: the submitted PROOF.lean must preserve
THEOREM.lean verbatim (from the first theorem/lemma/def onward),
with only the `sorry` holes replaced by actual proof bodies. This
single check catches:

  - renamed theorem
  - anonymous `example` instead of named theorem
  - changed signature / binders / hypotheses
  - leftover `sorry` in the proof
  - model proving a different (but related) statement

Comments are stripped and whitespace is normalized before comparison
so formatting differences (indentation, line wrapping, comments
added by the model) don't produce false rejections.
"""

import pytest

from openprover.prover import Prover


check = Prover._check_proof_preserves_theorem


# ── Success cases ─────────────────────────────────────────────────────

def test_basic_matching_proof():
    theorem = """
    import Mathlib
    theorem foo (x : ℝ) : x = x := by
      sorry
    """
    proof = """
    import Mathlib
    theorem foo (x : ℝ) : x = x := by
      rfl
    """
    assert check(theorem, proof) is None


def test_whitespace_differences_ok():
    theorem = "theorem foo (x : ℝ) : x = x := by sorry"
    proof = """
    import Mathlib

    theorem foo   (x : ℝ)  :   x = x := by
      rfl
    """
    assert check(theorem, proof) is None


def test_different_imports_ok():
    # The model can legitimately change imports (e.g. `import Mathlib`
    # vs the harness's `import MiniF2F.ProblemImports`). The check
    # should only require the theorem itself to match.
    theorem = """
    import MiniF2F.ProblemImports
    open scoped Real

    theorem foo : True := by sorry
    """
    proof = """
    import Mathlib
    open Real
    -- some comment added by the model

    theorem foo : True := by trivial
    """
    assert check(theorem, proof) is None


def test_added_model_comments_ok():
    theorem = "theorem foo : True := by sorry"
    proof = """
    import Mathlib
    -- Summary: This is a trivial theorem.
    theorem foo : True := by  /- inline reasoning -/ trivial
    """
    assert check(theorem, proof) is None


def test_helper_lemmas_ok():
    # Model may add helper lemmas BEFORE the main theorem
    theorem = "theorem exercise_X (n : ℕ) : n = n := by sorry"
    proof = """
    import Mathlib

    lemma my_helper : 1 + 1 = 2 := rfl

    theorem exercise_X (n : ℕ) : n = n := by rfl
    """
    assert check(theorem, proof) is None


def test_multiline_signature_ok():
    theorem = """
    theorem exercise_1_1a
      (x : ℝ) (y : ℚ) :
      (Irrational x) -> Irrational (x + y) := by
      sorry
    """
    proof = """
    import Mathlib
    theorem exercise_1_1a (x : ℝ) (y : ℚ) : (Irrational x) -> Irrational (x + y) := by
      intro h
      exact h.rat_add y
    """
    assert check(theorem, proof) is None


def test_apostrophe_name_ok():
    theorem = "theorem exercise_3_22' (P : Prop) : P → P := by sorry"
    proof = "theorem exercise_3_22' (P : Prop) : P → P := by exact id"
    assert check(theorem, proof) is None


def test_def_form_ok():
    # ProofNet uses `def` for structure-valued results
    theorem = """
    def exercise_2_1_21 (G : Type*) [Group G] [Fintype G]
      (hG : card G = 5) : CommGroup G := by sorry
    """
    proof = """
    import Mathlib
    def exercise_2_1_21 (G : Type*) [Group G] [Fintype G]
      (hG : card G = 5) : CommGroup G := by
      exact ⟨fun _ _ => by aesop⟩
    """
    assert check(theorem, proof) is None


# ── Failure cases ─────────────────────────────────────────────────────

def test_renamed_theorem_is_rejected():
    theorem = "theorem exercise_3_9 : (∫ x in (0:ℝ)..1, x) = 0.5 := by sorry"
    proof = """
    import Mathlib
    theorem integral_x_zero_one : (∫ x in (0:ℝ)..1, x) = 0.5 := by
      sorry
    """
    # Different name → rejection
    reason = check(theorem, proof)
    assert reason is not None
    assert "theorem header" in reason.lower() or "not found" in reason.lower()


def test_anonymous_example_is_rejected():
    theorem = "theorem exercise_X : True := by sorry"
    proof = """
    import Mathlib
    example : True := by trivial
    """
    assert check(theorem, proof) is not None


def test_changed_signature_is_rejected():
    # Classic cheat: keep the name, weaken to a trivial statement
    theorem = """
    theorem exercise_3_9 : (∫ x in (0:ℝ)..1, Real.log (Real.sin (Real.pi * x)))
      = -Real.log 2 := by sorry
    """
    proof = """
    import Mathlib
    theorem exercise_3_9 : True := by trivial
    """
    reason = check(theorem, proof)
    assert reason is not None


def test_added_hypothesis_is_rejected():
    # Model adds an extra hypothesis to make proof easier
    theorem = """
    theorem exercise_1_13c {f : ℂ → ℂ} (Ω : Set ℂ) (h : IsOpen Ω) :
      True := by sorry
    """
    proof = """
    import Mathlib
    theorem exercise_1_13c {f : ℂ → ℂ} (Ω : Set ℂ) (h : IsOpen Ω)
      (extra_hypothesis : True) : True := by trivial
    """
    assert check(theorem, proof) is not None


def test_removed_hypothesis_is_rejected():
    theorem = """
    theorem exercise_1_5 (A : Set ℝ) (hA : A.Nonempty) (hBdd : BddBelow A) :
      sInf A = sInf A := by sorry
    """
    # Model drops both hypotheses
    proof = """
    import Mathlib
    theorem exercise_1_5 (A : Set ℝ) : sInf A = sInf A := by rfl
    """
    assert check(theorem, proof) is not None


def test_alpha_renaming_is_rejected():
    # Strict: binder names must match verbatim
    theorem = "theorem foo (x : ℝ) : x = x := by sorry"
    proof = "theorem foo (y : ℝ) : y = y := by rfl"
    assert check(theorem, proof) is not None


def test_leftover_sorry_is_rejected():
    theorem = "theorem foo (x : ℝ) : x = x := by sorry"
    proof = """
    import Mathlib
    theorem foo (x : ℝ) : x = x := by
      sorry
    """
    reason = check(theorem, proof)
    assert reason is not None


def test_sorry_inside_string_is_not_ok():
    # Pragmatic: `sorry` appearing even inside a string is treated as
    # leftover. Real Lean proofs don't normally contain string
    # literals with the word sorry.
    theorem = "theorem foo (x : ℝ) : x = x := by sorry"
    proof = '''
    theorem foo (x : ℝ) : x = x := by
      have _ := "sorry"
      rfl
    '''
    # The regex matches "sorry" inside the string → detected.
    # This is a conservative false-positive; acceptable for our purposes.
    reason = check(theorem, proof)
    assert reason is not None


# ── Multiple sorries ─────────────────────────────────────────────────

def test_multiple_sorries_all_replaced_ok():
    theorem = """
    theorem exercise_A : True := by sorry
    theorem exercise_B : True := by sorry
    """
    proof = """
    theorem exercise_A : True := by trivial
    theorem exercise_B : True := by trivial
    """
    assert check(theorem, proof) is None


def test_multiple_sorries_one_left_behind_rejected():
    theorem = """
    theorem exercise_A : True := by sorry
    theorem exercise_B : True := by sorry
    """
    # Second sorry is actually still there
    proof = """
    theorem exercise_A : True := by trivial
    theorem exercise_B : True := by sorry
    """
    assert check(theorem, proof) is not None


def test_multiple_sorries_one_theorem_renamed_rejected():
    theorem = """
    theorem exercise_A : True := by sorry
    theorem exercise_B : True := by sorry
    """
    # exercise_B renamed
    proof = """
    theorem exercise_A : True := by trivial
    theorem something_else : True := by trivial
    """
    assert check(theorem, proof) is not None


# ── Edge cases ─────────────────────────────────────────────────────────

def test_theorem_with_no_sorry_skips_check():
    # If THEOREM.lean has no sorry, there's nothing to verify
    theorem = "theorem foo : True := trivial"
    proof = "whatever"
    assert check(theorem, proof) is None


def test_empty_theorem_text():
    assert check("", "whatever") is None


def test_theorem_without_any_declaration():
    # THEOREM.lean is somehow just comments/imports — nothing to check
    assert check("-- just a comment", "whatever") is None


# ── Regression: the real observed failures ───────────────────────────

def test_real_case_exercise_3_9():
    # The model renamed exercise_3_9 to integral_log_sin_pi_x_zero_one
    # and changed everything — name + signature
    theorem = """
    theorem exercise_3_9 :
      (∫ x in (0:ℝ)..1, Real.log (Real.sin (Real.pi * x))) = -Real.log 2 := by
      sorry
    """
    proof = """
    import Mathlib
    theorem integral_log_sin_pi_x_zero_one :
      (∫ x in (0:ℝ)..1, Real.log (Real.sin (Real.pi * x))) = -Real.log 2 := by
      sorry
    """
    assert check(theorem, proof) is not None


def test_real_case_exercise_1_13c_added_binder():
    theorem = """
    theorem exercise_1_13c {f : ℂ → ℂ} (Ω : Set ℂ) (a b : Ω)
      (h : IsOpen Ω) (hf : DifferentiableOn ℂ f Ω) : True := by sorry
    """
    # Model added (hpc : IsPreconnected Ω) hypothesis
    proof = """
    import Mathlib
    theorem exercise_1_13c {f : ℂ → ℂ} (Ω : Set ℂ) (a b : Ω)
      (h : IsOpen Ω) (hpc : IsPreconnected Ω)
      (hf : DifferentiableOn ℂ f Ω) : True := by trivial
    """
    assert check(theorem, proof) is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
