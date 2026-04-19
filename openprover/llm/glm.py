"""Z.ai GLM client (OpenAI-compatible native API).

Z.ai's Anthropic-compatible gateway zeroes out token usage, so we call the
native OpenAI-compatible endpoint instead.  This gives us real prompt_tokens /
completion_tokens in every response, which is required for token-based budget
tracking.

Endpoint: https://api.z.ai/api/coding/paas/v4/chat/completions
Auth:     Bearer <GLM_API_KEY>
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
    "glm-5": 128_000,
}

# GLM-5 supports reasoning_content in the same way as DeepSeek.
MAX_COMPLETION_TOKENS_REASONING = 32_768

DEFAULT_BASE_URL = "https://api.z.ai/api/coding/paas/v4"

STREAM_READ_TIMEOUT = 120  # GLM gateway can be slow


def _extract_reasoning(delta: dict) -> str:
    """Pull reasoning text regardless of which field the model uses."""
    return delta.get("reasoning") or delta.get("reasoning_content") or ""


def _extract_sse_data_str(line: str) -> str | None:
    if not line or not line.startswith("data:"):
        return None
    return line[len("data:"):].lstrip()


class GLMClient:
    """Calls Z.ai's OpenAI-compatible chat completions API for GLM models."""

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
    ):
        if model not in MODEL_CONTEXT_LENGTHS:
            raise ValueError(
                f"Unknown GLM model {model!r}. "
                f"Known models: {', '.join(MODEL_CONTEXT_LENGTHS)}"
            )
        if not api_key:
            raise ValueError("GLM api_key is required")
        self.model = model
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.archive_dir = archive_dir
        self.call_count = 0
        self.total_cost = 0.0
        self.context_length = MODEL_CONTEXT_LENGTHS[model]
        self.answer_reserve = answer_reserve
        self.reasoning_effort = reasoning_effort
        self.max_output_tokens = (
            MAX_COMPLETION_TOKENS_REASONING if reasoning_effort else answer_reserve
        )
        self._interrupted = threading.Event()

    # -- lifecycle ---------------------------------------------------------

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

    # -- public API --------------------------------------------------------

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
        """Single-turn completion."""
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
            raise RuntimeError(f"GLM request failed: {e}")

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
            raise RuntimeError(f"GLM chat request failed: {e}")

    # -- internals ---------------------------------------------------------

    def _build_payload(self, messages, tools, max_tokens, stream):
        effective_max = max_tokens if max_tokens is not None else self.max_output_tokens
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": effective_max,
            "temperature": 0.6,
            "top_p": 0.95,
            "stream": stream,
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
            },
        )
        return urllib.request.urlopen(req, timeout=600)

    def _non_stream(self, payload, prompt, system_prompt, json_schema,
                    call_num, label, start, archive_path, *, expect_tools=False):
        try:
            resp = self._make_request(payload)
            body_bytes = resp.read()
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="replace")
            elapsed_ms = int((time.time() - start) * 1000)
            self._archive(call_num, label, prompt, system_prompt, json_schema,
                          None, f"HTTP {e.code}: {body}", elapsed_ms, archive_path)
            raise RuntimeError(f"HTTP {e.code}: {body[:1000]}")

        try:
            raw = json.loads(body_bytes)
        except json.JSONDecodeError as e:
            elapsed_ms = int((time.time() - start) * 1000)
            self._archive(
                call_num, label, prompt, system_prompt, json_schema,
                None, f"JSON decode failed: {e}; body[:500]={body_bytes[:500]!r}",
                elapsed_ms, archive_path,
            )
            raise RuntimeError(
                f"GLM returned unparseable body ({len(body_bytes)} bytes): {e}"
            )
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

        # Normalize usage to Anthropic-style keys for _extract_token_usage
        oai_usage = raw.get("usage", {})
        raw["usage"] = {
            "input_tokens": oai_usage.get("prompt_tokens", 0),
            "output_tokens": oai_usage.get("completion_tokens", 0),
        }

        self._archive(call_num, label, prompt, system_prompt, json_schema,
                      raw, None, elapsed_ms, archive_path,
                      thinking=reasoning, result_text=content)
        logger.info("[%s] done %dms finish=%s in=%d out=%d",
                    label, elapsed_ms, finish_reason,
                    raw["usage"]["input_tokens"], raw["usage"]["output_tokens"])

        result = {
            "result": content,
            "thinking": reasoning,
            "cost": 0.0,
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
                f"GLM stopped sending data for {STREAM_READ_TIMEOUT}s"
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

        # Normalize usage to Anthropic-style keys
        raw_sidecar = {
            "result": result_text,
            "tool_calls": tool_calls,
            "usage": {
                "input_tokens": usage.get("prompt_tokens", 0),
                "output_tokens": usage.get("completion_tokens", 0),
            },
        }
        self._archive(call_num, label, prompt, system_prompt, json_schema,
                      raw_sidecar, None, elapsed_ms, archive_path,
                      thinking=thinking_text, result_text=result_text)
        logger.info("[%s] done %dms finish=%s in=%d out=%d",
                    label, elapsed_ms, finish_reason,
                    raw_sidecar["usage"]["input_tokens"],
                    raw_sidecar["usage"]["output_tokens"])

        result = {
            "result": result_text,
            "thinking": thinking_text,
            "cost": 0.0,
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
