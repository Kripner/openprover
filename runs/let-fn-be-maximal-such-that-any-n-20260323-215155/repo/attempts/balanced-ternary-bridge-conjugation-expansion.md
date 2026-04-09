Summary: Expanding the ternary bridge quantities $U_m,D_m$ child-by-child gives exact recursive formulas in terms of half-plane counts indexed by conjugated affine map pairs, but it remains unresolved whether those pairs collapse to the currently tracked state in a fixed balanced ternary template.

This note records the exact recursive expansion that emerged from the bridge-state analysis, while separating it from the still-unproved non-closure claim.

## Setup

Keep the notation of [[attempts/alternative-construction-balanced-ternary-split]]. Define
$$
\alpha_0:=\Phi_M^{-1}\Phi_L,
\qquad
\beta_0:=\Phi_M^{-1}\Phi_R.
$$
Then the bridge quantities can be rewritten exactly as
$$
U_m(\lambda,r)
=
\Bigl|\bigl\{z\in T_{m-1}: z \text{ lies above the line } \alpha_0(\lambda)\beta_0(r)\bigr\}\Bigr|,
$$
$$
D_m(\ell,\rho)
=
\Bigl|\bigl\{z\in T_{m-1}: z \text{ lies below the line } \alpha_0(\ell)\beta_0(\rho)\bigr\}\Bigr|.
$$

## Generalized half-plane counts

For affine injections $\alpha,\beta$ and $n\ge 0$, define
$$
H_n^+[\alpha,\beta](x,y)
:=
\Bigl|\bigl\{z\in T_n: z \text{ lies above the line } \alpha(x)\beta(y)\bigr\}\Bigr|,
$$
$$
H_n^-[\alpha,\beta](x,y)
:=
\Bigl|\bigl\{z\in T_n: z \text{ lies below the line } \alpha(x)\beta(y)\bigr\}\Bigr|.
$$
Then
$$
U_m(\lambda,r)=H_{m-1}^+[\alpha_0,\beta_0](\lambda,r),
\qquad
D_m(\ell,\rho)=H_{m-1}^-[\alpha_0,\beta_0](\ell,\rho).
$$

## Exact recursive expansion

Write $x=\Phi_i(x')$, $y=\Phi_j(y')$ with $i,j\in\{L,M,R\}$ and $x',y'\in T_{n-1}$. Since
$$
T_n=\bigsqcup_{k\in\{L,M,R\}}\Phi_k(T_{n-1}),
$$
every counted point has the form $z=\Phi_k(z')$. Affine invariance of sidedness yields the exact identities
$$
H_n^+[\alpha,\beta](\Phi_i(x'),\Phi_j(y'))
=
\sum_{k\in\{L,M,R\}}
H_{n-1}^+[\Phi_k^{-1}\alpha\Phi_i,\Phi_k^{-1}\beta\Phi_j](x',y'),
$$
$$
H_n^-[\alpha,\beta](\Phi_i(x'),\Phi_j(y'))
=
\sum_{k\in\{L,M,R\}}
H_{n-1}^-[\Phi_k^{-1}\alpha\Phi_i,\Phi_k^{-1}\beta\Phi_j](x',y').
$$

Applying this with $(\alpha,\beta)=(\alpha_0,\beta_0)$ gives exact expansions for $U_m$ and $D_m$ in terms of lower-level half-plane counts indexed by conjugated affine map pairs.

## What is established and what is not

Established exactly:
- $U_m,D_m$ are instances of generalized half-plane counts.
- Recursive expansion introduces the map pairs
$$
(\Phi_k^{-1}\alpha_0\Phi_i,\ \Phi_k^{-1}\beta_0\Phi_j).
$$

Not yet established:
- whether, in a fixed balanced ternary template, those conjugated pairs reduce to finitely many already tracked bridge types;
- whether the state $\{A_m,B_m,U_m,D_m\}$ therefore closes or fails to close.

So this note is a partial result only. The next step is a concrete conjugacy computation in one fixed balanced ternary normalization.
