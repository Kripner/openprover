#!/usr/bin/env python3
"""Test the Claude CLI (`claude -p`) with various reasoning/effort settings.

Useful for isolating how --effort and CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING
affect thinking token generation and time-to-first-text-token.

Examples:
  python scripts/ping_claude.py
  python scripts/ping_claude.py --effort low
  python scripts/ping_claude.py --effort max
  python scripts/ping_claude.py --no-thinking
  python scripts/ping_claude.py --model claude-opus-4-6 --effort max
  python scripts/ping_claude.py --show-thinking
"""

import argparse
import json
import os
import subprocess
import sys
import time


CLAUDE_MODEL_ALIASES = {
    "sonnet": "claude-sonnet-4-6",
    "opus":   "claude-opus-4-6",
    "haiku":  "claude-haiku-4-5-20251001",
}

DEFAULT_PROMPT = (
    "Prove that there are infinitely many primes."
)

DIM   = "\033[2m" if sys.stdout.isatty() else ""
GREEN = "\033[32m" if sys.stdout.isatty() else ""
YELLOW = "\033[33m" if sys.stdout.isatty() else ""
RED   = "\033[31m" if sys.stdout.isatty() else ""
RESET = "\033[0m"  if sys.stdout.isatty() else ""


SYSTEM_PROMPT = "You are a helpful assistant. Answer the user's question directly and concisely."


def run_claude(model: str, prompt: str, max_tokens: int,
               effort: str | None, no_thinking: bool,
               show_thinking: bool, debug: bool) -> None:
    cmd = [
        "claude", "-p",
        "--model", model,
        "--system-prompt", SYSTEM_PROMPT,
        "--output-format", "stream-json",
        "--verbose",
        "--include-partial-messages",
        "--tools", "",
    ]
    if effort:
        cmd.extend(["--effort", effort])

    env = dict(os.environ)
    env["CLAUDE_CODE_MAX_OUTPUT_TOKENS"] = str(max_tokens)
    if no_thinking:
        env["CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING"] = "1"
        env["MAX_THINKING_TOKENS"] = "0"

    print(f"Model:      {model}")
    print(f"Effort:     {effort or '(default)'}")
    print(f"No-thinking env: {'yes' if no_thinking else 'no'}")
    print(f"Max tokens: {max_tokens}")
    print(f"Prompt:     {prompt[:80]}{'...' if len(prompt) > 80 else ''}")
    print()

    start = time.monotonic()
    proc = subprocess.Popen(
        cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, bufsize=1, env=env,
    )
    proc.stdin.write(prompt)
    proc.stdin.close()

    thinking_chunks = 0
    text_chars = 0
    first_text_t: float | None = None
    first_thinking_t: float | None = None
    in_thinking_section = False

    print(f"{'─' * 60}")
    try:
        while True:
            line = proc.stdout.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue
            if debug:
                print(f"[debug] {line[:200]}", file=sys.stderr)
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue

            msg_type = msg.get("type", "")
            if msg_type != "stream_event":
                continue

            event = msg.get("event", {})
            etype = event.get("type", "")

            if etype == "content_block_start":
                cb = event.get("content_block", {})
                in_thinking_section = cb.get("type") == "thinking"

            elif etype == "content_block_stop":
                in_thinking_section = False

            elif etype == "content_block_delta":
                delta = event.get("delta", {})
                thinking = delta.get("thinking", "")
                text = delta.get("text", "")

                if thinking:
                    now = time.monotonic()
                    if first_thinking_t is None:
                        first_thinking_t = now - start
                    thinking_chunks += 1
                    if show_thinking:
                        sys.stdout.write(f"{DIM}{thinking}{RESET}")
                        sys.stdout.flush()

                elif text:
                    now = time.monotonic()
                    if first_text_t is None:
                        first_text_t = now - start
                        if thinking_chunks > 0 and not show_thinking:
                            # Separator after silent thinking
                            print(f"{DIM}[{thinking_chunks} thinking chunks in {first_text_t:.1f}s]{RESET}")
                        print()
                    text_chars += len(text)
                    sys.stdout.write(text)
                    sys.stdout.flush()

    except KeyboardInterrupt:
        proc.kill()
        print(f"\n{YELLOW}interrupted{RESET}")

    proc.wait()
    elapsed = time.monotonic() - start
    print()
    print(f"{'─' * 60}")
    if first_thinking_t is not None:
        print(f"First thinking chunk: {first_thinking_t:.2f}s")
    else:
        print(f"Thinking chunks:  {GREEN}0 (disabled or none){RESET}")
    if first_text_t is not None:
        print(f"First text token: {first_text_t:.2f}s")
    else:
        print(f"First text token: {RED}never{RESET}")
    print(f"Thinking chunks:  {thinking_chunks}")
    print(f"Text chars:       {text_chars}")
    print(f"Total elapsed:    {elapsed:.2f}s")
    print(f"Exit code:        {proc.returncode}")

    if proc.returncode != 0:
        stderr = proc.stderr.read()
        if stderr:
            print(f"\n{RED}stderr:{RESET}\n{stderr[:500]}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description="Test Claude CLI with various reasoning/effort settings"
    )
    parser.add_argument(
        "--model", default="sonnet",
        help="Model alias (sonnet, opus, haiku) or full model ID (default: sonnet)"
    )
    parser.add_argument(
        "--prompt", default=DEFAULT_PROMPT,
        help="Prompt to send"
    )
    parser.add_argument(
        "--max-tokens", type=int, default=8192,
        help="CLAUDE_CODE_MAX_OUTPUT_TOKENS (default: 8192)"
    )
    parser.add_argument(
        "--effort", choices=["low", "medium", "high", "max"], default=None,
        help="Effort level passed to claude --effort (default: none, uses Claude CLI default)"
    )
    parser.add_argument(
        "--no-thinking", action="store_true",
        help="Disable adaptive thinking via CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING=1 + MAX_THINKING_TOKENS=0"
    )
    parser.add_argument(
        "--show-thinking", action=argparse.BooleanOptionalAction, default=True,
        help="Print thinking chunks to stdout in dim (default: true)"
    )
    parser.add_argument(
        "--debug", action="store_true",
        help="Print raw stream-json lines to stderr"
    )
    args = parser.parse_args()

    model = CLAUDE_MODEL_ALIASES.get(args.model, args.model)

    run_claude(
        model=model,
        prompt=args.prompt,
        max_tokens=args.max_tokens,
        effort=args.effort,
        no_thinking=args.no_thinking,
        show_thinking=args.show_thinking,
        debug=args.debug,
    )


if __name__ == "__main__":
    main()
