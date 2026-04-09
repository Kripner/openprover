**Lemma (one-split structure of a spanning convex subset).**  
To make “standard recursively separated position” precise, it is enough to assume the following for the split
$$
P_m=L_m\sqcup R_m.
$$
After a generic rotation, all $x$-coordinates are distinct, and:

1. every point of $L_m$ lies to the left of every point of $R_m$;
2. every line through two points of $L_m$ lies strictly below every point of $R_m$;
3. every line through two points of $R_m$ lies strictly above every point of $L_m$.

Equivalently, $R_m$ is *high above* $L_m$.

Now let $S\subset P_m$ be in convex position, with
$$
S\cap L_m\neq\varnothing,\qquad S\cap R_m\neq\varnothing.
$$
Write
$$
\ell:=\text{leftmost point of }S,\qquad r:=\text{rightmost point of }S.
$$
Then necessarily $\ell\in L_m$ and $r\in R_m$. Also write
$$
\lambda:=\text{rightmost point of }(S\cap L_m),\qquad
\rho:=\text{leftmost point of }(S\cap R_m).
$$

Let $U(S)$ and $D(S)$ be the upper and lower hull chains of $S$, from left to right.

Then:

- $U(S)$ contains exactly one vertex from $L_m$, namely $\ell$.
- $D(S)$ contains exactly one vertex from $R_m$, namely $r$.

Hence the hull chains have the form
$$
U(S)=\ell,\rho=u_1,u_2,\dots,u_t=r
$$
with all $u_i\in R_m$, and
$$
D(S)=\ell=v_1,v_2,\dots,v_s=\lambda,r
$$
with all $v_j\in L_m$.

Therefore:

- $S\cap R_m$ is exactly the upper-hull chain in $R_m$, so it is a (possibly degenerate) cup with endpoints $(\rho,r)$;
- $S\cap L_m$ is exactly the lower-hull chain in $L_m$, so it is a (possibly degenerate) cap with endpoints $(\ell,\lambda)$.

In particular, every spanning convex subset has the exact decomposition
$$
S=(\text{cap in }L_m\text{ with endpoints }(\ell,\lambda))
\;\sqcup\;
(\text{cup in }R_m\text{ with endpoints }(\rho,r)).
$$

**Proof.**  
An edge of the upper hull is a supporting segment whose line has all points of $S$ on or below it. If the upper hull contained two consecutive vertices from $L_m$, then that supporting line would pass through two points of $L_m$, hence by hypothesis every point of $S\cap R_m$ would lie strictly above it, contradiction. So the upper hull contains at most one vertex from $L_m$; since it starts at the leftmost point, that vertex is $\ell$.

Similarly, an edge of the lower hull has all points of $S$ on or above it. If the lower hull contained two consecutive vertices from $R_m$, then every point of $S\cap L_m$ would lie strictly below the supporting line, contradiction. So the lower hull contains at most one vertex from $R_m$; since it ends at the rightmost point, that vertex is $r$.

Because every point of a set in convex position lies on exactly one of the two hull chains, all points of $S\cap R_m$ other than possibly $r$ must lie on the upper chain, and all points of $S\cap L_m$ other than possibly $\ell$ must lie on the lower chain. This gives the stated forms of $U(S)$ and $D(S)$, and the cup/cap description follows immediately. $\square$

**State data for a later recurrence.**  
For a convex subset crossing the split, the minimal endpoint data is
$$
(\ell,\lambda,\rho,r),
$$
equivalently:

- a cap-state on the left, indexed by its ordered endpoints $(\ell,\lambda)$;
- a cup-state on the right, indexed by its ordered endpoints $(\rho,r)$.

This is exactly the information needed to enforce endpoint matching. Indeed:

- $\ell$ is simultaneously the unique left-side vertex on the upper hull and the left endpoint of the lower-hull cap in $L_m$;
- $r$ is simultaneously the unique right-side vertex on the lower hull and the right endpoint of the upper-hull cup in $R_m$.

So the upper and lower hull chains of the full set have the same global endpoints $(\ell,r)$ automatically. Unrefined totals such as $Q_+$ and $Q_-$ forget this endpoint data, which is precisely why they do not by themselves control convex subsets spanning the split.