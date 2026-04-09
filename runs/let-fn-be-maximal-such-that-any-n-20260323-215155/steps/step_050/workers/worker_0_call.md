---
call_num: 4
label: worker_50_0
model: gpt-5.4
elapsed_ms: 291703
input_tokens: 81029
output_tokens: 15904
cache_read_tokens: 53504
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

Focus only on the lower-bound side.

Context:
- For an n-point set P in general position, let
  $$g(P):=\#\\{A\\subseteq P: A\\text{ is in convex position}\\},$$
  and let
  $$f(n):=\\min_{|P|=n} g(P).$$
- Verified: [[bounds/lower-bound-averaging]] gives
  $$f(n)\\ge 2^{(\\frac14-o(1))(\\log_2 n)^2}.$$
- Verified barriers:
  1. [[status/multi-k-averaging-barrier]] shows that summing the per-k averaging bounds over all admissible k still has quadratic constant $\\frac14$.
  2. [[status/multiplicity-aware-averaging-barrier]] shows that, for fixed k, enlarging the witness size m and counting all convex k-subsets inside each m-subset also collapses back to the original bound.

Task:
Investigate the next natural averaging mechanism beyond those two barriers: average the full total-count lower bound over m-subsets.

Concretely, for fixed m \\le n, every m-subset Q \\subseteq P satisfies
$$g(Q)\\ge f(m).$$
Set up the exact double count obtained by summing g(Q) over all m-subsets of P, i.e. count pairs
$$(A,Q)\\quad\\text{with }A\\subseteq Q\\subseteq P,\\ |Q|=m,\\ A\\text{ convex}.$$

Determine the focused question:
Can any asymptotic choice of m, combined only with the currently verified lower bound on f(m), produce a lower bound on f(n) whose quadratic coefficient beats $\\frac14$?
Or does this subset-bootstrapping route also close up as a barrier?

What I need:
1. The exact weighted inequality relating $\\sum_{|Q|=m} g(Q)$ to the size-by-size counts $\\mathrm{conv}_t(P)$ or directly to $g(P)$.
2. Either:
   - a concrete improvement beyond quadratic constant $\\frac14$, or
   - a precise barrier statement showing that bootstrapping through m-subsets and the current lower bound on f(m) still cannot raise the coefficient.
3. Repo-item-ready markdown if successful.

Requirements:
- Keep it self-contained.
- Use only current repo facts; no literature/web.
- Do not branch into upper-bound constructions or unrelated mechanisms.
- This is one focused question: does averaging the full lower bound f(m) over m-subsets bootstrap the constant past $\\frac14$?


# Referenced Materials

## [[bounds/lower-bound-averaging]]

Summary: Verified Erdős-Szekeres averaging proof that $f(n)\ge 2^{(\frac14-o(1))(\log_2 n)^2}$.

Let
\[
g(P):=\#\{A\subseteq P: A\text{ is in convex position}\},
\qquad
\mathrm{conv}_k(P):=\#\{A\subseteq P: |A|=k,\ A\text{ is in convex position}\}.
\]
Then
\[
f(n)=\min_{|P|=n} g(P).
\]

We prove a clean lower bound using only the Erdős-Szekeres theorem and Suk's asymptotic bound on the Erdős-Szekeres numbers.

## Proposition
Fix $k\ge 3$, and let $m:=ES(k)$. If $P$ is an $n$-point set in general position with $n\ge m$, then
\[
\mathrm{conv}_k(P)\ge \frac{\binom{n}{k}}{\binom{m}{k}}.
\]

### Proof
Consider the set
\[
\mathcal X:=\{(A,Q): A\subseteq Q\subseteq P,\ |A|=k,\ |Q|=m,\ A\text{ is in convex position}\}.
\]

We count $\mathcal X$ in two ways.

First, fix an $m$-subset $Q\subseteq P$. By the definition of $m=ES(k)$, every such $Q$ contains at least one $k$-subset in convex position. Hence each $Q$ contributes at least one pair $(A,Q)$, so
\[
|\mathcal X|\ge \binom{n}{m}.
\]

Second, fix a convex $k$-subset $A\subseteq P$. The number of $m$-subsets $Q\subseteq P$ containing $A$ is exactly
\[
\binom{n-k}{m-k}.
\]
Therefore
\[
|\mathcal X|=\mathrm{conv}_k(P)\binom{n-k}{m-k}.
\]

Comparing the two counts gives
\[
\mathrm{conv}_k(P)\binom{n-k}{m-k}\ge \binom{n}{m},
\]
hence
\[
\mathrm{conv}_k(P)\ge \frac{\binom{n}{m}}{\binom{n-k}{m-k}}
= \frac{\binom{n}{k}}{\binom{m}{k}}.
\]
The last identity is
\[
\binom{n}{m}\binom{m}{k}=\binom{n}{k}\binom{n-k}{m-k}.
\]
This proves the proposition. ∎

As a consequence, for every $k$ with $ES(k)\le n$ and every $n$-point set $P$,
\[
g(P)\ge \mathrm{conv}_k(P)\ge \frac{\binom{n}{k}}{\binom{ES(k)}{k}},
\]
so
\[
f(n)\ge \frac{\binom{n}{k}}{\binom{ES(k)}{k}}.
\]

## Asymptotic optimization
Use Suk's bound in the form
\[
ES(k)=2^{k+\varepsilon_k k},\qquad \varepsilon_k\to 0.
\]

Let
\[
L:=\log_2 n,\qquad k:=\Big\lfloor \frac{L}{2}\Big\rfloor.
\]
Then $k=(\tfrac12+o(1))L$, so
\[
\log_2 ES(k)=k+\varepsilon_k k=(\tfrac12+o(1))L<L
\]
for all sufficiently large $n$. Thus $ES(k)\le n$, and the previous bound applies.

Now
\[
\frac{\binom{n}{k}}{\binom{ES(k)}{k}}
=\prod_{i=0}^{k-1}\frac{n-i}{ES(k)-i}
\ge \left(\frac{n-k+1}{ES(k)}\right)^k.
\]
Taking $\log_2$,
\[
\log_2 f(n)\ge k\bigl(\log_2(n-k+1)-\log_2 ES(k)\bigr).
\]

Since $k=O(\log n)=o(n)$, we have $\log_2(n-k+1)=L+o(1)$. Also $\log_2 ES(k)=k+\varepsilon_k k$. Therefore
\[
\log_2 f(n)\ge k\bigl(L-k-\varepsilon_k k+o(1)\bigr).
\]
Now
\[
kL-k^2=\frac14L^2+O(L),\qquad
\varepsilon_k k^2=o(L^2),\qquad
k\cdot o(1)=o(L),
\]
so
\[
\log_2 f(n)\ge \frac14L^2-o(L^2).
\]

Hence
\[
f(n)\ge 2^{(\frac14-o(1))(\log_2 n)^2}.
\]

This is asymptotically optimal for this argument: if $k=\alpha\log_2 n$, then the main term is
\[
(\alpha-\alpha^2)(\log_2 n)^2,
\]
maximized at $\alpha=\tfrac12$.

## Final forms
Using base-$2$ logarithms,
\[
f(n)\ge 2^{(\frac14-o(1))(\log_2 n)^2}.
\]

Using natural logarithms,
\[
f(n)\ge \exp\!\left(\left(\frac{1}{4\ln 2}-o(1)\right)(\ln n)^2\right).
\]

Indeed,
\[
2^{(\frac14-o(1))(\log_2 n)^2}
=\exp\!\left((\tfrac14-o(1))\ln 2\cdot \frac{(\ln n)^2}{(\ln 2)^2}\right)
=\exp\!\left(\left(\frac{1}{4\ln 2}-o(1)\right)(\ln n)^2\right).
\]

So the Erdős-Szekeres input alone yields the lower bound
\[
f(n)\ge 2^{(\frac14-o(1))(\log_2 n)^2}
=\exp\!\left(\left(\frac{1}{4\ln 2}-o(1)\right)(\ln n)^2\right).
\]

## [[status/multi-k-averaging-barrier]]

Summary: Summing the verified per-$k$ averaging bounds over all admissible $k$ still gives only $2^{(\frac14+o(1))(\log_2 n)^2}$, so pure averaging over $k$ does not improve the quadratic constant.

Let
\[
\mathrm{conv}_j(P):=\#\{A\subseteq P: |A|=j,\ A\text{ is in convex position}\},
\qquad
g(P):=\#\{A\subseteq P: A\text{ is in convex position}\}.
\]
Since every convex subset has a unique size, the size classes are disjoint, so for every $P$
\[
g(P)=\sum_{j\ge 1}\mathrm{conv}_j(P).
\tag{1}
\]

Now fix $n$, and let
\[
A(n):=\{k\ge 1: ES(k)\le n\}.
\]
For $k=1,2$ we have $ES(1)=1$, $ES(2)=2$, and every $1$- or $2$-subset is in convex position, hence
\[
\mathrm{conv}_1(P)=n=\frac{\binom{n}{1}}{\binom{ES(1)}{1}},
\qquad
\mathrm{conv}_2(P)=\binom{n}{2}=\frac{\binom{n}{2}}{\binom{ES(2)}{2}}.
\]
For $k\ge 3$ with $ES(k)\le n$, the verified averaging proposition from [[bounds/lower-bound-averaging]] gives
\[
\mathrm{conv}_k(P)\ge \frac{\binom{n}{k}}{\binom{ES(k)}{k}}.
\]
Therefore, summing over the disjoint size classes in (1),
\[
g(P)\ge \sum_{k\in A(n)}\mathrm{conv}_k(P)
   \ge \sum_{k\in A(n)}\frac{\binom{n}{k}}{\binom{ES(k)}{k}}
   = S(n),
\tag{2}
\]
where
\[
S(n):=\sum_{k:ES(k)\le n}\frac{\binom{n}{k}}{\binom{ES(k)}{k}}.
\]
In particular, after minimizing over $P$,
\[
f(n):=\min_{|P|=n}g(P)\ge S(n).
\tag{3}
\]

## Proposition
With $L=\log_2 n$,
\[
\log_2 S(n)=\left(\frac14+o(1)\right)L^2.
\]

### Lower bound
Let
\[
k:=\Big\lfloor \frac L2\Big\rfloor.
\]
By Suk’s asymptotic,
\[
ES(k)=2^{k+o(k)}.
\]
Since $k=(\tfrac12+o(1))L$, we have
\[
\log_2 ES(k)=k+o(k)=(\tfrac12+o(1))L<L
\]
for all sufficiently large $n$. Thus $k\in A(n)$, so one term of $S(n)$ yields
\[
S(n)\ge \frac{\binom{n}{k}}{\binom{ES(k)}{k}}
      = \prod_{i=0}^{k-1}\frac{n-i}{ES(k)-i}
      \ge \left(\frac{n-k+1}{ES(k)}\right)^k.
\]
Taking $\log_2$,
\[
\log_2 S(n)\ge k\bigl(\log_2(n-k+1)-\log_2 ES(k)\bigr).
\]
Here $k=O(L)=o(n)$, so
\[
\log_2(n-k+1)=L+o(1),
\]
and also
\[
\log_2 ES(k)=k+o(k).
\]
Hence
\[
\log_2 S(n)\ge k\bigl(L-k-o(k)+o(1)\bigr).
\]
Since $k=\frac12L+O(1)$, this gives
\[
kL-k^2=\frac14L^2+O(L),\qquad k\,o(k)=o(L^2),\qquad k\,o(1)=o(L),
\]
so
\[
\log_2 S(n)\ge \frac14L^2-o(L^2).
\tag{4}
\]

### Upper bound
Write
\[
S(n)=n+\binom n2+\sum_{\substack{k\ge 3\\ ES(k)\le n}}
\frac{\binom{n}{k}}{\binom{ES(k)}{k}}.
\]
Fix $k\ge 3$, and put $m:=ES(k)$. Then
\[
\frac{\binom{n}{k}}{\binom{m}{k}}
=\prod_{i=0}^{k-1}\frac{n-i}{m-i}
\le \left(\frac{n}{m-k+1}\right)^k.
\]
Using the standard lower bound $ES(k)\ge 2^{k-2}+1$,
\[
m-k+1\ge 2^{k-2}-k+2.
\]
Also $2^{k-3}\ge k-2$ for all $k\ge 3$, so
\[
2^{k-2}-k+2\ge 2^{k-3}.
\]
Therefore
\[
\frac{\binom{n}{k}}{\binom{ES(k)}{k}}
\le \left(\frac{n}{2^{k-3}}\right)^k
=2^{kL-k^2+3k}.
\tag{5}
\]

Moreover, if $ES(k)\le n$, then $2^{k-2}+1\le n$, so
\[
k\le \log_2(n-1)+2\le L+2.
\]
Thus there are at most $L+2$ admissible values $k\ge 3$. From (5),
\[
\sum_{\substack{k\ge 3\\ ES(k)\le n}}
\frac{\binom{n}{k}}{\binom{ES(k)}{k}}
\le (L+2)\max_{k\ge 3} 2^{kL-k^2+3k}.
\]
Now
\[
kL-k^2+3k
= -\left(k-\frac{L+3}{2}\right)^2+\frac{(L+3)^2}{4},
\]
so
\[
\max_{k\ge 3}(kL-k^2+3k)\le \frac{(L+3)^2}{4}
=\frac14L^2+O(L).
\]
Hence
\[
\sum_{\substack{k\ge 3\\ ES(k)\le n}}
\frac{\binom{n}{k}}{\binom{ES(k)}{k}}
\le 2^{\frac14L^2+O(L)}.
\]
Since
\[
n+\binom n2 = 2^{O(L)},
\]
we conclude
\[
S(n)\le 2^{\frac14L^2+O(L)}.
\]
Therefore
\[
\log_2 S(n)\le \frac14L^2+o(L^2).
\tag{6}
\]

Combining (4) and (6),
\[
\log_2 S(n)=\left(\frac14+o(1)\right)L^2.
\]

## Consequence: the averaging barrier
Any argument that uses only the verified size-$k$ estimates
\[
\mathrm{conv}_k(P)\ge \frac{\binom{n}{k}}{\binom{ES(k)}{k}}
\qquad (ES(k)\le n)
\]
and then sums them over some admissible set $K(n)\subseteq A(n)$ can prove at most
\[
g(P)\ge \sum_{k\in K(n)}\frac{\binom{n}{k}}{\binom{ES(k)}{k}}
\le S(n).
\]
Hence every such pure averaging bound has logarithm at most
\[
\log_2 S(n)=\left(\frac14+o(1)\right)L^2.
\]
On the other hand, the single best $k$ already gives
\[
\left(\frac14-o(1)\right)L^2
\]
by the lower-bound argument above. So summing the verified per-$k$ averaging estimates over all admissible $k$ changes only lower-order terms: it does not improve the quadratic constant beyond $\frac14$.


## [[status/multiplicity-aware-averaging-barrier]]

Summary: Counting all convex $k$-subsets inside each $m$-subset gives an exact weighted identity, but with only the Erdős-Szekeres threshold input it collapses to the original fixed-$k$ averaging bound and still cannot beat quadratic constant $\frac14$.

Let
\[
\mathrm{conv}_k(P):=\#\{A\subseteq P:\ |A|=k,\ A\text{ is in convex position}\},
\]
and
\[
g(P):=\#\{A\subseteq P: A\text{ is in convex position}\},
\qquad
f(n):=\min_{|P|=n} g(P).
\]
For integers $m\ge k$, define
\[
h(m,k):=\min_{|Q|=m}\mathrm{conv}_k(Q),
\]
where the minimum is over $m$-point sets in general position.

We ask whether, for fixed $k$, using a larger witness size $m\ge ES(k)$ and counting all convex $k$-subsets inside each $m$-subset can improve the lower bound from [[bounds/lower-bound-averaging]].

## Proposition: exact multiplicity-weighted double count

Let $P$ be an $n$-point set in general position, with $n\ge m\ge k$. Then
\[
\sum_{\substack{Q\subseteq P\\ |Q|=m}} \mathrm{conv}_k(Q)
=
\binom{n-k}{m-k}\,\mathrm{conv}_k(P).
\tag{1}
\]

Consequently,
\[
\mathrm{conv}_k(P)\ge h(m,k)\frac{\binom{n}{m}}{\binom{n-k}{m-k}}
= h(m,k)\frac{\binom{n}{k}}{\binom{m}{k}}.
\tag{2}
\]

### Proof
Count pairs
\[
\mathcal X:=\{(A,Q): A\subseteq Q\subseteq P,\ |A|=k,\ |Q|=m,\ A\text{ is in convex position}\}.
\]

If $Q$ is fixed, it contributes exactly $\mathrm{conv}_k(Q)$ pairs. Therefore
\[
|\mathcal X|
=
\sum_{\substack{Q\subseteq P\\ |Q|=m}} \mathrm{conv}_k(Q).
\]

If a convex $k$-subset $A\subseteq P$ is fixed, then the number of $m$-subsets $Q\subseteq P$ containing $A$ is exactly
\[
\binom{n-k}{m-k}.
\]
Hence
\[
|\mathcal X|=\binom{n-k}{m-k}\,\mathrm{conv}_k(P).
\]
This proves (1).

Now each $m$-subset $Q$ satisfies $\mathrm{conv}_k(Q)\ge h(m,k)$ by definition, so
\[
|\mathcal X|\ge h(m,k)\binom{n}{m}.
\]
Combining with (1) gives
\[
\binom{n-k}{m-k}\,\mathrm{conv}_k(P)\ge h(m,k)\binom{n}{m},
\]
which is equivalent to (2).

## Corollary: density monotonicity

For $n\ge m\ge k$,
\[
h(n,k)\ge h(m,k)\frac{\binom{n}{k}}{\binom{m}{k}}.
\tag{3}
\]
Equivalently, the worst-case density
\[
\delta(t,k):=\frac{h(t,k)}{\binom{t}{k}}
\]
is nondecreasing in $t$.

### Proof
Apply (2) to an arbitrary $n$-point set $P$, then minimize over all such $P$.

## Barrier from current inputs

Take $m_0:=ES(k)$. By definition of $ES(k)$, every $m_0$-point set contains at least one convex $k$-subset, so
\[
h(m_0,k)\ge 1.
\]
Applying (3) with $m=m_0$ gives, for every $m\ge ES(k)$,
\[
h(m,k)\ge \frac{\binom{m}{k}}{\binom{ES(k)}{k}}.
\tag{4}
\]

Substituting (4) into the multiplicity-aware bound (2) yields
\[
\mathrm{conv}_k(P)\ge
\frac{\binom{m}{k}}{\binom{ES(k)}{k}}
\cdot
\frac{\binom{n}{k}}{\binom{m}{k}}
=
\frac{\binom{n}{k}}{\binom{ES(k)}{k}}.
\tag{5}
\]

But (5) is exactly the original bound from [[bounds/lower-bound-averaging]].

So the strengthened argument with larger witness size $m$ is transitive: with only the current universal input
\[
h(ES(k),k)\ge 1,
\]
it produces no stronger fixed-$k$ estimate than the original $m=ES(k)$ argument.

## Asymptotic consequence

The multiplicity-aware route yields, for each admissible $k$,
\[
\mathrm{conv}_k(P)\ge \frac{\binom{n}{k}}{\binom{ES(k)}{k}},
\]
and no better bound follows from the currently available fixed-$k$ inputs.

Therefore its asymptotic optimization is exactly the same as in [[bounds/lower-bound-averaging]]:

- Using Suk's asymptotic $ES(k)=2^{k+o(k)}$ and choosing
  \[
  k=\Big\lfloor \frac12\log_2 n\Big\rfloor,
  \]
  one gets
  \[
  \log_2 \mathrm{conv}_k(P)\ge \left(\frac14-o(1)\right)(\log_2 n)^2.
  \]

- Conversely, from the standard lower bound $ES(k)\ge 2^{k-2}+1$,
  \[
  \frac{\binom{n}{k}}{\binom{ES(k)}{k}}
  \le 2^{k\log_2 n-k^2+O(k)},
  \]
  whose quadratic term is maximized at $k=\frac12\log_2 n+O(1)$ and is at most
  \[
  \frac14(\log_2 n)^2+O(\log n).
  \]

Hence no asymptotic choice of $m,k$ obtainable from the current repo facts can beat the quadratic coefficient $\frac14$.

## Conclusion

Multiplicity-aware averaging improves the formulation but not the bound with current inputs.

The exact inequality is
\[
\mathrm{conv}_k(P)\ge h(m,k)\frac{\binom{n}{k}}{\binom{m}{k}}.
\]
However, the only universal lower bound on $h(m,k)$ presently available from the repo is
\[
h(m,k)\ge \frac{\binom{m}{k}}{\binom{ES(k)}{k}},
\]
which makes the factor $\binom{m}{k}$ cancel and recovers the original estimate.

Therefore this strengthened fixed-size averaging route also stalls at the same quadratic constant: optimizing over $k$ still yields only
\[
\left(\frac14+o(1)\right)(\log_2 n)^2
\]
on the logarithmic scale, with the matching lower side already achieved by the known choice $k\sim \frac12\log_2 n$.


======== RESPONSE ========

The route also closes as a barrier.

The exact double count is
\[
\sum_{\substack{Q\subseteq P\\ |Q|=m}} g(Q)
=
\sum_{t=1}^m \binom{n-t}{m-t}\,\mathrm{conv}_t(P),
\]
because each convex \(t\)-subset \(A\subseteq P\) is contained in exactly \(\binom{n-t}{m-t}\) \(m\)-subsets. Since every \(m\)-subset \(Q\) satisfies \(g(Q)\ge f(m)\),
\[
\sum_{t=1}^m \binom{n-t}{m-t}\,\mathrm{conv}_t(P)\ge \binom{n}{m}f(m).
\]
Using
\[
\binom{n-t}{m-t}=\binom{n}{m}\frac{\binom{m}{t}}{\binom{n}{t}},
\]
this is equivalently
\[
\sum_{t=1}^m \frac{\binom{m}{t}}{\binom{n}{t}}\,\mathrm{conv}_t(P)\ge f(m).
\tag{*}
\]

A crude corollary is
\[
g(P)\ge \frac{n}{m}f(m),
\]
since \(\binom{n-t}{m-t}\le \binom{n-1}{m-1}\). Plugging in the verified bound
\[
f(m)\ge 2^{(\frac14-o(1))(\log_2 m)^2}
\]
already gives no coefficient beyond \(\frac14\). But even the full weighted inequality \((*)\) still cannot do better.

Suggested repo note: `status/m-subset-total-count-bootstrapping-barrier.md`

```markdown
Summary: Averaging the full lower bound $g(Q)\ge f(m)$ over all $m$-subsets gives the exact weighted inequality
\[
\sum_{t=1}^m \frac{\binom{m}{t}}{\binom{n}{t}}\,\mathrm{conv}_t(P)\ge f(m).
\]
Using only the current repo bound
\[
f(m)\ge 2^{(\frac14-o(1))(\log_2 m)^2},
\]
this subset-bootstrapping mechanism still cannot force a lower bound for $f(n)$ with quadratic coefficient exceeding $\frac14$.

Let
\[
\mathrm{conv}_t(P):=\#\{A\subseteq P:\ |A|=t,\ A\text{ convex}\},
\qquad
g(P):=\sum_{t\ge 1}\mathrm{conv}_t(P).
\]

For $n\ge m$ and an $n$-point set $P$, count pairs
\[
(A,Q)\quad\text{with }A\subseteq Q\subseteq P,\ |Q|=m,\ A\text{ convex}.
\]
Fixing $Q$ contributes $g(Q)$ pairs, while fixing a convex $t$-subset $A$ contributes exactly $\binom{n-t}{m-t}$ choices of $Q$. Therefore
\[
\sum_{\substack{Q\subseteq P\\ |Q|=m}} g(Q)
=
\sum_{t=1}^m \binom{n-t}{m-t}\,\mathrm{conv}_t(P).
\tag{1}
\]
Since every $m$-subset satisfies $g(Q)\ge f(m)$,
\[
\sum_{t=1}^m \binom{n-t}{m-t}\,\mathrm{conv}_t(P)\ge \binom{n}{m}f(m).
\tag{2}
\]
Using
\[
\binom{n-t}{m-t}=\binom{n}{m}\frac{\binom{m}{t}}{\binom{n}{t}},
\]
(2) becomes
\[
\sum_{t=1}^m \frac{\binom{m}{t}}{\binom{n}{t}}\,\mathrm{conv}_t(P)\ge f(m).
\tag{3}
\]

Now insert only the currently verified lower bound
\[
f(m)\ge F(m):=2^{(\frac14-o(1))(\log_2 m)^2}.
\]
Write
\[
y_t:=\frac{\mathrm{conv}_t(P)}{\binom{n}{t}}\in[0,1].
\]
Then (3) implies
\[
\sum_{t=1}^m \binom{m}{t}y_t\ge F(m),
\qquad
g(P)\ge \sum_{t=1}^m \binom{n}{t}y_t.
\tag{4}
\]

So the strongest bound obtainable from this mechanism, using only the scalar input $f(m)\ge F(m)$, is the minimum of
\[
\sum_{t=1}^m \binom{n}{t}y_t
\]
subject to
\[
0\le y_t\le 1,
\qquad
\sum_{t=1}^m \binom{m}{t}y_t\ge F(m).
\tag{5}
\]
Since
\[
\frac{\binom{m}{t+1}/\binom{n}{t+1}}{\binom{m}{t}/\binom{n}{t}}
=\frac{m-t}{n-t}<1,
\]
the value-per-cost ratio decreases with $t$. Hence the minimizing solution fills the smallest sizes first. If $r$ is the least index such that
\[
\sum_{t=1}^r \binom{m}{t}\ge F(m),
\tag{6}
\]
then the extracted lower bound is at most
\[
\sum_{t=1}^r \binom{n}{t}.
\tag{7}
\]

Let $L:=\log_2 n$ and $M:=\log_2 m$. Fix $\varepsilon>0$ and set
\[
s:=\left\lceil \left(\frac14+\varepsilon\right)M\right\rceil.
\]
Then
\[
\binom{m}{s}\ge \left(\frac{m}{s}\right)^s,
\]
so
\[
\log_2 \binom{m}{s}
\ge s(M-\log_2 s)
=
\left(\frac14+\varepsilon\right)M^2-O(M\log M).
\]
Since $F(m)=2^{(\frac14-o(1))M^2}$, for large $m$ we have $F(m)\le \binom{m}{s}$, hence $r\le s$. Therefore
\[
\sum_{t=1}^r \binom{n}{t}\le r\,n^r,
\]
and so
\[
\log_2 f(n)\le \log_2(r\,n^r)
\le rL+o(L^2)
\le \left(\frac14+\varepsilon\right)ML+o(L^2)
\le \left(\frac14+\varepsilon\right)L^2+o(L^2).
\]
Because $\varepsilon>0$ is arbitrary,
\[
\log_2 f(n)\le \left(\frac14+o(1)\right)(\log_2 n)^2
\]
for every bound produced by this subset-bootstrapping route from the current input $f(m)\ge F(m)$.

Conclusion:
\[
\sum_{|Q|=m} g(Q)
=
\sum_{t=1}^m \binom{n-t}{m-t}\,\mathrm{conv}_t(P)
\]
is the exact identity, but feeding into it only the existing lower bound
\[
f(m)\ge 2^{(\frac14-o(1))(\log_2 m)^2}
\]
still cannot raise the quadratic coefficient past $\frac14$. So averaging the full total count over $m$-subsets is also a barrier.
```

I could not write the file in the workspace because the tool wrapper is failing with `bwrap: Unknown option --argv0`.
