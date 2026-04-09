Focus only on the lower-bound side.

Context:
- The verified lower bound is [[bounds/lower-bound-averaging]].
- Three averaging-based upgrades are now closed barriers:
  [[status/multi-k-averaging-barrier]],
  [[status/multiplicity-aware-averaging-barrier]],
  [[status/m-subset-total-count-bootstrapping-barrier]].
- So the next move must be genuinely non-averaging.

Mechanism to test:
Use the classical Erdős-Szekeres cups/caps inductive framework itself, not averaging over subsets. Work in the usual left-to-right ordering by $x$-coordinate. For each point one can consider the standard endpoint state data from the cups/caps proof (for example longest cup/cap lengths ending at that point, or an equivalent state formulation used in the classical recurrence).

Focused question:
Can this classical state-based / inductive mechanism force many convex subsets, in a way that could beat the quadratic coefficient $\frac14$ for $f(n)$? Or does this specific mechanism also collapse to a precise barrier?

What I need:
1. A clean formulation of one concrete non-averaging counting mechanism inside the classical cups/caps proof.
2. Either:
   - a usable lemma or recurrence that yields a genuine lower-bound improvement, or
   - a precise obstruction/barrier note for this specific state-counting mechanism.
3. Repo-item-ready markdown if successful.

Requirements:
- Keep the task tightly on this one mechanism only.
- Do not use averaging over subset sizes or over $m$-subsets; those are already closed.
- Do not branch into upper-bound constructions or literature.
- If you get a barrier, say exactly where the state-counting argument loses strength.
- If you get a positive result, make the lemma/recurrence explicit enough to build on next.
