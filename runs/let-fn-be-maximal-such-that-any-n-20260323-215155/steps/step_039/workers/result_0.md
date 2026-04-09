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