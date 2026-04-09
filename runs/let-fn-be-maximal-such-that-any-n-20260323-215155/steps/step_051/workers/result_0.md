This mechanism does not improve the lower bound. For the concrete endpoint-state count below, the certified output is only
\[
g(P)\ge \frac{\sqrt2}{3}n^{3/2}-O(n),
\]
so it is polynomial and cannot get anywhere near a \(2^{c(\log n)^2}\) lower bound, let alone beat the \(\frac14\) coefficient from [[bounds/lower-bound-averaging]].

I could not write the file into the repo because local tool execution is failing in this run (`bwrap: Unknown option --argv0`). The note below is repo-ready markdown.

```md
Summary: The most direct non-averaging count inside the classical cups/caps proof uses endpoint states $(u_i,v_i)$, where $u_i$ and $v_i$ are the longest cup/cap lengths ending at the $i$th point. This mechanism gives only
\[
g(P)\ge \frac{\sqrt 2}{3}n^{3/2}-O(n),
\]
so it is polynomial and therefore far below the stretched-exponential lower bound from [[bounds/lower-bound-averaging]]. The loss is exact: the state $(u_i,v_i)$ remembers only maximal attainable lengths, not the multiplicity of compatible predecessors, so one can certify at most one representative cup and one representative cap for each length at each endpoint.

Let
\[
P=\{p_1,\dots,p_n\}
\]
be in general position, ordered by increasing $x$-coordinate. For each $i$, let
\[
u_i:=\max\{t:\text{there is a }t\text{-cup ending at }p_i\},
\qquad
v_i:=\max\{t:\text{there is a }t\text{-cap ending at }p_i\}.
\]
By the classical Erdős-Szekeres cups/caps lemma, the pairs
\[
(u_i,v_i)\in \mathbf Z_{\ge 1}^2
\]
are all distinct.

## Concrete mechanism

For each $i$:

- fix one $t$-cup ending at $p_i$ for every $1\le t\le u_i$, obtained by truncating a fixed maximal $u_i$-cup ending at $p_i$;
- fix one $t$-cap ending at $p_i$ for every $1\le t\le v_i$, obtained by truncating a fixed maximal $v_i$-cap ending at $p_i$.

This produces exactly
\[
M(P):=\sum_{i=1}^n (u_i+v_i)
\]
chosen cup/cap subsets.

## Lemma

\[
M(P)\le 2g(P).
\]
Hence
\[
g(P)\ge \frac12\sum_{i=1}^n (u_i+v_i).
\tag{1}
\]

### Proof

Every chosen cup or cap is in convex position, so it is counted by $g(P)$.

A given convex subset $A\subseteq P$ of size at least $3$ can occur among the chosen objects at most once: if it occurs at all, then in left-to-right order it must be either a cup or a cap, and these two possibilities are mutually exclusive for $|A|\ge 3$. Also its rightmost point is intrinsic, so there is no second endpoint choice.

A $1$-subset or $2$-subset can occur at most twice, once from the cup side and once from the cap side. Therefore each convex subset contributes to at most two chosen objects, so $M(P)\le 2g(P)$. This proves (1). ∎

## Optimizing the state sum

Thus this mechanism reduces to minimizing
\[
\sum_{i=1}^n (u_i+v_i)
\]
over $n$ distinct lattice points in $\mathbf Z_{\ge 1}^2$.

For each integer $s\ge 2$, there are exactly $s-1$ pairs $(u,v)$ with $u+v=s$. Therefore the minimum is attained by taking the $n$ pairs with smallest values of $u+v$.

Let $m$ be the unique integer such that
\[
\frac{m(m-1)}2<n\le \frac{m(m+1)}2.
\]
Then all pairs with $u+v\le m$ are used, and the remaining
\[
r:=n-\frac{m(m-1)}2
\qquad (0<r\le m)
\]
pairs have sum $m+1$. Hence
\[
\sum_{i=1}^n (u_i+v_i)
\ge
\sum_{s=2}^{m} s(s-1)+r(m+1).
\]
Since
\[
\sum_{s=2}^{m} s(s-1)=\frac{m(m+1)(m-1)}3,
\]
we obtain the exact bound
\[
\sum_{i=1}^n (u_i+v_i)
\ge
\frac{m(m+1)(m-1)}3
+
\left(n-\frac{m(m-1)}2\right)(m+1).
\tag{2}
\]

Combining (1) and (2),
\[
g(P)\ge
\frac12\left[
\frac{m(m+1)(m-1)}3
+
\left(n-\frac{m(m-1)}2\right)(m+1)
\right].
\tag{3}
\]

Since $m=\sqrt{2n}+O(1)$, (3) gives
\[
g(P)\ge \frac{\sqrt 2}{3}n^{3/2}-O(n).
\tag{4}
\]

## Barrier

This endpoint-state mechanism is genuinely non-averaging, but it cannot approach the quadratic-logarithmic scale. Its output is only polynomial:
\[
\log_2 g(P)\ge \frac32\log_2 n+O(1).
\]
So this mechanism does not merely fail to beat the coefficient $\frac14$ in
\[
2^{(\frac14-o(1))(\log_2 n)^2};
\]
it does not even reach a lower bound of the form
\[
2^{c(\log n)^2}
\]
for any $c>0$.

The obstruction is precise. The classical state $(u_i,v_i)$ records only the largest cup length and largest cap length attainable at the endpoint $p_i$. It forgets how many distinct predecessor chains realize those lengths. After passing to this state, one can certify only one representative cup and one representative cap for each attainable length at that endpoint. The whole proof then collapses to a lattice-packing problem in $\mathbf Z_{\ge 1}^2$ with linear weight $u+v$, and the optimal growth is necessarily of order $n^{3/2}$.

So this concrete state-counting use of the classical cups/caps induction is a closed barrier: by itself it yields only the polynomial lower bound (4), and therefore cannot improve the quadratic coefficient $\frac14$ from [[bounds/lower-bound-averaging]].
```

If you want, I can next turn this into the repo’s exact house style once file access is working again.