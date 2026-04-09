Summary: Complete estimate of $f(n)$ with rigorous proofs of matching-scale bounds.

# Estimating the minimum number of convex subsets

## Statement

Let $f(n)$ be the largest integer such that any $n$ points in $\mathbb{R}^2$, with no three collinear, determine at least $f(n)$ convex subsets. Setting $L = \log_2 n$, we prove:

$$2^{(\frac{1}{4} - o(1))L^2} \le f(n) \le 2^{L^2 + O(L)}.$$

In particular, $\frac{1}{4} \le \liminf_{n\to\infty} \frac{\log_2 f(n)}{(\log_2 n)^2} \le \limsup_{n\to\infty} \frac{\log_2 f(n)}{(\log_2 n)^2} \le 1$.

---

## Part I: Lower bound — $f(n) \ge 2^{(\frac{1}{4}-o(1))L^2}$

### Notation

For a finite point set $P$ in general position (no three collinear), define:
- $g(P) := \#\{A \subseteq P : A \text{ is in convex position}\}$,
- $\mathrm{conv}_k(P) := \#\{A \subseteq P : |A| = k,\; A \text{ is in convex position}\}$,
- $f(n) := \min\{g(P) : |P| = n,\; P \text{ in general position}\}$,
- $ES(k)$ = the Erdős–Szekeres number: the smallest $m$ such that any $m$ points in general position contain a convex $k$-gon.

### Proposition (Fixed-$k$ averaging bound)

Fix $k \ge 3$ and set $m := ES(k)$. For every $n$-point set $P$ in general position with $n \ge m$:
$$\mathrm{conv}_k(P) \ge \frac{\binom{n}{k}}{\binom{m}{k}}.$$

**Proof.** Define the set of pairs
$$\mathcal{X} := \{(A, Q) : A \subseteq Q \subseteq P,\; |A| = k,\; |Q| = m,\; A \text{ in convex position}\}.$$

*Lower bound on $|\mathcal{X}|$:* For each $m$-element subset $Q \subseteq P$, the definition of $ES(k)$ guarantees at least one convex $k$-subset $A \subseteq Q$. Hence $|\mathcal{X}| \ge \binom{n}{m}$.

*Upper bound on $|\mathcal{X}|$:* For each convex $k$-subset $A$, the number of $m$-element supersets $Q \supseteq A$ with $Q \subseteq P$ is $\binom{n-k}{m-k}$. Hence $|\mathcal{X}| = \mathrm{conv}_k(P) \cdot \binom{n-k}{m-k}$.

Combining: $\mathrm{conv}_k(P) \ge \frac{\binom{n}{m}}{\binom{n-k}{m-k}} = \frac{\binom{n}{k}}{\binom{m}{k}}$, where the last equality is the identity $\binom{n}{m}\binom{m}{k} = \binom{n}{k}\binom{n-k}{m-k}$. $\square$

### Corollary (Lower bound)

$$f(n) \ge 2^{(\frac{1}{4} - o(1))(\log_2 n)^2}.$$

**Proof.** We use Suk's asymptotic refinement of the Erdős–Szekeres bound: $ES(k) = 2^{k + \varepsilon_k \cdot k}$ where $\varepsilon_k \to 0$ as $k \to \infty$ (specifically, $ES(k) \le 2^{k+O(k^{2/3} \log k)}$, following from Suk (2017)).

Set $L := \log_2 n$ and $k := \lfloor L/2 \rfloor$, so $k = (\frac{1}{2} + o(1))L$. For large $n$:
$$\log_2 ES(k) = k + \varepsilon_k k = (\tfrac{1}{2} + o(1))L < L,$$
so $ES(k) \le n$ and the Proposition applies. Using $g(P) \ge \mathrm{conv}_k(P)$:

$$f(n) \ge \frac{\binom{n}{k}}{\binom{ES(k)}{k}} \ge \left(\frac{n - k + 1}{ES(k)}\right)^k.$$

Taking $\log_2$:
$$\log_2 f(n) \ge k\bigl(\log_2(n-k+1) - \log_2 ES(k)\bigr).$$

Since $k = O(\log n) = o(n)$, we have $\log_2(n-k+1) = L + o(1)$. Also $\log_2 ES(k) = k + \varepsilon_k k$. Therefore:
$$\log_2 f(n) \ge k(L - k - \varepsilon_k k + o(1)) = kL - k^2 - \varepsilon_k k^2 + o(L).$$

With $k = (\frac{1}{2} + o(1))L$:
- $kL - k^2 = \frac{1}{4}L^2 + O(L)$,
- $\varepsilon_k k^2 = o(L^2)$.

Hence $\log_2 f(n) \ge \frac{1}{4}L^2 - o(L^2)$, i.e., $f(n) \ge 2^{(\frac{1}{4} - o(1))L^2}$.

This is optimal for the averaging method: the main term $kL - k^2 = (\alpha - \alpha^2)L^2$ for $k = \alpha L$ is maximized at $\alpha = \frac{1}{2}$. $\square$

---

## Part II: Upper bound — $f(n) \le 2^{L^2 + O(L)}$

### Construction: the recursively separated family

**Definition.** Let $P_1 = \{(0,0), (1,0)\}$. For $m \ge 2$, define
$$P_m = L_m \sqcup R_m, \quad L_m := \Phi_L(P_{m-1}),\quad R_m := \Phi_R(P_{m-1}),$$
where $\Phi_L(x,y) = (x/10 - 4, y/100 + 2)$ and $\Phi_R(x,y) = (x/10 + 5, y/100 - 2)$.

Then $|P_m| = 2^m$ for all $m \ge 1$.

### Bounding boxes

**Lemma 1.** For every $m \ge 1$,
$$P_m \subseteq B := \Bigl[-\tfrac{40}{9}, \tfrac{50}{9}\Bigr] \times \Bigl[-\tfrac{200}{99}, \tfrac{200}{99}\Bigr].$$
Moreover, $L_m \subseteq B_L := [-40/9, -31/9] \times [196/99, 200/99]$ and $R_m \subseteq B_R := [41/9, 50/9] \times [-200/99, -196/99]$.

**Proof.** By induction on $m$. For $m = 1$, $P_1 = \{(0,0),(1,0)\} \subseteq B$. For $m \ge 2$, $\Phi_L$ maps the $x$-range $[-40/9, 50/9]$ to $[(-40/9)/10 - 4, (50/9)/10 - 4] = [-40/9 \cdot 1/10 - 4, 50/90 - 4]$. Computing: $(-40/9)/10 = -4/9$, so $-4/9 - 4 = -40/9$. And $(50/9)/10 = 5/9$, so $5/9 - 4 = -31/9$. Similarly, $\Phi_L$ maps the $y$-range $[-200/99, 200/99]$ to $[-200/9900 + 2, 200/9900 + 2] = [-2/99 + 2, 2/99 + 2] = [196/99, 200/99]$.

For $\Phi_R$: the $x$-range maps to $[-4/9 + 5, 5/9 + 5] = [41/9, 50/9]$, and the $y$-range maps to $[-2/99 - 2, 2/99 - 2] = [-200/99, -196/99]$.

Their union lies in $B$. $\square$

In particular, the $x$-intervals of $L_m$ and $R_m$ are disjoint ($-31/9 < 41/9$), so every point of $L_m$ lies strictly to the left of every point of $R_m$.

### Slope control

**Lemma 2.** Every secant of $P_m$ has slope of absolute value at most $50/99$. Every secant contained entirely in one child $L_m$ or $R_m$ has slope of absolute value at most $5/99$.

**Proof.** By induction. For $m = 1$, the only secant has slope $0$. For $m \ge 2$:

*Same-child secants:* $\Phi_L$ and $\Phi_R$ multiply $x$-differences by $1/10$ and $y$-differences by $1/100$, so they multiply slopes by $1/10$. Hence same-child secant slopes have absolute value at most $(1/10)(50/99) = 5/99$.

*Cross-child secants:* By Lemma 1, the vertical difference is at most $200/99 - (-200/99) = 400/99$, and the horizontal difference is at least $41/9 - (-31/9) = 72/9 = 8$. So the absolute slope is at most $(400/99)/8 = 50/99$. $\square$

### Separation property

**Lemma 3.** For every $m \ge 2$, every point of $L_m$ lies strictly above every secant line of $R_m$, and every point of $R_m$ lies strictly below every secant line of $L_m$.

**Proof.** Consider a secant line $\ell$ of $R_m$. By Lemma 2, its slope $s$ satisfies $|s| \le 5/99$. Take any point $(u,v) \in R_m$ on $\ell$. By Lemma 1, $u \in [41/9, 50/9]$ and $v \le -196/99$. For any $x \in [-40/9, -31/9]$ (the $x$-range of $L_m$), we have $|x - u| \le 50/9 + 40/9 = 10$, so
$$\ell(x) = v + s(x - u) \le -196/99 + (5/99)(10) = -196/99 + 50/99 = -146/99.$$
Since every point of $L_m$ has $y \ge 196/99 > -146/99$, every point of $L_m$ lies strictly above $\ell$.

Symmetrically, for a secant $\ell$ of $L_m$: any point $(u,v) \in L_m$ on $\ell$ has $v \ge 196/99$, and for $x \in [41/9, 50/9]$,
$$\ell(x) = v + s(x-u) \ge 196/99 - (5/99)(10) = 146/99.$$
Since every point of $R_m$ has $y \le -196/99 < 146/99$, every point of $R_m$ lies strictly below $\ell$. $\square$

### General position

**Lemma 4.** Every $P_m$ is in general position, and all $x$-coordinates in $P_m$ are distinct.

**Proof.** Distinctness of $x$-coordinates: by induction, $\Phi_L$ and $\Phi_R$ preserve distinct $x$-coordinates, and the $x$-ranges of $L_m$ and $R_m$ are disjoint.

For general position: $P_1$ is trivially in general position. Assume $P_{m-1}$ is in general position. Since affine maps preserve collinearity, no three points within one child are collinear. If three points are collinear with two in one child and one in the other, then by Lemma 3, the secant line through the two same-child points lies strictly above (or below) the other child, so the third point cannot be on it. Contradiction. $\square$

### Cups and caps

Since all $x$-coordinates are distinct, every subset inherits a unique left-to-right order. A sequence $p_1, \ldots, p_r$ with strictly increasing $x$-coordinates is an **$r$-cup** if the consecutive slopes are strictly increasing:
$$\mathrm{slope}(p_1,p_2) < \cdots < \mathrm{slope}(p_{r-1},p_r).$$
It is an **$r$-cap** if the consecutive slopes are strictly decreasing.

Key criterion: for $x_1 < x_2 < x_3$, $\mathrm{slope}(p_1,p_2) < \mathrm{slope}(p_2,p_3)$ iff $p_2$ lies strictly below the line $p_1p_3$, and $\mathrm{slope}(p_1,p_2) > \mathrm{slope}(p_2,p_3)$ iff $p_2$ lies strictly above it.

Hence for a convex set with vertices ordered by $x$: the **upper hull = cap** (decreasing slopes) and the **lower hull = cup** (increasing slopes).

Let $Q_+(r,P)$, $Q_-(r,P)$ denote the numbers of $r$-cups and $r$-caps in $P$, and $Q(r,P) := \max(Q_+(r,P), Q_-(r,P))$.

### Chain-pair inequality

**Lemma 5.** For every $k \ge 3$,
$$C_k(P_m) \le \sum_{a=2}^{k} Q_-(a, P_m) \cdot Q_+(k+2-a, P_m) \le \sum_{a=2}^{k} Q(a, P_m) \cdot Q(k+2-a, P_m).$$

**Proof.** Let $A \subseteq P_m$ be a convex $k$-subset. It has unique leftmost and rightmost points. The upper hull $U$ (from leftmost to rightmost) is an $a$-cap, and the lower hull $W$ is a $(k+2-a)$-cup, where $a = |U|$, $b = |W| = k+2-a$, and $U \cap W$ consists of the two extreme points. The map $A \mapsto (U, W)$ is injective. Forgetting the endpoint-matching constraint only enlarges the count:
$$C_k(P_m) \le \sum_{a=2}^{k} Q_-(a, P_m) \cdot Q_+(k+2-a, P_m). \quad \square$$

### Cup/cap recursion

**Lemma 6.** For every $r \ge 3$ and $m \ge 2$,
$$Q_+(r,P_m) \le 2Q_+(r,P_{m-1}) + 2^{m-1}Q_+(r-1,P_{m-1}),$$
$$Q_-(r,P_m) \le 2Q_-(r,P_{m-1}) + 2^{m-1}Q_-(r-1,P_{m-1}),$$
and consequently $Q(r,P_m) \le 2Q(r,P_{m-1}) + 2^{m-1}Q(r-1,P_{m-1})$.

**Proof.** We prove the cup recursion; caps are symmetric.

Let $p_1, \ldots, p_r$ be an $r$-cup in $P_m$ in increasing $x$-order. Since $L_m$ is to the left of $R_m$, there exists $t \in \{0,1,\ldots,r\}$ with $p_1,\ldots,p_t \in L_m$ and $p_{t+1},\ldots,p_r \in R_m$.

If $t = 0$ or $t = r$: the cup lies in one child, contributing $\le 2Q_+(r, P_{m-1})$ total.

If $1 \le t \le r-1$: we claim $t = 1$. Suppose $t \ge 2$. Then $p_{t-1}, p_t \in L_m$ and $p_{t+1} \in R_m$. By Lemma 3, the secant line through $p_{t-1}, p_t$ (a secant of $L_m$) lies strictly above every point of $R_m$, so $p_{t+1}$ lies strictly below this line. By the criterion, this means $\mathrm{slope}(p_{t-1}, p_t) > \mathrm{slope}(p_t, p_{t+1})$, contradicting the cup condition. So $t = 1$.

Every mixed $r$-cup thus consists of one point of $L_m$ followed by an $(r-1)$-cup in $R_m$. The count is at most $|L_m| \cdot Q_+(r-1, R_m) = 2^{m-1} Q_+(r-1, P_{m-1})$.

For caps: if both children occur and $r - t \ge 2$, then $p_t \in L_m$ and $p_{t+1}, p_{t+2} \in R_m$. The secant of $R_m$ through $p_{t+1}, p_{t+2}$ lies strictly below $p_t$ (by Lemma 3), so $\mathrm{slope}(p_t, p_{t+1}) < \mathrm{slope}(p_{t+1}, p_{t+2})$, contradicting the cap condition. Hence $r - t = 1$: every mixed cap has $(r-1)$ points in $L_m$ and one point in $R_m$. $\square$

### Solving the recursion

**Lemma 7.** Define $d_2 = 1$ and $d_r = d_{r-1}/(2^r - 2)$ for $r \ge 3$. Then for all $r \ge 2$ and $m \ge 1$:
$$Q(r, P_m) \le d_r \cdot 2^{rm}.$$

**Proof.** By induction on $r$ and $m$. For $r = 2$: $Q(2, P_m) = \binom{2^m}{2} \le 2^{2m} = d_2 \cdot 2^{2m}$.

Fix $r \ge 3$, assume the bound for $r-1$. For $m = 1$: $|P_1| = 2 < r$, so $Q(r, P_1) = 0$. For $m \ge 2$, by Lemma 6:
$$Q(r, P_m) \le 2 d_r 2^{r(m-1)} + 2^{m-1} d_{r-1} 2^{(r-1)(m-1)} = 2^{rm-r}(2d_r + d_{r-1}).$$
Since $d_{r-1} = (2^r - 2)d_r$, we get $2d_r + d_{r-1} = 2^r d_r$, so $Q(r, P_m) \le d_r \cdot 2^{rm}$. $\square$

### Explicit bound on $d_r$

Iterating: $d_r = \prod_{j=3}^{r} \frac{1}{2^j - 2}$.

Since $2^j - 2 \ge 2^{j-1}$ for $j \ge 2$:
$$d_r \le \prod_{j=3}^{r} 2^{-(j-1)} = 2^{-\sum_{i=2}^{r-1} i} = 2^{1 - r(r-1)/2}.$$

### Bounding $C_k(P_m)$

**Lemma 8.** For every $k \ge 3$,
$$C_k(P_m) \le (k-1) \cdot 2^{(k+2)m - k(k+2)/4 + 2}.$$

**Proof.** By Lemmas 5 and 7:
$$C_k(P_m) \le \sum_{a=2}^{k} d_a d_{k+2-a} \cdot 2^{(k+2)m}.$$
With $b = k+2-a$ and the bound $d_r \le 2^{1 - r(r-1)/2}$:
$$d_a d_b \le 2^{2 - (a(a-1) + b(b-1))/2}.$$

Since $a + b = k+2$:
$$a(a-1) + b(b-1) = a^2 + b^2 - (k+2) = (a+b)^2 - 2ab - (a+b) \ge \frac{(k+2)^2}{2} - (k+2) = \frac{k(k+2)}{2},$$
using $ab \le (a+b)^2/4$.

Therefore $d_a d_b \le 2^{2 - k(k+2)/4}$. Summing over $k-1$ values of $a$:
$$C_k(P_m) \le (k-1) \cdot 2^{(k+2)m - k(k+2)/4 + 2}. \quad \square$$

### Summing over $k$

Set $\psi(k) := (k+2)m - k(k+2)/4$. Completing the square:
$$\psi(k) = m^2 + m + \frac{1}{4} - \frac{(k - 2m + 1)^2}{4}.$$
Maximum at $k = 2m-1$: $\psi(2m-1) = m^2 + m + 1/4$.

For $k = 0,1,2$: $C_0 + C_1 + C_2 \le 1 + 2^m + 2^{2m-1} \le 2^{2m+1}$.

For $k \ge 3$, writing $\delta = k - 2m + 1$:
$$\sum_{k \ge 3} C_k(P_m) \le 4 \cdot 2^{m^2 + m + 1/4} \sum_{\delta \in \mathbb{Z}} (2m + |\delta|) \cdot 2^{-\delta^2/4}.$$
The series $\sum_{\delta} 2^{-\delta^2/4}$ and $\sum_{\delta} |\delta| 2^{-\delta^2/4}$ converge, so the sum is $O(m)$.

Therefore:
$$g(P_m) \le 2^{m^2 + m + O(\log m)} \le 2^{m^2 + O(m)}.$$

### Extension to arbitrary $n$

For $n \ge 2$, set $M = \lceil \log_2 n \rceil$. Then $|P_M| = 2^M \ge n$. Any $n$-point subset $S \subseteq P_M$ is in general position, and $g(S) \le g(P_M) \le 2^{M^2 + O(M)}$. Since $M = L + O(1)$:
$$f(n) \le 2^{L^2 + O(L)}.$$

---

## Part III: Conclusion

Combining Parts I and II with $L = \log_2 n$:

$$2^{(\frac{1}{4} - o(1))L^2} \le f(n) \le 2^{L^2 + O(L)}.$$

Equivalently:
$$\frac{1}{4} \le \liminf_{n\to\infty} \frac{\log_2 f(n)}{(\log_2 n)^2} \le \limsup_{n\to\infty} \frac{\log_2 f(n)}{(\log_2 n)^2} \le 1.$$

So $\log_2 f(n) = \Theta((\log_2 n)^2)$, and if the limit $c = \lim \frac{\log f(n)}{(\log n)^2}$ exists, then $c$ is a positive finite constant satisfying $\frac{1}{4} \le c \le 1$ (in base-2 logarithms), or equivalently $\frac{1}{4\ln 2} \le c \le \frac{1}{\ln 2}$ (in natural logarithms).

The lower bound $1/4$ is sharp for any averaging argument using only the Erdős–Szekeres threshold. The upper bound coefficient $1$ is sharp for the class of binary separated recursions. Closing the gap requires either a non-averaging lower-bound technique or a fundamentally different construction.
