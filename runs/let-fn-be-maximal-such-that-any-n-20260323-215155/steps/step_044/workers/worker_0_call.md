---
call_num: 14
label: worker_44_0
model: gpt-5.4
elapsed_ms: 330381
input_tokens: 107484
output_tokens: 17845
cache_read_tokens: 97792
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

Focus on exactly one task: salvage the current explicit template by repairing the separated-position proof only, turning the near-complete note into a fully rigorous repo-ready obstruction note if possible.

Template and established data to reuse:
$$
\Phi_i(x)=Ax+t_i,\qquad
A=\operatorname{diag}(1/10,1/100),
$$
with
$$
t_L=(-4,2),\qquad t_M=(0,0),\qquad t_R=(5,-2).
$$
Already checked by prior worker/verification:
- coordinate-word formulas and the child boxes for $L_n,M_n,R_n$;
- same-child secant slope bound
$$
|\operatorname{slope}|\le \sigma:=40/297;
$$
- corrected bridge maps
$$
\alpha_0=\mathrm{id}+(-40,200),\qquad \beta_0=\mathrm{id}+(50,-200);
$$
- decisive first new pair at $(i,j,k)=(M,M,M)$:
$$
\alpha_1=\mathrm{id}+(-400,20000),\qquad \beta_1=\mathrm{id}+(500,-20000);
$$
- no nontrivial affine symmetry of the template.

The only remaining issue from verification:
- the separated-position inequalities in the latest note were written with overly broad quantifiers. The verifier explicitly said the endpoint comparisons look salvageable if rewritten with the correct one-sided ranges (evaluate left-child secants only for $x$ to the right of the whole left interval, etc.).

Deliverable:
1. Give a fully rigorous separated-position proof for this exact template, with correct quantifiers and correct worst-case endpoint choices.
2. Keep the proof tight and explicit:
   - state the box bounds;
   - state the secant slope bound used for top-level child secants;
   - for each of the three child types, compare only on the relevant opposite-side $x$-range.
3. If the repair succeeds, output a complete repo-ready markdown note with `Summary:` line for slug
   `status/balanced-ternary-concrete-bridge-obstruction`.
4. Reuse the already-correct affine obstruction and symmetry sections; do not redo them unless needed for coherence.
5. If the repair unexpectedly fails, output instead a repo-ready partial note stating exactly where the current template proof still breaks.

Requirements:
- Do not revisit asymptotics, binary constructions, or larger finite closures.
- Do not overclaim: proving a first exact obstruction to the currently tracked bridge state is enough.
- Keep exact identities separate from inequalities.
- The goal is a final repo-ready note, not just commentary.



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

I could not write the file because the sandbox launcher is failing before any command runs: `bwrap: Unknown option --argv0`. The repair itself closes. Below is a repo-ready note for `status/balanced-ternary-concrete-bridge-obstruction.md`.

```markdown
Summary: For the explicit balanced ternary template
$$
\Phi_i(x)=Ax+t_i,\qquad
A=\operatorname{diag}(1/10,1/100),
$$
with
$$
t_L=(-4,2),\qquad t_M=(0,0),\qquad t_R=(5,-2),
$$
the separated-position step is valid with the correct one-sided quantifiers. Hence [[lemmas/ternary-one-split-structure]] applies at every level. Combined with the already-verified conjugation data
$$
\alpha_0=\mathrm{id}+(-40,200),\qquad \beta_0=\mathrm{id}+(50,-200),
$$
and the first new pair
$$
\alpha_1=\mathrm{id}+(-400,20000),\qquad \beta_1=\mathrm{id}+(500,-20000),
$$
this gives a concrete obstruction to the currently tracked bridge state: the recursion for $(U_m,D_m)$ already leaves the state space generated by $(\alpha_0,\beta_0)$.

This note only repairs the separated-position proof for this exact template. It does not revisit asymptotics or any larger closure question.

## Setup

Let $T_0=\{(0,0)\}$ and, for $n\ge 1$,
$$
T_n=L_n\sqcup M_n\sqcup R_n,
\qquad
L_n=\Phi_L(T_{n-1}),\quad M_n=\Phi_M(T_{n-1}),\quad R_n=\Phi_R(T_{n-1}).
$$

The coordinate-word formulas already checked in the previous notes give
$$
T_n\subseteq [X_n^-,X_n^+]\times [Y_n^-,Y_n^+],
$$
where
$$
X_n^-=-\frac{40}{9}\bigl(1-10^{-n}\bigr),\qquad
X_n^+=\frac{50}{9}\bigl(1-10^{-n}\bigr),
$$
$$
Y_n^-=-\frac{200}{99}\bigl(1-100^{-n}\bigr),\qquad
Y_n^+=\frac{200}{99}\bigl(1-100^{-n}\bigr).
$$

Therefore, for $n\ge 1$, the three top-level children satisfy the exact box bounds
$$
L_n\subseteq I_L(n)\times J_L(n),
\qquad
M_n\subseteq I_M(n)\times J_M(n),
\qquad
R_n\subseteq I_R(n)\times J_R(n),
$$
with
$$
I_L(n)=\left[-\frac{40}{9}+\frac{4}{9}10^{-(n-1)},\ -\frac{31}{9}-\frac{5}{9}10^{-(n-1)}\right],
$$
$$
I_M(n)=\left[-\frac{4}{9}+\frac{4}{9}10^{-(n-1)},\ \frac{5}{9}-\frac{5}{9}10^{-(n-1)}\right],
$$
$$
I_R(n)=\left[\frac{41}{9}+\frac{4}{9}10^{-(n-1)},\ \frac{50}{9}-\frac{5}{9}10^{-(n-1)}\right],
$$
and
$$
J_L(n)=\left[\frac{196}{99}+\frac{2}{99}100^{-(n-1)},\ \frac{200}{99}-\frac{2}{99}100^{-(n-1)}\right],
$$
$$
J_M(n)=\left[-\frac{2}{99}+\frac{2}{99}100^{-(n-1)},\ \frac{2}{99}-\frac{2}{99}100^{-(n-1)}\right],
$$
$$
J_R(n)=\left[-\frac{200}{99}+\frac{2}{99}100^{-(n-1)},\ -\frac{196}{99}-\frac{2}{99}100^{-(n-1)}\right].
$$

For the inequalities below it is enough to use the coarser universal envelopes
$$
L_n\subseteq \bar I_L\times \bar J_L,\qquad
M_n\subseteq \bar I_M\times \bar J_M,\qquad
R_n\subseteq \bar I_R\times \bar J_R,
$$
where
$$
\bar I_L=\left[-\frac{40}{9},-\frac{31}{9}\right],\quad
\bar I_M=\left[-\frac{4}{9},\frac{5}{9}\right],\quad
\bar I_R=\left[\frac{41}{9},\frac{50}{9}\right],
$$
$$
\bar J_L=\left[\frac{196}{99},\frac{200}{99}\right],\quad
\bar J_M=\left[-\frac{2}{99},\frac{2}{99}\right],\quad
\bar J_R=\left[-\frac{200}{99},-\frac{196}{99}\right].
$$

We also use the verified same-child secant bound
$$
|\operatorname{slope}|\le \sigma:=\frac{40}{297}
$$
for every secant determined by two points of a single child.

## Proposition: separated position for the explicit template

For every $n\ge 1$:

1. every secant of $L_n$ lies strictly above every point of $M_n\cup R_n$;
2. every secant of $M_n$ lies strictly below every point of $L_n$ and strictly above every point of $R_n$;
3. every secant of $R_n$ lies strictly below every point of $L_n\cup M_n$.

### Proof

Let $s$ be a secant line of one of the three children. Write its slope as $m$, so $|m|\le \sigma$.

The repair is that each comparison is only required on the opposite-side $x$-range.

### 1. Left-child secants

Let $s$ be a secant of $L_n$. Only points with $x$-coordinate to the right of the whole left interval matter:
$$
x\in \bar I_M\cup \bar I_R\subseteq \left[-\frac{4}{9},\frac{50}{9}\right].
$$
Choose any point $(x_0,y_0)\in s\cap L_n$. Then
$$
y_0\ge \frac{196}{99},\qquad x_0\ge -\frac{40}{9}.
$$
For every such $x$ we have $x\ge x_0$, hence
$$
s(x)=y_0+m(x-x_0)\ge y_0-\sigma(x-x_0).
$$
Since
$$
x-x_0\le \frac{50}{9}-\left(-\frac{40}{9}\right)=10,
$$
it follows that
$$
s(x)\ge \frac{196}{99}-10\sigma
=\frac{196}{99}-\frac{400}{297}
=\frac{188}{297}.
$$
Now
$$
\frac{188}{297}>\frac{2}{99},
$$
so $s(x)>\frac{2}{99}$ throughout the full $x$-range of $M_n\cup R_n$. Since every point of $M_n$ has $y\le \frac{2}{99}$ and every point of $R_n$ has $y\le -\frac{196}{99}$, the secant $s$ lies strictly above every point of $M_n\cup R_n$.

### 2. Middle-child secants

Let $s$ be a secant of $M_n$.

First compare against $L_n$. Only the $x$-range to the left of the whole middle interval matters:
$$
x\in \bar I_L\subseteq \left[-\frac{40}{9},-\frac{31}{9}\right].
$$
Choose any point $(x_0,y_0)\in s\cap M_n$. Then
$$
y_0\le \frac{2}{99},\qquad x_0\le \frac{5}{9}.
$$
For every $x\in \bar I_L$ we have $x\le x_0$, hence
$$
s(x)=y_0+m(x-x_0)\le y_0+\sigma(x_0-x).
$$
Since
$$
x_0-x\le \frac{5}{9}-\left(-\frac{40}{9}\right)=5,
$$
we get
$$
s(x)\le \frac{2}{99}+5\sigma
=\frac{2}{99}+\frac{200}{297}
=\frac{206}{297}.
$$
Now
$$
\frac{206}{297}<\frac{196}{99},
$$
while every point of $L_n$ has $y\ge \frac{196}{99}$. So every secant of $M_n$ lies strictly below every point of $L_n$.

Next compare against $R_n$. Only the $x$-range to the right of the whole middle interval matters:
$$
x\in \bar I_R\subseteq \left[\frac{41}{9},\frac{50}{9}\right].
$$
For the same $(x_0,y_0)\in s\cap M_n$ we have
$$
y_0\ge -\frac{2}{99},\qquad x_0\ge -\frac{4}{9}.
$$
Now $x\ge x_0$, so
$$
s(x)=y_0+m(x-x_0)\ge y_0-\sigma(x-x_0).
$$
Since
$$
x-x_0\le \frac{50}{9}-\left(-\frac{4}{9}\right)=6,
$$
we obtain
$$
s(x)\ge -\frac{2}{99}-6\sigma
=-\frac{2}{99}-\frac{240}{297}
=-\frac{82}{99}.
$$
Finally,
$$
-\frac{82}{99}>-\frac{196}{99},
$$
and every point of $R_n$ has $y\le -\frac{196}{99}$. Hence every secant of $M_n$ lies strictly above every point of $R_n$.

So every secant of $M_n$ is strictly below $L_n$ and strictly above $R_n$.

### 3. Right-child secants

Let $s$ be a secant of $R_n$. Only points with $x$-coordinate to the left of the whole right interval matter:
$$
x\in \bar I_L\cup \bar I_M\subseteq \left[-\frac{40}{9},\frac{5}{9}\right].
$$
Choose any point $(x_0,y_0)\in s\cap R_n$. Then
$$
y_0\le -\frac{196}{99},\qquad x_0\le \frac{50}{9}.
$$
For every such $x$ we have $x\le x_0$, hence
$$
s(x)=y_0+m(x-x_0)\le y_0+\sigma(x_0-x).
$$
Since
$$
x_0-x\le \frac{50}{9}-\left(-\frac{40}{9}\right)=10,
$$
we conclude that
$$
s(x)\le -\frac{196}{99}+10\sigma
=-\frac{196}{99}+\frac{400}{297}
=-\frac{188}{297}.
$$
Because
$$
-\frac{188}{297}<-\frac{2}{99},
$$
and every point of $M_n$ has $y\ge -\frac{2}{99}$ while every point of $L_n$ has $y\ge \frac{196}{99}$, every secant of $R_n$ lies strictly below every point of $L_n\cup M_n$.

This proves the separated-position hypothesis at every level. $\square$

## Consequence: the ternary one-split structure applies exactly

By the proposition, the explicit template satisfies the hypotheses of [[lemmas/ternary-one-split-structure]] for every top-level decomposition
$$
T_n=L_n\sqcup M_n\sqcup R_n.
$$
Therefore the exact two-block and three-block structural formulas from that lemma, and hence the exact decomposition recorded in [[attempts/alternative-construction-balanced-ternary-split]], are valid for this template without any further repair.

In particular, the bridge quantities are exactly
$$
U_m(\lambda,r)
=
\Bigl|\bigl\{z\in T_{m-1}: z \text{ lies above the line } \alpha_0(\lambda)\beta_0(r)\bigr\}\Bigr|,
$$
$$
D_m(\ell,\rho)
=
\Bigl|\bigl\{z\in T_{m-1}: z \text{ lies below the line } \alpha_0(\ell)\beta_0(\rho)\bigr\}\Bigr|,
$$
where
$$
\alpha_0=\Phi_M^{-1}\Phi_L=\mathrm{id}+(-40,200),
\qquad
\beta_0=\Phi_M^{-1}\Phi_R=\mathrm{id}+(50,-200).
$$

## Concrete bridge obstruction for the current tracked state

The exact conjugation expansion from [[attempts/balanced-ternary-bridge-conjugation-expansion]] says that for affine injections $\alpha,\beta$,
$$
H_n^\pm[\alpha,\beta](\Phi_i(x'),\Phi_j(y'))
=
\sum_{k\in\{L,M,R\}}
H_{n-1}^\pm[\Phi_k^{-1}\alpha\Phi_i,\Phi_k^{-1}\beta\Phi_j](x',y').
$$

Apply this with $(\alpha,\beta)=(\alpha_0,\beta_0)$. The $(i,j,k)=(M,M,M)$ summand produces
$$
\alpha_1:=\Phi_M^{-1}\alpha_0\Phi_M=\mathrm{id}+(-400,20000),
$$
$$
\beta_1:=\Phi_M^{-1}\beta_0\Phi_M=\mathrm{id}+(500,-20000).
$$

These identities are exact. They are the first new affine pair in the expansion.

The already-verified symmetry computation for this template shows that the IFS admits no nontrivial affine symmetry. Therefore this new pair cannot be identified with the original bridge pair by a template symmetry. So the present bridge state
$$
\{A_m(a;\ell,\lambda)\},\qquad \{B_m(b;\rho,r)\},\qquad \{U_m(\lambda,r)\},\qquad \{D_m(\ell,\rho)\}
$$
does not close under the exact recursion: even at the first new step, the recursive expansion requires half-plane counts indexed by the new pair $(\alpha_1,\beta_1)$.

This is the precise obstruction established here. It is an obstruction only to the currently tracked bridge state, not a proof that no larger finite closure exists.
```
