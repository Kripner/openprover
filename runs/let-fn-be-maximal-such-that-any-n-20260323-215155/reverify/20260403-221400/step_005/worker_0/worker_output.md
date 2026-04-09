Let  
\[
n=\binom{2k-2}{k-1},\qquad L:=\log_2 n.
\]

There are two separate issues here:

1. the asymptotic of the trivial upper bound
\[
\sum_{j=0}^k \binom{n}{j},
\]
assuming every convex subset has size at most \(k\);

2. the actual number of convex subsets in a specific Erdős-Szekeres construction.

These are not the same. In particular, the binomial-size Erdős-Szekeres construction is the extremal construction for avoiding a \((k+1)\)-cup and a \((k+1)\)-cap, not for avoiding \((k+1)\) points in convex position. So the constant \(1/2\) below is the constant for the counting upper bound, not for the actual convex-subset count of a genuine ES lower-bound construction.

**1. Asymptotics of \(k\) in terms of \(n\)**

Set \(m=k-1\). Then Stirling gives
\[
n=\binom{2m}{m}
=\frac{4^m}{\sqrt{\pi m}}\left(1+O\!\left(\frac1m\right)\right).
\]
Hence
\[
L=\log_2 n
=2m-\frac12\log_2(\pi m)+O\!\left(\frac1m\right)
=2k-\frac12\log_2 k+O(1).
\]
Therefore
\[
k=\frac12L+\frac14\log_2 L+O(1).
\]

**2. Upper bound \(\sum_{j=0}^k \binom{n}{j}\)**

Let
\[
S(n,k):=\sum_{j=0}^k \binom{n}{j}.
\]
Since \(k=o(n)\), for \(1\le j\le k\),
\[
\frac{\binom{n}{j-1}}{\binom{n}{j}}
=\frac{j}{n-j+1}
\le \frac{k}{n-k+1}=o(1),
\]
so the sum is dominated by its last term:
\[
S(n,k)=(1+o(1))\binom{n}{k}.
\]
Also \(k^2/n\to0\), so
\[
\binom{n}{k}=\frac{n^k}{k!}(1+o(1)).
\]
Thus
\[
\log_2 S(n,k)
= kL-\log_2(k!)+o(1).
\]
Using Stirling again,
\[
\log_2(k!)
= k\log_2 k-(\log_2 e)k+O(\log k),
\]
hence
\[
\log_2 S(n,k)
= kL-k\log_2 k+O(k).
\]
Substituting \(k=\frac12L+\frac14\log_2 L+O(1)\), one gets
\[
\log_2 S(n,k)
= \frac12L^2-\frac14L\log_2 L+O(L).
\]
So
\[
\sum_{j=0}^k \binom{n}{j}
=
2^{\,\frac12(\log_2 n)^2-\frac14(\log_2 n)\log_2\log_2 n+O(\log n)}.
\]
In particular,
\[
\frac{\log_2\!\left(\sum_{j=0}^k \binom{n}{j}\right)}{(\log_2 n)^2}\to \frac12.
\]

**3. What this does and does not say about the ES construction**

This does **not** prove that the Erdős-Szekeres construction has
\[
2^{(\frac12+o(1))(\log_2 n)^2}
\]
convex subsets.

The reason is that the premise is incorrect: the classical binomial-size construction controls cups and caps, not arbitrary convex subsets. A convex \(r\)-gon need not be an \(r\)-cup or an \(r\)-cap; its upper and lower hulls can both be nontrivial. So counting cups/caps does not determine the number of convex subsets, and the statement

\[
\frac{\log_2 f(n)}{(\log_2 n)^2}\to \frac12
\]

for “the ES construction” does not follow from the standard cups-caps extremal example.

So the rigorous conclusion is:

\[
\boxed{
\log_2\!\left(\sum_{j=0}^k \binom{n}{j}\right)
=
\frac12(\log_2 n)^2-\frac14(\log_2 n)\log_2\log_2 n+O(\log n)
}
\]
and therefore
\[
\boxed{
\frac{\log_2\!\left(\sum_{j=0}^k \binom{n}{j}\right)}{(\log_2 n)^2}\to \frac12.
}
\]

But this is an **upper bound calculation**, not the asymptotic number of convex subsets in an actual Erdős-Szekeres extremal construction for convex position.