Use [[lemmas/one-split-structure-spanning-convex-subsets]] and [[bounds/upper-bound-recursive-family]].

Work on exactly one task: repair the proof that under the stored one-split hypotheses,

- every spanning cup has exactly one point in the left half, namely its global left endpoint;
- every spanning cap has exactly one point in the right half, namely its global right endpoint;

and then derive the exact crossing endpoint-refined identities.

Context you should use:
- The stored split lemma already proves that any spanning convex subset $S\subseteq P=L\sqcup R$ has state $(\ell,\lambda,\rho,r)$ and decomposes as
$$
S=(\text{cap in }L\text{ with endpoints }(\ell,\lambda))\sqcup(\text{cup in }R\text{ with endpoints }(\rho,r)).
$$
- The previous worker proof correctly observed that if $S$ is itself a cup, then its lower hull has only the two endpoints, so the split lemma should force $S\cap L=\{\ell\}$; dually for caps.
- The remaining problem is only the rigorous extension/bijection argument needed to get the exact identities.

The previous draft was flagged for two specific defects, which you must fix:
1. The surjectivity argument did not treat the case $t=2$ separately.
2. It falsely claimed every point of $T\setminus\{r\}$ lies above the line $u_1r$; only interior points do. The role of $u_1$ relative to the line $\ell r$ must be handled separately.

Deliverable:
Produce a short polished proposition note suitable to store directly as a repo item, containing:
- the exact statement of the stronger split fact;
- a fully rigorous proof;
- the exact crossing identities for endpoint-refined cup/cap counts;
- a brief sentence explaining how endpoint matching is enforced.

Requirements:
- Be self-contained relative to the stored split lemma.
- Keep definitions minimal but precise.
- Do not do asymptotic analysis.
- Do not use literature.
- Do not write Lean.
- If you discover that the stronger fact actually needs an extra hypothesis, say so explicitly and isolate the missing hypothesis; otherwise finish the proof under the current stored hypotheses.

A suggested slug is `lemmas/one-split-crossing-cup-cap-identities`.
