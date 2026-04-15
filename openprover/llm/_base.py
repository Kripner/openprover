"""Shared utilities for LLM client modules."""

import json
from pathlib import Path


class Interrupted(Exception):
    """Raised when an LLM call is cancelled via interrupt()."""
    pass


class StreamingUnavailable(RuntimeError):
    """Raised when HF server cannot stream in current configuration."""
    pass


def is_rate_limited_error(exc: Exception) -> bool:
    """Detect rate-limit / spending-limit errors from LLM CLI calls.

    Covers HTTP 429s as well as Claude-CLI messages about spending caps,
    billing, quota, or generic "rate limit" wording.
    """
    msg = str(exc).lower()
    if "429" in msg:
        return True
    return ("spending" in msg or "spend limit" in msg
            or "billing" in msg or "quota" in msg
            or ("rate" in msg and "limit" in msg))


def is_transient_error(exc: Exception) -> bool:
    """Detect transient errors worth retrying (timeouts, gateway hiccups).

    Covers request timeouts from upstream gateways (notably Z.ai's Anthropic
    bridge for GLM, which sporadically returns exit-1 with
    `result: "Request timed out"`) and common 5xx gateway errors.
    """
    msg = str(exc).lower()
    if any(code in msg for code in ("502", "503", "504")):
        return True
    return ("request timed out" in msg
            or "request timeout" in msg
            or "read timed out" in msg
            or "connection reset" in msg
            or "connection aborted" in msg
            or ("gateway" in msg and "time" in msg))


def archive(model, archive_dir, call_num, label, prompt, system_prompt,
            json_schema, response, error, elapsed_ms, archive_path=None,
            *, thinking="", result_text=""):
    """Archive an LLM call to a readable markdown file + raw JSON sidecar."""
    if archive_path:
        path = archive_path
        path.parent.mkdir(parents=True, exist_ok=True)
    else:
        archive_dir.mkdir(parents=True, exist_ok=True)
        path = archive_dir / f"call_{call_num:03d}.md"

    # Extract cost/tokens from raw response for frontmatter
    raw = response or {}
    usage = raw.get("usage", {})
    cost_usd = raw.get("total_cost_usd", 0.0)
    input_tokens = usage.get("input_tokens", usage.get("prompt_tokens", 0))
    output_tokens = usage.get("output_tokens", usage.get("completion_tokens", 0))
    cache_creation = usage.get("cache_creation_input_tokens", 0)
    cache_read = usage.get("cache_read_input_tokens", 0)
    stop_reason = raw.get("stop_reason", "")

    # Build YAML frontmatter
    fm_lines = [
        "---",
        f"call_num: {call_num}",
        f"label: {label}",
        f"model: {model}",
        f"elapsed_ms: {elapsed_ms}",
    ]
    if cost_usd:
        fm_lines.append(f"cost_usd: {cost_usd}")
    if input_tokens:
        fm_lines.append(f"input_tokens: {input_tokens}")
    if output_tokens:
        fm_lines.append(f"output_tokens: {output_tokens}")
    if cache_creation:
        fm_lines.append(f"cache_creation_tokens: {cache_creation}")
    if cache_read:
        fm_lines.append(f"cache_read_tokens: {cache_read}")
    if stop_reason:
        fm_lines.append(f"stop_reason: {stop_reason}")
    if error:
        # Single-line errors go inline, multi-line get quoted
        err_str = str(error)
        if "\n" in err_str:
            fm_lines.append(f'error: "{err_str.splitlines()[0][:200]}..."')
        else:
            fm_lines.append(f"error: {err_str[:200]}")
    fm_lines.append("---")

    # Build markdown body with section separators
    parts = ["\n".join(fm_lines)]

    if system_prompt:
        parts.append(f"\n\n======== SYSTEM PROMPT ========\n\n{system_prompt}")

    if prompt:
        parts.append(f"\n\n======== USER PROMPT ========\n\n{prompt}")

    if json_schema:
        parts.append(f"\n\n======== JSON SCHEMA ========\n\n```json\n{json.dumps(json_schema, indent=2)}\n```")

    if thinking:
        parts.append(f"\n\n======== THINKING ========\n\n{thinking}")

    if result_text:
        parts.append(f"\n\n======== RESPONSE ========\n\n{result_text}")
    elif error:
        parts.append(f"\n\n======== ERROR ========\n\n{error}")
    elif response is None:
        parts.append(f"\n\n======== RESPONSE ========\n\n(waiting for LLM response)")

    path.write_text("".join(parts) + "\n")

    # Write raw API response as JSON sidecar for debugging
    if response:
        raw_path = path.with_suffix(".raw.json")
        raw_path.write_text(json.dumps(response, indent=2, ensure_ascii=False))
