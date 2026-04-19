#!/usr/bin/env python3
"""Baseline prover: plain conversation, no tools.

The model is asked to write a Lean 4 proof inside <lean>...</lean> tags.
Each turn we extract the block, run lean_verify, and append the result
as a follow-up user message.  Loops until the proof verifies or the
time budget runs out.
"""

import argparse
import json
import logging
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

from openprover.lean.core import (
    LeanTheorem, LeanWorkDir, lean_has_errors, run_lean_check,
)
from openprover.llm import LLMClient, GLMClient, MistralClient, OpenRouterClient
from openprover.llm._base import is_rate_limited_error, is_transient_error

logger = logging.getLogger("baseline")

MISTRAL_MODEL_MAP = {"leanstral": "labs-leanstral-2603"}
OPENROUTER_MODEL_MAP = {
    "kimi-k2.5": "moonshotai/kimi-k2.5",
    "minimax-m2.5": "minimax/minimax-m2.5",
    "minimax-m2.7": "minimax/minimax-m2.7",
}
CLAUDE_MODELS = {"sonnet", "opus"}
GLM_MODEL_MAP = {"glm-5": "glm-5"}
GLM_BASE_URL = "https://api.z.ai/api/coding/paas/v4"
RATE_LIMIT_WAIT = 600  # seconds to wait before retrying after rate limit

# Match ```lean ... ``` (or ```lean4 ... ```) markdown code fences.
LEAN_FENCE_RE = re.compile(
    r"```lean[0-9]*\s*\n(.*?)\n```",
    re.DOTALL | re.IGNORECASE,
)


# ── Helpers ──────────────────────────────────────────────────────────

def _parse_duration(s: str) -> float:
    """Parse '10m', '2h', '1h30m' into seconds."""
    total = 0.0
    for match in re.finditer(r"(\d+(?:\.\d+)?)\s*([hms])", s):
        val, unit = float(match.group(1)), match.group(2)
        total += val * {"h": 3600, "m": 60, "s": 1}[unit]
    if total == 0:
        total = float(s)
    return total


def _slugify(text: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower()).strip("-")
    return s[:40] or "theorem"


def _extract_lean_blocks(text: str) -> list[str]:
    """Return the contents of every ```lean ... ``` block in text, in order."""
    return [m.strip() for m in LEAN_FENCE_RE.findall(text)]


def _sorry_column(raw_text: str, sorry_start: int) -> int:
    """Return the column (number of chars between start of line and `sorry`)."""
    line_start = raw_text.rfind("\n", 0, sorry_start) + 1
    return sorry_start - line_start


def _reindent(replacement: str, column: int) -> str:
    """Re-indent a multi-line proof body so subsequent lines match `column`.

    The first line replaces `sorry` directly and inherits whatever indent
    was already on that line, so we leave it alone. Every following line
    gets `column` spaces prepended (blank lines are left empty).
    """
    lines = replacement.splitlines()
    if len(lines) <= 1:
        return replacement
    pad = " " * column
    out = [lines[0]]
    for line in lines[1:]:
        out.append(pad + line if line.strip() else line)
    return "\n".join(out)


def _verify(code: str, work_dir: LeanWorkDir, project_dir: Path) -> tuple[bool, str]:
    """Run lean_verify and return (success, feedback)."""
    path = work_dir.make_file("baseline_verify", code)
    try:
        success, feedback, _ = run_lean_check(path, project_dir)
    finally:
        path.unlink(missing_ok=True)
    # Distinguish real errors from warnings-only (Lean exits non-zero for
    # warnings too).  This matches the logic in prover.py:1154-1157.
    if not success and feedback:
        if not lean_has_errors(feedback) and "sorry" not in feedback.lower():
            success = True
    if success:
        return True, "OK"
    if "sorry" in feedback.lower() and not lean_has_errors(feedback):
        return False, feedback + "\n\nNote: code contains sorry — proof has gaps."
    return False, feedback


def _write_turn_log(path: Path, *, turn: int, prompt: str, thinking: str,
                    reply: str, turn_tokens: int, outcome: str,
                    feedback: str, spliced: str) -> None:
    """Write a single turn's full record (prompt, thinking, reply, result)."""
    parts = [
        f"# Turn {turn}\n",
        f"- outcome: **{outcome or 'unknown'}**",
        f"- tokens: {turn_tokens}\n",
        "## User prompt\n",
        f"````\n{prompt}\n````\n",
    ]
    if thinking:
        parts.append("## Thinking\n")
        parts.append(f"````\n{thinking}\n````\n")
    parts.append("## Reply\n")
    parts.append(f"````\n{reply}\n````\n")
    if spliced:
        parts.append("## Spliced Lean source\n")
        parts.append(f"```lean\n{spliced}\n```\n")
    if feedback:
        parts.append("## Verifier feedback\n")
        parts.append(f"````\n{feedback}\n````\n")
    path.write_text("\n".join(parts))


def _format_turn_for_transcript(*, turn: int, prompt: str, thinking: str,
                                reply: str, turn_tokens: int, outcome: str,
                                feedback: str, spliced: str) -> str:
    """Return the markdown chunk appended to transcript.md after each turn."""
    out = [f"\n## Turn {turn} — {outcome or 'unknown'} ({turn_tokens} tokens)\n"]
    out.append("\n### User prompt\n\n````\n" + prompt + "\n````\n")
    if thinking:
        out.append("\n### Thinking\n\n````\n" + thinking + "\n````\n")
    out.append("\n### Reply\n\n````\n" + reply + "\n````\n")
    if feedback and outcome != "ok":
        out.append("\n### Verifier feedback\n\n````\n" + feedback + "\n````\n")
    return "".join(out)


# ── Core loop ────────────────────────────────────────────────────────

SYSTEM_PROMPT = '''\
You are a Lean 4 theorem prover. You will be given a theorem whose \
proof is `sorry`. You must produce ONLY the tactic/term block that \
replaces `sorry` — NOT the whole theorem.

The framework parses the original theorem, splices your block in place \
of `sorry`, and runs `lake env lean`. If verification fails, the \
compiler errors are reported back and you try again.

Output format: a single ```lean ... ``` markdown fence containing JUST \
the replacement code. Do NOT repeat the `theorem` line, the binders, \
the type, the `:= by`, the imports, or the opens.

### Worked example

Given this input theorem:

```lean
theorem add_zero_eq (n : ℕ) : n + 0 = n := by
  sorry
```

A correct reply is:

```lean
simp
```

That's it — just the proof body. After splicing, the framework runs:

```lean
theorem add_zero_eq (n : ℕ) : n + 0 = n := by
  simp
```

Multi-line tactic blocks are fine — just keep them as the proof body:

```lean
intro h
rw [h]
ring
```

If the theorem has multiple `sorry`s, output one ```lean ... ``` fence \
per `sorry`, in order. Only the LAST N fences in your reply are used \
(where N is the number of sorries), so you can iterate inside one reply \
and put your final attempt at the end.

You may NOT use any of: `sorry`, `axiom`, `unsafe`, `set_option`, \
`native_decide`, or `import` inside your replacement.\
'''

INITIAL_USER_MSG = """\
Prove this theorem.

## Informal statement
{informal}

## Theorem (your proof will replace the `sorry`)
```lean
{formal}
```

Output {num_sorries} ```lean ... ``` block(s), one per `sorry`, each \
containing ONLY the proof body (no `theorem` line, no imports).
"""


def run_baseline(
    name: str,
    theorem_lean: str,
    theorem_informal: str,
    lean_project_dir: Path,
    model: str,
    run_dir: Path,
    max_time: float | None = None,
    max_tokens: int | None = None,
    stream: bool = False,
    quiet: bool = False,
) -> dict:
    """Run the baseline on a single theorem.

    Exactly one of max_time (seconds) or max_tokens (completion tokens)
    must be set. When quiet=True, per-turn progress is only written to
    log.txt (not stdout) — used by the benchmark harness which prints
    its own one-line-per-problem summary. Returns
    {"status", "elapsed", "turns", "verifications", "tokens", "error"}.
    """
    if (max_time is None) == (max_tokens is None):
        raise ValueError("specify exactly one of max_time or max_tokens")

    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "THEOREM.lean").write_text(theorem_lean + "\n")
    if theorem_informal:
        (run_dir / "THEOREM.md").write_text(theorem_informal + "\n")

    # Per-turn detailed logs go under turns/, raw API archives under calls/.
    turns_dir = run_dir / "turns"
    turns_dir.mkdir(exist_ok=True)
    archive_dir = run_dir / "calls"
    transcript_path = run_dir / "transcript.md"
    transcript_path.write_text(
        f"# Baseline transcript: {name}\n\n"
        f"- model: `{model}`\n"
        f"- run dir: `{run_dir}`\n\n"
        f"## System prompt\n\n````\n{SYSTEM_PROMPT}\n````\n"
    )

    def _append_transcript(text: str) -> None:
        with transcript_path.open("a") as f:
            f.write(text)

    if model in CLAUDE_MODELS:
        client = LLMClient(model=model, archive_dir=archive_dir)
    elif model in GLM_MODEL_MAP:
        glm_key = os.environ.get("GLM_API_KEY")
        if not glm_key:
            print("Error: GLM_API_KEY environment variable not set.", file=sys.stderr)
            sys.exit(1)
        client = GLMClient(model=GLM_MODEL_MAP[model], archive_dir=archive_dir,
                           api_key=glm_key, base_url=GLM_BASE_URL)
    elif model in OPENROUTER_MODEL_MAP:
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            print("Error: OPENROUTER_API_KEY environment variable not set.",
                  file=sys.stderr)
            print("  Get an API key from https://openrouter.ai/keys",
                  file=sys.stderr)
            sys.exit(1)
        client = OpenRouterClient(model=OPENROUTER_MODEL_MAP[model],
                                  archive_dir=archive_dir, api_key=api_key)
    else:
        mistral_model = MISTRAL_MODEL_MAP.get(model, model)
        client = MistralClient(model=mistral_model, archive_dir=archive_dir)
    work_dir = LeanWorkDir(lean_project_dir)

    # Parse the input theorem so we can splice proof bodies into its
    # original sorries — the model can never edit the statement.
    parsed = LeanTheorem(theorem_lean)
    if parsed.num_sorries == 0:
        return {"status": "error", "elapsed": 0, "turns": 0,
                "verifications": 0, "tokens": 0,
                "error": "input theorem contains no `sorry` placeholder"}

    initial_user = INITIAL_USER_MSG.format(
        informal=theorem_informal or "(none provided)",
        formal=theorem_lean,
        num_sorries=parsed.num_sorries,
    )

    # For Mistral models we use the Conversations API's server-side
    # context (conversation_id) so we only send the NEW user message
    # each turn — avoids quadratic memory/disk growth.  For Claude we
    # still accumulate the full transcript client-side.
    use_conv_id = getattr(client, "mistral", False)
    conversation_id: str | None = None
    transcript: list[str] = [initial_user]
    log_lines: list[str] = []
    turns = 0
    verifications = 0
    tokens = 0
    proved = False
    start = time.monotonic()

    def log(msg: str):
        log_lines.append(msg)
        if not quiet:
            print(f"  [{name}] {msg}", flush=True)

    budget_str = (f"{max_time:.0f}s" if max_time is not None
                  else f"{max_tokens} tokens")
    log(f"starting (model={model}, budget={budget_str})")

    # Streaming callback (used by MistralClient if stream=True)
    dim = "\033[2m" if sys.stdout.isatty() else ""
    reset = "\033[0m" if sys.stdout.isatty() else ""
    state = {"in_thinking": False}

    def stream_cb(text: str, kind: str):
        if kind == "thinking":
            if not state["in_thinking"]:
                sys.stdout.write(dim)
                state["in_thinking"] = True
        else:
            if state["in_thinking"]:
                sys.stdout.write(reset)
                state["in_thinking"] = False
        sys.stdout.write(text)
        sys.stdout.flush()

    try:
        while True:
            elapsed = time.monotonic() - start
            if max_time is not None and elapsed >= max_time:
                log(f"time budget exhausted after {turns} turns, "
                    f"{verifications} verifications, {tokens} tokens")
                break
            if max_tokens is not None and tokens >= max_tokens:
                log(f"token budget exhausted after {turns} turns, "
                    f"{verifications} verifications, {tokens} tokens")
                break

            turns += 1

            # With conversation_id the server keeps context — only send
            # the latest user feedback.  Without it, join the full
            # transcript into one prompt (Claude path).
            if use_conv_id and conversation_id is not None:
                prompt = transcript[-1]   # just the new feedback
            else:
                prompt = "\n\n".join(transcript)

            call_kwargs: dict = dict(
                prompt=prompt,
                system_prompt=SYSTEM_PROMPT,
                label=f"baseline-{name}-t{turns}",
            )
            if use_conv_id and conversation_id is not None:
                call_kwargs["conversation_id"] = conversation_id

            def _call_with_retry(**extra):
                transient_backoff = 4
                while True:
                    try:
                        return client.call(**call_kwargs, **extra)
                    except RuntimeError as e:
                        if is_rate_limited_error(e):
                            log(f"turn {turns}: rate/spending limit hit: "
                                f"{str(e).splitlines()[0][:200]}")
                            log(f"turn {turns}: waiting "
                                f"{RATE_LIMIT_WAIT // 60}m before retry")
                            time.sleep(RATE_LIMIT_WAIT)
                            continue
                        if is_transient_error(e):
                            log(f"turn {turns}: transient error: "
                                f"{str(e).splitlines()[0][:200]}")
                            log(f"turn {turns}: waiting {transient_backoff}s "
                                f"before retry")
                            time.sleep(transient_backoff)
                            transient_backoff = min(transient_backoff * 2, 60)
                            continue
                        raise

            if stream:
                print(f"\n  ─── turn {turns} ───", flush=True)
                resp = _call_with_retry(stream_callback=stream_cb)
                if state["in_thinking"]:
                    sys.stdout.write(reset)
                    state["in_thinking"] = False
                print(flush=True)
            else:
                resp = _call_with_retry()

            # Capture conversation_id from the first response so
            # subsequent turns continue the same server-side context.
            if use_conv_id and conversation_id is None:
                conversation_id = resp.get("conversation_id")

            assistant_text = resp.get("result", "") or ""
            thinking_text = resp.get("thinking", "") or ""

            # Track completion tokens (use API usage if available, else
            # approximate via char count / 4 — works for streaming path
            # which doesn't expose usage).
            usage = (resp.get("raw") or {}).get("usage") or {}
            turn_tokens = (usage.get("completion_tokens")
                          or usage.get("output_tokens"))
            if turn_tokens is None:
                turn_tokens = (len(assistant_text) + len(thinking_text)) // 4
            tokens += turn_tokens

            # Outcome of this turn is filled in below; we write the turn
            # log + transcript chunk once we know it.
            turn_outcome: dict = {
                "prompt": prompt,
                "thinking": thinking_text,
                "reply": assistant_text,
                "turn_tokens": turn_tokens,
                "outcome": "",        # "ok" / "verify_failed" / "no_block" / "rejected"
                "feedback": "",
                "spliced": "",
            }

            def _flush_turn():
                _write_turn_log(turns_dir / f"turn_{turns:03d}.md",
                                turn=turns, **turn_outcome)
                _append_transcript(_format_turn_for_transcript(
                    turn=turns, **turn_outcome))
                # Also drop bare .lean / .err files alongside the .md so
                # the spliced source and compiler output are easy to find
                # with `ls`/`grep`, mirroring openprover's lean/ layout.
                if turn_outcome["spliced"]:
                    (turns_dir / f"turn_{turns:03d}.lean").write_text(
                        turn_outcome["spliced"] + "\n")
                if turn_outcome["feedback"] and turn_outcome["outcome"] != "ok":
                    (turns_dir / f"turn_{turns:03d}.err").write_text(
                        turn_outcome["feedback"] + "\n")

            blocks = _extract_lean_blocks(assistant_text)
            # Take the LAST `num_sorries` blocks (matches the system prompt:
            # the model puts its final attempt at the end).
            replacements = blocks[-parsed.num_sorries:] if blocks else []

            if len(replacements) != parsed.num_sorries:
                log(f"turn {turns}: expected {parsed.num_sorries} ```lean "
                    f"block(s), got {len(blocks)} "
                    f"(reply: {len(assistant_text)} chars, "
                    f"{turn_tokens} tokens)")
                turn_outcome["outcome"] = "no_block"
                turn_outcome["feedback"] = (
                    f"Expected {parsed.num_sorries} ```lean ... ``` block(s), "
                    f"got {len(blocks)}."
                )
                _flush_turn()
                feedback_msg = (
                    f"Expected {parsed.num_sorries} ```lean ... ``` "
                    f"code fence(s) (one per `sorry`), got {len(blocks)}. "
                    "Output exactly the right number of fenced blocks, in "
                    "order, each containing only the proof body that "
                    "replaces the corresponding `sorry`."
                )
                if use_conv_id:
                    # Server has the assistant reply; just queue feedback.
                    transcript.append(feedback_msg)
                else:
                    transcript.append(
                        f"# Assistant turn {turns}\n{assistant_text}\n\n"
                        f"# User\n{feedback_msg}"
                    )
                continue

            # Re-indent each replacement so multi-line proof bodies sit
            # under the column where `sorry` appeared. Without this, only
            # the first line inherits the existing indent and Lean closes
            # the `by` block at the next line that starts at column 0.
            indented_replacements = [
                _reindent(rep, _sorry_column(parsed.raw_text, start))
                for rep, (start, _) in zip(replacements, parsed.sorry_positions)
            ]

            # Splice into the original theorem. assemble_proof rejects
            # banned constructs (sorry, axiom, import, ...).
            try:
                full_code = parsed.assemble_proof(indented_replacements)
            except ValueError as e:
                log(f"turn {turns}: assembly rejected: {e}")
                turn_outcome["outcome"] = "rejected"
                turn_outcome["feedback"] = str(e)
                _flush_turn()
                feedback_msg = (
                    f"Your proof block was rejected: {e}. "
                    "Output a fresh ```lean ... ``` block containing only "
                    "the proof body."
                )
                if use_conv_id:
                    transcript.append(feedback_msg)
                else:
                    transcript.append(
                        f"# Assistant turn {turns}\n{assistant_text}\n\n"
                        f"# User\n{feedback_msg}"
                    )
                continue

            verifications += 1
            log(f"turn {turns}: verifying ({sum(len(r) for r in replacements)}"
                f" chars of proof, {turn_tokens} tokens this turn, {tokens} total)")
            if not quiet:
                # Show the spliced source verbatim so the user can see
                # exactly what the verifier is checking.
                for line in full_code.splitlines():
                    print(f"  │ {line}", flush=True)
            verify_start = time.monotonic()
            success, feedback = _verify(full_code, work_dir, lean_project_dir)
            verify_secs = time.monotonic() - verify_start

            turn_outcome["spliced"] = full_code
            turn_outcome["feedback"] = feedback

            if success:
                proved = True
                (run_dir / "PROOF.lean").write_text(full_code + "\n")
                log(f"turn {turns}: lean_verify #{verifications} -> OK "
                    f"({verify_secs:.1f}s)")
                log(f"PROVED in {turns} turns, {verifications} verifications, "
                    f"{tokens} tokens, {time.monotonic() - start:.0f}s")
                turn_outcome["outcome"] = "ok"
                _flush_turn()
                break

            log(f"turn {turns}: lean_verify #{verifications} -> failed "
                f"({verify_secs:.1f}s)")
            turn_outcome["outcome"] = "verify_failed"
            _flush_turn()

            if stream:
                # Show the compiler feedback in interactive mode so the user
                # can follow along.
                preview = feedback.strip()
                if len(preview) > 1500:
                    preview = preview[:1500] + "\n  ... (truncated)"
                for line in preview.splitlines():
                    print(f"  │ {line}", flush=True)

            feedback_msg = (
                f"lean_verify failed:\n```\n{feedback}\n```\n"
                "Try again. Output the full Lean source inside a "
                "```lean ... ``` code fence."
            )
            if use_conv_id:
                transcript.append(feedback_msg)
            else:
                transcript.append(
                    f"# Assistant turn {turns}\n{assistant_text}\n\n"
                    f"# User\n{feedback_msg}"
                )

    except Exception as e:
        elapsed = time.monotonic() - start
        log(f"error: {e}")
        (run_dir / "log.txt").write_text("\n".join(log_lines) + "\n")
        return {"status": "error", "elapsed": elapsed, "turns": turns,
                "verifications": verifications, "tokens": tokens, "error": str(e)}

    elapsed = time.monotonic() - start
    status = "proved" if proved else "not_proved"
    (run_dir / "log.txt").write_text("\n".join(log_lines) + "\n")
    (run_dir / "result.json").write_text(json.dumps({
        "name": name, "status": status, "elapsed": elapsed,
        "turns": turns, "verifications": verifications, "tokens": tokens,
    }, indent=2) + "\n")
    _append_transcript(
        f"\n## Result\n\n"
        f"- status: **{status}**\n"
        f"- elapsed: {elapsed:.0f}s\n"
        f"- turns: {turns}\n"
        f"- verifications: {verifications}\n"
        f"- tokens: {tokens}\n"
    )

    return {"status": status, "elapsed": elapsed, "turns": turns,
            "verifications": verifications, "tokens": tokens, "error": ""}


# ── CLI ──────────────────────────────────────────────────────────────

def _main():
    parser = argparse.ArgumentParser(
        prog="baseline",
        description="Baseline Lean prover: single conversation, no tools",
    )
    parser.add_argument("run_dir", nargs="?",
                        help="Working directory (auto-created under runs/ if omitted)")
    parser.add_argument("--theorem", type=Path, metavar="FILE",
                        help="Path to informal theorem statement (.md)")
    parser.add_argument("--lean-theorem", type=Path, metavar="FILE", required=True,
                        help="Path to formal theorem stub (.lean)")
    parser.add_argument("--lean-project", type=Path, metavar="DIR", required=True,
                        help="Path to Lean project with built .lake (lake build first)")
    parser.add_argument("--model", default="leanstral",
                        help="Model name (default: leanstral)")
    budget = parser.add_mutually_exclusive_group()
    budget.add_argument("--max-time", default=None, metavar="DURATION",
                        help="Wall-clock budget per problem (e.g. '10m', '2h')")
    budget.add_argument("--max-tokens", type=int, default=None, metavar="N",
                        help="Output token budget per problem")
    parser.add_argument("--stream", action=argparse.BooleanOptionalAction,
                        default=False,
                        help="Stream model output to console "
                             "(thinking shown dimmed)")
    args = parser.parse_args()

    if args.max_time is None and args.max_tokens is None:
        args.max_time = "10m"  # default

    if not args.lean_theorem.is_file():
        parser.error(f"--lean-theorem not found: {args.lean_theorem}")
    if not args.lean_project.is_dir():
        parser.error(f"--lean-project not found: {args.lean_project}")
    if not (args.lean_project / ".lake").is_dir():
        parser.error(f"{args.lean_project / '.lake'} not found — run `lake build` first")
    if args.theorem and not args.theorem.is_file():
        parser.error(f"--theorem not found: {args.theorem}")

    theorem_lean = args.lean_theorem.read_text()
    theorem_informal = args.theorem.read_text() if args.theorem else ""

    name_match = re.search(r"^theorem\s+(\S+)", theorem_lean, re.MULTILINE)
    name = name_match.group(1) if name_match else args.lean_theorem.stem

    if args.run_dir:
        run_dir = Path(args.run_dir)
    else:
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        run_dir = Path("runs") / f"baseline-{_slugify(name)}-{ts}"
        counter = 1
        while run_dir.exists():
            counter += 1
            run_dir = Path("runs") / f"baseline-{_slugify(name)}-{ts}-{counter}"

    budget_secs = _parse_duration(args.max_time) if args.max_time else None

    print(f"Theorem:  {name}")
    print(f"Model:    {args.model}")
    if budget_secs is not None:
        print(f"Budget:   {args.max_time} ({budget_secs:.0f}s)")
    else:
        print(f"Budget:   {args.max_tokens} tokens")
    print(f"Run dir:  {run_dir}")
    print("─" * 60)

    result = run_baseline(
        name=name,
        theorem_lean=theorem_lean,
        theorem_informal=theorem_informal,
        lean_project_dir=args.lean_project.resolve(),
        model=args.model,
        max_time=budget_secs,
        max_tokens=args.max_tokens,
        run_dir=run_dir,
        stream=args.stream,
    )

    print("─" * 60)
    print(f"Result:        {result['status']}")
    print(f"Elapsed:       {result['elapsed']:.0f}s")
    print(f"Turns:         {result['turns']}")
    print(f"Verifications: {result['verifications']}")
    print(f"Tokens:        {result['tokens']}")
    if result.get("error"):
        print(f"Error:         {result['error']}")
    raise SystemExit(0 if result["status"] == "proved" else 1)


if __name__ == "__main__":
    _main()
