Summary: Draft one-split structural lemma says a convex subset spanning the recursive split decomposes as a left cap plus right cup under explicit left-right and high-above hypotheses, but the proof still needs two minor rigor fixes.

Draft statement from worker output:

Assume for the split
$$
P_m=L_m\sqcup R_m
$$
that, after a generic rotation, all $x$-coordinates are distinct, and:
1. every point of $L_m$ lies to the left of every point of $R_m$;
2. every line through two points of $L_m$ lies strictly below every point of $R_m$;
3. every line through two points of $R_m$ lies strictly above every point of $L_m$.

Let $S\subset P_m$ be in convex position, with
$$
S\cap L_m\neq\varnothing,\qquad S\cap R_m\neq\varnothing.
$$
Let
$$
\ell=\text{leftmost point of }S,\quad r=\text{rightmost point of }S,
$$
and
$$
\lambda=\text{rightmost point of }(S\cap L_m),\quad
\rho=\text{leftmost point of }(S\cap R_m).
$$
Let $U(S)$ and $D(S)$ be the upper and lower hull chains of $S$, from left to right.

Claim:
- $\ell\in L_m$ and $r\in R_m$;
- the upper hull contains exactly one vertex from $L_m$, namely $\ell$;
- the lower hull contains exactly one vertex from $R_m$, namely $r$.

Hence
$$
U(S)=\ell,\rho=u_1,u_2,\dots,u_t=r
$$
with all interior $u_i\in R_m$, and
$$
D(S)=\ell=v_1,v_2,\dots,v_s=\lambda,r
$$
with all interior $v_j\in L_m$.

So:
- $S\cap R_m$ is exactly the upper-hull chain in $R_m$, i.e. a cup with endpoints $(\rho,r)$;
- $S\cap L_m$ is exactly the lower-hull chain in $L_m$, i.e. a cap with endpoints $(\ell,\lambda)$.

Therefore every spanning convex subset has the exact decomposition
$$
S=(\text{cap in }L_m\text{ with endpoints }(\ell,\lambda))
\sqcup
(\text{cup in }R_m\text{ with endpoints }(\rho,r)).
$$

State data suggested by worker:
$$
(\ell,\lambda,\rho,r),
$$
equivalently a left cap-state indexed by $(\ell,\lambda)$ and a right cup-state indexed by $(\rho,r)$.

Verifier feedback:
- The conclusion appears correct under the stated hypotheses.
- Two minor fixes are still needed before this should be promoted to a lemma item:
  1. explicitly justify why “more than one $L_m$-vertex on the upper hull” implies two consecutive $L_m$-vertices on that chain, using left-right $x$-separation and chain monotonicity;
  2. replace the sentence “every point of a set in convex position lies on exactly one of the two hull chains” by the correct endpoint-aware version, since the common endpoints lie on both chains.

Use this item as the source draft for a clean repaired lemma.
