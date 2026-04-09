Summary: The latest information-loss patch failed because the stored fixed-state and crossing notes appear to use incompatible cup/cap conventions, so the exact crossing passage could not be justified self-containedly from the cited items.

Verification outcome:
- The proposed note correctly identified the later endpoint-forgetting inequality
  $$
  C_k(P_m)\le \sum_{a=2}^k Q_+(a,P_m)\,Q_-(k+2-a,P_m)
  $$
  as the step that discards matched outer endpoints $(\ell,r)$.
- However, its derivation of the crossing identities was not repo-stable, because [[lemmas/one-split-fixed-state-recurrence]] and [[lemmas/one-split-crossing-cup-cap-identities]] do not currently line up on which side carries cups versus caps / which quantities are named $Q_+$ and $Q_-$.
- As a result, the note could not honestly claim to derive the crossing passage directly from the stored items.

Use this item to avoid repeating the same patch before the convention audit is done.