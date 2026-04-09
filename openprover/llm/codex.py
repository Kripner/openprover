"""Codex app-server client for OpenProver."""

import json
import logging
import os
import random
import re
import select
import subprocess
import threading
import time
from pathlib import Path

from ._base import Interrupted, QuotaExceeded, archive, is_quota_exceeded_error

logger = logging.getLogger("openprover.llm")


_FALLBACK_CONTEXT_LENGTH = 200_000
_GPT5_CONTEXT_LENGTH = 400_000


def _infer_context_length(model: str) -> int:
    """Infer a context window from the explicit Codex model id when known."""
    if model and model.lower().startswith("gpt-5"):
        return _GPT5_CONTEXT_LENGTH
    return _FALLBACK_CONTEXT_LENGTH


class CodexClient:
    """Calls Codex via the app-server and archives interactions."""

    provider = "codex"
    context_length = _FALLBACK_CONTEXT_LENGTH
    supports_mcp_tools = True

    def __init__(self, model: str, archive_dir: Path,
                 max_output_tokens: int = 128_000,
                 answer_reserve: int = 4096,
                 reasoning_effort: str | None = None,
                 requested_model: str | None = None):
        self.model = model
        self.requested_model = requested_model or model
        self.archive_dir = archive_dir
        self.call_count = 0
        self.total_cost = 0.0
        self.max_output_tokens = max_output_tokens
        self.answer_reserve = answer_reserve
        self.reasoning_effort = reasoning_effort or "high"
        self.context_length = _infer_context_length(model)
        self.mcp_config: dict | None = None

        self._requested_model = model
        self._interrupted = threading.Event()
        self._soft_interrupted = threading.Event()
        self._proc: subprocess.Popen | None = None
        self._io_lock = threading.Lock()
        self._call_lock = threading.Lock()
        self._request_id = 0
        self._ignored_response_ids: set[int] = set()
        self._pending_messages: list[dict] = []
        self._stdout_buffer = ""
        self._active_thread_id: str | None = None
        self._active_turn_id: str | None = None
        self._stderr_lines: list[str] = []
        self._stderr_thread: threading.Thread | None = None

        self._start_server()

    @staticmethod
    def _app_server_cmd() -> list[str]:
        """Build the Codex app-server command for current CLI releases."""
        return [
            "codex",
            "app-server",
            "--listen",
            "stdio://",
        ]

    def interrupt(self):
        """Signal the active LLM call to stop."""
        self._interrupted.set()
        self._send_turn_interrupt()

    def soft_interrupt(self):
        """Signal the active LLM call to stop and return partial output."""
        self._soft_interrupted.set()
        self._send_turn_interrupt()

    def cleanup(self):
        """Stop the Codex app-server process if it is running."""
        proc = self._proc
        if proc is None:
            return
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
        self._proc = None

    def clear_interrupt(self):
        """Reset interrupt flags so new calls can proceed."""
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
        max_tokens: int | None = None,
    ) -> dict:
        """Make a Codex call via app-server and archive it."""
        del json_schema
        del max_tokens

        with self._call_lock:
            self.call_count += 1
            call_num = self.call_count
            self._archive(
                call_num,
                label,
                prompt,
                system_prompt,
                None,
                None,
                None,
                0,
                archive_path,
            )

            if self._interrupted.is_set():
                self._archive(
                    call_num,
                    label,
                    prompt,
                    system_prompt,
                    None,
                    None,
                    "interrupted",
                    0,
                    archive_path,
                )
                raise Interrupted()

            self._ensure_server()
            start = time.time()
            try:
                thread_start_params = {
                    "model": self.model,
                    "ephemeral": True,
                    "approvalPolicy": "never",
                    "developerInstructions": system_prompt,
                }
                if web_search:
                    thread_start_params["config"] = {"web_search": "live"}
                elif self.mcp_config is not None:
                    thread_start_params["config"] = self.mcp_config

                thread_resp = self._rpc_request("thread/start", thread_start_params)
                thread_id = thread_resp.get("thread", {}).get("id")
                if not thread_id:
                    raise RuntimeError(
                        "Codex app-server thread/start missing thread id"
                    )
                self._active_thread_id = thread_id

                turn_resp = self._rpc_request(
                    "turn/start",
                    {
                        "threadId": thread_id,
                        "input": [{"type": "text", "text": prompt}],
                        "approvalPolicy": "never",
                        "effort": self.reasoning_effort,
                    },
                )
                turn_id = turn_resp.get("turn", {}).get("id")
                if not turn_id:
                    raise RuntimeError("Codex app-server turn/start missing turn id")
                self._active_turn_id = turn_id

                turn_completed, streamed = self._wait_for_turn_completed(
                    turn_id,
                    stream_callback=stream_callback,
                    tool_callback=tool_callback,
                    tool_start_callback=tool_start_callback,
                )
                elapsed_ms = int((time.time() - start) * 1000)

                status = turn_completed.get("turn", {}).get("status")
                finish_reason = "stop"
                hard_interrupted = self._interrupted.is_set() or (
                    status == "interrupted" and not self._soft_interrupted.is_set()
                )
                soft_interrupted = (
                    self._soft_interrupted.is_set()
                    and not self._interrupted.is_set()
                    and status == "interrupted"
                )

                if soft_interrupted:
                    finish_reason = "soft_interrupted"

                if hard_interrupted and not soft_interrupted:
                    self._archive(
                        call_num,
                        label,
                        prompt,
                        system_prompt,
                        None,
                        None,
                        "interrupted",
                        elapsed_ms,
                        archive_path,
                    )
                    raise Interrupted()

                raw = {
                    "thread_start": thread_resp,
                    "turn_start": turn_resp,
                    "turn_completed": turn_completed,
                    "stop_reason": finish_reason,
                    "usage": {},
                    "total_cost_usd": 0.0,
                }

                result_text, thinking_text = self._extract_turn_outputs(turn_completed)
                streamed_result = "".join(streamed["result_parts"]).strip()
                streamed_thinking = "".join(streamed["thinking_parts"]).strip()
                if not result_text and streamed_result:
                    result_text = streamed_result
                if not thinking_text and streamed_thinking:
                    thinking_text = streamed_thinking

                self._archive(
                    call_num,
                    label,
                    prompt,
                    system_prompt,
                    None,
                    raw,
                    None,
                    elapsed_ms,
                    archive_path,
                    thinking=thinking_text,
                    result_text=result_text,
                )

                return {
                    "result": result_text,
                    "thinking": thinking_text,
                    "cost": 0.0,
                    "duration_ms": elapsed_ms,
                    "raw": raw,
                    "finish_reason": finish_reason,
                }
            except Interrupted:
                raise
            except Exception as e:
                elapsed_ms = int((time.time() - start) * 1000)
                err = str(e)
                self._archive(
                    call_num,
                    label,
                    prompt,
                    system_prompt,
                    None,
                    None,
                    err,
                    elapsed_ms,
                    archive_path,
                )
                if is_quota_exceeded_error(err):
                    raise QuotaExceeded(err[:1000])
                self._active_turn_id = None
                self._active_thread_id = None
                raise
            finally:
                self._active_turn_id = None
                self._active_thread_id = None

    def _start_server(self):
        self.cleanup()
        cmd = self._app_server_cmd()
        self._proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        self._pending_messages.clear()
        self._ignored_response_ids.clear()
        self._stdout_buffer = ""
        self._stderr_lines = []
        self._stderr_thread = threading.Thread(target=self._drain_stderr, daemon=True)
        self._stderr_thread.start()

        init_resp = self._rpc_request(
            "initialize",
            {
                "clientInfo": {
                    "name": "openprover_codex",
                    "title": "OpenProver Codex Client",
                    "version": "0.1.0",
                }
            },
        )
        logger.debug("codex initialize ok: %s", bool(init_resp))
        self._send_notification("initialized")

        model_resp = self._rpc_request("model/list", {"includeHidden": False})
        model_entries = self._extract_model_entries(model_resp)
        if self.model not in self._extract_model_ids(model_resp):
            raise RuntimeError(
                f"Codex app-server model/list does not include required model {self.model!r}"
            )
        model_entry = model_entries.get(self.model)
        has_reasoning_metadata = self._model_has_reasoning_metadata(model_entry)
        # Older app-server catalogs may omit reasoning metadata entirely.
        if has_reasoning_metadata and not self._model_supports_reasoning(model_entry):
            raise RuntimeError(
                "Codex app-server model/list includes required model "
                f"{self.model!r} but does not report reasoning support/effort capability"
            )

    def _ensure_server(self):
        if self._proc is None or self._proc.poll() is not None:
            self._start_server()

    def _drain_stderr(self):
        proc = self._proc
        if proc is None or proc.stderr is None:
            return
        for line in proc.stderr:
            self._stderr_lines.append(line.rstrip("\n"))
            if len(self._stderr_lines) > 200:
                self._stderr_lines = self._stderr_lines[-200:]

    def _next_request_id(self) -> int:
        self._request_id += 1
        return self._request_id

    def _send_notification(self, method: str, params: dict | None = None):
        payload: dict[str, object] = {"method": method}
        if params is not None:
            payload["params"] = params
        self._write_json(payload)

    def _send_request_async(self, method: str, params: dict) -> int:
        req_id = self._next_request_id()
        payload = {"method": method, "id": req_id, "params": params}
        self._write_json(payload)
        self._ignored_response_ids.add(req_id)
        return req_id

    def _rpc_request(self, method: str, params: dict) -> dict:
        max_overload_retries = 5
        base_backoff_s = 0.2
        max_backoff_s = 3.0

        for attempt in range(max_overload_retries + 1):
            req_id = self._next_request_id()
            payload = {"method": method, "id": req_id, "params": params}
            self._write_json(payload)

            while True:
                msg = self._read_message(timeout_s=60, include_pending=False)

                if self._handle_server_request(msg):
                    continue

                msg_id = msg.get("id")
                if msg_id is None:
                    self._pending_messages.append(msg)
                    continue
                if msg_id in self._ignored_response_ids:
                    self._ignored_response_ids.discard(msg_id)
                    continue
                if msg_id != req_id:
                    continue
                if "error" in msg:
                    err = msg["error"]
                    if self._is_overload_error(err) and attempt < max_overload_retries:
                        backoff = min(max_backoff_s, base_backoff_s * (2**attempt))
                        jitter = random.uniform(0.0, backoff * 0.25)
                        sleep_s = backoff + jitter
                        logger.warning(
                            "Codex app-server overloaded during %s; retry %d/%d in %.2fs",
                            method,
                            attempt + 1,
                            max_overload_retries,
                            sleep_s,
                        )
                        time.sleep(sleep_s)
                        break
                    raise RuntimeError(self._format_rpc_error(method, err))
                return msg.get("result", {})

        raise RuntimeError(f"Codex app-server {method} failed after retries")

    def _read_message(self, timeout_s: float, *, include_pending: bool = True) -> dict:
        if include_pending and self._pending_messages:
            return self._pending_messages.pop(0)

        return self._read_transport_message(timeout_s=timeout_s)

    def _read_transport_message(self, timeout_s: float) -> dict:

        proc = self._proc
        if proc is None or proc.stdout is None:
            raise RuntimeError("Codex app-server is not running")

        deadline = time.time() + timeout_s
        stdout_fd = proc.stdout.fileno()

        while True:
            while "\n" in self._stdout_buffer:
                line, self._stdout_buffer = self._stdout_buffer.split("\n", 1)
                line = line.strip()
                if not line:
                    continue
                try:
                    return json.loads(line)
                except json.JSONDecodeError:
                    logger.debug("Ignoring non-JSON app-server line: %s", line)

            if proc.poll() is not None:
                stderr = "\n".join(self._stderr_lines[-20:])
                raise RuntimeError(
                    f"Codex app-server exited with code {proc.returncode}. {stderr}"
                )
            remaining = deadline - time.time()
            if remaining <= 0:
                raise RuntimeError("Timed out waiting for Codex app-server message")

            readable, _, _ = select.select([stdout_fd], [], [], remaining)
            if not readable:
                continue
            chunk = os.read(stdout_fd, 4096)
            if not chunk:
                time.sleep(0.01)
                continue
            self._stdout_buffer += chunk.decode("utf-8", errors="replace")

    def _wait_for_turn_completed(
        self,
        turn_id: str | None,
        *,
        stream_callback=None,
        tool_callback=None,
        tool_start_callback=None,
    ) -> tuple[dict, dict]:
        interrupt_sent = False
        deadline = time.time() + 600
        stream_state = {
            "result_parts": [],
            "thinking_parts": [],
            "agent_text_by_item": {},
            "reasoning_emitted_ids": set(),
            "reasoning_content_delta_ids": set(),
            "reasoning_summary_parts": {},
            "reasoning_summary_buffers": {},
            "pending_tools": {},
        }
        while True:
            if (
                self._interrupted.is_set() or self._soft_interrupted.is_set()
            ) and not interrupt_sent:
                self._send_turn_interrupt()
                interrupt_sent = True

            remaining = max(deadline - time.time(), 0.1)
            msg = self._read_message(timeout_s=remaining)

            if self._handle_server_request(msg):
                continue

            msg_id = msg.get("id")
            if msg_id is not None:
                if msg_id in self._ignored_response_ids:
                    self._ignored_response_ids.discard(msg_id)
                continue

            completed = self._process_stream_notification(
                msg,
                turn_id=turn_id,
                stream_callback=stream_callback,
                tool_callback=tool_callback,
                tool_start_callback=tool_start_callback,
                stream_state=stream_state,
            )
            if completed is not None:
                return completed, stream_state

            if msg.get("method") != "turn/completed":
                continue

            params = msg.get("params", {})
            completed_turn_id = params.get("turn", {}).get("id")
            if turn_id and completed_turn_id and completed_turn_id != turn_id:
                continue
            return params, stream_state

    def _send_turn_interrupt(self):
        turn_id = self._active_turn_id
        if not turn_id:
            return
        params = {"turnId": turn_id}
        thread_id = self._active_thread_id
        if thread_id:
            params["threadId"] = thread_id
        try:
            self._send_request_async("turn/interrupt", params)
        except RuntimeError:
            return

    def _write_json(self, payload: dict):
        proc = self._proc
        if proc is None or proc.stdin is None:
            raise RuntimeError("Codex app-server is not running")
        with self._io_lock:
            proc.stdin.write(json.dumps(payload) + "\n")
            proc.stdin.flush()

    def _send_error_response(self, req_id: int, code: int, message: str):
        self._write_json({"id": req_id, "error": {"code": code, "message": message}})

    def _handle_server_request(self, msg: dict) -> bool:
        req_id = msg.get("id")
        method = msg.get("method")
        if req_id is None or not isinstance(method, str):
            return False

        if self._is_approval_request_method(method):
            self._send_error_response(
                req_id,
                -32000,
                "Approvals are disabled in this integration",
            )
            raise RuntimeError(
                f"Codex app-server requested approval via {method!r} even though approvalPolicy is 'never'"
            )

        if method == "tool/requestUserInput":
            self._send_error_response(
                req_id,
                -32000,
                "Interactive user input is unsupported in this integration",
            )
            raise RuntimeError(
                "Codex app-server requested interactive user input unexpectedly"
            )

        self._send_error_response(
            req_id,
            -32601,
            f"Unsupported server request method: {method}",
        )
        raise RuntimeError(
            f"Codex app-server sent unsupported server request {method!r}"
        )

    @staticmethod
    def _is_approval_request_method(method: str) -> bool:
        lowered = method.lower()
        return (
            "requestapproval" in lowered
            or lowered == "item/permissions/requestapproval"
            or lowered == "item/commandexecution/requestapproval"
            or lowered == "item/filechange/requestapproval"
        )

    @staticmethod
    def _is_overload_error(err: dict) -> bool:
        code = err.get("code") if isinstance(err, dict) else None
        msg = err.get("message", "") if isinstance(err, dict) else ""
        return code == -32001 and "overload" in str(msg).lower()

    @classmethod
    def _format_rpc_error(cls, method: str, err: dict) -> str:
        message = str(err.get("message", err)) if isinstance(err, dict) else str(err)
        code = err.get("code") if isinstance(err, dict) else None
        lowered = message.lower()

        if code == -32001:
            return f"Codex app-server {method} failed after overload retries: {message}"
        if "auth" in lowered or "unauthor" in lowered or "forbidden" in lowered:
            return f"Codex app-server authentication failed during {method}: {message}"
        if (
            method in ("thread/start", "thread/resume")
            and "mcp" in lowered
            and (
                "required" in lowered or "initialize" in lowered or "failed" in lowered
            )
        ):
            return (
                "Codex app-server failed to start/resume thread because a required MCP "
                f"server failed to initialize: {message}"
            )
        if "approval" in lowered:
            return (
                "Codex app-server requested approval unexpectedly while approvalPolicy="
                f"'never': {message}"
            )
        if method in ("initialize", "model/list", "thread/start", "turn/start"):
            return f"Codex app-server startup failed during {method}: {message}"
        return f"Codex app-server {method} failed: {message}"

    @staticmethod
    def _normalize_tool_name(name: str) -> str:
        normalized = name.strip()
        if normalized.startswith("mcp__"):
            parts = normalized.split("__", 2)
            if len(parts) == 3 and parts[-1]:
                return parts[-1]
        return normalized

    @staticmethod
    def _parse_tool_args(raw_args) -> dict:
        if isinstance(raw_args, dict):
            return raw_args
        if isinstance(raw_args, str):
            stripped = raw_args.strip()
            if not stripped:
                return {}
            try:
                parsed = json.loads(stripped)
                if isinstance(parsed, dict):
                    return parsed
                return {"value": parsed}
            except json.JSONDecodeError:
                return {"raw": raw_args}
        if raw_args is None:
            return {}
        return {"value": raw_args}

    @staticmethod
    def _extract_tool_name(item: dict) -> str:
        for key in ("name", "toolName", "tool", "tool_name"):
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        call = item.get("call")
        if isinstance(call, dict):
            for key in ("name", "toolName"):
                value = call.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()
        return ""

    @classmethod
    def _extract_tool_args(cls, item: dict) -> dict:
        for key in ("input", "args", "arguments", "toolInput", "tool_input"):
            if key in item:
                return cls._parse_tool_args(item.get(key))
        call = item.get("call")
        if isinstance(call, dict):
            for key in ("input", "args", "arguments"):
                if key in call:
                    return cls._parse_tool_args(call.get(key))
        return {}

    @classmethod
    def _is_mcp_tool_item(cls, item: dict, raw_name: str) -> bool:
        if raw_name.startswith("mcp__"):
            return True
        item_type = item.get("type")
        return isinstance(item_type, str) and "mcp" in item_type.lower()

    @classmethod
    def _extract_tool_result_text(cls, item: dict) -> str:
        for key in ("result", "output", "response", "content", "text"):
            if key in item:
                value = item.get(key)
                if isinstance(value, dict):
                    nested = value.get("result", value.get("content", value))
                    text = cls._collect_text(nested)
                else:
                    text = cls._collect_text(value)
                if text:
                    return text
        call = item.get("call")
        if isinstance(call, dict):
            for key in ("result", "output", "response", "content"):
                if key in call:
                    text = cls._collect_text(call.get(key))
                    if text:
                        return text
        return ""

    @classmethod
    def _infer_tool_status(
        cls,
        name: str,
        result_text: str,
        *,
        is_error: bool,
        raw_status,
    ) -> str:
        status_map = {
            "ok": "ok",
            "success": "ok",
            "completed": "ok",
            "partial": "partial",
            "running": "running",
            "in_progress": "running",
            "pending": "running",
            "error": "error",
            "failed": "error",
        }
        if isinstance(raw_status, str):
            mapped = status_map.get(raw_status.strip().lower())
            if mapped:
                return mapped

        if is_error:
            return "error"

        if name == "lean_verify":
            first_line = result_text.split("\n", 1)[0] if result_text else ""
            if first_line.startswith("OK"):
                return "ok"
            if re.search(r"^\d+:\d+: error", result_text, re.MULTILINE):
                return "error"
            if "sorry" in result_text.lower():
                return "partial"
            return "ok"

        return "ok"

    @classmethod
    def _maybe_emit_tool_start(
        cls,
        item: dict,
        *,
        stream_state: dict,
        tool_start_callback,
    ) -> bool:
        item_id = item.get("id")
        if not isinstance(item_id, str) or not item_id:
            return False

        raw_name = cls._extract_tool_name(item)
        if not raw_name or not cls._is_mcp_tool_item(item, raw_name):
            return False

        name = cls._normalize_tool_name(raw_name)
        args = cls._extract_tool_args(item)
        start_entry = stream_state["pending_tools"].setdefault(
            item_id,
            {
                "name": name,
                "args": args,
                "started_at": time.time(),
                "start_emitted": False,
                "is_mcp": True,
            },
        )
        start_entry["name"] = name
        start_entry["args"] = args
        start_entry["is_mcp"] = True
        if callable(tool_start_callback) and not start_entry["start_emitted"]:
            tool_start_callback(name, args)
            start_entry["start_emitted"] = True
        return True

    @classmethod
    def _maybe_emit_tool_completed(
        cls,
        item: dict,
        *,
        stream_state: dict,
        tool_callback,
        tool_start_callback,
    ) -> bool:
        item_id = item.get("id")
        if not isinstance(item_id, str) or not item_id:
            return False

        raw_name = cls._extract_tool_name(item)
        pending = stream_state["pending_tools"].pop(item_id, None)
        pending_is_mcp = bool(pending and pending.get("is_mcp"))

        if not raw_name and pending:
            raw_name = pending.get("name", "")
        if not raw_name:
            return False
        if not (pending_is_mcp or cls._is_mcp_tool_item(item, raw_name)):
            return False

        name = cls._normalize_tool_name(raw_name)
        args = cls._extract_tool_args(item)
        if not args and pending:
            args = pending.get("args", {})

        started_at = time.time()
        start_emitted = False
        if pending:
            started_at = pending.get("started_at", started_at)
            start_emitted = bool(pending.get("start_emitted", False))

        if callable(tool_start_callback) and not start_emitted:
            tool_start_callback(name, args)
            start_emitted = True

        result_text = cls._extract_tool_result_text(item)
        is_error = bool(
            item.get("is_error") or item.get("isError") or item.get("error")
        )
        status = cls._infer_tool_status(
            name,
            result_text,
            is_error=is_error,
            raw_status=item.get("status"),
        )
        duration_ms = max(0, int((time.time() - started_at) * 1000))
        if callable(tool_callback):
            tool_callback(name, args, result_text, status, duration_ms)
        return True

    @staticmethod
    def _collect_text(value) -> str:
        if isinstance(value, str):
            return value.strip()
        if isinstance(value, list):
            parts = []
            for item in value:
                if isinstance(item, str) and item.strip():
                    parts.append(item.strip())
                    continue
                if isinstance(item, dict):
                    text = item.get("text")
                    if isinstance(text, str) and text.strip():
                        parts.append(text.strip())
            return "\n".join(parts).strip()
        return ""

    @classmethod
    def _extract_reasoning_text(cls, item: dict) -> str:
        content_text = cls._collect_text(item.get("content"))
        if content_text:
            return content_text
        return cls._collect_text(item.get("summary"))

    @classmethod
    def _process_stream_notification(
        cls,
        msg: dict,
        *,
        turn_id: str | None,
        stream_callback,
        tool_callback,
        tool_start_callback,
        stream_state: dict,
    ) -> dict | None:
        method = msg.get("method")
        if not isinstance(method, str):
            return None

        params = msg.get("params", {})
        if not isinstance(params, dict):
            return None

        msg_turn_id = params.get("turnId")
        if turn_id and isinstance(msg_turn_id, str) and msg_turn_id != turn_id:
            return None

        if method == "item/agentMessage/delta":
            delta = params.get("delta")
            item_id = params.get("itemId")
            if isinstance(delta, str) and delta:
                if callable(stream_callback):
                    stream_callback(delta, "text")
                stream_state["result_parts"].append(delta)
                if isinstance(item_id, str) and item_id:
                    current = stream_state["agent_text_by_item"].get(item_id, "")
                    stream_state["agent_text_by_item"][item_id] = current + delta
            return None

        if method == "item/reasoning/textDelta":
            delta = params.get("delta")
            item_id = params.get("itemId")
            if isinstance(delta, str) and delta:
                if callable(stream_callback):
                    stream_callback(delta, "thinking")
                stream_state["thinking_parts"].append(delta)
                if isinstance(item_id, str) and item_id:
                    stream_state["reasoning_emitted_ids"].add(item_id)
                    stream_state["reasoning_content_delta_ids"].add(item_id)
            return None

        if method == "item/reasoning/summaryPartAdded":
            item_id = params.get("itemId")
            summary_index = params.get("summaryIndex")
            if isinstance(item_id, str) and item_id and isinstance(summary_index, int):
                summary_parts = stream_state["reasoning_summary_parts"].setdefault(
                    item_id, set()
                )
                summary_parts.add(summary_index)
            return None

        if method == "item/reasoning/summaryTextDelta":
            delta = params.get("delta")
            item_id = params.get("itemId")
            summary_index = params.get("summaryIndex")
            if not (isinstance(delta, str) and delta):
                return None
            if not (isinstance(item_id, str) and item_id):
                return None
            if isinstance(summary_index, int):
                summary_parts = stream_state["reasoning_summary_parts"].setdefault(
                    item_id, set()
                )
                summary_parts.add(summary_index)
            summary_buffer = stream_state["reasoning_summary_buffers"].setdefault(
                item_id, []
            )
            summary_buffer.append(delta)
            return None

        if method == "item/completed":
            item = params.get("item")
            if not isinstance(item, dict):
                return None

            if cls._maybe_emit_tool_completed(
                item,
                stream_state=stream_state,
                tool_callback=tool_callback,
                tool_start_callback=tool_start_callback,
            ):
                return None

            item_type = item.get("type")
            item_id = item.get("id")

            if item_type == "agentMessage":
                final_text = cls._collect_text(item.get("text"))
                if not final_text:
                    return None
                streamed_text = ""
                if isinstance(item_id, str):
                    streamed_text = stream_state["agent_text_by_item"].get(item_id, "")
                missing = ""
                if streamed_text and final_text.startswith(streamed_text):
                    missing = final_text[len(streamed_text) :]
                elif not streamed_text:
                    missing = final_text
                elif final_text != streamed_text:
                    missing = final_text
                if missing:
                    if callable(stream_callback):
                        stream_callback(missing, "text")
                    stream_state["result_parts"].append(missing)
                    if isinstance(item_id, str) and item_id:
                        stream_state["agent_text_by_item"][item_id] = (
                            streamed_text + missing
                        )
                return None

            if item_type == "reasoning":
                item_key = item_id if isinstance(item_id, str) else ""
                if item_key and item_key in stream_state["reasoning_content_delta_ids"]:
                    stream_state["reasoning_summary_buffers"].pop(item_key, None)
                reasoning_text = ""
                if (
                    item_key
                    and item_key not in stream_state["reasoning_content_delta_ids"]
                ):
                    reasoning_text = "".join(
                        stream_state["reasoning_summary_buffers"].pop(item_key, [])
                    ).strip()
                if not reasoning_text:
                    reasoning_text = cls._extract_reasoning_text(item)
                if not reasoning_text:
                    return None
                if item_key and item_key in stream_state["reasoning_emitted_ids"]:
                    return None
                if callable(stream_callback):
                    # Emit completed-item reasoning only when no stable live
                    # reasoning deltas were emitted for this item.
                    stream_callback(reasoning_text, "thinking")
                stream_state["thinking_parts"].append(reasoning_text)
                if item_key:
                    stream_state["reasoning_emitted_ids"].add(item_key)
                return None

            return None

        if method == "item/started":
            item = params.get("item")
            if not isinstance(item, dict):
                return None
            cls._maybe_emit_tool_start(
                item,
                stream_state=stream_state,
                tool_start_callback=tool_start_callback,
            )
            return None

        if method == "turn/completed":
            for item_key, parts in list(
                stream_state["reasoning_summary_buffers"].items()
            ):
                if item_key in stream_state["reasoning_content_delta_ids"]:
                    continue
                if item_key in stream_state["reasoning_emitted_ids"]:
                    continue
                summary_text = "".join(parts).strip()
                if not summary_text:
                    continue
                if callable(stream_callback):
                    stream_callback(summary_text, "thinking")
                stream_state["thinking_parts"].append(summary_text)
                stream_state["reasoning_emitted_ids"].add(item_key)
            completed_turn_id = params.get("turn", {}).get("id")
            if turn_id and completed_turn_id and completed_turn_id != turn_id:
                return None
            return params

        return None

    @staticmethod
    def _extract_model_ids(model_list_result: dict) -> set[str]:
        out = set()
        for item in model_list_result.get("data", []):
            if isinstance(item, dict):
                model_id = item.get("id") or item.get("model")
                if isinstance(model_id, str) and model_id:
                    out.add(model_id)
        return out

    @staticmethod
    def _extract_model_entries(model_list_result: dict) -> dict[str, dict]:
        out: dict[str, dict] = {}
        for item in model_list_result.get("data", []):
            if not isinstance(item, dict):
                continue
            model_id = item.get("id") or item.get("model")
            if isinstance(model_id, str) and model_id:
                out[model_id] = item
        return out

    @staticmethod
    def _model_supports_reasoning(model_entry: dict | None) -> bool:
        if not isinstance(model_entry, dict):
            return False
        caps = model_entry.get("capabilities")
        if isinstance(caps, dict):
            for key in (
                "reasoning",
                "reasoningEffort",
                "supportsReasoning",
                "supports_reasoning",
                "effort",
            ):
                value = caps.get(key)
                if value:
                    return True
        for key in (
            "reasoning",
            "reasoningEffort",
            "supportsReasoning",
            "supports_reasoning",
            "effort",
            "supportedEfforts",
            "reasoningEfforts",
        ):
            value = model_entry.get(key)
            if value:
                return True
        return False

    @staticmethod
    def _model_has_reasoning_metadata(model_entry: dict | None) -> bool:
        if not isinstance(model_entry, dict):
            return False
        caps = model_entry.get("capabilities")
        if isinstance(caps, dict):
            for key in (
                "reasoning",
                "reasoningEffort",
                "supportsReasoning",
                "supports_reasoning",
                "effort",
            ):
                if key in caps:
                    return True
        for key in (
            "reasoning",
            "reasoningEffort",
            "supportsReasoning",
            "supports_reasoning",
            "effort",
            "supportedEfforts",
            "reasoningEfforts",
        ):
            if key in model_entry:
                return True
        return False

    @staticmethod
    def _extract_turn_outputs(turn_completed_params: dict) -> tuple[str, str]:
        result_parts = []
        thinking_parts = []
        items = turn_completed_params.get("turn", {}).get("items", [])
        if not isinstance(items, list):
            return "", ""

        for item in items:
            if not isinstance(item, dict):
                continue

            item_type = item.get("type")
            if item_type == "agentMessage":
                text = CodexClient._collect_text(item.get("text"))
                if text:
                    result_parts.append(text)
                continue

            if item_type == "reasoning":
                reasoning_text = CodexClient._extract_reasoning_text(item)
                if reasoning_text:
                    thinking_parts.append(reasoning_text)

        return "\n\n".join(result_parts).strip(), "\n\n".join(thinking_parts).strip()

    def _archive(
        self,
        call_num,
        label,
        prompt,
        system_prompt,
        json_schema,
        response,
        error,
        elapsed_ms,
        archive_path=None,
        *,
        thinking="",
        result_text="",
    ):
        archive(
            self.model,
            self.archive_dir,
            call_num,
            label,
            prompt,
            system_prompt,
            json_schema,
            response,
            error,
            elapsed_ms,
            archive_path,
            thinking=thinking,
            result_text=result_text,
            provider=self.provider,
            requested_model=self.requested_model,
            reasoning_effort=self.reasoning_effort or "",
        )
