# status/balanced-ternary-bridge-state-obstruction

Summary: The bridge quantities $U_m(\lambda,r)$ and $D_m(\ell,\rho)$ do not close under the presently tracked state $\{A_m,B_m,U_m,D_m\}$. Already the first recursive expansion of $U_m$ or $D_m$ produces new exact half-plane counts indexed by transformed endpoint-map pairs, not by the single standard pair defining $U$ and $D$.

## Setup

Keep the notation of [[attempts/alternative-construction-balanced-ternary-split]]. Set
$$
\alpha_0:=\Phi_M^{-1}\Phi_L,
\qquad
\beta_0:=\Phi_M^{-1}\Phi_R.
$$
Then, by definition,
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

So the bridge quantities are already half-plane incidence counts in $T_{m-1}$ for one specific endpoint-map pair $(\alpha_0,\beta_0)$.

## Generalized exact bridge state

For any affine injections $\alpha,\beta$ and any $n\ge 0$, define
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

These are exact identities.

## Exact recursive expansion

Let $x=\Phi_i(x')$ and $y=\Phi_j(y')$ with $i,j\in\{L,M,R\}$ and $x',y'\in T_{n-1}$. Since
$$
T_n=\bigsqcup_{k\in\{L,M,R\}}\Phi_k(T_{n-1}),
$$
every counted point has the form $z=\Phi_k(z')$. By affine invariance of sidedness with respect to lines,
$$
z \text{ lies above the line } \alpha(\Phi_i(x'))\beta(\Phi_j(y'))
$$
if and only if
$$
z' \text{ lies above the line }
\Phi_k^{-1}\alpha\Phi_i(x')\,
\Phi_k^{-1}\beta\Phi_j(y').
$$
Therefore, exactly,
$$
H_n^+[\alpha,\beta](\Phi_i(x'),\Phi_j(y'))
=
\sum_{k\in\{L,M,R\}}
H_{n-1}^+[\Phi_k^{-1}\alpha\Phi_i,\Phi_k^{-1}\beta\Phi_j](x',y').
$$
Similarly,
$$
H_n^-[\alpha,\beta](\Phi_i(x'),\Phi_j(y'))
=
\sum_{k\in\{L,M,R\}}
H_{n-1}^-[\Phi_k^{-1}\alpha\Phi_i,\Phi_k^{-1}\beta\Phi_j](x',y').
$$

Applying this with $(\alpha,\beta)=(\alpha_0,\beta_0)$ and $n=m-1$ gives
$$
U_m(\Phi_i(x'),\Phi_j(y'))
=
\sum_{k\in\{L,M,R\}}
H_{m-2}^+[\Phi_k^{-1}\alpha_0\Phi_i,\Phi_k^{-1}\beta_0\Phi_j](x',y'),
$$
$$
D_m(\Phi_i(x'),\Phi_j(y'))
=
\sum_{k\in\{L,M,R\}}
H_{m-2}^-[\Phi_k^{-1}\alpha_0\Phi_i,\Phi_k^{-1}\beta_0\Phi_j](x',y').
$$

All displayed formulas in this section are exact identities.

## First exact obstruction

The presently tracked bridge state records only the two families
$$
H_n^+[\alpha_0,\beta_0],
\qquad
H_n^-[\alpha_0,\beta_0],
$$
namely $U_{n+1}$ and $D_{n+1}$.

But the exact recursion above immediately requires, for each choice of $(i,j,k)$,
$$
H_{m-2}^\pm[\Phi_k^{-1}\alpha_0\Phi_i,\Phi_k^{-1}\beta_0\Phi_j].
$$
These are new endpoint-map pairs. Nothing in the current state
$$
\{A_n(a;\ell,\lambda)\},\qquad
\{B_n(b;\rho,r)\},\qquad
\{U_n(\lambda,r)\},\qquad
\{D_n(\ell,\rho)\}
$$
identifies them with the single standard pair $(\alpha_0,\beta_0)$.

So closure already fails at the first childwise expansion of $U_m$ or $D_m$: even with the full currently tracked endpoint-refined state at level $m-1$, the right-hand side is not expressible using only that state, because it asks for half-plane counts attached to transformed line families not recorded there.

This is the first exact obstruction.

## What data the bridge quantities depend on

Recursively, the bridge counts depend on:
$$
\text{the endpoint pair }(x,y),
\qquad
\text{the choice of sidedness }(\pm),
\qquad
\text{the affine endpoint-map pair }(\alpha,\beta).
$$

The standard bridge state keeps only one such affine pair, namely $(\alpha_0,\beta_0)$. The recursion generates further pairs by
$$
(\alpha,\beta)\longmapsto
(\Phi_k^{-1}\alpha\Phi_i,\Phi_k^{-1}\beta\Phi_j)
\qquad
(i,j,k\in\{L,M,R\}).
$$

## Natural exact closure after further enlargement

If one wants exact recursive closure, the natural enlarged state is the full family
$$
H_n^\pm[\alpha,\beta](x,y)
$$
for every affine pair $(\alpha,\beta)$ in the orbit of $(\alpha_0,\beta_0)$ under the update rule above. Equivalently, define
$$
\mathcal O_0:=\{(\alpha_0,\beta_0)\},
$$
$$
\mathcal O_{t+1}:=
\bigl\{
(\Phi_k^{-1}\alpha\Phi_i,\Phi_k^{-1}\beta\Phi_j):
(\alpha,\beta)\in\mathcal O_t,\ i,j,k\in\{L,M,R\}
\bigr\},
$$
and $\mathcal O:=\bigcup_{t\ge 0}\mathcal O_t$. Then exact closure requires carrying all
$$
H_n^\pm[\alpha,\beta]
\qquad
((\alpha,\beta)\in\mathcal O).
$$

This is the minimal natural exact state closed under the recursive split operator itself.

## Conclusion

The three-child decomposition of $C_m(k)$ in [[attempts/alternative-construction-balanced-ternary-split]] remains exact once $U_m$ and $D_m$ are interpreted literally. What fails is the claimed closure of the enlarged state
$$
\{A_m,B_m,U_m,D_m\}.
$$
The first exact obstruction is the childwise recursion for $U_m$ and $D_m$, which immediately introduces new map-indexed half-plane counts at level $m-2}$.

So the correct decision is: closure fails for the currently proposed bridge state. Exact closure is recovered only after enlarging further to the full orbit of generalized map-pair bridge counts, and from the present hypotheses there is no reason to expect that orbit to collapse to a finite clean family.

I could not write this into the repo because the sandbox wrapper failed on every file operation (`bwrap: Unknown option --argv0`).