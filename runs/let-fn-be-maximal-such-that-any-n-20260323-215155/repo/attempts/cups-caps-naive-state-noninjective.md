Summary: The naive state $(u_i,v_i)$ defined by longest cup and cap lengths both ending at $p_i$ is not injective, so it cannot support the claimed lattice-packing lower bound.

Consider the $x$-ordered point set
$$
(1,0),(2,3),(3,1),(4,4),(5,5).
$$
Let
$$
u_i:=\max\{t:\text{there is a }t\text{-cup ending at }p_i\},
\qquad
v_i:=\max\{t:\text{there is a }t\text{-cap ending at }p_i\}.
$$
A direct slope check gives
$$
(u_i,v_i)=(1,1),(2,2),(2,3),(3,3),(3,3).
$$
So the endpoint states are not all distinct.

Consequence:
the previous cups/caps barrier draft cannot justify an optimization over $n$ distinct lattice points in $\mathbf Z_{\ge 1}^2$, and therefore does not prove the claimed $n^{3/2}$ lower bound. The duplication bound on chosen cups/caps may still be useful, but any valid state-counting argument must use a genuinely injective classical state formulation.
