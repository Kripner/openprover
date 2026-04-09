Use [[lemmas/ternary-one-split-structure]], [[attempts/alternative-construction-balanced-ternary-split]], and [[attempts/balanced-ternary-bridge-conjugation-expansion]].

Work on exactly one task: choose one explicit balanced ternary separated template $(\Phi_L,\Phi_M,\Phi_R)$ and compute the bridge-map conjugates concretely, enough to decide whether the bridge state really closes in that template or whether a genuine new bridge type already appears at first expansion.

What is already established:
- The local ternary one-split lemma is verified.
- The total count decomposition into one-child, two-child, and bridge-weighted three-child terms is exact.
- The abstract recursive identity for generalized bridge counts is exact:
$$
H_n^\pm[\alpha,\beta](\Phi_i(x'),\Phi_j(y'))
=
\sum_{k\in\{L,M,R\}}
H_{n-1}^\pm[\Phi_k^{-1}\alpha\Phi_i,\Phi_k^{-1}\beta\Phi_j](x',y').
$$
- The current gap is that abstract appearance of conjugated pairs does not yet prove non-closure in the fixed balanced ternary template.

Deliverable:
1. Pick an explicit convenient balanced ternary template satisfying the separated-position hypotheses.
2. Compute
$$
\alpha_0=\Phi_M^{-1}\Phi_L,\qquad \beta_0=\Phi_M^{-1}\Phi_R,
$$
and then the first-generation pairs
$$
\Phi_k^{-1}\alpha_0\Phi_i,\qquad \Phi_k^{-1}\beta_0\Phi_j
\quad (i,j,k\in\{L,M,R\}).
$$
3. Decide exactly one of the following:
   - these pairs collapse, in this template, to a finite family already representable by a clean enlargement of the bridge state; give that exact state and recursion;
   - or at least one genuinely new pair appears already at first expansion, and this gives the first exact obstruction to closure of the currently tracked state.
4. If you claim obstruction, do not stop at “new pairs appear abstractly.” You must show concretely in the chosen template that at least one required pair is not one of the currently tracked bridge types (nor reducible by an actual symmetry of the template that you specify).
5. Keep exact identities separate from inequalities.
6. Output repo-ready markdown with a `Summary:` line.
   - If closure works, suitable slug: `status/balanced-ternary-recursion-closure`.
   - If obstruction is proved, suitable slug: `status/balanced-ternary-concrete-bridge-obstruction`.

Requirements:
- Focus only on the concrete conjugacy/closure question.
- Do not revisit asymptotics, binary variants, or nonrecursive constructions.
- A concrete matrix/affine computation is preferred over general discussion.
- If you need to enlarge the bridge state finitely, state the minimal exact finite family you found.
