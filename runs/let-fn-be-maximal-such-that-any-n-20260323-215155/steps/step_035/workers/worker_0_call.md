---
call_num: 5
label: worker_35_0
model: gpt-5.4
elapsed_ms: 306244
input_tokens: 99319
output_tokens: 16588
cache_read_tokens: 80768
stop_reason: completed
---

======== SYSTEM PROMPT ========

You are a research mathematician working on a specific task.

Think carefully before writing your answer. Explore the problem, consider edge cases, and work through the reasoning step by step before stating conclusions.

Complete the task thoroughly and report your findings. If you get stuck, return what you have so far - partial progress is valuable. Clearly state what you found, where you got stuck, and what remains open. The planner will decide whether to continue from your progress or try a different approach.

If asked to verify a proof: be rigorous. Check every step. Don't fill in gaps yourself. End your response with exactly one of:
VERDICT: CORRECT
VERDICT: INCORRECT

Write in concise mathematical style. Use $inline$ and $$display$$ LaTeX.

IMPORTANT: You are a single worker. Do NOT attempt to spawn subagents, delegate to other workers, or "launch agents in parallel". You do all the work yourself, directly in your response.


======== USER PROMPT ========

# Task

Use [[bounds/upper-bound-recursive-family]], [[status/recursive-family-information-loss]], and [[status/endpoint-matched-recursive-family]].

Work on exactly one task: propose and analyze one specific alternative sparse construction family that is not the current balanced recursively separated family, with the sole goal of seeing whether it can plausibly lower the coefficient $1$ in the upper bound.

Deliverable:
1. Choose one concrete family only.
   - Examples of acceptable directions: an unbalanced recursive split, a non-self-similar separated recursion, or another explicit geometric template.
   - Do not survey multiple families.
2. Define the family precisely enough that recursive counting can be attempted.
3. Derive the first nontrivial counting recurrence or structural decomposition for convex subsets in that family.
4. Decide one of:
   - the family immediately reproduces the same top-scale obstruction,
   - the family gives a genuinely different recurrence worth pursuing,
   - or the family is too ill-posed and should be discarded.
5. Output repo-ready markdown with a `Summary:` line.
   - If promising, use a slug like `attempts/alternative-construction-<short-name>`.
   - If it immediately fails, make the note a clean obstruction/diagnostic for that family.

Requirements:
- Stay constructive and focused on one family.
- Do not revisit endpoint-matching refinements inside the old balanced family.
- Do not use literature or Lean.
- Be explicit about exact identities versus inequalities.
- The note should make clear why this is the next fork after [[status/endpoint-matched-recursive-family]].



# Referenced Materials

## [[bounds/upper-bound-recursive-family]]

Summary: Verified upper bound via a recursively separated family showing $f(n)\le 2^{(\log_2 n)^2+O(\log n)}$.

Let $P_1$ be a two-point set, and for $m\ge 2$ let
$$
P_m=L_m\sqcup R_m
$$
where $L_m$ and $R_m$ are affine copies of $P_{m-1}$ in the standard recursively separated position. Thus
$$
|P_m|=2^m \qquad (m\ge 1).
$$

For each fixed $m$, we may first apply a sufficiently small generic rotation to $P_m$ so that all points of $P_m$ have distinct $x$-coordinates. This does not change the order type, hence does not change which subsets are in convex position. After this normalization, for $r\ge 2$ let $Q_+(r,P_m)$ and $Q_-(r,P_m)$ denote respectively the numbers of $r$-cups and $r$-caps in $P_m$. For $k\ge 1$, let $C_k(P_m)$ be the number of $k$-point subsets of $P_m$ in convex position, and set
$$
g(P_m):=\sum_{k=1}^{2^m} C_k(P_m).
$$

We first record the cup/cap bound.

**Lemma.** For each $r\ge 2$ there is a constant $d_r>0$ such that
$$
Q_\pm(r,P_m)\le d_r\,2^{rm}\qquad\text{for all }m\ge 1.
$$

**Proof.** The base case $r=2$ is explicit:
$$
Q_+(2,P_m)=Q_-(2,P_m)=\binom{2^m}{2}\le 2^{2m},
$$
so we may take $d_2=1$.

Now fix $r\ge 3$ and assume $d_{r-1}$ has already been chosen. For $m=1$ we have $Q_\pm(r,P_1)=0$, since $|P_1|=2<r$. For $m\ge 2$, every $r$-cup in $P_m$ is either contained entirely in $L_m$ or entirely in $R_m$, or else consists of one point from one side together with an $(r-1)$-cup from the other side; the same dichotomy holds for $r$-caps. Hence
$$
Q_\pm(r,P_m)\le 2\,Q_\pm(r,P_{m-1})+2^{m-1}Q_\pm(r-1,P_{m-1}).
$$
Choose $d_r$ so that
$$
(2^r-2)d_r\ge d_{r-1}.
$$
Then, using the inductive bounds in $m$ and in $r$,
\[
\begin{aligned}
Q_\pm(r,P_m)
&\le 2d_r\,2^{r(m-1)}+2^{m-1}d_{r-1}\,2^{(r-1)(m-1)} \\
&= \bigl(2d_r+d_{r-1}\bigr)2^{r(m-1)}
 \le 2^r d_r\,2^{r(m-1)}
 = d_r\,2^{rm}.
\end{aligned}
\]
This proves the claim. $\square$

Now let $k\ge 2$. Every convex $k$-subset $S\subseteq P_m$ has a unique leftmost point and a unique rightmost point. Along the upper hull from left to right one obtains an $a$-cup for some $2\le a\le k$, and along the lower hull one obtains a $(k+2-a)$-cap. Forgetting the endpoint-matching condition gives an injection into the disjoint union of pairs of chains, so
$$
C_k(P_m)\le \sum_{a=2}^k Q_+(a,P_m)\,Q_-(k+2-a,P_m).
$$
This is the accepted chain-pair injection.

Combining this with the accepted cup/cap estimates gives the finite-level bound
$$
C_k(P_m)\le (k-1)\,2^{(k+2)m-\lfloor (k+1)^2/4\rfloor}
\qquad (k\ge 2).
$$
For $k=1$ we simply have
$$
C_1(P_m)=|P_m|=2^m.
$$

Therefore
$$
g(P_m)=C_1(P_m)+\sum_{k=2}^{2^m} C_k(P_m)
\le 2^m+\sum_{k=2}^{2^m} (k-1)\,2^{(k+2)m-\lfloor (k+1)^2/4\rfloor}.
$$
The exponent
$$
\phi_m(k):=(k+2)m-\lfloor (k+1)^2/4\rfloor
$$
is maximized for $k$ near $2m-1$, with maximum value $m^2+m+O(1)$, and it decreases quadratically away from that point. Hence the whole sum is bounded by a polynomial factor times $2^{m^2+m}$, and therefore
$$
g(P_m)\le 2^{m^2+m+O(\log m)}.
$$

Finally, extend from the special sizes $|P_m|=2^m$ to arbitrary $n\ge 1$. If $n=1$, then trivially $f(1)=1$. If $n\ge 2$, let
$$
M:=\lceil \log_2 n\rceil,
$$
so $M\ge 1$ and $|P_M|=2^M\ge n$. Choose any $n$-point subset $S\subseteq P_M$. Every convex subset of $S$ is also a convex subset of $P_M$, so
$$
g(S)\le g(P_M)\le 2^{M^2+M+O(\log M)}.
$$
Since $M=\log_2 n+O(1)$, this yields
$$
f(n)\le 2^{(\log_2 n)^2+O(\log n)}
\qquad (n\ge 1).
$$

As for the discarded $\alpha=2$ claim: the obstruction is exactly that total cup/cap counts do not by themselves control convex $k$-sets, because a convex $k$-set requires the upper and lower hull chains to have matching endpoints, while the aggregate quantities $Q_+$ and $Q_-$ forget that endpoint data.

Remaining proof-tightness issues: none seen in this corrected upper-bound note beyond the already-recorded endpoint-matching obstruction for the discarded $\alpha=2$ claim.

## [[status/recursive-family-information-loss]]

Summary: With the repaired one-split convention, the spanning recurrence is exactly a left-cup/right-cap factorization, and the crossing cup/cap formulas are exact endpoint-refined identities. The first place [[bounds/upper-bound-recursive-family]] truly loses the matched outer endpoints $(\ell,r)$ is the chain-pair inequality
$$
C_k(P_m)\le \sum_{a=2}^k Q_+(a,P_m)\,Q_-(k+2-a,P_m),
$$
not the earlier auxiliary inequalities used only to bound total cup/cap counts.

Assume the one-split hypotheses of [[lemmas/one-split-structure-spanning-convex-subsets]]:
$$
P=L\sqcup R,
$$
every point of $L$ lies to the left of every point of $R$, every line through two points of $L$ lies strictly below every point of $R$, and every line through two points of $R$ lies strictly above every point of $L$.

For a spanning convex subset $S\subseteq P$, write
$$
\ell=\min_x S,\qquad r=\max_x S,\qquad \lambda=\max_x(S\cap L),\qquad \rho=\min_x(S\cap R).
$$
For $a,b\ge 1$, let
$$
C^\times(a,b,P;\ell,\lambda,\rho,r)
$$
denote the number of spanning convex subsets with $|S\cap L|=a$, $|S\cap R|=b$, and state $(\ell,\lambda,\rho,r)$.

The exact fixed-state identity from [[lemmas/one-split-fixed-state-recurrence]] is
$$
C^\times(a,b,P;\ell,\lambda,\rho,r)
=
\widetilde Q_+(a,L;\ell,\lambda)\,\widetilde Q_-(b,R;\rho,r).
$$
This is an identity, not an inequality: fixing the state fixes the left endpoint pair $(\ell,\lambda)$ and the right endpoint pair $(\rho,r)$ exactly.

If $C^\times(a,b,P)$ denotes the number of spanning convex subsets with $|S\cap L|=a$ and $|S\cap R|=b$, then the exact fixed-split-size identity is
$$
C^\times(a,b,P)
=
\sum_{(\ell,\lambda,\rho,r)\,\mathrm{admissible}}
C^\times(a,b,P;\ell,\lambda,\rho,r)
=
\sum_{(\ell,\lambda,\rho,r)\,\mathrm{admissible}}
\widetilde Q_+(a,L;\ell,\lambda)\,\widetilde Q_-(b,R;\rho,r).
$$
Again this is an identity: every spanning convex subset has a unique state, so the state classes are disjoint and exhaustive.

Now fix outer endpoints $\ell\in L$ and $r\in R$.

For $t\ge 2$, specialize to $b=1$. Since
$$
\widetilde Q_-(1,R;\rho,r)=0 \text{ unless } \rho=r,\qquad \widetilde Q_-(1,R;r,r)=1,
$$
the fixed-state identity becomes
$$
C^\times(t,1,P;\ell,\lambda,r,r)=Q_+(t,L;\ell,\lambda).
$$
Summing over the remaining endpoint parameter $\lambda$ gives the exact spanning-cup identity
$$
Q_+^\times(t+1,P;\ell,r)
=
\sum_{\lambda\in L,\ \ell<\lambda} Q_+(t,L;\ell,\lambda).
$$
There is no inequality here: a spanning $(t+1)$-cup with outer endpoints $(\ell,r)$ has exactly one right-side point, namely $r$, hence a unique state of the form $(\ell,\lambda,r,r)$; different $\lambda$ give disjoint classes; and every $t$-cup in $L$ with endpoints $(\ell,\lambda)$ extends uniquely by adjoining $r$.

Dually, specialize to $a=1$. Since
$$
\widetilde Q_+(1,L;\ell,\lambda)=0 \text{ unless } \lambda=\ell,\qquad \widetilde Q_+(1,L;\ell,\ell)=1,
$$
the fixed-state identity becomes
$$
C^\times(1,t,P;\ell,\ell,\rho,r)=Q_-(t,R;\rho,r).
$$
Summing over the remaining endpoint parameter $\rho$ gives the exact spanning-cap identity
$$
Q_-^\times(t+1,P;\ell,r)
=
\sum_{\rho\in R,\ \rho<r} Q_-(t,R;\rho,r).
$$
Again there is no inequality: a spanning $(t+1)$-cap with outer endpoints $(\ell,r)$ has exactly one left-side point, namely $\ell$, hence a unique state of the form $(\ell,\ell,\rho,r)$; different $\rho$ give disjoint classes; and every $t$-cap in $R$ with endpoints $(\rho,r)$ extends uniquely by adjoining $\ell$.

So the corrected one-split framework does not lose endpoint information. The exact state is $(\ell,\lambda,\rho,r)$, and the crossing identities are exact sums over the single remaining endpoint parameter after the degenerate specializations $b=1$ and $a=1$.

In [[bounds/upper-bound-recursive-family]], the first inequality that actually forgets the matched outer endpoints $(\ell,r)$ of a convex subset is
$$
C_k(P_m)\le \sum_{a=2}^k Q_+(a,P_m)\,Q_-(k+2-a,P_m).
$$
A convex $k$-subset determines an upper-hull cup and a lower-hull cap with the same outer endpoints $(\ell,r)$, but the right-hand side counts arbitrary pairs of cups and caps of the indicated sizes, whether or not they share those endpoints. That is the genuine endpoint-forgetting step.

This should be distinguished from the earlier auxiliary inequalities
$$
Q_\pm(r,P_m)\le 2\,Q_\pm(r,P_{m-1})+2^{m-1}Q_\pm(r-1,P_{m-1})
$$
and
$$
Q_\pm(r,P_m)\le d_r\,2^{rm}.
$$
Those inequalities are used only to bound total cup/cap counts. They are not the step where a convex set is represented by two hull chains and the requirement of matching outer endpoints is discarded.

Restoring endpoint matching alone does not explain, and by itself does not improve, the leading constant $1$ in
$$
f(n)\le 2^{(\log_2 n)^2+O(\log n)}.
$$
The reason is that the coefficient of $(\log_2 n)^2$ comes from the later optimization using the coarse total bounds for $Q_+$ and $Q_-$. Exact endpoint matching may change only lower-order factors associated with summing over endpoint choices; without a substantially sharper endpoint-refined bound than the present total $Q_\pm$ estimates, it does not change the leading quadratic constant.

## [[status/endpoint-matched-recursive-family]]

Summary: After summing the exact fixed-endpoint identity over the actual endpoint pairs of a given first-separation scale, the endpoint-matched count factorizes exactly as
$$
\sum_{s(\ell,r)=s} E_k(\ell,r)
=
2^{m-s}\sum_{a=1}^{k-1} Q_+(a,P_{s-1})\,Q_-(k-a,P_{s-1}).
$$
So the worst-case-over-pairs step can be repaired completely inside the recursive family. However, the repaired aggregate is already of size $2^{m^2-O(m)}$ for the top split and $k=2m$, hence the endpoint-matched analysis still has leading coefficient $1$ at the $(\log_2 n)^2$ scale and gives no genuine improvement.

Let
$$
P_m=L_m\sqcup R_m
$$
be the standard recursively separated family from [[bounds/upper-bound-recursive-family]]. For $d\ge 1$ and $a\ge 1$, set
$$
Q_d(a):=Q_+(a,P_d)=Q_-(a,P_d).
$$
The equality is by the left-right symmetry of the construction.

For $\ell<r$ in $P_m$, let $s(\ell,r)$ be the first separation scale, so $(\ell,r)$ lies in a unique copy of $P_s$ whose left and right children contain $\ell$ and $r$. Let $\ell^-,r^+\in P_{s-1}$ be the corresponding points in those child copies. By [[attempts/endpoint-matched-recursive-family-worst-case-gap]], for every such pair,
$$
E_k(\ell,r)=\sum_{a=1}^{k-1} U_{s-1}(a;\ell^-)\,V_{s-1}(k-a;r^+).
$$
This is an exact identity.

## Exact Aggregate Over Actual Endpoint Pairs

Fix $m\ge s\ge 2$, and define
$$
R_{m,s}(k):=\sum_{s(\ell,r)=s} E_k(\ell,r).
$$
There are exactly $2^{m-s}$ copies of $P_s$ inside $P_m$. In each such copy, the actual pairs $(\ell,r)$ with first separation scale $s$ are in bijection with the actual pairs $(x,y)\in P_{s-1}\times P_{s-1}$ coming from the left and right children. Therefore
$$
\begin{aligned}
R_{m,s}(k)
&=2^{m-s}\sum_{x\in P_{s-1}}\sum_{y\in P_{s-1}}
\sum_{a=1}^{k-1} U_{s-1}(a;x)\,V_{s-1}(k-a;y) \\
&=2^{m-s}\sum_{a=1}^{k-1}
\left(\sum_{x\in P_{s-1}} U_{s-1}(a;x)\right)
\left(\sum_{y\in P_{s-1}} V_{s-1}(k-a;y)\right).
\end{aligned}
$$
This is still exact: it is the sum over the true endpoint pairs, with no worst-case bound.

Now
$$
\sum_{x\in P_d} U_d(a;x)=Q_+(a,P_d)=Q_d(a),
\qquad
\sum_{y\in P_d} V_d(a;y)=Q_-(a,P_d)=Q_d(a),
$$
because every $a$-cup has a unique left endpoint and every $a$-cap has a unique right endpoint. Hence
$$
R_{m,s}(k)
=
2^{m-s}\sum_{a=1}^{k-1} Q_{s-1}(a)\,Q_{s-1}(k-a).
$$
This is the exact aggregate endpoint-matched formula.

Equivalently, if
$$
A_d(z):=\sum_{a\ge 1} Q_d(a)\,z^{a-1},
$$
then
$$
R_{m,s}(k)=2^{m-s}[z^{k-2}]\,A_{s-1}(z)^2.
$$
Again this is exact.

## Exact Recurrence For Convex Subsets

For $k\ge 2$, decomposing a convex $k$-subset of $P_m$ according to whether it lies in one child copy or spans the top split gives
$$
C_k(P_m)=2\,C_k(P_{m-1})+\sum_{a=1}^{k-1} Q_{m-1}(a)\,Q_{m-1}(k-a).
$$
This is an exact identity, not an inequality. Thus exact endpoint aggregation produces exactly the cup/cap convolution already present at each recursive split.

## Exact Formula For The Cup/Cap Totals

Summing the exact one-sided recurrences from [[attempts/endpoint-matched-recursive-family-worst-case-gap]] over all endpoints gives, for $d\ge 2$ and $a\ge 2$,
$$
Q_d(a)=2\,Q_{d-1}(a)+2^{d-1}Q_{d-1}(a-1),
$$
with
$$
Q_d(1)=2^d.
$$
Equivalently,
$$
A_1(z)=2+z,
\qquad
A_d(z)=(2+2^{d-1}z)\,A_{d-1}(z),
$$
so
$$
A_d(z)=\prod_{j=0}^{d-1}(2+2^j z).
$$
This is exact.

Extracting coefficients,
$$
Q_d(a)=\sum_{\substack{J\subseteq\{0,\dots,d-1\}\\|J|=a-1}}
2^{\,d-a+1+\sum_{j\in J} j}.
$$
This is exact. Hence
$$
Q_d(a)\ge 2^{\,ad-\frac{a(a+1)}2+1},
$$
by taking the largest summand, and
$$
Q_d(a)\le \binom{d}{a-1}\,2^{\,ad-\frac{a(a+1)}2+1}
\le 2^{\,ad-\frac{a(a+1)}2+1+d}.
$$
These are inequalities.

## Obstruction At The Quadratic Scale

The exact aggregate already has a top-split term of size $2^{m^2-O(m)}$.

Indeed, $A_d(z)$ has degree $d$, and its top coefficient is
$$
Q_d(d+1)=2^{0+1+\cdots+(d-1)}=2^{\binom d2}.
$$
This is exact.

Now take the top split of $P_m$, so $s=m$ and $d=m-1$. For $k=2m$, the convolution has only one nonzero term, namely $a=m$, because $Q_{m-1}(a)=0$ for $a>m$. Therefore
$$
R_{m,m}(2m)=Q_{m-1}(m)^2
=2^{\,2\binom{m-1}{2}}
=2^{(m-1)(m-2)}.
$$
This is exact.

So the repaired aggregate endpoint-matched count already contains terms of size
$$
2^{m^2-3m+2}=2^{(\log_2 |P_m|)^2+O(\log |P_m|)}.
$$
Therefore exact summation over the actual endpoint states/signatures does not improve the quadratic coefficient below $1$.

Combined with the accepted upper bound from [[bounds/upper-bound-recursive-family]],
$$
g(P_m)\le 2^{m^2+O(m)},
$$
the endpoint-matched analysis inside the present recursive family still has leading coefficient exactly $1$ at the $(\log_2 n)^2$ scale.

Conclusion: the gap in [[attempts/endpoint-matched-recursive-family-worst-case-gap]] can be repaired rigorously, but the repaired aggregate shows no real improvement. Endpoint matching disappears only after an exact summation over the actual endpoint pairs, and that exact sum is already large enough to force the same quadratic coefficient $1$.

======== RESPONSE ========

I could not write the file into the repo in this session because every filesystem tool call failed with `bwrap: Unknown option --argv0`. The note below is repo-ready markdown for `attempts/alternative-construction-fibonacci-split.md`.

```md
Summary: Replace the balanced split by the non-self-similar separated recursion $F_m=F_{m-1}\sqcup F_{m-2}$. This gives exact recurrences different from the balanced family, but one explicit top-split term already forces
$$
g(F_m)\ge 2^{\left(\frac{3}{4\log_2\varphi}+o(1)\right)(\log_2 n)^2}
$$
with $\frac{3}{4\log_2\varphi}>1$, so this family should be discarded as a route to lowering the coefficient $1$ in [[bounds/upper-bound-recursive-family]].

# Alternative Construction: Fibonacci Split

After [[status/endpoint-matched-recursive-family]], endpoint matching inside the old balanced family no longer looks like the right bottleneck: the exact endpoint-matched aggregate already keeps the quadratic coefficient $1$. The next fork is therefore to change the recursion itself. A minimal explicit test case is the unbalanced separated split with child depths $m-1$ and $m-2$.

## Definition

Let $F_1$ be a one-point set and $F_2$ a two-point set. For $m\ge 3$, define
$$
F_m=L_m\sqcup R_m,
$$
where $L_m$ is an affine copy of $F_{m-1}$, $R_m$ an affine copy of $F_{m-2}$, and $(L_m,R_m)$ is in the standard one-split separated position.

Let
$$
N_m:=|F_m|.
$$
Then exactly
$$
N_1=1,\qquad N_2=2,\qquad N_m=N_{m-1}+N_{m-2}\quad (m\ge 3).
$$
Hence $N_m=\Theta(\varphi^m)$ with $\varphi=\frac{1+\sqrt5}{2}$, so
$$
\log_2 N_m=m\log_2\varphi+O(1).
$$

For $a\ge 1$ define
$$
U_m(a):=Q_+(a,F_m),\qquad V_m(a):=Q_-(a,F_m),
$$
and for $k\ge 1$ define
$$
C_m(k):=C_k(F_m).
$$

## Exact Recurrences

By the exact one-split factorization from [[status/recursive-family-information-loss]], for $a\ge 2$ we have:

$$
U_m(a)=U_{m-1}(a)+U_{m-2}(a)+N_{m-2}U_{m-1}(a-1).
$$

This is an exact identity: a spanning $a$-cup consists of an $(a-1)$-cup in $L_m$ and one point of $R_m$. Also
$$
U_m(1)=N_m.
$$

Dually,
$$
V_m(a)=V_{m-1}(a)+V_{m-2}(a)+N_{m-1}V_{m-2}(a-1),
$$
again an exact identity, with
$$
V_m(1)=N_m.
$$

Summing the exact endpoint-refined spanning identity over all states gives the exact convex-subset recurrence
$$
C_m(k)=C_{m-1}(k)+C_{m-2}(k)+\sum_{a=1}^{k-1}U_{m-1}(a)V_{m-2}(k-a).
$$

So this family does give a genuinely different recurrence from the balanced family: the spanning convolution now mixes different depths.

## First Top-Scale Obstruction

Set
$$
u_m:=\max\{a:U_m(a)>0\}.
$$
From the exact cup recurrence,
$$
u_1=1,\qquad u_2=2,\qquad u_m=u_{m-1}+1,
$$
so exactly
$$
u_m=m.
$$

Let
$$
U_m^\ast:=U_m(m).
$$
Since neither child alone contains an $m$-cup, the maximal cups are exactly the spanning ones, hence
$$
U_m^\ast=N_{m-2}U_{m-1}^\ast
$$
with $U_2^\ast=1$. Therefore exactly
$$
U_m^\ast=\prod_{j=1}^{m-2}N_j.
$$

Now set
$$
v_m:=\max\{a:V_m(a)>0\}.
$$
From the exact cap recurrence,
$$
v_1=1,\qquad v_2=2,\qquad v_m=\max(v_{m-1},1+v_{m-2}),
$$
so
$$
v_{2t}=t+1,\qquad v_{2t+1}=t+1.
$$

Define
$$
V_{2t}^\ast:=V_{2t}(t+1).
$$
Because $v_{2t}=t+1>v_{2t-1}=t$ and $v_{2t-2}=t$, the maximal caps in even depth are again exactly the spanning ones. Thus
$$
V_{2t}^\ast=N_{2t-1}V_{2t-2}^\ast
$$
with $V_2^\ast=1$, hence exactly
$$
V_{2t}^\ast=\prod_{i=1}^{t-1}N_{2i+1}.
$$

Take $m=2t+2$. In the exact convex-subset recurrence, keep only the summand
$$
a=u_{m-1}=2t+1,\qquad k-a=v_{m-2}=t+1.
$$
Then
$$
C_m(3t+2)\ge U_{2t+1}^\ast V_{2t}^\ast
=\left(\prod_{j=1}^{2t-1}N_j\right)\left(\prod_{i=1}^{t-1}N_{2i+1}\right).
$$
This is an inequality obtained from one term of an exact recurrence.

Using $N_r=\Theta(\varphi^r)$,
$$
\log_2 U_{2t+1}^\ast
=(\log_2\varphi)\sum_{j=1}^{2t-1}j+O(t)
=(\log_2\varphi)(2t^2-t)+O(t),
$$
and
$$
\log_2 V_{2t}^\ast
=(\log_2\varphi)\sum_{i=1}^{t-1}(2i+1)+O(t)
=(\log_2\varphi)(t^2-1)+O(t).
$$
Therefore
$$
\log_2 g(F_m)\ge \log_2 C_m(3t+2)\ge \frac34(\log_2\varphi)m^2+O(m).
$$

Since $\log_2 N_m=m\log_2\varphi+O(1)$, this becomes
$$
g(F_m)\ge 2^{\left(\frac{3}{4\log_2\varphi}+o(1)\right)(\log_2 N_m)^2}.
$$
Numerically,
$$
\frac{3}{4\log_2\varphi}\approx 1.0802>1.
$$

## Conclusion

This Fibonacci-split family is well-posed and its counting recurrence is genuinely different from the balanced family, but it already fails at the quadratic scale: one explicit top-split contribution forces a coefficient strictly larger than $1$. So this alternative should be discarded as the next fork after [[status/endpoint-matched-recursive-family]].
```
