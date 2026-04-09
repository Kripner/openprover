Use [[lemmas/one-split-structure-spanning-convex-subsets]], [[lemmas/one-split-fixed-state-recurrence]], [[lemmas/one-split-crossing-cup-cap-identities]], and [[status/fixed-lag-separated-recursions-obstruction]] only as binary background.

Work on exactly one task: analyze a single geometric split with three blocks in left-middle-right separated position, and classify the convex subsets that meet more than one block.

Setup:
- Consider three point sets $L,M,R$ in general position.
- Assume a clean ternary separated geometry: all $x$-coordinates in $L$ are left of those in $M$, which are left of those in $R$; and the blocks are placed so that every line through two points of an earlier block lies above every later block, and every line through two points of a later block lies below every earlier block, in the natural left-to-right sense needed to force monotone hull behavior.
- If this formulation is not quite the right one, replace it by a precise equivalent geometric hypothesis that makes the structure theorem true.

Deliverable:
1. State a precise ternary one-split lemma for convex subsets of $L\sqcup M\sqcup R$.
2. Classify separately:
   - subsets meeting exactly two blocks;
   - subsets meeting all three blocks.
3. Identify the exact chain types involved on each block (for example cup/cap behavior or another clean notion if binary terminology is insufficient).
4. Say explicitly which formulas/claims are exact identities and which are only inequalities.
5. Output repo-ready markdown with a `Summary:` line.
   - Suitable slug if successful: `lemmas/ternary-one-split-structure`.
   - If the natural ternary formulation breaks, give a clean obstruction note instead with a suitable slug under `attempts/`.

Requirements:
- Do not analyze the full recursion $T_m$ yet.
- Do not attempt asymptotic counting.
- Do not revisit binary lag variants.
- Keep the task local: one ternary split only.
- The note should be self-contained and make clear why this local classification is the necessary next step before any ternary recurrence can be written.
