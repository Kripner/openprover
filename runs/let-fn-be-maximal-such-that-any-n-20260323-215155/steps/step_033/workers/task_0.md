Use [[bounds/upper-bound-recursive-family]], [[status/recursive-family-information-loss]], [[lemmas/one-split-fixed-state-recurrence]], [[lemmas/one-split-crossing-cup-cap-identities]], and [[lemmas/one-split-structure-spanning-convex-subsets]].

Work on exactly one task: keep the common outer endpoints $(\ell,r)$ throughout the recursive construction and determine whether the present recursive family admits an endpoint-refined recurrence or classification that is genuinely sharper than the aggregate $Q_\pm$ bounds.

Deliverable:
1. Define a natural endpoint-matched quantity for the recursive family, ideally organized by the recursive class of the pair $(\ell,r)$ (for example by the first split level where the endpoints separate, or any cleaner equivalent).
2. Derive exact recurrences or usable upper bounds for those endpoint-matched quantities from the recursive construction.
3. Decide whether this gives any genuine improvement over the coarse bound leading to coefficient $1$ at the $(\log n)^2$ scale.
4. Output repo-ready markdown with a `Summary:` line.
   - If there is a nontrivial gain, state the improved bound clearly.
   - If there is no gain, state the precise obstruction inside this recursive family and why endpoint matching still does not change the leading constant.

Requirements:
- Stay entirely within the current recursive family.
- Do not switch to alternative constructions, literature, or Lean.
- Be explicit about which formulas are exact identities and which are inequalities.
- Keep the note self-contained relative to the cited repo items.
- Suitable slug if positive: `status/endpoint-matched-recursive-family`.
- Suitable slug if negative/diagnostic: `attempts/endpoint-matched-recursive-family-no-gain`.