Summary: Polished upper-bound note for the recursively separated family $P_m$, with the normalization corrected to apply only at a fixed target level (equivalently, any finite initial segment), proving $g(P_m)\le 2^{m^2+m+O(\log m)}$ and hence $f(n)\le 2^{(\log_2 n)^2+O(\log n)}$.

Let $P_1$ be a one-point set. For each $m\ge 1$, let
$$
P_{m+1}=P_m^0\cup P_m^1,
$$
where $P_m^0$ and $P_m^1$ are disjoint copies of $P_m$, every point of $P_m^1$ lies to the right of every point of $P_m^0$, every point of $P_m^1$ lies above every line through two points of $P_m^0$, and every point of $P_m^0$ lies below every line through two points of $P_m^1$. Then $|P_m|=2^m$.

For the counting arguments we need distinct $x$-coordinates, but this normalization must be made only levelwise.

Fix a target level $M$. Choose one concrete recursive realization of the finite tower $P_1,\dots,P_M$. There are only finitely many strict inequalities asserting the left-right separation of the two halves and the above/below incidences used in the recursive definition for levels $\le M$. By continuity, all these strict inequalities remain true after every sufficiently small rotation. Among those small rotations, exclude the finitely many angles for which some pair of points in $\bigcup_{j=1}^M P_j$ acquires the same $x$-coordinate. Hence there is a sufficiently small generic rotation for which, simultaneously for every $j\le M$, all points of $P_j$ have distinct $x$-coordinates and all recursive separation properties remain valid. Since the proof for $P_M$ uses only this finite tower, this levelwise normalization is enough.

Fix such an $M$, perform this normalization, and write $P_m$ for the normalized configuration at each level $m\le M$.

For a finite point set with distinct $x$-coordinates, an $r$-cup is an $r$-tuple $(p_1,\dots,p_r)$ with
$$
x(p_1)<\cdots<x(p_r)
$$
such that the successive slopes
$$
\operatorname{slope}(p_1p_2),\operatorname{slope}(p_2p_3),\dots,\operatorname{slope}(p_{r-1}p_r)
$$
are strictly increasing. An $r$-cap is defined similarly, with strictly decreasing successive slopes. Let $Q_+(r,P_m)$ be the number of $r$-cups in $P_m$, and $Q_-(r,P_m)$ the number of $r$-caps in $P_m$.

Let $C_k(P_m)$ be the number of $k$-point subsets of $P_m$ in convex position, and let
$$
g(P_m):=\sum_{k\ge 1} C_k(P_m)
$$
be the total number of convex-position subsets of $P_m$.

We take as input the recurrences
$$
Q_+(r,P_{m+1})\le 2Q_+(r,P_m)+2^mQ_+(r-1,P_m),
$$
and
$$
Q_-(r,P_{m+1})\le 2Q_-(r,P_m)+2^mQ_-(r-1,P_m).
$$

Set
$$
d_r:=\prod_{j=2}^r (2^j-2)^{-1}
\qquad(r\ge 1),
$$
with the empty product $d_1=1$.

We claim that for every $r\ge 1$ and every $m\ge 1$,
$$
Q_\pm(r,P_m)\le d_r\,2^{rm}.
$$

Proof. Fix one sign and write $q_r(m)=Q_\pm(r,P_m)$. For $r=1$ we have $q_1(m)=|P_m|=2^m=d_1\,2^m$. For $m=1$ and $r>1$, trivially $q_r(1)=0$. Now argue by induction on $r+m$. Using the recurrence and the induction hypothesis,
$$
q_r(m+1)\le 2q_r(m)+2^m q_{r-1}(m)
\le 2d_r2^{rm}+2^m d_{r-1}2^{(r-1)m}.
$$
Since $d_{r-1}=(2^r-2)d_r$, this becomes
$$
q_r(m+1)\le (2d_r+d_{r-1})2^{rm}
=2^r d_r\,2^{rm}
=d_r\,2^{r(m+1)}.
$$
This proves the claim for both $Q_+$ and $Q_-$.

Next, for every $r\ge 1$,
$$
2^j-2\ge 2^{j-1}\qquad(j\ge 2),
$$
so
$$
d_r\le \prod_{j=2}^r 2^{-(j-1)}=2^{-r(r-1)/2}.
$$

Now let $k\ge 2$. Every $k$-point subset $S\subset P_m$ in convex position has a unique leftmost point and a unique rightmost point. The boundary of $\operatorname{conv}(S)$ therefore decomposes into a lower chain and an upper chain from the leftmost to the rightmost point. If the lower chain has $a$ vertices, then $2\le a\le k$, the upper chain has $k+2-a$ vertices, the lower chain is an $a$-cup, and the upper chain is a $(k+2-a)$-cap. The pair of chains determines $S$, so
$$
C_k(P_m)\le \sum_{a=2}^k Q_+(a,P_m)\,Q_-(k+2-a,P_m).
$$

Insert the bounds for $Q_\pm$:
$$
C_k(P_m)\le \sum_{a=2}^k d_a d_{k+2-a}\,2^{(k+2)m}.
$$
Using $d_r\le 2^{-r(r-1)/2}$, we get
$$
d_a d_{k+2-a}
\le 2^{-\frac{a(a-1)}2-\frac{(k+2-a)(k+1-a)}2}.
$$
For fixed $k$, the exponent on the right is minimized when $a$ is as close as possible to $(k+2)/2$, and the minimum is
$$
\left\lfloor \frac{(k+1)^2}{4}\right\rfloor.
$$
Hence every summand is at most
$$
2^{(k+2)m-\lfloor (k+1)^2/4\rfloor},
$$
and since there are $k-1$ summands,
$$
C_k(P_m)\le (k-1)\,2^{(k+2)m-\lfloor (k+1)^2/4\rfloor}.
$$

We now sum over $k$. For $k\ge 2$, write
$$
t:=k-(2m-1).
$$
Then
$$
(k+2)m-\frac{(k+1)^2}{4}=m^2+m-\frac{t^2}{4},
$$
so
$$
(k+2)m-\left\lfloor \frac{(k+1)^2}{4}\right\rfloor
\le m^2+m+1-\frac{t^2}{4}.
$$
Also $k-1=2m-2+t\le 2m+|t|$. Therefore
$$
C_k(P_m)\le (2m+|t|)\,2^{m^2+m+1-t^2/4}.
$$
Since $C_1(P_m)=|P_m|=2^m$, we obtain
$$
g(P_m)
= C_1(P_m)+\sum_{k=2}^{2^m} C_k(P_m)
\le 2^m + 2^{m^2+m+1}\sum_{t\in \mathbb Z} (2m+|t|)\,2^{-t^2/4}.
$$
The Gaussian tail sum is $O(m)$, so
$$
g(P_m)\le 2^{m^2+m+O(\log m)}.
$$

Finally, let $f(n)$ denote the minimum possible number of convex-position subsets in an $n$-point set in general position. Put
$$
\ell:=\lceil \log_2 n\rceil.
$$
Choose any $n$-point subset $S\subseteq P_\ell$. Every convex-position subset of $S$ is also a convex-position subset of $P_\ell$, so
$$
f(n)\le g(S)\le g(P_\ell)\le 2^{\ell^2+\ell+O(\log \ell)}
=2^{(\log_2 n)^2+O(\log n)}.
$$

The flaw in the discarded $\alpha=2$ overclaim is that it implicitly treated the denominator in $d_r$ as decaying faster than justified: the uniform bound available here is only $2^j-2\ge 2^{j-1}$, not a stronger estimate that would support that claim.

Remaining proof-tightness issues: none seen after the levelwise normalization fix.

VERDICT: CORRECT