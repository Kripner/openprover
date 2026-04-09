## Goal
Estimate $f(n)$, min convex subsets of $n$ general-position points. Does $\lim \frac{\log f(n)}{(\log n)^2}=c$ exist?

## Current bracket (verified)
$$2^{(\frac14-o(1))L^2} \le f(n) \le 2^{L^2+O(L)}, \quad L=\log_2 n.$$

## Plan
- [x] Lower bound proof (Part I) — CORRECT per verifier
- [ ] Upper bound proof (Part II) — FLAWED, needs repair:
  1. Convention fix: upper hull = cap, lower hull = cup
  2. Make $d_r$ explicit: $d_r = \prod_{j=3}^r \frac{1}{2^j-2}$, giving $\log_2 d_r = -r^2/2 + O(r)$
  3. Derive $C_k$ bound from explicit $d_r$: $d_a d_{k+2-a} \le 2^{-k(k+2)/4+O(1)}$ at $a=(k+2)/2$
  4. Justify separated construction (e.g., explicit affine maps with verified separation)
- [ ] After fix, re-verify, then submit

## Key computation for fix
$d_r \le 2^{-r(r-1)/2+1}$ (from $2^j-2 \ge 2^{j-1}$). Product:
$$d_a d_{k+2-a} \le 2^{-a(a-1)/2-(k+2-a)(k+1-a)/2+2}$$
Minimized at $a=(k+2)/2$: $\le 2^{-k(k+2)/4+2}$.
Exponent of $C_k$: $(k+2)m - k(k+2)/4 + O(\log k)$, max at $k=2m-1$ giving $m^2+m+O(\log m)$.
So $g(P_m) \le 2^{m^2+O(m)}$, giving $f(n) \le 2^{L^2+O(L)}$.

## Failed
- All averaging-based lower-bound routes closed at $\frac14$
- Cups/caps state probe: naive state not injective
- Binary/ternary separated constructions all give coefficient $\ge 1$
- Previous proof/final-estimate: FLAWED per verifier (conventions, missing derivations)

## Status
Spawning worker to write clean complete proof with all fixes.