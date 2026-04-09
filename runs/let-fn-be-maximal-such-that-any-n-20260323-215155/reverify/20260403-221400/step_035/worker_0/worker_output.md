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