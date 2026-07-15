"""Browse LLM prompts and outputs from an OpenProver run directory."""

import os
import re
import signal
import shutil
import sys
import termios
import textwrap
import tty
from pathlib import Path

from .tui._colors import DIM, BOLD, RESET, RED, GREEN, YELLOW, BLUE, CYAN, GRAY

HEADER_ROWS = 3

# Section separator pattern used in archive .md files
_SECTION_RE = re.compile(r'^======== (.+?) ========$', re.MULTILINE)


def find_latest_run() -> Path:
    """Find the most recently modified run directory."""
    runs_dir = Path("runs")
    if not runs_dir.exists():
        print("Error: no runs/ directory found", file=sys.stderr)
        sys.exit(1)
    dirs = [d for d in runs_dir.iterdir() if d.is_dir()]
    if not dirs:
        print("Error: no runs found in runs/", file=sys.stderr)
        sys.exit(1)
    return max(dirs, key=lambda d: d.stat().st_mtime)


def _load_call(path: Path) -> dict | None:
    """Load an LLM call archive file (.md with YAML frontmatter)."""
    if not path.exists():
        return None
    try:
        text = path.read_text()
    except OSError:
        return None

    # Parse markdown format: YAML frontmatter + sections
    data: dict = {}

    # Extract YAML frontmatter
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            fm_text = text[4:end]
            body = text[end + 5:]
            for line in fm_text.splitlines():
                if ": " in line:
                    key, val = line.split(": ", 1)
                    key = key.strip()
                    # Parse numeric values
                    if key in ("call_num", "elapsed_ms", "input_tokens",
                               "output_tokens", "cache_creation_tokens",
                               "cache_read_tokens"):
                        try:
                            data[key] = int(val)
                        except ValueError:
                            data[key] = val
                    elif key == "cost_usd":
                        try:
                            data[key] = float(val)
                        except ValueError:
                            data[key] = val
                    else:
                        data[key] = val
        else:
            body = text
    else:
        body = text

    # Parse sections
    sections: dict[str, str] = {}
    matches = list(_SECTION_RE.finditer(body))
    for i, m in enumerate(matches):
        name = m.group(1)
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        sections[name] = body[start:end].strip()

    # Map sections back to the dict keys that _make_pages expects
    data["system_prompt"] = sections.get("SYSTEM PROMPT", "")
    data["prompt"] = sections.get("USER PROMPT", "")
    data["thinking"] = sections.get("THINKING", "")
    data["result_text"] = sections.get("RESPONSE", "")
    if not data.get("error") and "ERROR" in sections:
        data["error"] = sections["ERROR"]
    # response=None signals "in progress" to _make_pages
    if "RESPONSE" not in sections and "ERROR" not in sections and not data.get("error"):
        data["response"] = None
    else:
        data["response"] = True  # non-None sentinel

    return data


def _format_tokens(data: dict) -> str:
    inp = data.get("input_tokens", 0)
    out = data.get("output_tokens", 0)
    cache_read = data.get("cache_read_tokens", 0)
    cache_create = data.get("cache_creation_tokens", 0)
    parts = []
    if inp:
        parts.append(f"in:{inp}")
    if out:
        parts.append(f"out:{out}")
    if cache_read:
        parts.append(f"cache_r:{cache_read}")
    if cache_create:
        parts.append(f"cache_w:{cache_create}")
    return " ".join(parts)


def _format_cost(data: dict) -> str:
    cost = data.get("cost_usd", 0.0)
    if cost:
        return f"${cost:.4f}"
    return ""


def _format_duration(data: dict) -> str:
    ms = data.get("elapsed_ms", 0)
    if ms:
        return f"{ms / 1000:.1f}s"
    return ""


def _make_pages(data: dict, step: int | str, role: str, label: str) -> list[dict]:
    """Create prompt and output pages from an archive dict."""
    pages = []
    model = data.get("model", "")
    meta_parts = [p for p in [model, _format_duration(data), _format_tokens(data), _format_cost(data)] if p]
    meta = " | ".join(meta_parts)

    sys_prompt = data.get("system_prompt", "")
    user_prompt = data.get("prompt", "")
    prompt_parts = []
    if sys_prompt:
        prompt_parts.append(("dim", "── System Prompt ──\n\n" + sys_prompt))
    if sys_prompt and user_prompt:
        prompt_parts.append(("normal", "\n\n── User Prompt ──\n\n" + user_prompt))
    elif user_prompt:
        prompt_parts.append(("normal", user_prompt))

    pages.append({
        "type": "prompt",
        "step": step,
        "label": f"{label} Prompt",
        "segments": prompt_parts,
        "thinking": "",
        "metadata": meta,
    })

    error = data.get("error")
    result = data.get("result_text", "")
    thinking = data.get("thinking", "")
    response = data.get("response")

    out_segments = []
    if error:
        out_segments.append(("red", f"Error: {error}"))
        if result:
            out_segments.append(("normal", "\n\n" + result))
    elif result:
        out_segments.append(("normal", result))
    elif response is None and not error:
        out_segments.append(("dim", "(in progress - waiting for LLM response)"))
    else:
        out_segments.append(("dim", "(no output)"))

    pages.append({
        "type": "error" if error else "output",
        "step": step,
        "label": f"{label} Output",
        "segments": out_segments,
        "thinking": thinking,
        "metadata": meta,
    })

    return pages


def _make_lean_page(step: int, label: str, lean_code: str, result_text: str) -> dict:
    success = result_text.strip() == "OK"
    segments = [
        ("normal", "```lean\n" + lean_code + "\n```"),
        ("normal", "\n\n── Verification Result ──\n"),
    ]
    if success:
        segments.append(("normal", "OK"))
    else:
        segments.append(("red", result_text))

    return {
        "type": "lean_ok" if success else "lean_err",
        "step": step,
        "label": label,
        "segments": segments,
        "thinking": "",
        "metadata": "OK" if success else "FAILED",
    }


def _load_lean_pages(step_dir: Path, step_num: int) -> list[dict]:
    lean_dir = step_dir / "lean"
    if not lean_dir.exists():
        return []

    pages = []

    item_files = sorted(lean_dir.glob("item_*.lean"))
    for item_path in item_files:
        name = item_path.stem
        parts = name.split("_", 2)
        slug = parts[2] if len(parts) >= 3 else name
        result_path = lean_dir / f"result_{'_'.join(parts[1:])}.txt"
        lean_code = item_path.read_text()
        result_text = result_path.read_text() if result_path.exists() else "(no result)"
        pages.append(_make_lean_page(step_num, f"Lean [[{slug}]]", lean_code, result_text))

    proof_path = lean_dir / "proof_attempt.lean"
    if proof_path.exists():
        lean_code = proof_path.read_text()
        result_path = lean_dir / "proof_result.txt"
        result_text = result_path.read_text() if result_path.exists() else "(no result)"
        pages.append(_make_lean_page(step_num, "Lean Proof Attempt", lean_code, result_text))

    return pages


def load_pages(run_dir: Path) -> list[dict]:
    """Load all pages from a run directory."""
    pages = []
    steps_dir = run_dir / "steps"
    if not steps_dir.exists():
        print(f"Error: no steps/ directory in {run_dir}", file=sys.stderr)
        sys.exit(1)

    step_dirs = sorted(
        [d for d in steps_dir.iterdir() if d.is_dir() and d.name.startswith("step_")]
    )

    for step_dir in step_dirs:
        step_num = int(step_dir.name.removeprefix("step_"))

        planner = _load_call(step_dir / "planner_call.md")
        if planner:
            pages.extend(_make_pages(planner, step_num, "planner", "Planner"))

        retry_idx = 1
        while True:
            retry_data = _load_call(step_dir / f"planner_call_retry_{retry_idx}.md")
            if not retry_data:
                break
            pages.extend(_make_pages(retry_data, step_num, "retry", f"Retry {retry_idx}"))
            retry_idx += 1

        workers_dir = step_dir / "workers"
        if workers_dir.exists():
            worker_idx = 0
            while True:
                worker_data = _load_call(workers_dir / f"worker_{worker_idx}_call.md")
                if not worker_data:
                    break
                pages.extend(_make_pages(worker_data, step_num, "worker", f"Worker {worker_idx}"))
                worker_idx += 1

            search_data = _load_call(workers_dir / "search_call.md")
            if search_data:
                pages.extend(_make_pages(search_data, step_num, "search", "Search"))

        pages.extend(_load_lean_pages(step_dir, step_num))

    discussion = _load_call(run_dir / "discussion_call.md")
    if discussion:
        pages.extend(_make_pages(discussion, "end", "discussion", "Discussion"))

    return pages


class InspectTUI:
    def __init__(self, pages: list[dict], run_dir: Path):
        self.pages = pages
        self.run_dir = run_dir
        self.page_idx = 0
        self.scroll_offset = 0
        self.trace_visible = False
        self.rows = 0
        self.cols = 0
        self._resize_pending = False
        self._old_termios = None
        self._old_sigwinch = None

    def run(self):
        if not self.pages:
            print("No pages to display.")
            return

        size = shutil.get_terminal_size()
        self.cols, self.rows = size.columns, size.lines

        try:
            self._old_termios = termios.tcgetattr(sys.stdin)
            tty.setcbreak(sys.stdin.fileno())
        except (termios.error, OSError):
            self._old_termios = None

        sys.stdout.write("\033[?1049h\033[2J\033[?25l\033[?1000h\033[?1006h")
        sys.stdout.flush()

        self._old_sigwinch = signal.getsignal(signal.SIGWINCH)
        signal.signal(signal.SIGWINCH, self._on_resize)

        try:
            self._draw()
            while True:
                if self._resize_pending:
                    self._apply_resize()
                key = self._read_key()
                if self._resize_pending:
                    self._apply_resize()
                if key in ("q", "\x1b"):
                    break
                elif key == "right":
                    if self.page_idx < len(self.pages) - 1:
                        self.page_idx += 1
                        self.scroll_offset = 0
                        self._draw()
                elif key == "left":
                    if self.page_idx > 0:
                        self.page_idx -= 1
                        self.scroll_offset = 0
                        self._draw()
                elif key == "t":
                    self.trace_visible = not self.trace_visible
                    self._draw()
                elif key in ("down", "j", "scroll_down"):
                    self.scroll_offset += 3
                    self._draw()
                elif key in ("up", "k", "scroll_up"):
                    self.scroll_offset = max(0, self.scroll_offset - 3)
                    self._draw()
                elif key == "pgdn":
                    content_h = self.rows - HEADER_ROWS
                    self.scroll_offset += content_h // 2
                    self._draw()
                elif key == "pgup":
                    content_h = self.rows - HEADER_ROWS
                    self.scroll_offset = max(0, self.scroll_offset - content_h // 2)
                    self._draw()
                elif key == " ":
                    content_h = self.rows - HEADER_ROWS
                    self.scroll_offset += content_h // 2
                    self._draw()
                elif key == "g":
                    self.scroll_offset = 0
                    self._draw()
                elif key == "G":
                    lines = self._render_lines(self.pages[self.page_idx])
                    content_h = self.rows - HEADER_ROWS
                    self.scroll_offset = max(0, len(lines) - content_h)
                    self._draw()
        finally:
            self._cleanup()

    def _on_resize(self, signum, frame):
        self._resize_pending = True

    def _apply_resize(self):
        self._resize_pending = False
        size = shutil.get_terminal_size()
        self.cols = max(size.columns, 1)
        self.rows = max(size.lines, 1)
        self._draw()

    def _cleanup(self):
        sys.stdout.write("\033[?1000l\033[?1006l\033[?1049l\033[?25h")
        sys.stdout.flush()
        if self._old_termios:
            try:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self._old_termios)
            except (termios.error, OSError):
                pass
        if self._old_sigwinch is not None:
            signal.signal(signal.SIGWINCH, self._old_sigwinch)

    def _read_key(self) -> str:
        try:
            ch = os.read(sys.stdin.fileno(), 1).decode("utf-8", errors="replace")
        except InterruptedError:
            return ""
        if ch == "\x1b":
            import select as sel
            if sel.select([sys.stdin], [], [], 0.05)[0]:
                try:
                    ch2 = os.read(sys.stdin.fileno(), 1).decode("utf-8", errors="replace")
                except InterruptedError:
                    return ""
                if ch2 == "[":
                    try:
                        ch3 = os.read(sys.stdin.fileno(), 1).decode("utf-8", errors="replace")
                    except InterruptedError:
                        return ""
                    if ch3 == "A":
                        return "up"
                    elif ch3 == "B":
                        return "down"
                    elif ch3 == "C":
                        return "right"
                    elif ch3 == "D":
                        return "left"
                    elif ch3 == "5":
                        try:
                            os.read(sys.stdin.fileno(), 1)
                        except InterruptedError:
                            return ""
                        return "pgup"
                    elif ch3 == "6":
                        try:
                            os.read(sys.stdin.fileno(), 1)
                        except InterruptedError:
                            return ""
                        return "pgdn"
                    elif ch3 == "<":
                        buf = ""
                        while True:
                            try:
                                c = os.read(sys.stdin.fileno(), 1).decode("utf-8", errors="replace")
                            except InterruptedError:
                                return ""
                            if c in ("M", "m"):
                                break
                            buf += c
                        parts = buf.split(";")
                        if len(parts) >= 1:
                            btn = int(parts[0])
                            if btn == 64:
                                return "scroll_up"
                            elif btn == 65:
                                return "scroll_down"
                        return ""
                    else:
                        while sel.select([sys.stdin], [], [], 0.01)[0]:
                            try:
                                os.read(sys.stdin.fileno(), 1)
                            except InterruptedError:
                                return ""
                return "\x1b"
            return "\x1b"
        return ch

    def _render_lines(self, page: dict) -> list[str]:
        lines = []
        width = self.cols

        if self.trace_visible and page.get("thinking"):
            thinking = page["thinking"]
            lines.append(f"{GRAY}── Reasoning Trace ──{RESET}")
            lines.append("")
            for raw_line in thinking.splitlines():
                wrapped = textwrap.wrap(raw_line, width - 1) if raw_line.strip() else [""]
                for wl in wrapped:
                    lines.append(f"{GRAY}{wl}{RESET}")
            lines.append("")
            lines.append(f"{GRAY}── End Trace ──{RESET}")
            lines.append("")

        style_map = {
            "normal": "",
            "dim": DIM,
            "red": RED,
        }
        for style, text in page.get("segments", []):
            prefix = style_map.get(style, "")
            suffix = RESET if prefix else ""
            for raw_line in text.splitlines():
                wrapped = textwrap.wrap(raw_line, width - 1) if raw_line.strip() else [""]
                for wl in wrapped:
                    lines.append(f"{prefix}{wl}{suffix}")

        return lines

    def _draw(self):
        page = self.pages[self.page_idx]
        content_h = self.rows - HEADER_ROWS
        lines = self._render_lines(page)

        max_scroll = max(0, len(lines) - content_h)
        self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))

        buf = []
        buf.append("\033[2J\033[H")

        step = page["step"]
        step_str = f"Step {step}" if isinstance(step, int) else str(step).capitalize()
        label = page["label"]
        page_type = page["type"]
        if page_type == "error" or page_type == "lean_err":
            type_color = RED
        elif page_type == "prompt":
            type_color = BLUE
        elif page_type == "lean_ok":
            type_color = CYAN
        else:
            type_color = GREEN
        pos = f"[{self.page_idx + 1}/{len(self.pages)}]"
        meta = page.get("metadata", "")
        trace_indicator = f"{YELLOW}[trace on]{RESET}" if self.trace_visible else f"{DIM}[trace off]{RESET}"

        header = f" {BOLD}{step_str}{RESET} {DIM}│{RESET} {type_color}{label}{RESET} {DIM}│{RESET} {pos}"
        if trace_indicator:
            header += f" {trace_indicator}"
        if meta:
            header += f" {DIM}│ {meta}{RESET}"
        buf.append(header)

        scroll_info = ""
        if len(lines) > content_h:
            pct = int(self.scroll_offset / max(1, max_scroll) * 100)
            scroll_info = f" {DIM}scroll:{pct}%{RESET}"
        controls = f" {DIM}←/→ pages  ↑/↓/scroll  t trace  g/G top/bottom  q quit{scroll_info}{RESET}"
        buf.append(controls)

        buf.append(f" {DIM}{'─' * (self.cols - 2)}{RESET}")

        visible = lines[self.scroll_offset:self.scroll_offset + content_h]
        for line in visible:
            buf.append(f" {line}")

        for _ in range(content_h - len(visible)):
            buf.append("")

        sys.stdout.write("\n".join(buf))
        sys.stdout.flush()


def inspect_main(run_dir: str | None = None):
    """Entry point for the inspect subcommand."""
    if run_dir:
        rd = Path(run_dir)
    else:
        rd = find_latest_run()

    if not rd.exists():
        print(f"Error: {rd} does not exist", file=sys.stderr)
        sys.exit(1)

    print(f"Loading {rd.name}...", end="", flush=True)
    pages = load_pages(rd)
    print(f" {len(pages)} pages")

    if not pages:
        print("No LLM calls found.")
        sys.exit(0)

    tui = InspectTUI(pages, rd)
    tui.run()
