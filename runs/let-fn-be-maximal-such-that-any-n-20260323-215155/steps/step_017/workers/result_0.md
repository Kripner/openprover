**Status**

I did not find a paper that settles the total-count problem \(f(n)\) asymptotically. The best evidence I found is:

- Erdős’s 1978 note introduced essentially this function \(s(r)\): the minimum number of convex subsets of a planar \(r\)-point set in general position. As reported in the Morris–Soltan survey, Erdős proved
  \[
  r^{a\log r}<s(r)<r^{b\log r}
  \]
  for some constants \(a,b>0\), and explicitly asked whether
  \[
  \lim_{r\to\infty}\frac{\log s(r)}{(\log r)^2}
  \]
  exists. I found no later paper resolving that limit question.  
  Sources: Morris–Soltan survey, §5.1; original reference is Erdős 1978.  
  https://www.ams.org/bull/2000-37-04/S0273-0979-00-00877-6/  
  https://www.erdosproblems.com/838

- I found no published improvement specifically for the global exponent bracket
  \[
  \tfrac14 \le \liminf \frac{\log_2 f(n)}{(\log_2 n)^2}
  \le \limsup \frac{\log_2 f(n)}{(\log_2 n)^2}\le 1
  \]
  and no exact asymptotic \(f(n)=2^{(c+o(1))(\log_2 n)^2}\).

**What the literature does give**

- Bárány–Valtr (1998), positive-fraction Erdős–Szekeres: for every fixed \(k\) there is \(c_k>0\) such that every sufficiently large planar point set contains subsets \(Y_1,\dots,Y_k\), each of size at least \(c_k n\), with every transversal \(\{y_1,\dots,y_k\}\) in convex position. Hence, for fixed \(k\), the minimum number of convex \(k\)-gons is \(\Omega(n^k)\).  
  https://doi.org/10.1007/PL00009350

- Pór–Valtr (2002), partitioned version: strengthens the positive-fraction viewpoint. A later paper states an explicit consequence:
  every \(n\)-point set contains a convex \(k\)-clustering \(C_1,\dots,C_k\) with
  \[
  |C_i|\ge 2^{-32k}n.
  \]
  This yields, by optimization over \(k\), the older literature-based lower bound
  \[
  \log_2 f(n)\ge \left(\tfrac{1}{128}-o(1)\right)(\log_2 n)^2.
  \]
  The last inequality is an inference from the clustering theorem.  
  Sources: Pór–Valtr 2002; explicit bound quoted in Aichholzer et al. 2014, Thm. 6.  
  https://doi.org/10.1007/S00454-002-2894-1  
  https://www.sciencedirect.com/science/article/pii/S0925772114000534

- Suk (2017) proved
  \[
  ES(k)=2^{k+o(k)}.
  \]
  By the standard averaging/double-counting argument, this implies
  \[
  \log_2 f(n)\ge \left(\tfrac14-o(1)\right)(\log_2 n)^2.
  \]
  This is an inference from Suk’s theorem, not a theorem stated there about \(f(n)\).  
  https://www.ams.org/jams/2017-30-04/S0894-0347-2016-00869-X/

**Nearby terminology / related papers**

- Fixed-\(k\) version: “minimum number of convex \(k\)-gons in an \(n\)-point set.” Morris–Soltan list this as Problem 5.1 and cite Bárány–Valtr for the positive-fraction result.  
  https://www.ams.org/bull/2000-37-04/S0273-0979-00-00877-6/

- “Convexly independent subsets” is standard synonymous language.

- “Islands” is related but slightly different: a convex \(k\)-gon with \(\ell\) interior points corresponds to an island of size \(k+\ell\). For terminology and identities involving \(X_{k,\ell}\), see Huemer–Oliveros–Pérez-Lantero–Torra–Vogtenhuber (2022).  
  https://link.springer.com/article/10.1007/s00454-022-00395-8

**Bottom line**

- No exact asymptotic for total \(f(n)\) found.
- No improvement found for the total-count constants beyond the current \([1/4,1]\) bracket.
- No theorem found proving or disproving existence of \(\lim \log f(n)/(\log n)^2\).
- The main relevant literature is still: Erdős 1978; Bárány–Valtr 1998; Pór–Valtr 2002; Suk 2017.

I found strong nearby results on fixed-\(k\) convex polygons and positive-fraction/partitioned Erdős–Szekeres theorems, but no primary source resolving the total-count problem itself.