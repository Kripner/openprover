"""Streaming and spinner display for the TUI."""

import re
import sys
import time

_TOML_TAGS_RE = re.compile(r'</?(?:OPENPROVER_ACTION|TOML_OUTPUT)>\n?')

from ._colors import DIM, GREEN, RESET, SPINNER
from ._types import _LogEntry, _Tab


class StreamMixin:

    @staticmethod
    def _spinner_status(elapsed: int, tokens: int) -> str:
        """Format the elapsed time + token count suffix for spinner display."""
        parts = [f"{elapsed}s"]
        if tokens > 0:
            if tokens >= 1000:
                parts.append(f"{tokens / 1000:.1f}k tok")
            else:
                parts.append(f"{tokens} tok")
        return " · ".join(parts)

    @staticmethod
    def _tab_shows_spinner(tab: _Tab) -> bool:
        return tab.streaming and bool(tab.spinner_label)

    def _update_spinner(self):
        tab = self._active_tab
        now = time.monotonic()
        if self._main_visible:
            if self.view == "whiteboard_split":
                self._split_dirty = True
                return
            ch = SPINNER[tab.spinner_tick]
            elapsed = int(now - tab.spinner_start)
            status = self._spinner_status(elapsed, tab.spinner_tokens)
            with self._write_lock:
                if (not tab.spinner_label
                        or self._has_visible_stream_content(tab)):
                    return
                bar = f' {GREEN}▎{RESET}' if self._spinner_selected(tab) else '  '
                self._write_raw(f'\r\033[2K{bar}{DIM}{ch} {tab.spinner_label} {status}{RESET}')
                sys.stdout.flush()

    # ── Streaming ───────────────────────────────────────────────

    def stream_start(self, label: str = "thinking", tab: str = "planner"):
        target = self._find_tab_or_none(tab)
        if target is None:
            return
        target.trace_buf = []
        target.output_buf = []
        target.stream_segments = []
        target.toml_pending = ""
        target.toml_close_tag = ""
        target.output_non_toml_seen = False
        target.output_toml_seen = False
        target.show_toml = False
        target.streaming = True
        target.is_waiting = False
        target.done = False
        target.spinner_label = label
        target.spinner_tick = 0
        target.spinner_tokens = 0
        target.spinner_time = time.monotonic()
        target.spinner_start = target.spinner_time
        self._redraw_header()
        if target is self._active_tab and self._main_visible:
            if self.view == "whiteboard_split":
                self._split_dirty = True
            else:
                self._write(f'  {DIM}{SPINNER[0]} {label} {self._spinner_status(0, 0)}{RESET}')

    def stream_text(self, text: str, kind: str = "text", tab: str = "planner", show_toml: bool = False):
        self._check_keys()
        target = self._find_tab_or_none(tab)
        if target is None:
            return
        # Ignore stale chunks that arrive after a stream has ended.
        if not target.streaming:
            return
        # Planner should never emit model chunks while just waiting for workers.
        if target.id == "planner" and target.is_waiting:
            return
        if show_toml:
            target.show_toml = True
        target.spinner_tokens += 1
        is_active = target is self._active_tab
        at_bottom = target.scroll_offset == 0
        is_thinking = kind == "thinking"

        # Was there visible content before this chunk?
        had_visible = self._has_visible_stream_content(target)
        had_visible_output = (
            target.output_non_toml_seen
            or (target.output_toml_seen and (self.trace_visible or target.show_toml))
        )

        output_segments: list[tuple[bool, str]] = []
        output_shown = False

        if is_thinking:
            target.trace_buf.append(text)
            # Track interleaved order
            if target.stream_segments and target.stream_segments[-1][0] == "thinking":
                target.stream_segments[-1][1].append(text)
            else:
                target.stream_segments.append(("thinking", [text]))
        else:
            # Update spinner label when transitioning from thinking to action
            if (not self.trace_visible
                    and target.spinner_label == "thinking"
                    and not target.output_buf):
                target.spinner_label = "crafting action"
            target.output_buf.append(text)
            # Track interleaved order
            if target.stream_segments and target.stream_segments[-1][0] == "text":
                target.stream_segments[-1][1].append(text)
            else:
                target.stream_segments.append(("text", [text]))
            output_segments = self._split_toml_stream_segments(target, text)
            for is_toml, seg in output_segments:
                if not seg:
                    continue
                if is_toml:
                    target.output_toml_seen = True
                    if self.trace_visible or show_toml:
                        output_shown = True
                else:
                    target.output_non_toml_seen = True
                    output_shown = True

        has_visible = self._has_visible_stream_content(target)

        # Clear spinner on first visible content
        if (not had_visible and has_visible
                and self._main_visible and is_active and at_bottom):
            if self.view == "whiteboard_split":
                self._split_dirty = True
                return
            with self._write_lock:
                self._write_raw('\r\033[2K')
                sys.stdout.flush()

        trace_needs_newline = (
            output_shown
            and not had_visible_output
            and self.trace_visible
            and bool(target.trace_buf)
            and not target.trace_buf[-1].endswith("\n")
        )

        should_display = (is_thinking and self.trace_visible) or (not is_thinking and output_shown)
        if should_display and self._main_visible and is_active and at_bottom:
            if self.view == "whiteboard_split":
                self._split_dirty = True
                return
            if trace_needs_newline and self.trace_visible:
                self._write("\n")
            if is_thinking:
                self._write(f'{DIM}{text}{RESET}')
            else:
                for is_toml, seg in output_segments:
                    if not seg:
                        continue
                    if is_toml:
                        if self.trace_visible:
                            self._write(f'{DIM}{seg}{RESET}')
                        elif show_toml:
                            clean = _TOML_TAGS_RE.sub('', seg)
                            if clean:
                                self._write(clean)
                    else:
                        self._write(seg)

    def stream_end(self, tab: str = "planner"):
        target = self._find_tab_or_none(tab)
        if target is None:
            return
        target.streaming = False
        target.is_waiting = False
        target.spinner_label = ""

        target.last_trace = "".join(target.trace_buf) if target.trace_buf else ""
        target.last_output = "".join(target.output_buf) if target.output_buf else ""

        # Bake segments in interleaved order to preserve think/output ordering
        for seg_kind, seg_chunks in target.stream_segments:
            joined = "".join(seg_chunks)
            if not joined:
                continue
            if seg_kind == "thinking":
                target.log_lines.append(_LogEntry(joined, is_trace=True))
            else:
                target.log_lines.append(_LogEntry(joined, is_output=True))

        if len(target.log_lines) > 500:
            target.log_lines = target.log_lines[-500:]

        target.trace_buf = []
        target.output_buf = []
        target.stream_segments = []

        is_active = target is self._active_tab
        had_visible = ((target.last_trace and self.trace_visible)
                       or target.last_output)
        if is_active and self._main_visible:
            if self.view == "whiteboard_split" or target.scroll_offset > 0:
                self._redraw()
            else:
                self._write('\r\033[2K')
        self._redraw_header()

    def _spinner_selected(self, tab: _Tab) -> bool:
        """Return True when the spinner line belongs to the currently selected entry."""
        if tab.id == "planner":
            return (self._nav_step >= 0
                    and self.step_entries
                    and self._nav_step == len(self.step_entries) - 1)
        return (tab.nav_idx >= 0
                and tab.entries
                and tab.nav_idx == len(tab.entries) - 1)

    def _advance_tab_spinners(self):
        now = time.monotonic()
        updated = False
        for tab in self.tabs:
            if not self._tab_shows_spinner(tab):
                continue
            if now - tab.spinner_time < 0.08:
                continue
            tab.spinner_time = now
            tab.spinner_tick = (tab.spinner_tick + 1) % len(SPINNER)
            updated = True
        if updated:
            self._redraw_header()

    def _split_toml_stream_segments(self, tab: _Tab,
                                    chunk: str) -> list[tuple[bool, str]]:
        """Stream-safe split that preserves partial TOML tags across chunks."""
        open_to_close = {
            "<TOML_OUTPUT>": "</TOML_OUTPUT>",
            "<OPENPROVER_ACTION>": "</OPENPROVER_ACTION>",
        }
        open_tags = tuple(open_to_close.keys())
        close_tags = tuple(open_to_close.values())
        tags_all = open_tags + close_tags

        data = tab.toml_pending + chunk
        tab.toml_pending = ""
        out: list[tuple[bool, str]] = []
        i = 0

        while i < len(data):
            if tab.toml_close_tag:
                close_tag = tab.toml_close_tag
                close_idx = data.find(close_tag, i)
                if close_idx < 0:
                    tail = data[i:]
                    keep = self._longest_partial_tag_suffix(tail, (close_tag,))
                    emit = tail[:-len(keep)] if keep else tail
                    if emit:
                        out.append((True, emit))
                    tab.toml_pending = keep
                    return out
                end = close_idx + len(close_tag)
                out.append((True, data[i:end]))
                i = end
                tab.toml_close_tag = ""
                continue

            next_open_idx = -1
            next_open_tag = ""
            for open_tag in open_tags:
                idx = data.find(open_tag, i)
                if idx >= 0 and (next_open_idx < 0 or idx < next_open_idx):
                    next_open_idx = idx
                    next_open_tag = open_tag

            if next_open_idx < 0:
                tail = data[i:]
                keep = self._longest_partial_tag_suffix(tail, tags_all)
                emit = tail[:-len(keep)] if keep else tail
                if emit:
                    out.append((False, emit))
                tab.toml_pending = keep
                return out

            if next_open_idx > i:
                out.append((False, data[i:next_open_idx]))

            close_tag = open_to_close[next_open_tag]
            close_idx = data.find(close_tag, next_open_idx + len(next_open_tag))
            if close_idx < 0:
                tab.toml_close_tag = close_tag
                tail = data[next_open_idx:]
                keep = self._longest_partial_tag_suffix(tail, (close_tag,))
                emit = tail[:-len(keep)] if keep else tail
                if emit:
                    out.append((True, emit))
                tab.toml_pending = keep
                return out

            end = close_idx + len(close_tag)
            out.append((True, data[next_open_idx:end]))
            i = end

        return out

    def _has_visible_stream_content(self, tab: _Tab) -> bool:
        if tab.output_non_toml_seen:
            return True
        if tab.output_toml_seen and (self.trace_visible or tab.show_toml):
            return True
        return bool(tab.trace_buf and self.trace_visible)
