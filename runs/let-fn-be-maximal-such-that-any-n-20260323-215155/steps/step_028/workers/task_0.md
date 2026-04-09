Use [[lemmas/one-split-fixed-state-recurrence]], [[lemmas/one-split-crossing-cup-cap-identities]], and [[bounds/upper-bound-recursive-family]].

Work on exactly one task: repair the note currently intended for `status/recursive-family-information-loss` by filling the one remaining gap.

What is already solid:
- For fixed state $(\ell,\lambda,\rho,r)$,
  $$
  C^\times(a,b,P_m;\ell,\lambda,\rho,r)
  =
  \widetilde Q_+(a,L_m;\ell,\lambda)\,\widetilde Q_-(b,R_m;\rho,r).
  $$
- Summing over all states gives the exact factorization for fixed split size $(a,b)$.
- The likely first genuine loss is later, when endpoint-matched identities are replaced by products of coarse totals and the shared outer endpoints $(\ell,r)$ are forgotten.

Your job:
Produce a short polished note, ready to store directly as `status/recursive-family-information-loss`, that does all of the following:
1. States the exact fixed-split-size identity.
2. Explicitly derives the exact crossing passage, not just by assertion:
   - write the exact formulas for spanning cups/caps obtained by summing the fixed-state identities in the cases $a=1$ or $b=1$;
   - explain clearly why this still involves exact summation over the relevant endpoint parameter and no inequality.
3. Then identify the first actual inequality in the recursive-family upper-bound argument, specifying precisely which endpoint information is forgotten there.
4. State whether that loss alone explains the exponent constant $1$, with a brief justification.

Requirements:
- Keep it self-contained relative to the cited items.
- Be explicit about which displayed formulas are exact identities and which are only inequalities.
- Do not do new asymptotic optimization, literature, or Lean.
- The output should be repo-ready markdown with a `Summary:` line.

If you find any hidden earlier inequality before the endpoint-forgetting step, say so precisely and revise the conclusion accordingly.