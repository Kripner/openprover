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
