## Verification

### Box Bounds

I verify the child box formulas. For instance, $L_n = \Phi_L(T_{n-1})$ has $x$-range:
$$\left[-4 - \tfrac{4}{9}(1-10^{-(n-1)}),\; -4 + \tfrac{5}{9}(1-10^{-(n-1)})\right] = \left[-\tfrac{40}{9}+\tfrac{4}{9}\cdot 10^{-(n-1)},\; -\tfrac{31}{9}-\tfrac{5}{9}\cdot 10^{-(n-1)}\right]$$
Matches. Spot-checking $n=1$: $L_1=\{(-4,2)\}$ and $I_L(1)=[-4,-4]$, $J_L(1)=[2,2]$. ✓

The universal envelopes $\bar{I}_\cdot, \bar{J}_\cdot$ contain the exact boxes for all $n\ge 1$ since the correction terms $\tfrac{4}{9}\cdot 10^{-(n-1)}\ge 0$ only shrink them inward. ✓

### Gap Verification

The children are $x$-separated:
- Gap $L$–$M$: $-4/9 - (-31/9) = 27/9 = 3 > 0$. ✓
- Gap $M$–$R$: $41/9 - 5/9 = 36/9 = 4 > 0$. ✓

### Separated-Position Inequalities

**Part 1 (Left-child secants).** For $(x_0,y_0)\in L_n$ and $x\in \bar{I}_M\cup\bar{I}_R$: $x\ge -4/9 > -31/9 \ge x_0$, so $x-x_0>0$. Then:
$$s(x) \ge y_0 - \sigma(x-x_0) \ge \tfrac{196}{99} - \tfrac{40}{297}\cdot 10 = \tfrac{588-400}{297} = \tfrac{188}{297}$$
Compare: every $M_n$ point has $y\le \tfrac{2}{99}=\tfrac{6}{297}$. Since $188>6$: ✓. Every $R_n$ point has $y<0<\tfrac{188}{297}$: ✓.

**Part 2a (Middle vs. Left).** For $(x_0,y_0)\in M_n$, $x\in\bar{I}_L$: $x\le -31/9 < -4/9 \le x_0$, so $x_0-x>0$. Then:
$$s(x) \le y_0 + \sigma(x_0-x) \le \tfrac{2}{99} + \tfrac{40}{297}\cdot 5 = \tfrac{6+200}{297} = \tfrac{206}{297}$$
Compare: every $L_n$ point has $y\ge \tfrac{196}{99}=\tfrac{588}{297}$. Since $206<588$: ✓.

**Part 2b (Middle vs. Right).** For $x\in\bar{I}_R$: $x\ge 41/9 > 5/9\ge x_0$, so $x-x_0>0$. Then:
$$s(x) \ge -\tfrac{2}{99} - \tfrac{40}{297}\cdot 6 = \tfrac{-6-240}{297} = -\tfrac{246}{297} = -\tfrac{82}{99}$$
Compare: every $R_n$ point has $y\le -\tfrac{196}{99}$. Since $-82>-196$: ✓.

**Part 3 (Right-child secants).** For $(x_0,y_0)\in R_n$, $x\in\bar{I}_L\cup\bar{I}_M$: $x\le 5/9 < 41/9 \le x_0$. Then:
$$s(x) \le -\tfrac{196}{99} + \tfrac{40}{297}\cdot 10 = \tfrac{-588+400}{297} = -\tfrac{188}{297}$$
Compare: every $M_n$ point has $y\ge -\tfrac{2}{99}=-\tfrac{6}{297}$. Since $-188<-6$: ✓. Every $L_n$ point has $y>0>-\tfrac{188}{297}$: ✓.

All six comparisons hold with explicit numerical slack. The quantifiers are now correctly one-sided (each child's secants are compared only on the opposite-side $x$-range). ✓

### Bridge Maps and Obstruction

Verified:
$$\Phi_M^{-1}\Phi_L(x) = (10(x_1/10-4),\,100(x_2/100+2)) = x + (-40,200) \;\checkmark$$
$$\alpha_1 = \Phi_M^{-1}\alpha_0\Phi_M:\; x\mapsto (10(x_1/10-40),\,100(x_2/100+200))= x+(-400,20000) \;\checkmark$$

Since $(-400,20000)\neq(-40,200)$ and no nontrivial affine symmetry exists, $\alpha_1\neq\alpha_0$ in the orbit, confirming non-closure. ✓

### Completeness Check

The note includes: box bounds, secant slope bound, one-sided comparisons for all three child types, bridge conjugation computation, and obstruction conclusion with appropriate hedging ("obstruction only to the currently tracked bridge state"). All requested deliverables are present.

VERDICT: CORRECT