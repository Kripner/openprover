#!/usr/bin/env python3
"""Ping the Mistral API with a sample message and print the response.

Leanstral supports explicit reasoning via reasoning_effort='high' (temperature
must be 1.0). Reasoning tokens are returned in a separate 'reasoning' field.
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error


def build_example_calculator_tool():
    return {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Evaluate a basic arithmetic operation on two numbers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["add", "subtract", "multiply", "divide"],
                        "description": "Arithmetic operation to perform.",
                    },
                    "a": {"type": "number", "description": "First operand."},
                    "b": {"type": "number", "description": "Second operand."},
                },
                "required": ["operation", "a", "b"],
                "additionalProperties": False,
            },
        },
    }


def print_tool_calls(tool_calls):
    if not tool_calls:
        return
    print("\n\nTool calls:")
    for i, call in enumerate(tool_calls, start=1):
        print(f"  [{i}] {json.dumps(call, ensure_ascii=False)}")


def merge_function_call_delta(aggregated, chunk):
    """Handle Mistral's function.call.delta event — fields are top-level on the chunk."""
    fc_id = chunk.get("id", "")
    entry = aggregated.setdefault(
        fc_id,
        {"id": fc_id, "tool_call_id": "", "name": "", "arguments": ""},
    )
    if chunk.get("tool_call_id"):
        entry["tool_call_id"] = chunk["tool_call_id"]
    if chunk.get("name"):
        entry["name"] = chunk["name"]
    entry["arguments"] += chunk.get("arguments", "")


def main():
    parser = argparse.ArgumentParser(description="Ping the Mistral API")
    parser.add_argument("--model", default="labs-leanstral-2603",
                        help="Model name (default: labs-leanstral-2603)")
    parser.add_argument("--prompt", default="Hello! What is the square root of 144?",
                        help="Prompt to send")
    parser.add_argument("--max-tokens", type=int, default=2048)
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--reasoning-effort", choices=["none", "high"], default=None,
                        help="Enable reasoning (forces temperature=1.0)")
    parser.add_argument("--stream", action=argparse.BooleanOptionalAction,
                        default=True,
                        help="Stream tokens to console (default: true)")
    parser.add_argument("--example-tool", action=argparse.BooleanOptionalAction,
                        default=False,
                        help="Include a sample calculator tool in request (default: false)")
    parser.add_argument("--debug-stream", action=argparse.BooleanOptionalAction,
                        default=False,
                        help="Print raw SSE debug info to stderr (default: false)")
    parser.add_argument("--test-multi-turn", action="store_true",
                        help="Test multi-turn tool calling: replay a fake tool "
                             "call history to verify the entry format works")
    args = parser.parse_args()

    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("ERROR: MISTRAL_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    tools = [build_example_calculator_tool()] if args.example_tool else []

    temperature = 1.0 if args.reasoning_effort == "high" else args.temperature
    completion_args = {
        "temperature": temperature,
        "max_tokens": args.max_tokens,
        "top_p": 1,
    }
    if args.reasoning_effort:
        completion_args["reasoning_effort"] = args.reasoning_effort

    if args.test_multi_turn:
        # Two-step test: 1) send prompt with tool → get tool call + conv_id
        # 2) continue conversation with tool result using conv_id
        # This tests whether thinking stays structured in multi-turn.
        tools = [build_example_calculator_tool()]
        completion_args["reasoning_effort"] = "high"
        completion_args["temperature"] = 1.0
        args.debug_stream = True

        print("Step 1: Sending prompt with calculator tool...")
        print("─" * 60)

        step1_payload = json.dumps({
            "model": args.model,
            "inputs": [{"role": "user", "content":
                         "Use the calculator tool to compute 17 + 25."}],
            "tools": tools,
            "stream": True,
            "completion_args": completion_args,
        }).encode()

        step1_req = urllib.request.Request(
            "https://api.mistral.ai/v1/conversations",
            data=step1_payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
        )
        try:
            step1_resp = urllib.request.urlopen(step1_req, timeout=120)
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="replace")
            print(f"ERROR: HTTP {e.code}: {body}", file=sys.stderr)
            sys.exit(1)

        conv_id = None
        tc_acc = {}
        for line in step1_resp:
            line = line.decode(errors="replace").strip()
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
            if etype == "conversation.response.started":
                conv_id = chunk.get("conversation_id")
                print(f"  conversation_id: {conv_id}")
            elif etype == "function.call.delta":
                merge_function_call_delta(tc_acc, chunk)
            elif etype == "message.output.delta":
                content = chunk.get("content", "")
                fmt = "dict" if isinstance(content, dict) else "str"
                if isinstance(content, dict):
                    print(f"  [content {fmt} type={content.get('type','?')}]",
                          end="", flush=True)
                elif content:
                    sys.stdout.write(content)
                    sys.stdout.flush()

        print()
        if tc_acc:
            tc = list(tc_acc.values())[0]
            tc_id = tc.get("tool_call_id") or tc.get("id")
            print(f"  Tool call: {tc['name']}({tc['arguments']})"
                  f" id={tc_id}")
        else:
            print("  No tool calls — can't continue multi-turn test")
            sys.exit(0)

        # Execute the "tool" (just return 42)
        tool_result = '{"result": 42}'
        print(f"\nStep 2: Continuing conversation {conv_id} with tool result...")
        print("  Watch for content format: dict{{'type':'thinking'}} vs plain str")
        print("─" * 60)

        step2_payload = json.dumps({
            "inputs": [{
                "tool_call_id": tc_id,
                "result": tool_result,
                "type": "function.result",
            }],
            "stream": True,
            "completion_args": completion_args,
        }).encode()

        step2_req = urllib.request.Request(
            f"https://api.mistral.ai/v1/conversations/{conv_id}",
            data=step2_payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
        )
        try:
            step2_resp = urllib.request.urlopen(step2_req, timeout=120)
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="replace")
            print(f"ERROR: HTTP {e.code}: {body}", file=sys.stderr)
            sys.exit(1)

        first_content = True
        dim = "\033[2m" if sys.stdout.isatty() else ""
        reset = "\033[0m" if sys.stdout.isatty() else ""
        for line in step2_resp:
            line = line.decode(errors="replace").strip()
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
            if etype == "message.output.delta":
                content = chunk.get("content", "")
                if first_content and content:
                    fmt = type(content).__name__
                    if isinstance(content, dict):
                        print(f"  ** Content format: {fmt}"
                              f" type={content.get('type','?')} **")
                    else:
                        print(f"  ** Content format: {fmt} **")
                    first_content = False
                if isinstance(content, str) and content:
                    sys.stdout.write(content)
                    sys.stdout.flush()
                elif isinstance(content, dict):
                    ctype = content.get("type", "")
                    if ctype == "thinking":
                        for p in content.get("thinking", []):
                            sys.stdout.write(f'{dim}{p.get("text","")}{reset}')
                    else:
                        for p in content.get("content", []):
                            sys.stdout.write(p.get("text", ""))
                    sys.stdout.flush()

        print("\n" + "─" * 60)
        print("Done. If content was 'dict type=thinking', thinking is preserved.")
        print("If content was 'str', thinking is lost in multi-turn.")
        sys.exit(0)
    else:
        inputs = [{"role": "user", "content": args.prompt}]

    payload = json.dumps({
        "model": args.model,
        "inputs": inputs,
        "tools": tools,
        "stream": args.stream,
        "completion_args": completion_args,
    }).encode()

    req = urllib.request.Request(
        "https://api.mistral.ai/v1/conversations",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )

    print(f"Model:  {args.model}")
    if args.reasoning_effort:
        print(f"Reasoning: {args.reasoning_effort}  (temperature forced to 1.0)")
    if args.example_tool:
        print("Tools:  calculator")
    print("─" * 60)
    print(f"[User] {args.prompt}")
    print("─" * 60)

    try:
        resp = urllib.request.urlopen(req, timeout=120)
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        print(f"ERROR: HTTP {e.code}: {body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"ERROR: Request failed: {e}", file=sys.stderr)
        sys.exit(1)

    usage = {}

    if args.stream:
        tool_calls_by_index = {}
        in_reasoning = False

        for line in resp:
            line = line.decode(errors="replace").strip()
            if args.debug_stream:
                print(f"[debug] raw: {line[:300]}", file=sys.stderr)
            if not line.startswith("data:"):
                continue
            data_str = line[len("data:"):].lstrip()
            if data_str == "[DONE]":
                break
            try:
                chunk = json.loads(data_str)
            except json.JSONDecodeError:
                continue
            if args.debug_stream:
                print(f"[debug] chunk keys: {list(chunk.keys())}", file=sys.stderr)

            if "usage" in chunk:
                usage = chunk["usage"]

            event_type = chunk.get("type", "")

            if event_type == "function.call.delta":
                merge_function_call_delta(tool_calls_by_index, chunk)
                continue

            if event_type != "message.output.delta":
                continue

            content = chunk.get("content", "")
            reasoning_token = ""
            content_token = ""
            if isinstance(content, str):
                content_token = content
            elif isinstance(content, dict):
                ctype = content.get("type", "")
                if ctype == "thinking":
                    for part in content.get("thinking", []):
                        reasoning_token += part.get("text", "")
                else:
                    for part in content.get("content", []):
                        content_token += part.get("text", "")
                    if not content_token:
                        content_token = content.get("text", "")

            if reasoning_token:
                if not in_reasoning:
                    sys.stdout.write(dim)
                    in_reasoning = True
                sys.stdout.write(reasoning_token)
                sys.stdout.flush()
            if content_token:
                if in_reasoning:
                    sys.stdout.write(reset)
                    in_reasoning = False
                sys.stdout.write(content_token)
                sys.stdout.flush()

        if in_reasoning:
            sys.stdout.write(reset)
        print()

        if tool_calls_by_index:
            print_tool_calls(list(tool_calls_by_index.values()))
    else:
        data = json.loads(resp.read())
        if args.debug_stream:
            print(f"[debug] response keys: {list(data.keys())}", file=sys.stderr)
        usage = data.get("usage", {})
        tool_calls = []
        for entry in data.get("outputs", []):
            if entry.get("role") != "assistant":
                continue
            reasoning = entry.get("reasoning", "")
            if reasoning:
                print(f"{dim}{reasoning}{reset}")
            print(entry.get("content", ""))
            tool_calls.extend(entry.get("tool_calls") or [])
        print_tool_calls(tool_calls)

    print("─" * 60)
    print(f"Prompt tokens:     {usage.get('prompt_tokens', '?')}")
    print(f"Completion tokens: {usage.get('completion_tokens', '?')}")
    print(f"Total tokens:      {usage.get('total_tokens', '?')}")


if __name__ == "__main__":
    main()
