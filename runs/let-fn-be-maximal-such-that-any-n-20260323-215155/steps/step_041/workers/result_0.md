I couldn’t write the file because the workspace command wrapper is failing; the repo-ready markdown is below.

```markdown
Summary: In the explicit separated balanced ternary template
$$
\Phi_L(z)=Az+t_L,\qquad \Phi_M(z)=Az+t_M,\qquad \Phi_R(z)=Az+t_R
$$
with
$$
A=\begin{pmatrix}\frac1{10}&0\\[2pt]0&\frac1{100}\end{pmatrix},\qquad
t_L=\binom{0}{3},\quad t_M=\binom{2}{0},\quad t_R=\binom{5}{-2},
$$
the first conjugation expansion of the tracked bridge pair $(\alpha_0,\beta_0)=(\Phi_M^{-1}\Phi_L,\Phi_M^{-1}\Phi_R)$ already produces new affine pairs, for example
$$
(\mathrm{id},T_{(50,-500)}),\qquad (T_{(-50,500)},\mathrm{id}),
$$
so the state $\{A_m,B_m,U_m,D_m\}$ does not close as currently tracked.

# status/balanced-ternary-concrete-bridge-obstruction

Take
$$
\Phi_L(z)=Az+t_L,\qquad \Phi_M(z)=Az+t_M,\qquad \Phi_R(z)=Az+t_R,
$$
with
$$
A=\begin{pmatrix}\frac1{10}&0\\[2pt]0&\frac1{100}\end{pmatrix},\qquad
t_L=\binom{0}{3},\quad t_M=\binom{2}{0},\quad t_R=\binom{5}{-2}.
$$
Let $T_0=\{(0,0)\}$ and $T_n=\Phi_L(T_{n-1})\sqcup\Phi_M(T_{n-1})\sqcup\Phi_R(T_{n-1})$.

## 1. Separated-position check

From the coordinate recursions,
$$
0\le x(T_n)\le \frac{50}{9},\qquad -\frac{200}{99}\le y(T_n)\le \frac{300}{99}.
$$
Hence
$$
L_n\subseteq \Bigl[0,\frac59\Bigr]\times \Bigl[\frac{295}{99},\frac{100}{33}\Bigr],
$$
$$
M_n\subseteq \Bigl[2,\frac{23}{9}\Bigr]\times \Bigl[-\frac{2}{99},\frac{1}{33}\Bigr],
$$
$$
R_n\subseteq \Bigl[5,\frac{50}{9}\Bigr]\times \Bigl[-\frac{200}{99},-\frac{65}{33}\Bigr].
$$
So the $x$-ranges are disjoint and ordered.

Let $S_n$ be the maximum absolute slope of a secant of $T_n$. Same-child secants scale by $\frac1{10}$:
$$
\operatorname{slope}(Az_1+t_i,Az_2+t_i)=\frac1{10}\operatorname{slope}(z_1,z_2).
$$
Cross-child secants satisfy
$$
\frac{302/99}{13/9}<3,\qquad \frac{203/99}{22/9}<3,\qquad \frac{500/99}{40/9}<3,
$$
for the pairs $(L,M),(M,R),(L,R)$ respectively, so inductively $S_n\le 3$ for all $n$.

Therefore every secant inside one child has slope magnitude at most $\frac3{10}$. Using the rectangles above:

- every $L_n$-secant, evaluated anywhere on $x\in[2,50/9]$, has
  $$
  y\ge \frac{295}{99}-\frac3{10}\cdot \frac{50}{9}=\frac{130}{99}>\frac{1}{33},
  $$
  hence lies strictly above $M_n\cup R_n$;

- every $M_n$-secant, evaluated on $x\in[0,5/9]$, has
  $$
  y\le \frac{1}{33}+\frac3{10}\cdot \frac{23}{9}<\frac{295}{99},
  $$
  so it lies strictly below $L_n$, and evaluated on $x\in[5,50/9]$ has
  $$
  y\ge -\frac{2}{99}-\frac3{10}\Bigl(\frac{50}{9}-2\Bigr)>-\frac{65}{33},
  $$
  so it lies strictly above $R_n$;

- every $R_n$-secant, evaluated on $x\in[0,23/9]$, has
  $$
  y\le -\frac{65}{33}+\frac3{10}\cdot \frac{50}{9}=-\frac{10}{33}<-\frac{2}{99},
  $$
  hence lies strictly below $L_n\cup M_n$.

So this template satisfies the ternary separated-position hypotheses.

## 2. Basic bridge pair

Since
$$
A^{-1}=\begin{pmatrix}10&0\\[2pt]0&100\end{pmatrix},
$$
we get
$$
\alpha_0=\Phi_M^{-1}\Phi_L=T_{(-20,300)},\qquad
\beta_0=\Phi_M^{-1}\Phi_R=T_{(30,-200)},
$$
where $T_{(a,b)}(z)=z+\binom{a}{b}$.

Thus
$$
U_m(\lambda,r)=H_{m-1}^+[T_{(-20,300)},T_{(30,-200)}](\lambda,r),
$$
$$
D_m(\ell,\rho)=H_{m-1}^-[T_{(-20,300)},T_{(30,-200)}](\ell,\rho).
$$

## 3. First-generation conjugates

Exactly,
$$
\Phi_k^{-1}\alpha_0\Phi_i=T_{A^{-1}(t_i+t_L-t_M-t_k)},\qquad
\Phi_k^{-1}\beta_0\Phi_j=T_{A^{-1}(t_j+t_R-t_M-t_k)}.
$$

For the $\alpha$-side:
$$
\begin{array}{c|ccc}
\Phi_k^{-1}\alpha_0\Phi_i & i=L & i=M & i=R\\ \hline
k=L & T_{(-20,300)} & \mathrm{id} & T_{(30,-200)}\\
k=M & T_{(-40,600)} & T_{(-20,300)} & T_{(10,100)}\\
k=R & T_{(-70,800)} & T_{(-50,500)} & T_{(-20,300)}
\end{array}
$$

For the $\beta$-side:
$$
\begin{array}{c|ccc}
\Phi_k^{-1}\beta_0\Phi_j & j=L & j=M & j=R\\ \hline
k=L & T_{(30,-200)} & T_{(50,-500)} & T_{(80,-700)}\\
k=M & T_{(10,100)} & T_{(30,-200)} & T_{(60,-400)}\\
k=R & T_{(-20,300)} & \mathrm{id} & T_{(30,-200)}
\end{array}
$$

## 4. Exact obstruction at first expansion

Take $i=j=M$. Then the exact recursive identity gives
$$
H_n^\pm[\alpha_0,\beta_0](\Phi_M(x),\Phi_M(y))
=
\sum_{k\in\{L,M,R\}}
H_{n-1}^\pm[\Phi_k^{-1}\alpha_0\Phi_M,\Phi_k^{-1}\beta_0\Phi_M](x,y),
$$
so
$$
H_n^\pm[T_{(-20,300)},T_{(30,-200)}](\Phi_M(x),\Phi_M(y))
$$
$$
=
H_{n-1}^\pm[\mathrm{id},T_{(50,-500)}](x,y)
+
H_{n-1}^\pm[T_{(-20,300)},T_{(30,-200)}](x,y)
+
H_{n-1}^\pm[T_{(-50,500)},\mathrm{id}](x,y).
$$

The middle term is the tracked bridge type. The other two are new.

## 5. These are not symmetry reductions

Any affine symmetry $S(z)=Bz+b$ of the template must satisfy
$$
S\circ \Phi_i=\Phi_{\pi(i)}\circ S,
$$
hence $BA=AB$. Since $A=\operatorname{diag}(1/10,1/100)$ has distinct eigenvalues, $B$ is diagonal.

On $x$-coordinates, a diagonal affine map acts by $x\mapsto ax+b_x$. But the child $x$-translations are $\{0,2,5\}$, which is not an arithmetic progression, so no nontrivial affine self-map of the line permutes them. Hence $\pi$ is the identity.

Then
$$
Bt_i+b=Ab+t_i\qquad(i=L,M,R).
$$
Subtracting shows that $B$ fixes both $t_M-t_L=(2,-3)$ and $t_R-t_M=(3,-2)$. These are linearly independent, so $B=I$. Then $b=Ab$, hence $b=0$.

Therefore the template has no nontrivial affine symmetry. In particular,
$$
(\mathrm{id},T_{(50,-500)})
\quad\text{and}\quad
(T_{(-50,500)},\mathrm{id})
$$
are not symmetry-equivalent to
$$
(T_{(-20,300)},T_{(30,-200)}).
$$

## 6. Conclusion

This explicit template gives the first exact obstruction requested in [[attempts/balanced-ternary-bridge-conjugation-expansion]]: the currently tracked bridge state does not close. A genuinely new bridge pair appears already at first expansion, concretely in the $(i,j,k)=(M,M,L)$ and $(M,M,R)$ terms.
```