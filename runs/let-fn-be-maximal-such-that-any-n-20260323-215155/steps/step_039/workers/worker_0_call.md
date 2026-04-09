---
call_num: 9
label: worker_39_0
model: gpt-5.4
elapsed_ms: 372268
input_tokens: 220950
output_tokens: 18867
cache_read_tokens: 209152
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

Use [[lemmas/ternary-one-split-structure]] as the main input, with [[bounds/upper-bound-recursive-family]] and [[status/fixed-lag-separated-recursions-obstruction]] only as motivation/background.

Work on exactly one task: define the balanced ternary separated recursion and derive the exact recurrence/state propagation forced by the new ternary one-split lemma. Then determine whether one explicit top-scale contribution already gives an obstruction comparable to or worse than coefficient $1$, or whether ternary recursion remains genuinely open after this local classification.

Deliverable:
1. Define a precise balanced ternary family $T_m$.
   - Natural target: three child copies of $T_{m-1}$ in left-middle-right ternary separated position.
   - If one extra geometric normalization is needed so the bridge-region counts are well-defined recursively, state it explicitly.
2. Derive the exact counting decomposition for convex subsets of $T_m$.
   - Separate subsets contained in one child, spanning exactly two children, and spanning all three children.
   - Make explicit what state variables must be tracked recursively.
   - Distinguish exact identities from inequalities.
3. Decide one of the following, with justification:
   - an explicit top-split term already forces a quadratic coefficient at least $1$ (or larger), so balanced ternary recursion is already obstructed;
   - the exact recurrence closes but introduces new bridge-state quantities that remain nontrivial and keep ternary genuinely alive;
   - or the first exact place where the recursion fails to close in a manageable state space.
4. Output repo-ready markdown with a `Summary:` line.
   - If clearly obstructed, suitable slug: `status/ternary-separated-recursion-obstruction`.
   - If the main result is an exact but not yet resolved recurrence/state description, suitable slug: `attempts/alternative-construction-balanced-ternary-split`.

Requirements:
- Focus on balanced ternary recursion only.
- Build directly from [[lemmas/ternary-one-split-structure]]; do not redo the local geometry from scratch.
- Do not revisit binary endpoint matching or binary lag variants.
- Do not use literature or Lean.
- Be explicit about the minimal recursive state: if bridge counts force extra endpoint-dependent data, say exactly what it is.
- If you obtain only a lower-bound obstruction from one term of an exact recurrence, isolate that term cleanly and state that the conclusion is an inequality rather than an exact count.



# Referenced Materials

## [[lemmas/ternary-one-split-structure]]

Summary: In a clean left-middle-right ternary split with the vertical-dual one-split orientation, every convex subset meeting more than one block is classified exactly as follows: for any two-block span, the earlier block contributes a cap and the later block contributes a cup; for a three-block span, the left block is a cap, the right block is a cup, and the middle block contributes at most one upper bridge point and at most one lower bridge point, determined by the endpoint-dependent bridge lines $\lambda r$ and $\ell\rho$. All formulas below are exact identities.

Let
$$
P=L\sqcup M\sqcup R
$$
be a finite planar point set in general position. After a sufficiently small generic rotation, assume all $x$-coordinates are distinct and
$$
x(L)<x(M)<x(R).
$$

We use the following precise ternary separated-position hypothesis.

## Ternary separated position

Assume:

1. every line through two points of $L$ lies strictly above every point of $M\cup R$;
2. every line through two points of $M$ lies strictly below every point of $L$ and strictly above every point of $R$;
3. every line through two points of $R$ lies strictly below every point of $L\cup M$.

Equivalently: for each earlier-later pair of blocks, every secant of the earlier block lies strictly above the later block, and every secant of the later block lies strictly below the earlier block.

For a set $S$ in convex position, write $U(S)$ and $D(S)$ for the upper and lower hull chains, both listed from left to right. A chain is a cup if its consecutive slopes are strictly increasing, and a cap if its consecutive slopes are strictly decreasing.

For points $p,q\in X$ with $x(p)\le x(q)$, let $Q_-(a,X;p,q)$ denote the number of $a$-point caps in $X$ with left endpoint $p$ and right endpoint $q$, and let $Q_+(a,X;p,q)$ denote the analogous number of endpoint-refined cups.

## Lemma

Let $S\subseteq P$ be in convex position and assume that $S$ meets more than one block.

### 1. Subsets meeting exactly two blocks

If $S$ meets exactly two blocks, say an earlier block $X$ and a later block $Y$, then:

- the points of $S\cap X$ are exactly the $X$-vertices on $U(S)$, hence $S\cap X$ is a cap in $X$;
- the points of $S\cap Y$ are exactly the $Y$-vertices on $D(S)$, hence $S\cap Y$ is a cup in $Y$.

So, exactly:

- for $L\cup M$: the $L$-part is a cap and the $M$-part is a cup;
- for $M\cup R$: the $M$-part is a cap and the $R$-part is a cup;
- for $L\cup R$: the $L$-part is a cap and the $R$-part is a cup.

These are exact structural identities.

### 2. Subsets meeting all three blocks

Assume now
$$
S\cap L\neq\varnothing,\qquad S\cap M\neq\varnothing,\qquad S\cap R\neq\varnothing.
$$
Write
$$
\ell=\min_x S\in L,\qquad r=\max_x S\in R,
$$
$$
\lambda=\max_x(S\cap L),\qquad \rho=\min_x(S\cap R),
$$
and list
$$
S\cap L=\{v_1=\ell<\cdots<v_a=\lambda\},\qquad
S\cap R=\{u_1=\rho<\cdots<u_b=r\}.
$$

Then:

1. $D(S)$ contains exactly one vertex from $L$, namely $\ell$.
2. $U(S)$ contains exactly one vertex from $R$, namely $r$.
3. $U(S)$ contains at most one vertex from $M$.
4. $D(S)$ contains at most one vertex from $M$.

Hence
$$
U(S)=v_1,\dots,v_a,\;m^\uparrow,\;r
$$
with $m^\uparrow$ omitted if $U(S)\cap M=\varnothing$, and
$$
D(S)=\ell,\;m^\downarrow,\;u_1,\dots,u_b
$$
with $m^\downarrow$ omitted if $D(S)\cap M=\varnothing$.

Consequently:

- $S\cap L$ is a cap in $L$ with endpoints $(\ell,\lambda)$;
- $S\cap R$ is a cup in $R$ with endpoints $(\rho,r)$;
- $|S\cap M|\in\{1,2\}$;
- if $|S\cap M|=2$, then one middle point lies on $U(S)$ and one lies on $D(S)$.

So the middle block is not a cup/cap chain. Its exact local type is an upper bridge point together with a lower bridge point, each optional but not both absent.

Define the bridge regions
$$
M^\uparrow(\lambda,r):=\{m\in M:\text{$m$ lies strictly above the line }\lambda r\},
$$
$$
M^\downarrow(\ell,\rho):=\{m\in M:\text{$m$ lies strictly below the line }\ell\rho\}.
$$
Then
$$
m^\uparrow\in M^\uparrow(\lambda,r),\qquad
m^\downarrow\in M^\downarrow(\ell,\rho),
$$
and the two regions are disjoint.

Conversely, let
$$
A=\{v_1=\ell<\cdots<v_a=\lambda\}\subseteq L
$$
be any cap in $L$, and let
$$
B=\{u_1=\rho<\cdots<u_b=r\}\subseteq R
$$
be any cup in $R$. Choose
$$
m^\uparrow\in M^\uparrow(\lambda,r)\cup\{\bot\},\qquad
m^\downarrow\in M^\downarrow(\ell,\rho)\cup\{\bot\},
$$
not both equal to $\bot$. Then
$$
S:=A\cup B\cup\bigl(\{m^\uparrow\}\setminus\{\bot\}\bigr)\cup\bigl(\{m^\downarrow\}\setminus\{\bot\}\bigr)
$$
is in convex position, meets all three blocks, and has hull chains exactly
$$
U(S)=A,\;m^\uparrow,\;r,
\qquad
D(S)=\ell,\;m^\downarrow,\;B.
$$

Thus the three-block classification is exact.

## Proof

The two-block statement is the vertical dual of the binary one-split structure lemma. If an earlier block $X$ and a later block $Y$ are in the present orientation, then $U(S)$ cannot contain two vertices of $Y$, because an upper-hull edge through two points of $Y$ would have to lie above all of $S$, while every point of $X$ lies strictly above every $Y$-secant. Dually, $D(S)$ cannot contain two vertices of $X$, because a lower-hull edge through two points of $X$ would have to lie below all of $S$, while every point of $Y$ lies strictly below every $X$-secant. Hence the earlier block lies on the upper hull and forms a cap, while the later block lies on the lower hull and forms a cup.

Now assume $S$ meets all three blocks.

If $D(S)$ contained two vertices of $L$, then the first two such vertices on $D(S)$ would be consecutive on $D(S)$. Since they form a lower-hull edge, all points of $S$ must lie on or above their line. But every point of $M\cup R$ lies strictly below every $L$-secant, contradiction. So $D(S)$ contains exactly one $L$-vertex, namely $\ell$.

Dually, $U(S)$ contains exactly one $R$-vertex, namely $r$.

If $U(S)$ contained two vertices of $M$, then the last two such vertices on $U(S)$ would be consecutive on $U(S)$, and their line would have to lie above all of $S$. But every point of $L$ lies strictly above every $M$-secant, contradiction. Hence $U(S)$ contains at most one $M$-vertex.

Similarly, if $D(S)$ contained two vertices of $M$, then the first two such vertices on $D(S)$ would be consecutive on $D(S)$, and their line would have to lie below all of $S$. But every point of $R$ lies strictly below every $M$-secant, contradiction. Hence $D(S)$ contains at most one $M$-vertex.

Therefore all points of $S\cap L\setminus\{\ell\}$ lie on $U(S)$, so $S\cap L$ is a cap, and all points of $S\cap R\setminus\{r\}$ lie on $D(S)$, so $S\cap R$ is a cup. This gives the stated hull formulas.

Set
$$
A:=(S\cap L)\cup(S\cap R).
$$
By the already proved $L$-$R$ two-block case, $A$ is in convex position with upper hull
$$
v_1,\dots,v_a,r
$$
and lower hull
$$
\ell,u_1,\dots,u_b.
$$
Since all points of $M$ lie strictly between the $x$-ranges of $L$ and $R$, the portion of $\partial\operatorname{conv}(A)$ across the $M$-strip is exactly the upper segment $\lambda r$ and the lower segment $\ell\rho$.

Every point of $S\cap M$ is a vertex of $\operatorname{conv}(S)$, hence lies outside $\operatorname{conv}(A)$. So each middle point lies either strictly above $\lambda r$ or strictly below $\ell\rho$. This proves
$$
S\cap M\subseteq M^\uparrow(\lambda,r)\cup M^\downarrow(\ell,\rho).
$$
The two regions are disjoint because $\lambda r$ is the upper boundary and $\ell\rho$ is the lower boundary of $\operatorname{conv}(A)$ across the $M$-strip. Together with the already proved at-most-one-on-each-hull statement, this yields $|S\cap M|\in\{1,2\}$ and the exact upper/lower placement.

For the converse, start from the $L$-$R$ convex set
$$
S_0:=A\cup B.
$$
Its upper hull is $A,r$, and its lower hull is $\ell,B$.

If $m^\uparrow\in M^\uparrow(\lambda,r)$, then $\lambda,m^\uparrow,r$ is a $3$-cap. Indeed, if $a=1$, this is exactly the condition that $m^\uparrow$ lie above $\ell r$. If $a\ge2$, then the last edge of the cap $A$ has slope $\operatorname{slope}(v_{a-1},v_a)$, every point of $M$ lies strictly below the line $v_{a-1}v_a$, so
$$
\operatorname{slope}(v_{a-1},v_a)>\operatorname{slope}(v_a,m^\uparrow),
$$
and $m^\uparrow$ above the line $\lambda r$ gives
$$
\operatorname{slope}(v_a,m^\uparrow)>\operatorname{slope}(m^\uparrow,r).
$$
Hence $A,m^\uparrow,r$ is a cap.

Dually, if $m^\downarrow\in M^\downarrow(\ell,\rho)$, then $\ell,m^\downarrow,B$ is a cup.

So the chosen upper chain is a cap from $\ell$ to $r$, and the chosen lower chain is a cup from $\ell$ to $r$. Therefore all interior vertices of the upper chain lie strictly above the chord $\ell r$, and all interior vertices of the lower chain lie strictly below $\ell r$. The two chains meet only at $\ell$ and $r$, hence form the boundary of a convex polygon whose vertex set is exactly $S$.

This proves the converse. $\square$

## Exact fixed-state formulas

Define
$$
\widetilde Q_-(a,L;\ell,\lambda):=
\begin{cases}
1,& a=1\text{ and }\ell=\lambda,\\
Q_-(a,L;\ell,\lambda),& a\ge2\text{ and }\ell<\lambda,\\
0,&\text{otherwise,}
\end{cases}
$$
and
$$
\widetilde Q_+(b,R;\rho,r):=
\begin{cases}
1,& b=1\text{ and }\rho=r,\\
Q_+(b,R;\rho,r),& b\ge2\text{ and }\rho<r,\\
0,&\text{otherwise.}
\end{cases}
$$
Also set
$$
U_M(\lambda,r):=\bigl|M^\uparrow(\lambda,r)\bigr|,
\qquad
D_M(\ell,\rho):=\bigl|M^\downarrow(\ell,\rho)\bigr|.
$$

### Two-block identities

For each earlier-later pair $(X,Y)\in\{(L,M),(M,R),(L,R)\}$, the endpoint-refined two-block count is exactly
$$
\text{(cap count on $X$)}\times \text{(cup count on $Y$)}.
$$
This is an exact identity.

### Three-block identities

Let
$$
C^{LMR}(a,c,b,P;\ell,\lambda,\rho,r)
$$
denote the number of convex subsets $S\subseteq P$ with
$$
|S\cap L|=a,\qquad |S\cap M|=c,\qquad |S\cap R|=b,
$$
meeting all three blocks and having outer state $(\ell,\lambda,\rho,r)$.

Then:
$$
C^{LMR}(a,1,b,P;\ell,\lambda,\rho,r)
=
\widetilde Q_-(a,L;\ell,\lambda)\,
\widetilde Q_+(b,R;\rho,r)\,
\bigl(U_M(\lambda,r)+D_M(\ell,\rho)\bigr),
$$
$$
C^{LMR}(a,2,b,P;\ell,\lambda,\rho,r)
=
\widetilde Q_-(a,L;\ell,\lambda)\,
\widetilde Q_+(b,R;\rho,r)\,
U_M(\lambda,r)\,D_M(\ell,\rho),
$$
and for every $c\ge3$,
$$
C^{LMR}(a,c,b,P;\ell,\lambda,\rho,r)=0.
$$

These are exact identities, not inequalities.

## Why this is the necessary local step before any ternary recurrence

In the binary split, fixed-state convex subsets factor through two local chain states. In the ternary split, they do not: after fixing the outer cap state $(\ell,\lambda)$ on $L$ and the outer cup state $(\rho,r)$ on $R$, the middle contribution still depends on the endpoint-dependent bridge regions
$$
M^\uparrow(\lambda,r),\qquad M^\downarrow(\ell,\rho).
$$
So any exact ternary recurrence must carry this new bridge data. One cannot write an exact ternary recurrence using only aggregate cup/cap counts on the three blocks.

This note isolates that new local state exactly, without yet attempting any full ternary recursion or any asymptotic counting.


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

## [[status/fixed-lag-separated-recursions-obstruction]]

Summary: For the fixed-lag separated recursion
$$
F_m^{(t)}=F_{m-1}^{(t)}\sqcup F_{m-t}^{(t)} \qquad (t\ge 2),
$$
one explicit top-split term already gives
$$
\limsup_{m\to\infty}\frac{\log_2 g(F_m^{(t)})}{(\log_2 |F_m^{(t)}|)^2}\ge \alpha_t,
\qquad
\alpha_t=\frac{t+1}{2t\log_2\lambda_t},
$$
where $\lambda_t>1$ is the positive root of $\lambda_t^t=\lambda_t^{t-1}+1$. Moreover $\alpha_t>1$ for every fixed $t\ge 2$. Hence no fixed lag can lower the quadratic coefficient below $1$; the whole fixed-lag binary family is obstructed.

Fix $t\ge 2$.

## Definition

Define $F_1^{(t)},\dots,F_t^{(t)}$ to be one-point sets. For $m\ge t+1$, define
$$
F_m^{(t)}=L_m\sqcup R_m,
$$
where $L_m$ is an affine copy of $F_{m-1}^{(t)}$, $R_m$ is an affine copy of $F_{m-t}^{(t)}$, and $(L_m,R_m)$ is in the standard separated position.

Let
$$
N_m:=|F_m^{(t)}|.
$$
Then
$$
N_1=\cdots=N_t=1,
\qquad
N_m=N_{m-1}+N_{m-t}\quad (m\ge t+1).
$$
Let $\lambda_t>1$ be the unique positive root of
$$
x^t-x^{t-1}-1=0.
$$
Then
$$
N_m=\Theta_t(\lambda_t^m),
\qquad
\log_2 N_m=m\log_2\lambda_t+O_t(1).
$$

For $a\ge 1$ define
$$
U_m(a):=Q_+(a,F_m^{(t)}),
\qquad
V_m(a):=Q_-(a,F_m^{(t)}),
$$
and for $k\ge 1$ define
$$
C_m(k):=C_k(F_m^{(t)}).
$$

## Exact Recurrences

For $a\ge 2$ and $m\ge t+1$, the cup counts satisfy the exact identity
$$
U_m(a)=U_{m-1}(a)+U_{m-t}(a)+N_{m-t}U_{m-1}(a-1),
$$
with
$$
U_m(1)=N_m.
$$

For $a\ge 2$ and $m\ge t+1$, the cap counts satisfy the exact identity
$$
V_m(a)=V_{m-1}(a)+V_{m-t}(a)+N_{m-1}V_{m-t}(a-1),
$$
with
$$
V_m(1)=N_m.
$$

For $k\ge 1$ and $m\ge t+1$, the convex-subset counts satisfy the exact identity
$$
C_m(k)=C_{m-1}(k)+C_{m-t}(k)+\sum_{a=1}^{k-1}U_{m-1}(a)V_{m-t}(k-a).
$$

## Maximal Cups

Let
$$
\nu_m:=\max\{a:U_m(a)>0\}.
$$
Then
$$
\nu_1=\cdots=\nu_t=1,
\qquad
\nu_m=\nu_{m-1}+1 \quad (m\ge t+1),
$$
hence exactly
$$
\nu_m=m-t+1 \qquad (m\ge t).
$$

Set
$$
U_m^*:=U_m(\nu_m).
$$
For $m\ge t+1$, the maximal cups are exactly the spanning ones, so
$$
U_m^*=N_{m-t}U_{m-1}^*
$$
is exact. Since $U_t^*=1$, it follows that
$$
U_m^*=\prod_{j=1}^{m-t}N_j
\qquad (m\ge t).
$$

## Maximal Caps

Let
$$
v_m:=\max\{a:V_m(a)>0\}.
$$
Then
$$
v_1=\cdots=v_t=1,
\qquad
v_m=\max\bigl(v_{m-1},1+v_{m-t}\bigr)\quad (m\ge t+1),
$$
so exactly
$$
v_m=1+\left\lfloor\frac{m-1}{t}\right\rfloor.
$$

The maximal cap length increases only at depths $m=qt+1$. Define
$$
W_q:=V_{qt+1}(q+1).
$$
Since the maximal cap at depth $qt+1$ must be spanning, one gets the exact identity
$$
W_q=N_{qt}W_{q-1}
$$
for $q\ge 1$, with $W_0=1$. Therefore
$$
W_q=\prod_{i=1}^q N_{it}.
$$

## Explicit Top-Split Obstruction

Take
$$
m_q:=(q+1)t+1.
$$
Then
$$
m_q-1=(q+1)t,
\qquad
m_q-t=qt+1.
$$
In the exact recurrence for $C_{m_q}(k)$, keep only the single term
$$
a=\nu_{m_q-1}=qt+1,
\qquad
k-a=v_{m_q-t}=q+1.
$$
This gives the inequality
$$
C_{m_q}\bigl(q(t+1)+2\bigr)
\ge
U_{(q+1)t}^*\,W_q
=
\left(\prod_{j=1}^{qt}N_j\right)
\left(\prod_{i=1}^q N_{it}\right).
$$

Using $N_r=\Theta_t(\lambda_t^r)$,
$$
\log_2 U_{(q+1)t}^*
=(\log_2\lambda_t)\sum_{j=1}^{qt}j+O_t(q),
$$
and
$$
\log_2 W_q
=(\log_2\lambda_t)\sum_{i=1}^q it+O_t(q).
$$
Therefore
$$
\log_2 g(F_{m_q}^{(t)})
\ge
(\log_2\lambda_t)\left(\sum_{j=1}^{qt}j+\sum_{i=1}^q it\right)+O_t(q).
$$
Since
$$
\sum_{j=1}^{qt}j+\sum_{i=1}^q it
=
\frac{qt(qt+1)}2+\frac{tq(q+1)}2
=
\frac{t(t+1)}2\,q^2+O_t(q),
$$
and
$$
m_q=tq+O_t(1),
$$
this becomes
$$
\log_2 g(F_{m_q}^{(t)})
\ge
\left(\frac{t+1}{2t}\log_2\lambda_t\right)m_q^2+O_t(m_q).
$$
Using
$$
\log_2 N_{m_q}=m_q\log_2\lambda_t+O_t(1),
$$
we obtain
$$
g(F_{m_q}^{(t)})
\ge
2^{\left(\alpha_t+o(1)\right)(\log_2 N_{m_q})^2},
\qquad
\alpha_t:=\frac{t+1}{2t\log_2\lambda_t}.
$$
Hence
$$
\limsup_{m\to\infty}\frac{\log_2 g(F_m^{(t)})}{(\log_2 N_m)^2}\ge \alpha_t.
$$

## Why $\alpha_t>1$

For $t=2$, $\lambda_2=\varphi$, and $\log_2\varphi<\frac34$, so
$$
\alpha_2=\frac{3}{4\log_2\varphi}>1.
$$

For $t=3$, one has $\lambda_3<\frac32$ and $\log_2(3/2)<\frac23$, so
$$
\alpha_3=\frac{4}{6\log_2\lambda_3}>1.
$$

For every $t\ge 4$,
$$
(\sqrt2)^t-(\sqrt2)^{t-1}-1>0,
$$
so $\lambda_t<\sqrt2$, hence $\log_2\lambda_t<\frac12$. Therefore
$$
\alpha_t=\frac{t+1}{2t\log_2\lambda_t}
>
\frac{t+1}{2t\cdot (1/2)}
=
\frac{t+1}{t}
>1.
$$

## Conclusion

For every fixed $t\ge 2$, the separated recursion
$$
F_m^{(t)}=F_{m-1}^{(t)}\sqcup F_{m-t}^{(t)}
$$
has an explicit top-split contribution forcing a quadratic coefficient strictly larger than $1$. So increasing the lag does not help inside the binary separated paradigm. The next productive direction is to leave binary recursions entirely.


======== RESPONSE ========

I could not write the file because the sandbox tools are failing with `bwrap: Unknown option --argv0`. The note below is ready to save as `attempts/alternative-construction-balanced-ternary-split.md`.

```markdown
Summary: The balanced ternary family admits an exact convex-subset recursion only after enlarging the state to endpoint-refined cap/cup counts together with parent-scale bridge functions \(U_m,D_m\); the first three-block term is exact in that enlarged state, but no single top-split term from the ternary one-split lemma alone forces quadratic coefficient at least \(1\).

# Balanced ternary separated recursion

We use [[lemmas/ternary-one-split-structure]] as the local input throughout.

## Definition

Fix affine contractions
\[
\Phi_L,\Phi_M,\Phi_R:\mathbb R^2\to\mathbb R^2
\]
such that for every finite set \(X\) in general position, after one fixed small generic rotation the three images
\[
\Phi_L(X),\qquad \Phi_M(X),\qquad \Phi_R(X)
\]
have disjoint \(x\)-ranges in the order
\[
x(\Phi_L(X))<x(\Phi_M(X))<x(\Phi_R(X))
\]
and satisfy the ternary separated-position hypotheses of [[lemmas/ternary-one-split-structure]].

This fixed-template normalization is the only extra geometric normalization needed: it canonically identifies each child with the previous-level model, so the bridge-region counts become recursively well-defined functions of canonical endpoint states.

Let \(T_0\) be a one-point set. For \(m\ge 1\), define
\[
T_m=L_m\sqcup M_m\sqcup R_m
\]
by
\[
L_m=\Phi_L(T_{m-1}),\qquad M_m=\Phi_M(T_{m-1}),\qquad R_m=\Phi_R(T_{m-1}).
\]
Then
\[
|T_m|=3^m.
\]

## Minimal exact state

For endpoint-refined cap/cup counts, write
\[
A_m(a;\ell,\lambda):=\widetilde Q_-(a,T_m;\ell,\lambda),
\qquad
B_m(b;\rho,r):=\widetilde Q_+(b,T_m;\rho,r).
\]

The ternary lemma shows that these do not suffice by themselves: the middle contribution in a three-block convex set depends on endpoint-dependent bridge regions. Thus one must also track
\[
U_m(\lambda,r):=\Bigl|\Bigl\{z\in T_{m-1}:\Phi_M(z)\text{ lies above the line }\Phi_L(\lambda)\Phi_R(r)\Bigr\}\Bigr|,
\]
\[
D_m(\ell,\rho):=\Bigl|\Bigl\{z\in T_{m-1}:\Phi_M(z)\text{ lies below the line }\Phi_L(\ell)\Phi_R(\rho)\Bigr\}\Bigr|.
\]

So the minimal exact recursive state forced by the lemma is
\[
\{A_m(a;\ell,\lambda)\}_{a,\ell,\lambda},\qquad
\{B_m(b;\rho,r)\}_{b,\rho,r},\qquad
\{U_m(\lambda,r)\}_{\lambda,r},\qquad
\{D_m(\ell,\rho)\}_{\ell,\rho}.
\]

No extra joint middle-state is needed: the lemma gives disjoint upper/lower bridge regions, so the exact \(c=2\) count is just the product \(U_m(\lambda,r)D_m(\ell,\rho)\).

## Exact decomposition of convex subsets

Let \(C_m(k)\) be the number of \(k\)-point subsets of \(T_m\) in convex position.

Every convex subset of \(T_m\) belongs to exactly one of the following classes.

### 1. Contained in one child

Exactly
\[
C_m^{(1)}(k)=3\,C_{m-1}(k).
\]

### 2. Spanning exactly two children

For each earlier-later pair \((X,Y)\in\{(L_m,M_m),(M_m,R_m),(L_m,R_m)\}\), the ternary one-split lemma says exactly: the \(X\)-part is a cap and the \(Y\)-part is a cup.

Set
\[
A_{m-1}^{\mathrm{tot}}(a):=\sum_{\ell,\lambda\in T_{m-1}}A_{m-1}(a;\ell,\lambda),
\qquad
B_{m-1}^{\mathrm{tot}}(b):=\sum_{\rho,r\in T_{m-1}}B_{m-1}(b;\rho,r).
\]
Then the exact two-child contribution is
\[
C_m^{(2)}(k)=3\sum_{a+b=k}A_{m-1}^{\mathrm{tot}}(a)\,B_{m-1}^{\mathrm{tot}}(b).
\]

### 3. Spanning all three children

Fix outer state
\[
(\ell,\lambda,\rho,r)\in T_{m-1}^4.
\]
By [[lemmas/ternary-one-split-structure]], any three-child convex subset is obtained uniquely from

1. a cap in \(L_m\) with endpoints \((\ell,\lambda)\),
2. a cup in \(R_m\) with endpoints \((\rho,r)\),
3. one optional upper bridge point from the region counted by \(U_m(\lambda,r)\),
4. one optional lower bridge point from the region counted by \(D_m(\ell,\rho)\),

with at least one of the two bridge choices present.

Hence the exact contribution with exactly one middle point is
\[
C_m^{(3,1)}(k)=
\sum_{a+b+1=k}\;
\sum_{\ell,\lambda,\rho,r}
A_{m-1}(a;\ell,\lambda)\,
B_{m-1}(b;\rho,r)\,
\bigl(U_m(\lambda,r)+D_m(\ell,\rho)\bigr),
\]
and the exact contribution with exactly two middle points is
\[
C_m^{(3,2)}(k)=
\sum_{a+b+2=k}\;
\sum_{\ell,\lambda,\rho,r}
A_{m-1}(a;\ell,\lambda)\,
B_{m-1}(b;\rho,r)\,
U_m(\lambda,r)\,D_m(\ell,\rho).
\]

Also, again by the lemma,
\[
C_m^{(3,c)}(k)=0\qquad(c\ge 3).
\]

Therefore the total exact recurrence is
\[
C_m(k)=C_m^{(1)}(k)+C_m^{(2)}(k)+C_m^{(3,1)}(k)+C_m^{(3,2)}(k).
\]

All displayed formulas in this section are exact identities.

## First exact failure of a binary-style state space

The aggregated cap/cup totals \(A_m^{\mathrm{tot}},B_m^{\mathrm{tot}}\) suffice for the two-child term, but they already fail at the first all-three-block contribution:
\[
C_m^{(3,1)}(k),\qquad C_m^{(3,2)}(k).
\]
The obstruction is exact: the middle factors depend on the actual outer endpoints,
\[
U_m(\lambda,r),\qquad D_m(\ell,\rho),
\]
not merely on the sizes \(a,b\).

So the recursion does close exactly, but only after enlarging the state from aggregate chain counts to endpoint-refined chain counts plus the bridge functions \(U_m,D_m\). This is the new state propagation forced by the lemma.

## One explicit top-split term

Keeping one summand from the exact three-child formulas gives valid inequalities. For \(k=a+b+1\),
\[
C_m(k)\ge
A_{m-1}(a;\ell,\lambda)\,
B_{m-1}(b;\rho,r)\,
\bigl(U_m(\lambda,r)+D_m(\ell,\rho)\bigr),
\]
and for \(k=a+b+2\),
\[
C_m(k)\ge
A_{m-1}(a;\ell,\lambda)\,
B_{m-1}(b;\rho,r)\,
U_m(\lambda,r)\,D_m(\ell,\rho).
\]

These are clean top-split lower bounds, but they are only inequalities obtained by retaining one exact summand.

## Decision

The correct conclusion at this stage is:

\[
\boxed{\text{the exact recurrence closes, but only with new bridge-state quantities; ternary remains genuinely open.}}
\]

Reason: the ternary one-split lemma tells us exactly how \(U_m,D_m\) enter, but by itself it gives no uniform lower bound on those bridge factors for the endpoint states carrying the dominant cap/cup multiplicities. In particular, the lemma alone does not imply any universal estimate such as
\[
U_m(\lambda,r)+D_m(\ell,\rho)\ge 1
\quad\text{or}\quad
U_m(\lambda,r)D_m(\ell,\rho)\ge 1
\]
for the outer states that matter asymptotically.

So one explicit top-scale term does not yet force a quadratic coefficient \(\ge 1\). The first local obstruction is not a coefficient obstruction; it is the failure of aggregate chain counts to close the three-block term without the new endpoint-dependent bridge data.
```

The outcome is option 2: exact recurrence in an enlarged state space, but no local coefficient-`1` obstruction yet.
