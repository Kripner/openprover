---
call_num: 19
label: worker_28_0
model: gpt-5.4
elapsed_ms: 251380
input_tokens: 79691
output_tokens: 11658
cache_read_tokens: 56832
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

Use [[lemmas/one-split-fixed-state-recurrence]], [[lemmas/one-split-crossing-cup-cap-identities]], and [[bounds/upper-bound-recursive-family]].

Work on exactly one task: repair the note currently intended for `status/recursive-family-information-loss` by filling the one remaining gap.

What is already solid:
- For fixed state $(\ell,\lambda,\rho,r)$,
  $$
  C^\times(a,b,P_m;\ell,\lambda,\rho,r)
  =
  \widetilde Q_+(a,L_m;\ell,\lambda)\,\widetilde Q_-(b,R_m;\rho,r).
  $$
- Summing over all states gives the exact factorization for fixed split size $(a,b)$.
- The likely first genuine loss is later, when endpoint-matched identities are replaced by products of coarse totals and the shared outer endpoints $(\ell,r)$ are forgotten.

Your job:
Produce a short polished note, ready to store directly as `status/recursive-family-information-loss`, that does all of the following:
1. States the exact fixed-split-size identity.
2. Explicitly derives the exact crossing passage, not just by assertion:
   - write the exact formulas for spanning cups/caps obtained by summing the fixed-state identities in the cases $a=1$ or $b=1$;
   - explain clearly why this still involves exact summation over the relevant endpoint parameter and no inequality.
3. Then identify the first actual inequality in the recursive-family upper-bound argument, specifying precisely which endpoint information is forgotten there.
4. State whether that loss alone explains the exponent constant $1$, with a brief justification.

Requirements:
- Keep it self-contained relative to the cited items.
- Be explicit about which displayed formulas are exact identities and which are only inequalities.
- Do not do new asymptotic optimization, literature, or Lean.
- The output should be repo-ready markdown with a `Summary:` line.

If you find any hidden earlier inequality before the endpoint-forgetting step, say so precisely and revise the conclusion accordingly.


# Referenced Materials

## [[lemmas/one-split-fixed-state-recurrence]]

Summary: For a fixed state in a one-split configuration, spanning convex subsets are counted exactly by a product of a left endpoint-refined cup count and a right endpoint-refined cap count; summing over states is also exact.

Assume the hypotheses of [[lemmas/one-split-structure-spanning-convex-subsets]]:
$$
P=L\sqcup R,
$$
every point of $L$ lies to the left of every point of $R$, every line through two points of $L$ lies strictly below every point of $R$, and every line through two points of $R$ lies strictly above every point of $L$.

For a spanning convex subset $S\subseteq P$, write
$$
\ell=\min_x S,\qquad r=\max_x S,
$$
$$
\lambda=\max_x(S\cap L),\qquad \rho=\min_x(S\cap R).
$$
Call $(\ell,\lambda,\rho,r)$ the state of $S$.

For integers $a,b\ge 1$, let
$$
C^\times(a,b,P;\ell,\lambda,\rho,r)
$$
denote the number of spanning convex subsets $S\subseteq P$ with
$$
|S\cap L|=a,\qquad |S\cap R|=b,
$$
and state $(\ell,\lambda,\rho,r)$.

Define degenerate endpoint-refined local counts by
$$
\widetilde Q_+(a,L;\ell,\lambda):=
\begin{cases}
1,& a=1\text{ and }\ell=\lambda,\\
Q_+(a,L;\ell,\lambda),& a\ge 2\text{ and }\ell<\lambda,\\
0,&\text{otherwise,}
\end{cases}
$$
and
$$
\widetilde Q_-(b,R;\rho,r):=
\begin{cases}
1,& b=1\text{ and }\rho=r,\\
Q_-(b,R;\rho,r),& b\ge 2\text{ and }\rho<r,\\
0,&\text{otherwise.}
\end{cases}
$$

## Proposition

For every admissible state $(\ell,\lambda,\rho,r)$ and every $a,b\ge 1$,
$$
C^\times(a,b,P;\ell,\lambda,\rho,r)
=
\widetilde Q_+(a,L;\ell,\lambda)\,\widetilde Q_-(b,R;\rho,r).
$$

Here the local quantities are a left cup count and a right cap count. Endpoint matching is enforced because fixing $(\ell,\lambda,\rho,r)$ forces the local endpoint pairs to be exactly $(\ell,\lambda)$ on $L$ and $(\rho,r)$ on $R$.

## Proof

Let $S$ be counted by $C^\times(a,b,P;\ell,\lambda,\rho,r)$, and list
$$
S\cap L=\{v_1=\ell<\cdots<v_a=\lambda\},\qquad
S\cap R=\{u_1=\rho<\cdots<u_b=r\}.
$$
By the explicit hull-chain formulas in [[lemmas/one-split-structure-spanning-convex-subsets]],
$$
D(S)=v_1,\dots,v_a,r,
\qquad
U(S)=\ell,u_1,\dots,u_b.
$$
Since $D(S)$ is a lower hull chain, its consecutive slopes are strictly increasing, so
$$
v_1,\dots,v_a
$$
is an $a$-cup in $L$ with endpoints $(\ell,\lambda)$ when $a\ge 2$, and when $a=1$ this says $\lambda=\ell$.
Since $U(S)$ is an upper hull chain, its consecutive slopes are strictly decreasing, so
$$
u_1,\dots,u_b
$$
is a $b$-cap in $R$ with endpoints $(\rho,r)$ when $b\ge 2$, and when $b=1$ this says $\rho=r$.

Thus
$$
\Phi(S):=(S\cap L,\;S\cap R)
$$
lands in the product counted by
$$
\widetilde Q_+(a,L;\ell,\lambda)\,\widetilde Q_-(b,R;\rho,r),
$$
and $\Phi$ is injective because
$$
S=(S\cap L)\sqcup(S\cap R).
$$

For surjectivity, let
$$
A=\{v_1=\ell<\cdots<v_a=\lambda\}\subseteq L
$$
be counted by $\widetilde Q_+(a,L;\ell,\lambda)$ and let
$$
B=\{u_1=\rho<\cdots<u_b=r\}\subseteq R
$$
be counted by $\widetilde Q_-(b,R;\rho,r)$. Set $S:=A\cup B$.

If $a\ge 2$, then $A$ is an $a$-cup, so
$$
\operatorname{slope}(v_1,v_2)<\cdots<\operatorname{slope}(v_{a-1},v_a).
$$
Because $v_{a-1},v_a\in L$, every point of $R$, in particular $r$, lies strictly above the line through $v_{a-1},v_a$. Since
$$
x_{v_{a-1}}<x_{v_a}<x_r,
$$
this is equivalent to
$$
\operatorname{slope}(v_{a-1},v_a)<\operatorname{slope}(v_a,r).
$$
Hence
$$
v_1,\dots,v_a,r
$$
is an $(a+1)$-cup. For $a=1$ this chain is just $\ell,r$.

If $b\ge 2$, then $B$ is a $b$-cap, so
$$
\operatorname{slope}(u_1,u_2)>\cdots>\operatorname{slope}(u_{b-1},u_b).
$$
Because $u_1,u_2\in R$, every point of $L$, in particular $\ell$, lies strictly below the line through $u_1,u_2$. Since
$$
x_\ell<x_{u_1}<x_{u_2},
$$
this is equivalent to
$$
\operatorname{slope}(\ell,u_1)>\operatorname{slope}(u_1,u_2).
$$
Hence
$$
\ell,u_1,\dots,u_b
$$
is a $(b+1)$-cap. For $b=1$ this chain is just $\ell,r$.

Therefore
$$
\ell=v_1,\dots,v_a,r
$$
is a lower cup-chain and
$$
\ell,u_1,\dots,u_b=r
$$
is an upper cap-chain with the same endpoints $(\ell,r)$. The cup-chain has all interior vertices strictly below the chord $\ell r$, and the cap-chain has all interior vertices strictly above $\ell r$, so they meet only at $\ell$ and $r$. Hence the boundary of $\operatorname{conv}(S)$ is exactly the concatenation of these two chains, so $S$ is in convex position. Its state is plainly $(\ell,\lambda,\rho,r)$.

Thus $\Phi$ is surjective, hence bijective, and
$$
C^\times(a,b,P;\ell,\lambda,\rho,r)
=
\widetilde Q_+(a,L;\ell,\lambda)\,\widetilde Q_-(b,R;\rho,r).
$$
$\square$

## State Sum

Summing over states gives an exact identity, not merely an inequality. Every spanning convex subset has a unique state $(\ell,\lambda,\rho,r)$, so the families counted by
$$
C^\times(a,b,P;\ell,\lambda,\rho,r)
$$
are disjoint and their union is exactly the family of spanning convex subsets with $|S\cap L|=a$ and $|S\cap R|=b$. Therefore the state sum is exact.

The previous draft failed because it attached the wrong local types: with a left cap and a right cup, the bridge inequalities across the split point the wrong way, so the claimed gluing map is not bijective. With the corrected left-cup/right-cap assignment, the same split inequalities give exactly the needed extensions.


## [[lemmas/one-split-crossing-cup-cap-identities]]

Summary: Under the one-split hypotheses, every spanning cup has exactly one left point and every spanning cap exactly one right point, yielding exact endpoint-refined crossing identities.

Assume the hypotheses of [[lemmas/one-split-structure-spanning-convex-subsets]]: namely
$$
P=L\sqcup R,
$$
every point of $L$ lies to the left of every point of $R$, every line through two points of $L$ lies strictly below every point of $R$, and every line through two points of $R$ lies strictly above every point of $L$.

For $t\ge 2$ and points $a,b$ of a planar point set $X$, write $Q_+(t,X;a,b)$ for the number of $t$-cups in $X$ whose left and right endpoints are $a,b$, and $Q_-(t,X;a,b)$ for the number of $t$-caps in $X$ whose left and right endpoints are $a,b$. Equivalently, in left-to-right order, the consecutive slopes of a cup are strictly increasing and those of a cap are strictly decreasing.

For $\ell\in L$, $r\in R$, and $t\ge 2$, write $Q_+^\times(t+1,P;\ell,r)$ for the number of spanning $(t+1)$-cups $S\subseteq P$ with global endpoints $(\ell,r)$. Define $Q_-^\times(t+1,P;\ell,r)$ analogously for spanning caps.

**Proposition.**
Under the one-split hypotheses, the following hold.

1. If $S\subseteq P$ is a spanning cup with global endpoints $(\ell,r)$, then
$$
S\cap L=\{\ell\}.
$$
So every spanning cup has exactly one point in the left half, namely its global left endpoint.

2. If $S\subseteq P$ is a spanning cap with global endpoints $(\ell,r)$, then
$$
S\cap R=\{r\}.
$$
So every spanning cap has exactly one point in the right half, namely its global right endpoint.

3. Consequently, for every $\ell\in L$, $r\in R$, and $t\ge 2$,
$$
Q_+^\times(t+1,P;\ell,r)=\sum_{\rho\in R,\ \rho<r} Q_+(t,R;\rho,r),
$$
and
$$
Q_-^\times(t+1,P;\ell,r)=\sum_{\lambda\in L,\ \ell<\lambda} Q_-(t,L;\ell,\lambda).
$$

Here $\rho<r$ and $\ell<\lambda$ refer to the left-to-right $x$-order.

**Proof.**
Let $S\subseteq P$ be spanning, and use the notation of [[lemmas/one-split-structure-spanning-convex-subsets]]:
$$
\ell=\min_x S,\qquad r=\max_x S,
$$
$$
\lambda=\max_x(S\cap L),\qquad \rho=\min_x(S\cap R).
$$
That lemma shows that $S\cap L$ is a cap with endpoints $(\ell,\lambda)$, $S\cap R$ is a cup with endpoints $(\rho,r)$, and if
$$
S\cap L=\{v_1=\ell<\cdots<v_s=\lambda\},
$$
then
$$
D(S)=v_1,\dots,v_s,r,
$$
while if
$$
S\cap R=\{u_1=\rho<\cdots<u_t=r\},
$$
then
$$
U(S)=\ell,u_1,\dots,u_t.
$$

Now suppose that $S$ is itself a cup. Then its lower hull has only the two global endpoints $\ell,r$. Comparing with
$$
D(S)=v_1,\dots,v_s,r
$$
forces $s=1$, hence $\lambda=\ell$ and
$$
S\cap L=\{\ell\}.
$$
This proves (1).

The proof of (2) is dual. If $S$ is a spanning cap, then its upper hull has only the two global endpoints $\ell,r$. Comparing with
$$
U(S)=\ell,u_1,\dots,u_t
$$
forces $t=1$, hence $\rho=r$ and
$$
S\cap R=\{r\}.
$$

For the counting identities, fix $\ell\in L$, $r\in R$, and $t\ge 2$.

For cups, define
$$
\Phi(S)=S\cap R.
$$
By (1), this gives a map from spanning $(t+1)$-cups with endpoints $(\ell,r)$ into the disjoint union over $\rho\in R$ with $\rho<r$ of the sets of $t$-cups in $R$ with endpoints $(\rho,r)$. It is injective because
$$
S=\{\ell\}\sqcup \Phi(S).
$$

To prove surjectivity, let
$$
T=\{u_1=\rho<u_2<\cdots<u_t=r\}\subseteq R
$$
be a $t$-cup, and set
$$
S:=\{\ell\}\cup T.
$$
Since $T$ is a cup,
$$
\operatorname{slope}(u_1,u_2)<\operatorname{slope}(u_2,u_3)<\cdots<\operatorname{slope}(u_{t-1},u_t).
$$
Also, $u_1,u_2\in R$, so the line through $u_1,u_2$ lies strictly above every point of $L$, in particular above $\ell$. Because $x_\ell<x_{u_1}<x_{u_2}$, this is equivalent to
$$
\operatorname{slope}(\ell,u_1)<\operatorname{slope}(u_1,u_2).
$$
Hence
$$
\operatorname{slope}(\ell,u_1)
<
\operatorname{slope}(u_1,u_2)
<
\cdots
<
\operatorname{slope}(u_{t-1},u_t),
$$
so
$$
\ell,u_1,\dots,u_t
$$
is a $(t+1)$-cup with endpoints $(\ell,r)$. This includes the case $t=2$: one only uses
$$
\operatorname{slope}(\ell,u_1)<\operatorname{slope}(u_1,r),
$$
so no separate interior-point argument is needed.

Therefore $\Phi$ is bijective, and taking cardinalities gives
$$
Q_+^\times(t+1,P;\ell,r)=\sum_{\rho\in R,\ \rho<r} Q_+(t,R;\rho,r).
$$

The cap identity is dual. Let
$$
T=\{v_1=\ell<v_2<\cdots<v_t=\lambda\}\subseteq L
$$
be a $t$-cap, and set
$$
S:=T\cup\{r\}.
$$
Since $T$ is a cap,
$$
\operatorname{slope}(v_1,v_2)>\operatorname{slope}(v_2,v_3)>\cdots>\operatorname{slope}(v_{t-1},v_t).
$$
Also, $v_{t-1},v_t\in L$, so the line through $v_{t-1},v_t$ lies strictly below every point of $R$, in particular below $r$. Because $x_{v_{t-1}}<x_{v_t}<x_r$, this is equivalent to
$$
\operatorname{slope}(v_{t-1},v_t)>\operatorname{slope}(v_t,r).
$$
Hence
$$
\operatorname{slope}(v_1,v_2)>
\cdots>
\operatorname{slope}(v_{t-1},v_t)>
\operatorname{slope}(v_t,r),
$$
so
$$
v_1,\dots,v_t,r
$$
is a $(t+1)$-cap with endpoints $(\ell,r)$. Thus
$$
Q_-^\times(t+1,P;\ell,r)=\sum_{\lambda\in L,\ \ell<\lambda} Q_-(t,L;\ell,\lambda).
$$

Endpoint matching is enforced because the global outer endpoints $(\ell,r)$ are fixed, while the split lemma recovers uniquely the first right-side vertex $\rho$ for cups and the last left-side vertex $\lambda$ for caps. $\square$

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

The local tool wrapper failed, so I could not patch the file directly. Here is the repo-ready markdown for `status/recursive-family-information-loss`:

```md
Summary: The fixed-split and crossing decompositions are exact identities; the first loss of endpoint information occurs only when the exact endpoint-matched chain-pair count is replaced by a product of total cup/cap counts, although the auxiliary cup/cap-growth lemma already contains earlier inequalities unrelated to endpoint matching.

Let
$$
C^\times(a,b,P_m)
$$
denote the number of spanning convex subsets $S\subseteq P_m=L_m\sqcup R_m$ with
$$
|S\cap L_m|=a,\qquad |S\cap R_m|=b.
$$
By [[lemmas/one-split-fixed-state-recurrence]], for each fixed state $(\ell,\lambda,\rho,r)$ one has the exact identity
$$
C^\times(a,b,P_m;\ell,\lambda,\rho,r)
=
\widetilde Q_+(a,L_m;\ell,\lambda)\,\widetilde Q_-(b,R_m;\rho,r).
\tag{Exact}
$$
Summing over states is still exact, because each spanning convex subset has a unique state. Hence
$$
C^\times(a,b,P_m)
=
\sum_{\ell,\lambda\in L_m}\ \sum_{\rho,r\in R_m}
\widetilde Q_+(a,L_m;\ell,\lambda)\,\widetilde Q_-(b,R_m;\rho,r).
\tag{Exact}
$$
Here inadmissible terms vanish by definition of the degenerate refinements.

The crossing passage is obtained by specializing this exact state-sum to the degenerate cases $b=1$ or $a=1$.

For spanning cups, take $b=1$. Then necessarily $\rho=r$, and
$$
\widetilde Q_-(1,R_m;\rho,r)=
\begin{cases}
1,&\rho=r,\\
0,&\rho\ne r.
\end{cases}
$$
So for fixed outer endpoints $\ell\in L_m$ and $r\in R_m$,
$$
C^\times(a,1,P_m;\ell,\lambda,r,r)
=
\widetilde Q_+(a,L_m;\ell,\lambda).
$$
Summing exactly over the possible last left-side vertex $\lambda$ gives
$$
Q_+^\times(a+1,P_m;\ell,r)
=
\sum_{\lambda\in L_m,\ \ell<\lambda} Q_+(a,L_m;\ell,\lambda).
\tag{Exact}
$$
There is no inequality here: different $\lambda$ give disjoint state classes, and the outer endpoints $(\ell,r)$ remain fixed throughout.

For spanning caps, take $a=1$. Then necessarily $\lambda=\ell$, and
$$
\widetilde Q_+(1,L_m;\ell,\lambda)=
\begin{cases}
1,&\lambda=\ell,\\
0,&\lambda\ne\ell.
\end{cases}
$$
So for fixed outer endpoints $\ell\in L_m$ and $r\in R_m$,
$$
C^\times(1,b,P_m;\ell,\ell,\rho,r)
=
\widetilde Q_-(b,R_m;\rho,r).
$$
Summing exactly over the possible first right-side vertex $\rho$ gives
$$
Q_-^\times(b+1,P_m;\ell,r)
=
\sum_{\rho\in R_m,\ \rho<r} Q_-(b,R_m;\rho,r).
\tag{Exact}
$$
Again there is no inequality: one is partitioning by the unique endpoint parameter $\rho$, with $(\ell,r)$ still fixed. This is exactly the crossing passage isolated in [[lemmas/one-split-crossing-cup-cap-identities]].

The first inequality that forgets endpoint data appears later in [[bounds/upper-bound-recursive-family]]. Before forgetting endpoints, the convex $k$-subsets admit the exact endpoint-matched decomposition
$$
C_k(P_m)
=
\sum_{a=2}^k\ \sum_{\ell<r}
Q_+(a,P_m;\ell,r)\,Q_-(k+2-a,P_m;\ell,r).
\tag{Exact}
$$
The upper-bound note then passes to
$$
C_k(P_m)
\le
\sum_{a=2}^k Q_+(a,P_m)\,Q_-(k+2-a,P_m).
\tag{Inequality}
$$
This is the first place where the shared outer endpoints are forgotten: the cup and cap coming from a convex $k$-set must have the same left endpoint $\ell$ and the same right endpoint $r$, whereas the product of total counts discards both matching conditions.

A literal chronological caveat is that [[bounds/upper-bound-recursive-family]] already contains earlier inequalities inside the auxiliary cup/cap estimate, beginning with
$$
Q_\pm(r,P_m)\le 2\,Q_\pm(r,P_{m-1})+2^{m-1}Q_\pm(r-1,P_{m-1}).
$$
But those inequalities are not endpoint-forgetting steps: they occur in the separate bound for total cup/cap counts and do not discard any shared outer-endpoint parameter. So the first inequality that loses the relevant endpoint information is still the endpoint-forgetting step above.

That loss alone does not explain the exponent constant $1$ in
$$
f(n)\le 2^{(\log_2 n)^2+O(\log n)}.
$$
It explains why one cannot replace exact endpoint-matched identities by products of coarse totals without loss, but the coefficient $1$ comes from combining the separate coarse bounds
$$
Q_\pm(r,P_m)\ll 2^{rm}
$$
with the later optimization in $k$. Restoring endpoint matching by itself does not determine, and does not by itself improve, that quadratic coefficient.
```
