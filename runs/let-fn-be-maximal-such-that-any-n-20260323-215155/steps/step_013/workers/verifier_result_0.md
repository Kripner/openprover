The normalization fix is correct: for each fixed target level $M$, a sufficiently small generic rotation preserves the finitely many strict separation inequalities on the finite tower $P_1,\dots,P_M$ while also making all $x$-coordinates distinct. The derivations of
$$
Q_\pm(r,P_m)\le d_r\,2^{rm},\qquad
C_k(P_m)\le \sum_{a=2}^k Q_+(a,P_m)Q_-(k+2-a,P_m),
$$
the bound
$$
C_k(P_m)\le (k-1)\,2^{(k+2)m-\lfloor (k+1)^2/4\rfloor},
$$
and the Gaussian-tail summation to
$$
g(P_m)\le 2^{m^2+m+O(\log m)}
$$
are all fine.

There is, however, one concrete consistency error in the note as written. It starts with “Let $P_1$ be a one-point set,” but later uses $|P_m|=2^m$ and, in the final step, takes an $n$-point subset of $P_{\lceil \log_2 n\rceil}$. If $P_1$ really has one point, then $|P_m|=2^{m-1}$, so that last step is not literally valid. This is a minor indexing/base-case fix: either start with $P_0$ as a one-point set, or start with $P_1$ as a two-point set, and keep the rest consistent. Apart from that, I do not see remaining proof-tightness issues.

VERDICT: NEEDS MINOR FIXES - base-level indexing/cardinality is inconsistent ($P_1$ is called one-point but later $|P_m|=2^m$ is used)