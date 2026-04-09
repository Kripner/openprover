Use [[lemmas/ternary-one-split-structure]] as the main input, with [[bounds/upper-bound-recursive-family]] and [[status/fixed-lag-separated-recursions-obstruction]] only as motivation/background.

Work on exactly one task: define the balanced ternary separated recursion and derive the exact recurrence/state propagation forced by the new ternary one-split lemma. Then determine whether one explicit top-scale contribution already gives an obstruction comparable to or worse than coefficient $1$, or whether ternary recursion remains genuinely open after this local classification.

Deliverable:
1. Define a precise balanced ternary family $T_m$.
   - Natural target: three child copies of $T_{m-1}$ in left-middle-right ternary separated position.
   - If one extra geometric normalization is needed so the bridge-region counts are well-defined recursively, state it explicitly.
2. Derive the exact counting decomposition for convex subsets of $T_m$.
   - Separate subsets contained in one child, spanning exactly two children, and spanning all three children.
   - Make explicit what state variables must be tracked recursively.
   - Distinguish exact identities from inequalities.
3. Decide one of the following, with justification:
   - an explicit top-split term already forces a quadratic coefficient at least $1$ (or larger), so balanced ternary recursion is already obstructed;
   - the exact recurrence closes but introduces new bridge-state quantities that remain nontrivial and keep ternary genuinely alive;
   - or the first exact place where the recursion fails to close in a manageable state space.
4. Output repo-ready markdown with a `Summary:` line.
   - If clearly obstructed, suitable slug: `status/ternary-separated-recursion-obstruction`.
   - If the main result is an exact but not yet resolved recurrence/state description, suitable slug: `attempts/alternative-construction-balanced-ternary-split`.

Requirements:
- Focus on balanced ternary recursion only.
- Build directly from [[lemmas/ternary-one-split-structure]]; do not redo the local geometry from scratch.
- Do not revisit binary endpoint matching or binary lag variants.
- Do not use literature or Lean.
- Be explicit about the minimal recursive state: if bridge counts force extra endpoint-dependent data, say exactly what it is.
- If you obtain only a lower-bound obstruction from one term of an exact recurrence, isolate that term cleanly and state that the conclusion is an inequality rather than an exact count.
