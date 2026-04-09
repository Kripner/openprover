Use [[lemmas/one-split-structure-spanning-convex-subsets]], [[lemmas/one-split-crossing-cup-cap-identities]], [[bounds/upper-bound-recursive-family]], and [[attempts/one-split-fixed-state-product-draft-flaw]].

Work on exactly one task: determine the correct fixed-state counting statement for spanning convex subsets across one split.

What is known:
- The one-split structural lemma gives a state $(\ell,\lambda,\rho,r)$ for every spanning convex subset.
- The crossing proposition is already verified and exact.
- The previous fixed-state product note failed because its core slope inequalities were reversed; see [[attempts/one-split-fixed-state-product-draft-flaw]].

Deliverable:
Produce a short polished note suitable to store directly as a repo item, doing the following and nothing more:
1. Re-derive from the stored split lemma the correct local object types on $L$ and $R$ attached to a spanning convex subset with fixed state $(\ell,\lambda,\rho,r)$.
2. Determine whether the fixed-state count is:
   - an exact product of two endpoint-refined local counts, or
   - only an inequality / bound.
3. If an exact product is correct, state it with the correct local quantities and give a fully rigorous proof, including the edge cases $a=1$ and/or $b=1$.
4. If exact product fails, give the sharpest rigorous replacement and explain precisely where bijectivity breaks.
5. State whether summing over states gives an exact identity or only an inequality, and justify that point.

Requirements:
- Do not assume the previous draft’s cup/cap assignment is correct; re-derive it from scratch from the stored lemmas.
- Keep the note self-contained relative to the cited items.
- No asymptotic analysis, no literature, no Lean.
- Be explicit about which statements are exact and which are only bounds.
- Include one brief sentence explaining how endpoint matching is enforced at the fixed-state level.

A suitable slug would be `lemmas/one-split-fixed-state-recurrence`.
