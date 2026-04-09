The chosen convention $P_1$ as a two-point set is otherwise coherent, and the core upper-bound argument looks correct: the levelwise normalization statement, the cup/cap recurrence, the chain-pair injection, the finite-level estimate, the optimization giving $m^2+m$, and the endpoint-matching objection to the discarded $\alpha=2$ claim are all fine.

Two minor consistency issues remain.

1. In the arbitrary-$n$ step, taking
$$
M=\lceil \log_2 n\rceil
$$
is not fully compatible with a theory that starts at $P_1$, because for $n=1$ this gives $M=0$ and $P_0$ is undefined. One should either state $n\ge 2$ there, or replace $M$ by $\max(1,\lceil \log_2 n\rceil)$.

2. The displayed summation
$$
g(P_m)\le \sum_{k\ge 1}(k-1)\,2^{(k+2)m-\lfloor (k+1)^2/4\rfloor}
$$
does not follow as written, since the chain-pair bound only applies for $k\ge 2$, and in the given definitions $C_1(P_m)=2^m$. So the $k=1$ term must be handled separately, or the sum should begin at $k\ge 2$. Relatedly, the inductive step invoking $d_{r-1}$ should be stated for $r\ge 3$, since $d_1$ is not defined.

VERDICT: NEEDS MINOR FIXES - the $n=1$ truncation and the $k=1$/base-step bookkeeping are still inconsistent.