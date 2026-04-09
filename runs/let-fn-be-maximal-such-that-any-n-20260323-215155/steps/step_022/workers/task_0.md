Use [[lemmas/one-split-structure-spanning-convex-subsets]] together with the recursive family in [[bounds/upper-bound-recursive-family]].

Work on one narrow task only.

Context:
- $P_1$ is a two-point set.
- For $m\ge 2$, $P_m=L_m\sqcup R_m$, where $L_m,R_m$ are affine copies of $P_{m-1}$ in the recursively separated position covered by [[lemmas/one-split-structure-spanning-convex-subsets]].
- Any convex subset spanning the split has endpoint state $(\ell,\lambda,\rho,r)$ and decomposes as a left cap plus a right cup.

Your task:
Define the smallest useful endpoint-refined counting quantities based on this state data, and derive the sharpest rigorous recurrence(s) you can for those quantities under the split $P_m=L_m\sqcup R_m$.

Deliverable:
- precise definitions of the endpoint-refined quantities;
- rigorous recurrence identities or inequalities at one recursive split;
- a brief explanation of exactly how endpoint matching is enforced by the state.

Scope restrictions:
- Do not do asymptotic optimization, solve the recurrence, or try to finish the whole problem.
- Do not use literature.
- Do not write Lean.
- Keep the note self-contained and suitable to store directly as a lemma/proposition item.

Because earlier broader tasks timed out, keep this tightly scoped: recurrence only.
