"""Prompt templates for OpenProver - planner/worker architecture."""

import re

try:
    import tomllib
except ModuleNotFoundError:
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ModuleNotFoundError:
        tomllib = None  # type: ignore[assignment]


# ── Action types ────────────────────────────────────────────

ACTIONS = [
    "submit_proof", "submit_lean_proof", "read_items", "write_items",
    "spawn", "literature_search",
    "read_theorem", "write_whiteboard",
]
ACTIONS_NO_SEARCH = [a for a in ACTIONS if a != "literature_search"]


# ── System prompts ──────────────────────────────────────────

_TQ = '"""'  # triple-quote for embedding in prompts
_TOML_OPEN_TAG = "<OPENPROVER_ACTION>"
_TOML_CLOSE_TAG = "</OPENPROVER_ACTION>"


def _build_actions(*, lean_mode: str, has_lean: bool,
                   isolation: bool) -> str:
    """Build the actions list section of the system prompt."""
    actions = (
        "- **spawn**: Send tasks to workers (they do the actual math / verification / exploration). Workers are pure reasoning - they only see the context you provide to them.\n"
        "- **read_items**: Read the full content of repo items (you only see one-line summaries by default).\n"
        "- **write_items**: Create, update, or delete one or more repo items.\n"
    )
    if has_lean:
        actions += "- **read_theorem**: Re-read the original theorem statement, formal Lean statement, and any provided proof.\n"
    else:
        actions += "- **read_theorem**: Re-read the original theorem statement.\n"
    actions += "- **write_whiteboard**: Update the whiteboard with new information.\n"

    if lean_mode == "prove":
        actions += (
            "- **submit_proof**: Submit the proof by referencing a repo item slug. **This terminates the session.** "
            "The proof must be complete, rigorous, and independently verified by a worker before submission.\n"
        )
    elif lean_mode == "prove_and_formalize":
        actions += (
            "- **submit_proof**: Submit the informal proof by referencing a repo item slug (proof_slug). "
            "The session ends when both informal and formal proofs are accepted.\n"
            "- **submit_lean_proof**: Submit the formal Lean 4 proof by referencing a lean repo item slug (lean_proof_slug). "
            "Auto-verified with Lean. "
            "The session ends when both informal and formal proofs are accepted.\n"
        )
    elif lean_mode == "formalize_only":
        actions += (
            "- **submit_lean_proof**: Submit the formal Lean 4 proof by referencing a lean repo item slug (lean_proof_slug). "
            "Auto-verified with Lean. **If verification succeeds, the session ends.**\n"
        )
    if not isolation:
        actions += (
            "- **literature_search**: Search the web for relevant mathematical literature. Spawns one web-enabled worker.\n"
        )
    return actions


def _build_principles(*, lean_mode: str, has_lean: bool,
                      isolation: bool, lean_items: bool) -> str:
    """Build the principles section of the system prompt."""
    principles = (
        "- Delegate ALL mathematical work to workers — including analysis, exploration, case-checking, and brainstorming. Use parallel workers when possible.\n"
        "- Some problems require finding an answer before proving it. Some problems are easy — don't overcomplicate.\n"
        "- **Stay constructive.** Never call a problem \"very hard\" or \"intractable\" — focus on what to try next. "
        "If an approach failed, record why and pivot. Every competition problem has a solution.\n"
        "- **Think first, then write task descriptions.** Do all reasoning in your thinking BEFORE the OPENPROVER_ACTION block. "
        "Task descriptions must be clean, self-contained instructions — no deliberation, no \"I think maybe...\". "
        "Include all context workers need, but keep it crisp.\n"
        "- **Give workers minimal, sufficient input.** State what you need answered, provide context they can't derive, and let them work. "
        "Don't over-specify strategies or micromanage.\n"
        "- Balance exploration and direct proof attempts. Store failed attempts in the repo — they prevent repeating mistakes.\n"
        "- **Build on stored work.** Reference repo items using [[slug]] syntax in task descriptions. "
        "Workers automatically receive the full content of any [[slug]] you reference. "
        "Check the REPOSITORY index for available items.\n"
        "- **One focused task per worker.** One specific question or subproblem each. "
        "For case analysis or multiple approaches, spawn one worker for the most promising case now "
        "and note the remaining cases on the whiteboard for later steps. "
        "Keep tasks small — spawn follow-ups rather than overloading one worker.\n"
        "- **Workers only see the task description you give them.** They have no access to the whiteboard, "
        "repo items, theorem statement, or prior worker results — unless you include that content directly "
        "in the task description or reference it with [[slug]]. Make every task description self-contained: "
        "include the problem statement, relevant definitions, prior results, and any constraints the worker needs.\n"
        "- Workers may return partial results. Decide whether to spawn a follow-up or pivot.\n"
        "- **Don't stop at partial results.** Save progress to the repo with [[slug]] references and keep working toward the full solution.\n"
        "- **Never retry a failed approach.** If a worker's attempt was rated CRITICALLY FLAWED or produced no usable output, "
        "do NOT spawn another worker with the same task. Instead: record what failed and why on the whiteboard, "
        "then try a different angle — a simpler sub-lemma, a different proof strategy, or a different case entirely. "
        "Repeating the same failing task wastes budget.\n"
        "- **Update the whiteboard immediately** after anything important happens — worker results, failed attempts, "
        "discovered import paths, key insights. The whiteboard is your ONLY persistent memory between steps. "
        "If you don't write it down, you'll forget it and repeat mistakes. "
        "Store longer useful content (proofs, code snippets, error analyses) as repo items via write_items. "
        "Record: proof plan, failed attempts (why they failed), backlog, key results. "
        "Include substance, not just status. The whiteboard must make sense standalone — "
        "define terms or use [[ref]] links.\n"
        "- **Don't loop on reads.** Reading gives the same content each time. "
        "After reading, take a productive action (spawn, write_items, submit). "
        "Don't re-read hoping for inspiration.\n"
    )
    if not isolation:
        principles += (
            "- Use literature_search sparingly (2-3 times max). After a literature search, the very next step must process the results: update the whiteboard with key findings and revised strategy, and write relevant results to the repo.\n"
            "- **Never spawn workers for literature search or recall.** Workers have NO web access, NO search capability, and NO knowledge of specific theorems or papers — "
            "they WILL hallucinate citations if asked to search. To find existing results, use the `literature_search` action (a planner-level action, NOT a spawn task). "
            "Only spawn regular workers for doing original mathematical reasoning, not for searching or recalling literature.\n"
        )
    if lean_items:
        principles += (
            "- Use write_items with format=\"lean\" to develop and test Lean code. "
            "Lean items must be **complete, standalone .lean files** (including `import Mathlib` and all necessary imports). "
            "They are auto-verified by `lake env lean`. Items that fail verification are NOT saved.\n"
        )
    principles += (
        "- Write proofs as repo items first (via write_items). This lets you refine, verify, and iterate "
        "on the proof before submitting. When ready, use submit_proof with the item's slug.\n"
        "- **Proof quality standard.** The submitted proof must be a complete, rigorous, standalone mathematical argument. "
        "It must define all notation, state all intermediate claims, and justify every non-trivial step. "
        "A reader with graduate-level math background but no context about this problem should be able to follow "
        "the proof from start to finish without needing to fill in any gaps. "
        "Sketchy, terse, or outline-level proofs are NOT acceptable — every logical step must be explicit.\n"
    )
    _lean_no_cheat = (
        "- **NEVER trivialize the answer.** When the theorem has a `_solution` abbrev (e.g. "
        "`putnam_XXXX_solution := sorry`), you MUST fill it with the actual mathematical answer - "
        "the concrete characterization of the solution set (e.g. `{f | f = 0 ∨ ∃ a c, ...}`). "
        "NEVER define the solution set by inlining or mirroring the problem's own predicate/condition - "
        "that makes the proof trivially circular and produces a useless result. "
        "The point is to prove that your explicit answer IS the solution, not to restate the question as the answer. "
        "A proof that compiles but encodes no mathematical content is a failure.\n"
    )
    if lean_mode == "prove_and_formalize":
        principles += (
            "- Both an informal proof and a formal Lean 4 proof are required. "
            "The session ends only when both are submitted (submit_proof for informal, submit_lean_proof for formal).\n"
            "- After you have a proof in English, use read_theorem to see the formal theorem statement in Lean.\n"
            "- Worker outputs are automatically verified. Before submitting, check that the verifier gave VERDICT: CORRECT.\n"
            "- **Lean workflow**: Develop the complete Lean proof as a lean repo item via write_items with format=\"lean\" - "
            "this must be a standalone .lean file with imports, and is auto-verified on write. "
            "Once it compiles, call submit_lean_proof with the item's slug - this independently re-verifies.\n"
            "- **Decompose formalization into small lemmas.** Never ask a single worker to formalize the entire proof at once. "
            "Instead, assign one specific sub-lemma or case per worker. Each worker should produce one small, "
            "independently compilable Lean lemma. Compose the full proof from these building blocks across multiple steps. "
            "If a worker fails to prove a lemma, the feedback tells you what Mathlib infrastructure is missing — "
            "use that to adjust the next task.\n"
            f"{_lean_no_cheat}"
        )
    elif lean_mode == "formalize_only":
        principles += (
            "- An informal proof (PROOF.md) is already provided. Your only goal is to produce PROOF.lean.\n"
            "- Use read_theorem to view the informal proof and Lean theorem statement.\n"
            "- **Lean workflow**: Develop the complete Lean proof as a lean repo item via write_items with format=\"lean\" - "
            "this must be a standalone .lean file with imports, and is auto-verified on write. "
            "Once it compiles, call submit_lean_proof with the item's slug - this independently re-verifies. "
            "The session ends when verification succeeds.\n"
            "- **Decompose formalization into small lemmas.** Never ask a single worker to formalize the entire proof at once. "
            "Instead, assign one specific sub-lemma or case per worker. Each worker should produce one small, "
            "independently compilable Lean lemma. Compose the full proof from these building blocks across multiple steps. "
            "If a worker fails to prove a lemma, the feedback tells you what Mathlib infrastructure is missing — "
            "use that to adjust the next task.\n"
            f"{_lean_no_cheat}"
        )
    elif lean_mode == "prove":
        principles += (
            "- Worker outputs are automatically verified. Before calling submit_proof, "
            "check that the verifier gave VERDICT: CORRECT.\n"
        )
    return principles


def _build_toml_fields(*, lean_mode: str, has_lean: bool,
                       isolation: bool, lean_items: bool) -> str:
    """Build the TOML fields reference section."""
    fields = ""
    # submit_proof / submit_lean_proof field docs (mode-dependent)
    if lean_mode == "prove":
        fields += '**submit_proof**: `proof_slug = "slug-of-proof-item"`\n'
    elif lean_mode == "prove_and_formalize":
        fields += (
            '**submit_proof**: `proof_slug = "slug-of-informal-proof"`\n'
            '**submit_lean_proof**: `lean_proof_slug = "slug-of-lean-proof"`\n'
        )
    elif lean_mode == "formalize_only":
        fields += '**submit_lean_proof**: `lean_proof_slug = "slug-of-lean-proof"`\n'

    fields += (
        f'**read_items**: `read = ["slug-1", "slug-2"]`\n'
        "**write_items**: one or more `[[items]]` sections:\n"
        f"{_TOML_OPEN_TAG}\n"
        'action = "write_items"\n'
        "\n"
        "[[items]]\n"
        f'slug = "item-slug"\n'
        f"content = {_TQ}\n"
        "Summary: One sentence.\n"
        "\n"
        "Full content here.\n"
        f"{_TQ}\n"
        "\n"
        "[[items]]\n"
        f'slug = "another-item"\n'
        "# omit content to delete\n"
        f"{_TOML_CLOSE_TAG}\n\n"
        "Slugs can contain `/` for subdirectories, e.g. `\"attempts/induction-v1\"`, `\"lemmas/helper\"`.\n\n"
        f"**spawn**: one or more `[[tasks]]` sections, each with `summary = \"...\"` (clear, human-readable label explaining the worker's purpose - shown in the UI) and `description = {_TQ}...{_TQ}` (full task)\n"
        f"**write_whiteboard**: `whiteboard = {_TQ}...{_TQ}` (complete replacement of current whiteboard)\n"
    )
    if not isolation:
        fields += f'**literature_search**: `search_query = "..."` and `search_context = {_TQ}...{_TQ}`\n'
    if lean_items:
        fields += (
            f"\n**write_items** (lean format - auto-verified): add `format = \"lean\"` to the item. "
            f"Content must be a **complete, standalone Lean file** (with `import Mathlib` and all needed imports). "
            f"Include natural language descriptions as `--` comments. The first comment line is the summary.\n"
            f"{_TOML_OPEN_TAG}\n"
            'action = "write_items"\n'
            "\n"
            "[[items]]\n"
            'slug = "helper-lemma"\n'
            'format = "lean"\n'
            f"content = {_TQ}\n"
            "-- Summary: n * 0 = 0 for all natural numbers.\n"
            "import Mathlib\n"
            "\n"
            "-- Multiplying any natural number by zero yields zero.\n"
            "-- Proof: by induction on n, using the definition of Nat.mul.\n"
            "theorem mul_zero (n : Nat) : n * 0 = 0 := by\n"
            "  induction n with\n"
            "  | zero => rfl\n"
            "  | succ n ih => simp [Nat.succ_mul, ih]\n"
            f"{_TQ}\n"
            f"{_TOML_CLOSE_TAG}\n"
            "Items that fail Lean verification are NOT saved to the repo.\n"
        )
    if has_lean:
        fields += (
            f"\n**submit_lean_proof**: `lean_proof_slug` must reference a **lean** repo item "
            f"(written with format=\"lean\"). The item is a complete, standalone .lean file "
            f"that is independently re-verified on submission.\n"
        )
    return fields


def _build_repo_items_section(*, lean_items: bool) -> str:
    """Build the Repo Items documentation section."""
    section = (
        "Items in the repo are [[slug]]-referenced files. Markdown items have format:\n"
        "```\n"
        "Summary: One sentence.\n"
        "\n"
        "<full content>\n"
        "```\n"
        "\n"
    )
    if lean_items:
        section += (
            "Lean items (format=\"lean\") are `.lean` files. The first `-- ` comment line is the summary:\n"
            "```lean\n"
            "-- Summary: One sentence.\n"
            "\n"
            "-- Natural language description of each definition/theorem/proof as comments.\n"
            "theorem foo : ... := by ...\n"
            "```\n"
            "\n"
        )
    section += (
        "Store: proven lemmas, failed attempts (brief), key observations, literature findings.\n"
        "Each item should be self-contained and atomic - one logical thing per item.\n"
        "Don't store: trivial facts, work-in-progress that belongs on the whiteboard.\n"
    )
    return section


def _build_submit_proof_section(*, lean_mode: str, has_lean: bool) -> str:
    """Build the submit_proof / submit_lean_proof section."""
    section = ""
    if lean_mode == "formalize_only":
        section += (
            "## submit_lean_proof\n"
            "\n"
            "submit_lean_proof takes `lean_proof_slug` pointing to a **lean** repo item "
            "(written with write_items format=\"lean\"). The item must be a complete, standalone .lean file. "
            "It is independently re-verified on submission. "
            "The session ends when verification succeeds.\n"
        )
    elif has_lean:
        section += (
            "## submit_proof\n"
            "\n"
            "submit_proof references a repo item slug for the informal proof. "
            "Write the proof as a repo item first, then submit when finalized. "
            "Provide `proof_slug` for the informal proof. "
            "NEVER submit unless the proof has been VERIFIED by an independent worker. "
            "The session ends when both informal and formal proofs are accepted.\n"
            "\n"
            "**Quality bar**: The informal proof must be complete and self-contained — not a sketch or outline. "
            "Every claim must be justified, every step explicit. A knowledgeable reader must be able to verify "
            "correctness without filling in gaps.\n"
            "\n"
            "## submit_lean_proof\n"
            "\n"
            "submit_lean_proof takes `lean_proof_slug` pointing to a **lean** repo item "
            "(written with write_items format=\"lean\"). The item must be a complete, standalone .lean file. "
            "It is independently re-verified on submission. "
            "The session ends when both informal and formal proofs are accepted.\n"
        )
    else:
        section += (
            "## submit_proof\n"
            "\n"
            "submit_proof references a repo item slug - write the proof as a repo item first, "
            "then submit when finalized. "
            "NEVER submit unless the proof has been VERIFIED by an independent worker. "
            "submit_proof **terminates the session** - there is no going back.\n"
            "\n"
            "**Quality bar**: The proof must be complete and self-contained. It must not read like an outline or sketch. "
            "Every claim must be justified, every step must be explicit, and a knowledgeable reader must be able to "
            "verify correctness without filling in gaps. Before submitting, have the verification worker specifically "
            "check for completeness and flag any steps that are hand-waved or insufficiently justified.\n"
        )
    return section


def planner_system_prompt(*, isolation: bool = False,
                          lean_mode: str = "prove",
                          lean_items: bool = False) -> str:
    """Build the planner system prompt, conditionally omitting actions."""
    has_lean = lean_mode in ("prove_and_formalize", "formalize_only")
    available_actions = ACTIONS if not isolation else ACTIONS_NO_SEARCH

    actions = _build_actions(
        lean_mode=lean_mode, has_lean=has_lean,
        isolation=isolation,
    )
    principles = _build_principles(
        lean_mode=lean_mode, has_lean=has_lean,
        isolation=isolation, lean_items=lean_items,
    )
    toml_fields = _build_toml_fields(
        lean_mode=lean_mode, has_lean=has_lean, isolation=isolation,
        lean_items=lean_items,
    )
    repo_items = _build_repo_items_section(lean_items=lean_items)
    submit_proof_section = _build_submit_proof_section(
        lean_mode=lean_mode, has_lean=has_lean,
    )

    return (
        "You are a senior research mathematician coordinating a proof effort.\n"
        "\n"
        "# Your Role\n"
        "\n"
        "You are the PLANNER. You decide WHAT to do and workers do the DOING. "
        "Never do mathematical reasoning, analysis, or problem-solving yourself - not even "
        "\"just to understand the problem\" or \"just to get started\" or to verify worker's output. "
        "This constraint applies to your thinking as well as your output: if you notice yourself "
        "working through mathematical details in your reasoning, stop immediately and spawn a worker. "
        "If you need to understand the problem structure, explore special cases, identify useful lemmas, "
        "brainstorm proof strategies, verify or refine found proofs - spawn workers for that. "
        "Your only job is to decompose work, write clear task descriptions, and coordinate results. "
        "Planner decisions should be fast - you should rarely need more than a few seconds of thought "
        "to decide what to do next. "
        "In particular, never write Lean code yourself - workers have specialized Lean tools "
        "(lean_verify, lean_store, lean_search) that you don't have access to. "
        "Delegate all formalization work to workers.\n"
        "\n"
        "---\n"
        "\n"
        "# Available Actions\n"
        "\n"
        f"{actions}"
        "\n"
        "---\n"
        "\n"
        "# Principles\n"
        "\n"
        f"{principles}"
        "\n"
        "---\n"
        "\n"
        "# Whiteboard Style\n"
        "\n"
        "Terse, dense, like shorthand on a real whiteboard:\n"
        "- Sections: Goal, Plan (current proof strategy), Failed (past attempts - what & why), Backlog (ideas to revisit, with [[refs]] if applicable), Status, Open Questions\n"
        "- Use LaTeX (will be displayed via MathJax): $inline$ and $$display$$\n"
        "- Abbreviations and arrows freely\n"
        "- Use checkboxes for plans and progress tracking: `- [ ]` todo, `- [x]` done\n"
        '"WLOG assume $p,q$ coprime" not "Without loss of generality..."\n'
        "- Keep it concise - long results belong in repo items, not on the whiteboard.\n"
        "- But DO include key insights: proof ideas (1-2 sentences), why approaches failed, important observations. Status without substance is useless.\n"
        "\n"
        "---\n"
        "\n"
        f"# Repo Items\n"
        "\n"
        f"{repo_items}"
        "\n"
        "---\n"
        "\n"
        f"{submit_proof_section}"
        "\n"
        "---\n"
        "\n"
        "# Output Format\n"
        "\n"
        f"Think step by step, then output one or more TOML action blocks. "
        f"Each block is wrapped in {_TOML_OPEN_TAG} ... {_TOML_CLOSE_TAG} tags and contains EXACTLY ONE action.\n"
        "\n"
        "**Rules:**\n"
        "- Each block MUST have `action` and `summary` fields. Exception: `spawn` - the summary goes on each `[[tasks]]` entry instead.\n"
        "- At most ONE `spawn` block per step (spawning is expensive).\n"
        "- Low-impact actions (write_whiteboard, read_items, read_theorem, write_items) can be combined freely with each other and with spawn.\n"
        "- Typical pattern: write_whiteboard + spawn, or write_whiteboard + write_items + spawn.\n"
        "\n"
        "Example with two blocks:\n"
        "\n"
        f"{_TOML_OPEN_TAG}\n"
        'action = "write_whiteboard"\n'
        'summary = "Update plan after worker results"\n'
        f'whiteboard = {_TQ}\n'
        "...\n"
        f'{_TQ}\n'
        f"{_TOML_CLOSE_TAG}\n"
        "\n"
        f"{_TOML_OPEN_TAG}\n"
        f'action = "spawn"\n'
        "\n"
        "[[tasks]]\n"
        'summary = "Prove Case 1: convex pentagon"\n'
        f'description = {_TQ}\n'
        "Prove that if 5 points in the plane have a convex hull with 5 vertices,\n"
        "then any 4 of them form a convex quadrilateral.\n"
        "\n"
        "The informal proof is in [[proofs/informal-main]] — see Case 1.\n"
        "Use the helper lemma from [[lemmas/extreme-point-not-in-hull]].\n"
        f'{_TQ}\n'
        f"{_TOML_CLOSE_TAG}\n"
        "\n"
        f"Valid actions: {', '.join(available_actions)}\n"
        "\n"
        "## Action-specific TOML fields\n"
        "\n"
        f"{toml_fields}"
    )

def worker_system_prompt(*, lean_worker_tools: bool = False) -> str:
    """Build worker system prompt, optionally documenting tool actions."""
    base = (
        "You are a research mathematician working on a specific task.\n"
        "\n"
        "Think carefully before writing your answer. Explore the problem, consider edge cases, "
        "and work through the reasoning step by step before stating conclusions.\n"
        "\n"
        "Complete the task and report your findings. "
        "If you get stuck, report concretely: "
        "(1) what you completed, "
        "(2) the exact blocker (specific error, missing lemma, or proof gap), "
        "(3) any useful intermediate results. "
        "Do not retry the same failing approach — if 3 attempts at similar code or queries "
        "fail with the same error, **stop and report the blocker**. "
        "The planner can adjust strategy.\n"
        "\n"
        "When writing proofs: write a **complete, rigorous, self-contained** argument. "
        "Define all notation, state and justify every non-trivial step, cite known theorems explicitly. "
        "Never write outline-level or sketch proofs — every logical step must be explicit.\n"
        "\n"
        "Write in concise mathematical style. Use $inline$ and $$display$$ LaTeX.\n"
        "\n"
        "IMPORTANT: You are a single worker. Do NOT attempt to spawn subagents, delegate to other workers, "
        "or \"launch agents in parallel\". You do all the work yourself, directly in your response.\n"
        "\n"
        "IMPORTANT: You have NO web access, NO search capability, and NO access to external databases or papers. "
        "Do not attempt literature searches or cite specific papers — you will hallucinate references. "
        "Work from first principles using your mathematical knowledge.\n"
        "\n"
        "IMPORTANT: All reasoning must happen in your thinking trace, not in your output. "
        "When writing your response, write the final answer directly — do not re-reason, backtrack, "
        "hedge with \"let me reconsider\", or narrate your thought process. "
        "Your thinking budget is for exploration; your output is for results.\n"
    )
    if lean_worker_tools:
        base += (
            "\n"
            "## Available Tools\n"
            "\n"
            "You have access to the following tools:\n"
            "\n"
            "- **lean_verify(code)**: Verify Lean 4 code. "
            "Code from `lean_store` is automatically prepended, so you only need "
            "to include new code. Returns 'OK' on success or compiler errors on failure.\n"
            "\n"
            "- **lean_store(code)**: Store a verified Lean 4 snippet (lemma, definition, "
            "import, etc.) into a persistent prefix. Stored code is automatically "
            "prepended to all subsequent `lean_verify` calls, so you don't need to "
            "repeat it. **IMPORTANT: The snippet MUST NOT contain `sorry` anywhere. "
            "Only store fully proven code — no placeholders, no `sorry` keywords.** "
            "The snippet must also compile without errors. "
            "Imports are automatically deduplicated and hoisted to the top.\n"
            "\n"
            "- **lean_search(query)**: Search Lean 4 declarations across Batteries, "
            "Init, Lean, Mathlib, and Std by name or meaning. "
            "Query with a declaration name (e.g. `lean_search('Nat.Prime')`, "
            "`lean_search('List.map')`) or a natural language description "
            "(e.g. `lean_search('continuous function on a compact set')`, "
            "`lean_search('sum of geometric series')`). "
            "Returns matching declaration names, source code, docstrings, "
            "and natural language descriptions.\n"
            "\n"
            "**lean_search tips:** Query building-block concepts (`convexHull`, `Finset.card`), "
            "not problem titles. Try synonyms if no results. After 3 misses on the same concept, "
            "stop searching and prove it from basics.\n"
            "\n"
            "## Formalization Strategy\n"
            "\n"
            "Build proofs one small lemma at a time. Use `sorry` placeholders to get a skeleton "
            "compiling, then fill them in one by one. Use `lean_store` to save each proven lemma "
            "(no `sorry` allowed) — it will be auto-prepended to future `lean_verify` calls.\n"
            "\n"
            "If the skeleton itself won't compile, simplify: use concrete types like `ℝ × ℝ` instead of "
            "abstract types, avoid unnecessary typeclasses, start with the simplest possible statement "
            "that captures the mathematical content.\n"
            "\n"
            "**Stopping rule:** If you hit the same error 3+ times, STOP. Report: "
            "(1) what compiles so far (lean_store it), (2) the exact Lean error, "
            "(3) what Mathlib lemma or tactic you need but couldn't find.\n"
        )
    return base


def verifier_system_prompt() -> str:
    """Build system prompt for the independent verifier."""
    return (
        "You are an independent verifier reviewing a mathematician's work.\n"
        "\n"
        "You will receive the original task and the worker's output. "
        "Your job is to independently verify the correctness of the worker's reasoning and conclusions.\n"
        "\n"
        "IMPORTANT: Do NOT verify formal Lean code statements - those are checked automatically by the system. "
        "Focus on:\n"
        "- Informal mathematical reasoning and proofs\n"
        "- Logical gaps or unjustified steps\n"
        "- Incorrect claims or conclusions\n"
        "- Whether the task was actually completed as requested\n"
        "\n"
        "End your response with exactly one of:\n"
        "VERDICT: CORRECT\n"
        "VERDICT: CRITICALLY FLAWED - <brief reason>\n"
        "VERDICT: NEEDS MINOR FIXES - <brief reason>\n"
        "\n"
        "Be concise. Use $inline$ and $$display$$ LaTeX.\n"
    )


def format_verifier_prompt(task_description: str, worker_output: str) -> str:
    """Format the prompt for a verifier given the original task and worker output."""
    return (
        f"# Original Task\n\n{task_description}\n\n"
        f"# Worker Output\n\n{worker_output}\n\n"
        f"# Your Task\n\n"
        f"Independently verify the worker's output above. "
        f"Do not verify formal Lean code - focus on informal reasoning, "
        f"logical correctness, and whether the task was completed as requested."
    )


def extract_verdict(verifier_output: str) -> str:
    """Extract the VERDICT line from verifier output, or return empty string."""
    for line in reversed(verifier_output.splitlines()):
        line = line.strip()
        if line.startswith("VERDICT:"):
            return line
    return ""


SEARCH_SYSTEM_PROMPT = (
    "You are a mathematical research assistant. Search for relevant mathematical "
    "literature and results. Report findings concisely with precise mathematical content."
)


# ── History truncation ──────────────────────────────────────


def _truncate_keep_end(text: str, limit: int) -> str:
    """Truncate from the start, keeping the end (where the TOML block is)."""
    if len(text) <= limit:
        return text
    return "...\n" + text[-(limit - 4):]


# ── Prompt formatters ───────────────────────────────────────

def format_planner_prompt(
    whiteboard: str,
    repo_index: str,
    step_history: list[dict],
    budget_status: str,
    parallelism: int = 1,
    *,
    theorem_text: str = "",
    has_lean_theorem: bool = False,
    has_proof_md: bool = False,
    has_proof_lean: bool = False,
    history_budget: int = 0,
) -> str:
    def heading(title):
        bar = "=" * (len(title) + 2)
        return f"{bar}\n {title}\n{bar}"

    parts = [f"{heading('WHITEBOARD')}\n\n{whiteboard}"]

    if theorem_text:
        parts.append(f"\n\n{heading('THEOREM')}\n\n{theorem_text}")

    # Status indicators
    status_lines = [f"- Theorem statement: already present"]
    if has_lean_theorem:
        status_lines.append(f"- Formal Lean statement of theorem: already present")
        status_lines.append(f"- Proof in natural language: {'already present' if has_proof_md else 'missing'}")
        status_lines.append(f"- Formal Lean proof (verified): {'already present' if has_proof_lean else 'missing'}")
    else:
        status_lines.append(f"- Proof: {'already present' if has_proof_md else 'missing'}")
    parts.append(f"\n\n{heading('STATUS')}\n\n" + "\n".join(status_lines))

    if repo_index:
        parts.append(f"\n\n{heading('REPOSITORY')}\n\n{repo_index}")
    if step_history and history_budget > 0:
        # Distribute budget: split evenly across entries, 2/3 planner 1/3 output
        per_entry = history_budget // len(step_history)
        planner_limit = per_entry * 2 // 3
        output_limit = per_entry - planner_limit

        parts.append(f"\n\n{heading('RECENT HISTORY')}")
        for entry in step_history:
            step = entry.get("step", "?")

            planner = entry.get("planner", "")
            if planner:
                planner = _truncate_keep_end(planner, planner_limit)
                parts.append(f"\n\n# Planner output (step {step})\n\n<planner_output>\n{planner}\n</planner_output>")

            # Support both new list format ("outputs") and legacy string ("output")
            outputs = entry.get("outputs")
            if outputs is None:
                legacy = entry.get("output", "")
                if legacy:
                    outputs = [{"action": entry.get("action", ""), "summary": entry.get("summary", ""), "output": legacy}]
                else:
                    outputs = []

            for i, ao in enumerate(outputs):
                text = ao.get("output", "")
                if not text:
                    continue
                text = _truncate_keep_end(text, output_limit)
                a_action = ao.get("action", "")
                a_summary = ao.get("summary", "")
                if len(outputs) > 1:
                    label = f"Action {i + 1} output (step {step})"
                else:
                    label = f"Action output (step {step})"
                if a_action:
                    label += f": {a_action}"
                if a_summary:
                    label += f" - {a_summary}"
                parts.append(f"\n\n# {label}\n\n<action_output>\n{text}\n</action_output>")
    parts.append(f"\nMax {parallelism} worker(s) per spawn. What's the most productive next move?")
    return "".join(parts)


def format_worker_prompt(task_description: str, resolved_refs: str) -> str:
    parts = [f"# Task\n\n{task_description}"]
    if resolved_refs:
        parts.append(f"\n\n# Referenced Materials\n\n{resolved_refs}")
    return "\n".join(parts)


def format_search_prompt(query: str, context: str) -> str:
    parts = [f"# Literature Search\n\nSearch query: {query}"]
    if context:
        parts.append(f"\n\nContext: {context}")
    parts.append(
        "\n\nSearch the web for relevant theorems, proof techniques, known results, "
        "or partial progress. Report concisely: what's known, what techniques are used, "
        "any useful references. Focus on mathematical content."
    )
    return "\n".join(parts)


def format_initial_whiteboard(theorem: str, mode: str) -> str:
    theorem_text = theorem.strip()
    if mode == "prove_and_formalize":
        return f"""## Goal

**Prove and Formalize**
Produce both an informal proof and a formal Lean 4 proof of this theorem:

### Theorem
{theorem_text}

## Plan

- [ ] Find a proof in natural language.
- [ ] Formalize the proof in Lean 4.

## Notes

(none)
"""
    # TODO: also inject the proof!
    if mode == "formalize_only":
        return f"""## Goal

**Formalize**
Formalize the proof of the following theorem in Lean 4:

### Theorem
{theorem_text}

## Plan

- [ ] Formalize the proof in Lean 4.

## Notes

(none)
"""
    if mode == "prove":
        return f"""## Goal

Produce a proof of this theorem:

### Theorem
{theorem_text}

## Plan

- [ ] Find a proof of the theorem.

## Notes

(none)
"""
    raise ValueError(f"Invalid mode: {mode}")


def discussion_system_prompt() -> str:
    """System prompt for the discussion call - user-facing, no planner actions."""
    return (
        "You are a senior research mathematician writing a brief post-mortem "
        "discussion of a proof effort.\n"
        "\n"
        "The reader is the person who posed the problem. Write for them - "
        "explain results, insights, and gaps in plain mathematical language. "
        "Do NOT reference internal system actions (spawn, read_theorem, "
        "write_items, etc.) - those were mechanisms used during the proof "
        "session and are not available to the reader. "
        "Recommendations should be about the mathematics, not about tooling.\n"
        "\n"
        "Use $ and $$ for LaTeX math. Reference repo items with [[slug]] "
        "links - the reader will have access to the full repo."
    )


def format_discussion_prompt(
    theorem: str,
    whiteboard: str,
    repo_index: str,
    steps_taken: int,
    budget_summary: str,
    proof: str = "",
    has_proof_md: bool = False,
    has_proof_lean: bool = False,
) -> str:
    parts = [
        f"# Theorem\n\n{theorem}",
        f"\n\n# Final Whiteboard\n\n{whiteboard}",
    ]
    # Explicit submission status so the LLM knows what actually happened,
    # regardless of whether the whiteboard was updated after submission.
    status_lines = []
    if has_proof_md:
        status_lines.append("- Informal proof (PROOF.md): **submitted and accepted**")
    if has_proof_lean:
        status_lines.append("- Formal Lean proof (PROOF.lean): **submitted and verified**")
    if status_lines:
        parts.append("\n\n# Submission Status\n\n" + "\n".join(status_lines))
    if repo_index:
        parts.append(f"\n\n# Repository\n\n{repo_index}")
    if proof:
        parts.append(f"\n\n# Proof\n\n{proof}")
    parts.append(f"\n\n{steps_taken} steps taken. Budget: {budget_summary}.")
    parts.append(
        "\n\nWrite a brief discussion. Begin by stating exactly what theorem was being proved "
        "(copy or paraphrase the statement precisely). Then cover: result, approaches tried, "
        "key insights, open gaps, recommendations. Use $ and $$ for math. "
        "Reference repo items with [[slug]] links - the reader will have access to the full repo."
    )
    return "".join(parts)


# ── Planner retry ──────────────────────────────────────────

def format_planner_retry(
    original_prompt: str,
    raw_output: str,
    error: str,
    attempt: int,
) -> str:
    """Build a retry prompt with error feedback appended to the original."""
    excerpt = raw_output[-500:] if len(raw_output) > 500 else raw_output
    if len(raw_output) > 500:
        excerpt = "..." + excerpt
    return (
        f"{original_prompt}\n\n"
        f"---\n\n"
        f"**RETRY ({attempt}/2)** - Your previous response could not be parsed.\n\n"
        f"Error: {error}\n\n"
        f"Your previous output ended with:\n"
        f"```\n{excerpt}\n```\n\n"
        f"Please respond again with a valid TOML decision block wrapped in "
        f"{_TOML_OPEN_TAG} ... {_TOML_CLOSE_TAG}."
    )


def format_planner_truncated(
    original_prompt: str,
    truncated_output: str,
) -> str:
    """Build a Phase 2 prompt when planner output was truncated."""
    excerpt = truncated_output[-2000:] if len(truncated_output) > 2000 else truncated_output
    if len(truncated_output) > 2000:
        excerpt = "..." + excerpt
    return (
        f"{original_prompt}\n\n"
        f"---\n\n"
        f"Your previous response was cut off. Here is what you generated:\n\n"
        f"```\n{excerpt}\n```\n\n"
        f"Produce ONLY the {_TOML_OPEN_TAG} ... {_TOML_CLOSE_TAG} decision block. "
        f"Do not reason further."
    )


# ── TOML parser ─────────────────────────────────────────────

class ParseError:
    """Represents a parse failure with a specific error message."""
    def __init__(self, message: str):
        self.message = message


def _parse_single_toml(toml_text: str) -> dict | None:
    """Parse a single TOML block string into a dict."""
    if tomllib is None:
        return _parse_toml_minimal(toml_text)
    try:
        return tomllib.loads(toml_text)
    except Exception:
        return _parse_toml_minimal(toml_text)


def parse_planner_toml(text: str) -> list[dict] | ParseError | None:
    """Extract and parse TOML decision blocks from planner output.

    Returns:
        list[dict]: One or more successfully parsed action blocks.
        ParseError: A block was found but had a specific problem.
        None: No OPENPROVER_ACTION block found at all.
    """
    # Find all <OPENPROVER_ACTION> ... </OPENPROVER_ACTION> blocks
    matches = re.findall(
        rf"{re.escape(_TOML_OPEN_TAG)}\s*\n?(.*?){re.escape(_TOML_CLOSE_TAG)}",
        text,
        re.DOTALL,
    )
    if not matches:
        return None

    plans: list[dict] = []
    spawn_count = 0
    for toml_text in matches:
        parsed = _parse_single_toml(toml_text)
        if parsed is None:
            parsed = {}

        action = parsed.get("action", "")
        if not action:
            return ParseError(
                'Missing required field: action = "...". '
                "Every OPENPROVER_ACTION block must include an action type. "
                f"Valid actions: {', '.join(ACTIONS)}."
            )
        if action not in ACTIONS:
            return ParseError(
                f'Unknown action: "{action}". '
                f"Valid actions: {', '.join(ACTIONS)}."
            )
        if action == "spawn":
            spawn_count += 1
            if spawn_count > 1:
                return ParseError(
                    "At most one spawn block is allowed per step. "
                    "Put ALL tasks inside a SINGLE spawn block using multiple [[tasks]] entries:\n"
                    "<OPENPROVER_ACTION>\n"
                    'action = "spawn"\n\n'
                    "[[tasks]]\n"
                    'summary = "First task"\n'
                    'description = """..."""\n\n'
                    "[[tasks]]\n"
                    'summary = "Second task"\n'
                    'description = """..."""\n'
                    "</OPENPROVER_ACTION>"
                )
        plans.append(parsed)

    return plans


def parse_saved_step_toml(text: str) -> dict | None:
    """Parse a saved planner.toml file (no OPENPROVER_ACTION tags)."""
    if tomllib is None:
        return _parse_toml_minimal(text)
    try:
        return tomllib.loads(text)
    except Exception:
        return _parse_toml_minimal(text)


def _parse_toml_minimal(text: str) -> dict | None:
    """Minimal TOML-ish parser for our specific format.

    Handles: top-level key = "value", triple-quoted multiline strings,
    key = [...] arrays, [[tasks]] and [[items]] array-of-tables.
    """
    result: dict = {}
    # Array-of-tables: [[tasks]], [[items]]
    array_tables: dict[str, list[dict]] = {"tasks": [], "items": []}
    current_table: dict | None = None

    lines = text.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Skip empty lines and comments
        if not line or line.startswith('#'):
            i += 1
            continue

        # [[tasks]] or [[items]] - start a new table entry
        if line in ('[[tasks]]', '[[items]]'):
            table_name = line[2:-2]
            current_table = {}
            array_tables[table_name].append(current_table)
            i += 1
            continue

        # key = value
        m = re.match(r'(\w+)\s*=\s*(.*)', line)
        if not m:
            i += 1
            continue

        key = m.group(1)
        rest = m.group(2).strip()
        target = current_table if current_table is not None else result

        # Triple-quoted multiline string
        if rest.startswith('"""'):
            content_parts = [rest[3:]]
            i += 1
            while i < len(lines):
                if '"""' in lines[i]:
                    before = lines[i].split('"""')[0]
                    content_parts.append(before)
                    break
                content_parts.append(lines[i])
                i += 1
            target[key] = '\n'.join(content_parts).strip()
            i += 1
            continue

        # Single-line string
        if rest.startswith('"') and rest.endswith('"'):
            target[key] = rest[1:-1]
            i += 1
            continue

        # Array
        if rest.startswith('['):
            arr_text = rest
            while arr_text.count('[') > arr_text.count(']') and i + 1 < len(lines):
                i += 1
                arr_text += lines[i].strip()
            items = re.findall(r'"([^"]*)"', arr_text)
            target[key] = items
            i += 1
            continue

        # Boolean
        if rest in ('true', 'false'):
            target[key] = rest == 'true'
            i += 1
            continue

        # Bare value
        target[key] = rest
        i += 1

    for name, entries in array_tables.items():
        if entries:
            result[name] = entries

    return result or None
