The local tool wrapper failed, so I could not patch the file directly. Here is the repo-ready markdown for `status/recursive-family-information-loss`:

```md
Summary: The fixed-split and crossing decompositions are exact identities; the first loss of endpoint information occurs only when the exact endpoint-matched chain-pair count is replaced by a product of total cup/cap counts, although the auxiliary cup/cap-growth lemma already contains earlier inequalities unrelated to endpoint matching.

Let
$$
C^\times(a,b,P_m)
$$
denote the number of spanning convex subsets $S\subseteq P_m=L_m\sqcup R_m$ with
$$
|S\cap L_m|=a,\qquad |S\cap R_m|=b.
$$
By [[lemmas/one-split-fixed-state-recurrence]], for each fixed state $(\ell,\lambda,\rho,r)$ one has the exact identity
$$
C^\times(a,b,P_m;\ell,\lambda,\rho,r)
=
\widetilde Q_+(a,L_m;\ell,\lambda)\,\widetilde Q_-(b,R_m;\rho,r).
\tag{Exact}
$$
Summing over states is still exact, because each spanning convex subset has a unique state. Hence
$$
C^\times(a,b,P_m)
=
\sum_{\ell,\lambda\in L_m}\ \sum_{\rho,r\in R_m}
\widetilde Q_+(a,L_m;\ell,\lambda)\,\widetilde Q_-(b,R_m;\rho,r).
\tag{Exact}
$$
Here inadmissible terms vanish by definition of the degenerate refinements.

The crossing passage is obtained by specializing this exact state-sum to the degenerate cases $b=1$ or $a=1$.

For spanning cups, take $b=1$. Then necessarily $\rho=r$, and
$$
\widetilde Q_-(1,R_m;\rho,r)=
\begin{cases}
1,&\rho=r,\\
0,&\rho\ne r.
\end{cases}
$$
So for fixed outer endpoints $\ell\in L_m$ and $r\in R_m$,
$$
C^\times(a,1,P_m;\ell,\lambda,r,r)
=
\widetilde Q_+(a,L_m;\ell,\lambda).
$$
Summing exactly over the possible last left-side vertex $\lambda$ gives
$$
Q_+^\times(a+1,P_m;\ell,r)
=
\sum_{\lambda\in L_m,\ \ell<\lambda} Q_+(a,L_m;\ell,\lambda).
\tag{Exact}
$$
There is no inequality here: different $\lambda$ give disjoint state classes, and the outer endpoints $(\ell,r)$ remain fixed throughout.

For spanning caps, take $a=1$. Then necessarily $\lambda=\ell$, and
$$
\widetilde Q_+(1,L_m;\ell,\lambda)=
\begin{cases}
1,&\lambda=\ell,\\
0,&\lambda\ne\ell.
\end{cases}
$$
So for fixed outer endpoints $\ell\in L_m$ and $r\in R_m$,
$$
C^\times(1,b,P_m;\ell,\ell,\rho,r)
=
\widetilde Q_-(b,R_m;\rho,r).
$$
Summing exactly over the possible first right-side vertex $\rho$ gives
$$
Q_-^\times(b+1,P_m;\ell,r)
=
\sum_{\rho\in R_m,\ \rho<r} Q_-(b,R_m;\rho,r).
\tag{Exact}
$$
Again there is no inequality: one is partitioning by the unique endpoint parameter $\rho$, with $(\ell,r)$ still fixed. This is exactly the crossing passage isolated in [[lemmas/one-split-crossing-cup-cap-identities]].

The first inequality that forgets endpoint data appears later in [[bounds/upper-bound-recursive-family]]. Before forgetting endpoints, the convex $k$-subsets admit the exact endpoint-matched decomposition
$$
C_k(P_m)
=
\sum_{a=2}^k\ \sum_{\ell<r}
Q_+(a,P_m;\ell,r)\,Q_-(k+2-a,P_m;\ell,r).
\tag{Exact}
$$
The upper-bound note then passes to
$$
C_k(P_m)
\le
\sum_{a=2}^k Q_+(a,P_m)\,Q_-(k+2-a,P_m).
\tag{Inequality}
$$
This is the first place where the shared outer endpoints are forgotten: the cup and cap coming from a convex $k$-set must have the same left endpoint $\ell$ and the same right endpoint $r$, whereas the product of total counts discards both matching conditions.

A literal chronological caveat is that [[bounds/upper-bound-recursive-family]] already contains earlier inequalities inside the auxiliary cup/cap estimate, beginning with
$$
Q_\pm(r,P_m)\le 2\,Q_\pm(r,P_{m-1})+2^{m-1}Q_\pm(r-1,P_{m-1}).
$$
But those inequalities are not endpoint-forgetting steps: they occur in the separate bound for total cup/cap counts and do not discard any shared outer-endpoint parameter. So the first inequality that loses the relevant endpoint information is still the endpoint-forgetting step above.

That loss alone does not explain the exponent constant $1$ in
$$
f(n)\le 2^{(\log_2 n)^2+O(\log n)}.
$$
It explains why one cannot replace exact endpoint-matched identities by products of coarse totals without loss, but the coefficient $1$ comes from combining the separate coarse bounds
$$
Q_\pm(r,P_m)\ll 2^{rm}
$$
with the later optimization in $k$. Restoring endpoint matching by itself does not determine, and does not by itself improve, that quadratic coefficient.
```