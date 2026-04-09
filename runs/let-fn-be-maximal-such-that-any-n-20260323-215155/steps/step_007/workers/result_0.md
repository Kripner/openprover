**Main Takeaway**

I did not find a paper that explicitly studies  
`f(n) = min_P #{A ⊆ P : A in convex position}`  
or the limit of `log f(n)/(\log n)^2`. But the literature already gives the right order of growth:

`log f(n) = Θ((log n)^2)`.

The open part seems to be the constant in front, not the `(\log n)^2` scale.

**What is known**

- For each fixed `k`, let `conv_k(n)` be the minimum number of convex `k`-subsets in an `n`-point set in general position. Then `conv_4(n)=\overline{cr}(n)=Θ(n^4)`, and for every fixed `k≥5`, `conv_k(n)=Θ(n^k)`. A good summary source is Aichholzer et al., *On k-gons and k-holes in point sets*:
  https://upcommons.upc.edu/entities/publication/03ad3b9a-dd7d-431f-94c0-281d7948afe5

- Goaoc–Hubard–de Joannis de Verclos–Sereni–Volec, *Limits of Order Types*, study the minimum densities  
  `c_k = lim conv_k(n)/binom(n,k)`  
  and prove by flag algebras that `c_5 ≥ 0.0608516` and `c_6 ≥ 0.0018311`; they also discuss recursive Erdős-Szekeres/Horton-type limits where convex-`k` densities decay like `2^{-Θ(k^2)}`:
  https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.SOCG.2015.300

- Most relevant for your question: by double counting, for every `k`,
  `conv_k(n) ≥ binom(n,k) / binom(ES(k),k)`,
  where `ES(k)` is the Erdős-Szekeres number.
  This is an inference from the Erdős-Szekeres theorem.

- Combining that with Suk’s bound `ES(k)=2^{k+o(k)}` gives
  `conv_k(n) ≥ 2^{k log_2 n - k^2 - o(k^2)}`
  for suitable `k`, hence
  `log_2 f(n) ≥ (1/4 - o(1)) (log_2 n)^2`.
  Source for the modern `ES(k)` bound:
  https://doi.org/10.1090/jams/869

- The upper-bound direction is classical from Erdős-Szekeres extremal constructions: there are `n`-point sets with no convex subset larger than `(1+o(1)) log_2 n`, so
  `f(n) ≤ Σ_{j≤(1+o(1))log_2 n} binom(n,j) = 2^{(1+o(1)) (log_2 n)^2}`.
  So `Θ((log n)^2)` is already forced on both sides.

- Goaoc et al. go further: their recursive ES/Horton-type limit `ℓ_H` has convex-`k` density `≤ 2^{-Θ(k^2)}` (more precisely, their cup/cap argument gives about `2^{-k^2/8+O(k log k)}` for `k` points in convex position). This is the closest thing I found to literature directly supporting the “correct constant” program.

**Useful techniques / papers**

- Flag algebras and order-type limits for fixed-`k` densities:
  https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.SOCG.2015.300

- Continuous-motion / alternating-sum identities for counts `X_{k,ℓ}` of convex `k`-gons with `ℓ` interior points:
  https://link.springer.com/article/10.1007/s00454-022-00395-8

- Earlier identities for empty convex polygons:
  https://doi.org/10.1016/j.jcta.2005.03.007

- Fixed-`k` extremal counting summary:
  https://upcommons.upc.edu/entities/publication/03ad3b9a-dd7d-431f-94c0-281d7948afe5

**Bottom line**

- I found no paper explicitly on the limit  
  `lim log f(n)/(\log n)^2`.
- But existing literature already implies
  `f(n)=2^{Θ((\log n)^2)}`.
- The most relevant existing machinery for the constant appears to be:
  Erdős-Szekeres averaging for lower bounds, and recursive ES/Horton-type constructions plus order-type limits/flag algebras for upper bounds and density heuristics.