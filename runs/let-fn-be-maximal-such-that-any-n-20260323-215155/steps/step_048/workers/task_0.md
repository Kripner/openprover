Focus only on the lower-bound averaging route.

Context:
- [[bounds/lower-bound-averaging]] gives, for every $n$-point set $P$ and every $k$ with $ES(k)\le n$,
  $$
  \mathrm{conv}_k(P)\ge \frac{\binom{n}{k}}{\binom{ES(k)}{k}}.
  $$
- A previous worker analyzed
  $$
  S(n):=\sum_{k:ES(k)\le n}\frac{\binom{n}{k}}{\binom{ES(k)}{k}}
  $$
  and concluded that
  $$
  \log_2 S(n)=\left(\frac14+o(1)\right)(\log_2 n)^2,
  $$
  but the writeup had two minor rigor gaps:
  1. the summation from the per-size lower bounds needs to be stated cleanly via
     $g(P)=\sum_j \mathrm{conv}_j(P)$ and disjoint size classes;
  2. the upper-bound argument handled only $k\ge 3$, so $k=1,2$ should be separated off.

Task:
Produce a self-contained, repo-item-ready markdown note proving the barrier statement:
- Let $L=\log_2 n$.
- Show rigorously that
  $$
  \log_2 S(n)=\left(\frac14+o(1)\right)L^2.
  $$
- Deduce the clean consequence:
  any lower bound obtained solely by summing these verified per-$k$ averaging estimates over admissible $k$ still has quadratic constant $\frac14$, so “pure averaging over $k$” does not improve the current lower bound at the $(\log n)^2$ scale.

Requirements:
- Keep the proof self-contained.
- Handle $k=1,2$ explicitly.
- Use only the verified ingredients already in the repo plus the standard lower bound $ES(k)\ge 2^{k-2}+1$ and Suk’s asymptotic $ES(k)=2^{k+o(k)}$.
- If successful, format the output exactly as a repo item with a `Summary:` line and then the full note.
- If you find a real issue with the barrier claim, explain precisely where the previous argument breaks.
- Do not branch into upper-bound constructions, literature, or alternative mechanisms.
