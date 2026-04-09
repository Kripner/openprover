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
