"""Claude CLI client for OpenProver."""

import json
import logging
import os
import re
import subprocess
import threading
import time
from pathlib import Path

from ._base import Interrupted, archive, kill_process_tree

logger = logging.getLogger("openprover.llm")


class LLMClient:
    """Calls Claude via the CLI and archives all interactions."""

    context_length = 200_000  # Claude models
    supports_mcp_tools = True

    def __init__(self, model: str, archive_dir: Path,
                 max_output_tokens: int = 128_000,
                 reasoning_effort: str | None = None,
                 effort: str | None = None):
        self.model = model
        self.archive_dir = archive_dir
        self.call_count = 0
        self.total_cost = 0.0
        self.max_output_tokens = max_output_tokens
        if effort is not None and reasoning_effort is not None and effort != reasoning_effort:
            raise ValueError("effort and reasoning_effort must match when both are provided")
        self.effort = effort or reasoning_effort
        self.mcp_config: dict | None = None  # set by Prover for MCP tool-calling
        self._interrupted = threading.Event()
        self._soft_interrupted = threading.Event()
        self._active_procs: list[subprocess.Popen] = []
        self._procs_lock = threading.Lock()
        # Override Claude CLI's default 32k output token cap
        self._env = {
            **os.environ,
            "CLAUDE_CODE_MAX_OUTPUT_TOKENS": str(max_output_tokens),
        }
        if self.effort:
            self._env["CLAUDE_CODE_EFFORT_LEVEL"] = self.effort

    def interrupt(self):
        """Signal all active LLM calls to stop."""
        self._interrupted.set()
        self._kill_active_procs()

    def soft_interrupt(self):
        """Signal active LLM calls to stop and return partial output."""
        self._soft_interrupted.set()
        self._kill_active_procs()

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
        """Reset only the soft interrupt flag (before Phase 2 calls)."""
        self._soft_interrupted.clear()

    def _build_cmd(self, *, system_prompt: str, json_schema: dict | None,
                   web_search: bool, use_streaming: bool) -> list[str]:
        """Build a Claude CLI command for a single call."""
        cmd = [
            "claude", "-p",
            "--model", self.model,
            "--system-prompt", system_prompt,
        ]
        if self.effort:
            cmd.extend(["--effort", self.effort])

        if use_streaming:
            cmd.extend(["--output-format", "stream-json", "--verbose",
                         "--include-partial-messages"])
        else:
            cmd.extend(["--output-format", "json"])

        if web_search:
            cmd.extend(["--permission-mode", "bypassPermissions",
                         "--allowedTools", "WebSearch WebFetch"])
        elif self.mcp_config:
            cmd.extend(["--mcp-config", json.dumps(self.mcp_config),
                         "--strict-mcp-config",
                         "--permission-mode", "bypassPermissions",
                         "--allowedTools",
                         "mcp__lean_tools__lean_verify mcp__lean_tools__lean_search"])
        else:
            cmd.extend(["--tools", ""])
        if json_schema:
            cmd.extend(["--json-schema", json.dumps(json_schema)])
        return cmd

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
        max_tokens: int | None = None,  # overrides max_output_tokens for this call
        no_thinking: bool = False,      # disable extended thinking for this call
    ) -> dict:
        """Make an LLM call and archive it.

        Args:
            web_search: If True, enable WebSearch tool instead of disabling all tools.
            stream_callback: If provided, called with text chunks as they arrive.
                Signature: callback(text: str).
            tool_callback: If provided, called when MCP tool events are detected.
                Signature: tool_callback(name: str, input: dict, result: str, status: str, duration_ms: int).
            tool_start_callback: If provided, called when a tool use begins.
                Signature: tool_start_callback(name: str, input: dict).

        Returns dict with keys: result (str), cost (float), duration_ms (int),
        raw (full JSON response).
        """
        self.call_count += 1
        call_num = self.call_count

        # Archive input immediately so it can be inspected while LLM runs
        self._archive(call_num, label, prompt, system_prompt, json_schema,
                      None, None, 0, archive_path)

        use_streaming = bool(stream_callback)
        logger.info("[%s] calling %s%s", label, self.model,
                    " (streaming)" if use_streaming else "")

        if self._interrupted.is_set():
            elapsed_ms = 0
            self._archive(call_num, label, prompt, system_prompt, json_schema,
                          None, "interrupted", elapsed_ms, archive_path)
            logger.info("[%s] interrupted before call started", label)
            raise Interrupted()

        cmd = self._build_cmd(
            system_prompt=system_prompt,
            json_schema=json_schema,
            web_search=web_search,
            use_streaming=use_streaming,
        )

        env = self._env
        if max_tokens:
            env = {**self._env, "CLAUDE_CODE_MAX_OUTPUT_TOKENS": str(max_tokens)}
        if no_thinking:
            env = {**env,
                   "CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING": "1",
                   "MAX_THINKING_TOKENS": "0"}

        start = time.time()

        if use_streaming:
            return self._call_streaming(
                cmd, prompt, system_prompt, json_schema,
                call_num, label, start, stream_callback, archive_path,
                tool_callback=tool_callback,
                tool_start_callback=tool_start_callback,
                env=env,
            )

        proc = subprocess.Popen(
            cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, env=env,
            start_new_session=True,
        )
        with self._procs_lock:
            self._active_procs.append(proc)
        try:
            stdout, stderr = proc.communicate(input=prompt)
        finally:
            with self._procs_lock:
                if proc in self._active_procs:
                    self._active_procs.remove(proc)
        elapsed_ms = int((time.time() - start) * 1000)

        if proc.returncode != 0:
            self._archive(call_num, label, prompt, system_prompt, json_schema,
                          None, stderr, elapsed_ms, archive_path)
            if self._interrupted.is_set():
                logger.info("[%s] interrupted after %dms", label, elapsed_ms)
                raise Interrupted()
            raise RuntimeError(f"Claude CLI failed (exit {proc.returncode}): {stderr[:500]}")

        try:
            raw = json.loads(stdout)
        except json.JSONDecodeError:
            self._archive(call_num, label, prompt, system_prompt, json_schema,
                          None, stdout[:1000], elapsed_ms, archive_path)
            raise RuntimeError(f"Failed to parse Claude response as JSON: {stdout[:500]}")

        cost = raw.get("total_cost_usd", 0.0)
        self.total_cost += cost

        # Check for structured output failures
        subtype = raw.get("subtype", "")
        if "error" in subtype:
            # Token limit exceeded - return partial content with "length" finish
            err = raw.get("result", "") or subtype
            if "exceeded" in err and "token" in err:
                result_text = raw.get("result", "")
                duration = raw.get("duration_ms", elapsed_ms)
                self._archive(call_num, label, prompt, system_prompt,
                              json_schema, raw, None, elapsed_ms, archive_path,
                              result_text=result_text)
                logger.warning("[%s] output token limit hit after %dms",
                               label, elapsed_ms)
                return {
                    "result": result_text,
                    "thinking": "",
                    "cost": cost,
                    "duration_ms": duration,
                    "raw": raw,
                    "finish_reason": "length",
                }
            self._archive(call_num, label, prompt, system_prompt, json_schema,
                          raw, subtype, elapsed_ms, archive_path)
            raise RuntimeError(f"Claude CLI error: {subtype}")

        # When using --json-schema, structured output is in 'structured_output'
        if json_schema and "structured_output" in raw:
            result_text = json.dumps(raw["structured_output"])
        else:
            result_text = raw.get("result", "")

        duration = raw.get("duration_ms", elapsed_ms)
        self._archive(call_num, label, prompt, system_prompt, json_schema,
                      raw, None, elapsed_ms, archive_path,
                      result_text=result_text)
        logger.info("[%s] done %dms $%.4f", label, duration, cost)

        return {
            "result": result_text,
            "thinking": "",
            "cost": cost,
            "duration_ms": duration,
            "raw": raw,
            "finish_reason": raw.get("stop_reason", "end_turn"),
        }

    def _call_streaming(self, cmd, prompt, system_prompt, json_schema,
                        call_num, label, start, callback, archive_path=None,
                        tool_callback=None, tool_start_callback=None, env=None):
        """Stream text deltas to callback, return final result.

        Args:
            tool_callback: Optional callback for MCP tool events.
                Signature: tool_callback(tool_name: str, tool_input: dict,
                                         result: str, status: str, duration_ms: int)
            tool_start_callback: Optional callback when a tool use begins.
                Signature: tool_start_callback(tool_name: str, tool_input: dict)
        """
        proc = subprocess.Popen(
            cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, bufsize=1,
            env=env if env is not None else self._env,
            start_new_session=True,
        )
        with self._procs_lock:
            self._active_procs.append(proc)
        proc.stdin.write(prompt)
        proc.stdin.close()

        result_data = None
        thinking_parts = []
        result_parts = []
        interrupted = False
        soft_interrupted = False
        # Tool event tracking for MCP calls
        # Claude CLI streams tool_use as content blocks, then emits the
        # tool result as a top-level {"type": "user"} message.
        _in_tool_use = False
        _cur_tool_id = ""
        _cur_tool_name = ""
        _cur_tool_input_parts: list[str] = []
        _pending_tools: dict[str, dict] = {}  # tool_use_id -> {name, input}
        # Use readline() instead of iterator - the iterator uses an internal
        # read-ahead buffer that defeats real-time streaming.
        try:
            while True:
                if self._interrupted.is_set():
                    interrupted = True
                    proc.kill()
                    break
                if self._soft_interrupted.is_set():
                    soft_interrupted = True
                    proc.kill()
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

                msg_type = msg.get("type", "")

                if msg_type == "stream_event":
                    event = msg.get("event", {})
                    etype = event.get("type", "")

                    if etype == "content_block_start":
                        cb = event.get("content_block", {})
                        if cb.get("type") == "tool_use":
                            _in_tool_use = True
                            _cur_tool_id = cb.get("id", "")
                            _cur_tool_name = cb.get("name", "")
                            _cur_tool_input_parts = []

                    elif etype == "content_block_delta":
                        delta = event.get("delta", {})
                        dtype = delta.get("type", "")
                        if dtype == "input_json_delta" and _in_tool_use:
                            _cur_tool_input_parts.append(
                                delta.get("partial_json", ""))
                        else:
                            thinking = delta.get("thinking", "")
                            text = delta.get("text", "")
                            if thinking:
                                thinking_parts.append(thinking)
                                callback(thinking, "thinking")
                            elif text:
                                result_parts.append(text)
                                callback(text, "text")

                    elif etype == "content_block_stop":
                        if _in_tool_use:
                            _in_tool_use = False
                            try:
                                tool_input = json.loads(
                                    "".join(_cur_tool_input_parts))
                            except (json.JSONDecodeError, ValueError):
                                tool_input = {"raw": "".join(
                                    _cur_tool_input_parts)}
                            _pending_tools[_cur_tool_id] = {
                                "name": _cur_tool_name,
                                "input": tool_input,
                                "start_time": time.time(),
                            }
                            if tool_start_callback and _cur_tool_name.startswith("mcp__"):
                                parts = _cur_tool_name.split("__", 2)
                                tname = parts[-1] if len(parts) == 3 else _cur_tool_name
                                tool_start_callback(tname, tool_input)

                # Claude CLI emits tool results as {"type": "user"} messages
                elif msg_type == "user" and tool_callback:
                    # Extract tool_result from user message content
                    content = msg.get("message", {}).get("content", [])
                    if isinstance(content, list):
                        for item in content:
                            if not isinstance(item, dict):
                                continue
                            if item.get("type") != "tool_result":
                                continue
                            tid = item.get("tool_use_id", "")
                            tc = _pending_tools.pop(tid, None)
                            if not tc:
                                continue
                            # Skip non-MCP tools (e.g. ToolSearch)
                            name = tc["name"]
                            if not name.startswith("mcp__"):
                                continue
                            # Strip MCP prefix (mcp__server__tool → tool)
                            parts = name.split("__", 2)
                            name = parts[-1] if len(parts) == 3 else name
                            # Extract result text
                            raw_content = item.get("content", "")
                            try:
                                parsed = json.loads(raw_content)
                                result_text = str(parsed.get(
                                    "result", raw_content))
                            except (json.JSONDecodeError, ValueError,
                                    AttributeError):
                                result_text = raw_content
                            is_error = item.get("is_error", False)
                            # Infer status for lean tools
                            if is_error:
                                status = "error"
                            elif name == "lean_verify":
                                if "OK" in result_text.split('\n', 1)[0] or result_text.startswith("OK"):
                                    status = "ok"
                                elif re.search(r"^\d+:\d+: error", result_text, re.MULTILINE):
                                    status = "error"
                                elif "sorry" in result_text.lower():
                                    status = "partial"
                                else:
                                    status = "ok"
                            elif name == "lean_store":
                                status = "ok" if result_text.startswith("OK") else "error"
                            else:
                                status = "ok"
                            duration_ms = int(
                                (time.time() - tc.get("start_time", time.time())) * 1000)
                            tool_callback(
                                name, tc["input"], result_text, status,
                                duration_ms)

                elif msg_type == "result":
                    result_data = msg
        finally:
            with self._procs_lock:
                if proc in self._active_procs:
                    self._active_procs.remove(proc)
            proc.wait()

        elapsed_ms = int((time.time() - start) * 1000)

        # Catch race: flags set while readline() was blocked.
        # _soft_interrupted may have been cleared by a sibling worker thread that
        # already reached Phase 2, so also treat a signal-killed process with no
        # result as a soft interrupt (negative returncode = killed by SIGKILL).
        if not soft_interrupted and not interrupted:
            if self._soft_interrupted.is_set():
                soft_interrupted = True
            elif self._interrupted.is_set():
                interrupted = True
            elif result_data is None and proc.returncode is not None and proc.returncode < 0:
                soft_interrupted = True

        if soft_interrupted:
            partial_text = "".join(result_parts)
            thinking_text = "".join(thinking_parts)
            self._archive(call_num, label, prompt, system_prompt, json_schema,
                          None, "soft_interrupted", elapsed_ms, archive_path,
                          thinking=thinking_text, result_text=partial_text)
            logger.info("[%s] soft-interrupted after %dms", label, elapsed_ms)
            return {
                "result": partial_text,
                "thinking": thinking_text,
                "cost": 0.0,
                "duration_ms": elapsed_ms,
                "raw": {},
                "finish_reason": "soft_interrupted",
            }

        if interrupted:
            self._archive(call_num, label, prompt, system_prompt, json_schema,
                          None, "interrupted", elapsed_ms, archive_path)
            logger.info("[%s] interrupted after %dms", label, elapsed_ms)
            raise Interrupted()

        if result_data is None:
            stderr = proc.stderr.read()
            self._archive(call_num, label, prompt, system_prompt, json_schema,
                          None, stderr, elapsed_ms, archive_path)
            raise RuntimeError(f"No result from streaming call: {stderr[:500]}")

        subtype = result_data.get("subtype", "")
        if result_data.get("is_error") or "error" in subtype:
            err = result_data.get("result", "") or subtype or "streaming error"
            # Token limit exceeded - return partial streamed content instead of crashing
            if "exceeded" in err and "token" in err and result_parts:
                partial_text = "".join(result_parts)
                thinking_text = "".join(thinking_parts)
                cost = result_data.get("total_cost_usd", 0.0)
                self.total_cost += cost
                self._archive(call_num, label, prompt, system_prompt,
                              json_schema, result_data, None, elapsed_ms,
                              archive_path, thinking=thinking_text,
                              result_text=partial_text)
                logger.warning("[%s] output token limit hit after %dms, "
                               "returning partial output (%d chars)",
                               label, elapsed_ms, len(partial_text))
                return {
                    "result": partial_text,
                    "thinking": thinking_text,
                    "cost": cost,
                    "duration_ms": elapsed_ms,
                    "raw": result_data,
                    "finish_reason": "length",
                }
            self._archive(call_num, label, prompt, system_prompt, json_schema,
                          result_data, err, elapsed_ms, archive_path)
            raise RuntimeError(f"Claude CLI streaming error: {err[:500]}")

        cost = result_data.get("total_cost_usd", 0.0)
        self.total_cost += cost
        if json_schema and "structured_output" in result_data:
            result_text = json.dumps(result_data["structured_output"])
        else:
            result_text = result_data.get("result", "")

        thinking_text = "".join(thinking_parts)
        duration = result_data.get("duration_ms", elapsed_ms)
        self._archive(call_num, label, prompt, system_prompt, json_schema,
                      result_data, None, elapsed_ms, archive_path,
                      thinking=thinking_text, result_text=result_text)
        logger.info("[%s] done %dms $%.4f", label, duration, cost)

        return {
            "result": result_text,
            "thinking": thinking_text,
            "cost": cost,
            "duration_ms": duration,
            "raw": result_data,
            "finish_reason": result_data.get("stop_reason", "end_turn"),
        }

    def _archive(self, call_num, label, prompt, system_prompt, json_schema,
                 response, error, elapsed_ms, archive_path=None,
                 *, thinking="", result_text=""):
        archive(self.model, self.archive_dir, call_num, label, prompt,
                system_prompt, json_schema, response, error, elapsed_ms,
                archive_path, thinking=thinking, result_text=result_text)
