Summary: The first fixed-state endpoint-refined recurrence draft failed because its main slope-chain argument had the inequalities reversed, so the claimed product formula was not proved.

Context: this concerns the attempted note after [[lemmas/one-split-crossing-cup-cap-identities]].

Claimed draft conclusion:
$$
C^\times(a,b,P;\ell,\lambda,\rho,r)
=
\widetilde Q_-(a,L;\ell,\lambda)\,\widetilde Q_+(b,R;\rho,r).
$$

Verified defects:
1. In the surjectivity argument, from “the line through $u_1,u_2$ lies strictly above $\ell$” the draft deduced
$$
\operatorname{slope}(\ell,u_1)<\operatorname{slope}(u_1,u_2),
$$
but verification says the inequality goes the other way. Dually, the cap-side inequality was also reversed.
2. Because of this, the proof did not establish that adjoining the left chain and right chain yields the claimed cup/cap structure, so the exact product formula was not proved.
3. The final sentence saying that after forgetting the state one has only upper bounds was unsupported; if fixed states partition the spanning convex subsets, that point needs separate justification.
4. There was also an edge-case gap when $a=1$ or $b=1$, because the argument invoked a secant such as $\ell\lambda$ or $\rho r$ when that secant is undefined.

Use this item to avoid repeating the same slope argument without first re-deriving the correct local orientation.
