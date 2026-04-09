Use [[attempts/one-split-structure-draft]] and the recursive construction in [[bounds/upper-bound-recursive-family]].

Your one task is to turn the draft into a clean, self-contained lemma note.

What to do:
- State the exact geometric hypotheses on the split $P_m=L_m\sqcup R_m$ that are really needed.
- Repair the two specific rigor gaps flagged by verification:
  1. explain explicitly why, if the upper hull had more than one vertex from $L_m$, then two such vertices are consecutive on that left-to-right hull chain;
  2. fix the endpoint wording so the statement about chain membership is literally correct.
- Give a short rigorous proof of the structural decomposition of any convex subset $S\subset P_m$ meeting both halves.
- State the minimal endpoint/state data needed for a later recurrence, and explain briefly why it enforces common global endpoints.

Scope restrictions:
- Do not do any counting, recurrence derivation, asymptotics, or optimization.
- Do not use literature.
- Do not write Lean.

Deliverable:
Return a polished note suitable to store directly as a lemma item, with a suggested slug such as
`lemmas/one-split-structure-spanning-convex-subsets`.
