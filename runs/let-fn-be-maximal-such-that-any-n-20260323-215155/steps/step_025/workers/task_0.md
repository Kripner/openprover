Use [[lemmas/one-split-structure-spanning-convex-subsets]], [[lemmas/one-split-crossing-cup-cap-identities]], and [[bounds/upper-bound-recursive-family]].

Work on exactly one task: produce the clean endpoint-refined recurrence note for spanning convex subsets across one recursive split.

Context:
- For the recursive family, $P_m=L_m\sqcup R_m$ with $L_m,R_m$ affine copies of $P_{m-1}$ in the one-split position covered by [[lemmas/one-split-structure-spanning-convex-subsets]].
- We now have the verified stronger crossing fact in [[lemmas/one-split-crossing-cup-cap-identities]]: every spanning cup has exactly one point in the left half and every spanning cap exactly one point in the right half, with exact endpoint-refined crossing identities.
- The earlier draft already suggested endpoint-refined quantities counting cups, caps, and spanning convex subsets with fixed state $(\ell,\lambda,\rho,r)$, but it was unclear which statements are exact equalities and which are only upper bounds.

Deliverable:
Produce a short polished note suitable to store directly as a repo item, with:
1. minimal precise definitions of the endpoint-refined quantities you actually need;
2. the rigorous one-split recurrences/identities/inequalities that follow for those quantities;
3. explicit use of the exact crossing identities where they are now justified;
4. a clear statement of whether the spanning-convex count with fixed state is an exact product or only an inequality under the stored hypotheses, with proof or explanation;
5. one brief sentence explaining how endpoint matching is enforced.

Requirements:
- Keep it self-contained relative to the two stored lemmas above.
- Do not do asymptotic analysis or solve the recurrence.
- Do not use literature.
- Do not write Lean.
- If a statement is only an upper bound, say so plainly; if an exact identity is available, prove it.
- Aim for a note ready to store under a slug such as `lemmas/one-split-endpoint-refined-recurrence`.