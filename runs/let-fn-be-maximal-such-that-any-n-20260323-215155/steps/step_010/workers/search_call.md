---
call_num: 2
label: search_step_10
model: gpt-5.4
elapsed_ms: 220949
input_tokens: 106365
output_tokens: 10024
cache_read_tokens: 9344
stop_reason: completed
---

======== SYSTEM PROMPT ========

You are a mathematical research assistant. Search for relevant mathematical literature and results. Report findings concisely with precise mathematical content.

======== USER PROMPT ========

# Literature Search

Search query: Horton set recursive Erdos-Szekeres construction number of convex k-gons convex subsets density 2^{-k^2} upper bound


Context: We already have a verified lower bound
\[
f(n)\ge 2^{(\frac14-o(1))(\log_2 n)^2}
\]
for the minimum number of convex subsets in an n-point planar set in general position.

The next task is the upper bound: find an explicit construction and a quantitative count of its convex subsets.

Please search specifically for results on recursive Erdős-Szekeres constructions, Horton sets, or order-type limits that bound the number/density of convex k-subsets (or convex k-gons) by something like \(2^{-\Theta(k^2)}\), and identify statements strong enough to convert into an upper bound on the total number of convex subsets of an n-point set.

What I need from the search:
1. Concrete constructions, not just existence statements.
2. Explicit asymptotic bounds on the number or density of convex k-subsets in those constructions.
3. Any statement precise enough to sum over k and derive an upper bound of the form
\[
2^{(\alpha+o(1))(\log_2 n)^2}.
\]
4. If possible, identify the best constant \(\alpha\) supported by the literature or by a clean conversion of the cited result.

Please emphasize exact statements and how they would feed into the total-count upper bound problem.


Search the web for relevant theorems, proof techniques, known results, or partial progress. Report concisely: what's known, what techniques are used, any useful references. Focus on mathematical content.

======== RESPONSE ========

Most relevant hit: [Goaoc, Hubard, de Joannis de Verclos, Sereni, Volec, *Limits of Order Types* (SoCG 2015)](https://doi.org/10.4230/LIPIcs.SOCG.2015.300). This is the cleanest source I found that gives a `2^{-Theta(k^2)}` upper density for convex `k`-subsets in an explicit recursive construction.

They define an explicit binary recursive family `P_m` of size `2^m`:
`P_{m+1}=P_m^0 \cup P_m^1`, where `P_m^1` lies to the right of `P_m^0`, every point of `P_m^1` lies above every line through two points of `P_m^0`, and every point of `P_m^0` lies below every line through two points of `P_m^1` ([ibid., construction before Prop. 5](https://doi.org/10.4230/LIPIcs.SOCG.2015.300)). This is explicitly described there as a variation on Erdős-Szekeres/Horton-type constructions.

The quantitative part is in their proof of Prop. 5. If `Q_+(r,P_m)` counts `r`-cups, they prove the recurrence
\[
Q_+(r,P_{m+1})\le 2Q_+(r,P_m)+2^m Q_+(r-1,P_m),
\]
hence
\[
q_+(r,P_m)\le 2^{-r^2/2+r\log_2 r+O(r)},
\]
and similarly for caps. Since every `k`-tuple in convex position contains a `\lceil k/2\rceil`-cup or `\lceil k/2\rceil`-cap, the proof yields
\[
\frac{C_k(P_m)}{\binom{2^m}{k}}
\le 2^{-k^2/8+O(k\log k)}.
\]
This finite-level bound is a clean conversion of their Lemma 14 on the limit density `\ell_H(\triangle_k)`.

From that,
\[
C_k(P_m)\le \binom{2^m}{k}2^{-k^2/8+O(k\log k)}
=2^{km-k^2/8+O(k)}.
\]
Summing over `k`, the exponent is maximized at `k=4m+O(1)`, giving
\[
\sum_k C_k(P_m)\le 2^{2m^2+O(m)}
=2^{(2+o(1))(\log_2 n)^2}
\quad (n=2^m).
\]
So this literature supports the explicit upper bound
\[
f(n)\le 2^{(2+o(1))(\log_2 n)^2}.
\]
Among sources I found, this gives the best explicit constant
\[
\alpha=2.
\]

What else seems relevant but weaker for your purpose:

- [Horton 1983](https://doi.org/10.4153/CMB-1983-077-8): explicit recursive construction with no empty convex `7`-gon. Important structurally, but it controls empty polygons, not all convex subsets, so by itself it does not yield the desired total-count upper bound.
- [Baek–Balko, *The Erdős-Szekeres Conjecture Revisited* (SoCG 2025)](https://doi.org/10.4230/LIPIcs.SoCG.2025.13): introduces “decomposable sets” and says their new constructions generalize previous Erdős-Szekeres-type extremal constructions. Useful structurally, but I did not find in it a quantitative `2^{-ck^2}` count for convex `k`-subsets.
- [Valtr/Fulek et al. on cups and caps](https://doi.org/10.1016/j.ejc.2006.09.009): relevant because the counting mechanism above is cup/cap counting, but I did not find a sharper total-convex-subset upper bound there.

Bottom line: the strongest web-find I found that actually converts to a total-count upper bound is Goaoc et al.’s recursive `P_m`, and the clean conversion gives `\alpha=2`. I did not find a published explicit construction with a smaller constant.
