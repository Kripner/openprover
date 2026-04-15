#!/usr/bin/env python3
"""Ping OpenRouter's chat completions API.

Sends a sample query to OpenRouter (default model: moonshotai/kimi-k2.5) to
verify credentials, streaming, reasoning, and tool calling all work end-to-end.

Requires: OPENROUTER_API_KEY in the environment.

Examples:
  python scripts/ping_openrouter.py
  python scripts/ping_openrouter.py --no-stream
  python scripts/ping_openrouter.py --tools
  python scripts/ping_openrouter.py --model moonshotai/kimi-k2.5 --prompt "..."
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error


BASE_URL = "https://openrouter.ai/api/v1"


def build_example_tool():
    return {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "Return the current wall-clock time for a given IANA timezone.",
            "parameters": {
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "description": "IANA timezone, e.g. 'Europe/Prague' or 'UTC'.",
                    },
                },
                "required": ["timezone"],
                "additionalProperties": False,
            },
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Ping the OpenRouter API")
    parser.add_argument("--model", default="moonshotai/kimi-k2.5",
                        help="OpenRouter model id (default: moonshotai/kimi-k2.5)")
    parser.add_argument("--prompt",
                        default="Hello! In one sentence: what is the square root of 144?",
                        help="Prompt to send")
    parser.add_argument("--max-tokens", type=int, default=1024)
    parser.add_argument("--reasoning-effort", choices=["low", "medium", "high"],
                        default="high", help="Reasoning effort (default: high)")
    parser.add_argument("--stream", action=argparse.BooleanOptionalAction,
                        default=True, help="Stream tokens to console (default: true)")
    parser.add_argument("--tools", action="store_true",
                        help="Include a dummy get_time tool and expect a tool call")
    parser.add_argument("--debug-stream", action="store_true",
                        help="Print raw SSE lines to stderr for debugging")
    args = parser.parse_args()

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("ERROR: OPENROUTER_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    prompt = args.prompt
    tools = None
    if args.tools:
        tools = [build_example_tool()]
        prompt = "Use the get_time tool to fetch the current time in Europe/Prague."

    payload = {
        "model": args.model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": args.max_tokens,
        "temperature": 0.6,
        "top_p": 0.95,
        "stream": args.stream,
        "reasoning": {"effort": args.reasoning_effort},
        "usage": {"include": True},
    }
    if args.stream:
        payload["stream_options"] = {"include_usage": True}
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"

    req = urllib.request.Request(
        f"{BASE_URL}/chat/completions",
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://github.com/kripner/openprover",
            "X-Title": "openprover",
        },
    )

    print(f"Model:  {args.model}")
    print(f"Effort: {args.reasoning_effort}")
    if tools:
        print("Tools:  get_time")
    print("─" * 60)
    print(f"[User] {prompt}")
    print("─" * 60)

    try:
        resp = urllib.request.urlopen(req, timeout=300)
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        print(f"ERROR: HTTP {e.code}: {body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"ERROR: Request failed: {e}", file=sys.stderr)
        sys.exit(1)

    dim = "\033[2m" if sys.stdout.isatty() else ""
    reset = "\033[0m" if sys.stdout.isatty() else ""

    finish_reason = None
    usage: dict = {}
    tool_calls_by_index: dict[int, dict] = {}
    in_reasoning = False

    if args.stream:
        for raw_line in resp:
            line = raw_line.decode(errors="replace").strip()
            if args.debug_stream:
                print(f"[debug] {line[:300]}", file=sys.stderr)
            if not line.startswith("data:"):
                continue
            data_str = line[len("data:"):].lstrip()
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
            fr = choice.get("finish_reason")
            if fr:
                finish_reason = fr
            delta = choice.get("delta", {})

            reasoning = delta.get("reasoning") or delta.get("reasoning_content") or ""
            if reasoning:
                if not in_reasoning:
                    sys.stdout.write(dim)
                    in_reasoning = True
                sys.stdout.write(reasoning)
                sys.stdout.flush()

            content = delta.get("content") or ""
            if content:
                if in_reasoning:
                    sys.stdout.write(reset)
                    in_reasoning = False
                sys.stdout.write(content)
                sys.stdout.flush()

            for tc in delta.get("tool_calls") or []:
                idx = tc.get("index", 0)
                acc = tool_calls_by_index.setdefault(idx, {
                    "id": tc.get("id", ""),
                    "type": "function",
                    "function": {"name": "", "arguments": ""},
                })
                if tc.get("id"):
                    acc["id"] = tc["id"]
                fn = tc.get("function", {})
                if fn.get("name"):
                    acc["function"]["name"] = fn["name"]
                if fn.get("arguments"):
                    acc["function"]["arguments"] += fn["arguments"]

        if in_reasoning:
            sys.stdout.write(reset)
        print()
    else:
        data = json.loads(resp.read())
        usage = data.get("usage", {}) or {}
        choice = data["choices"][0]
        msg = choice.get("message", {})
        finish_reason = choice.get("finish_reason")
        reasoning = msg.get("reasoning") or msg.get("reasoning_content") or ""
        if reasoning:
            print(f"{dim}{reasoning}{reset}")
        if msg.get("content"):
            print(msg["content"])
        for i, tc in enumerate(msg.get("tool_calls") or []):
            tool_calls_by_index[i] = tc

    tool_calls = [tool_calls_by_index[i] for i in sorted(tool_calls_by_index)]
    if tool_calls:
        print("\nTool calls:")
        for i, tc in enumerate(tool_calls, start=1):
            fn = tc.get("function", {})
            name = fn.get("name", "?")
            raw_args = fn.get("arguments", "")
            try:
                parsed = json.loads(raw_args) if raw_args else {}
                rendered = json.dumps(parsed, ensure_ascii=False)
            except json.JSONDecodeError:
                rendered = raw_args
            print(f"  [{i}] {name}({rendered})  id={tc.get('id','')}")

    print("─" * 60)
    print(f"Finish reason:     {finish_reason or '?'}")
    print(f"Prompt tokens:     {usage.get('prompt_tokens', '?')}")
    print(f"Completion tokens: {usage.get('completion_tokens', '?')}")
    print(f"Total tokens:      {usage.get('total_tokens', '?')}")
    cost = usage.get("cost")
    if cost is not None:
        print(f"Cost (USD):        ${float(cost):.6f}")

    if args.tools:
        if not tool_calls:
            print("\nFAIL: --tools was set but model produced no tool calls",
                  file=sys.stderr)
            sys.exit(2)
        if finish_reason != "tool_calls":
            print(f"\nWARNING: finish_reason={finish_reason!r} (expected 'tool_calls')",
                  file=sys.stderr)


if __name__ == "__main__":
    main()
