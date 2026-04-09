I could not write the note into the workspace because the tool layer is failing with `bwrap: Unknown option --argv0`. The note content is below, ready for `status/recursive-family-information-loss`.

```markdown
# Recursive-family Information Loss

Let
$$
C_m^\times(a,b)
:=
\#\{S\subseteq P_m:\ S\text{ is in convex position},\ |S\cap L_m|=a,\ |S\cap R_m|=b\},
$$
for $a,b\ge 1$, where $P_m=L_m\sqcup R_m$ is the one-split decomposition from [[bounds/upper-bound-recursive-family]].

By [[lemmas/one-split-fixed-state-recurrence]], for each state
$$
(\ell,\lambda,\rho,r)
\quad
(\ell,\lambda\in L_m,\ \rho,r\in R_m),
$$
one has the exact identity
$$
C^\times(a,b,P_m;\ell,\lambda,\rho,r)
=
\widetilde Q_+(a,L_m;\ell,\lambda)\,\widetilde Q_-(b,R_m;\rho,r).
$$
Summing over all states gives another exact identity:
$$
\begin{aligned}
C_m^\times(a,b)
&=
\sum_{\ell,\lambda\in L_m}\sum_{\rho,r\in R_m}
C^\times(a,b,P_m;\ell,\lambda,\rho,r) \\
&=
\sum_{\ell,\lambda\in L_m}\sum_{\rho,r\in R_m}
\widetilde Q_+(a,L_m;\ell,\lambda)\,\widetilde Q_-(b,R_m;\rho,r).
\end{aligned}
$$
Here the degenerate conventions already enforce $\ell=\lambda$ when $a=1$ and $\rho=r$ when $b=1$, so no further correction is needed. Since the left and right endpoint variables are independent in the one-split gluing, this factors exactly as
$$
C_m^\times(a,b)
=
\Bigl(\sum_{\ell,\lambda\in L_m}\widetilde Q_+(a,L_m;\ell,\lambda)\Bigr)
\Bigl(\sum_{\rho,r\in R_m}\widetilde Q_-(b,R_m;\rho,r)\Bigr).
$$
Thus the passage from state counts to fixed split-size counts loses no information at all. In particular, the inner state data $(\lambda,\rho)$ are summed out exactly.

The same point persists when one passes to the crossing cup/cap families from [[lemmas/one-split-crossing-cup-cap-identities]]: the split-side extension step is still an exact summation over the relevant endpoint parameter, not yet an inequality. So the displayed recursive inequalities for $Q_\pm(r,P_m)$ in [[bounds/upper-bound-recursive-family]] are coarse rewritings of a decomposition that can still be kept exact at that stage.

The first genuine loss of exactness occurs later, when one replaces matched endpoint-refined hull counts by the coarse totals $Q_+(t,P_m)$ and $Q_-(u,P_m)$. For convex $k$-subsets there is an exact endpoint-refined identity
$$
C_k(P_m)
=
\sum_{a=2}^k\ \sum_{\ell<r}
Q_+(a,P_m;\ell,r)\,Q_-(k+2-a,P_m;\ell,r),
$$
where the cup and cap are required to have the same global endpoints $(\ell,r)$. The upper-bound note then replaces this by
$$
C_k(P_m)\le \sum_{a=2}^k Q_+(a,P_m)\,Q_-(k+2-a,P_m),
$$
which is only an inequality. This is the first projection where exactness is actually lost: one forgets that the upper-hull cup and lower-hull cap must share the same outer endpoints $(\ell,r)$. Relative to the state-level formula, one has first forgotten the interior bridge data $(\lambda,\rho)$ by exact summation, and then here one forgets the remaining matched endpoint data $(\ell,r)$ by inequality.

This loss is not, by itself, enough to explain why the recursive-family argument still gives exponent constant $1$. Even before this inequality, the exact one-split formula has already collapsed to a product of total left-cup and right-cap counts, and the available cup/cap bounds are still of size $2^{rm+O(1)}$. Plugging those bounds into either the exact split formula or the coarse chain-pair inequality leads to the same $m^2+O(m)$ exponent scale. So the real obstruction is later: the method has no sharper control on the matched-endpoint quantities than on the aggregate cup/cap totals, and without new structure beyond those totals the exponent constant does not improve.
```