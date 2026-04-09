## Post-Mortem Discussion

### The Problem

Let $f(n)$ be the largest integer such that any $n$ points in $\mathbb{R}^2$, with no three collinear, determine at least $f(n)$ convex subsets. Estimate $f(n)$. In particular, does there exist a constant $c$ such that

$$\lim_{n\to\infty} \frac{\log f(n)}{(\log n)^2} = c\,?$$

### Result

We established that $\log_2 f(n) = \Theta((\log_2 n)^2)$, with the quantitative bracket

$$2^{(\frac{1}{4} - o(1))L^2} \;\le\; f(n) \;\le\; 2^{L^2 + O(L)}, \qquad L = \log_2 n.$$

Equivalently, if the limit $c$ exists (in base-2 logs), then $\frac{1}{4} \le c \le 1$. The full proof is in [[proof/final-estimate]].

We did **not** determine whether the limit exists, nor did we pin down its value.

### Lower Bound: The Averaging Approach

The lower bound is a clean Erdős–Szekeres averaging argument ([[bounds/lower-bound-averaging]]). For each $k$, every $m$-subset with $m = ES(k)$ contains a convex $k$-gon, and double-counting gives $\mathrm{conv}_k(P) \ge \binom{n}{k}/\binom{m}{k}$. Plugging in Suk's bound $ES(k) = 2^{k+o(k)}$ and optimizing at $k = \lfloor L/2 \rfloor$ yields the $\frac{1}{4}$ coefficient.

**Key insight:** The coefficient $\frac{1}{4}$ is an intrinsic barrier to all averaging-based approaches. The function $\alpha L \cdot (L - \alpha L) = \alpha(1-\alpha)L^2$ is maximized at $\alpha = 1/2$, giving $L^2/4$, and no summation or weighting trick escapes this. We verified this barrier from several angles:

- Summing the per-$k$ bound over all $k$ ([[status/multi-k-averaging-barrier]]),
- Bootstrapping via $m$-subset totals ([[status/m-subset-total-count-bootstrapping-barrier]]),
- Multiplicity-aware double counting ([[status/multiplicity-aware-averaging-barrier]]).

All collapse back to $\frac{1}{4}$.

### Upper Bound: The Recursively Separated Construction

The upper bound constructs an explicit $n$-point set with few convex subsets ([[bounds/upper-bound-recursive-family]]). The family $P_m$ is built by a binary recursion $P_m = \Phi_L(P_{m-1}) \sqcup \Phi_R(P_{m-1})$, where the two affine images are placed so that:

1. $L_m$ lies entirely left of and above $R_m$,
2. Every point of $L_m$ is above every secant of $R_m$, and vice versa (the "separation property").

This separation forces every mixed cup to have exactly one left point and every mixed cap to have exactly one right point. The resulting recursion $Q(r, P_m) \le 2Q(r, P_{m-1}) + 2^{m-1}Q(r-1, P_{m-1})$ solves to $Q(r, P_m) \le d_r \cdot 2^{rm}$ with $d_r = \prod_{j=3}^{r}(2^j - 2)^{-1}$. The chain-pair inequality $C_k \le \sum_a Q_-(a)\,Q_+(k+2-a)$ then gives $g(P_m) \le 2^{m^2 + O(m)}$, i.e., coefficient $1$.

**Key insight:** The bottleneck is the chain-pair inequality (Lemma 5 in the proof), which forgets endpoint matching between the upper and lower hulls. The exact spanning count factors through matched endpoint states ([[lemmas/one-split-fixed-state-recurrence]]), and the first place information is truly lost is the decoupling of outer endpoints ([[status/recursive-family-information-loss]]). Tightening this is the most promising route to improving the upper bound coefficient below $1$.

### Approaches That Did Not Pan Out

Several attempts to close the gap from either side were explored:

- **Ternary separated constructions** ([[attempts/alternative-construction-balanced-ternary-split]], [[lemmas/ternary-one-split-structure]]): Splitting into three children introduces "bridge points" connecting the middle block to the outer blocks. The exact bridge-state recurrences are significantly more complex and remained unresolved ([[status/balanced-ternary-concrete-bridge-obstruction]]).

- **Fibonacci and fixed-lag splits** ([[attempts/alternative-construction-fibonacci-split]], [[status/fixed-lag-separated-recursions-obstruction]]): Non-self-similar recursions $F_m = F_{m-1} \sqcup F_{m-2}$ were tried, but even a single top-split term already forces the coefficient $\ge 1$.

- **Cups/caps state-based lower bounds** ([[attempts/cups-caps-naive-state-noninjective]]): We attempted to use the state $(u_i, v_i)$ = (longest cup ending at $p_i$, longest cap ending at $p_i$) to inject convex subsets into a lattice, but this state is not injective.

- **Endpoint-refined recursion** ([[attempts/endpoint-matched-recursive-family-worst-case-gap]], [[status/endpoint-matched-recursive-family]]): Tracking exact endpoint pairs through the recursion gives tighter formulas, but only a worst-case bound over pairs was extracted, which did not improve the coefficient.

### Open Gaps and Recommendations

The central open question remains: **what is the true coefficient?**

$$c = \lim_{n\to\infty} \frac{\log_2 f(n)}{(\log_2 n)^2} \;\stackrel{?}{\in}\; \Bigl[\tfrac{1}{4},\, 1\Bigr].$$

Here is where I think progress is most likely:

1. **Improving the upper bound (lowering the coefficient below 1).** The endpoint-matching information lost in the chain-pair inequality is substantial. The exact recurrence ([[lemmas/one-split-fixed-state-recurrence]]) counts spanning subsets as a sum over states $(\ell, \lambda, \rho, r)$ of products of endpoint-refined cup and cap counts. If one can solve this refined recursion (rather than bounding each factor independently), the coefficient should decrease. The ternary construction may also help, if the bridge-state recurrences can be closed.

2. **Improving the lower bound (raising the coefficient above 1/4).** This requires a fundamentally non-averaging technique. The averaging barrier at $1/4$ is robust ([[status/multi-k-averaging-barrier]]). A promising direction would be a structural decomposition argument—perhaps showing that any point set, after suitable partitioning, must produce many convex subsets through a mechanism more refined than just "every large subset contains a convex $k$-gon."

3. **Existence of the limit.** Even the question of whether $c$ exists is open. A sub-multiplicativity or Fekete-type argument for $\log f(n)$ would settle this, but $f$ does not obviously satisfy such a condition.

4. **Literature.** We found no prior work resolving these questions ([[status/literature-total-convex-subsets]]). The problem sits at an interesting junction of Erdős–Szekeres theory and extremal combinatorial geometry, and the gap $[1/4, 1]$ seems wide enough that there should be room for a new idea.