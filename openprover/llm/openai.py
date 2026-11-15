"""OpenAI Responses API client for OpenProver."""
import json
import os
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path
from ._base import Interrupted, archive

class OpenAIClient:
    """Existing OpenProver client contract, using the Responses API."""
    vllm = True  # Native function-tool calling in the existing worker loop.

    def __init__(self, model="gpt-6-astra", archive_dir=None, api_key=None,
                 base_url="https://api.openai.com/v1", reasoning_mode="pro",
                 reasoning_effort="max", reasoning_summary="auto",
                 answer_reserve=4096):
        self.model, self.archive_dir = model, Path(archive_dir or ".")
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is required")
        self.base_url = base_url.rstrip("/")
        self.reasoning_mode, self.reasoning_effort = reasoning_mode, reasoning_effort
        self.reasoning_summary = reasoning_summary
        self.answer_reserve, self.context_length = answer_reserve, 1_050_000
        self.max_output_tokens = 32768
        self.total_cost, self.call_count = 0.0, 0
        self._interrupt, self._lock = threading.Event(), threading.Lock()
        self._previous_items = {}

    def interrupt(self): self._interrupt.set()
    def soft_interrupt(self): self._interrupt.set()
    def clear_interrupt(self): self._interrupt.clear()
    def clear_soft_interrupt(self): self._interrupt.clear()
    def cleanup(self): pass

    def _input(self, messages):
        items = []
        for m in messages:
            role = m.get("role")
            if role == "tool":
                items.append({"type": "function_call_output", "call_id": m["tool_call_id"],
                              "output": str(m.get("content") or "")})
            elif role == "assistant" and m.get("tool_calls"):
                with self._lock:
                    saved = self._previous_items.get(m["tool_calls"][0]["id"])
                if saved:
                    items.extend(saved)  # Preserve reasoning items, not only visible text.
                else:
                    for tc in m["tool_calls"]:
                        items.append({"type": "function_call", "call_id": tc["id"],
                                      "name": tc["function"]["name"],
                                      "arguments": tc["function"]["arguments"]})
                    if m.get("content"):
                        items.append({"role": "assistant", "content": m["content"]})
            else:
                items.append({"role": role, "content": m.get("content") or ""})
        return items

    def _payload(self, messages, tools=None, max_tokens=None, schema=None):
        reasoning = {"mode": self.reasoning_mode}
        if self.reasoning_effort != "model-default":
            reasoning["effort"] = self.reasoning_effort
        if self.reasoning_summary != "off":
            reasoning["summary"] = self.reasoning_summary
        payload = {"model": self.model, "input": self._input(messages),
                   "reasoning": reasoning, "store": False,
                   "max_output_tokens": max_tokens or self.max_output_tokens}
        if tools:
            payload["tools"] = [
                {"type": "function", "name": t["function"]["name"],
                 "description": t["function"].get("description", ""),
                 "parameters": t["function"]["parameters"], "strict": False}
                for t in tools
            ]
        if schema:
            payload["text"] = {"format": {"type": "json_schema",
                "name": "openprover_result", "schema": schema, "strict": True}}
        return payload

    @staticmethod
    def _decode(raw):
        texts, summaries, calls = [], [], []
        for item in raw.get("output", []):
            if item.get("type") == "message":
                texts.extend(p.get("text", "") for p in item.get("content", [])
                             if p.get("type") == "output_text")
            elif item.get("type") == "reasoning":
                summaries.extend(p.get("text", "") for p in item.get("summary", []))
            elif item.get("type") == "function_call":
                calls.append({"id": item["call_id"], "type": "function",
                    "function": {"name": item["name"],
                                 "arguments": item.get("arguments", "{}")}})
        usage = raw.get("usage") or {}
        cached = (usage.get("input_tokens_details") or {}).get("cached_tokens", 0)
        raw["usage"] = {**usage, "cache_read_input_tokens": cached,
                        "cache_creation_input_tokens": 0}
        finish = "tool_calls" if calls else (
            "length" if raw.get("status") == "incomplete" else "stop")
        return {"result": "".join(texts), "thinking": "\n".join(summaries),
                "tool_calls": calls, "finish_reason": finish,
                "raw": raw, "cost": 0.0, "duration_ms": 0}

    def _request(self, payload, callback):
        if self._interrupt.is_set():
            raise Interrupted()
        payload = {**payload, "stream": bool(callback)}
        req = urllib.request.Request(self.base_url + "/responses",
            data=json.dumps(payload).encode(),
            headers={"Authorization": "Bearer " + self.api_key,
                     "Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=900) as response:
                if callback is None:
                    return json.load(response)
                completed = None
                for raw_line in response:
                    if self._interrupt.is_set():
                        raise Interrupted()
                    line = raw_line.decode(errors="replace").strip()
                    if not line.startswith("data:"):
                        continue
                    data = line[5:].strip()
                    if data == "[DONE]":
                        break
                    try:
                        event = json.loads(data)
                    except ValueError:
                        continue
                    kind = event.get("type")
                    if kind == "response.output_text.delta":
                        callback(event.get("delta", ""), "text")
                    elif kind == "response.reasoning_summary_text.delta":
                        callback(event.get("delta", ""), "thinking")
                    elif kind in ("response.completed", "response.incomplete"):
                        completed = event.get("response")
                    elif kind in ("response.failed", "error"):
                        raise RuntimeError("OpenAI response failed: " + str(event))
                if completed is None:
                    raise RuntimeError("OpenAI stream ended without a completed response")
                return completed
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")[:2000]
            raise RuntimeError("OpenAI HTTP %d: %s" % (e.code, detail)) from e

    def _execute(self, payload, label, prompt, system_prompt, schema,
                 callback, archive_path):
        with self._lock:
            self.call_count += 1
            number = self.call_count
        start = time.monotonic()
        try:
            raw = self._request(payload, callback)
            if self._interrupt.is_set():
                raise Interrupted()
            result = self._decode(raw)
            result["duration_ms"] = int((time.monotonic() - start) * 1000)
            with self._lock:
                for tc in result["tool_calls"]:
                    self._previous_items[tc["id"]] = raw.get("output", [])
            archive(self.model, self.archive_dir, number, label, prompt,
                    system_prompt, schema, raw, None, result["duration_ms"],
                    archive_path, thinking=result["thinking"],
                    result_text=result["result"])
            return result
        except Exception as e:
            archive(self.model, self.archive_dir, number, label, prompt,
                    system_prompt, schema, None, str(e),
                    int((time.monotonic() - start) * 1000), archive_path)
            raise

    def call(self, prompt, system_prompt, json_schema=None, label="",
             web_search=False, stream_callback=None, archive_path=None,
             max_tokens=None, **kwargs):
        if web_search:
            raise NotImplementedError("OpenAI web search will be added in the research tools PR")
        messages = [{"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}]
        return self._execute(self._payload(messages, max_tokens=max_tokens,
                             schema=json_schema), label, prompt, system_prompt,
                             json_schema, stream_callback, archive_path)

    def chat(self, messages, tools=None, max_tokens=None, label="",
             stream_callback=None, archive_path=None, **kwargs):
        return self._execute(self._payload(messages, tools=tools,
                             max_tokens=max_tokens), label,
                             json.dumps(messages, ensure_ascii=False), "",
                             None, stream_callback, archive_path)
