Query: Horton set recursive Erdos-Szekeres construction number of convex k-gons convex subsets density 2^{-k^2} upper bound

Context: We already have a verified lower bound
\[
f(n)\ge 2^{(\frac14-o(1))(\log_2 n)^2}
\]
for the minimum number of convex subsets in an n-point planar set in general position.

The next task is the upper bound: find an explicit construction and a quantitative count of its convex subsets.

Please search specifically for results on recursive Erdős-Szekeres constructions, Horton sets, or order-type limits that bound the number/density of convex k-subsets (or convex k-gons) by something like \(2^{-\Theta(k^2)}\), and identify statements strong enough to convert into an upper bound on the total number of convex subsets of an n-point set.

What I need from the search:
1. Concrete constructions, not just existence statements.
2. Explicit asymptotic bounds on the number or density of convex k-subsets in those constructions.
3. Any statement precise enough to sum over k and derive an upper bound of the form
\[
2^{(\alpha+o(1))(\log_2 n)^2}.
\]
4. If possible, identify the best constant \(\alpha\) supported by the literature or by a clean conversion of the cited result.

Please emphasize exact statements and how they would feed into the total-count upper bound problem.