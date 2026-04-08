# OpenProver

![system_plot](assets/openprover_system.png)

Theorem prover powered by language models.

A **planner** coordinates proof search by maintaining a whiteboard and repository, delegating focused tasks to parallel **workers** via Claude CLI or local models (vLLM).

## How it works

You give it a theorem statement (a `.md` file). A planner LLM maintains a **whiteboard** (terse mathematical scratchpad) and a **repository** of items (lemmas, observations, literature findings). Each step, the planner decides what to do: spawn workers to explore proof avenues, search literature, read/write repository items, or submit the proof.

Workers run in parallel (up to `-P` at a time), each focused on a single task. They can reference repository items via `[[wikilinks]]`. Results flow back to the planner, which updates the whiteboard and decides the next step.

With `--lean-project`, workers get access to **lean_verify** (compile Lean 4 code) and **lean_search** (search Mathlib/Lean declarations) tools, enabling interactive formal proof development.

Modes:
- **Interactive** (default): see each step's plan, accept or give feedback
- **Autonomous** (`--autonomous`): runs hands-off until proof found or budget exhausted
- **Isolation** (default) / **No-isolation** (`--no-isolation`): by default, workers have no web access. With `--no-isolation`, the planner can use `literature_search` to find relevant papers and results online when the worker model supports web search (currently Claude workers)
- **Formal verification** (`--lean-project`): proof attempts are verified via `lake env lean`, workers can verify code and search Lean libraries

## Requirements

- Python 3.10+
- **Claude** (default): [Claude Code](https://docs.anthropic.com/en/docs/claude-code) (`claude` command on PATH)
- **Leanstral** (alternative): Mistral's Lean-specialized model; requires `MISTRAL_API_KEY` (get one at https://console.mistral.ai/)
- **Local models** (alternative): any OpenAI-compatible server such as [vLLM](https://github.com/vllm-project/vllm); pass `--provider-url` to point at it

## Install

```bash
pip install openprover
```

Or from source:
```bash
git clone https://github.com/open-prover/openprover.git
cd openprover
python -m venv .venv && source .venv/bin/activate
pip install -e .
```

For Lean search support (optional):
```bash
openprover fetch-lean-data
```

## Usage

```bash
# Interactive mode (file argument = theorem)
openprover examples/sqrt2_irrational.md

# Autonomous with Opus, 2h time budget, 3 parallel workers
openprover --theorem examples/erdos_838.md --model opus --max-time 2h --autonomous -P 3

# Token budget instead of time
openprover --theorem examples/cauchy_schwarz.md --max-tokens 500000

# Resume an interrupted run (directory argument = run dir)
openprover runs/sqrt2-irrational-20260217-143012

# Use different models for planner and worker
openprover --theorem examples/cauchy_schwarz.md --planner-model opus --worker-model sonnet

# Enable web searches (disabled by default)
openprover --theorem examples/cauchy_schwarz.md --no-isolation

# Use a local model (via vLLM)
openprover --theorem examples/infinite_primes.md --model minimax-m2.5 --provider-url http://localhost:8000

# Prove and formalize in Lean 4
openprover --theorem examples/addition.md \
  --lean-project ~/mathlib4 \
  --lean-theorem examples/addition.lean

# Formalize an existing proof
openprover --theorem examples/addition.md \
  --lean-project ~/mathlib4 \
  --lean-theorem examples/addition.lean \
  --proof runs/addition-20260223/PROOF.md
```

### Subcommands

| Command | Description |
|---------|-------------|
| `openprover <theorem.md>` | Run the prover (main command) |
| `openprover inspect [run_dir]` | Browse prompts and outputs from a run |
| `openprover fetch-lean-data` | Download Lean Explore search data and models |

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--model` | `sonnet` | Model for both planner and worker |
| `--planner-model` | | Override model for planner |
| `--worker-model` | | Override model for worker |
| `--max-time` | `4h` | Wall-clock time budget (e.g. `30m`, `2h`) |
| `--max-tokens` | | Output token budget (mutually exclusive with `--max-time`) |
| `--conclude-after` | `0.99` | Fraction of budget that triggers conclusion phase (0.9-1.0) |
| `--autonomous` | off | Run without human confirmation |
| `-P, --parallelism` | `1` | Max parallel workers per step |
| `--isolation` / `--no-isolation` | on | Isolation disables web access; `--no-isolation` requires a web-search-capable worker model (`sonnet` or `opus`) |
| `--give-up-after` | `0.5` | Fraction of budget before give_up is allowed |
| `--lean-project` | | Path to Lean project with lakefile |
| `--lean-theorem` | | Path to THEOREM.lean (requires `--lean-project`) |
| `--proof` | | Path to existing PROOF.md (formalize-only mode) |
| `--lean-items` | auto | Allow saving .lean items to the repo (auto-enabled with `--lean-project`) |
| `--lean-worker-tools` | auto | Worker tool calls (lean_verify, lean_search) via MCP/vLLM (auto-enabled with `--lean-project` + capable worker) |
| `--headless` | off | Non-interactive mode (logs to stdout, implies `--autonomous`) |
| `--verbose` | off | Show full LLM responses |
| `--read-only` | off | Inspect run without resuming |
| `--provider-url` | `http://localhost:8000` | Server URL for local models |
| `--answer-reserve` | `4096` | Tokens reserved for answer after thinking (local models) |

Available Claude models: `sonnet`, `opus`. Use `leanstral` for Mistral's Lean-specialized model (requires `MISTRAL_API_KEY`). For local models, pass any model name supported by your OpenAI-compatible server (e.g. `minimax-m2.5`) together with `--provider-url`.

### TUI controls

| Key | Action |
|-----|--------|
| `r` | Toggle reasoning trace |
| `i` | Show worker input (on worker tabs) |
| `w` | Toggle whiteboard view |
| `a` | Toggle autonomous mode |
| `Left/Right` | Switch between planner/worker tabs |
| `Up/Down` | Browse step history / navigate worker actions |
| `PgUp/PgDn` | Scroll content |
| `?` | Help overlay |

When confirming a step: Tab switches between accept/feedback, Enter confirms or opens detail view, Esc dismisses, `a` accepts and enters autonomous mode.

## Lean setup (for formal verification)

To use formal verification (`--lean-project`), you need [elan](https://github.com/leanprover/elan) (Lean version manager) installed. elan automatically fetches the right Lean toolchain.

Benchmarks like MiniF2F and PutnamBench ship their own Lean projects with Mathlib dependencies. Build them once before running:

```bash
# MiniF2F
git clone https://github.com/google-deepmind/miniF2F.git
cd miniF2F
lake exe cache get   # download precompiled Mathlib oleans
lake build           # compile MiniF2F itself

# PutnamBench
git clone https://github.com/trishullab/PutnamBench.git
cd PutnamBench/lean4
lake exe cache get
lake build
```

Then point OpenProver at the project:

```bash
openprover --theorem thm.md --lean-project ./miniF2F --lean-theorem thm.lean
```

## Benchmarks

Scripts in `scripts/` run OpenProver against standard benchmarks:

```bash
# MiniF2F (fetches theorems from GitHub, uses local Lean project for verification)
python scripts/run_minif2f.py valid --model leanstral --repo-path ./miniF2F --max-time 10m --problem-parallelism 10
python scripts/run_minif2f.py test  --model leanstral --repo-path ./miniF2F --max-time 10m

# PutnamBench
python scripts/run_putnam.py --repo-path ./PutnamBench --model opus --max-time 2h --problem-parallelism 4

# Run a single problem
python scripts/run_minif2f.py valid --problem mathd_algebra_182 --model leanstral --repo-path ./miniF2F
```

Use `--informal` to skip Lean verification (faster but scores are not meaningful).

## Planner actions

Each step, the planner chooses one action:

| Action | Description |
|--------|-------------|
| `spawn` | Delegate tasks to parallel workers |
| `literature_search` | Web-enabled search for relevant papers/results |
| `read_items` | Retrieve full content of repository items |
| `write_items` | Create, update, or delete repository items (lean items auto-verified) |
| `write_whiteboard` | Update the whiteboard without spawning workers |
| `read_theorem` | Re-read theorem statement(s) and any provided proof |
| `submit_proof` | Submit proof (informal and/or formal Lean) |
| `give_up` | Abandon search (only allowed after give-up threshold) |

## Worker tools

When `--lean-project` is set with a tool-capable worker model, workers get access to:

| Tool | Description |
|------|-------------|
| `lean_verify(code)` | Compile Lean 4 code via `lake env lean`, returns OK or compiler errors |
| `lean_search(query)` | Search Mathlib/Lean declarations by natural language query |

Tools are provided via MCP (Claude workers) or native tool calling (vLLM workers). Actions are shown in the worker tab and can be browsed with arrow keys.

## Output

Each run creates a directory under `runs/`:

```
runs/<slug>-<timestamp>/
  THEOREM.md           - original theorem statement
  THEOREM.lean         - formal Lean statement (if provided)
  WHITEBOARD.md        - current whiteboard state
  PROOF.md             - final proof (if found)
  PROOF.lean           - formal Lean proof (if lean mode)
  DISCUSSION.md        - post-session analysis
  repo/                - repository items (lemmas, observations, etc.)
  steps/step_NNN/      - per-step planner decisions and worker results
  archive/calls/       - raw LLM call logs with cost/timing
```

All state lives on disk, so runs can be interrupted and resumed.

## Example theorems

The `examples/` directory has theorem statements at various difficulty levels:

| File | Difficulty |
|------|-----------|
| `sqrt2_irrational.md` | Easy |
| `infinite_primes.md` | Easy |
| `e_irrational.md` | Medium |
| `cauchy_schwarz.md` | Medium |
| `erdos_205.md` | Medium |
| `erdos_838.md` | Hard (open) |
| `collatz.md` | Harder (open) |

# Ideas

- Add modes where OpenProver also tries to 1) simplify a proof or make it nicer and 2) generalize a proof.
- In the `lean_verify` action, provide proof states to the planner.

# Cite

If you find OpenProver helpful in your research cite simply as:

```
@misc{openprover,
  author = {Matěj Kripner},
  title = {OpenProver},
  year = {2025},
  publisher = {GitHub},
  url = {https://github.com/kripner/openprover}
}
```
