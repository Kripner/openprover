The core argument is sound.

The double count
$$
\sum_{|Q|=m} g(Q)=\sum_{t=1}^m \binom{n-t}{m-t}\,\mathrm{conv}_t(P)
$$
is correct, hence
$$
\sum_{t=1}^m \frac{\binom{m}{t}}{\binom{n}{t}}\,\mathrm{conv}_t(P)\ge f(m)
$$
is the right weighted inequality. Rewriting with
$$
y_t:=\frac{\mathrm{conv}_t(P)}{\binom{n}{t}}\in[0,1]
$$
gives the natural linear program for the best lower bound this mechanism alone can certify. The monotonicity
$$
\frac{\binom{m}{t+1}/\binom{n}{t+1}}{\binom{m}{t}/\binom{n}{t}}=\frac{m-t}{n-t}\le 1
$$
shows the optimal relaxed strategy is to fill small $t$ first, so it is enough to bound the least $r$ with $\sum_{t\le r}\binom{m}{t}\ge F(m)$.

The estimate with $s=\lceil (\frac14+\varepsilon)\log_2 m\rceil$ is also correct:
$$
\log_2 \binom{m}{s}\ge s(\log_2 m-\log_2 s)=\left(\frac14+\varepsilon\right)(\log_2 m)^2-O((\log m)\log\log m),
$$
so for large $m$, one has $F(m)\le \binom{m}{s}$ and thus $r\le s$. Then
$$
\sum_{t\le r}\binom{n}{t}\le r\,n^r
$$
gives an extractable lower bound of size at most
$$
2^{(\frac14+\varepsilon)\log_2 m\,\log_2 n+o((\log n)^2)}
\le
2^{(\frac14+\varepsilon+o(1))(\log_2 n)^2}.
$$
So this subset-bootstrapping mechanism does not beat quadratic constant $\frac14$.

The only fix needed is wording: the note should not write $\log_2 f(n)\le \cdots$, which reads as an upper bound on the true $f(n)$. What is proved is that any lower bound obtainable from this mechanism, using only the current input $f(m)\ge 2^{(\frac14-o(1))(\log_2 m)^2}$, cannot exceed that scale.

VERDICT: NEEDS MINOR FIXES - conflates the true $f(n)$ with the best lower bound certifiable by this mechanism