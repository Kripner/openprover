## Verification

### Checking the hull claim in Part (1)

The worker states: *"Suppose $S$ is itself a cup. Then its lower hull has only the two global endpoints $\ell, r$."*

This is **false**. A cup has strictly increasing consecutive slopes, meaning all its points lie on a convex curve. For such a curve, every point lies *below* the chord from the first to last point. Therefore:

- **Lower hull of a cup = all points** (they are all "low")
- **Upper hull of a cup = just the two endpoints** $\{\ell, r\}$

Concrete check: the cup $(-1,1),\,(0,0),\,(1,1)$ (slopes $-1 < 1$) has lower hull $\{(-1,1),(0,0),(1,1)\}$ and upper hull $\{(-1,1),(1,1)\}$. The worker's claim holds for **caps**, not cups.

### Checking the slope inequality in surjectivity

The worker claims: *"$\ell$ below line through $u_1, u_2$ is equivalent to $\operatorname{slope}(\ell, u_1) < \operatorname{slope}(u_1, u_2)$."*

Direct computation with $x_\ell < x_{u_1} < x_{u_2}$:

$$y_\ell < y_{u_1} + m_{12}(x_\ell - x_{u_1}) \;\;\Longrightarrow\;\; \frac{y_\ell - y_{u_1}}{x_\ell - x_{u_1}} > m_{12}$$

(inequality flips because $x_\ell - x_{u_1} < 0$), giving $\operatorname{slope}(\ell, u_1) > \operatorname{slope}(u_1, u_2)$. The worker has the inequality **reversed**.

Numerical check: $\ell=(0,-100)$, $u_1=(3,10)$, $u_2=(4,14)$ satisfies the one-split hypotheses. $\operatorname{slope}(\ell,u_1) = 110/3 \approx 36.7$, $\operatorname{slope}(u_1,u_2) = 4$. Indeed $36.7 > 4$.

### Consequences: the conclusions are swapped

Using the **correct** hull correspondence:

- **Cup** $S$: upper hull $= \{\ell, r\}$. Comparing with $U(S) = \ell, u_1, \dots, u_t$ from the split lemma gives $t=1$, hence $S \cap R = \{r\}$.

- **Cap** $S$: lower hull $= \{\ell, r\}$. Comparing with $D(S) = v_1, \dots, v_s, r$ gives $s=1$, hence $S \cap L = \{\ell\}$.

The worker states the **opposite**: cups have $S\cap L = \{\ell\}$ and caps have $S\cap R = \{r\}$. Verified by example: the spanning 3-cup $\{(0,-100),(1,-99),(4,14)\}$ has **two** points in $L$ and **one** in $R$.

### The counting identities are for the wrong halves

The correct identities should be:
$$Q_+^\times(t{+}1, P; \ell, r) = \sum_{\substack{\lambda \in L \\ \ell < \lambda}} Q_+(t, L; \ell, \lambda), \qquad Q_-^\times(t{+}1, P; \ell, r) = \sum_{\substack{\rho \in R \\ \rho < r}} Q_-(t, R; \rho, r).$$

The worker writes the cup identity summing over $R$ and the cap identity summing over $L$—exactly transposed.

### Note on the split lemma description

The worker describes the split lemma as giving "$S\cap L$ = cap, $S\cap R$ = cup." Under the stated one-split hypotheses ($L$ low, $R$ high), $L$-points sit on the lower hull (cup structure) and $R$-points on the upper hull (cap structure). So the split lemma likely states $S \cap L$ is a **cup** and $S \cap R$ is a **cap**, opposite to what the worker writes. This further propagates the cup/cap confusion throughout.

VERDICT: CRITICALLY FLAWED - Lower/upper hull of cups vs caps is inverted, slope inequality direction is reversed, and consequently the singleton-half conclusions and counting identities have L and R swapped.