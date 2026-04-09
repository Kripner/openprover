Use [[lemmas/ternary-one-split-structure]] and [[attempts/alternative-construction-balanced-ternary-split]].

Work on exactly one task: determine whether the new bridge-state quantities in the balanced ternary recursion actually propagate recursively from level $m-1$, or whether closure already fails there.

Context you should take as established:
- The local ternary split lemma is verified.
- The total count $C_m(k)$ has already been decomposed exactly into one-child, two-child, and bridge-weighted three-child terms in [[attempts/alternative-construction-balanced-ternary-split]].
- The verifier-approved gap is that the note did not derive recursive formulas for the bridge quantities
$$
U_m(\lambda,r),\qquad D_m(\ell,\rho),
$$
so the claim of an “exact closed enlarged-state recursion” is currently unjustified.

Deliverable:
1. Decide exactly one of these:
   - derive recursive propagation formulas for $U_m(\lambda,r)$ and $D_m(\ell,\rho)$ in the fixed balanced ternary template, enough to justify that the enlarged state truly closes; or
   - prove/identify the first exact obstruction showing that these bridge quantities are not determined by the previously tracked endpoint-refined state in any clean closed way.
2. Be explicit about what data the bridge quantities depend on.
   - If closure works, state the minimal exact state and give the exact recursion.
   - If closure fails, point to the first exact place where two configurations with the same currently tracked state can have different bridge counts.
3. Keep exact identities separate from inequalities.
4. Do not pursue asymptotic estimates unless they fall out immediately after resolving closure.
5. Output repo-ready markdown with a `Summary:` line.
   - If closure works, a suitable slug is `status/balanced-ternary-recursion-closure`.
   - If closure fails, a suitable slug is `status/balanced-ternary-bridge-state-obstruction`.

Requirements:
- Focus only on the bridge-state closure question.
- Do not redo the local ternary geometry from scratch.
- Do not revisit binary endpoint matching, binary lag variants, or nonrecursive constructions.
- If you use a counterexample/obstruction, make it precise and self-contained.
- If you derive closure only after enlarging the state further, say exactly what extra state is needed and why.
