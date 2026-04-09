---
call_num: 1
label: worker_31_0
model: gpt-5.4
elapsed_ms: 265614
input_tokens: 52397
output_tokens: 14336
cache_read_tokens: 44288
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

Use [[lemmas/one-split-fixed-state-recurrence]], [[lemmas/one-split-crossing-cup-cap-identities]], and [[lemmas/one-split-structure-spanning-convex-subsets]].

Work on exactly one task: reconcile the apparent cup/cap convention mismatch between the stored fixed-state note and the stored crossing note.

Deliverable:
Produce a short repo-ready package that does all of the following:
1. Extract the exact displayed formulas/conventions used in the two stored notes, with no reinterpretation.
2. Decide whether the clash is:
   - a genuine mathematical error in one item, or
   - only a notation/label mismatch that can be repaired cleanly.
3. Identify precisely which repo item(s) must be changed.
4. Provide repo-ready replacement markdown for every affected item, or, if neither item is mathematically wrong, provide a repo-ready reconciliation note that makes the translation between conventions explicit.

Requirements:
- Keep the task narrowly focused on convention reconciliation only.
- Be explicit about which formulas are exact identities.
- Use [[lemmas/one-split-structure-spanning-convex-subsets]] only to determine the canonical side/type assignment if needed.
- Do not do asymptotics, new proof strategy, literature, Lean, or the information-loss note yet.
- The output should be ready for direct storage via `write_items`.

Suitable slugs:
- `status/one-split-convention-audit`
- plus any corrected lemma slugs if replacements are needed.



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

## [[lemmas/one-split-structure-spanning-convex-subsets]]

Summary: Under left-right separation plus the two high-above secant conditions, any convex subset meeting both sides of a split decomposes uniquely as a left cap and a right cup, with endpoint state $(\ell,\lambda,\rho,r)$.

Let
$$
P=L\sqcup R
$$
be a finite planar point set. After a sufficiently small generic rotation, assume all points of $P$ have distinct $x$-coordinates, and that:

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
Equivalently, the points of $S\cap R$ are exactly the $R$-vertices on $U(S)$, and the points of $S\cap L$ are exactly the $L$-vertices on $D(S)$. Hence $S\cap R$ forms a cup with endpoints $(\rho,r)$, and $S\cap L$ forms a cap with endpoints $(\ell,\lambda)$.

In particular,
$$
S=(\text{cap in }L\text{ with endpoints }(\ell,\lambda))
\sqcup
(\text{cup in }R\text{ with endpoints }(\rho,r)),
$$
with the degenerate cases $\ell=\lambda$ and $\rho=r$ allowed.

**Proof.** By (1), every point of $L$ has smaller $x$-coordinate than every point of $R$. Since $S$ meets both halves, its leftmost point lies in $L$ and its rightmost point lies in $R$, so $\ell\in L$ and $r\in R$.

Because all $x$-coordinates are distinct, each hull chain $U(S)$ and $D(S)$ is strictly monotone in $x$. Hence on either chain every vertex from $L$ appears before every vertex from $R$.

Suppose $U(S)$ contains at least two vertices from $L$. Let $p,q$ be the last two such vertices along $U(S)$ from left to right. They are consecutive on $U(S)$: any vertex between them on that chain would have $x$-coordinate between those of $p$ and $q$, hence by the left-right separation would also lie in $L$, contradicting the choice of $p,q$ as the last two $L$-vertices. Since $pq$ is an edge of the upper hull of $S$, every point of $S$ lies on or below the line through $p,q$. But $p,q\in L$, so by (2) every point of $R$, hence every point of $S\cap R$, lies strictly above that line. This contradicts $S\cap R\neq\varnothing$. Therefore $U(S)$ contains at most one vertex from $L$, and since $\ell\in U(S)\cap L$, it contains exactly one such vertex, namely $\ell$.

The lower-hull statement is symmetric. If $D(S)$ contained at least two vertices from $R$, let $p,q$ be the first two such vertices along $D(S)$ from left to right. Again they are consecutive on $D(S)$, because any intermediate vertex would also lie in $R$. Since $pq$ is an edge of the lower hull, every point of $S$ lies on or above the line through $p,q$. But $p,q\in R$, so by (3) every point of $L$, hence every point of $S\cap L$, lies strictly below that line, contradiction. Thus $D(S)$ contains exactly one vertex from $R$, namely $r$.

Now use the endpoint-aware hull decomposition: every non-endpoint vertex of a set in convex position lies on exactly one of the two chains $U(S),D(S)$, while the common endpoints $\ell,r$ lie on both. Since the only $R$-vertex on $D(S)$ is the endpoint $r$, every point of $S\cap R\setminus\{r\}$ lies on $U(S)$. Hence all points of $S\cap R$ occur on $U(S)$, and by $x$-monotonicity they appear there exactly in increasing $x$-order, from $\rho$ to $r$. This gives
$$
U(S)=\ell,u_1,\dots,u_t.
$$
Similarly, since the only $L$-vertex on $U(S)$ is the endpoint $\ell$, every point of $S\cap L\setminus\{\ell\}$ lies on $D(S)$, so the points of $S\cap L$ appear on $D(S)$ exactly in increasing $x$-order from $\ell$ to $\lambda$, giving
$$
D(S)=v_1,\dots,v_s,r.
$$
The cap-cup decomposition follows immediately. $\square$

For a later recurrence, the natural endpoint/state data is
$$
(\ell,\lambda,\rho,r),
$$
equivalently a left-cap state indexed by $(\ell,\lambda)$ together with a right-cup state indexed by $(\rho,r)$. The outer entries $\ell$ and $r$ are the global leftmost and rightmost points of the spanning convex set, while $\lambda$ and $\rho$ record the terminal vertices of the left and right local chains at the split. Thus this state keeps exactly the global-endpoint information lost by aggregate cup/cap totals such as $Q_+$ and $Q_-$.


======== RESPONSE ========

Package ready for `write_items` is below. The fixed-state note needs no change.

`status/one-split-convention-audit`
```markdown
Summary: The stored fixed-state note and the stored crossing note use opposite local cup/cap assignments. Using the displayed hull-chain formulas from [[lemmas/one-split-structure-spanning-convex-subsets]], the canonical assignment is left cup and right cap. Hence the fixed-state note is consistent, while the crossing note is mathematically wrong as written. The structure note also has its concluding cup/cap labels reversed and should be corrected at the same time.

## Exact stored formulas and conventions

From [[lemmas/one-split-fixed-state-recurrence]], the displayed local counts are
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
Its proposition is the exact identity
$$
C^\times(a,b,P;\ell,\lambda,\rho,r)
=
\widetilde Q_+(a,L;\ell,\lambda)\,\widetilde Q_-(b,R;\rho,r).
$$
The note states explicitly: the local quantities are a left cup count and a right cap count.

From [[lemmas/one-split-crossing-cup-cap-identities]], the displayed crossing identities are
$$
Q_+^\times(t+1,P;\ell,r)=\sum_{\rho\in R,\ \rho<r} Q_+(t,R;\rho,r),
$$
and
$$
Q_-^\times(t+1,P;\ell,r)=\sum_{\lambda\in L,\ \ell<\lambda} Q_-(t,L;\ell,\lambda).
$$
Its proof states that
$$
S\cap L\text{ is a cap with endpoints }(\ell,\lambda),\qquad
S\cap R\text{ is a cup with endpoints }(\rho,r).
$$

## Canonical assignment from the structure note

Use only the displayed hull formulas from [[lemmas/one-split-structure-spanning-convex-subsets]]:
$$
U(S)=\ell,u_1,\dots,u_t,\qquad D(S)=v_1,\dots,v_s,r.
$$
With the fixed convention
$$
Q_+:\text{ consecutive slopes strictly increasing},\qquad
Q_-:\text{ consecutive slopes strictly decreasing},
$$
the lower chain gives a cup and the upper chain gives a cap. Therefore these displayed formulas force
$$
S\cap L\text{ to be a cup with endpoints }(\ell,\lambda),
$$
and
$$
S\cap R\text{ to be a cap with endpoints }(\rho,r).
$$

## Decision

This is a genuine mathematical error, not only a notation mismatch. Once $Q_+$ and $Q_-$ are fixed by slope monotonicity, the crossing note's local side/type assignment and its two exact counting identities are reversed.

The correct exact identities are
$$
Q_+^\times(t+1,P;\ell,r)=\sum_{\lambda\in L,\ \ell<\lambda} Q_+(t,L;\ell,\lambda),
$$
and
$$
Q_-^\times(t+1,P;\ell,r)=\sum_{\rho\in R,\ \rho<r} Q_-(t,R;\rho,r).
$$
Equivalently:
- every spanning cup has exactly one right point, namely $r$;
- every spanning cap has exactly one left point, namely $\ell$.

## Items to change

1. Replace [[lemmas/one-split-crossing-cup-cap-identities]].
2. Replace [[lemmas/one-split-structure-spanning-convex-subsets]] so its concluding labels match its displayed hull formulas.
3. Leave [[lemmas/one-split-fixed-state-recurrence]] unchanged.
```

`lemmas/one-split-crossing-cup-cap-identities`
```markdown
Summary: Under the one-split hypotheses, every spanning cup has exactly one right point and every spanning cap exactly one left point, yielding exact endpoint-refined crossing identities.

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
S\cap R=\{r\}.
$$
So every spanning cup has exactly one point in the right half, namely its global right endpoint.

2. If $S\subseteq P$ is a spanning cap with global endpoints $(\ell,r)$, then
$$
S\cap L=\{\ell\}.
$$
So every spanning cap has exactly one point in the left half, namely its global left endpoint.

3. Consequently, for every $\ell\in L$, $r\in R$, and $t\ge 2$,
$$
Q_+^\times(t+1,P;\ell,r)=\sum_{\lambda\in L,\ \ell<\lambda} Q_+(t,L;\ell,\lambda),
$$
and
$$
Q_-^\times(t+1,P;\ell,r)=\sum_{\rho\in R,\ \rho<r} Q_-(t,R;\rho,r).
$$

Here $\ell<\lambda$ and $\rho<r$ refer to the left-to-right $x$-order.

**Proof.**
Let $S\subseteq P$ be spanning, and use the notation of [[lemmas/one-split-structure-spanning-convex-subsets]]:
$$
\ell=\min_x S,\qquad r=\max_x S,
$$
$$
\lambda=\max_x(S\cap L),\qquad \rho=\min_x(S\cap R).
$$
That lemma shows that $S\cap L$ is a cup with endpoints $(\ell,\lambda)$, $S\cap R$ is a cap with endpoints $(\rho,r)$, and if
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

Now suppose that $S$ is itself a cup. Then its upper hull has only the two global endpoints $\ell,r$. Comparing with
$$
U(S)=\ell,u_1,\dots,u_t
$$
forces $t=1$, hence $\rho=r$ and
$$
S\cap R=\{r\}.
$$
This proves (1).

The proof of (2) is dual. If $S$ is a spanning cap, then its lower hull has only the two global endpoints $\ell,r$. Comparing with
$$
D(S)=v_1,\dots,v_s,r
$$
forces $s=1$, hence $\lambda=\ell$ and
$$
S\cap L=\{\ell\}.
$$

For the counting identities, fix $\ell\in L$, $r\in R$, and $t\ge 2$.

For cups, define
$$
\Phi(S)=S\cap L.
$$
By (1), this gives a map from spanning $(t+1)$-cups with endpoints $(\ell,r)$ into the disjoint union over $\lambda\in L$ with $\ell<\lambda$ of the sets of $t$-cups in $L$ with endpoints $(\ell,\lambda)$. It is injective because
$$
S=\Phi(S)\sqcup \{r\}.
$$

To prove surjectivity, let
$$
T=\{v_1=\ell<v_2<\cdots<v_t=\lambda\}\subseteq L
$$
be a $t$-cup, and set
$$
S:=T\cup\{r\}.
$$
Since $T$ is a cup,
$$
\operatorname{slope}(v_1,v_2)<\operatorname{slope}(v_2,v_3)<\cdots<\operatorname{slope}(v_{t-1},v_t).
$$
Also, $v_{t-1},v_t\in L$, so the line through $v_{t-1},v_t$ lies strictly below every point of $R$, in particular below $r$. Because $x_{v_{t-1}}<x_{v_t}<x_r$, this is equivalent to
$$
\operatorname{slope}(v_{t-1},v_t)<\operatorname{slope}(v_t,r).
$$
Hence
$$
\operatorname{slope}(v_1,v_2)
<
\cdots
<
\operatorname{slope}(v_{t-1},v_t)
<
\operatorname{slope}(v_t,r),
$$
so
$$
v_1,\dots,v_t,r
$$
is a $(t+1)$-cup with endpoints $(\ell,r)$. Thus $\Phi$ is bijective, and taking cardinalities gives
$$
Q_+^\times(t+1,P;\ell,r)=\sum_{\lambda\in L,\ \ell<\lambda} Q_+(t,L;\ell,\lambda).
$$

The cap identity is dual. Let
$$
T=\{u_1=\rho<u_2<\cdots<u_t=r\}\subseteq R
$$
be a $t$-cap, and set
$$
S:=\{\ell\}\cup T.
$$
Since $T$ is a cap,
$$
\operatorname{slope}(u_1,u_2)>\operatorname{slope}(u_2,u_3)>\cdots>\operatorname{slope}(u_{t-1},u_t).
$$
Also, $u_1,u_2\in R$, so the line through $u_1,u_2$ lies strictly above every point of $L$, in particular above $\ell$. Because $x_\ell<x_{u_1}<x_{u_2}$, this is equivalent to
$$
\operatorname{slope}(\ell,u_1)>\operatorname{slope}(u_1,u_2).
$$
Hence
$$
\operatorname{slope}(\ell,u_1)>
\operatorname{slope}(u_1,u_2)>
\cdots>
\operatorname{slope}(u_{t-1},u_t),
$$
so
$$
\ell,u_1,\dots,u_t
$$
is a $(t+1)$-cap with endpoints $(\ell,r)$. Thus
$$
Q_-^\times(t+1,P;\ell,r)=\sum_{\rho\in R,\ \rho<r} Q_-(t,R;\rho,r).
$$

Endpoint matching is enforced because the global outer endpoints $(\ell,r)$ are fixed, while the split lemma recovers uniquely the last left-side vertex $\lambda$ for cups and the first right-side vertex $\rho$ for caps. $\square$
```

`lemmas/one-split-structure-spanning-convex-subsets`
```markdown
Summary: Under left-right separation plus the two high-above secant conditions, any convex subset meeting both sides of a split decomposes uniquely as a left cup and a right cap, with endpoint state $(\ell,\lambda,\rho,r)$.

Let
$$
P=L\sqcup R
$$
be a finite planar point set. After a sufficiently small generic rotation, assume all points of $P$ have distinct $x$-coordinates, and that:

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
Equivalently, the points of $S\cap R$ are exactly the $R$-vertices on $U(S)$, and the points of $S\cap L$ are exactly the $L$-vertices on $D(S)$. Hence $S\cap R$ forms a cap with endpoints $(\rho,r)$, and $S\cap L$ forms a cup with endpoints $(\ell,\lambda)$.

In particular,
$$
S=(\text{cup in }L\text{ with endpoints }(\ell,\lambda))
\sqcup
(\text{cap in }R\text{ with endpoints }(\rho,r)),
$$
with the degenerate cases $\ell=\lambda$ and $\rho=r$ allowed.

**Proof.** By (1), every point of $L$ has smaller $x$-coordinate than every point of $R$. Since $S$ meets both halves, its leftmost point lies in $L$ and its rightmost point lies in $R$, so $\ell\in L$ and $r\in R$.

Because all $x$-coordinates are distinct, each hull chain $U(S)$ and $D(S)$ is strictly monotone in $x$. Hence on either chain every vertex from $L$ appears before every vertex from $R$.

Suppose $U(S)$ contains at least two vertices from $L$. Let $p,q$ be the last two such vertices along $U(S)$ from left to right. They are consecutive on $U(S)$: any vertex between them on that chain would have $x$-coordinate between those of $p$ and $q$, hence by the left-right separation would also lie in $L$, contradicting the choice of $p,q$ as the last two $L$-vertices. Since $pq$ is an edge of the upper hull of $S$, every point of $S$ lies on or below the line through $p,q$. But $p,q\in L$, so by (2) every point of $R$, hence every point of $S\cap R$, lies strictly above that line. This contradicts $S\cap R\neq\varnothing$. Therefore $U(S)$ contains at most one vertex from $L$, and since $\ell\in U(S)\cap L$, it contains exactly one such vertex, namely $\ell$.

The lower-hull statement is symmetric. If $D(S)$ contained at least two vertices from $R$, let $p,q$ be the first two such vertices along $D(S)$ from left to right. Again they are consecutive on $D(S)$, because any intermediate vertex would also lie in $R$. Since $pq$ is an edge of the lower hull, every point of $S$ lies on or above the line through $p,q$. But $p,q\in R$, so by (3) every point of $L$, hence every point of $S\cap L$, lies strictly below that line, contradiction. Thus $D(S)$ contains exactly one vertex from $R$, namely $r$.

Now use the endpoint-aware hull decomposition: every non-endpoint vertex of a set in convex position lies on exactly one of the two chains $U(S),D(S)$, while the common endpoints $\ell,r$ lie on both. Since the only $R$-vertex on $D(S)$ is the endpoint $r$, every point of $S\cap R\setminus\{r\}$ lies on $U(S)$. Hence all points of $S\cap R$ occur on $U(S)$, and by $x$-monotonicity they appear there exactly in increasing $x$-order, from $\rho$ to $r$. This gives
$$
U(S)=\ell,u_1,\dots,u_t.
$$
Similarly, since the only $L$-vertex on $U(S)$ is the endpoint $\ell$, every point of $S\cap L\setminus\{\ell\}$ lies on $D(S)$, so the points of $S\cap L$ appear on $D(S)$ exactly in increasing $x$-order from $\ell$ to $\lambda$, giving
$$
D(S)=v_1,\dots,v_s,r.
$$
The cup-cap decomposition follows immediately. $\square$

For a later recurrence, the natural endpoint/state data is
$$
(\ell,\lambda,\rho,r),
$$
equivalently a left-cup state indexed by $(\ell,\lambda)$ together with a right-cap state indexed by $(\rho,r)$. The outer entries $\ell$ and $r$ are the global leftmost and rightmost points of the spanning convex set, while $\lambda$ and $\rho$ record the terminal vertices of the left and right local chains at the split. Thus this state keeps exactly the global-endpoint information lost by aggregate cup/cap totals such as $Q_+$ and $Q_-$.
```
