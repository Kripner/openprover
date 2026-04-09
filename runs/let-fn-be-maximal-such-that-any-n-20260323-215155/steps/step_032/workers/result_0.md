I could not write the file in this environment because every filesystem/tool call failed with `bwrap: Unknown option --argv0`. The repo-ready content is below.

```markdown
Summary: With the repaired one-split convention, the spanning recurrence is exactly a left-cup/right-cap factorization, and the crossing cup/cap formulas are exact endpoint-refined identities. The first place [[bounds/upper-bound-recursive-family]] truly loses the matched outer endpoints $(\ell,r)$ is the chain-pair inequality
$$
C_k(P_m)\le \sum_{a=2}^k Q_+(a,P_m)\,Q_-(k+2-a,P_m),
$$
not the earlier auxiliary inequalities used only to bound total cup/cap counts.

Assume the one-split hypotheses of [[lemmas/one-split-structure-spanning-convex-subsets]]:
$$
P=L\sqcup R,
$$
every point of $L$ lies to the left of every point of $R$, every line through two points of $L$ lies strictly below every point of $R$, and every line through two points of $R$ lies strictly above every point of $L$.

For a spanning convex subset $S\subseteq P$, write
$$
\ell=\min_x S,\qquad r=\max_x S,\qquad \lambda=\max_x(S\cap L),\qquad \rho=\min_x(S\cap R).
$$
For $a,b\ge 1$, let
$$
C^\times(a,b,P;\ell,\lambda,\rho,r)
$$
denote the number of spanning convex subsets with $|S\cap L|=a$, $|S\cap R|=b$, and state $(\ell,\lambda,\rho,r)$.

The exact fixed-state identity from [[lemmas/one-split-fixed-state-recurrence]] is
$$
C^\times(a,b,P;\ell,\lambda,\rho,r)
=
\widetilde Q_+(a,L;\ell,\lambda)\,\widetilde Q_-(b,R;\rho,r).
$$
This is an identity, not an inequality: fixing the state fixes the left endpoint pair $(\ell,\lambda)$ and the right endpoint pair $(\rho,r)$ exactly.

If $C^\times(a,b,P)$ denotes the number of spanning convex subsets with $|S\cap L|=a$ and $|S\cap R|=b$, then the exact fixed-split-size identity is
$$
C^\times(a,b,P)
=
\sum_{(\ell,\lambda,\rho,r)\,\mathrm{admissible}}
C^\times(a,b,P;\ell,\lambda,\rho,r)
=
\sum_{(\ell,\lambda,\rho,r)\,\mathrm{admissible}}
\widetilde Q_+(a,L;\ell,\lambda)\,\widetilde Q_-(b,R;\rho,r).
$$
Again this is an identity: every spanning convex subset has a unique state, so the state classes are disjoint and exhaustive.

Now fix outer endpoints $\ell\in L$ and $r\in R$.

For $t\ge 2$, specialize to $b=1$. Since
$$
\widetilde Q_-(1,R;\rho,r)=0 \text{ unless } \rho=r,\qquad \widetilde Q_-(1,R;r,r)=1,
$$
the fixed-state identity becomes
$$
C^\times(t,1,P;\ell,\lambda,r,r)=Q_+(t,L;\ell,\lambda).
$$
Summing over the remaining endpoint parameter $\lambda$ gives the exact spanning-cup identity
$$
Q_+^\times(t+1,P;\ell,r)
=
\sum_{\lambda\in L,\ \ell<\lambda} Q_+(t,L;\ell,\lambda).
$$
There is no inequality here: a spanning $(t+1)$-cup with outer endpoints $(\ell,r)$ has exactly one right-side point, namely $r$, hence a unique state of the form $(\ell,\lambda,r,r)$; different $\lambda$ give disjoint classes; and every $t$-cup in $L$ with endpoints $(\ell,\lambda)$ extends uniquely by adjoining $r$.

Dually, specialize to $a=1$. Since
$$
\widetilde Q_+(1,L;\ell,\lambda)=0 \text{ unless } \lambda=\ell,\qquad \widetilde Q_+(1,L;\ell,\ell)=1,
$$
the fixed-state identity becomes
$$
C^\times(1,t,P;\ell,\ell,\rho,r)=Q_-(t,R;\rho,r).
$$
Summing over the remaining endpoint parameter $\rho$ gives the exact spanning-cap identity
$$
Q_-^\times(t+1,P;\ell,r)
=
\sum_{\rho\in R,\ \rho<r} Q_-(t,R;\rho,r).
$$
Again there is no inequality: a spanning $(t+1)$-cap with outer endpoints $(\ell,r)$ has exactly one left-side point, namely $\ell$, hence a unique state of the form $(\ell,\ell,\rho,r)$; different $\rho$ give disjoint classes; and every $t$-cap in $R$ with endpoints $(\rho,r)$ extends uniquely by adjoining $\ell$.

So the corrected one-split framework does not lose endpoint information. The exact state is $(\ell,\lambda,\rho,r)$, and the crossing identities are exact sums over the single remaining endpoint parameter after the degenerate specializations $b=1$ and $a=1$.

In [[bounds/upper-bound-recursive-family]], the first inequality that actually forgets the matched outer endpoints $(\ell,r)$ of a convex subset is
$$
C_k(P_m)\le \sum_{a=2}^k Q_+(a,P_m)\,Q_-(k+2-a,P_m).
$$
A convex $k$-subset determines an upper-hull cup and a lower-hull cap with the same outer endpoints $(\ell,r)$, but the right-hand side counts arbitrary pairs of cups and caps of the indicated sizes, whether or not they share those endpoints. That is the genuine endpoint-forgetting step.

This should be distinguished from the earlier auxiliary inequalities
$$
Q_\pm(r,P_m)\le 2\,Q_\pm(r,P_{m-1})+2^{m-1}Q_\pm(r-1,P_{m-1})
$$
and
$$
Q_\pm(r,P_m)\le d_r\,2^{rm}.
$$
Those inequalities are used only to bound total cup/cap counts. They are not the step where a convex set is represented by two hull chains and the requirement of matching outer endpoints is discarded.

Restoring endpoint matching alone does not explain, and by itself does not improve, the leading constant $1$ in
$$
f(n)\le 2^{(\log_2 n)^2+O(\log n)}.
$$
The reason is that the coefficient of $(\log_2 n)^2$ comes from the later optimization using the coarse total bounds for $Q_+$ and $Q_-$. Exact endpoint matching may change only lower-order factors associated with summing over endpoint choices; without a substantially sharper endpoint-refined bound than the present total $Q_\pm$ estimates, it does not change the leading quadratic constant.
```