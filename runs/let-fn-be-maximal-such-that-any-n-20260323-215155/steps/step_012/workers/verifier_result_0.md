The main argument checks out: the recurrence solves to $Q_\pm(r,P_m)\le d_r\,2^{rm}$ with the stated $d_r$, the convex $k$-set to lower/upper chain injection is correct, the estimate
$$
C_k(P_m)\le (k-1)\,2^{(k+2)m-\lfloor (k+1)^2/4\rfloor}
$$
follows, and the Gaussian-type summation gives $g(P_m)\le 2^{m^2+m+O(\log m)}$, hence $\alpha=1$. The subset monotonicity argument for $f(n)$ is also valid if $f(n)=\min_{|P|=n} g(P)$.

The only point I would not call fully proof-tight as written is the normalization sentence. One cannot simply assert one small generic rotation works for *all* $P_m$ simultaneously without justification. It should be phrased for each fixed target level $m$ (or each finite initial segment up to $m$), where only finitely many strict inequalities need to be preserved. With that clarification, the note is sound.

VERDICT: NEEDS MINOR FIXES - generic-rotation normalization should be stated per finite level, not globally for all $m$ at once