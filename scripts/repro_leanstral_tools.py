#!/usr/bin/env python3
"""Reproduce: labs-leanstral-2603 tool calling breaks with longer instructions.

Tool calling on the Conversations API (/v1/conversations) silently stops
working when the `instructions` field exceeds roughly 15 tokens.  The model
ignores both the tools and the user message, producing generic greetings
instead.

The example uses a trivial `add(a, b)` tool with the explicit user message
"Call the add tool with a=2 and b=3" — there is no ambiguity about whether
the model should call the tool.

Usage:
    export MISTRAL_API_KEY='...'
    python scripts/repro_leanstral_tools.py
"""

import json
import os
import sys
import time
import urllib.request

API_KEY = os.environ.get("MISTRAL_API_KEY", "")
if not API_KEY:
    print("Set MISTRAL_API_KEY first.", file=sys.stderr)
    sys.exit(1)

MODEL = "labs-leanstral-2603"
URL = "https://api.mistral.ai/v1/conversations"
RUNS = 3

TOOL = {
    "type": "function",
    "function": {
        "name": "add",
        "description": "Add two numbers.",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {"type": "number", "description": "First number."},
                "b": {"type": "number", "description": "Second number."},
            },
            "required": ["a", "b"],
        },
    },
}

USER_MSG = "Call the add tool with a=2 and b=3."


def call(instructions: str, *, stream: bool) -> dict:
    """Returns {"tool_call": bool, "output": str}."""
    payload = {
        "model": MODEL,
        "inputs": [{"role": "user", "content": USER_MSG}],
        "instructions": instructions,
        "tools": [TOOL],
        "stream": stream,
        "completion_args": {
            "temperature": 1.0,
            "max_tokens": 4096,
            "top_p": 1,
            "reasoning_effort": "high",
        },
    }
    req = urllib.request.Request(
        URL,
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
        },
    )
    resp = urllib.request.urlopen(req, timeout=120)

    if not stream:
        raw = json.loads(resp.read())
        for o in raw.get("outputs", []):
            if o.get("type") == "function.call":
                return {"tool_call": True, "output": f'{o["name"]}({o["arguments"]})'}
        text = ""
        for o in raw.get("outputs", []):
            c = o.get("content", "")
            if isinstance(c, str) and c:
                text = c
        return {"tool_call": False, "output": text[:80]}

    has_tc = False
    tc_name, tc_args = "", ""
    output_parts: list[str] = []
    for raw_line in resp:
        line = raw_line.decode(errors="replace").strip()
        if not line.startswith("data:"):
            continue
        data_str = line[len("data:"):].lstrip()
        if data_str == "[DONE]":
            break
        try:
            chunk = json.loads(data_str)
        except json.JSONDecodeError:
            continue
        etype = chunk.get("type", "")
        if etype == "function.call.delta":
            has_tc = True
            if chunk.get("name"):
                tc_name = chunk["name"]
            tc_args += chunk.get("arguments", "")
        elif etype == "message.output.delta":
            c = chunk.get("content", "")
            if isinstance(c, str):
                output_parts.append(c)

    if has_tc:
        return {"tool_call": True, "output": f"{tc_name}({tc_args})"}
    return {"tool_call": False, "output": "".join(output_parts)[:80]}


def run_case(label, instructions, stream):
    mode = "stream" if stream else "non-stream"
    results = []
    for _ in range(RUNS):
        r = call(instructions, stream=stream)
        results.append(r)
        time.sleep(0.5)
    hits = sum(1 for r in results if r["tool_call"])
    markers = " ".join("✓" if r["tool_call"] else "✗" for r in results)
    print(f"  [{mode:<10}] {markers}  ({hits}/{RUNS})  {label}")
    if hits == 0:
        print(f"               sample output: {results[0]['output']!r}")


def main():
    print(f"Model: {MODEL}")
    print(f"User:  {USER_MSG!r}")
    print(f"Tool:  add(a: number, b: number)")
    print(f"Runs:  {RUNS} per case")
    print()

    cases = [
        ("short (29 chars)",
         "You have an add tool. Use it."),
        ("long  (73 chars)",
         "You are a helpful math assistant. Always use the add tool for arithmetic."),
    ]

    for label, instr in cases:
        print(f'instructions: {instr!r}')
        for stream in [True, False]:
            run_case(label, instr, stream)
            time.sleep(0.5)
        print()

    print("-" * 72)
    print("Expected: all cases return tool_call (the user explicitly")
    print('  says "Call the add tool with a=2 and b=3").')
    print()
    print("Observed: with short instructions, tool calls usually work")
    print("  (but sometimes stop working for extended periods). With")
    print("  long instructions (~15+ tokens), tool calls never work —")
    print("  the model ignores both the tool and the user message.")


if __name__ == "__main__":
    main()
