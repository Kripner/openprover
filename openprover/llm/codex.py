"""OpenAI Codex CLI client for OpenProver."""

import json
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

from ._base import Interrupted, archive, kill_process_tree

logger = logging.getLogger("openprover.llm")


_FALLBACK_CONTEXT_LENGTH = 200_000
_GPT5_CONTEXT_LENGTH = 400_000
_CODEX_PRICING_USD_PER_MILLION: list[tuple[str, tuple[float, float, float]]] = [
    ("gpt-5.2-codex", (1.75, 0.175, 14.0)),
    ("gpt-5.2", (1.75, 0.175, 14.0)),
    ("gpt-5.1-codex-mini", (0.25, 0.025, 2.0)),
    ("gpt-5-mini", (0.25, 0.025, 2.0)),
    ("gpt-5.1-codex-max", (1.25, 0.125, 10.0)),
    ("gpt-5.1-codex", (1.25, 0.125, 10.0)),
    ("gpt-5-codex", (1.25, 0.125, 10.0)),
    ("gpt-5.1", (1.25, 0.125, 10.0)),
    ("gpt-5", (1.25, 0.125, 10.0)),
]


def _compose_prompt(system_prompt: str, prompt: str) -> str:
    """Embed the OpenProver system prompt into the stdin prompt for Codex."""
    if not system_prompt:
        return prompt
    payload = {
        "system_prompt": system_prompt.rstrip(),
        "user_prompt": prompt,
    }
    return (
        "Treat the following JSON object as the request context.\n"
        "The `system_prompt` value is higher priority than `user_prompt`.\n\n"
        f"{json.dumps(payload, ensure_ascii=False, indent=2)}"
    )


def _normalize_item_type(item_type: str) -> str:
    """Normalize Codex item types to a stable snake_case form."""
    return item_type.replace("-", "_").replace(" ", "_").lower()


def _match_model_prefix(model: str, prefix: str) -> bool:
    """Match an exact model id or a snapshot/build suffix of that id."""
    model = model.lower()
    prefix = prefix.lower()
    return model == prefix or model.startswith(f"{prefix}-")


def _lookup_codex_pricing(model: str) -> tuple[float, float, float] | None:
    """Return per-1M token pricing for known published Codex/OpenAI models."""
    if not model:
        return None
    normalized = model.lower()
    for prefix, pricing in _CODEX_PRICING_USD_PER_MILLION:
        if _match_model_prefix(normalized, prefix):
            return pricing
    return None


def _infer_context_length(model: str) -> int:
    """Infer a context window from the explicit Codex model id when known."""
    if model and model.lower().startswith("gpt-5"):
        return _GPT5_CONTEXT_LENGTH
    return _FALLBACK_CONTEXT_LENGTH


def _estimate_cost_usd(model: str, usage: dict) -> float:
    """Estimate Codex cost from usage for known published model ids."""
    pricing = _lookup_codex_pricing(model)
    if not pricing:
        return 0.0
    input_price, cached_input_price, output_price = pricing
    input_tokens = int(usage.get("input_tokens", 0) or 0)
    cached_input_tokens = int(usage.get("cached_input_tokens", 0) or 0)
    output_tokens = int(usage.get("output_tokens", 0) or 0)
    uncached_input_tokens = max(input_tokens - cached_input_tokens, 0)
    return (
        uncached_input_tokens * input_price
        + cached_input_tokens * cached_input_price
        + output_tokens * output_price
    ) / 1_000_000


def _find_codex_bin() -> str:
    """Resolve the Codex executable appropriate for the current platform."""
    if sys.platform == "win32":
        candidates = ("codex.cmd", "codex")
    else:
        candidates = ("codex", "codex.cmd")
    for name in candidates:
        path = shutil.which(name)
        if path:
            return path
    return candidates[0]


def _extract_mcp_servers(mcp_config: dict | None) -> dict:
    """Accept either Claude-style mcpServers or Codex-style mcp_servers."""
    if not mcp_config:
        return {}
    servers = mcp_config.get("mcpServers")
    if isinstance(servers, dict):
        return servers
    servers = mcp_config.get("mcp_servers")
    if isinstance(servers, dict):
        return servers
    return {}


def _codex_mcp_overrides(mcp_config: dict | None) -> list[str]:
    """Convert an MCP config dict into Codex CLI `-c` overrides."""
    overrides: list[str] = []
    for name, cfg in sorted(_extract_mcp_servers(mcp_config).items()):
        if not isinstance(cfg, dict):
            continue
        prefix = f"mcp_servers.{name}"
        if "command" in cfg:
            overrides.extend(["-c", f"{prefix}.command={json.dumps(str(cfg['command']))}"])
            args = cfg.get("args") or []
            overrides.extend(["-c", f"{prefix}.args={json.dumps([str(a) for a in args])}"])
            env = cfg.get("env") or {}
            for env_key, env_val in sorted(env.items()):
                overrides.extend([
                    "-c",
                    f"{prefix}.env.{env_key}={json.dumps(str(env_val))}",
                ])
        if "url" in cfg:
            overrides.extend(["-c", f"{prefix}.url={json.dumps(str(cfg['url']))}"])
        token_env = cfg.get("bearer_token_env_var") or cfg.get("bearerTokenEnvVar")
        if token_env:
            overrides.extend([
                "-c",
                f"{prefix}.bearer_token_env_var={json.dumps(str(token_env))}",
            ])
    return overrides


def _extract_tool_result_text(result) -> str:
    """Extract readable text from a Codex MCP tool result payload."""
    if result is None:
        return ""
    if isinstance(result, str):
        return result
    if isinstance(result, dict):
        content = result.get("content")
        if isinstance(content, list):
            parts: list[str] = []
            for item in content:
                if not isinstance(item, dict):
                    continue
                if item.get("type") == "text" and item.get("text"):
                    parts.append(str(item["text"]))
            if parts:
                return "\n".join(parts)
        structured = result.get("structured_content")
        if structured is not None:
            return json.dumps(structured, ensure_ascii=False)
    return json.dumps(result, ensure_ascii=False)


def _infer_tool_status(name: str, result_text: str, is_error: bool) -> str:
    """Map MCP tool results onto the statuses the TUI already understands."""
    if is_error:
        return "error"
    if name == "lean_verify":
        first_line = result_text.split("\n", 1)[0]
        if "OK" in first_line or result_text.startswith("OK"):
            return "ok"
        if re.search(r"^\d+:\d+: error", result_text, re.MULTILINE):
            return "error"
        if "sorry" in result_text.lower():
            return "partial"
        return "ok"
    if name == "lean_store":
        return "ok" if result_text.startswith("OK") else "error"
    return "ok"


class CodexClient:
    """Calls Codex CLI via `codex exec --json` and archives interactions."""

    context_length = _FALLBACK_CONTEXT_LENGTH
    supports_mcp_tools = True

    def __init__(self, model: str, archive_dir: Path,
                 max_output_tokens: int = 32_000,
                 answer_reserve: int = 4096,
                 reasoning_effort: str | None = None):
        self.model = model
        self.archive_dir = archive_dir
        self.call_count = 0
        self.total_cost = 0.0
        self.max_output_tokens = max_output_tokens
        self.answer_reserve = answer_reserve
        self.reasoning_effort = reasoning_effort
        self.context_length = _infer_context_length(model)
        self.mcp_config: dict | None = None
        self._interrupted = threading.Event()
        self._soft_interrupted = threading.Event()
        self._active_procs: list[subprocess.Popen] = []
        self._procs_lock = threading.Lock()
        self._work_dir = archive_dir.resolve()
        self._codex_bin = _find_codex_bin()

    def interrupt(self):
        """Signal all active Codex calls to stop."""
        self._interrupted.set()
        self._kill_active_procs()

    def soft_interrupt(self):
        """Ask active Codex calls to finish the current response if possible.

        Codex JSON mode only emits the assistant message on completion, so
        killing the process here loses the in-flight answer entirely. A hard
        interrupt still terminates immediately via interrupt().
        """
        self._soft_interrupted.set()

    def cleanup(self):
        """Kill all active subprocesses. Safe to call multiple times."""
        self._kill_active_procs()

    def _kill_active_procs(self):
        with self._procs_lock:
            for proc in self._active_procs:
                if proc.poll() is None:
                    kill_process_tree(proc)

    def clear_interrupt(self):
        """Reset the interrupt flag so new calls can proceed."""
        self._interrupted.clear()
        self._soft_interrupted.clear()

    def clear_soft_interrupt(self):
        """Reset only the soft interrupt flag."""
        self._soft_interrupted.clear()

    def call(
        self,
        prompt: str,
        system_prompt: str,
        json_schema: dict | None = None,
        label: str = "",
        web_search: bool = False,
        stream_callback=None,
        archive_path: Path | None = None,
        tool_callback=None,
        tool_start_callback=None,
        max_tokens: int | None = None,  # currently ignored by Codex CLI
    ) -> dict:
        """Make a Codex CLI call and archive it."""
        del max_tokens

        self.call_count += 1
        call_num = self.call_count

        self._archive(call_num, label, prompt, system_prompt, json_schema,
                      None, None, 0, archive_path)

        logger.info("[%s] calling codex%s", label,
                    f" ({self.model})" if self.model else "")

        if self._interrupted.is_set():
            self._archive(call_num, label, prompt, system_prompt, json_schema,
                          None, "interrupted", 0, archive_path)
            logger.info("[%s] interrupted before call started", label)
            raise Interrupted()

        composed_prompt = _compose_prompt(system_prompt, prompt)
        cmd, schema_path = self._build_cmd(
            web_search=web_search,
            json_schema=json_schema,
        )
        start = time.time()

        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            # New session/process group on Unix so kill_process_tree() can
            # tear down the full Codex subprocess tree. Windows cleanup uses
            # taskkill /T and does not depend on killpg semantics.
            start_new_session=True,
        )
        with self._procs_lock:
            self._active_procs.append(proc)

        try:
            if proc.stdin:
                proc.stdin.write(composed_prompt)
                proc.stdin.close()
            result = self._collect_events(
                proc=proc,
                call_num=call_num,
                label=label,
                prompt=prompt,
                system_prompt=system_prompt,
                json_schema=json_schema,
                archive_path=archive_path,
                start=start,
                stream_callback=stream_callback,
                tool_callback=tool_callback,
                tool_start_callback=tool_start_callback,
            )
        finally:
            with self._procs_lock:
                if proc in self._active_procs:
                    self._active_procs.remove(proc)
            if schema_path:
                schema_path.unlink(missing_ok=True)

        return result

    def _build_cmd(self, *, web_search: bool,
                   json_schema: dict | None) -> tuple[list[str], Path | None]:
        """Build a `codex exec` command line for a single call."""
        cmd = [self._codex_bin]
        if web_search:
            cmd.append("--search")
        cmd.extend([
            "-a", "never",
            "-s", "read-only",
            "exec",
            "--json",
            "--ephemeral",
            "--skip-git-repo-check",
            "--cd", str(self._work_dir),
        ])
        if self.model and self.model != "codex":
            cmd.extend(["-m", self.model])
        if self.reasoning_effort:
            cmd.extend([
                "-c",
                f"model_reasoning_effort={json.dumps(self.reasoning_effort)}",
            ])
        cmd.extend(_codex_mcp_overrides(self.mcp_config))

        schema_path = None
        if json_schema:
            fd, raw_path = tempfile.mkstemp(
                prefix="openprover-codex-schema-",
                suffix=".json",
            )
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(json_schema, f, ensure_ascii=False)
            schema_path = Path(raw_path)
            cmd.extend(["--output-schema", str(schema_path)])

        return cmd, schema_path

    def _collect_events(self, *, proc: subprocess.Popen,
                        call_num: int, label: str,
                        prompt: str, system_prompt: str,
                        json_schema: dict | None,
                        archive_path: Path | None,
                        start: float,
                        stream_callback,
                        tool_callback,
                        tool_start_callback) -> dict:
        """Read Codex JSONL events and produce an OpenProver-style response."""
        raw_events: list[dict] = []
        last_agent_message = ""
        usage: dict = {}
        interrupted = False
        soft_interrupted = False
        event_error = ""
        tool_start_times: dict[str, float] = {}

        try:
            while True:
                if self._interrupted.is_set():
                    interrupted = True
                    kill_process_tree(proc)
                    break

                line = proc.stdout.readline()
                if not line:
                    break
                line = line.strip()
                if not line:
                    continue
                try:
                    msg = json.loads(line)
                except json.JSONDecodeError:
                    continue

                raw_events.append(msg)
                msg_type = msg.get("type", "")

                if msg_type == "turn.completed":
                    usage = msg.get("usage", {}) or {}
                    continue

                if msg_type.endswith(".failed") or msg_type == "error":
                    event_error = json.dumps(msg, ensure_ascii=False)
                    continue

                item = msg.get("item")
                if not isinstance(item, dict):
                    continue
                item_type = _normalize_item_type(str(item.get("type", "")))

                if msg_type == "item.started":
                    if item_type == "mcp_tool_call" and tool_start_callback:
                        tool_name = str(item.get("tool") or item.get("name") or "")
                        tool_args = item.get("arguments") or item.get("input") or {}
                        tool_id = str(item.get("id") or "")
                        if tool_id:
                            tool_start_times[tool_id] = time.time()
                        tool_start_callback(tool_name, tool_args)
                    continue

                if msg_type != "item.completed":
                    continue

                if item_type == "agent_message":
                    last_agent_message = str(item.get("text") or "")
                    continue

                if item_type != "mcp_tool_call" or not tool_callback:
                    continue

                tool_name = str(item.get("tool") or item.get("name") or "")
                tool_args = item.get("arguments") or item.get("input") or {}
                result_text = _extract_tool_result_text(item.get("result"))
                is_error = bool(item.get("error"))
                if is_error and not result_text:
                    result_text = str(item.get("error"))
                status = _infer_tool_status(tool_name, result_text, is_error)
                tool_id = str(item.get("id") or "")
                started_at = tool_start_times.pop(tool_id, None)
                duration_ms = 0
                if started_at is not None:
                    duration_ms = int((time.time() - started_at) * 1000)
                tool_callback(tool_name, tool_args, result_text, status, duration_ms)
        finally:
            proc.wait()

        elapsed_ms = int((time.time() - start) * 1000)
        stderr = proc.stderr.read() if proc.stderr else ""

        # Soft interrupts are advisory for Codex: allow the current response to
        # finish so we keep the agent message instead of discarding it.
        if self._soft_interrupted.is_set():
            soft_interrupted = True
            self._soft_interrupted.clear()

        if interrupted:
            self._archive(call_num, label, prompt, system_prompt, json_schema,
                          None, "interrupted", elapsed_ms, archive_path)
            logger.info("[%s] interrupted after %dms", label, elapsed_ms)
            raise Interrupted()

        if proc.returncode != 0:
            err = stderr.strip() or event_error or (
                f"Codex CLI failed (exit {proc.returncode})"
            )
            self._archive(call_num, label, prompt, system_prompt, json_schema,
                          None, err, elapsed_ms, archive_path)
            raise RuntimeError(err[:1000])

        if event_error:
            self._archive(call_num, label, prompt, system_prompt, json_schema,
                          None, event_error, elapsed_ms, archive_path)
            raise RuntimeError(event_error[:1000])

        raw = {
            "model": self.model,
            "usage": {
                "input_tokens": usage.get("input_tokens", 0),
                "output_tokens": usage.get("output_tokens", 0),
                "cache_read_input_tokens": usage.get("cached_input_tokens", 0),
            },
            "stop_reason": "completed",
            "events": raw_events,
        }
        cost = _estimate_cost_usd(self.model, usage)
        if cost:
            raw["total_cost_usd"] = cost
            self.total_cost += cost

        self._archive(call_num, label, prompt, system_prompt, json_schema,
                      raw, None, elapsed_ms, archive_path,
                      result_text=last_agent_message)
        if soft_interrupted:
            logger.info("[%s] soft interrupt requested; returned completed output after %dms",
                        label, elapsed_ms)
        else:
            logger.info("[%s] done %dms", label, elapsed_ms)

        if stream_callback and last_agent_message:
            stream_callback(last_agent_message, "text")

        return {
            "result": last_agent_message,
            "thinking": "",
            "cost": cost,
            "duration_ms": elapsed_ms,
            "raw": raw,
            "finish_reason": "stop",
        }

    def _archive(self, call_num, label, prompt, system_prompt, json_schema,
                 response, error, elapsed_ms, archive_path=None,
                 *, thinking="", result_text=""):
        archive(self.model, self.archive_dir, call_num, label, prompt,
                system_prompt, json_schema, response, error, elapsed_ms,
                archive_path, thinking=thinking, result_text=result_text)
