No extra hypothesis is needed under the stored one-split assumptions. I was not able to write the file because the workspace tool wrapper is failing before command execution (`bwrap: Unknown option --argv0`), so the note content is below for direct storage at [lemmas/one-split-crossing-cup-cap-identities.md](/home/josh/projects/openprover/runs/let-fn-be-maximal-such-that-any-n-20260323-215155/lemmas/one-split-crossing-cup-cap-identities.md).

```md
Assume the hypotheses of [[lemmas/one-split-structure-spanning-convex-subsets]]: namely
$$
P=L\sqcup R,
$$
every point of $L$ lies to the left of every point of $R$, every line through two points of $L$ lies strictly below every point of $R$, and every line through two points of $R$ lies strictly above every point of $L$.

For $t\ge 2$ and points $a,b$ of a planar point set $X$, write $Q_+(t,X;a,b)$ for the number of $t$-cups in $X$ whose left and right endpoints are $a,b$, and $Q_-(t,X;a,b)$ for the number of $t$-caps in $X$ whose left and right endpoints are $a,b$. Equivalently, in left-to-right order, the consecutive slopes of a cup are strictly increasing and those of a cap are strictly decreasing.

For $\ell\in L$, $r\in R$, and $t\ge 2$, write $Q_+^\times(t+1,P;\ell,r)$ for the number of spanning $(t+1)$-cups $S\subseteq P$ with global endpoints $(\ell,r)$. Define $Q_-^\times(t+1,P;\ell,r)$ analogously for spanning caps.

**Proposition.**
Under the one-split hypotheses, the following hold.

1. If $S\subseteq P$ is a spanning cup with global endpoints $(\ell,r)$, then
$$
S\cap L=\{\ell\}.
$$
So every spanning cup has exactly one point in the left half, namely its global left endpoint.

2. If $S\subseteq P$ is a spanning cap with global endpoints $(\ell,r)$, then
$$
S\cap R=\{r\}.
$$
So every spanning cap has exactly one point in the right half, namely its global right endpoint.

3. Consequently, for every $\ell\in L$, $r\in R$, and $t\ge 2$,
$$
Q_+^\times(t+1,P;\ell,r)=\sum_{\rho\in R,\ \rho<r} Q_+(t,R;\rho,r),
$$
and
$$
Q_-^\times(t+1,P;\ell,r)=\sum_{\lambda\in L,\ \ell<\lambda} Q_-(t,L;\ell,\lambda).
$$

Here $\rho<r$ and $\ell<\lambda$ refer to the left-to-right $x$-order.

**Proof.**
Let $S\subseteq P$ be spanning, and use the notation of [[lemmas/one-split-structure-spanning-convex-subsets]]:
$$
\ell=\min_x S,\qquad r=\max_x S,
$$
$$
\lambda=\max_x(S\cap L),\qquad \rho=\min_x(S\cap R).
$$
That lemma shows that $S\cap L$ is a cap with endpoints $(\ell,\lambda)$, $S\cap R$ is a cup with endpoints $(\rho,r)$, and if
$$
S\cap L=\{v_1=\ell<\cdots<v_s=\lambda\},
$$
then
$$
D(S)=v_1,\dots,v_s,r,
$$
while if
$$
S\cap R=\{u_1=\rho<\cdots<u_t=r\},
$$
then
$$
U(S)=\ell,u_1,\dots,u_t.
$$

Now suppose that $S$ is itself a cup. Then its lower hull has only the two global endpoints $\ell,r$. Comparing with
$$
D(S)=v_1,\dots,v_s,r
$$
forces $s=1$, hence $\lambda=\ell$ and
$$
S\cap L=\{\ell\}.
$$
This proves (1).

The proof of (2) is dual. If $S$ is a spanning cap, then its upper hull has only the two global endpoints $\ell,r$. Comparing with
$$
U(S)=\ell,u_1,\dots,u_t
$$
forces $t=1$, hence $\rho=r$ and
$$
S\cap R=\{r\}.
$$

For the counting identities, fix $\ell\in L$, $r\in R$, and $t\ge 2$.

For cups, define
$$
\Phi(S)=S\cap R.
$$
By (1), this gives a map from spanning $(t+1)$-cups with endpoints $(\ell,r)$ into the disjoint union over $\rho\in R$ with $\rho<r$ of the sets of $t$-cups in $R$ with endpoints $(\rho,r)$. It is injective because
$$
S=\{\ell\}\sqcup \Phi(S).
$$

To prove surjectivity, let
$$
T=\{u_1=\rho<u_2<\cdots<u_t=r\}\subseteq R
$$
be a $t$-cup, and set
$$
S:=\{\ell\}\cup T.
$$
Since $T$ is a cup,
$$
\operatorname{slope}(u_1,u_2)<\operatorname{slope}(u_2,u_3)<\cdots<\operatorname{slope}(u_{t-1},u_t).
$$
Also, $u_1,u_2\in R$, so the line through $u_1,u_2$ lies strictly above every point of $L$, in particular above $\ell$. Because $x_\ell<x_{u_1}<x_{u_2}$, this is equivalent to
$$
\operatorname{slope}(\ell,u_1)<\operatorname{slope}(u_1,u_2).
$$
Hence
$$
\operatorname{slope}(\ell,u_1)
<
\operatorname{slope}(u_1,u_2)
<
\cdots
<
\operatorname{slope}(u_{t-1},u_t),
$$
so
$$
\ell,u_1,\dots,u_t
$$
is a $(t+1)$-cup with endpoints $(\ell,r)$. This includes the case $t=2$: one only uses
$$
\operatorname{slope}(\ell,u_1)<\operatorname{slope}(u_1,r),
$$
so no separate interior-point argument is needed.

Therefore $\Phi$ is bijective, and taking cardinalities gives
$$
Q_+^\times(t+1,P;\ell,r)=\sum_{\rho\in R,\ \rho<r} Q_+(t,R;\rho,r).
$$

The cap identity is dual. Let
$$
T=\{v_1=\ell<v_2<\cdots<v_t=\lambda\}\subseteq L
$$
be a $t$-cap, and set
$$
S:=T\cup\{r\}.
$$
Since $T$ is a cap,
$$
\operatorname{slope}(v_1,v_2)>\operatorname{slope}(v_2,v_3)>\cdots>\operatorname{slope}(v_{t-1},v_t).
$$
Also, $v_{t-1},v_t\in L$, so the line through $v_{t-1},v_t$ lies strictly below every point of $R$, in particular below $r$. Because $x_{v_{t-1}}<x_{v_t}<x_r$, this is equivalent to
$$
\operatorname{slope}(v_{t-1},v_t)>\operatorname{slope}(v_t,r).
$$
Hence
$$
\operatorname{slope}(v_1,v_2)>
\cdots>
\operatorname{slope}(v_{t-1},v_t)>
\operatorname{slope}(v_t,r),
$$
so
$$
v_1,\dots,v_t,r
$$
is a $(t+1)$-cap with endpoints $(\ell,r)$. Thus
$$
Q_-^\times(t+1,P;\ell,r)=\sum_{\lambda\in L,\ \ell<\lambda} Q_-(t,L;\ell,\lambda).
$$

Endpoint matching is enforced because the global outer endpoints $(\ell,r)$ are fixed, while the split lemma recovers uniquely the first right-side vertex $\rho$ for cups and the last left-side vertex $\lambda$ for caps. $\square$
```