The core argument is correct. Counting
$$
\mathcal X=\{(A,Q): A\subseteq Q\subseteq P,\ |A|=k,\ |Q|=m,\ A\text{ convex}\}
$$
first by $Q$ and then by $A$ gives
$$
\sum_{|Q|=m}\mathrm{conv}_k(Q)=\binom{n-k}{m-k}\,\mathrm{conv}_k(P),
$$
hence
$$
\mathrm{conv}_k(P)\ge h(m,k)\frac{\binom{n}{m}}{\binom{n-k}{m-k}}
= h(m,k)\frac{\binom{n}{k}}{\binom{m}{k}}.
$$
Applying the same inequality to an $m$-point set with witness size $ES(k)$ and using $h(ES(k),k)\ge 1$ yields
$$
h(m,k)\ge \frac{\binom{m}{k}}{\binom{ES(k)}{k}},
$$
so substitution cancels the $\binom{m}{k}$ factor and recovers exactly the original pure-averaging bound. Thus, with only the Erdős-Szekeres threshold input, larger witness size $m$ does not improve the fixed-$k$ bound; any improvement would need a genuinely stronger universal lower bound on $h(m,k)$.

The asymptotic conclusion is also sound: the lower side still comes from $ES(k)=2^{k+o(k)}$, while the barrier side comes from $ES(k)\ge 2^{k-2}+1$, so optimizing in $k$ still yields quadratic coefficient $1/4$. The only issue I see is editorial: the purportedly self-contained markdown ends with $\log_2 f(n)\ge \cdots$ without defining $f(n)$ inside the note.

VERDICT: NEEDS MINOR FIXES - undefined notation $f(n)$ in the self-contained markdown