"""OpenRouter HTTP client.

OpenRouter exposes an OpenAI-compatible `/v1/chat/completions` endpoint, so this
client is structurally very similar to the vLLM branch of HFClient.  We keep it
as a separate module to avoid tangling the local-server plumbing (health check,
batched-mode fallback) with a hosted API that has its own auth, attribution
headers, and cost reporting.
"""

import json
import logging
import socket
import threading
import time
import urllib.request
import urllib.error
from pathlib import Path

from ._base import Interrupted, archive

logger = logging.getLogger("openprover.llm")


MODEL_CONTEXT_LENGTHS = {
    "moonshotai/kimi-k2.5": 262_144,
    "minimax/minimax-m2.5": 196_608,
    "minimax/minimax-m2.7": 196_608,
}

DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"

# Recommended attribution headers (https://openrouter.ai/docs/api-reference/overview)
DEFAULT_REFERER = "https://github.com/kripner/openprover"
DEFAULT_TITLE = "openprover"

STREAM_READ_TIMEOUT = 60  # per-read timeout for SSE streams


def _extract_reasoning(delta: dict) -> str:
    """Pull reasoning text regardless of which field the model uses."""
    return delta.get("reasoning") or delta.get("reasoning_content") or ""


def _extract_sse_data_str(line: str) -> str | None:
    if not line or not line.startswith("data:"):
        return None
    return line[len("data:"):].lstrip()


class OpenRouterClient:
    """Calls OpenRouter's OpenAI-compatible chat completions API."""

    # Mark as vLLM-shaped so prover.py's tool gate picks the OpenAI format path.
    vllm = True

    def __init__(
        self,
        model: str,
        archive_dir: Path,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        answer_reserve: int = 4096,
        reasoning_effort: str | None = "high",
        referer: str = DEFAULT_REFERER,
        title: str = DEFAULT_TITLE,
    ):
        if model not in MODEL_CONTEXT_LENGTHS:
            raise ValueError(
                f"Unknown OpenRouter model {model!r}. "
                f"Known models: {', '.join(MODEL_CONTEXT_LENGTHS)}"
            )
        if not api_key:
            raise ValueError("OpenRouter api_key is required")
        self.model = model
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.archive_dir = archive_dir
        self.call_count = 0
        self.total_cost = 0.0
        self.context_length = MODEL_CONTEXT_LENGTHS[model]
        self.answer_reserve = answer_reserve
        # Conservative per-call output budget; OpenRouter rejects requests that
        # reserve more than the model's completion cap.
        self.max_output_tokens = answer_reserve
        self.reasoning_effort = reasoning_effort
        self.referer = referer
        self.title = title
        self._interrupted = threading.Event()

    # ── lifecycle ──────────────────────────────────────────────────

    def interrupt(self):
        self._interrupted.set()

    def soft_interrupt(self):
        self._interrupted.set()

    def cleanup(self):
        pass

    def clear_interrupt(self):
        self._interrupted.clear()

    def clear_soft_interrupt(self):
        pass

    # ── public API ─────────────────────────────────────────────────

    def call(
        self,
        prompt: str,
        system_prompt: str,
        json_schema: dict | None = None,
        label: str = "",
        web_search: bool = False,
        stream_callback=None,
        archive_path: Path | None = None,
        max_tokens: int | None = None,
        **_kwargs,
    ) -> dict:
        """Single-turn completion. json_schema and web_search are ignored."""
        self.call_count += 1
        call_num = self.call_count

        self._archive(call_num, label, prompt, system_prompt, json_schema,
                      None, None, 0, archive_path)

        logger.info("[%s] calling %s%s", label, self.model,
                    " (streaming)" if stream_callback else "")

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]
        payload = self._build_payload(
            messages,
            tools=None,
            max_tokens=max_tokens,
            stream=bool(stream_callback),
        )

        start = time.time()
        if self._interrupted.is_set():
            elapsed_ms = int((time.time() - start) * 1000)
            self._archive(call_num, label, prompt, system_prompt, json_schema,
                          None, "interrupted", elapsed_ms, archive_path)
            raise Interrupted()

        try:
            if stream_callback:
                return self._stream(
                    payload, prompt, system_prompt, json_schema,
                    call_num, label, start, stream_callback, archive_path,
                )
            return self._non_stream(
                payload, prompt, system_prompt, json_schema,
                call_num, label, start, archive_path,
            )
        except (urllib.error.URLError, ConnectionError) as e:
            elapsed_ms = int((time.time() - start) * 1000)
            self._archive(call_num, label, prompt, system_prompt, json_schema,
                          None, str(e), elapsed_ms, archive_path)
            raise RuntimeError(f"OpenRouter request failed: {e}")

    def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        max_tokens: int | None = None,
        label: str = "",
        stream_callback=None,
        archive_path: Path | None = None,
        **_kwargs,
    ) -> dict:
        """Multi-turn chat with optional tool calling (OpenAI function format)."""
        self.call_count += 1
        call_num = self.call_count

        payload = self._build_payload(
            messages,
            tools=tools,
            max_tokens=max_tokens,
            stream=bool(stream_callback),
        )

        prompt_text = json.dumps(messages, ensure_ascii=False)
        self._archive(call_num, label, prompt_text, "", None,
                      None, None, 0, archive_path)

        logger.info("[%s] chat %s%s", label, self.model,
                    " (streaming)" if stream_callback else "")
        start = time.time()

        if self._interrupted.is_set():
            elapsed_ms = int((time.time() - start) * 1000)
            self._archive(call_num, label, prompt_text, "", None,
                          None, "interrupted", elapsed_ms, archive_path)
            raise Interrupted()

        try:
            if stream_callback:
                return self._stream(
                    payload, prompt_text, "", None,
                    call_num, label, start, stream_callback, archive_path,
                    expect_tools=True,
                )
            return self._non_stream(
                payload, prompt_text, "", None,
                call_num, label, start, archive_path,
                expect_tools=True,
            )
        except (urllib.error.URLError, ConnectionError) as e:
            elapsed_ms = int((time.time() - start) * 1000)
            self._archive(call_num, label, prompt_text, "", None,
                          None, str(e), elapsed_ms, archive_path)
            raise RuntimeError(f"OpenRouter chat request failed: {e}")

    # ── internals ──────────────────────────────────────────────────

    def _build_payload(self, messages, tools, max_tokens, stream):
        effective_max = max_tokens if max_tokens is not None else self.max_output_tokens
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": effective_max,
            "temperature": 0.6,
            "top_p": 0.95,
            "stream": stream,
            # Ask OpenRouter to include usage (prompt/completion tokens + cost
            # in USD) in the final chunk / response body.
            "usage": {"include": True},
        }
        if stream:
            payload["stream_options"] = {"include_usage": True}
        if self.reasoning_effort:
            payload["reasoning"] = {"effort": self.reasoning_effort}
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        return payload

    def _make_request(self, payload):
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode(),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": self.referer,
                "X-Title": self.title,
            },
        )
        return urllib.request.urlopen(req, timeout=600)

    def _non_stream(self, payload, prompt, system_prompt, json_schema,
                    call_num, label, start, archive_path, *, expect_tools=False):
        try:
            resp = self._make_request(payload)
            raw = json.loads(resp.read())
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="replace")
            elapsed_ms = int((time.time() - start) * 1000)
            self._archive(call_num, label, prompt, system_prompt, json_schema,
                          None, f"HTTP {e.code}: {body}", elapsed_ms, archive_path)
            raise RuntimeError(f"HTTP {e.code}: {body[:1000]}")
        elapsed_ms = int((time.time() - start) * 1000)

        if self._interrupted.is_set():
            self._archive(call_num, label, prompt, system_prompt, json_schema,
                          None, "interrupted", elapsed_ms, archive_path)
            raise Interrupted()

        choice = raw["choices"][0]
        msg = choice.get("message", {})
        finish_reason = choice.get("finish_reason", "stop")
        reasoning = msg.get("reasoning") or msg.get("reasoning_content") or ""
        content = msg.get("content") or ""
        tool_calls = msg.get("tool_calls")

        cost = float(raw.get("usage", {}).get("cost") or 0.0)
        self.total_cost += cost

        self._archive(call_num, label, prompt, system_prompt, json_schema,
                      raw, None, elapsed_ms, archive_path,
                      thinking=reasoning, result_text=content)
        logger.info("[%s] done %dms finish=%s tools=%d cost=$%.4f",
                    label, elapsed_ms, finish_reason,
                    len(tool_calls) if tool_calls else 0, cost)

        result = {
            "result": content,
            "thinking": reasoning,
            "cost": cost,
            "duration_ms": elapsed_ms,
            "raw": raw,
            "finish_reason": finish_reason,
        }
        if expect_tools:
            result["tool_calls"] = tool_calls
        return result

    def _stream(self, payload, prompt, system_prompt, json_schema,
                call_num, label, start, callback, archive_path,
                *, expect_tools=False):
        try:
            resp = self._make_request(payload)
            if hasattr(resp, "fp") and hasattr(resp.fp, "raw"):
                resp.fp.raw._sock.settimeout(STREAM_READ_TIMEOUT)
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="replace")
            elapsed_ms = int((time.time() - start) * 1000)
            self._archive(call_num, label, prompt, system_prompt, json_schema,
                          None, f"HTTP {e.code}: {body}", elapsed_ms, archive_path)
            raise RuntimeError(f"HTTP {e.code}: {body[:1000]}")

        thinking_parts: list[str] = []
        output_parts: list[str] = []
        tool_call_acc: dict[int, dict] = {}
        finish_reason = "stop"
        interrupted = False
        usage: dict = {}

        try:
            for raw_line in resp:
                if self._interrupted.is_set():
                    interrupted = True
                    resp.close()
                    break
                line = raw_line.decode(errors="replace").strip()
                data_str = _extract_sse_data_str(line)
                if data_str is None:
                    # OpenRouter emits `: OPENROUTER PROCESSING` keep-alive comments.
                    continue
                if data_str == "[DONE]":
                    break
                try:
                    chunk = json.loads(data_str)
                except json.JSONDecodeError:
                    continue

                if "usage" in chunk and chunk["usage"]:
                    usage = chunk["usage"]

                choices = chunk.get("choices") or []
                if not choices:
                    continue
                choice = choices[0]
                chunk_finish = choice.get("finish_reason")
                if chunk_finish:
                    finish_reason = chunk_finish
                delta = choice.get("delta", {})

                reasoning = _extract_reasoning(delta)
                if reasoning:
                    callback(reasoning, "thinking")
                    thinking_parts.append(reasoning)

                content = delta.get("content") or ""
                if content:
                    callback(content, "text")
                    output_parts.append(content)

                for tc_delta in delta.get("tool_calls") or []:
                    idx = tc_delta.get("index", 0)
                    if idx not in tool_call_acc:
                        tool_call_acc[idx] = {
                            "id": tc_delta.get("id", ""),
                            "type": "function",
                            "function": {"name": "", "arguments": ""},
                        }
                    acc = tool_call_acc[idx]
                    if tc_delta.get("id"):
                        acc["id"] = tc_delta["id"]
                    fn = tc_delta.get("function", {})
                    if fn.get("name"):
                        acc["function"]["name"] = fn["name"]
                    if fn.get("arguments"):
                        acc["function"]["arguments"] += fn["arguments"]
        except socket.timeout:
            elapsed_ms = int((time.time() - start) * 1000)
            self._archive(call_num, label, prompt, system_prompt, json_schema,
                          None, f"stream read timeout ({STREAM_READ_TIMEOUT}s)",
                          elapsed_ms, archive_path)
            raise RuntimeError(
                f"OpenRouter stopped sending data for {STREAM_READ_TIMEOUT}s"
            )

        elapsed_ms = int((time.time() - start) * 1000)

        if interrupted:
            self._archive(call_num, label, prompt, system_prompt, json_schema,
                          None, "interrupted", elapsed_ms, archive_path)
            raise Interrupted()

        thinking_text = "".join(thinking_parts)
        result_text = "".join(output_parts)
        tool_calls = (
            [tool_call_acc[i] for i in sorted(tool_call_acc)]
            if tool_call_acc else None
        )
        cost = float(usage.get("cost") or 0.0) if usage else 0.0
        self.total_cost += cost

        raw_sidecar = {
            "result": result_text,
            "tool_calls": tool_calls,
            "usage": usage,
        }
        self._archive(call_num, label, prompt, system_prompt, json_schema,
                      raw_sidecar, None, elapsed_ms, archive_path,
                      thinking=thinking_text, result_text=result_text)
        logger.info("[%s] done %dms finish=%s tools=%d cost=$%.4f",
                    label, elapsed_ms, finish_reason,
                    len(tool_calls) if tool_calls else 0, cost)

        result = {
            "result": result_text,
            "thinking": thinking_text,
            "cost": cost,
            "duration_ms": elapsed_ms,
            "raw": raw_sidecar,
            "finish_reason": finish_reason,
        }
        if expect_tools:
            result["tool_calls"] = tool_calls
        return result

    def _archive(self, call_num, label, prompt, system_prompt, json_schema,
                 response, error, elapsed_ms, archive_path=None,
                 *, thinking="", result_text=""):
        archive(self.model, self.archive_dir, call_num, label, prompt,
                system_prompt, json_schema, response, error, elapsed_ms,
                archive_path, thinking=thinking, result_text=result_text)
