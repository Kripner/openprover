I could not persist the file because every workspace tool call fails immediately with `bwrap: Unknown option --argv0`. The note itself is below in repo-ready form.

```md
# One-split endpoint-refined recurrence

Assume
$$
P=L\sqcup R
$$
satisfies the one-split hypotheses of [[lemmas/one-split-structure-spanning-convex-subsets]]: every point of $L$ lies to the left of every point of $R$, every line through two points of $L$ lies strictly below every point of $R$, and every line through two points of $R$ lies strictly above every point of $L$.

## Definitions

For $a\ge 1$ and $\ell,\lambda\in L$, let
$$
\widetilde Q_-(a,L;\ell,\lambda)
$$
be the number of $a$-point caps in $L$ with endpoints $(\ell,\lambda)$, with the convention
$$
\widetilde Q_-(1,L;\ell,\ell)=1,\qquad
\widetilde Q_-(1,L;\ell,\lambda)=0\ \text{for }\ell\neq\lambda.
$$
For $a\ge 2$ this is just $Q_-(a,L;\ell,\lambda)$.

For $b\ge 1$ and $\rho,r\in R$, let
$$
\widetilde Q_+(b,R;\rho,r)
$$
be the number of $b$-point cups in $R$ with endpoints $(\rho,r)$, with the convention
$$
\widetilde Q_+(1,R;r,r)=1,\qquad
\widetilde Q_+(1,R;\rho,r)=0\ \text{for }\rho\neq r.
$$
For $b\ge 2$ this is just $Q_+(b,R;\rho,r)$.

For $a,b\ge 1$, define
$$
C^\times(a,b,P;\ell,\lambda,\rho,r)
$$
to be the number of spanning convex subsets $S\subseteq P$ such that
$$
|S\cap L|=a,\qquad |S\cap R|=b,
$$
the global leftmost and rightmost points of $S$ are $\ell$ and $r$, and
$$
\lambda=\max_x(S\cap L),\qquad \rho=\min_x(S\cap R).
$$
Equivalently, $S$ has state $(\ell,\lambda,\rho,r)$.

For fixed $k\ge 2$, set
$$
C^\times(k,P;\ell,\lambda,\rho,r):=\sum_{a+b=k} C^\times(a,b,P;\ell,\lambda,\rho,r).
$$

## Exact fixed-state factorization

**Proposition.** For every $a,b\ge 1$ and every admissible state $(\ell,\lambda,\rho,r)$,
$$
C^\times(a,b,P;\ell,\lambda,\rho,r)
=
\widetilde Q_-(a,L;\ell,\lambda)\,\widetilde Q_+(b,R;\rho,r).
$$
Hence
$$
C^\times(k,P;\ell,\lambda,\rho,r)
=
\sum_{a+b=k}\widetilde Q_-(a,L;\ell,\lambda)\,\widetilde Q_+(b,R;\rho,r).
$$

**Proof.** By [[lemmas/one-split-structure-spanning-convex-subsets]], every spanning convex set $S$ with state $(\ell,\lambda,\rho,r)$ decomposes uniquely as
$$
S=(S\cap L)\sqcup(S\cap R),
$$
where $S\cap L$ is a cap with endpoints $(\ell,\lambda)$ and $S\cap R$ is a cup with endpoints $(\rho,r)$. So
$$
S\mapsto (S\cap L,S\cap R)
$$
is injective into the Cartesian product on the right.

For surjectivity, let
$$
A=\{v_1=\ell<\cdots<v_a=\lambda\}\subseteq L
$$
be such a cap and
$$
B=\{u_1=\rho<\cdots<u_b=r\}\subseteq R
$$
be such a cup. Since $B$ is a cup and the line through $u_1,u_2$ lies strictly above every point of $L$, in particular above $\ell$,
$$
\operatorname{slope}(\ell,u_1)<\operatorname{slope}(u_1,u_2)<\cdots<\operatorname{slope}(u_{b-1},u_b),
$$
with the evident truncation when $b=1$. Thus
$$
\ell,u_1,\dots,u_b
$$
is a cup from $\ell$ to $r$.

Dually, since $A$ is a cap and the line through $v_{a-1},v_a$ lies strictly below every point of $R$, in particular below $r$,
$$
\operatorname{slope}(v_1,v_2)>\cdots>\operatorname{slope}(v_{a-1},v_a)>\operatorname{slope}(v_a,r),
$$
with the evident truncation when $a=1$. Thus
$$
v_1,\dots,v_a,r
$$
is a cap from $\ell$ to $r$.

Now every upper-chain edge with both endpoints in $R$ lies strictly above every point of $L$. For the first upper edge $\ell\rho$, all points of $A$ lie on or below the chord $\ell\lambda$ because $A$ is a cap, and $\rho$ lies strictly above the line $\ell\lambda$ because $\ell,\lambda\in L$; hence the segment $\ell\rho$ lies strictly above every point of $A\setminus\{\ell\}$. The dual argument shows that every lower-chain edge lies strictly below every point of $B\setminus\{r\}$.

Therefore the upper hull of $A\cup B$ is
$$
\ell,u_1,\dots,u_b
$$
and the lower hull is
$$
v_1,\dots,v_a,r.
$$
So $A\cup B$ is in convex position, spanning, and has state $(\ell,\lambda,\rho,r)$. This proves surjectivity. $\square$

Thus the spanning-convex count with fixed state is an **exact product**, not merely an upper bound.

## Crossing specializations

The exact crossing identities of [[lemmas/one-split-crossing-cup-cap-identities]] are the degenerate-state cases:
$$
C^\times(1,b,P;\ell,\ell,\rho,r)=\widetilde Q_+(b,R;\rho,r),
$$
$$
C^\times(a,1,P;\ell,\lambda,r,r)=\widetilde Q_-(a,L;\ell,\lambda).
$$
Summing over the free split endpoint gives, for $k\ge 2$,
$$
Q_+^\times(k,P;\ell,r)
=
\sum_{\rho\in R,\ \rho<r} C^\times(1,k-1,P;\ell,\ell,\rho,r)
=
\sum_{\rho\in R,\ \rho<r} Q_+(k-1,R;\rho,r),
$$
and
$$
Q_-^\times(k,P;\ell,r)
=
\sum_{\lambda\in L,\ \ell<\lambda} C^\times(k-1,1,P;\ell,\lambda,r,r)
=
\sum_{\lambda\in L,\ \ell<\lambda} Q_-(k-1,L;\ell,\lambda).
$$

## Recursive-family form

For the recursive family $P_m=L_m\sqcup R_m$ from [[bounds/upper-bound-recursive-family]], the same formulas apply verbatim:
$$
C^\times(a,b,P_m;\ell,\lambda,\rho,r)
=
\widetilde Q_-(a,L_m;\ell,\lambda)\,\widetilde Q_+(b,R_m;\rho,r),
$$
and
$$
C^\times(k,P_m;\ell,\lambda,\rho,r)
=
\sum_{a+b=k}\widetilde Q_-(a,L_m;\ell,\lambda)\,\widetilde Q_+(b,R_m;\rho,r).
$$

Endpoint matching is enforced by the state $(\ell,\lambda,\rho,r)$ itself: it fixes both local endpoint pairs and the common global endpoints $(\ell,r)$, so only the uniquely compatible left cap and right cup are paired.

After this state is forgotten, one is back in the situation of [[bounds/upper-bound-recursive-family]]: the remaining statements are only upper bounds, because unmatched endpoint choices can no longer be excluded exactly.
```