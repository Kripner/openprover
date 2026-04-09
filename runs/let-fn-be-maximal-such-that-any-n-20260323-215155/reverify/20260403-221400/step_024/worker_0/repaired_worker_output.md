```md
---
slug: lemmas/one-split-crossing-cup-cap-identities
depends:
  - lemmas/one-split-structure-spanning-convex-subsets
  - bounds/upper-bound-recursive-family
---

Assume the hypotheses of [[lemmas/one-split-structure-spanning-convex-subsets]]:
$$
P = L \sqcup R,
$$
every point of $L$ lies to the left of every point of $R$, every line through two points of $L$ lies strictly below every point of $R$, and every line through two points of $R$ lies strictly above every point of $L$.

**Notation.** For $t \ge 2$ and points $a, b$ in a planar point set $X$ (with $a$ left of $b$), write $Q_+(t,X;a,b)$ for the number of $t$-cups in $X$ with left endpoint $a$ and right endpoint $b$ (i.e.\ $t$ points in left-to-right order whose consecutive slopes are strictly increasing), and $Q_-(t,X;a,b)$ for the number of $t$-caps (strictly decreasing consecutive slopes).

For $\ell \in L$, $r \in R$, and $t \ge 2$, write $Q_+^\times(t{+}1,P;\ell,r)$ for the number of spanning $(t{+}1)$-cups in $P$ with global endpoints $(\ell,r)$, and $Q_-^\times(t{+}1,P;\ell,r)$ for spanning $(t{+}1)$-caps.

**Proposition.** Under the one-split hypotheses, the following hold.

1. Every spanning cup $S \subseteq P$ with global endpoints $(\ell, r)$ satisfies
$$S \cap R = \{r\}.$$
That is, the only point of $S$ in the right half is its global right endpoint.

2. Every spanning cap $S \subseteq P$ with global endpoints $(\ell, r)$ satisfies
$$S \cap L = \{\ell\}.$$
That is, the only point of $S$ in the left half is its global left endpoint.

3. For every $\ell \in L$, $r \in R$, and $t \ge 2$:
$$
Q_+^\times(t{+}1, P; \ell, r) \;=\; \sum_{\substack{\lambda \in L \\[2pt] \ell < \lambda}} Q_+(t, L;\, \ell, \lambda),
$$
$$
Q_-^\times(t{+}1, P; \ell, r) \;=\; \sum_{\substack{\rho \in R \\[2pt] \rho < r}} Q_-(t, R;\, \rho, r).
$$

Here $<$ denotes the left-to-right $x$-order throughout.

No extra hypothesis beyond the stored one-split assumptions is needed.

**Proof.**

*Hull decomposition from the split lemma.* Let $S \subseteq P$ be a spanning convex subset. Set
$$
\ell = \min_x S,\quad r = \max_x S,\quad \lambda = \max_x(S \cap L),\quad \rho = \min_x(S \cap R).
$$
Write
$$
S \cap L = \{v_1 = \ell < v_2 < \cdots < v_s = \lambda\},\qquad
S \cap R = \{u_1 = \rho < u_2 < \cdots < u_t = r\}.
$$
By [[lemmas/one-split-structure-spanning-convex-subsets]], the lower and upper hulls of $S$ are
$$
D(S) = v_1, v_2, \ldots, v_s,\, r, \qquad U(S) = \ell,\, u_1, u_2, \ldots, u_t.
$$
Since $D(S)$ is a cup (strictly increasing consecutive slopes), its initial segment $v_1, \ldots, v_s$ inherits strictly increasing consecutive slopes, so $S \cap L$ is a **cup** with endpoints $(\ell, \lambda)$. Since $U(S)$ is a cap (strictly decreasing consecutive slopes), its terminal segment $u_1, \ldots, u_t$ inherits strictly decreasing consecutive slopes, so $S \cap R$ is a **cap** with endpoints $(\rho, r)$.

*Proof of (1).* Suppose $S$ is a spanning cup.  We show that the upper hull of any cup consists of just its two endpoints.  Let $p_1 < p_2 < \cdots < p_n$ be a cup with consecutive slopes $m_{i} := \operatorname{slope}(p_i, p_{i+1})$ satisfying $m_1 < m_2 < \cdots < m_{n-1}$.  For any interior index $1 < k < n$, the slope $\operatorname{slope}(p_1, p_k)$ is the weighted average
$$
\operatorname{slope}(p_1, p_k) \;=\; \frac{\sum_{i=1}^{k-1} m_i\,(x_{p_{i+1}} - x_{p_i})}{\sum_{i=1}^{k-1} (x_{p_{i+1}} - x_{p_i})},
$$
which is strictly less than $\operatorname{slope}(p_1, p_n)$ (the analogous average over all $m_1, \ldots, m_{n-1}$, with each $m_i$ for $i \ge k$ strictly larger).  Since $x_{p_k} - x_{p_1} > 0$, this gives
$$
y_{p_k} = y_{p_1} + \operatorname{slope}(p_1, p_k)\cdot(x_{p_k} - x_{p_1})
\;<\;
y_{p_1} + \operatorname{slope}(p_1, p_n)\cdot(x_{p_k} - x_{p_1}),
$$
so $p_k$ is strictly below the line $p_1 p_n$.  Hence $U(S) = \{\ell, r\}$.

Comparing with $U(S) = \ell,\, u_1, \ldots, u_t$ from the split lemma forces $t = 1$ and $u_1 = r$, giving
$$
S \cap R = \{r\}.\qquad\square_{(1)}
$$

*Proof of (2).* Dually, if $S$ is a spanning cap with consecutive slopes $m_1 > m_2 > \cdots > m_{n-1}$, the same weighted-average argument shows every interior point lies strictly *above* the line $\ell\, r$, so $D(S) = \{\ell, r\}$.

Comparing with $D(S) = v_1, \ldots, v_s,\, r$ forces $s = 1$ and $v_1 = \ell$, giving
$$
S \cap L = \{\ell\}.\qquad\square_{(2)}
$$

*Proof of (3): cup identity.* Fix $\ell \in L$, $r \in R$, $t \ge 2$.  Define $\Phi(S) = S \cap L$.  By (1), any spanning $(t{+}1)$-cup $S$ with endpoints $(\ell, r)$ has $S \cap R = \{r\}$, so $|S \cap L| = t$, and $\Phi(S)$ is a $t$-cup in $L$ with endpoints $(\ell, \lambda)$ for some $\lambda \in L$ with $\ell < \lambda$ (since $t \ge 2$).

*Injectivity:* $S = \Phi(S) \cup \{r\}$, so $\Phi$ determines $S$.

*Surjectivity:* Let
$$
T = \{v_1 = \ell < v_2 < \cdots < v_t = \lambda\} \subseteq L
$$
be a $t$-cup, and set $S = T \cup \{r\}$.  Since $T$ is a cup,
$$
\operatorname{slope}(v_1,v_2) < \operatorname{slope}(v_2,v_3) < \cdots < \operatorname{slope}(v_{t-1},v_t).
$$
Since $v_{t-1}, v_t \in L$ and $r \in R$, the one-split hypothesis gives that $r$ lies strictly above the line through $v_{t-1}$ and $v_t$.  Because $x_{v_{t-1}} < x_{v_t} < x_r$, this means
$$
y_r > y_{v_t} + \operatorname{slope}(v_{t-1},v_t)\cdot(x_r - x_{v_t}),
$$
and dividing by $x_r - x_{v_t} > 0$:
$$
\operatorname{slope}(v_t, r) > \operatorname{slope}(v_{t-1}, v_t).
$$
Hence the full slope sequence
$$
\operatorname{slope}(v_1,v_2) < \cdots < \operatorname{slope}(v_{t-1},v_t) < \operatorname{slope}(v_t, r)
$$
is strictly increasing, so $S = v_1, \ldots, v_t, r$ is a $(t{+}1)$-cup with endpoints $(\ell, r)$.  The case $t = 2$ is covered: one uses only $\operatorname{slope}(v_1, v_2) < \operatorname{slope}(v_2, r)$ via the same one-split inequality, with no separate treatment required.

Therefore $\Phi$ is bijective, giving
$$
Q_+^\times(t{+}1, P;\, \ell, r) = \sum_{\substack{\lambda \in L \\[2pt] \ell < \lambda}} Q_+(t, L;\, \ell, \lambda).
$$

*Proof of (3): cap identity (dual).* Define $\Psi(S) = S \cap R$.  By (2), any spanning $(t{+}1)$-cap with endpoints $(\ell, r)$ has $S \cap L = \{\ell\}$, so $|S \cap R| = t$, and $\Psi(S)$ is a $t$-cap in $R$ with endpoints $(\rho, r)$ for some $\rho \in R$ with $\rho < r$.

*Injectivity:* $S = \{\ell\} \cup \Psi(S)$.

*Surjectivity:* Let
$$
T = \{u_1 = \rho < u_2 < \cdots < u_t = r\} \subseteq R
$$
be a $t$-cap, and set $S = \{\ell\} \cup T$.  Since $T$ is a cap,
$$
\operatorname{slope}(u_1,u_2) > \operatorname{slope}(u_2,u_3) > \cdots > \operatorname{slope}(u_{t-1},u_t).
$$
Since $u_1, u_2 \in R$ and $\ell \in L$, the one-split hypothesis gives that $\ell$ lies strictly below the line through $u_1$ and $u_2$.  Because $x_\ell < x_{u_1} < x_{u_2}$:
$$
y_\ell < y_{u_1} + \operatorname{slope}(u_1, u_2)\cdot(x_\ell - x_{u_1}).
$$
Dividing by $x_\ell - x_{u_1} < 0$ reverses the inequality:
$$
\operatorname{slope}(\ell, u_1) > \operatorname{slope}(u_1, u_2).
$$
Hence
$$
\operatorname{slope}(\ell, u_1) > \operatorname{slope}(u_1, u_2) > \cdots > \operatorname{slope}(u_{t-1}, u_t),
$$
so $S = \ell, u_1, \ldots, u_t$ is a $(t{+}1)$-cap with endpoints $(\ell, r)$.  Again, $t = 2$ requires no separate argument.

Therefore $\Psi$ is bijective, giving
$$
Q_-^\times(t{+}1, P;\, \ell, r) = \sum_{\substack{\rho \in R \\[2pt] \rho < r}} Q_-(t, R;\, \rho, r).
$$

Endpoint matching is enforced because the global endpoints $(\ell, r)$ are fixed throughout, while the bijections $\Phi$ and $\Psi$ preserve the inner endpoint: $\lambda = \max_x(S \cap L)$ for cups and $\rho = \min_x(S \cap R)$ for caps. $\square$
```