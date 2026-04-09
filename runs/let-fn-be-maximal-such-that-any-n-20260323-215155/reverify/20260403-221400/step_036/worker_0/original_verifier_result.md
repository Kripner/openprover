The mathematical argument checks out. The stated exact recurrences are the natural ones for a separated union: spanning $a$-cups come from an $(a-1)$-cup on the left plus one right point, spanning $a$-caps are dual, and spanning convex $k$-subsets split into a left cup and a right cap. From these, the extrema
$$
\nu_m=m-t+1,\qquad v_m=1+\left\lfloor \frac{m-1}{t}\right\rfloor
$$
are correct, and the exact product formulas
$$
U_m^*=\prod_{j=1}^{m-t}N_j,\qquad W_q=\prod_{i=1}^q N_{it}
$$
follow.

The chosen top split at $m_q=(q+1)t+1$ is also correct:
$$
C_{m_q}\bigl(q(t+1)+2\bigr)\ge U_{(q+1)t}^*\,W_q.
$$
Using $N_m=\Theta_t(\lambda_t^m)$ with $\lambda_t>1$ defined by $\lambda_t^t=\lambda_t^{t-1}+1$, this gives
$$
\limsup_{m\to\infty}\frac{\log_2 g(F_m^{(t)})}{(\log_2 N_m)^2}\ge \alpha_t,
\qquad
\alpha_t=\frac{t+1}{2t\log_2\lambda_t}.
$$
The proof that $\alpha_t>1$ for every fixed $t\ge2$ is valid: the $t=2,3$ checks are correct, and for $t\ge4$, $p_t(\sqrt2)>0$ implies $\lambda_t<\sqrt2$, hence $\log_2\lambda_t<\tfrac12$ and so $\alpha_t>\tfrac{t+1}{t}>1$. So the conclusion that the whole fixed-lag family is obstructed is justified. The only thing not completed was writing the markdown to disk, which is an operational issue rather than a flaw in the mathematics.

VERDICT: CORRECT