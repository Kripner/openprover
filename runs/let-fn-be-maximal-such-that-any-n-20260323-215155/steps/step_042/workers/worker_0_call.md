---
call_num: 12
label: worker_42_0
model: gpt-5.4
elapsed_ms: 669630
input_tokens: 109614
output_tokens: 19785
cache_read_tokens: 99712
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

Work on exactly one task: pick a very simple explicit balanced ternary separated template and recompute the bridge conjugates correctly from scratch, enough to decide whether the currently tracked bridge state closes or already fails at first expansion.

Context already established:
- The ternary local geometry is verified.
- The total count decomposition into one-child, two-child, and bridge-weighted three-child terms is exact.
- The abstract bridge expansion
$$
H_n^\pm[\alpha,\beta](\Phi_i(x'),\Phi_j(y'))
=
\sum_{k\in\{L,M,R\}}
H_{n-1}^\pm[\Phi_k^{-1}\alpha\Phi_i,\Phi_k^{-1}\beta\Phi_j](x',y')
$$
is exact.
- The previous concrete obstruction attempt is invalid because the first-generation conjugates were computed incorrectly.

What to do:
1. Choose an explicit convenient balanced ternary template.
   - Prefer the simplest possible one, e.g. a common small homothety plus three asymmetric translation vectors, if that still satisfies the separated-position hypotheses.
   - Verify the separated-position hypotheses for your template.
2. Compute correctly
$$
\alpha_0=\Phi_M^{-1}\Phi_L,\qquad \beta_0=\Phi_M^{-1}\Phi_R,
$$
then compute the first-generation conjugates
$$
\Phi_k^{-1}\alpha_0\Phi_i,\qquad \Phi_k^{-1}\beta_0\Phi_j
$$
for the instances you need to decide closure.
   - Derive the correct general formula first.
   - Check decisive instances explicitly, including at least the $i=j=k=M$ instance.
   - If useful, summarize the whole first-generation family compactly.
3. Decide exactly one of the following:
   - the first-generation pairs collapse to a finite clean family that yields an exact closed enlarged-state recursion; state that family and the exact closure;
   - or at least one genuinely new required pair appears already at first expansion and is not one of the currently tracked bridge types, nor identified by an actual symmetry of the chosen template; state that as the first exact obstruction.
4. If you claim obstruction, make the conclusion precise:
   - identify the concrete new pair(s);
   - explain why the currently tracked state only covers the standard bridge pair(s);
   - explain why the new pair is not removed by template symmetry.
5. Keep exact identities separate from inequalities.
6. Output repo-ready markdown with a `Summary:` line.
   - If closure works, suitable slug: `status/balanced-ternary-recursion-closure`.
   - If obstruction is proved, suitable slug: `status/balanced-ternary-concrete-bridge-obstruction`.
7. If the corrected computation still does not suffice to prove obstruction, say exactly what weaker statement is established instead; do not overclaim.

Requirements:
- Focus only on the corrected concrete conjugacy/closure question.
- Do not revisit asymptotics, binary variants, or nonrecursive constructions.
- A clean explicit affine computation is preferred over discussion.



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

I could not write the file in-place because every tool call failed with `bwrap: Unknown option --argv0`. Repo-ready markdown follows; suggested slug: `status/balanced-ternary-concrete-bridge-obstruction`.

```markdown
Summary: In the explicit asymmetric balanced ternary template
$$
\Phi_s(z)=Az+t_s,\qquad
A=\begin{pmatrix}1/10&0\\0&1/100\end{pmatrix},
$$
with
$$
t_L=(-4,2),\qquad t_M=(0,0),\qquad t_R=(5,-2),
$$
the first bridge expansion already produces the new pair
$$
\bigl(\mathrm{id}+(-400,20000),\ \mathrm{id}+(500,-20000)\bigr)
$$
at the $(i,j,k)=(M,M,M)$ term. Hence the currently tracked bridge state $(\alpha_0,\beta_0)$ does not close at first expansion.

# Status: concrete bridge obstruction

## 1. Explicit template and separated position

Take
$$
\Phi_s(z)=Az+t_s,\qquad
A=\begin{pmatrix}1/10&0\\0&1/100\end{pmatrix},
\qquad
t_L=(-4,2),\ t_M=(0,0),\ t_R=(5,-2).
$$

Let
$$
K=\left[-\frac{50}{9},\frac{50}{9}\right]\times\left[-\frac{200}{99},\frac{200}{99}\right].
$$
Then $\Phi_L(K)\cup\Phi_M(K)\cup\Phi_R(K)\subseteq K$, so every $T_n$ lies in $K$.

The child boxes are
$$
K_L=\left[-\frac{41}{9},-\frac{31}{9}\right]\times\left[\frac{196}{99},\frac{200}{99}\right],
$$
$$
K_M=\left[-\frac59,\frac59\right]\times\left[-\frac{2}{99},\frac{2}{99}\right],
$$
$$
K_R=\left[\frac{40}{9},\frac{50}{9}\right]\times\left[-\frac{200}{99},-\frac{196}{99}\right].
$$
Hence
$$
x(K_L)<x(K_M)<x(K_R).
$$

Now control secant slopes. At level $1$ the three slopes are
$$
\operatorname{slope}(t_L,t_M)=-\frac12,\qquad
\operatorname{slope}(t_M,t_R)=-\frac25,\qquad
\operatorname{slope}(t_L,t_R)=-\frac49,
$$
so all lie in $[-1,0]$. Inductively:

- same-child slopes are multiplied by $(1/100)/(1/10)=1/10$, so remain in $[-1,0]$;
- different-child slopes, read off from the three boxes above, are also in $[-1,0]$.

Therefore every secant slope in every $T_n$ lies in $[-1,0]$, and every secant of a top-level child block has slope in
$$
\left[-\frac{1}{10},0\right].
$$

Now verify the three separated-position inequalities.

For an $L$-secant, at the furthest relevant rightward point $x=50/9$,
$$
y\ge \frac{196}{99}-\frac{1}{10}\left(\frac{50}{9}+\frac{31}{9}\right)
=\frac{196}{99}-\frac{9}{10}
=\frac{1069}{990}>1,
$$
while every point of $K_M\cup K_R$ has $y\le 2/99<1$. So every $L$-secant lies strictly above $M\cup R$.

For an $M$-secant, at $x=-41/9$,
$$
y\le \frac{2}{99}+\frac{1}{10}\left(\frac59+\frac{41}{9}\right)
=\frac{2}{99}+\frac{23}{45}
<\frac{196}{99},
$$
while every point of $K_L$ has $y\ge 196/99$; and at $x=50/9$,
$$
y\ge -\frac{2}{99}-\frac{1}{10}\left(\frac{50}{9}+\frac59\right)
=-\frac{2}{99}-\frac{11}{18}
>-\frac{196}{99},
$$
while every point of $K_R$ has $y\le -196/99$. So every $M$-secant lies strictly below $L$ and strictly above $R$.

For an $R$-secant, at the furthest relevant leftward point $x=-41/9$,
$$
y\le -\frac{196}{99}+\frac{1}{10}\left(\frac{50}{9}+\frac{41}{9}\right)
=-\frac{196}{99}+\frac{91}{90}
<-\frac{2}{99},
$$
while every point of $K_L\cup K_M$ has $y\ge -2/99$. So every $R$-secant lies strictly below $L\cup M$.

Thus the template satisfies the ternary separated-position hypotheses.

## 2. Correct bridge maps and first-generation conjugates

By definition,
$$
\alpha_0=\Phi_M^{-1}\Phi_L,\qquad \beta_0=\Phi_M^{-1}\Phi_R.
$$
Since
$$
A^{-1}=\begin{pmatrix}10&0\\0&100\end{pmatrix},
$$
we get
$$
\alpha_0(z)=z+A^{-1}(t_L-t_M)=z+(-40,200),
$$
$$
\beta_0(z)=z+A^{-1}(t_R-t_M)=z+(50,-200).
$$

For a common linear part $A$, the exact general formula is
$$
\Phi_k^{-1}\alpha_0\Phi_i
=\mathrm{id}+A^{-2}(t_L-t_M)+A^{-1}(t_i-t_k),
$$
$$
\Phi_k^{-1}\beta_0\Phi_j
=\mathrm{id}+A^{-2}(t_R-t_M)+A^{-1}(t_j-t_k).
$$

Here
$$
A^{-2}(t_L-t_M)=(-400,20000),\qquad
A^{-2}(t_R-t_M)=(500,-20000),
$$
and
$$
A^{-1}(t_i-t_k)=
\begin{array}{c|ccc}
 & i=L & i=M & i=R\\ \hline
k=L & (0,0) & (40,-200) & (90,-400)\\
k=M & (-40,200) & (0,0) & (50,-200)\\
k=R & (-90,400) & (-50,200) & (0,0)
\end{array}
$$
with the same table for the $(j,k)$ term in the $\beta$-slot.

So the whole first-generation family is
$$
\Phi_k^{-1}\alpha_0\Phi_i=\mathrm{id}+u_{k,i},
\qquad
u_{k,i}=(-400,20000)+A^{-1}(t_i-t_k),
$$
$$
\Phi_k^{-1}\beta_0\Phi_j=\mathrm{id}+v_{k,j},
\qquad
v_{k,j}=(500,-20000)+A^{-1}(t_j-t_k).
$$

In particular, the required $(i,j,k)=(M,M,M)$ instance is
$$
\Phi_M^{-1}\alpha_0\Phi_M=\mathrm{id}+(-400,20000),
$$
$$
\Phi_M^{-1}\beta_0\Phi_M=\mathrm{id}+(500,-20000).
$$

## 3. First exact obstruction

The currently tracked bridge state is only
$$
U_m(\lambda,r)=H_{m-1}^+[\alpha_0,\beta_0](\lambda,r),
\qquad
D_m(\ell,\rho)=H_{m-1}^-[\alpha_0,\beta_0](\ell,\rho),
$$
so it tracks only the single pair
$$
(\alpha_0,\beta_0)
=\bigl(\mathrm{id}+(-40,200),\ \mathrm{id}+(50,-200)\bigr).
$$

But the exact expansion
$$
H_n^\pm[\alpha_0,\beta_0](\Phi_i(x'),\Phi_j(y'))
=
\sum_{k\in\{L,M,R\}}
H_{n-1}^\pm[\Phi_k^{-1}\alpha_0\Phi_i,\Phi_k^{-1}\beta_0\Phi_j](x',y')
$$
already contains, at $(i,j,k)=(M,M,M)$, the new term
$$
H_{n-1}^\pm[\mathrm{id}+(-400,20000),\mathrm{id}+(500,-20000)](x',y').
$$

This pair is not one of the tracked bridge types, since
$$
(-400,20000)\neq(-40,200),\qquad (500,-20000)\neq(50,-200).
$$

It is also not removed by template symmetry. Indeed, any affine symmetry $S(z)=Lz+b$ satisfying
$$
S\Phi_s=\Phi_{\pi(s)}S
$$
must have $LA=AL$. Since $A=\operatorname{diag}(1/10,1/100)$ has distinct eigenvalues, $L$ is diagonal. On $x$-coordinates, such a symmetry must preserve the asymmetric three-point set
$$
\{-4,0,5\},
$$
so it is already forced to be the identity on $x$. Then it also fixes the point labels, and hence is the identity on the whole template. Therefore there is no nontrivial symmetry identifying the new pair with $(\alpha_0,\beta_0)$.

Hence the corrected computation proves the exact obstruction:
$$
\text{the currently tracked bridge state } \{A_m,B_m,U_m,D_m\}\text{ fails to close already at first expansion.}
$$

This does **not** prove that no larger finite enlarged family can close; it only identifies the first exact obstruction to closure of the presently tracked bridge pair.
```
