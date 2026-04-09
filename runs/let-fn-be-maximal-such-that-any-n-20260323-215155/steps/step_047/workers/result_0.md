Let
\[
T_k(n):=\frac{\binom{n}{k}}{\binom{ES(k)}{k}},\qquad
S(n):=\sum_{k:\,ES(k)\le n} T_k(n),
\qquad L:=\log_2 n.
\]

The summed refinement does **not** improve the quadratic constant. One has
\[
\log_2 S(n)=\left(\frac14+o(1)\right)L^2.
\]
Hence the multi-\(k\) averaging bound gives
\[
f(n)\ge S(n)=2^{(\frac14+o(1))(\log_2 n)^2},
\]
with the same leading constant \(1/4\) as the single optimized \(k\)-term.

## Proof

For every \(n\)-point set \(P\),
\[
g(P)=\sum_{j\ge 0}\mathrm{conv}_j(P),
\]
so summing the verified bound from the averaging argument over all admissible \(k\) gives
\[
g(P)\ge \sum_{k:\,ES(k)\le n}\frac{\binom{n}{k}}{\binom{ES(k)}{k}}=S(n).
\]
Therefore \(f(n)\ge S(n)\).

So it remains to determine the size of \(S(n)\).

### Lower bound

Take
\[
k:=\left\lfloor \frac L2\right\rfloor.
\]
Using \(ES(k)=2^{k+o(k)}\), we have \(ES(k)\le n\) for all large \(n\), so this \(k\) is admissible. Then
\[
T_k(n)
=\prod_{i=0}^{k-1}\frac{n-i}{ES(k)-i}
\ge \left(\frac{n-k+1}{ES(k)}\right)^k.
\]
Hence
\[
\log_2 T_k(n)
\ge k\bigl(\log_2(n-k+1)-\log_2 ES(k)\bigr).
\]
Now \(k=O(L)=o(n)\), so \(\log_2(n-k+1)=L+o(1)\), while
\[
\log_2 ES(k)=k+o(k).
\]
Therefore
\[
\log_2 T_k(n)\ge k(L-k-o(k))
=\frac14L^2-o(L^2).
\]
Since \(S(n)\ge T_k(n)\),
\[
\log_2 S(n)\ge \frac14L^2-o(L^2).
\]

### Upper bound

To upper-bound the sum, use the standard Erdős-Szekeres lower bound
\[
ES(k)\ge 2^{k-2}+1.
\]
If \(ES(k)\le n\), then \(2^{k-2}<n\), so
\[
k\le L+2.
\]
Thus there are only \(O(L)\) admissible values of \(k\).

Also, for any admissible \(k\ge 3\),
\[
T_k(n)
=\prod_{i=0}^{k-1}\frac{n-i}{ES(k)-i}
\le \left(\frac{n}{ES(k)-k+1}\right)^k.
\]
Using \(ES(k)\ge 2^{k-2}+1\),
\[
ES(k)-k+1\ge 2^{k-2}-k+2\ge 2^{k-3}
\qquad (k\ge 3),
\]
so
\[
T_k(n)\le \left(\frac{n}{2^{k-3}}\right)^k
=2^{kL-k^2+3k}.
\]
Rewrite the quadratic part as
\[
kL-k^2=\frac14L^2-\left(k-\frac L2\right)^2.
\]
Hence
\[
\log_2 T_k(n)\le \frac14L^2-\left(k-\frac L2\right)^2+3k
\le \frac14L^2-\left(k-\frac L2\right)^2+O(L),
\]
uniformly for admissible \(k\).

Summing over admissible \(k\),
\[
S(n)\le \sum_{k\le L+2}2^{\frac14L^2-(k-L/2)^2+O(L)}
\le 2^{\frac14L^2+O(L)}\sum_{k\in\mathbb Z}2^{-(k-L/2)^2}.
\]
The last series is bounded by an absolute constant, so
\[
\log_2 S(n)\le \frac14L^2+O(L).
\]
Therefore
\[
\log_2 S(n)\le \left(\frac14+o(1)\right)L^2.
\]

Combining with the lower bound,
\[
\log_2 S(n)=\left(\frac14+o(1)\right)L^2.
\]

## Window interpretation

This also gives the clean “maximizing window” statement.

For any fixed \(\eta>0\), if \(|k-L/2|\ge \eta L\), then
\[
\log_2 T_k(n)\le \left(\frac14-\eta^2\right)L^2+O(L),
\]
so the total contribution of all such \(k\) is
\[
\le 2^{(\frac14-\eta^2)L^2+O(L)}.
\]
Thus all \(k\) outside any fixed linear window around \(L/2\) are exponentially smaller at the quadratic scale.

Inside the central window \(|k-L/2|<\eta L\), there are only \(O(L)\) summands, and in fact the bound above shows a discrete Gaussian decay. So even summing the whole central window changes \(\log_2\) only by \(O(L)\), hence only by \(o(L^2)\).

## Conclusion

The natural summed refinement
\[
S(n)=\sum_{k:\,ES(k)\le n}\frac{\binom{n}{k}}{\binom{ES(k)}{k}}
\]
has the same quadratic-scale growth as the best single term:
\[
\log_2 S(n)=\left(\frac14+o(1)\right)(\log_2 n)^2.
\]
So multi-\(k\) aggregation of the verified averaging lower bound does **not** raise the leading constant above \(1/4\).