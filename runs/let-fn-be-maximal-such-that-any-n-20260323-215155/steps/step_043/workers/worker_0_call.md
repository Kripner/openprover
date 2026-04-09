---
call_num: 13
label: worker_43_0
model: gpt-5.4
elapsed_ms: 397736
input_tokens: 175921
output_tokens: 21306
cache_read_tokens: 155776
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

Use [[lemmas/ternary-one-split-structure]], [[attempts/alternative-construction-balanced-ternary-split]], and [[attempts/balanced-ternary-bridge-conjugation-expansion]].

Work on exactly one task: produce one fully verified explicit balanced ternary template for which the corrected first bridge expansion gives a genuine new bridge pair, so that the concrete obstruction becomes repo-ready.

What is already established and should be reused:
- The ternary local geometry is verified.
- The decomposition of the total count into one-child, two-child, and bridge-weighted three-child terms is exact.
- The abstract bridge expansion is exact:
$$
H_n^\pm[\alpha,\beta](\Phi_i(x'),\Phi_j(y'))
=
\sum_{k\in\{L,M,R\}}
H_{n-1}^\pm[\Phi_k^{-1}\alpha\Phi_i,\Phi_k^{-1}\beta\Phi_j](x',y').
$$
- For a common linear part $A$ and translations $t_L,t_M,t_R$, the corrected conjugation formulas are
$$
\alpha_0=\Phi_M^{-1}\Phi_L=\mathrm{id}+A^{-1}(t_L-t_M),
$$
$$
\beta_0=\Phi_M^{-1}\Phi_R=\mathrm{id}+A^{-1}(t_R-t_M),
$$
and
$$
\Phi_k^{-1}\alpha_0\Phi_i
=
\mathrm{id}+A^{-2}(t_L-t_M)+A^{-1}(t_i-t_k),
$$
$$
\Phi_k^{-1}\beta_0\Phi_j
=
\mathrm{id}+A^{-2}(t_R-t_M)+A^{-1}(t_j-t_k).
$$
- In the candidate template
$$
A=\operatorname{diag}(1/10,1/100),\qquad
t_L=(-4,2),\ t_M=(0,0),\ t_R=(5,-2),
$$
the affine obstruction appears correct, but the previous separated-position verification was not rigorous enough.

Your deliverable:
1. Either rigorously verify the separated-position hypotheses for that exact candidate template, or replace it by a simpler asymmetric common-homothety template that you can verify cleanly.
2. Keep the task narrowly focused on the template verification + concrete obstruction. Do not revisit asymptotics or binary constructions.
3. If the candidate template works, give a clean proof of the secant inequalities with correct worst-case endpoint choices.
4. If it does not, choose a nearby simpler template and recompute only the concrete data needed:
   - the valid template definition,
   - the standard pair $(\alpha_0,\beta_0)$,
   - one decisive first-generation new pair (for example at a specific $(i,j,k)$),
   - the statement that the currently tracked bridge state records only the standard pair,
   - and a proof that no actual symmetry of the template identifies the new pair with the standard one.
5. Do not overclaim:
   - proving a first exact obstruction to the current bridge state is enough;
   - you do not need to prove that no larger finite closure exists.
6. Output repo-ready markdown with a `Summary:` line.
   - If successful, use slug `status/balanced-ternary-concrete-bridge-obstruction`.
   - If you can only partially repair the template step, output a repo-ready partial note instead and state exactly what remains open.

Requirements:
- Be explicit and fully rigorous about the separated-position check.
- Keep exact identities separate from inequalities.
- A shorter, cleaner valid template is better than salvaging a messy one.



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


## [[attempts/alternative-construction-balanced-ternary-split]]

Summary: For the balanced ternary separated recursion, the total convex-subset count decomposes exactly into one-child, two-child, and endpoint-refined three-child terms, but exact recursive propagation of the new bridge-state quantities $U_m,D_m$ is still unresolved.

This note records the current exact decomposition forced by [[lemmas/ternary-one-split-structure]], together with the precise point still missing for a closed recursion.

## Setup

Fix affine contractions
$$
\\Phi_L,\\Phi_M,\\Phi_R:\\mathbb R^2\\to\\mathbb R^2
$$
such that for every finite set $X$ in general position, after one fixed small generic rotation the three images
$$
\\Phi_L(X),\\qquad \\Phi_M(X),\\qquad \\Phi_R(X)
$$
have disjoint $x$-ranges in the order
$$
x(\\Phi_L(X))<x(\\Phi_M(X))<x(\\Phi_R(X))
$$
and satisfy the ternary separated-position hypotheses of [[lemmas/ternary-one-split-structure]].

Let $T_0$ be a one-point set. For $m\\ge 1$, define
$$
T_m=L_m\\sqcup M_m\\sqcup R_m
$$
by
$$
L_m=\\Phi_L(T_{m-1}),\\qquad M_m=\\Phi_M(T_{m-1}),\\qquad R_m=\\Phi_R(T_{m-1}).
$$
Then
$$
|T_m|=3^m.
$$

## Endpoint-refined outer-chain state

For endpoint-refined cap/cup counts, write
$$
A_m(a;\\ell,\\lambda):=\\widetilde Q_-(a,T_m;\\ell,\\lambda),
\\qquad
B_m(b;\\rho,r):=\\widetilde Q_+(b,T_m;\\rho,r).
$$

The ternary lemma shows that these do not suffice by themselves for three-child spans: after fixing outer endpoints, the middle contribution depends on bridge regions. Define the parent-scale bridge quantities
$$
U_m(\\lambda,r):=\\Bigl|\\Bigl\\{z\\in T_{m-1}:\\Phi_M(z)\\text{ lies above the line }\\Phi_L(\\lambda)\\Phi_R(r)\\Bigr\\}\\Bigr|,
$$
$$
D_m(\\ell,\\rho):=\\Bigl|\\Bigl\\{z\\in T_{m-1}:\\Phi_M(z)\\text{ lies below the line }\\Phi_L(\\ell)\\Phi_R(\\rho)\\Bigr\\}\\Bigr|.
$$

## Exact decomposition of $C_m(k)$

Let $C_m(k)$ be the number of $k$-point subsets of $T_m$ in convex position.

### 1. One-child contribution

Exactly
$$
C_m^{(1)}(k)=3\,C_{m-1}(k).
$$

### 2. Exactly two children

For each earlier-later pair $(X,Y)\\in\\{(L_m,M_m),(M_m,R_m),(L_m,R_m)\\}$, [[lemmas/ternary-one-split-structure]] gives exactly: the $X$-part is a cap and the $Y$-part is a cup.

Set
$$
A_{m-1}^{\\mathrm{tot}}(a):=\\sum_{\\ell,\\lambda\\in T_{m-1}}A_{m-1}(a;\\ell,\\lambda),
\\qquad
B_{m-1}^{\\mathrm{tot}}(b):=\\sum_{\\rho,r\\in T_{m-1}}B_{m-1}(b;\\rho,r).
$$
Then the exact two-child contribution is
$$
C_m^{(2)}(k)=3\\sum_{a+b=k}A_{m-1}^{\\mathrm{tot}}(a)\,B_{m-1}^{\\mathrm{tot}}(b).
$$

### 3. All three children

Fix outer state
$$
(\\ell,\\lambda,\\rho,r)\\in T_{m-1}^4.
$$
By [[lemmas/ternary-one-split-structure]], any three-child convex subset is obtained from
1. a cap in $L_m$ with endpoints $(\\ell,\\lambda)$,
2. a cup in $R_m$ with endpoints $(\\rho,r)$,
3. optionally one upper bridge point from the region counted by $U_m(\\lambda,r)$,
4. optionally one lower bridge point from the region counted by $D_m(\\ell,\\rho)$,

with at least one bridge choice present, and with at most one upper and at most one lower middle point.

Hence the exact contribution with exactly one middle point is
$$
C_m^{(3,1)}(k)=
\\sum_{a+b+1=k}\\;
\\sum_{\\ell,\\lambda,\\rho,r}
A_{m-1}(a;\\ell,\\lambda)\,
B_{m-1}(b;\\rho,r)\,
\\bigl(U_m(\\lambda,r)+D_m(\\ell,\\rho)\\bigr),
$$
and the exact contribution with exactly two middle points is
$$
C_m^{(3,2)}(k)=
\\sum_{a+b+2=k}\\;
\\sum_{\\ell,\\lambda,\\rho,r}
A_{m-1}(a;\\ell,\\lambda)\,
B_{m-1}(b;\\rho,r)\,
U_m(\\lambda,r)\,D_m(\\ell,\\rho).
$$
Also, by the same lemma,
$$
C_m^{(3,c)}(k)=0\\qquad(c\\ge 3).
$$

Therefore
$$
C_m(k)=C_m^{(1)}(k)+C_m^{(2)}(k)+C_m^{(3,1)}(k)+C_m^{(3,2)}(k).
$$

All displayed formulas in this section are exact identities, assuming the bridge quantities are interpreted exactly as above.

## Exact place still unresolved

This note does not establish recursive propagation formulas for
$$
U_m(\\lambda,r),\\qquad D_m(\\ell,\\rho)
$$
from level $m-1$ data.

So the current status is:

- the decomposition of $C_m(k)$ into one-child, two-child, and bridge-weighted three-child terms is exact;
- aggregate cap/cup totals do not suffice for the three-child term;
- but it remains unproved whether the enlarged state
$$
\\{A_m(a;\\ell,\\lambda)\\},\\ \\{B_m(b;\\rho,r)\\},\\ \\{U_m(\\lambda,r)\\},\\ \\{D_m(\\ell,\\rho)\\}
$$
itself closes recursively in the balanced ternary template.

## Consequence for next step

The next task is not to estimate asymptotics yet. It is to determine one of the following exactly:

1. derive recursive formulas for $U_m,D_m$ from level-$m-1$ state data, thereby closing the balanced ternary recurrence in an enlarged state space; or
2. identify the first exact obstruction showing that no such manageable closure holds in this template.

Until that is settled, no coefficient obstruction from the ternary family is established.

## [[attempts/balanced-ternary-bridge-conjugation-expansion]]

Summary: Expanding the ternary bridge quantities $U_m,D_m$ child-by-child gives exact recursive formulas in terms of half-plane counts indexed by conjugated affine map pairs, but it remains unresolved whether those pairs collapse to the currently tracked state in a fixed balanced ternary template.

This note records the exact recursive expansion that emerged from the bridge-state analysis, while separating it from the still-unproved non-closure claim.

## Setup

Keep the notation of [[attempts/alternative-construction-balanced-ternary-split]]. Define
$$
\alpha_0:=\Phi_M^{-1}\Phi_L,
\qquad
\beta_0:=\Phi_M^{-1}\Phi_R.
$$
Then the bridge quantities can be rewritten exactly as
$$
U_m(\lambda,r)
=
\Bigl|\bigl\{z\in T_{m-1}: z \text{ lies above the line } \alpha_0(\lambda)\beta_0(r)\bigr\}\Bigr|,
$$
$$
D_m(\ell,\rho)
=
\Bigl|\bigl\{z\in T_{m-1}: z \text{ lies below the line } \alpha_0(\ell)\beta_0(\rho)\bigr\}\Bigr|.
$$

## Generalized half-plane counts

For affine injections $\alpha,\beta$ and $n\ge 0$, define
$$
H_n^+[\alpha,\beta](x,y)
:=
\Bigl|\bigl\{z\in T_n: z \text{ lies above the line } \alpha(x)\beta(y)\bigr\}\Bigr|,
$$
$$
H_n^-[\alpha,\beta](x,y)
:=
\Bigl|\bigl\{z\in T_n: z \text{ lies below the line } \alpha(x)\beta(y)\bigr\}\Bigr|.
$$
Then
$$
U_m(\lambda,r)=H_{m-1}^+[\alpha_0,\beta_0](\lambda,r),
\qquad
D_m(\ell,\rho)=H_{m-1}^-[\alpha_0,\beta_0](\ell,\rho).
$$

## Exact recursive expansion

Write $x=\Phi_i(x')$, $y=\Phi_j(y')$ with $i,j\in\{L,M,R\}$ and $x',y'\in T_{n-1}$. Since
$$
T_n=\bigsqcup_{k\in\{L,M,R\}}\Phi_k(T_{n-1}),
$$
every counted point has the form $z=\Phi_k(z')$. Affine invariance of sidedness yields the exact identities
$$
H_n^+[\alpha,\beta](\Phi_i(x'),\Phi_j(y'))
=
\sum_{k\in\{L,M,R\}}
H_{n-1}^+[\Phi_k^{-1}\alpha\Phi_i,\Phi_k^{-1}\beta\Phi_j](x',y'),
$$
$$
H_n^-[\alpha,\beta](\Phi_i(x'),\Phi_j(y'))
=
\sum_{k\in\{L,M,R\}}
H_{n-1}^-[\Phi_k^{-1}\alpha\Phi_i,\Phi_k^{-1}\beta\Phi_j](x',y').
$$

Applying this with $(\alpha,\beta)=(\alpha_0,\beta_0)$ gives exact expansions for $U_m$ and $D_m$ in terms of lower-level half-plane counts indexed by conjugated affine map pairs.

## What is established and what is not

Established exactly:
- $U_m,D_m$ are instances of generalized half-plane counts.
- Recursive expansion introduces the map pairs
$$
(\Phi_k^{-1}\alpha_0\Phi_i,\ \Phi_k^{-1}\beta_0\Phi_j).
$$

Not yet established:
- whether, in a fixed balanced ternary template, those conjugated pairs reduce to finitely many already tracked bridge types;
- whether the state $\{A_m,B_m,U_m,D_m\}$ therefore closes or fails to close.

So this note is a partial result only. The next step is a concrete conjugacy computation in one fixed balanced ternary normalization.


======== RESPONSE ========

I could not write the file because the workspace tool wrapper is failing with `bwrap: Unknown option --argv0`. Below is the repo-ready note for `status/balanced-ternary-concrete-bridge-obstruction.md`.

```markdown
Summary: the diagonal template
$$
A=\operatorname{diag}(1/10,1/100),\qquad
t_L=(-4,2),\ t_M=(0,0),\ t_R=(5,-2)
$$
satisfies the ternary separated-position hypotheses with explicit margins, and the corrected first bridge expansion already produces a conjugated bridge pair not recorded by the current bridge state and not identified with the standard pair by any actual symmetry of the template.

# Status: concrete bridge obstruction in the balanced ternary template

We keep the candidate common-linear-part template
$$
\Phi_i(x)=Ax+t_i,
\qquad
A=\operatorname{diag}(1/10,1/100),
$$
with
$$
t_L=(-4,2),\qquad t_M=(0,0),\qquad t_R=(5,-2).
$$

We verify two points:

1. this template satisfies the separated-position hypotheses needed in [[lemmas/ternary-one-split-structure]];
2. the corrected first bridge expansion already produces a genuine new affine bridge pair, so the currently tracked bridge state does not close even at the first conjugation step.

## 1. Coordinate model and invariant boxes

Take
$$
T_0=\{(0,0)\},
\qquad
T_n=\Phi_L(T_{n-1})\sqcup \Phi_M(T_{n-1})\sqcup \Phi_R(T_{n-1}).
$$

For a word $w=w_1\cdots w_n\in\{L,M,R\}^n$, write
$$
a(L)=-4,\ a(M)=0,\ a(R)=5,
$$
$$
b(L)=2,\ b(M)=0,\ b(R)=-2.
$$
Then the point of $T_n$ indexed by $w$ has coordinates
$$
x(w)=\sum_{r=1}^n a(w_r)\,10^{-(r-1)},
\qquad
y(w)=\sum_{r=1}^n b(w_r)\,100^{-(r-1)}.
$$

Hence every $T_n$ lies in
$$
K=\left[-\frac{40}{9},\frac{50}{9}\right]\times\left[-\frac{200}{99},\frac{200}{99}\right].
$$
Therefore
$$
L_n:=\Phi_L(T_{n-1})\subseteq
\left[-\frac{40}{9},-\frac{31}{9}\right]\times\left[\frac{196}{99},\frac{200}{99}\right],
$$
$$
M_n:=\Phi_M(T_{n-1})\subseteq
\left[-\frac{4}{9},\frac{5}{9}\right]\times\left[-\frac{2}{99},\frac{2}{99}\right],
$$
$$
R_n:=\Phi_R(T_{n-1})\subseteq
\left[\frac{41}{9},\frac{50}{9}\right]\times\left[-\frac{200}{99},-\frac{196}{99}\right].
$$
In particular,
$$
x(L_n)<x(M_n)<x(R_n)
$$
strictly.

## 2. Uniform secant-slope bound

Let $p,q\in T_n$ be distinct, with words $u,v$. Let $m$ be the first index with $u_m\neq v_m$.

Then
$$
x(p)-x(q)=10^{-(m-1)}(\Delta_x+\varepsilon_x),
\qquad
\Delta_x\in\{\pm4,\pm5,\pm9\},
$$
$$
y(p)-y(q)=100^{-(m-1)}(\Delta_y+\varepsilon_y),
\qquad
\Delta_y\in\{\pm2,\pm4\},
$$
with tail bounds
$$
|\varepsilon_x|\le \sum_{s\ge1}9\cdot 10^{-s}=1,
\qquad
|\varepsilon_y|\le \sum_{s\ge1}4\cdot 100^{-s}=\frac4{99}.
$$
Hence
$$
|x(p)-x(q)|\ge 10^{-(m-1)}(4-1)=3\cdot 10^{-(m-1)},
$$
$$
|y(p)-y(q)|\le 100^{-(m-1)}\left(4+\frac4{99}\right)=\frac{400}{99}\,100^{-(m-1)}.
$$
Therefore
$$
\left|\operatorname{slope}(pq)\right|
\le
\frac{\frac{400}{99}\,100^{-(m-1)}}{3\cdot 10^{-(m-1)}}
=
\frac{400}{297}\,10^{-(m-1)}
\le \frac{400}{297}.
$$

If $p,q$ lie in one fixed first-generation child, then $m\ge2$, so
$$
\left|\operatorname{slope}(pq)\right|\le \frac{40}{297}.
$$
Set
$$
\sigma:=\frac{40}{297}.
$$

## 3. Separated-position verification

We now check the exact ternary separated-position conditions.

### 3.1. Every $L_n$-secant lies strictly above $M_n\cup R_n$

Let $\ell$ be a line through two points of $L_n$. Then $\operatorname{slope}(\ell)\ge -\sigma$ and every point of $L_n$ has $y\ge 196/99$ and $x\ge -40/9$. Hence for every $x\ge -40/9$,
$$
\ell(x)\ge \frac{196}{99}-\sigma\left(x+\frac{40}{9}\right).
$$

For $M_n$, the worst case is the rightmost $x=5/9$:
$$
\ell(x)\ge \frac{196}{99}-5\sigma
=\frac{196}{99}-\frac{200}{297}
=\frac{388}{297}.
$$
But every point of $M_n$ has $y\le 2/99=6/297$, so
$$
\frac{388}{297}>\frac{2}{99}.
$$

For $R_n$, the worst case is the rightmost $x=50/9$:
$$
\ell(x)\ge \frac{196}{99}-10\sigma
=\frac{196}{99}-\frac{400}{297}
=\frac{188}{297}.
$$
But every point of $R_n$ has $y\le -196/99$, so
$$
\frac{188}{297}>-\frac{196}{99}.
$$

Thus every $L_n$-secant lies strictly above every point of $M_n\cup R_n$.

### 3.2. Every $M_n$-secant lies strictly below $L_n$ and strictly above $R_n$

Let $\ell$ be a line through two points of $M_n$.

To compare with $L_n$, use the rightmost anchor $(5/9,2/99)$ and the most negative slope $-\sigma$. For every $x\le 5/9$,
$$
\ell(x)\le \frac{2}{99}+\sigma\left(\frac59-x\right).
$$
The worst case in $L_n$ is the leftmost $x=-40/9$:
$$
\ell(x)\le \frac{2}{99}+5\sigma
=\frac{2}{99}+\frac{200}{297}
=\frac{206}{297}.
$$
But every point of $L_n$ has $y\ge 196/99=588/297$, so
$$
\frac{206}{297}<\frac{196}{99}.
$$

To compare with $R_n$, use the leftmost anchor $(-4/9,-2/99)$ and the most negative slope $-\sigma$. For every $x\ge -4/9$,
$$
\ell(x)\ge -\frac{2}{99}-\sigma\left(x+\frac49\right).
$$
The worst case in $R_n$ is the rightmost $x=50/9$:
$$
\ell(x)\ge -\frac{2}{99}-6\sigma
=-\frac{2}{99}-\frac{240}{297}
=-\frac{82}{99}.
$$
But every point of $R_n$ has $y\le -196/99$, so
$$
-\frac{82}{99}>-\frac{196}{99}.
$$

Thus every $M_n$-secant lies strictly below $L_n$ and strictly above $R_n$.

### 3.3. Every $R_n$-secant lies strictly below $L_n\cup M_n$

Let $\ell$ be a line through two points of $R_n$. Using the rightmost anchor $(50/9,-196/99)$ and the most negative slope $-\sigma$, for every $x\le 50/9$,
$$
\ell(x)\le -\frac{196}{99}+\sigma\left(\frac{50}{9}-x\right).
$$

For $M_n$, the worst case is the leftmost $x=-4/9$:
$$
\ell(x)\le -\frac{196}{99}+6\sigma
=-\frac{196}{99}+\frac{240}{297}
=-\frac{116}{99}.
$$
But every point of $M_n$ has $y\ge -2/99$, so
$$
-\frac{116}{99}<-\frac{2}{99}.
$$

For $L_n$, the worst case is the leftmost $x=-40/9$:
$$
\ell(x)\le -\frac{196}{99}+10\sigma
=-\frac{196}{99}+\frac{400}{297}
=-\frac{188}{297}.
$$
But every point of $L_n$ has $y\ge 196/99$, so
$$
-\frac{188}{297}<\frac{196}{99}.
$$

Thus every $R_n$-secant lies strictly below every point of $L_n\cup M_n$.

### 3.4. Conclusion

So the candidate template satisfies exactly the ternary separated-position hypotheses of [[lemmas/ternary-one-split-structure]]. The inequalities hold with uniform positive margins. Hence, if desired, one may apply a sufficiently small generic rotation afterward to enforce general position without destroying any of the strict separations.

## 4. The standard bridge pair

Because the linear part is common,
$$
\alpha_0=\Phi_M^{-1}\Phi_L=\operatorname{id}+A^{-1}(t_L-t_M),
$$
$$
\beta_0=\Phi_M^{-1}\Phi_R=\operatorname{id}+A^{-1}(t_R-t_M).
$$
Since
$$
A^{-1}=\operatorname{diag}(10,100),
$$
we obtain
$$
\alpha_0=\operatorname{id}+(-40,200),
\qquad
\beta_0=\operatorname{id}+(50,-200).
$$

By definition,
$$
U_m(\lambda,r)=H_{m-1}^+[\alpha_0,\beta_0](\lambda,r),
\qquad
D_m(\ell,\rho)=H_{m-1}^-[\alpha_0,\beta_0](\ell,\rho).
$$
So the currently tracked bridge state records only the single affine pair $(\alpha_0,\beta_0)$.

## 5. A decisive first-generation new pair

Take the exact bridge expansion at
$$
x=\Phi_M(x'),\qquad y=\Phi_M(y').
$$
In the $k=M$ summand, the conjugated pair is
$$
\alpha_1:=\Phi_M^{-1}\alpha_0\Phi_M,
\qquad
\beta_1:=\Phi_M^{-1}\beta_0\Phi_M.
$$
Using the corrected formula
$$
\Phi_k^{-1}\alpha_0\Phi_i
=
\operatorname{id}+A^{-2}(t_L-t_M)+A^{-1}(t_i-t_k),
$$
$$
\Phi_k^{-1}\beta_0\Phi_j
=
\operatorname{id}+A^{-2}(t_R-t_M)+A^{-1}(t_j-t_k),
$$
with $i=j=k=M$, we get
$$
\alpha_1=\operatorname{id}+A^{-2}(t_L-t_M),
\qquad
\beta_1=\operatorname{id}+A^{-2}(t_R-t_M).
$$
Since
$$
A^{-2}=\operatorname{diag}(100,10000),
$$
this is
$$
\alpha_1=\operatorname{id}+(-400,20000),
\qquad
\beta_1=\operatorname{id}+(500,-20000).
$$

This is not the standard pair:
$$
(-400,20000)\neq (-40,200),
\qquad
(500,-20000)\neq (50,-200).
$$

## 6. No actual symmetry identifies $(\alpha_1,\beta_1)$ with $(\alpha_0,\beta_0)$

Let $S(x)=Bx+c$ be an affine symmetry of the template, meaning
$$
S\circ \Phi_i=\Phi_{\sigma(i)}\circ S
\qquad (i\in\{L,M,R\})
$$
for some permutation $\sigma$.

Comparing linear parts gives
$$
BA=AB.
$$
Since
$$
A=\operatorname{diag}(1/10,1/100)
$$
has distinct eigenvalues, $B$ must be diagonal:
$$
B=\operatorname{diag}(u,v).
$$

Comparing translations and subtracting the equations for $i,j$ gives
$$
B(t_i-t_j)=t_{\sigma(i)}-t_{\sigma(j)}.
$$
The $x$-differences among the three translation points are
$$
\pm4,\ \pm5,\ \pm9,
$$
so multiplying by $u$ must preserve this set; hence $|u|=1$.
The nonzero $y$-differences are
$$
\pm2,\ \pm4,
$$
so multiplying by $v$ must preserve this set; hence $|v|=1$.
Thus
$$
u,v\in\{\pm1\}.
$$

Now
$$
t_L-t_R=(-9,4).
$$
So
$$
B(t_L-t_R)=(-9u,4v).
$$
Among all differences $t_a-t_b$, the only vectors with absolute values $(9,4)$ are
$$
(-9,4)\quad\text{and}\quad(9,-4),
$$
hence $u=v$. Therefore
$$
B=I\quad\text{or}\quad B=-I.
$$

If $B=-I$, then
$$
B(t_L-t_M)=(4,-2)=t_M-t_L,
$$
so $\sigma(L)=M$ and $\sigma(M)=L$.
But also
$$
B(t_M-t_R)=(5,-2)=t_R-t_M,
$$
so $\sigma(M)=R$ and $\sigma(R)=M$.
Contradiction. Hence $B\neq -I$.

So $B=I$. Then
$$
t_{\sigma(i)}-t_{\sigma(j)}=t_i-t_j
$$
for all $i,j$, hence $\sigma=\operatorname{id}$. Returning to
$$
Bt_i+c=Ac+t_i
$$
gives
$$
c=Ac.
$$
Since $1$ is not an eigenvalue of $A$, this forces $c=0$.

Therefore the template has only the identity affine symmetry.

Consequently, symmetry-equivalence of bridge pairs reduces to literal equality. Since
$$
(\alpha_1,\beta_1)\neq(\alpha_0,\beta_0),
$$
the pair $(\alpha_1,\beta_1)$ is a genuine new bridge pair.

## 7. Concrete obstruction

The currently tracked bridge state carries only
$$
H_n^\pm[\alpha_0,\beta_0].
$$
But the exact first corrected bridge expansion already contains the additional pair
$$
(\alpha_1,\beta_1)
=
\bigl(\operatorname{id}+(-400,20000),\ \operatorname{id}+(500,-20000)\bigr),
$$
coming from the $(i,j,k)=(M,M,M)$ summand.

Thus this template yields a concrete first exact obstruction:

1. the template is valid and satisfies the ternary separated-position hypotheses;
2. the current bridge state records only the standard pair $(\alpha_0,\beta_0)$;
3. the first exact bridge expansion already produces the new pair $(\alpha_1,\beta_1)$;
4. no actual symmetry of the template identifies this new pair with the standard one.

This proves a first exact obstruction to the currently tracked bridge state. No stronger claim is made here: this note does not prove that no larger finite closure exists.
```
