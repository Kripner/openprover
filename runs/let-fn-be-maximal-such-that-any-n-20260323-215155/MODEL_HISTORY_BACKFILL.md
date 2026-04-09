# Model History Backfill

Manual backfill created on 2026-04-01 for this existing run folder.

This note is based only on artifacts already present in the run:

- `trace.log`
- `run_config.toml`
- `steps/*/*.raw.json`
- `steps/*/workers/*.raw.json`

## Confidence

- `confirmed`: directly visible in a raw payload or explicit trace line
- `inferred`: the most likely interpretation of the run state, but not directly persisted in old metadata
- `unknown`: not recoverable from this folder

## Main findings

1. `run_config.toml` is not a reliable history source for resumed runs.
   It still says `planner_provider = "claude"` and `worker_provider = "claude"`, but the run clearly used both Claude and Codex later.

2. Planner history is easy to recover.
   The planner was Claude Opus early, Codex `gpt-5.4` through the long middle section, then Claude Opus again for the final proof-writing phase.

3. Worker and verifier history is only partly recoverable.
   Provider/model are usually recoverable from raw payloads, but reasoning effort is almost never present in this older archive format.

4. This folder does not provide evidence for `xhigh` verifier usage.
   The only explicit effort values I found are `high` on steps 56 and 57. No raw payload in this run records `xhigh`.

## Recovered timeline

### Phase A: initial Claude run

- Steps `1-4`
- Planner: `claude-opus-4-6` (`confirmed`)
- Evidence:
  - `trace.log` starts with `Mode: prove, Model: opus 4.6`
  - `steps/step_001/planner_call.raw.json`
  - `steps/step_004/planner_call.raw.json`

Worker/verifier details in this phase:

- Step `4` worker: Claude Opus (`confirmed`)
  - `trace.log` line 33 shows `[worker_4_0] calling opus (streaming)`
  - `steps/step_004/workers/worker_0_call.raw.json` has Claude-style payload data
- Step `4` verifier: Claude Opus (`confirmed` by trace, payload incomplete)
  - `trace.log` line 35 shows `[verifier_4_0] calling opus (streaming)`
  - `steps/step_004/workers/verifier_0_call.raw.json` is a quota-hit error payload with empty `modelUsage`

Reasoning effort in this phase:

- Claude effort: `unknown`
- The old archive does not preserve a normalized reasoning-effort field for these calls

### Phase B: mixed planner/worker transition

- Steps `5-8`
- Planner: Claude Opus (`confirmed`)
- Evidence:
  - `trace.log` lines 90-115
  - `steps/step_005/planner_call.raw.json`
  - `steps/step_008/planner_call.raw.json`

Worker/verifier details in this phase:

- Step `5` worker: Codex `gpt-5.4` (`confirmed`)
- Step `5` verifier: Codex `gpt-5.4` (`confirmed`)
- Step `7` literature search: Codex `gpt-5.4` (`confirmed` from trace and raw search payload)

Interpretation:

- By step `5`, the run was already using Claude for the planner and Codex for worker-side calls
- `trace.log` line 88 records this mixed mode as `Mode: prove, Model: opus/codex gpt-5.4`

Reasoning effort in this phase:

- Codex effort: `unknown`
- The raw payloads record model name but no `reasoningEffort`

### Phase C: Codex middle section

- Steps `9-53`
- Planner: Codex `gpt-5.4` (`confirmed`)
- Evidence:
  - `trace.log` line 119 switches to `Mode: prove, Model: codex gpt-5.4`
  - representative planner raws:
    - `steps/step_009/planner_call.raw.json`
    - `steps/step_025/planner_call.raw.json`
    - `steps/step_050/planner_call.raw.json`
    - `steps/step_053/planner_call.raw.json`

Worker/verifier details in this phase:

- Where worker/verifier raws exist, they are also Codex `gpt-5.4` (`confirmed`)
- This includes many steps such as `9`, `11-15`, `20-28`, `31-36`, `38-45`, `47-51`

Reasoning effort in this phase:

- Codex effort: mostly `unknown`
- I did not find archived `reasoningEffort` fields for these middle steps

### Phase D: final mixed proof-writing phase

- Steps `54-59`
- Planner: Claude Opus (`confirmed`)
- Evidence:
  - `trace.log` lines 575-614
  - `steps/step_054/planner_call.raw.json`
  - `steps/step_059/planner_call.raw.json`

Worker/verifier details in this phase:

- Step `56` worker: Codex `gpt-5.4` (`confirmed`)
- Step `56` verifier: Codex `gpt-5.4` (`confirmed`)
- Step `57` worker: Codex `gpt-5.4` (`confirmed`)
- Step `57` verifier: Codex `gpt-5.4` (`confirmed`)

Reasoning effort in this phase:

- Step `56` worker: `high` (`confirmed`)
- Step `56` verifier: `high` (`confirmed`)
- Step `57` worker: `high` (`confirmed`)
- Step `57` verifier: `high` (`confirmed`)
- Evidence:
  - `steps/step_056/workers/worker_0_call.raw.json`
  - `steps/step_056/workers/verifier_0_call.raw.json`
  - `steps/step_057/workers/worker_0_call.raw.json`
  - `steps/step_057/workers/verifier_0_call.raw.json`

Final completion:

- Step `59` submits the proof under Claude planner control
- `trace.log` line 614 shows `Actions: write_items, submit_proof`

## What cannot be recovered reliably

- Exact reasoning effort for most Claude calls
- Exact reasoning effort for most Codex calls before step `56`
- Whether any verifier call in this run used `xhigh`

If `xhigh` was used at some point, that change is not evidenced by the archived payloads in this folder.

## Practical conclusion

Manual backfill is workable for provider/model history and phase boundaries.

Manual backfill is poor for reasoning-effort history on older runs, because the old archive format usually did not persist that field. For future runs, the new metadata changes should make this much cleaner.
