Focus only on the already-derived upper-bound note. Do not change the mathematics except to repair the base-level indexing/cardinality convention and any statements that depend on it.

Context:
- The current upper-bound argument is otherwise accepted.
- The levelwise generic-rotation normalization has already been fixed correctly.
- A verifier found one remaining inconsistency: the draft said “Let $P_1$ be a one-point set” but also used $|P_m|=2^m$ and the final step took an $n$-point subset of $P_{\lceil \log_2 n\rceil}$.
- Earlier accepted flaw statement for the discarded $\alpha=2$ claim: total cup/cap counts alone do not control convex $k$-sets without endpoint matching.

Task:
Produce the final repo-item text with one consistent indexing convention throughout. You may either:
- start with $P_0$ as a one-point set and reindex everything accordingly, or
- start with $P_1$ as a two-point set and keep $|P_m|=2^m$.
Choose one convention and make every definition, recurrence base case, cardinality statement, and the arbitrary-$n$ extension consistent with it.

Keep these components in the note:
1. Correct levelwise normalization for each fixed target level.
2. Definitions of $Q_\pm(r,P_m)$, $C_k(P_m)$, and $g(P_m)$.
3. The bound
$$
Q_\pm(r,P_m)\le d_r\,2^{rm},\qquad d_r=\prod_{j=2}^r(2^j-2)^{-1},
$$
with explicit base cases consistent with your indexing choice.
4. The chain-pair injection
$$
C_k(P_m)\le \sum_{a=2}^k Q_+(a,P_m)Q_-(k+2-a,P_m).
$$
5. The finite-level bound
$$
C_k(P_m)\le (k-1)\,2^{(k+2)m-\lfloor (k+1)^2/4\rfloor}
$$
or the exactly corresponding version under your chosen indexing.
6. The summed estimate
$$
g(P_m)\le 2^{m^2+m+O(\log m)}
$$
and the extension to arbitrary $n$ giving
$$
f(n)\le 2^{(\log_2 n)^2+O(\log n)}.
$$
7. A short final sentence identifying the flaw in the discarded $\alpha=2$ overclaim, using the endpoint-matching issue above.

Output format:
- First line exactly `Summary: ...`
- Then the full repo-item text
- End with `Remaining proof-tightness issues: ...`

Do not brainstorm alternatives; just return the corrected final note.