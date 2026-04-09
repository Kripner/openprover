A tight one-split note is:

\[
\textbf{Endpoint-refined one-split recurrences.}
\]

Let \(m\ge 2\), and write
\[
P_m=L_m\sqcup R_m
\]
for the recursive split from [[bounds/upper-bound-recursive-family]], in the normalized position from [[lemmas/one-split-structure-spanning-convex-subsets]].

For any normalized finite planar set \(X\), any \(t\ge 1\), and any \(a,b\in X\) with \(x(a)\le x(b)\), define
\[
\mathcal U_X(t;a,b)
:=\#\{T\subseteq X:\ |T|=t,\ T\text{ is a }t\text{-cup, leftmost}(T)=a,\ \text{rightmost}(T)=b\},
\]
\[
\mathcal D_X(t;a,b)
:=\#\{T\subseteq X:\ |T|=t,\ T\text{ is a }t\text{-cap, leftmost}(T)=a,\ \text{rightmost}(T)=b\}.
\]
Use the convention
\[
\mathcal U_X(1;a,b)=\mathcal D_X(1;a,b)=
\begin{cases}
1,&a=b,\\
0,&a\neq b.
\end{cases}
\]
This is the minimal useful local refinement: it keeps exactly the endpoint data of a cup or cap, including the degenerate one-point case needed when \(\ell=\lambda\) or \(\rho=r\).

Now let \(P=L\sqcup R\) satisfy the one-split hypotheses. For \(i,j\ge 1\) and
\[
\ell,\lambda\in L,\qquad \rho,r\in R,
\]
define
\[
\mathcal N_P(i,j;\ell,\lambda,\rho,r)
\]
to be the number of subsets \(S\subseteq P\) such that:
\[
|S\cap L|=i,\qquad |S\cap R|=j,
\]
\(S\) is in convex position, and its state is exactly \((\ell,\lambda,\rho,r)\). Also set
\[
\mathcal N_P(k;\ell,\lambda,\rho,r):=\sum_{i+j=k}\mathcal N_P(i,j;\ell,\lambda,\rho,r).
\]

Then the one-step recurrences are:

\[
\mathcal U_{P_m}(t;a,b)=
\begin{cases}
\mathcal U_{L_m}(t;a,b),&a,b\in L_m,\\
\mathcal U_{R_m}(t;a,b),&a,b\in R_m,\\
\displaystyle\sum_{\rho\in R_m}\mathcal U_{R_m}(t-1;\rho,b),&a\in L_m,\ b\in R_m,\ t\ge 2,\\
0,&a\in R_m,\ b\in L_m,
\end{cases}
\]
and
\[
\mathcal D_{P_m}(t;a,b)=
\begin{cases}
\mathcal D_{L_m}(t;a,b),&a,b\in L_m,\\
\mathcal D_{R_m}(t;a,b),&a,b\in R_m,\\
\displaystyle\sum_{\lambda\in L_m}\mathcal D_{L_m}(t-1;a,\lambda),&a\in L_m,\ b\in R_m,\ t\ge 2,\\
0,&a\in R_m,\ b\in L_m.
\end{cases}
\]

These are exact identities. The crossing cup identity is the endpoint-refined form of the accepted split fact that every spanning cup is exactly one point from \(L_m\) together with a cup from \(R_m\); similarly every spanning cap is exactly a cap from \(L_m\) together with one point from \(R_m\).

For spanning convex subsets, the one-split lemma gives the injection
\[
S\longmapsto (S\cap L_m,\ S\cap R_m),
\]
so for every state \((\ell,\lambda,\rho,r)\),
\[
\mathcal N_{P_m}(i,j;\ell,\lambda,\rho,r)
\le
\mathcal D_{L_m}(i;\ell,\lambda)\,\mathcal U_{R_m}(j;\rho,r),
\]
hence
\[
\mathcal N_{P_m}(k;\ell,\lambda,\rho,r)
\le
\sum_{i+j=k}\mathcal D_{L_m}(i;\ell,\lambda)\,\mathcal U_{R_m}(j;\rho,r).
\]

If \(\phi_L,\phi_R:P_{m-1}\to L_m,R_m\) are the affine copy maps, then affine invariance rewrites the crossing identities as
\[
\mathcal U_{P_m}(t;\phi_L(a),\phi_R(b))
=
\sum_{c\in P_{m-1}}\mathcal U_{P_{m-1}}(t-1;c,b),
\]
\[
\mathcal D_{P_m}(t;\phi_L(a),\phi_R(b))
=
\sum_{c\in P_{m-1}}\mathcal D_{P_{m-1}}(t-1;a,c),
\]
and
\[
\mathcal N_{P_m}(i,j;\phi_L(a),\phi_L(a'),\phi_R(b'),\phi_R(b))
\le
\mathcal D_{P_{m-1}}(i;a,a')\,\mathcal U_{P_{m-1}}(j;b',b).
\]

Exactly how endpoint matching is enforced is now transparent: \(\ell,r\) are the global outer endpoints of the spanning convex set, while \(\lambda,\rho\) are the two split-adjacent terminal endpoints of the local left and right chains. Thus a spanning set with state \((\ell,\lambda,\rho,r)\) can only contribute to a left cap with endpoints \((\ell,\lambda)\) and a right cup with endpoints \((\rho,r)\). Aggregate totals such as \(Q_+\) and \(Q_-\) forget precisely this four-point matching data.

I could not write this into the workspace because the local tool wrapper is failing with `bwrap: Unknown option --argv0`.