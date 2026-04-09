## Verification

### 1. Structural Lemma (Hull Chains → Cup/Cap Types)

The key fact is that the upper hull $U(S)$ has **decreasing** consecutive slopes (concavity), while the lower hull $D(S)$ has **increasing** consecutive slopes (convexity). Given:
$$U(S) = \ell, u_1, \dots, u_t, \qquad D(S) = v_1, \dots, v_s, r,$$
the sub-chain $u_1, \dots, u_t \subseteq R$ inherits decreasing slopes → **cap**. The sub-chain $v_1, \dots, v_s \subseteq L$ inherits increasing slopes → **cup**. So:

- $S \cap L$ is a **cup** $(\ell, \lambda)$ ✓  
- $S \cap R$ is a **cap** $(\rho, r)$ ✓  

The worker's canonical assignment (left cup, right cap) is correct.

### 2. The Original Error Diagnosis

The original crossing note claimed $S \cap L$ is a cap and $S \cap R$ is a cup — the exact reverse. With $Q_+/Q_-$ locked to increasing/decreasing slopes respectively, this isn't a label swap: it produces formulas summing over the **wrong side**. The worker correctly identifies this as a genuine mathematical error. ✓

### 3. Corrected Crossing Identities

**Cups:** A cup has $U(S) = \{\ell, r\}$. Comparing with $U(S) = \ell, u_1, \dots, u_t$ forces $t=1$, so $S \cap R = \{r\}$. The bijection $S \mapsto S \cap L$ gives:
$$Q_+^\times(t{+}1, P; \ell, r) = \sum_{\substack{\lambda \in L \\ \ell < \lambda}} Q_+(t, L; \ell, \lambda). \quad \checkmark$$

**Caps:** A cap has $D(S) = \{\ell, r\}$. Comparing with $D(S) = v_1, \dots, v_s, r$ forces $s=1$, so $S \cap L = \{\ell\}$. The bijection $S \mapsto S \cap R$ gives:
$$Q_-^\times(t{+}1, P; \ell, r) = \sum_{\substack{\rho \in R \\ \rho < r}} Q_-(t, R; \rho, r). \quad \checkmark$$

### 4. Surjectivity (Junction Slope Inequalities)

- **Cup case:** For $T$ a $t$-cup in $L$ with rightmost pair $(v_{t-1}, v_t)$: since $v_{t-1}, v_t \in L$, condition (2) places $r$ strictly above line $v_{t-1}v_t$. With $x_{v_t} < x_r$, this gives $\operatorname{slope}(v_{t-1},v_t) < \operatorname{slope}(v_t, r)$, extending the cup. ✓  
- **Cap case:** For $T$ a $t$-cap in $R$ with leftmost pair $(u_1, u_2)$: since $u_1, u_2 \in R$, condition (3) places $\ell$ strictly below line $u_1 u_2$. With $x_\ell < x_{u_1}$, this gives $\operatorname{slope}(\ell, u_1) > \operatorname{slope}(u_1, u_2)$, extending the cap. ✓

### 5. Consistency with the Fixed-State Note

The fixed-state note uses $\widetilde Q_+(a, L; \ell, \lambda)$ (left cup) and $\widetilde Q_-(b, R; \rho, r)$ (right cap), which matches the corrected canonical assignment. No change needed. ✓

### 6. Task Completion

- Exact formulas extracted from both notes ✓  
- Clash classified (genuine error) ✓  
- Affected items identified (crossing note + structure note labels) ✓  
- Repo-ready replacements for all three slugs provided ✓  
- Scope limited to convention reconciliation only ✓

VERDICT: CORRECT