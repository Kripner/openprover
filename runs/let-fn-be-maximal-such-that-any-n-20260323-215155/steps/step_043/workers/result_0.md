I could not write the file because the workspace tool wrapper is failing with `bwrap: Unknown option --argv0`. Below is the repo-ready note for `status/balanced-ternary-concrete-bridge-obstruction.md`.

```markdown
Summary: the diagonal template
$$
A=\operatorname{diag}(1/10,1/100),\qquad
t_L=(-4,2),\ t_M=(0,0),\ t_R=(5,-2)
$$
satisfies the ternary separated-position hypotheses with explicit margins, and the corrected first bridge expansion already produces a conjugated bridge pair not recorded by the current bridge state and not identified with the standard pair by any actual symmetry of the template.

# Status: concrete bridge obstruction in the balanced ternary template

We keep the candidate common-linear-part template
$$
\Phi_i(x)=Ax+t_i,
\qquad
A=\operatorname{diag}(1/10,1/100),
$$
with
$$
t_L=(-4,2),\qquad t_M=(0,0),\qquad t_R=(5,-2).
$$

We verify two points:

1. this template satisfies the separated-position hypotheses needed in [[lemmas/ternary-one-split-structure]];
2. the corrected first bridge expansion already produces a genuine new affine bridge pair, so the currently tracked bridge state does not close even at the first conjugation step.

## 1. Coordinate model and invariant boxes

Take
$$
T_0=\{(0,0)\},
\qquad
T_n=\Phi_L(T_{n-1})\sqcup \Phi_M(T_{n-1})\sqcup \Phi_R(T_{n-1}).
$$

For a word $w=w_1\cdots w_n\in\{L,M,R\}^n$, write
$$
a(L)=-4,\ a(M)=0,\ a(R)=5,
$$
$$
b(L)=2,\ b(M)=0,\ b(R)=-2.
$$
Then the point of $T_n$ indexed by $w$ has coordinates
$$
x(w)=\sum_{r=1}^n a(w_r)\,10^{-(r-1)},
\qquad
y(w)=\sum_{r=1}^n b(w_r)\,100^{-(r-1)}.
$$

Hence every $T_n$ lies in
$$
K=\left[-\frac{40}{9},\frac{50}{9}\right]\times\left[-\frac{200}{99},\frac{200}{99}\right].
$$
Therefore
$$
L_n:=\Phi_L(T_{n-1})\subseteq
\left[-\frac{40}{9},-\frac{31}{9}\right]\times\left[\frac{196}{99},\frac{200}{99}\right],
$$
$$
M_n:=\Phi_M(T_{n-1})\subseteq
\left[-\frac{4}{9},\frac{5}{9}\right]\times\left[-\frac{2}{99},\frac{2}{99}\right],
$$
$$
R_n:=\Phi_R(T_{n-1})\subseteq
\left[\frac{41}{9},\frac{50}{9}\right]\times\left[-\frac{200}{99},-\frac{196}{99}\right].
$$
In particular,
$$
x(L_n)<x(M_n)<x(R_n)
$$
strictly.

## 2. Uniform secant-slope bound

Let $p,q\in T_n$ be distinct, with words $u,v$. Let $m$ be the first index with $u_m\neq v_m$.

Then
$$
x(p)-x(q)=10^{-(m-1)}(\Delta_x+\varepsilon_x),
\qquad
\Delta_x\in\{\pm4,\pm5,\pm9\},
$$
$$
y(p)-y(q)=100^{-(m-1)}(\Delta_y+\varepsilon_y),
\qquad
\Delta_y\in\{\pm2,\pm4\},
$$
with tail bounds
$$
|\varepsilon_x|\le \sum_{s\ge1}9\cdot 10^{-s}=1,
\qquad
|\varepsilon_y|\le \sum_{s\ge1}4\cdot 100^{-s}=\frac4{99}.
$$
Hence
$$
|x(p)-x(q)|\ge 10^{-(m-1)}(4-1)=3\cdot 10^{-(m-1)},
$$
$$
|y(p)-y(q)|\le 100^{-(m-1)}\left(4+\frac4{99}\right)=\frac{400}{99}\,100^{-(m-1)}.
$$
Therefore
$$
\left|\operatorname{slope}(pq)\right|
\le
\frac{\frac{400}{99}\,100^{-(m-1)}}{3\cdot 10^{-(m-1)}}
=
\frac{400}{297}\,10^{-(m-1)}
\le \frac{400}{297}.
$$

If $p,q$ lie in one fixed first-generation child, then $m\ge2$, so
$$
\left|\operatorname{slope}(pq)\right|\le \frac{40}{297}.
$$
Set
$$
\sigma:=\frac{40}{297}.
$$

## 3. Separated-position verification

We now check the exact ternary separated-position conditions.

### 3.1. Every $L_n$-secant lies strictly above $M_n\cup R_n$

Let $\ell$ be a line through two points of $L_n$. Then $\operatorname{slope}(\ell)\ge -\sigma$ and every point of $L_n$ has $y\ge 196/99$ and $x\ge -40/9$. Hence for every $x\ge -40/9$,
$$
\ell(x)\ge \frac{196}{99}-\sigma\left(x+\frac{40}{9}\right).
$$

For $M_n$, the worst case is the rightmost $x=5/9$:
$$
\ell(x)\ge \frac{196}{99}-5\sigma
=\frac{196}{99}-\frac{200}{297}
=\frac{388}{297}.
$$
But every point of $M_n$ has $y\le 2/99=6/297$, so
$$
\frac{388}{297}>\frac{2}{99}.
$$

For $R_n$, the worst case is the rightmost $x=50/9$:
$$
\ell(x)\ge \frac{196}{99}-10\sigma
=\frac{196}{99}-\frac{400}{297}
=\frac{188}{297}.
$$
But every point of $R_n$ has $y\le -196/99$, so
$$
\frac{188}{297}>-\frac{196}{99}.
$$

Thus every $L_n$-secant lies strictly above every point of $M_n\cup R_n$.

### 3.2. Every $M_n$-secant lies strictly below $L_n$ and strictly above $R_n$

Let $\ell$ be a line through two points of $M_n$.

To compare with $L_n$, use the rightmost anchor $(5/9,2/99)$ and the most negative slope $-\sigma$. For every $x\le 5/9$,
$$
\ell(x)\le \frac{2}{99}+\sigma\left(\frac59-x\right).
$$
The worst case in $L_n$ is the leftmost $x=-40/9$:
$$
\ell(x)\le \frac{2}{99}+5\sigma
=\frac{2}{99}+\frac{200}{297}
=\frac{206}{297}.
$$
But every point of $L_n$ has $y\ge 196/99=588/297$, so
$$
\frac{206}{297}<\frac{196}{99}.
$$

To compare with $R_n$, use the leftmost anchor $(-4/9,-2/99)$ and the most negative slope $-\sigma$. For every $x\ge -4/9$,
$$
\ell(x)\ge -\frac{2}{99}-\sigma\left(x+\frac49\right).
$$
The worst case in $R_n$ is the rightmost $x=50/9$:
$$
\ell(x)\ge -\frac{2}{99}-6\sigma
=-\frac{2}{99}-\frac{240}{297}
=-\frac{82}{99}.
$$
But every point of $R_n$ has $y\le -196/99$, so
$$
-\frac{82}{99}>-\frac{196}{99}.
$$

Thus every $M_n$-secant lies strictly below $L_n$ and strictly above $R_n$.

### 3.3. Every $R_n$-secant lies strictly below $L_n\cup M_n$

Let $\ell$ be a line through two points of $R_n$. Using the rightmost anchor $(50/9,-196/99)$ and the most negative slope $-\sigma$, for every $x\le 50/9$,
$$
\ell(x)\le -\frac{196}{99}+\sigma\left(\frac{50}{9}-x\right).
$$

For $M_n$, the worst case is the leftmost $x=-4/9$:
$$
\ell(x)\le -\frac{196}{99}+6\sigma
=-\frac{196}{99}+\frac{240}{297}
=-\frac{116}{99}.
$$
But every point of $M_n$ has $y\ge -2/99$, so
$$
-\frac{116}{99}<-\frac{2}{99}.
$$

For $L_n$, the worst case is the leftmost $x=-40/9$:
$$
\ell(x)\le -\frac{196}{99}+10\sigma
=-\frac{196}{99}+\frac{400}{297}
=-\frac{188}{297}.
$$
But every point of $L_n$ has $y\ge 196/99$, so
$$
-\frac{188}{297}<\frac{196}{99}.
$$

Thus every $R_n$-secant lies strictly below every point of $L_n\cup M_n$.

### 3.4. Conclusion

So the candidate template satisfies exactly the ternary separated-position hypotheses of [[lemmas/ternary-one-split-structure]]. The inequalities hold with uniform positive margins. Hence, if desired, one may apply a sufficiently small generic rotation afterward to enforce general position without destroying any of the strict separations.

## 4. The standard bridge pair

Because the linear part is common,
$$
\alpha_0=\Phi_M^{-1}\Phi_L=\operatorname{id}+A^{-1}(t_L-t_M),
$$
$$
\beta_0=\Phi_M^{-1}\Phi_R=\operatorname{id}+A^{-1}(t_R-t_M).
$$
Since
$$
A^{-1}=\operatorname{diag}(10,100),
$$
we obtain
$$
\alpha_0=\operatorname{id}+(-40,200),
\qquad
\beta_0=\operatorname{id}+(50,-200).
$$

By definition,
$$
U_m(\lambda,r)=H_{m-1}^+[\alpha_0,\beta_0](\lambda,r),
\qquad
D_m(\ell,\rho)=H_{m-1}^-[\alpha_0,\beta_0](\ell,\rho).
$$
So the currently tracked bridge state records only the single affine pair $(\alpha_0,\beta_0)$.

## 5. A decisive first-generation new pair

Take the exact bridge expansion at
$$
x=\Phi_M(x'),\qquad y=\Phi_M(y').
$$
In the $k=M$ summand, the conjugated pair is
$$
\alpha_1:=\Phi_M^{-1}\alpha_0\Phi_M,
\qquad
\beta_1:=\Phi_M^{-1}\beta_0\Phi_M.
$$
Using the corrected formula
$$
\Phi_k^{-1}\alpha_0\Phi_i
=
\operatorname{id}+A^{-2}(t_L-t_M)+A^{-1}(t_i-t_k),
$$
$$
\Phi_k^{-1}\beta_0\Phi_j
=
\operatorname{id}+A^{-2}(t_R-t_M)+A^{-1}(t_j-t_k),
$$
with $i=j=k=M$, we get
$$
\alpha_1=\operatorname{id}+A^{-2}(t_L-t_M),
\qquad
\beta_1=\operatorname{id}+A^{-2}(t_R-t_M).
$$
Since
$$
A^{-2}=\operatorname{diag}(100,10000),
$$
this is
$$
\alpha_1=\operatorname{id}+(-400,20000),
\qquad
\beta_1=\operatorname{id}+(500,-20000).
$$

This is not the standard pair:
$$
(-400,20000)\neq (-40,200),
\qquad
(500,-20000)\neq (50,-200).
$$

## 6. No actual symmetry identifies $(\alpha_1,\beta_1)$ with $(\alpha_0,\beta_0)$

Let $S(x)=Bx+c$ be an affine symmetry of the template, meaning
$$
S\circ \Phi_i=\Phi_{\sigma(i)}\circ S
\qquad (i\in\{L,M,R\})
$$
for some permutation $\sigma$.

Comparing linear parts gives
$$
BA=AB.
$$
Since
$$
A=\operatorname{diag}(1/10,1/100)
$$
has distinct eigenvalues, $B$ must be diagonal:
$$
B=\operatorname{diag}(u,v).
$$

Comparing translations and subtracting the equations for $i,j$ gives
$$
B(t_i-t_j)=t_{\sigma(i)}-t_{\sigma(j)}.
$$
The $x$-differences among the three translation points are
$$
\pm4,\ \pm5,\ \pm9,
$$
so multiplying by $u$ must preserve this set; hence $|u|=1$.
The nonzero $y$-differences are
$$
\pm2,\ \pm4,
$$
so multiplying by $v$ must preserve this set; hence $|v|=1$.
Thus
$$
u,v\in\{\pm1\}.
$$

Now
$$
t_L-t_R=(-9,4).
$$
So
$$
B(t_L-t_R)=(-9u,4v).
$$
Among all differences $t_a-t_b$, the only vectors with absolute values $(9,4)$ are
$$
(-9,4)\quad\text{and}\quad(9,-4),
$$
hence $u=v$. Therefore
$$
B=I\quad\text{or}\quad B=-I.
$$

If $B=-I$, then
$$
B(t_L-t_M)=(4,-2)=t_M-t_L,
$$
so $\sigma(L)=M$ and $\sigma(M)=L$.
But also
$$
B(t_M-t_R)=(5,-2)=t_R-t_M,
$$
so $\sigma(M)=R$ and $\sigma(R)=M$.
Contradiction. Hence $B\neq -I$.

So $B=I$. Then
$$
t_{\sigma(i)}-t_{\sigma(j)}=t_i-t_j
$$
for all $i,j$, hence $\sigma=\operatorname{id}$. Returning to
$$
Bt_i+c=Ac+t_i
$$
gives
$$
c=Ac.
$$
Since $1$ is not an eigenvalue of $A$, this forces $c=0$.

Therefore the template has only the identity affine symmetry.

Consequently, symmetry-equivalence of bridge pairs reduces to literal equality. Since
$$
(\alpha_1,\beta_1)\neq(\alpha_0,\beta_0),
$$
the pair $(\alpha_1,\beta_1)$ is a genuine new bridge pair.

## 7. Concrete obstruction

The currently tracked bridge state carries only
$$
H_n^\pm[\alpha_0,\beta_0].
$$
But the exact first corrected bridge expansion already contains the additional pair
$$
(\alpha_1,\beta_1)
=
\bigl(\operatorname{id}+(-400,20000),\ \operatorname{id}+(500,-20000)\bigr),
$$
coming from the $(i,j,k)=(M,M,M)$ summand.

Thus this template yields a concrete first exact obstruction:

1. the template is valid and satisfies the ternary separated-position hypotheses;
2. the current bridge state records only the standard pair $(\alpha_0,\beta_0)$;
3. the first exact bridge expansion already produces the new pair $(\alpha_1,\beta_1)$;
4. no actual symmetry of the template identifies this new pair with the standard one.

This proves a first exact obstruction to the currently tracked bridge state. No stronger claim is made here: this note does not prove that no larger finite closure exists.
```