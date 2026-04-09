Focus only on the lower-bound side.

Context:
- For an n-point set P in general position, let
  $$g(P):=\#\\{A\\subseteq P: A\\text{ is in convex position}\\},$$
  and let
  $$f(n):=\\min_{|P|=n} g(P).$$
- Verified: [[bounds/lower-bound-averaging]] gives
  $$f(n)\\ge 2^{(\\frac14-o(1))(\\log_2 n)^2}.$$
- Verified barriers:
  1. [[status/multi-k-averaging-barrier]] shows that summing the per-k averaging bounds over all admissible k still has quadratic constant $\\frac14$.
  2. [[status/multiplicity-aware-averaging-barrier]] shows that, for fixed k, enlarging the witness size m and counting all convex k-subsets inside each m-subset also collapses back to the original bound.

Task:
Investigate the next natural averaging mechanism beyond those two barriers: average the full total-count lower bound over m-subsets.

Concretely, for fixed m \\le n, every m-subset Q \\subseteq P satisfies
$$g(Q)\\ge f(m).$$
Set up the exact double count obtained by summing g(Q) over all m-subsets of P, i.e. count pairs
$$(A,Q)\\quad\\text{with }A\\subseteq Q\\subseteq P,\\ |Q|=m,\\ A\\text{ convex}.$$

Determine the focused question:
Can any asymptotic choice of m, combined only with the currently verified lower bound on f(m), produce a lower bound on f(n) whose quadratic coefficient beats $\\frac14$?
Or does this subset-bootstrapping route also close up as a barrier?

What I need:
1. The exact weighted inequality relating $\\sum_{|Q|=m} g(Q)$ to the size-by-size counts $\\mathrm{conv}_t(P)$ or directly to $g(P)$.
2. Either:
   - a concrete improvement beyond quadratic constant $\\frac14$, or
   - a precise barrier statement showing that bootstrapping through m-subsets and the current lower bound on f(m) still cannot raise the coefficient.
3. Repo-item-ready markdown if successful.

Requirements:
- Keep it self-contained.
- Use only current repo facts; no literature/web.
- Do not branch into upper-bound constructions or unrelated mechanisms.
- This is one focused question: does averaging the full lower bound f(m) over m-subsets bootstrap the constant past $\\frac14$?