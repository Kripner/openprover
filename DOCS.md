# OpenProver internals

## Architecture

OpenProver uses a **planner-worker** architecture. A single planner LLM coordinates the proof search by maintaining a whiteboard and repository, spawning focused worker tasks that run in parallel. All state lives on disk for resumability.

```
cli.py          Parse args, setup TUI, run prover, print cost
prover.py       Planner loop, step dispatch, action handlers, Repo
prompts.py      All prompt templates, TOML parser, actions enum
budget.py       Budget tracking (token or time limits)
inspect.py      Read-only run browser
llm/
  _base.py      Shared helpers: Interrupted, StreamingUnavailable, archive(), error detection
  claude.py     LLMClient - Claude CLI wrapper (default backend)
  mistral.py    MistralClient - Mistral Conversations API (Leanstral)
  glm.py        GLMClient - Z.ai OpenAI-compatible API (GLM-5)
  openrouter.py OpenRouterClient - OpenRouter API (Kimi K2.5, MiniMax M2.5/M2.7)
  hf.py         HFClient - local OpenAI-compatible servers (vLLM, serve_hf.py)
lean/
  core.py       Lean 4 integration: parsing, assembly, verification
  data.py       Lean Explore data management (fetch, availability checks)
  mcp_server.py MCP server exposing lean_verify, lean_store, lean_search tools
  tools.py      Tool definitions for vLLM native tool calling, execute_worker_tool()
tui/
  tui.py        Full-screen interactive TUI (ANSI scroll regions, tabs, streaming)
  headless.py   Non-interactive TUI (logs to stdout/stderr)
  _render.py    Terminal rendering, ANSI coloring
  _steps.py     Step/turn display logic
  _stream.py    Real-time streaming text updates
  _input.py     User input handling (keyboard, confirmation UI)
  _nav.py       Navigation state (tab switching, history)
  _tabs.py      Tab management (planner vs worker views)
  _text.py      Text utilities (wrapping, formatting)
  _colors.py    ANSI color/style definitions
  _types.py     Type definitions for TUI state
```

## Planner-worker model

**Planner** (runs every step):
- Maintains a **whiteboard**: terse mathematical scratchpad (LaTeX, abbreviations)
- Manages a **repository** of items: lemmas, observations, failed attempts, literature findings
- Receives: whiteboard + repo index (one-line summaries) + recent outputs (rolling window)
- Outputs: structured decision with action, summary, updated whiteboard, and action-specific fields

**Workers** (spawned on demand, parallel):
- Receive a task description from the planner
- Can reference repo items via `[[wikilink]]` syntax (resolved before sending)
- When `--lean-project` is set with a tool-capable worker model, workers have access to `lean_verify`, `lean_store`, and `lean_search` tools via MCP (Claude) or native tool calling (other backends)
- Report free-form results back to the planner

**Repository** (`repo/` directory):
- Each item is a `.md` file: `Summary: One sentence.\n\nFull content`
- Planner can create, read, update, or delete items
- Used to persist proven lemmas, observations, literature reviews, failed approaches

## Modules

### `cli.py`

Entry point. Parses arguments, creates a `Prover` and `TUI`, installs signal handlers, runs the prover, prints cost summary on exit.

Subcommands:
- `openprover <theorem>` - main proving loop
- `openprover inspect [run_dir]` - browse a historical run
- `openprover fetch-lean-data` - download Lean Explore search data and models

The LLM client is constructed via a factory pattern: `Prover` calls `make_llm(archive_dir)` after setting up the work directory, so the archive path is correct from the start. Separate planner and worker models are supported via `--planner-model` and `--worker-model`.

Model routing maps short names to backends:
- `sonnet`, `opus` - `LLMClient` (Claude CLI)
- `leanstral` - `MistralClient` (Mistral Conversations API)
- `glm-5` - `GLMClient` (Z.ai native API)
- `kimi-k2.5`, `minimax-m2.5`, `minimax-m2.7` - `OpenRouterClient`

Run configuration is saved to `run_config.toml` in the work directory on fresh starts and restored on resume. CLI flags override saved values. Version mismatch between the saved config and the running binary is rejected.

### `budget.py`

Tracks proving session budget in two modes:
- **Time budget** (`--max-time`, default `4h`): wall-clock seconds
- **Token budget** (`--max-tokens`): cumulative output tokens

The `Budget` class tracks elapsed time/tokens and exposes `is_exhausted`, `should_conclude` (at `--conclude-after` fraction). The planner prompt receives budget status so it can pace itself.

### `prover.py`

The `Prover` class owns the proving loop and all state.

**Init:** Creates or resumes a run directory (`runs/<slug>-<timestamp>/`). Loads or initializes the whiteboard. Creates the `Repo` instance. Resume is detected by checking for existing `WHITEBOARD.md` + `THEOREM.md`; step count inferred from `step_NNN` directories.

When `lean_worker_tools` is enabled, sets up tool calling for workers:
- **Claude CLI workers**: Configures an MCP server (`lean/mcp_server.py`) with `lean_verify`, `lean_store`, and `lean_search` tools
- **Other backends**: Initializes LeanExplore search service in-process and uses native OpenAI tool calling

**Step flow** (`run` -> `_do_step`):

1. **Planner call**: Build prompt from whiteboard + repo index + prev worker output. LLM call with streaming (shows in planner tab). Response must contain a structured action block.

2. **Parse action**: Extract action, summary, whiteboard update, and action-specific fields (`[[tasks]]`, `[[items]]`, `search_query`, etc.) via `parse_planner_toml()`.

3. **Dispatch** to action handler based on the action field.

4. **Save step**: Write `planner.toml`, worker tasks/results, archive LLM calls, update `WHITEBOARD.md` on disk.

**Action handlers:**

| Handler | What it does |
|---------|-------------|
| `_handle_spawn` | Run worker tasks in parallel via `ThreadPoolExecutor` (up to `--max-workers`). Each worker gets its task description with wikilinks resolved. Results pushed to output window. |
| `_handle_literature_search` | Spawn a web-enabled worker (Claude CLI with `WebSearch` + `WebFetch` tools). Results fed back to planner. |
| `_handle_read_items` | Fetch full content of requested repo items, push to output. |
| `_handle_write_items` | Create/update/delete repo items. Items with `format="lean"` are auto-verified via `lake env lean`. |
| `_handle_write_whiteboard` | Update the whiteboard without spawning workers. |
| `_handle_read_theorem` | Return THEOREM.md + THEOREM.lean + PROOF.md content to the planner. |
| `_handle_submit_proof` | Save proof to `PROOF.md`. Terminates the session in `prove` mode. |
| `_handle_submit_lean_proof` | Assembles and verifies Lean proof via `lake env lean`, writes `PROOF.lean` on success. Terminates the session in `formalize_only` mode; in `prove_and_formalize`, the session ends when both informal and formal proofs are accepted. |

**`Repo` class** (also in `prover.py`):
- `list_summaries()`: Returns index of all items (name + first-line summary)
- `read_item(slug)` / `read_items(slugs)`: Fetch content
- `write_item(slug, content)`: Create, update, or delete
- `resolve_wikilinks(text)`: Find `[[slug]]` references, return resolved text + appended reference materials

**Output window:** The planner sees recent outputs in a rolling window (via `_push_output()`). Outputs persist across steps until pushed out by newer ones. This gives the planner context about recent progress.

**Operating modes** (determined by CLI args):

| Mode | Inputs | Goal | Terminates when |
|------|--------|------|-----------------|
| `prove` | THEOREM.md | Informal proof | `submit_proof` -> PROOF.md |
| `prove_and_formalize` | THEOREM.md + THEOREM.lean | Both proofs | PROOF.md + PROOF.lean both exist |
| `formalize_only` | THEOREM.md + THEOREM.lean + PROOF.md | Formal proof | `submit_lean_proof` succeeds -> PROOF.lean |

**Worker tool execution** (when `lean_worker_tools` is enabled):

For backends with native tool calling (vLLM, GLM, OpenRouter, Mistral), tools are executed in a multi-turn loop: the LLM requests tool calls, `execute_worker_tool()` dispatches to the appropriate handler, results are appended to the conversation, and the LLM continues.

For the Claude CLI path, tool execution is handled by the MCP server subprocess. Tool call events are detected from the stream and reported to the TUI via `add_worker_action()`.

**Other methods:**
- `_write_discussion()`: Post-session analysis via LLM call
- `is_finished`: Check if run completed (mode-aware: checks for required artifacts)
- `inspect()`: Browse a historical run in read-only mode
- `_load_history()`: Restore step history from disk for inspect mode

### `llm/`

Five LLM client backends with a shared interface.

**Shared interface** (`call` method):
```python
def call(
    prompt, system_prompt,
    json_schema=None, label="", web_search=False,
    stream_callback=None, archive_path=None, max_tokens=None, **kwargs
) -> dict  # {result, thinking, cost, duration_ms, raw, finish_reason, ...}
```

Tool-capable clients also support `chat()` for multi-turn tool calling conversations.

**`LLMClient`** (Claude CLI, `claude.py`):

Non-streaming:
```
claude -p --model <model> --system-prompt <...> --output-format json --tools ""
```

Streaming:
```
claude -p --model <model> --system-prompt <...> --output-format stream-json --verbose --include-partial-messages --tools ""
```
Uses `Popen` + `readline()` (not the line iterator, which has read-ahead buffering that defeats real-time streaming). Parses NDJSON lines, dispatches `content_block_delta` text to the callback.

Web search: When `web_search=True`, replaces `--tools ""` with `--permission-mode bypassPermissions --allowedTools WebSearch WebFetch`.

MCP tool calling: When `mcp_config` is set, adds `--mcp-config <json> --strict-mcp-config --permission-mode bypassPermissions --allowedTools mcp__lean_tools__lean_verify mcp__lean_tools__lean_store mcp__lean_tools__lean_search`. Tool events are detected from the stream:
- `tool_use` content blocks are tracked by their ID (capturing tool name and input as they stream in)
- Tool results appear as top-level `{"type": "user"}` messages (not as content blocks), containing `tool_result` entries matched by `tool_use_id`
- MCP prefixes are stripped from tool names (`mcp__lean_tools__lean_verify` -> `lean_verify`)
- Status is inferred from result text (e.g., `lean_verify` results starting with "OK" = success)

Archiving: Every call saved to `archive/calls/call_NNN.json` with full prompt, system prompt, schema, response, cost, timing, and errors.

**`MistralClient`** (`mistral.py`):
- Uses the Mistral Conversations API, which persists context server-side
- Avoids re-sending the full transcript on each turn
- Supports streaming and tool calling
- Requires `MISTRAL_API_KEY`

**`GLMClient`** (`glm.py`):
- Calls Z.ai's native OpenAI-compatible API for accurate token usage reporting
- Supports `reasoning_content` (extended thinking, same format as DeepSeek)
- 128k context window
- Requires `GLM_API_KEY`

**`OpenRouterClient`** (`openrouter.py`):
- Calls OpenRouter's OpenAI-compatible API
- Hosts Kimi K2.5 (262k context), MiniMax M2.5/M2.7 (196k context)
- Supports streaming and tool calling
- Requires `OPENROUTER_API_KEY`

**`HFClient`** (`hf.py`, for vLLM/serve_hf.py):
- Calls an OpenAI-compatible API at `--provider-url`
- Health check on init (`/health` endpoint)
- Streaming via chunked transfer encoding
- `chat()` method for multi-turn tool calling conversations
- Supports `reasoning_content` field
- Cost always 0.0 (local model)
- Automatically enforces `--isolation`

**Key gotchas:**
- Claude CLI: `--json-schema` puts structured output in `raw["structured_output"]`, not `raw["result"]`
- Claude CLI: `--tools ""` disables all tools (pure reasoning mode)
- Cost tracking uses `total_cost_usd` from the Claude CLI response
- All backends archive calls with markdown frontmatter + raw JSON sidecars

### `prompts.py`

All prompt templates, the TOML parser, and the actions enum.

**Actions:**
```python
ACTIONS = [
    "submit_proof", "submit_lean_proof", "read_items", "write_items",
    "spawn", "literature_search", "read_theorem", "write_whiteboard",
]
```

**System prompts:**
- `planner_system_prompt(...)`: Built dynamically. Instructs the planner to coordinate proof search, maintain whiteboard, manage repo, delegate to workers. Actions and principles are assembled based on mode (`prove`/`prove_and_formalize`/`formalize_only`), isolation setting, and Lean availability.
- `worker_system_prompt(lean_worker_tools=False)`: Instructs worker to complete its task rigorously. When `lean_worker_tools=True`, documents `lean_verify`, `lean_store`, and `lean_search` tools. If verifying, be skeptical and end with `VERDICT: CORRECT` or `VERDICT: INCORRECT`.
- `SEARCH_SYSTEM_PROMPT`: Instructs literature search worker.

**Prompt formatters:**
- `format_planner_prompt(whiteboard, repo_index, prev_outputs, ...)`: Planner input (prev_outputs is a list of recent outputs). Includes status indicators for theorem statement, Lean statement, informal proof, and formal proof.
- `format_worker_prompt(task_description, resolved_refs)`: Worker input
- `format_search_prompt(query, context)`: Literature search prompt
- `format_initial_whiteboard(theorem, mode)`: Template with Goal / Strategy / Status / Tried. Includes mode banner for lean modes.
- `format_discussion_prompt(...)`: Post-session analysis

**TOML parser** (`parse_planner_toml`):
- Extracts TOML from fenced block or bare TOML at end of response
- Uses `tomllib` (Python 3.11+) or `tomli` (3.10 fallback)
- Falls back to a minimal regex-based parser if neither available
- Handles `[[tasks]]`, `[[items]]`, and `[[lean_blocks]]` array-of-tables syntax
- Post-processes `lean_block_N` numbered keys into a `lean_blocks` list (both styles accepted from LLMs)

### `lean/core.py`

Lean 4 integration -- all formal verification logic isolated here.

**`LeanTheorem`**: Parses a THEOREM.lean file.
- Extracts preamble (import/open lines at top), locates all `sorry` positions via `\bsorry\b` regex
- `assemble_proof(replacements, context)`: replaces each sorry with its corresponding block (in reverse order to preserve offsets), injects optional context after preamble. Validates: correct count, no `import` in injected code.

**`run_lean_check(lean_file, project_dir, timeout=300)`**: Runs `lake env lean <file>` from the project directory. Returns `(True, "")` if returncode 0 and empty stdout; otherwise `(False, feedback)` with combined stdout/stderr.

**`LeanWorkDir`**: Manages an `OpenProver-{random_8hex}` subdirectory within the Lean project. Generated lean files go here with `{slug}-{random_6hex}.lean` naming. The final verified proof is written as `PROOF.lean`.

### `lean/mcp_server.py`

MCP server exposing `lean_verify`, `lean_store`, and `lean_search` tools for Claude CLI workers. Runs as a subprocess spawned by Claude CLI via `--mcp-config`. Communicates over stdio using JSON-RPC (MCP protocol).

- **`lean_verify(code)`**: Writes code to a temp file in the Lean work directory, runs `run_lean_check()`, returns "OK - no errors" or compiler output. If a persistent store exists, its contents are automatically prepended.
- **`lean_store(code)`**: Verifies the snippet, then appends it to the worker's persistent prefix. Stored code is auto-prepended to all subsequent `lean_verify` calls for that worker. Rejects code with `sorry`, `axiom`, `unsafe`, `set_option`, or `native_decide`. Imports are automatically deduplicated.
- **`lean_search(query)`**: Searches Lean 4 declarations using LeanExplore. Returns matching names, signatures, and docstrings.

Environment variables `LEAN_PROJECT_DIR` and `LEAN_WORK_DIR` are set by the prover when spawning the MCP server.

### `lean/tools.py`

Tool definitions in OpenAI function-calling format for non-Claude backends. Defines `WORKER_TOOLS` (list of tool specs for `lean_verify`, `lean_store`, `lean_search`) and `execute_worker_tool()` which dispatches tool calls and manages per-worker persistent stores.

### `lean/data.py`

Manages LeanExplore search data and dependencies.

- `is_lean_data_available()`: Checks for lean-explore package, torch, sentence-transformers, and fetched data files
- `fetch_lean_data()`: Installs missing dependencies (lean-explore, torch CPU, sentence-transformers), fetches search data via `lean-explore data fetch`, and pre-downloads the embedding model

Called automatically on startup when `--lean-worker-tools` is enabled and data is missing. Also available as `openprover fetch-lean-data`.

### Lean Explore search pipeline

The `lean_search` tool searches ~400k Lean 4 declarations (Init, Batteries, Lean, Mathlib, Std) using a multi-stage pipeline:

1. **BM25 retrieval** (~0.01s): Keyword search over LLM-generated natural language descriptions ("informalizations") of each declaration. Two indices with different tokenization strategies, results merged.

2. **Semantic retrieval** (~1s): Encodes query with Qwen3-Embedding-0.6B (sentence-transformer, 1024-dim), searches pre-built FAISS index for nearest neighbors by cosine similarity.

3. **Score fusion**: Normalizes both score sets to [0,1], combines as `0.3 * bm25 + 0.7 * semantic`, applies dependency boost for related declarations.

4. **Reranking** (GPU only, ~1-2s; skipped on CPU): Cross-encoder scoring with Qwen3-Reranker-0.6B. Disabled on CPU where it takes ~50s per query.

5. **Hydration**: Looks up full metadata (signature, docstring, source) from SQLite.

First call takes ~10s (model loading from disk). Subsequent calls ~1s.

Data is fetched once via `openprover fetch-lean-data` or automatically on first use. Stored in `~/.lean_explore/cache/`.

### `tui/`

Modular full-screen terminal UI using ANSI escape codes and scroll regions.

**Layout:** Rows 1-4 are a fixed header (theorem name, step counter, model, tab bar). Row 5+ is the scrolling content area.

**Tab system:**
- Always has a `planner` tab (fixed)
- Spawn and search steps create worker tabs dynamically
- Tab bar shows status indicators: checkmark = done, ellipsis = streaming
- Left/right arrows switch tabs instantly

**Views:** `main` (log + streaming trace), `whiteboard`, `help`, `step_detail`, `input` (worker task on worker tabs).

**Key handling:** Background thread reads stdin in cbreak mode via `select()` + `os.read()`. Instant keys (work during streaming): `r`, `i`, `w`, `a`, left/right, up/down, PgUp/PgDn, `?`. Queued keys (during confirmation): `Tab`, `Enter`, `s`, `p`, `q`, `Esc`.

**Worker action display:** When workers use `lean_verify`, `lean_store`, or `lean_search`, each tool call appears as a navigable entry in the worker tab. Up/down arrows cycle through actions, Enter opens a detail view showing the tool input and result.

**Streaming:** Braille spinner while waiting for first token (~12 FPS). Toggleable reasoning trace with `r`. Worker tabs show their own streaming output independently.

**Confirmation UI:** Two-option selector (accept / give feedback) with text input. Up/down browse step history; Enter on a history entry opens detail view.

**Thread safety:** All stdout writes protected by `_write_lock`. Background key thread doesn't hold the lock during I/O.

**HeadlessTUI:** Non-interactive alternative for `--headless` mode. Logs step summaries and worker results to stdout, errors to stderr. No streaming display.

### `inspect.py`

Read-only run browser. Loads a completed run directory and displays it in the TUI for review. Accessed via `openprover inspect [run_dir]` or automatically when resuming a finished run.

## Run directory

```
runs/<slug>-<timestamp>/
  THEOREM.md                   - immutable copy of input
  THEOREM.lean                 - formal Lean statement (if --lean-theorem)
  WHITEBOARD.md                - latest whiteboard state (enables resume)
  PROOF.md                     - written only if proof found
  PROOF.lean                   - formal Lean proof (if lean mode)
  DISCUSSION.md                - post-session analysis
  run_config.toml              - saved run configuration (for resume)
  repo/
    *.md                       - repository items (lemmas, observations, etc.)
  steps/
    step_001/
      planner.toml             - planner's TOML decision
      workers/
        task_0.md              - worker task description
        result_0.md            - worker output
        worker_0_call.json     - archived LLM call
    step_002/...
  archive/
    calls/
      call_001.json            - full LLM call record
```

**Slug format:** First 40 chars of theorem, lowercased, non-alphanumeric replaced with hyphens. Example: `sqrt2-irrational-20260220-143706`.

**Resume:** If the run directory contains `WHITEBOARD.md` + `THEOREM.md`, the prover picks up from the last completed step. Settings are restored from `run_config.toml`; CLI flags override saved values.

## Verification

**Informal verification** (all modes): Workers can be tasked with verification by the planner. A verifier worker sees only the proof text (not the reasoning that produced it) and must end its response with `VERDICT: CORRECT` or `VERDICT: INCORRECT`. The planner is instructed to verify proofs before submitting. The `--verifier` / `--no-verifier` flag controls whether an automatic LLM verifier runs after each worker.

**Formal verification** (lean modes): When `--lean-project` is provided, the system supports automatic Lean 4 verification:

- **`write_items` with `format="lean"`**: Lean items are written to the `OpenProver-{id}/` subdirectory within the Lean project and verified via `lake env lean`. The planner receives pass/fail feedback with compiler errors.
- **`submit_lean_proof`**: The planner provides N replacement blocks (one per `sorry` in THEOREM.lean) plus optional context. The system assembles the complete file, verifies it, and writes PROOF.lean on success. On failure, compiler errors are fed back.
- **`read_theorem`**: Returns THEOREM.md, THEOREM.lean, and PROOF.md (if provided) content so the planner can reference the formal statement.

**Worker tools** (when `--lean-worker-tools` is enabled): Workers can directly verify Lean code (`lean_verify`), store verified snippets (`lean_store`), and search Lean libraries (`lean_search`) during their reasoning. Tool calls are shown in the TUI worker tab.

Generated Lean files are placed in `<lean-project>/OpenProver-<random_id>/` with `{slug}-{random_suffix}.lean` names to avoid collisions. No `import` statements are allowed in injected code (enforced at assembly time).

## Wikilinks

Task descriptions can reference repository items via `[[slug]]` syntax. Before a worker receives its task, `repo.resolve_wikilinks()` finds all references, fetches the content, and appends it as a "Referenced Materials" section. This lets the planner share proven lemmas, observations, or literature findings with workers without duplicating content in every task.

## Adding a new action

1. Add the action name to `ACTIONS` in `prompts.py`
2. Describe it in `_build_actions()` in `prompts.py` (format and when to use it)
3. Handle it in `Prover._do_step()` (add a `_handle_<action>` method)
4. Add a color in `ACTION_STYLE` in `tui/_colors.py`

## Adding a new worker tool

1. Add the tool function to `lean/mcp_server.py` (decorated with `@mcp.tool()`)
2. Add the tool definition to `WORKER_TOOLS` in `lean/tools.py` (OpenAI format)
3. Add a dispatch case in `execute_worker_tool()` in `lean/tools.py`
4. Add the `--allowedTools` entry in `llm/claude.py` (MCP tool name)
5. Document it in `worker_system_prompt()` in `prompts.py`
6. Add a color in `TOOL_STYLE` in `tui/_colors.py`

## Adding a new LLM backend

1. Create a new module in `llm/` implementing `call()` and optionally `chat()` methods
2. Export it from `llm/__init__.py`
3. Add model name(s) to `model_choices` and the appropriate `*_MODEL_MAP` / `*_MODELS` set in `cli.py`
4. Add the factory logic in `cli.py` to construct the client
