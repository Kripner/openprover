---
call_num: 8
label: verifier_21_0
model: gpt-5.4
elapsed_ms: 135016
input_tokens: 39345
output_tokens: 7010
cache_read_tokens: 32000
stop_reason: completed
---

======== SYSTEM PROMPT ========

You are an independent verifier reviewing a mathematician's work.

You will receive the original task and the worker's output. Your job is to independently verify the correctness of the worker's reasoning and conclusions.

IMPORTANT: Do NOT verify formal Lean code statements - those are checked automatically by the system. Focus on:
- Informal mathematical reasoning and proofs
- Logical gaps or unjustified steps
- Incorrect claims or conclusions
- Whether the task was actually completed as requested

End your response with exactly one of:
VERDICT: CORRECT
VERDICT: CRITICALLY FLAWED - <brief reason>
VERDICT: NEEDS MINOR FIXES - <brief reason>

Be concise. Use $inline$ and $$display$$ LaTeX.


======== USER PROMPT ========

# Original Task

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


# Worker Output

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

# Your Task

Independently verify the worker's output above. Do not verify formal Lean code - focus on informal reasoning, logical correctness, and whether the task was completed as requested.

======== RESPONSE ========

The core argument is sound. In particular:

- Gap (1) is repaired correctly: if the upper chain had at least two $L$-vertices, choosing the last two forces them to be consecutive because any intermediate chain vertex would have intermediate $x$-coordinate and hence also lie in $L$.
- Gap (2) is repaired correctly: the proof uses the literal endpoint-aware fact that every non-endpoint lies on exactly one hull chain, while the common endpoints $\ell,r$ lie on both.

Under the stated hypotheses, the main structural conclusion is justified:
$$
U(S)=\ell,\; \text{all points of }S\cap R\text{ in increasing }x,
\qquad
D(S)=\text{all points of }S\cap L\text{ in increasing }x,\; r.
$$
So the decomposition of any spanning convex subset $S$ into a left lower-chain piece and a right upper-chain piece is proved rigorously.

One wording issue remains. The sentence
$$
\text{“}S\cap R\text{ is exactly the upper-hull chain in }R\text{ from }\rho\text{ to }r\text{”}
$$
is stronger or at least more ambiguous than what was proved from hypotheses (1)–(3). What is proved is that $S\cap R$ is the portion of the upper hull chain of $S$ consisting of points from $R$ (hence it forms a cup), and similarly $S\cap L$ is the portion of the lower hull chain of $S$ in $L$. If the author wants an ambient statement about hull chains of $R$ and $L$ themselves, that ambient cup/cap structure must be stated separately.

The endpoint-state paragraph is otherwise fine: $(\ell,\lambda,\rho,r)$ is clearly sufficient for later recurrence bookkeeping, even if “minimal” is justified informally rather than proved.

VERDICT: NEEDS MINOR FIXES - ambiguous “upper-hull chain in $R$ / lower-hull chain in $L$” wording exceeds the stated hypotheses
