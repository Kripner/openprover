"""MCP server exposing lean_verify and lean_search tools for Claude CLI.

Runs as a subprocess spawned by Claude CLI via --mcp-config.
Communicates over stdio using JSON-RPC (MCP protocol).

Environment variables:
    LEAN_PROJECT_DIR: Path to Lean project with lakefile (required for lean_verify)
    LEAN_WORK_DIR: Path to working directory for temporary Lean files
"""

import asyncio
import os
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from .core import LeanWorkDir, lean_has_errors, merge_lean_imports, run_lean_check, strip_code_fences

mcp = FastMCP("lean_tools")

# Initialized lazily from environment variables
_project_dir: Path | None = None
_work_dir: LeanWorkDir | None = None
_search_service = None
_store: str = ""  # per-process store (each worker gets its own MCP subprocess)


def _get_project_dir() -> Path:
    global _project_dir
    if _project_dir is None:
        val = os.environ.get("LEAN_PROJECT_DIR")
        if not val:
            raise RuntimeError("LEAN_PROJECT_DIR not set")
        _project_dir = Path(val)
    return _project_dir


def _get_work_dir() -> LeanWorkDir:
    global _work_dir
    if _work_dir is None:
        val = os.environ.get("LEAN_WORK_DIR")
        if val:
            # Use the specified directory directly (already created by Prover)
            wd = LeanWorkDir.__new__(LeanWorkDir)
            wd.project_dir = _get_project_dir()
            wd.dir = Path(val)
            wd.dir.mkdir(parents=True, exist_ok=True)
            wd.random_id = "mcp"
            _work_dir = wd
        else:
            _work_dir = LeanWorkDir(_get_project_dir())
    return _work_dir


_has_gpu: bool | None = None

def _gpu_available() -> bool:
    global _has_gpu
    if _has_gpu is None:
        try:
            import torch
            _has_gpu = torch.cuda.is_available()
        except Exception:
            _has_gpu = False
    return _has_gpu


def _get_search_service():
    global _search_service
    if _search_service is None:
        from lean_explore.search import SearchEngine, Service
        engine = SearchEngine(use_local_data=False)
        _search_service = Service(engine=engine)
    return _search_service


@mcp.tool()
def lean_verify(code: str) -> str:
    """Verify Lean 4 code. Returns compiler output (errors/warnings or OK). Code from lean_store is automatically prepended."""
    code = strip_code_fences(code)
    if not code.strip():
        raise ValueError("no code provided")
    work_dir = _get_work_dir()
    project_dir = _get_project_dir()
    full_code = merge_lean_imports(_store, code) if _store else code
    path = work_dir.make_file("mcp_verify", full_code)
    success, feedback, _cmd_info = run_lean_check(path, project_dir)
    if success:
        result = "OK - no errors"
    else:
        result = feedback
        if not lean_has_errors(feedback) and "sorry" in feedback.lower():
            result += (
                "\n\nNote: code contains sorry — this means the proof has gaps. "
                "lean_store will REJECT code with sorry. You must fill ALL sorry "
                "holes with actual proof terms before storing."
            )
    if _store:
        store_lines = len(_store.splitlines())
        result = f"({store_lines} lines from lean_store were automatically prepended)\n{result}"
    return result


@mcp.tool()
def lean_store(code: str) -> str:
    """Store a verified Lean 4 snippet (lemma, definition, etc.) into the persistent prefix. Stored code is automatically prepended to all subsequent lean_verify calls. The snippet must compile without errors or sorry. Imports are automatically deduplicated."""
    global _store
    code = strip_code_fences(code)
    if not code.strip():
        raise ValueError("no code provided")
    work_dir = _get_work_dir()
    project_dir = _get_project_dir()
    candidate = merge_lean_imports(_store, code)
    path = work_dir.make_file("mcp_store", candidate)
    success, feedback, _cmd_info = run_lean_check(path, project_dir)
    if not success:
        if lean_has_errors(feedback):
            return feedback
        if "sorry" in feedback.lower():
            return f"Store rejected: code contains sorry\n{feedback}"
        # Non-sorry warnings are acceptable
    _store = candidate
    return f"OK - stored.\n\nCurrent store:\n```lean\n{candidate}\n```"


@mcp.tool()
async def lean_search(query: str) -> str:
    """Search Lean 4 declarations by name or natural language description. Query with a declaration name (e.g. 'List.map', 'Nat.Prime') or an informal description (e.g. 'continuous function on a compact set'). Uses hybrid retrieval (lexical + semantic)."""
    if not query.strip():
        raise ValueError("no query provided")
    service = _get_search_service()
    rerank = 25 if _gpu_available() else 0
    response = await service.search(
        query, limit=10, rerank_top=rerank,
        packages=["Mathlib", "Batteries", "Init", "Lean", "Std"],
    )
    results = response.results
    if not results:
        return "No results found"
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
    return "\n\n".join(parts)


if __name__ == "__main__":
    mcp.run(transport="stdio")
