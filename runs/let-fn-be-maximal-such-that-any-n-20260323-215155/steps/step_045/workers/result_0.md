I could not write into the workspace because the local sandbox wrapper is failing before command execution (`bwrap: Unknown option --argv0`). The orbit question is decisive, though. The correct slug is `status/balanced-ternary-infinite-bridge-orbit-obstruction`, and the repo-ready markdown is:

```markdown
Summary: In the explicit balanced ternary template, repeated exact bridge conjugation already generates infinitely many distinct affine bridge pairs. Since [[status/balanced-ternary-concrete-bridge-obstruction]] establishes that the template has only the identity affine symmetry, these pairs remain distinct modulo actual template symmetry. Hence no finite affine-pair state space can be closed under the exact bridge recursion for this template.

## Setup

Work in the explicit template
$$
\Phi_i(x)=Ax+t_i,
\qquad
A=\operatorname{diag}(1/10,1/100),
$$
with
$$
t_L=(-4,2),\qquad t_M=(0,0),\qquad t_R=(5,-2).
$$

Write translations as
$$
\tau_u(x)=x+u.
$$
The standard bridge pair is
$$
\alpha_0=\tau_{u_0},
\qquad
\beta_0=\tau_{v_0},
$$
with
$$
u_0=(-40,200),
\qquad
v_0=(50,-200).
$$

The exact bridge expansion from [[attempts/balanced-ternary-bridge-conjugation-expansion]] is
$$
H_n^\pm[\alpha,\beta](\Phi_i(x'),\Phi_j(y'))
=
\sum_{k\in\{L,M,R\}}
H_{n-1}^\pm[\Phi_k^{-1}\alpha\Phi_i,\Phi_k^{-1}\beta\Phi_j](x',y').
$$

By [[status/balanced-ternary-concrete-bridge-obstruction]], the affine symmetry group of this template is trivial.

## Exact affine-pair dynamics

Let $\alpha=\tau_u$ and $\beta=\tau_v$. Since
$$
\Phi_i(x)=Ax+t_i,
\qquad
\Phi_k^{-1}(x)=A^{-1}(x-t_k),
$$
one computes exactly
$$
\Phi_k^{-1}\tau_u\Phi_i(x)
=
A^{-1}(A x+t_i+u-t_k)
=
x+A^{-1}(u+t_i-t_k).
$$
Thus
$$
\Phi_k^{-1}\tau_u\Phi_i=\tau_{A^{-1}(u+t_i-t_k)}.
$$
Similarly,
$$
\Phi_k^{-1}\tau_v\Phi_j=\tau_{A^{-1}(v+t_j-t_k)}.
$$

So the exact conjugation mechanism acts on translation pairs by
$$
(u,v)\longmapsto
\bigl(A^{-1}(u+t_i-t_k),\,A^{-1}(v+t_j-t_k)\bigr).
$$
In particular, every descendant of $(\alpha_0,\beta_0)$ in the recursion tree is again a pair of translations.

## The repeated middle branch

Take the single branch
$$
(i,j,k)=(M,M,M).
$$
Since $t_M=0$, this branch acts by
$$
(u,v)\longmapsto (A^{-1}u,A^{-1}v).
$$

Define recursively
$$
\alpha_{n+1}:=\Phi_M^{-1}\alpha_n\Phi_M,
\qquad
\beta_{n+1}:=\Phi_M^{-1}\beta_n\Phi_M,
$$
with $(\alpha_0,\beta_0)$ as above. Then
$$
\alpha_n=\tau_{u_n},
\qquad
\beta_n=\tau_{v_n},
$$
where
$$
u_n=A^{-n}u_0,
\qquad
v_n=A^{-n}v_0.
$$
Because
$$
A^{-1}=\operatorname{diag}(10,100),
$$
this gives the exact formulas
$$
u_n=\bigl(-40\cdot 10^n,\ 200\cdot 100^n\bigr),
\qquad
v_n=\bigl(50\cdot 10^n,\ -200\cdot 100^n\bigr).
$$
For $n=1$ this is exactly the already observed pair
$$
\alpha_1=\mathrm{id}+(-400,20000),
\qquad
\beta_1=\mathrm{id}+(500,-20000).
$$

These pairs genuinely occur in the exact recursion. Indeed, for every $q\ge n$, the point $0$ lies in $T_q$ because $\Phi_M(0)=0$, and repeated application of the expansion to
$$
H_q^\pm[\alpha_0,\beta_0](0,0)
$$
along the branch $(i,j,k)=(M,M,M)$ exactly $n$ times produces the descendant term
$$
H_{q-n}^\pm[\alpha_n,\beta_n](0,0).
$$

## Infinite orbit

If $m\neq n$, then
$$
u_m\neq u_n
$$
because their first coordinates are $-40\cdot 10^m$ and $-40\cdot 10^n$. Hence
$$
\alpha_m\neq \alpha_n.
$$
Therefore
$$
(\alpha_m,\beta_m)\neq (\alpha_n,\beta_n)
\qquad\text{for }m\neq n.
$$

Since the template has only the identity affine symmetry, passing to affine pairs modulo actual template symmetry does not identify any additional pairs. Therefore the orbit of the standard bridge pair under exact bridge conjugation is infinite modulo template symmetry.

## Consequence for exact bridge-state closure

Within the affine-pair recursion framework of [[attempts/balanced-ternary-bridge-conjugation-expansion]], an exact closed state space must contain every affine pair that appears in the recursion tree of $(\alpha_0,\beta_0)$. The repeated middle branch already produces infinitely many distinct pairs
$$
(\alpha_n,\beta_n)
=
\bigl(\mathrm{id}+(-40\cdot 10^n,\,200\cdot 100^n),\ 
\mathrm{id}+(50\cdot 10^n,\,-200\cdot 100^n)\bigr),
\qquad n\ge 0.
$$
Hence no finite affine bridge-pair state space can close for this template under this exact affine-pair recursion.

This is the full consequence proved here. It does not assert that no different kind of compression exists; it only rules out finite closure inside the present exact affine-pair recursion framework.
```