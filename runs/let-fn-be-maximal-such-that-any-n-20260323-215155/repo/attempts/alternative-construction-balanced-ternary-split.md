Summary: For the balanced ternary separated recursion, the total convex-subset count decomposes exactly into one-child, two-child, and endpoint-refined three-child terms, but exact recursive propagation of the new bridge-state quantities $U_m,D_m$ is still unresolved.

This note records the current exact decomposition forced by [[lemmas/ternary-one-split-structure]], together with the precise point still missing for a closed recursion.

## Setup

Fix affine contractions
$$
\\Phi_L,\\Phi_M,\\Phi_R:\\mathbb R^2\\to\\mathbb R^2
$$
such that for every finite set $X$ in general position, after one fixed small generic rotation the three images
$$
\\Phi_L(X),\\qquad \\Phi_M(X),\\qquad \\Phi_R(X)
$$
have disjoint $x$-ranges in the order
$$
x(\\Phi_L(X))<x(\\Phi_M(X))<x(\\Phi_R(X))
$$
and satisfy the ternary separated-position hypotheses of [[lemmas/ternary-one-split-structure]].

Let $T_0$ be a one-point set. For $m\\ge 1$, define
$$
T_m=L_m\\sqcup M_m\\sqcup R_m
$$
by
$$
L_m=\\Phi_L(T_{m-1}),\\qquad M_m=\\Phi_M(T_{m-1}),\\qquad R_m=\\Phi_R(T_{m-1}).
$$
Then
$$
|T_m|=3^m.
$$

## Endpoint-refined outer-chain state

For endpoint-refined cap/cup counts, write
$$
A_m(a;\\ell,\\lambda):=\\widetilde Q_-(a,T_m;\\ell,\\lambda),
\\qquad
B_m(b;\\rho,r):=\\widetilde Q_+(b,T_m;\\rho,r).
$$

The ternary lemma shows that these do not suffice by themselves for three-child spans: after fixing outer endpoints, the middle contribution depends on bridge regions. Define the parent-scale bridge quantities
$$
U_m(\\lambda,r):=\\Bigl|\\Bigl\\{z\\in T_{m-1}:\\Phi_M(z)\\text{ lies above the line }\\Phi_L(\\lambda)\\Phi_R(r)\\Bigr\\}\\Bigr|,
$$
$$
D_m(\\ell,\\rho):=\\Bigl|\\Bigl\\{z\\in T_{m-1}:\\Phi_M(z)\\text{ lies below the line }\\Phi_L(\\ell)\\Phi_R(\\rho)\\Bigr\\}\\Bigr|.
$$

## Exact decomposition of $C_m(k)$

Let $C_m(k)$ be the number of $k$-point subsets of $T_m$ in convex position.

### 1. One-child contribution

Exactly
$$
C_m^{(1)}(k)=3\,C_{m-1}(k).
$$

### 2. Exactly two children

For each earlier-later pair $(X,Y)\\in\\{(L_m,M_m),(M_m,R_m),(L_m,R_m)\\}$, [[lemmas/ternary-one-split-structure]] gives exactly: the $X$-part is a cap and the $Y$-part is a cup.

Set
$$
A_{m-1}^{\\mathrm{tot}}(a):=\\sum_{\\ell,\\lambda\\in T_{m-1}}A_{m-1}(a;\\ell,\\lambda),
\\qquad
B_{m-1}^{\\mathrm{tot}}(b):=\\sum_{\\rho,r\\in T_{m-1}}B_{m-1}(b;\\rho,r).
$$
Then the exact two-child contribution is
$$
C_m^{(2)}(k)=3\\sum_{a+b=k}A_{m-1}^{\\mathrm{tot}}(a)\,B_{m-1}^{\\mathrm{tot}}(b).
$$

### 3. All three children

Fix outer state
$$
(\\ell,\\lambda,\\rho,r)\\in T_{m-1}^4.
$$
By [[lemmas/ternary-one-split-structure]], any three-child convex subset is obtained from
1. a cap in $L_m$ with endpoints $(\\ell,\\lambda)$,
2. a cup in $R_m$ with endpoints $(\\rho,r)$,
3. optionally one upper bridge point from the region counted by $U_m(\\lambda,r)$,
4. optionally one lower bridge point from the region counted by $D_m(\\ell,\\rho)$,

with at least one bridge choice present, and with at most one upper and at most one lower middle point.

Hence the exact contribution with exactly one middle point is
$$
C_m^{(3,1)}(k)=
\\sum_{a+b+1=k}\\;
\\sum_{\\ell,\\lambda,\\rho,r}
A_{m-1}(a;\\ell,\\lambda)\,
B_{m-1}(b;\\rho,r)\,
\\bigl(U_m(\\lambda,r)+D_m(\\ell,\\rho)\\bigr),
$$
and the exact contribution with exactly two middle points is
$$
C_m^{(3,2)}(k)=
\\sum_{a+b+2=k}\\;
\\sum_{\\ell,\\lambda,\\rho,r}
A_{m-1}(a;\\ell,\\lambda)\,
B_{m-1}(b;\\rho,r)\,
U_m(\\lambda,r)\,D_m(\\ell,\\rho).
$$
Also, by the same lemma,
$$
C_m^{(3,c)}(k)=0\\qquad(c\\ge 3).
$$

Therefore
$$
C_m(k)=C_m^{(1)}(k)+C_m^{(2)}(k)+C_m^{(3,1)}(k)+C_m^{(3,2)}(k).
$$

All displayed formulas in this section are exact identities, assuming the bridge quantities are interpreted exactly as above.

## Exact place still unresolved

This note does not establish recursive propagation formulas for
$$
U_m(\\lambda,r),\\qquad D_m(\\ell,\\rho)
$$
from level $m-1$ data.

So the current status is:

- the decomposition of $C_m(k)$ into one-child, two-child, and bridge-weighted three-child terms is exact;
- aggregate cap/cup totals do not suffice for the three-child term;
- but it remains unproved whether the enlarged state
$$
\\{A_m(a;\\ell,\\lambda)\\},\\ \\{B_m(b;\\rho,r)\\},\\ \\{U_m(\\lambda,r)\\},\\ \\{D_m(\\ell,\\rho)\\}
$$
itself closes recursively in the balanced ternary template.

## Consequence for next step

The next task is not to estimate asymptotics yet. It is to determine one of the following exactly:

1. derive recursive formulas for $U_m,D_m$ from level-$m-1$ state data, thereby closing the balanced ternary recurrence in an enlarged state space; or
2. identify the first exact obstruction showing that no such manageable closure holds in this template.

Until that is settled, no coefficient obstruction from the ternary family is established.