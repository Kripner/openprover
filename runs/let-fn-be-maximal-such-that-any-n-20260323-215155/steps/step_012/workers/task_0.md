Focus only on the upper-bound direction.

Context you may use:
- Lower bound is already stored as [[bounds/lower-bound-averaging]]; do not revisit it.
- We have an explicit recursive family $P_m$ of size $2^m$ with
  $P_{m+1}=P_m^0\cup P_m^1$,
  where $P_m^1$ lies to the right of $P_m^0$, every point of $P_m^1$ lies above every line through two points of $P_m^0$, and every point of $P_m^0$ lies below every line through two points of $P_m^1$.
- Reported recurrence:
$$
Q_+(r,P_{m+1})\le 2Q_+(r,P_m)+2^m Q_+(r-1,P_m),
$$
and similarly for caps.
- A previous worker derived the corrected upper bound
$$
g(P_m)\le 2^{m^2+O(m)},
$$
and an independent verifier said the argument is sound but needs minor fixes: make the base case explicit, and make the distinct-$x$ / generic-rotation assumption explicit.

Task:
Produce a self-contained, proof-quality writeup suitable to store directly as a repo item if correct.

Please do exactly this:
1. State carefully any harmless geometric normalization needed to speak about cups/caps (for example distinct $x$-coordinates after a generic rotation or equivalent).
2. Define $Q_+(r,P_m),Q_-(r,P_m),C_k(P_m),g(P_m)$.
3. Prove from the recurrence that
$$
Q_\pm(r,P_m)\le d_r\,2^{rm},
\qquad
d_r=\prod_{j=2}^r (2^j-2)^{-1},
$$
with all base cases spelled out.
4. Prove rigorously that each convex $k$-subset determines an upper/lower chain pair with sizes $a,b$ satisfying $a+b=k+2$, and deduce
$$
C_k(P_m)\le \sum_{a=2}^k Q_+(a,P_m)\,Q_-(k+2-a,P_m).
$$
5. From this, derive an explicit finite-level bound of the shape
$$
C_k(P_m)\le (k-1)\,2^{(k+2)m-\lfloor (k+1)^2/4\rfloor}
$$
or any equivalent bound you can justify cleanly.
6. Sum over $k$ to obtain the best rigorous asymptotic bound on
$$
g(P_m)=\#\{A\subseteq P_m:\ A\text{ is in convex position}\}.
$$
State the leading constant $\alpha$ in
$$
g(P_m)\le 2^{(\alpha+o(1))(\log_2 |P_m|)^2}.
$$
7. If valid, extend this from $|P_m|=2^m$ to an upper bound for $f(n)$ for arbitrary $n$ by a clean subset/monotonicity argument. If that extension fails, identify the exact obstruction and stop at the $2^m$ case.
8. Briefly note the precise flaw in the earlier overclaim with constant $2$: total cup/cap counts alone do not control convex $k$-sets without endpoint matching.

Deliverable:
- A polished repo-item-style note.
- If the arbitrary-$n$ extension works, include the final statement for $f(n)$.
- If not, state only the strongest fully rigorous bound actually obtained.