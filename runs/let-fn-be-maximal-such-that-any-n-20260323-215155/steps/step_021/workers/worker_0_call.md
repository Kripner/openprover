---
call_num: 12
label: worker_21_0
model: gpt-5.4
elapsed_ms: 127968
input_tokens: 75397
output_tokens: 6694
cache_read_tokens: 65280
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

Use [[attempts/one-split-structure-draft]] and the recursive construction in [[bounds/upper-bound-recursive-family]].

Your one task is to turn the draft into a clean, self-contained lemma note.

What to do:
- State the exact geometric hypotheses on the split $P_m=L_m\sqcup R_m$ that are really needed.
- Repair the two specific rigor gaps flagged by verification:
  1. explain explicitly why, if the upper hull had more than one vertex from $L_m$, then two such vertices are consecutive on that left-to-right hull chain;
  2. fix the endpoint wording so the statement about chain membership is literally correct.
- Give a short rigorous proof of the structural decomposition of any convex subset $S\subset P_m$ meeting both halves.
- State the minimal endpoint/state data needed for a later recurrence, and explain briefly why it enforces common global endpoints.

Scope restrictions:
- Do not do any counting, recurrence derivation, asymptotics, or optimization.
- Do not use literature.
- Do not write Lean.

Deliverable:
Return a polished note suitable to store directly as a lemma item, with a suggested slug such as
`lemmas/one-split-structure-spanning-convex-subsets`.



# Referenced Materials

## [[attempts/one-split-structure-draft]]

Summary: Draft one-split structural lemma says a convex subset spanning the recursive split decomposes as a left cap plus right cup under explicit left-right and high-above hypotheses, but the proof still needs two minor rigor fixes.

Draft statement from worker output:

Assume for the split
$$
P_m=L_m\sqcup R_m
$$
that, after a generic rotation, all $x$-coordinates are distinct, and:
1. every point of $L_m$ lies to the left of every point of $R_m$;
2. every line through two points of $L_m$ lies strictly below every point of $R_m$;
3. every line through two points of $R_m$ lies strictly above every point of $L_m$.

Let $S\subset P_m$ be in convex position, with
$$
S\cap L_m\neq\varnothing,\qquad S\cap R_m\neq\varnothing.
$$
Let
$$
\ell=\text{leftmost point of }S,\quad r=\text{rightmost point of }S,
$$
and
$$
\lambda=\text{rightmost point of }(S\cap L_m),\quad
\rho=\text{leftmost point of }(S\cap R_m).
$$
Let $U(S)$ and $D(S)$ be the upper and lower hull chains of $S$, from left to right.

Claim:
- $\ell\in L_m$ and $r\in R_m$;
- the upper hull contains exactly one vertex from $L_m$, namely $\ell$;
- the lower hull contains exactly one vertex from $R_m$, namely $r$.

Hence
$$
U(S)=\ell,\rho=u_1,u_2,\dots,u_t=r
$$
with all interior $u_i\in R_m$, and
$$
D(S)=\ell=v_1,v_2,\dots,v_s=\lambda,r
$$
with all interior $v_j\in L_m$.

So:
- $S\cap R_m$ is exactly the upper-hull chain in $R_m$, i.e. a cup with endpoints $(\rho,r)$;
- $S\cap L_m$ is exactly the lower-hull chain in $L_m$, i.e. a cap with endpoints $(\ell,\lambda)$.

Therefore every spanning convex subset has the exact decomposition
$$
S=(\text{cap in }L_m\text{ with endpoints }(\ell,\lambda))
\sqcup
(\text{cup in }R_m\text{ with endpoints }(\rho,r)).
$$

State data suggested by worker:
$$
(\ell,\lambda,\rho,r),
$$
equivalently a left cap-state indexed by $(\ell,\lambda)$ and a right cup-state indexed by $(\rho,r)$.

Verifier feedback:
- The conclusion appears correct under the stated hypotheses.
- Two minor fixes are still needed before this should be promoted to a lemma item:
  1. explicitly justify why “more than one $L_m$-vertex on the upper hull” implies two consecutive $L_m$-vertices on that chain, using left-right $x$-separation and chain monotonicity;
  2. replace the sentence “every point of a set in convex position lies on exactly one of the two hull chains” by the correct endpoint-aware version, since the common endpoints lie on both chains.

Use this item as the source draft for a clean repaired lemma.


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

======== RESPONSE ========

Suggested slug: `lemmas/one-split-structure-spanning-convex-subsets`

Let
$$
P=L\sqcup R
$$
be a finite planar point set. After a sufficiently small generic rotation, assume that all points of $P$ have distinct $x$-coordinates, and that:

1. every point of $L$ lies to the left of every point of $R$;
2. every line through two points of $L$ lies strictly below every point of $R$;
3. every line through two points of $R$ lies strictly above every point of $L$.

These are the only geometric properties of the recursive split used below.

For a subset $S\subset P$ in convex position, write $U(S)$ and $D(S)$ for the upper and lower hull chains of $S$, both listed from left to right.

**Lemma.** Let $S\subset P$ be in convex position and assume
$$
S\cap L\neq\varnothing,\qquad S\cap R\neq\varnothing.
$$
Let
$$
\ell=\text{leftmost point of }S,\qquad r=\text{rightmost point of }S,
$$
and let
$$
\lambda=\text{rightmost point of }(S\cap L),\qquad
\rho=\text{leftmost point of }(S\cap R).
$$
Then:

1. $\ell\in L$ and $r\in R$.
2. $U(S)$ contains exactly one vertex from $L$, namely $\ell$.
3. $D(S)$ contains exactly one vertex from $R$, namely $r$.

Consequently, if the points of $S\cap R$ are listed in increasing $x$-order as
$$
\rho=u_1,\dots,u_t=r,
$$
then
$$
U(S)=\ell,u_1,\dots,u_t.
$$
Likewise, if the points of $S\cap L$ are listed in increasing $x$-order as
$$
\ell=v_1,\dots,v_s=\lambda,
$$
then
$$
D(S)=v_1,\dots,v_s,r.
$$
Equivalently, $S\cap R$ is exactly the upper-hull chain in $R$ from $\rho$ to $r$, and $S\cap L$ is exactly the lower-hull chain in $L$ from $\ell$ to $\lambda$.

In particular,
$$
S=(\text{cap in }L\text{ with endpoints }(\ell,\lambda))
\sqcup
(\text{cup in }R\text{ with endpoints }(\rho,r)),
$$
with the degenerate cases $\ell=\lambda$ and $\rho=r$ allowed.

**Proof.** By hypothesis (1), every point of $L$ has smaller $x$-coordinate than every point of $R$. Since $S$ meets both halves, its leftmost point lies in $L$ and its rightmost point lies in $R$, so $\ell\in L$ and $r\in R$.

Because all $x$-coordinates are distinct, each of the hull chains $U(S)$ and $D(S)$ is strictly monotone in $x$. Hence on either chain every vertex from $L$ appears before every vertex from $R$.

Suppose that $U(S)$ contains at least two vertices from $L$. Let $p,q$ be the last two such vertices along $U(S)$ from left to right. They are consecutive on $U(S)$: any vertex between them on that chain would have $x$-coordinate between those of $p$ and $q$, hence by the left-right separation would also lie in $L$, contradicting the choice of $p,q$ as the last two $L$-vertices. Since $pq$ is an edge of the upper hull of $S$, every point of $S$ lies on or below the line through $p,q$. But $p,q\in L$, so hypothesis (2) says that every point of $R$, hence every point of $S\cap R$, lies strictly above that line. This contradicts $S\cap R\neq\varnothing$. Therefore $U(S)$ contains at most one vertex from $L$, and since $\ell\in U(S)\cap L$, it contains exactly one such vertex, namely $\ell$.

The lower-hull statement is symmetric. If $D(S)$ contained at least two vertices from $R$, let $p,q$ be the first two such vertices along $D(S)$ from left to right. Again they are consecutive on $D(S)$, because any intermediate vertex would also have to lie in $R$. Since $pq$ is an edge of the lower hull, every point of $S$ lies on or above the line through $p,q$. But $p,q\in R$, so hypothesis (3) implies that every point of $L$, hence every point of $S\cap L$, lies strictly below that line, contradiction. Thus $D(S)$ contains exactly one vertex from $R$, namely $r$.

Now use the correct endpoint-aware hull decomposition: every non-endpoint of $S$ lies on exactly one of the two chains $U(S),D(S)$, while the common endpoints $\ell,r$ lie on both. Since the only $R$-vertex on $D(S)$ is the endpoint $r$, every point of $S\cap R\setminus\{r\}$ lies on $U(S)$. Hence all points of $S\cap R$ occur on $U(S)$, and by $x$-monotonicity they appear there exactly in increasing $x$-order, from $\rho$ to $r$. This gives
$$
U(S)=\ell,u_1,\dots,u_t.
$$
Similarly, since the only $L$-vertex on $U(S)$ is the endpoint $\ell$, every point of $S\cap L\setminus\{\ell\}$ lies on $D(S)$, so the points of $S\cap L$ appear on $D(S)$ exactly in increasing $x$-order from $\ell$ to $\lambda$, giving
$$
D(S)=v_1,\dots,v_s,r.
$$
The cap-cup decomposition follows immediately. $\square$

For a later recurrence, the minimal endpoint/state data is
$$
(\ell,\lambda,\rho,r),
$$
equivalently a left-cap state indexed by $(\ell,\lambda)$ together with a right-cup state indexed by $(\rho,r)$. The outer entries $\ell$ and $r$ are the global leftmost and rightmost points of the spanning convex set, while $\lambda$ and $\rho$ record the terminal vertices of the left and right local chains at the split. Thus this state retains exactly the global-endpoint information lost by the aggregate counts $Q_+$ and $Q_-$, and it is enough to enforce common global endpoints when the two sides are combined.

I was not able to write this into the workspace because the local tool wrapper is failing with `bwrap: Unknown option --argv0`.
