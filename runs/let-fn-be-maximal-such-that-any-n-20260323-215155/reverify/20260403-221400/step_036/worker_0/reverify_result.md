## Verification

### 1. Definition and Growth Law
The base cases $N_1 = \cdots = N_t = 1$ and recurrence $N_m = N_{m-1} + N_{m-t}$ are correct. The characteristic polynomial $p_t(x) = x^t - x^{t-1} - 1$ is right: since $p_t(1) = -1 < 0$ and $p_t(x) \to \infty$, a unique positive root $\lambda_t > 1$ exists. ✓

### 2. Exact Recurrences
The cup/cap/convex-subset recurrences are the standard separated-union decompositions. The spanning terms have the correct asymmetry: cups gain a point from the right child ($N_{m-t} \cdot U_{m-1}(a-1)$), caps gain a point from the left child ($N_{m-1} \cdot V_{m-t}(a-1)$). ✓

### 3. Maximal Cups
Claim: $\nu_m = m - t + 1$ for $m \ge t$. The key step is $\nu_{m-1} \ge \nu_{m-t}$. For $m \ge t+1$: $\nu_{m-1} = m - t$ while $\nu_{m-t} \le m - 2t + 1$ (or $1$), so the inequality holds for $t \ge 2$. At the maximal level, $U_{m-1}(\nu_m) = 0$ and $U_{m-t}(\nu_m) = 0$, confirming $U_m^* = N_{m-t} \cdot U_{m-1}^*$, hence $U_m^* = \prod_{j=1}^{m-t} N_j$. ✓

### 4. Maximal Caps
Claim: $v_m = 1 + \lfloor(m-1)/t\rfloor$. Verified by induction through the recurrence $v_m = \max(v_{m-1}, 1 + v_{m-t})$. Spot-checked for $t=2$ and $t=3$. ✓

At $m = qt+1$: $v_{qt} = q$ and $v_{(q-1)t+1} = q$, so both non-spanning cap terms vanish at level $q+1$, giving $W_q = N_{qt} \cdot W_{q-1}$ exactly. ✓

### 5. Obstruction Term
At $m_q = (q+1)t + 1$: the single spanning term with $a = qt+1$, $k - a = q + 1$ yields

$$C_{m_q}(q(t+1)+2) \ge U_{(q+1)t}^* \cdot W_q = \prod_{j=1}^{qt} N_j \cdot \prod_{i=1}^q N_{it}.$$

Summing logs: $\sum_{j=1}^{qt} j + t\sum_{i=1}^q i = \frac{t(t+1)}{2}q^2 + O_t(q)$. With $m_q = tq + O_t(1)$, this gives $\frac{(t+1)\log_2\lambda_t}{2t} m_q^2 + O_t(m_q)$. Converting to $\log_2 N_{m_q}$:

$$\alpha_t = \frac{t+1}{2t\log_2\lambda_t}. \quad \checkmark$$

### 6. Verifying $\alpha_t > 1$

- **$t=2$:** $\varphi^4 = 3\varphi + 2 \approx 6.854 < 8$, so $\log_2\varphi < 3/4$. ✓
- **$t=3$:** $p_3(3/2) = 1/8 > 0$ and $(3/2)^3 = 3.375 < 4$, so $\log_2\lambda_3 < 2/3$. ✓
- **$t\ge 4$:** $p_t(\sqrt{2}) = 2^{(t-1)/2}(\sqrt{2}-1) - 1 \ge 2^{3/2}(\sqrt{2}-1) - 1 = 3 - 2\sqrt{2} > 0$, so $\log_2\lambda_t < 1/2 < \frac{t+1}{2t}$. ✓

All cases give $\alpha_t > 1$. ✓

### 7. Task Completion
All five deliverables are present. The work treats the family as one parameterized class, distinguishes exact identities from inequalities, avoids endpoint refinements, and avoids literature/Lean. The conclusion is clear: the entire fixed-lag family is obstructed.

VERDICT: CORRECT