"""Lean tool definitions and execution for vLLM worker tool-calling."""

import asyncio
import logging
import time

from .core import LeanWorkDir, lean_has_errors, merge_lean_imports, run_lean_check, strip_code_fences

logger = logging.getLogger("openprover.lean")

# Per-worker store state (vLLM path only; MCP uses per-process module state)
_worker_stores: dict[str, str] = {}

WORKER_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "lean_verify",
            "description": "Verify Lean 4 code. Returns compiler output (errors/warnings or OK).",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Complete Lean 4 source code to verify.",
                    },
                },
                "required": ["code"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "lean_store",
            "description": "Store a verified Lean 4 snippet (lemma, definition, etc.) into the persistent prefix. Stored code is automatically prepended to all subsequent lean_verify calls, so you don't need to repeat it. The snippet must compile without errors or sorry. Imports are automatically deduplicated.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Lean 4 code to store (must compile without errors or sorry).",
                    },
                },
                "required": ["code"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "lean_search",
            "description": "Search Lean 4 declarations by name or natural language description. Supports two query styles: by declaration name (e.g. 'List.map', 'Nat.Prime') or by meaning (e.g. 'continuous function on a compact set'). Uses hybrid retrieval (lexical + semantic) so both styles work automatically.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "A Lean declaration name (e.g. 'List.filter', 'Nat.Prime') or an informal natural language description (e.g. 'prime number divisibility', 'sum of geometric series').",
                    },
                },
                "required": ["query"],
            },
        },
    },
]


def execute_worker_tool(
    name: str,
    args: dict,
    worker_id: str,
    lean_work_dir: LeanWorkDir | None,
    lean_project_dir,
    lean_explore_service,
) -> tuple[str, str]:
    """Execute a worker tool call. Returns (result_text, status)."""
    if name == "lean_verify":
        return _tool_lean_verify(args, worker_id, lean_work_dir, lean_project_dir)
    if name == "lean_store":
        return _tool_lean_store(args, worker_id, lean_work_dir, lean_project_dir)
    if name == "lean_search":
        return _tool_lean_search(args, worker_id, lean_explore_service)
    return (f"Unknown tool: {name}", "error")


def _tool_lean_verify(
    args: dict,
    worker_id: str,
    lean_work_dir: LeanWorkDir | None,
    lean_project_dir,
) -> tuple[str, str]:
    """Verify Lean code via lean_check."""
    code = strip_code_fences(args.get("code", ""))
    if not code:
        return ("No code provided", "error")
    if not lean_work_dir:
        return ("Lean project not configured", "error")

    # Prepend stored prefix if any
    store = _worker_stores.get(worker_id, "")
    full_code = merge_lean_imports(store, code) if store else code
    if store:
        args["_store_prefix"] = store  # expose to TUI detail page

    slug = f"worker_verify_{worker_id}"
    path = lean_work_dir.make_file(slug, full_code)
    success, feedback, _cmd_info = run_lean_check(path, lean_project_dir)
    if success:
        status = "ok"
        result = "OK"
    else:
        # Distinguish real errors from warnings-only
        if lean_has_errors(feedback):
            status = "error"
        elif "sorry" in feedback.lower():
            status = "partial"
            feedback += (
                "\n\nNote: code contains sorry — this means the proof has gaps. "
                "lean_store will REJECT code with sorry. You must fill ALL sorry "
                "holes with actual proof terms before storing."
            )
        else:
            # Warnings only, no errors - treat as success
            status = "ok"
        result = feedback
    logger.info("[%s] lean_verify: %s", worker_id, status)
    return (result, status)


def _tool_lean_store(
    args: dict,
    worker_id: str,
    lean_work_dir: LeanWorkDir | None,
    lean_project_dir,
) -> tuple[str, str]:
    """Store a verified Lean snippet into the worker's persistent prefix."""
    code = strip_code_fences(args.get("code", ""))
    if not code:
        return ("No code provided", "error")
    if not lean_work_dir:
        return ("Lean project not configured", "error")

    store = _worker_stores.get(worker_id, "")
    candidate = merge_lean_imports(store, code)

    slug = f"worker_store_{worker_id}"
    path = lean_work_dir.make_file(slug, candidate)
    success, feedback, _cmd_info = run_lean_check(path, lean_project_dir)

    if not success:
        if lean_has_errors(feedback):
            logger.info("[%s] lean_store: rejected (errors)", worker_id)
            return (feedback, "error")
        # Warnings only - check for sorry
        if "sorry" in feedback.lower():
            logger.info("[%s] lean_store: rejected (sorry)", worker_id)
            return (f"Store rejected: code contains sorry\n{feedback}", "error")
        # Non-sorry warnings are acceptable

    _worker_stores[worker_id] = candidate
    logger.info("[%s] lean_store: ok (%d chars)", worker_id, len(candidate))
    return (f"OK - stored.\n\nCurrent store:\n```lean\n{candidate}\n```", "ok")


def _tool_lean_search(
    args: dict,
    worker_id: str,
    lean_explore_service,
) -> tuple[str, str]:
    """Search Mathlib declarations."""
    import torch
    query = args.get("query", "")
    if not query:
        return ("No query provided", "error")
    if not lean_explore_service:
        return ("lean_search not available (lean_explore not installed)", "error")

    rerank = 25 if torch.cuda.is_available() else 0
    try:
        t0 = time.time()
        response = asyncio.run(
            lean_explore_service.search(
                query, limit=10, rerank_top=rerank,
                packages=["Mathlib", "Batteries", "Init", "Lean", "Std"],
            )
        )
        elapsed = time.time() - t0
        results = response.results
        logger.info("[%s] lean_search query=%r returned %d results in %.1fs",
                    worker_id, query, len(results), elapsed)
        if not results:
            return ("No results found", "ok")
        parts = []
        for r in results:
            name = getattr(r, 'name', '')
            module = getattr(r, 'module', '') or ''
            source = getattr(r, 'source_text', '') or ''
            doc = getattr(r, 'docstring', '') or ''
            info = getattr(r, 'informalization', '') or ''
            header = f"**{name}**"
            if module:
                header += f"  ({module})"
            entry = header
            if source:
                entry += f"\n```lean\n{source.strip()}\n```"
            if doc:
                entry += f"\n{doc.strip()}"
            if info:
                entry += f"\nInformalization: {info.strip()}"
            parts.append(entry)
        return ("\n\n".join(parts), "ok")
    except Exception as e:
        logger.warning("[%s] lean_search error: %s", worker_id, e)
        return (f"Search error: {e}", "error")
