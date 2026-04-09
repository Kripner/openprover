The main argument is **not correct as written**. Its key step is the claim that for
$$
u_i=\max\{t:\text{there is a }t\text{-cup ending at }p_i\},\qquad
v_i=\max\{t:\text{there is a }t\text{-cap ending at }p_i\},
$$
the pairs $(u_i,v_i)$ are all distinct. For this concrete choice, that is false.

A counterexample is the $x$-ordered set
$$
(1,0),(2,3),(3,1),(4,4),(5,5).
$$
A direct slope check gives
$$
(u_i,v_i)=(1,1),(2,2),(2,3),(3,3),(3,3).
$$
So the endpoint states are **not** distinct. Therefore the optimization step over $n$ distinct lattice points in $\mathbf Z_{\ge 1}^2$, and hence formulas (2)-(4), do not follow.

The duplication bound $M(P)\le 2g(P)$ is basically fine (assuming $g(P)$ counts $1$- and $2$-point convex subsets; otherwise it only changes the estimate by $O(n)$). So the overall barrier idea may be repairable by switching to a genuinely distinct classical state formulation, but the worker’s specific proof does **not** establish the claimed
$$
g(P)\ge \frac{\sqrt2}{3}n^{3/2}-O(n).
$$

VERDICT: NEEDS MINOR FIXES - distinctness of the chosen endpoint states is false, so the $n^{3/2}$ barrier is not proved as written