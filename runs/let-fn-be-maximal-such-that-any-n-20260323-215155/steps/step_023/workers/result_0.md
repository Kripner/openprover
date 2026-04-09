**Proposition (Endpoint-refined crossing cup/cap identities for one split).**

Assume \(P=L\sqcup R\) satisfies the hypotheses of [[lemmas/one-split-structure-spanning-convex-subsets]]:

1. every point of \(L\) lies to the left of every point of \(R\);
2. every line through two points of \(L\) lies strictly below every point of \(R\);
3. every line through two points of \(R\) lies strictly above every point of \(L\).

For endpoint-refined counting, keep the degenerate size-\(1\) convention
\[
q_X^\pm(1;u,u)=1,\qquad q_X^\pm(1;u,v)=0\ \ (u\neq v),
\]
and for \(t\ge 2\) let \(q_X^+(t;u,v)\), \(q_X^-(t;u,v)\) denote the numbers of \(t\)-cups and \(t\)-caps in \(X\) with leftmost point \(u\) and rightmost point \(v\).

For \(\ell\in L\), \(r\in R\), let \(q_{P,\times}^+(t;\ell,r)\) and \(q_{P,\times}^-(t;\ell,r)\) be the numbers of spanning \(t\)-cups and spanning \(t\)-caps in \(P\) with global endpoints \((\ell,r)\).

Then the stronger split fact is true:

1. Every spanning cup \(S\subseteq P\) has exactly one point in \(L\), namely its leftmost point \(\ell\). Equivalently its split state is \((\ell,\ell,\rho,r)\).
2. Every spanning cap \(S\subseteq P\) has exactly one point in \(R\), namely its rightmost point \(r\). Equivalently its split state is \((\ell,\lambda,r,r)\).

Consequently, for every \(t\ge 2\),
\[
q_{P,\times}^+(t;\ell,r)=\sum_{\rho\in R} q_R^+(t-1;\rho,r),
\qquad
q_{P,\times}^-(t;\ell,r)=\sum_{\lambda\in L} q_L^-(t-1;\ell,\lambda).
\]

If \(Q_{+,\times}(t,P)\) and \(Q_{-,\times}(t,P)\) denote the total numbers of spanning \(t\)-cups and spanning \(t\)-caps, then summing over endpoints gives
\[
Q_{+,\times}(t,P)=|L|\,Q_+(t-1,R),\qquad
Q_{-,\times}(t,P)=|R|\,Q_-(t-1,L).
\]

**Proof.**
Let \(S\) be a spanning cup, and let \((\ell,\lambda,\rho,r)\) be its state from [[lemmas/one-split-structure-spanning-convex-subsets]]. Since \(S\) is a cup, its lower hull has only the two endpoints \(\ell,r\). The split lemma says that the points of \(S\cap L\) are exactly the \(L\)-vertices on the lower hull. Hence \(S\cap L=\{\ell\}\), so \(\lambda=\ell\). The cap case is symmetric: if \(S\) is a spanning cap, then its upper hull has only the two endpoints, and the split lemma says that the points of \(S\cap R\) are exactly the \(R\)-vertices on the upper hull, so \(S\cap R=\{r\}\), hence \(\rho=r\).

Now fix \(\ell\in L\), \(r\in R\). By the first part, every spanning \(t\)-cup with endpoints \((\ell,r)\) is uniquely of the form
\[
S=\{\ell\}\sqcup T,
\]
where \(T\subseteq R\) is a \((t-1)\)-cup with right endpoint \(r\) and left endpoint \(\rho=\min_x T\). This gives an injection into the disjoint union on the right-hand side.

For surjectivity, let \(T=\{u_1=\rho,\dots,u_{t-1}=r\}\subseteq R\) be any \((t-1)\)-cup, and set \(S=\{\ell\}\cup T\). For each upper-hull edge \(u_i u_{i+1}\) of \(T\), all points of \(T\) lie on or below its line, and hypothesis (3) puts \(\ell\) strictly below that line, so these edges remain upper-hull edges in \(S\). For the new first edge \(\ell u_1\), if \(j>1\), then \(\ell\) lies below the secant \(u_1u_j\); since \(x_\ell<x_{u_1}<x_{u_j}\), this implies
\[
\operatorname{slope}(\ell,u_1)>\operatorname{slope}(u_1,u_j),
\]
so \(u_j\) lies below the line \(\ell u_1\). Thus
\[
U(S)=\ell,u_1,\dots,u_{t-1}.
\]
Also \(D(T)=u_1,r\), so every point of \(T\setminus\{r\}\) lies above the line \(u_1r\); because \(\ell\) lies below \(u_1r\) by (3), the line \(\ell r\) lies strictly below \(u_1r\) on \([x_{u_1},x_r)\), hence every point of \(T\setminus\{r\}\) lies above \(\ell r\). Therefore
\[
D(S)=\ell,r,
\]
so \(S\) is a spanning \(t\)-cup with endpoints \((\ell,r)\). This proves the first identity. The cap identity is symmetric, using hypothesis (2). \(\square\)

Endpoint matching is enforced by the endpoint state: for a spanning cup the left-hand state is forced to be the singleton \((\ell,\ell)\), and for a spanning cap the right-hand state is forced to be the singleton \((r,r)\). Thus the exact crossing identities survive; they do not need to be weakened.