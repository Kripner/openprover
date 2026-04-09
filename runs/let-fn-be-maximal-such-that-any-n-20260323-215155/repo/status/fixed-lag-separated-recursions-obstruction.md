Summary: For the fixed-lag separated recursion
$$
F_m^{(t)}=F_{m-1}^{(t)}\sqcup F_{m-t}^{(t)} \qquad (t\ge 2),
$$
one explicit top-split term already gives
$$
\limsup_{m\to\infty}\frac{\log_2 g(F_m^{(t)})}{(\log_2 |F_m^{(t)}|)^2}\ge \alpha_t,
\qquad
\alpha_t=\frac{t+1}{2t\log_2\lambda_t},
$$
where $\lambda_t>1$ is the positive root of $\lambda_t^t=\lambda_t^{t-1}+1$. Moreover $\alpha_t>1$ for every fixed $t\ge 2$. Hence no fixed lag can lower the quadratic coefficient below $1$; the whole fixed-lag binary family is obstructed.

Fix $t\ge 2$.

## Definition

Define $F_1^{(t)},\dots,F_t^{(t)}$ to be one-point sets. For $m\ge t+1$, define
$$
F_m^{(t)}=L_m\sqcup R_m,
$$
where $L_m$ is an affine copy of $F_{m-1}^{(t)}$, $R_m$ is an affine copy of $F_{m-t}^{(t)}$, and $(L_m,R_m)$ is in the standard separated position.

Let
$$
N_m:=|F_m^{(t)}|.
$$
Then
$$
N_1=\cdots=N_t=1,
\qquad
N_m=N_{m-1}+N_{m-t}\quad (m\ge t+1).
$$
Let $\lambda_t>1$ be the unique positive root of
$$
x^t-x^{t-1}-1=0.
$$
Then
$$
N_m=\Theta_t(\lambda_t^m),
\qquad
\log_2 N_m=m\log_2\lambda_t+O_t(1).
$$

For $a\ge 1$ define
$$
U_m(a):=Q_+(a,F_m^{(t)}),
\qquad
V_m(a):=Q_-(a,F_m^{(t)}),
$$
and for $k\ge 1$ define
$$
C_m(k):=C_k(F_m^{(t)}).
$$

## Exact Recurrences

For $a\ge 2$ and $m\ge t+1$, the cup counts satisfy the exact identity
$$
U_m(a)=U_{m-1}(a)+U_{m-t}(a)+N_{m-t}U_{m-1}(a-1),
$$
with
$$
U_m(1)=N_m.
$$

For $a\ge 2$ and $m\ge t+1$, the cap counts satisfy the exact identity
$$
V_m(a)=V_{m-1}(a)+V_{m-t}(a)+N_{m-1}V_{m-t}(a-1),
$$
with
$$
V_m(1)=N_m.
$$

For $k\ge 1$ and $m\ge t+1$, the convex-subset counts satisfy the exact identity
$$
C_m(k)=C_{m-1}(k)+C_{m-t}(k)+\sum_{a=1}^{k-1}U_{m-1}(a)V_{m-t}(k-a).
$$

## Maximal Cups

Let
$$
\nu_m:=\max\{a:U_m(a)>0\}.
$$
Then
$$
\nu_1=\cdots=\nu_t=1,
\qquad
\nu_m=\nu_{m-1}+1 \quad (m\ge t+1),
$$
hence exactly
$$
\nu_m=m-t+1 \qquad (m\ge t).
$$

Set
$$
U_m^*:=U_m(\nu_m).
$$
For $m\ge t+1$, the maximal cups are exactly the spanning ones, so
$$
U_m^*=N_{m-t}U_{m-1}^*
$$
is exact. Since $U_t^*=1$, it follows that
$$
U_m^*=\prod_{j=1}^{m-t}N_j
\qquad (m\ge t).
$$

## Maximal Caps

Let
$$
v_m:=\max\{a:V_m(a)>0\}.
$$
Then
$$
v_1=\cdots=v_t=1,
\qquad
v_m=\max\bigl(v_{m-1},1+v_{m-t}\bigr)\quad (m\ge t+1),
$$
so exactly
$$
v_m=1+\left\lfloor\frac{m-1}{t}\right\rfloor.
$$

The maximal cap length increases only at depths $m=qt+1$. Define
$$
W_q:=V_{qt+1}(q+1).
$$
Since the maximal cap at depth $qt+1$ must be spanning, one gets the exact identity
$$
W_q=N_{qt}W_{q-1}
$$
for $q\ge 1$, with $W_0=1$. Therefore
$$
W_q=\prod_{i=1}^q N_{it}.
$$

## Explicit Top-Split Obstruction

Take
$$
m_q:=(q+1)t+1.
$$
Then
$$
m_q-1=(q+1)t,
\qquad
m_q-t=qt+1.
$$
In the exact recurrence for $C_{m_q}(k)$, keep only the single term
$$
a=\nu_{m_q-1}=qt+1,
\qquad
k-a=v_{m_q-t}=q+1.
$$
This gives the inequality
$$
C_{m_q}\bigl(q(t+1)+2\bigr)
\ge
U_{(q+1)t}^*\,W_q
=
\left(\prod_{j=1}^{qt}N_j\right)
\left(\prod_{i=1}^q N_{it}\right).
$$

Using $N_r=\Theta_t(\lambda_t^r)$,
$$
\log_2 U_{(q+1)t}^*
=(\log_2\lambda_t)\sum_{j=1}^{qt}j+O_t(q),
$$
and
$$
\log_2 W_q
=(\log_2\lambda_t)\sum_{i=1}^q it+O_t(q).
$$
Therefore
$$
\log_2 g(F_{m_q}^{(t)})
\ge
(\log_2\lambda_t)\left(\sum_{j=1}^{qt}j+\sum_{i=1}^q it\right)+O_t(q).
$$
Since
$$
\sum_{j=1}^{qt}j+\sum_{i=1}^q it
=
\frac{qt(qt+1)}2+\frac{tq(q+1)}2
=
\frac{t(t+1)}2\,q^2+O_t(q),
$$
and
$$
m_q=tq+O_t(1),
$$
this becomes
$$
\log_2 g(F_{m_q}^{(t)})
\ge
\left(\frac{t+1}{2t}\log_2\lambda_t\right)m_q^2+O_t(m_q).
$$
Using
$$
\log_2 N_{m_q}=m_q\log_2\lambda_t+O_t(1),
$$
we obtain
$$
g(F_{m_q}^{(t)})
\ge
2^{\left(\alpha_t+o(1)\right)(\log_2 N_{m_q})^2},
\qquad
\alpha_t:=\frac{t+1}{2t\log_2\lambda_t}.
$$
Hence
$$
\limsup_{m\to\infty}\frac{\log_2 g(F_m^{(t)})}{(\log_2 N_m)^2}\ge \alpha_t.
$$

## Why $\alpha_t>1$

For $t=2$, $\lambda_2=\varphi$, and $\log_2\varphi<\frac34$, so
$$
\alpha_2=\frac{3}{4\log_2\varphi}>1.
$$

For $t=3$, one has $\lambda_3<\frac32$ and $\log_2(3/2)<\frac23$, so
$$
\alpha_3=\frac{4}{6\log_2\lambda_3}>1.
$$

For every $t\ge 4$,
$$
(\sqrt2)^t-(\sqrt2)^{t-1}-1>0,
$$
so $\lambda_t<\sqrt2$, hence $\log_2\lambda_t<\frac12$. Therefore
$$
\alpha_t=\frac{t+1}{2t\log_2\lambda_t}
>
\frac{t+1}{2t\cdot (1/2)}
=
\frac{t+1}{t}
>1.
$$

## Conclusion

For every fixed $t\ge 2$, the separated recursion
$$
F_m^{(t)}=F_{m-1}^{(t)}\sqcup F_{m-t}^{(t)}
$$
has an explicit top-split contribution forcing a quadratic coefficient strictly larger than $1$. So increasing the lag does not help inside the binary separated paradigm. The next productive direction is to leave binary recursions entirely.
