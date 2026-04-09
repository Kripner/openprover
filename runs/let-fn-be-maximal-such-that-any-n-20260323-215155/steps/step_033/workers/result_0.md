I derived the negative endpoint-matched refinement. I could not write the file because local tool execution is failing in this session (`bwrap: Unknown option --argv0`), so below is repo-ready markdown for [attempts/endpoint-matched-recursive-family-no-gain.md](/home/josh/projects/openprover/runs/let-fn-be-maximal-such-that-any-n-20260323-215155/attempts/endpoint-matched-recursive-family-no-gain.md).

```markdown
Summary: Keeping the outer endpoints $(\ell,r)$ fixed does admit an exact recursive classification inside the present family, but the closed state is not just the first split level where $\ell$ and $r$ separate. The exact state is the separation level together with the left-turn scales of $\ell$ and the right-turn scales of $r$. This yields exact fixed-endpoint recurrences and explicit weighted-subset formulas. After summing over matched endpoint pairs, however, the optimization still gives only $2^{m^2+O(m)}$ for $|P_m|=2^m$, so endpoint matching does not improve the coefficient $1$ of $(\log_2 n)^2$ in this recursive family.

# Endpoint-Matched Refinement for the Recursive Family

Let $P_1$ be a two-point set, and for $m\ge 2$ let
$$
P_m=L_m\sqcup R_m
$$
with $L_m,R_m$ affine copies of $P_{m-1}$ in the standard recursively separated position.

The point of [[status/recursive-family-information-loss]] is that the first genuine loss in [[bounds/upper-bound-recursive-family]] occurs when one forgets that the upper and lower hull chains of a convex subset have the same outer endpoints $(\ell,r)$. The question is whether keeping $(\ell,r)$ through the recursion gives a genuinely sharper bound.

Inside this recursive family, the answer is negative at the $(\log n)^2$ scale.

## 1. Natural endpoint-matched state

For an ordered pair $\ell<r$ in $P_m$, let $s=s(\ell,r)$ be the unique integer such that $\ell,r$ lie in a common copy $B\cong P_s$, they lie in different children of the top split of $B$, and no smaller recursive copy has this property. Thus $s(\ell,r)$ is the first recursive scale at which the endpoints separate.

This parameter alone is not closed under the exact recursion. Once $B=L\sqcup R$ is the minimal block where $\ell$ and $r$ separate, the exact fixed-endpoint count depends on how much cup-growth is available below $\ell$ inside $L$ and how much cap-growth is available below $r$ inside $R$.

For a point $x\in P_d$, define
$$
\mathcal L_d(x)\subseteq\{1,\dots,d\}
$$
to be the set of recursive scales $j$ such that, in the unique nested copy of $P_j$ containing $x$, the point $x$ lies in the left child, and define $\mathcal R_d(x)$ dually for the right child.

Now define
$$
U_d(a;x):=\sum_y \widetilde Q_+(a,P_d;x,y),
\qquad
V_d(b;x):=\sum_y \widetilde Q_-(b,P_d;y,x),
$$
with $\widetilde Q_\pm$ as in [[lemmas/one-split-fixed-state-recurrence]]. Concretely:

1. $U_d(1;x)=1$, and for $a\ge 2$, $U_d(a;x)$ is the number of $a$-cups in $P_d$ whose left endpoint is $x$.
2. $V_d(1;x)=1$, and for $b\ge 2$, $V_d(b;x)$ is the number of $b$-caps in $P_d$ whose right endpoint is $x$.

For a pair $(\ell,r)$ with $s(\ell,r)=s$, let $\ell^-\in P_{s-1}$ be the point corresponding to $\ell$ inside the left child of the minimal block, and let $r^+\in P_{s-1}$ be the corresponding point inside the right child. The natural closed recursive state is
$$
\Sigma(\ell,r):=\bigl(s(\ell,r),\mathcal L_{s-1}(\ell^-),\mathcal R_{s-1}(r^+)\bigr).
$$

So the first-separation level is not enough; the exact state is the separation level together with the endpoint signatures below that split.

## 2. Exact one-sided recurrences

Fix $d\ge 2$ and $x\in P_d$, and let $x'\in P_{d-1}$ be the corresponding point in the relevant child copy.

These identities are exact:

If $x\in L_d$, then for every $a\ge 1$,
$$
U_d(a;x)=U_{d-1}(a;x')+2^{d-1}U_{d-1}(a-1;x').
$$
If $x\in R_d$, then
$$
U_d(a;x)=U_{d-1}(a;x').
$$

Dually, if $x\in R_d$, then for every $b\ge 1$,
$$
V_d(b;x)=V_{d-1}(b;x')+2^{d-1}V_{d-1}(b-1;x'),
$$
and if $x\in L_d$, then
$$
V_d(b;x)=V_{d-1}(b;x').
$$

Proof: if $x\in L_d$, an $a$-cup with left endpoint $x$ is either contained in $L_d$ or crosses the top split. By [[lemmas/one-split-crossing-cup-cap-identities]], a crossing cup has exactly one point in $R_d$, namely its global right endpoint. For each $r\in R_d$, the exact crossing identity gives a bijection between spanning $a$-cups with endpoints $(x,r)$ and $(a-1)$-cups in $L_d$ with left endpoint $x$. Since $|R_d|=2^{d-1}$, the spanning contribution is exactly $2^{d-1}U_{d-1}(a-1;x')$. The other formulas are dual.

## 3. Exact closed forms

Iterating the previous recurrences gives exact formulas:
$$
U_d(a;x)=\sum_{\substack{J\subseteq \mathcal L_d(x)\\ |J|=a-1}} 2^{\sum_{j\in J}(j-1)},
$$
$$
V_d(b;x)=\sum_{\substack{J\subseteq \mathcal R_d(x)\\ |J|=b-1}} 2^{\sum_{j\in J}(j-1)}.
$$

These are exact identities.

Interpretation: to build a cup from a fixed left endpoint $x$, one chooses the recursive scales at which the construction jumps from the current left branch to a right child; each chosen scale $j$ contributes a factor $2^{j-1}$. The cap formula is the right-end dual.

## 4. Exact fixed-endpoint recurrence for convex subsets

Fix $\ell<r$ in $P_m$, and let $s=s(\ell,r)$. Let
$$
E_k(\ell,r)
$$
be the number of convex $k$-subsets of $P_m$ whose leftmost point is $\ell$ and whose rightmost point is $r$.

Since every point between $\ell$ and $r$ lies in the minimal block $B\cong P_s$, every such subset is contained in $B$. Since $\ell$ and $r$ lie in opposite sides of the top split of $B$, every such subset is spanning with respect to that split. Therefore, by the exact state-sum identity from [[lemmas/one-split-fixed-state-recurrence]],
$$
E_k(\ell,r)=\sum_{a=1}^{k-1} U_{s-1}(a;\ell^-)\,V_{s-1}(k-a;r^+).
$$
This is an exact identity.

Combining with the exact closed forms gives
$$
E_k(\ell,r)=\sum_{a=1}^{k-1}
\left(
\sum_{\substack{J\subseteq \mathcal L_{s-1}(\ell^-)\\ |J|=a-1}}
2^{\sum_{j\in J}(j-1)}
\right)
\left(
\sum_{\substack{I\subseteq \mathcal R_{s-1}(r^+)\\ |I|=k-a-1}}
2^{\sum_{i\in I}(i-1)}
\right).
$$
So the fixed-endpoint count depends only on the refined state $\Sigma(\ell,r)$.

## 5. Usable upper bounds

From the exact closed forms, the largest possible value of $\sum_{j\in J}(j-1)$ over all $(a-1)$-subsets of $\{1,\dots,d\}$ is
$$
(d-1)+(d-2)+\cdots+(d-a+1)=(a-1)d-\binom{a}{2}.
$$
Hence
$$
U_d(a;x)\le \binom{d}{a-1}\,2^{(a-1)d-\binom{a}{2}},
$$
and similarly
$$
V_d(b;x)\le \binom{d}{b-1}\,2^{(b-1)d-\binom{b}{2}}.
$$
These are inequalities.

Insert these into the exact fixed-endpoint formula with $d=s-1$. For every pair $(\ell,r)$ with $s(\ell,r)=s$,
$$
E_k(\ell,r)
\le
\sum_{a=1}^{k-1}
\binom{s-1}{a-1}\binom{s-1}{k-a-1}
2^{(a-1)(s-1)-\binom{a}{2}}
2^{(k-a-1)(s-1)-\binom{k-a}{2}}.
$$
Therefore
$$
E_k(\ell,r)\le
2^{(k-2)(s-1)-\min_{1\le a\le k-1}\left(\binom{a}{2}+\binom{k-a}{2}\right)+O(s)}.
$$
The minimum occurs when $a$ and $k-a$ are as balanced as possible, and equals
$$
\left\lfloor\frac{(k-1)^2}{4}\right\rfloor.
$$
So
$$
E_k(\ell,r)\le
2^{(k-2)(s-1)-\lfloor (k-1)^2/4\rfloor+O(s)}.
$$

Now count endpoint pairs. The number of pairs in $P_m$ with first separation scale exactly $s$ is
$$
N_{m,s}=2^{m-s}\cdot 2^{s-1}\cdot 2^{s-1}=2^{m+s-2},
$$
because there are $2^{m-s}$ copies of $P_s$, and inside each copy one may choose $\ell$ arbitrarily in the left child and $r$ arbitrarily in the right child.

Hence the contribution of scale $s$ to $C_k(P_m)$ satisfies
$$
C_{k,s}(P_m)\le
2^{m+s-2}\,
2^{(k-2)(s-1)-\lfloor (k-1)^2/4\rfloor+O(s)}.
$$
Equivalently,
$$
C_{k,s}(P_m)\le
2^{m+(k-1)s-\lfloor (k-1)^2/4\rfloor+O(s)}.
$$
This is maximized at the largest scale, namely $s=m$, so
$$
C_k(P_m)\le 2^{km-\lfloor (k-1)^2/4\rfloor+O(m)}.
$$

Optimizing in $k$ still gives
$$
g(P_m)=\sum_k C_k(P_m)\le 2^{m^2+O(m)}.
$$
Since $|P_m|=2^m$, this is
$$
g(P_m)\le 2^{(\log_2 |P_m|)^2+O(\log |P_m|)}.
$$

## 6. Obstruction and conclusion

The endpoint condition can be restored exactly, but inside this recursive family it changes only lower-order bookkeeping:

1. Fixing $(\ell,r)$ removes the false independence between the upper and lower hull chains.
2. The exact fixed-endpoint count still factors into a left-end quantity $U$ and a right-end quantity $V$, and each of these already has exponential growth across many recursive scales.
3. There are still $2^{m+s-2}$ matched endpoint pairs at separation scale $s$.
4. The dominant contribution still comes from the top scale $s=m$.

So the endpoint-forgetting step in [[bounds/upper-bound-recursive-family]] is real, but correcting it does not change the leading quadratic exponent inside this family. Endpoint matching removes only lower-order overcounting; it does not reduce the top-scale supply of admissible endpoint states and one-sided chain growth enough to beat coefficient $1$ at the $(\log_2 n)^2$ scale.
```