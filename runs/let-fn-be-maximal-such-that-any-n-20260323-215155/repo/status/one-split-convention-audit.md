Summary: The stored fixed-state note and the stored crossing note use opposite local cup/cap assignments. Using the displayed hull-chain formulas from [[lemmas/one-split-structure-spanning-convex-subsets]], the canonical assignment is left cup and right cap. Hence the fixed-state note is consistent, while the crossing note is mathematically wrong as written. The structure note also has its concluding cup/cap labels reversed and should be corrected at the same time.

## Exact stored formulas and conventions

From [[lemmas/one-split-fixed-state-recurrence]], the displayed local counts are
$$
\widetilde Q_+(a,L;\ell,\lambda):=
\begin{cases}
1,& a=1\text{ and }\ell=\lambda,\\
Q_+(a,L;\ell,\lambda),& a\ge 2\text{ and }\ell<\lambda,\\
0,&\text{otherwise,}
\end{cases}
$$
and
$$
\widetilde Q_-(b,R;\rho,r):=
\begin{cases}
1,& b=1\text{ and }\rho=r,\\
Q_-(b,R;\rho,r),& b\ge 2\text{ and }\rho<r,\\
0,&\text{otherwise.}
\end{cases}
$$
Its proposition is the exact identity
$$
C^\times(a,b,P;\ell,\lambda,\rho,r)
=
\widetilde Q_+(a,L;\ell,\lambda)\,\widetilde Q_-(b,R;\rho,r).
$$
The note states explicitly: the local quantities are a left cup count and a right cap count.

From [[lemmas/one-split-crossing-cup-cap-identities]], the displayed crossing identities are
$$
Q_+^\times(t+1,P;\ell,r)=\sum_{\rho\in R,\ \rho<r} Q_+(t,R;\rho,r),
$$
and
$$
Q_-^\times(t+1,P;\ell,r)=\sum_{\lambda\in L,\ \ell<\lambda} Q_-(t,L;\ell,\lambda).
$$
Its proof states that
$$
S\cap L\text{ is a cap with endpoints }(\ell,\lambda),\qquad
S\cap R\text{ is a cup with endpoints }(\rho,r).
$$

## Canonical assignment from the structure note

Use only the displayed hull formulas from [[lemmas/one-split-structure-spanning-convex-subsets]]:
$$
U(S)=\ell,u_1,\dots,u_t,\qquad D(S)=v_1,\dots,v_s,r.
$$
With the fixed convention
$$
Q_+:\text{ consecutive slopes strictly increasing},\qquad
Q_-:\text{ consecutive slopes strictly decreasing},
$$
the lower chain gives a cup and the upper chain gives a cap. Therefore these displayed formulas force
$$
S\cap L\text{ to be a cup with endpoints }(\ell,\lambda),
$$
and
$$
S\cap R\text{ to be a cap with endpoints }(\rho,r).
$$

## Decision

This is a genuine mathematical error, not only a notation mismatch. Once $Q_+$ and $Q_-$ are fixed by slope monotonicity, the crossing note's local side/type assignment and its two exact counting identities are reversed.

The correct exact identities are
$$
Q_+^\times(t+1,P;\ell,r)=\sum_{\lambda\in L,\ \ell<\lambda} Q_+(t,L;\ell,\lambda),
$$
and
$$
Q_-^\times(t+1,P;\ell,r)=\sum_{\rho\in R,\ \rho<r} Q_-(t,R;\rho,r).
$$
Equivalently:
- every spanning cup has exactly one right point, namely $r$;
- every spanning cap has exactly one left point, namely $\ell$.

## Items to change

1. Replace [[lemmas/one-split-crossing-cup-cap-identities]].
2. Replace [[lemmas/one-split-structure-spanning-convex-subsets]] so its concluding labels match its displayed hull formulas.
3. Leave [[lemmas/one-split-fixed-state-recurrence]] unchanged.