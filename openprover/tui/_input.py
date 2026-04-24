"""Key handling, confirmation, and interrupt handling for the TUI."""

import os
import queue
import select
import sys
import time as _time

from ._colors import DIM, GREEN, RESET


class InputMixin:

    def _bg_loop(self):
        fd = sys.stdin.fileno()
        _last_budget_refresh = 0.0
        while not self._bg_stop:
            try:
                if self._resize_pending:
                    self._apply_resize()

                self._advance_tab_spinners()
                tab = self._active_tab
                if tab.spinner_label and tab.streaming:
                    self._update_spinner()

                if self._split_dirty:
                    self._split_dirty = False
                    self._redraw()

                # Live-update budget display for time mode (~1s interval)
                budget = getattr(self, '_budget_ref', None)
                if budget and budget.mode == "time":
                    now = _time.monotonic()
                    if now - _last_budget_refresh >= 1.0:
                        _last_budget_refresh = now
                        self.update_budget(budget.status_str())

                # Process queued keys when idle (no streaming, no confirmation)
                if not self._confirming and not tab.streaming:
                    if not self._key_queue.empty():
                        self._check_keys()

                if not select.select([fd], [], [], 0.04)[0]:
                    continue
                data = os.read(fd, 32)
                if not data:
                    continue

                i = 0
                while i < len(data):
                    b = data[i]
                    if b == 0x1b:
                        if i + 2 < len(data) and data[i + 1] == 0x5b:
                            # SGR mouse: \033[<Btn;Col;RowM/m
                            if data[i + 2] == 0x3c:
                                j = i + 3
                                while j < len(data) and data[j] not in (0x4d, 0x6d):
                                    j += 1
                                if j < len(data):
                                    try:
                                        params = data[i+3:j].decode('ascii')
                                        btn = int(params.split(';')[0])
                                        if btn in (64, 65):
                                            key = 'scroll_up' if btn == 64 else 'scroll_down'
                                            if self._can_handle_directly():
                                                self._process_key(key)
                                            else:
                                                self._key_queue.put(key)
                                    except (ValueError, IndexError):
                                        pass
                                    i = j + 1
                                else:
                                    i = len(data)
                                continue
                            # Check for CSI N ~ sequences (Page Up/Down etc.)
                            if (i + 3 < len(data)
                                    and 0x30 <= data[i + 2] <= 0x39
                                    and data[i + 3] == 0x7e):
                                seq = chr(0x1b) + '[' + chr(data[i + 2]) + '~'
                                if self._can_handle_directly() and seq in ('\x1b[5~', '\x1b[6~'):
                                    self._process_key(seq)
                                else:
                                    self._key_queue.put(seq)
                                i += 4
                                continue
                            # Arrow keys - handle directly during streaming
                            arrow = chr(data[i + 2])
                            seq = chr(0x1b) + '[' + arrow
                            if self._can_handle_directly() and arrow in ('A', 'B', 'C', 'D'):
                                self._process_key(seq)
                                i += 3
                                continue
                            self._key_queue.put(seq)
                            i += 3
                            continue
                        if self._can_handle_directly() and self.view != "main":
                            self.view = "main"
                            self._redraw()
                        else:
                            self._key_queue.put('\x1b')
                        i += 1
                        continue

                    ch = chr(b)
                    if ch == '\x03':
                        cb = getattr(self, '_ctrl_c_cb', None)
                        if cb and not self._confirming:
                            cb()
                        else:
                            self._key_queue.put(ch)
                        i += 1
                        continue
                    if self._can_handle_directly():
                        if ch in ('r', 'd', 'w', '?', 'a'):
                            self._process_key(ch)
                            i += 1
                            continue
                        if ch in ('\n', '\r') and (
                            self.view not in ("main", "whiteboard_split")
                            or self._active_tab.scroll_offset > 0
                            or self._active_tab.nav_idx >= 0
                            or self._nav_step >= 0
                            or self._nav_proposal
                        ):
                            self._process_key(ch)
                            i += 1
                            continue

                    self._key_queue.put(ch)
                    i += 1
            except (OSError, ValueError):
                break

    def _can_handle_directly(self) -> bool:
        return self._active_tab.streaming and not self._confirming

    # ── Key handling ────────────────────────────────────────────

    def _check_keys(self):
        if not self._key_process_lock.acquire(blocking=False):
            return
        try:
            while True:
                try:
                    ch = self._key_queue.get_nowait()
                except queue.Empty:
                    break
                self._process_key(ch)
        finally:
            self._key_process_lock.release()

    def _process_key(self, ch: str):
        if ch == 'r':
            self._toggle_trace()
        elif ch == 'd':
            if self.active_tab_idx > 0:
                self._toggle_view("detail")
        elif ch == 'w':
            if self.active_tab_idx == 0:
                if self.view == "main":
                    self.view = "whiteboard_split"
                elif self.view == "whiteboard_split":
                    self.view = "whiteboard"
                elif self.view == "whiteboard":
                    self.view = "main"
                else:
                    self.view = "whiteboard_split"
                self._redraw()
        elif ch == '?':
            self._toggle_view("help")
        elif ch == 'a':
            self.autonomous = not self.autonomous
            self._redraw()
        elif ch == '\x1b[C':  # right arrow - next tab
            self._switch_tab(1)
        elif ch == '\x1b[D':  # left arrow - prev tab
            self._switch_tab(-1)
        elif ch == '\x1b[5~':
            self._scroll_up()
        elif ch == '\x1b[6~':
            self._scroll_down()
        elif ch == '\x1b[A':  # up arrow - navigate entries
            if self._main_visible:
                tab = self._active_tab
                if tab.id == "planner" and self.step_entries:
                    self._nav_up()
                    self._redraw()
                elif tab.entries:
                    self._tab_nav_up(tab)
                    self._redraw()
                else:
                    self._scroll_lines_up()
            else:
                self._scroll_lines_up()
        elif ch == '\x1b[B':  # down arrow - navigate entries
            if self._main_visible:
                tab = self._active_tab
                if tab.id == "planner" and self.step_entries:
                    self._nav_down()
                    self._redraw()
                elif tab.entries:
                    self._tab_nav_down(tab)
                    self._redraw()
                else:
                    self._scroll_lines_down()
            else:
                self._scroll_lines_down()
        elif ch == 'scroll_up':
            self._scroll_lines_up()
        elif ch == 'scroll_down':
            self._scroll_lines_down()
        elif ch == '\x1b':
            if self.view != "main":
                self.view = "main"
                self._redraw()
            elif self._nav_step >= 0:
                self._nav_step = -1
                self._restore_worker_tabs()
                self._redraw()
            elif self._nav_proposal:
                self._nav_proposal = False
                self._redraw()
            elif self._active_tab.nav_idx >= 0:
                self._active_tab.nav_idx = -1
                self._redraw()
        elif ch in ('\n', '\r'):
            if self.view not in ("main", "whiteboard_split"):
                self.view = "main"
                self._redraw()
            elif self._active_tab.nav_idx >= 0 and self._active_tab.id != "planner":
                self._open_selected_action_detail()
                self._redraw()
            elif self._nav_step >= 0:
                self._open_selected_step_detail()
                self._redraw()
            elif self._nav_proposal:
                self._open_proposal_detail()
                self._redraw()
            elif self._active_tab.nav_idx >= 0:
                self._open_selected_action_detail()
                self._redraw()
            elif self._active_tab.scroll_offset > 0:
                self._active_tab.scroll_offset = 0
                self._redraw()
    def interrupt(self):
        """Cancel any pending confirmation by injecting ctrl+c into key queue."""
        self._key_queue.put('\x03')

    # ── Confirmation UI ────────────────────────────────────────

    def get_confirmation(self) -> str:
        self._confirming = True
        self._confirm_accept_label = "accept"
        self._confirm_selected = 0
        self._confirm_buf = []
        self._confirm_cursor = 0
        self._nav_step = -1
        self._nav_proposal = False
        self._scroll_selection_into_view()
        self._redraw()
        self._write('\033[?25h')

        try:
            while True:
                try:
                    ch = self._key_queue.get(timeout=0.1)
                except queue.Empty:
                    continue

                # Whether the feedback text field is actively focused
                _in_feedback = (self._confirm_selected == 1
                                and self._nav_step == -1
                                and not self._nav_proposal)

                if ch == '\x1b':
                    if self.view != "main":
                        self.view = "main"
                    elif self._nav_step >= 0:
                        self._nav_step = -1
                        self._restore_worker_tabs()
                        self._scroll_selection_into_view()
                    elif self._nav_proposal:
                        self._nav_proposal = False
                        self._scroll_selection_into_view()
                    else:
                        self._confirm_buf.clear()
                        self._confirm_cursor = 0
                    self._redraw()
                    continue

                if ch in ('scroll_up', 'scroll_down'):
                    if ch == 'scroll_up':
                        self._scroll_lines_up()
                    else:
                        self._scroll_lines_down()
                    continue

                if len(ch) >= 3 and ch[:2] == '\x1b[':
                    if ch == '\x1b[A':
                        if self._nav_step == -1 and not self._nav_proposal:
                            if self._confirm_selected == 0 and (
                                    self.step_entries or self._current_proposal):
                                self._nav_up()
                            else:
                                self._confirm_selected = 0
                                self._scroll_selection_into_view()
                        else:
                            self._nav_up()
                        self._redraw()
                    elif ch == '\x1b[B':
                        if self._nav_step == -1 and not self._nav_proposal:
                            self._confirm_selected = 1 - self._confirm_selected
                            self._scroll_selection_into_view()
                        else:
                            self._nav_down()
                        self._redraw()
                    elif ch == '\x1b[C':
                        if _in_feedback and self._confirm_cursor < len(self._confirm_buf):
                            self._confirm_cursor += 1
                            self._redraw()
                        elif not _in_feedback:
                            self._switch_tab(1)
                    elif ch == '\x1b[D':
                        if _in_feedback and self._confirm_cursor > 0:
                            self._confirm_cursor -= 1
                            self._redraw()
                        elif not _in_feedback:
                            self._switch_tab(-1)
                    elif ch == '\x1b[5~':
                        self._scroll_up()
                    elif ch == '\x1b[6~':
                        self._scroll_down()
                    elif _in_feedback and ch == '\x1b[H':
                        self._confirm_cursor = 0
                        self._redraw()
                    elif _in_feedback and ch == '\x1b[F':
                        self._confirm_cursor = len(self._confirm_buf)
                        self._redraw()
                    continue

                if ch in ('\n', '\r'):
                    if self.view not in ("main", "whiteboard_split"):
                        self.view = "main"
                        self._redraw()
                        continue
                    if self._active_tab.nav_idx >= 0 and self._active_tab.id != "planner":
                        self._open_selected_action_detail()
                        self._redraw()
                        continue
                    if self._nav_step >= 0:
                        self._open_selected_step_detail()
                        self._redraw()
                        continue
                    if self._nav_proposal:
                        self._open_proposal_detail()
                        self._redraw()
                        continue
                    if self._confirm_selected == 0:
                        return ""
                    return "".join(self._confirm_buf)

                if ch in ('\x7f', '\x08'):
                    if self._confirm_selected == 1 and self._confirm_cursor > 0:
                        self._confirm_cursor -= 1
                        del self._confirm_buf[self._confirm_cursor]
                        self._redraw()
                    continue

                if ch in ('\x03', '\x04'):
                    return "q"

                if ch == '\t':
                    if self._nav_step >= 0:
                        self._nav_step = -1
                        self._restore_worker_tabs()
                        self._scroll_selection_into_view()
                    elif self._nav_proposal:
                        self._nav_proposal = False
                        self._scroll_selection_into_view()
                    else:
                        self._confirm_selected = 1 - self._confirm_selected
                    self._redraw()
                    continue

                if self._confirm_selected == 0 and ch in ('r', 'd', 'w', '?'):
                    self._process_key(ch)
                    continue

                if ch == 'a' and self._confirm_selected == 0:
                    if self._nav_step >= 0:
                        self._nav_step = -1
                        self._restore_worker_tabs()
                    self._nav_proposal = False
                    self.autonomous = True
                    self._redraw()
                    return "a"

                if ch.isprintable():
                    if self._nav_step >= 0:
                        self._nav_step = -1
                        self._restore_worker_tabs()
                    self._nav_proposal = False
                    if self._confirm_selected == 0:
                        self._confirm_selected = 1
                        self._confirm_cursor = 0
                    self._confirm_buf.insert(self._confirm_cursor, ch)
                    self._confirm_cursor += 1
                    self._redraw()

        finally:
            self._confirming = False
            self._nav_step = -1
            self._restore_worker_tabs()
            self._clear_proposal()
            self._redraw()
            self._write('\033[?25l')

    def show_interrupt_options(self):
        """Show continue / give feedback after CTRL+C interruption."""
        # Drain any stale keys from the queue (including the ctrl+c itself)
        while not self._key_queue.empty():
            try:
                self._key_queue.get_nowait()
            except queue.Empty:
                break

    def get_interrupt_response(self) -> str:
        """Block for user input: '' = continue, 'q' = quit, else = feedback text.

        Feedback is selected by default (unlike get_confirmation where accept is default).
        """
        self._confirming = True
        self._confirm_accept_label = "continue"
        self._confirm_selected = 1  # feedback selected by default
        self._confirm_buf = []
        self._confirm_cursor = 0
        self._nav_step = -1
        self._redraw()
        self._write('\033[?25h')

        try:
            while True:
                try:
                    ch = self._key_queue.get(timeout=0.1)
                except queue.Empty:
                    continue

                _in_feedback = (self._confirm_selected == 1)

                if ch == '\x1b':
                    if self.view != "main":
                        self.view = "main"
                    else:
                        self._confirm_buf.clear()
                        self._confirm_cursor = 0
                    self._redraw()
                    continue

                if ch in ('scroll_up', 'scroll_down'):
                    if ch == 'scroll_up':
                        self._scroll_lines_up()
                    else:
                        self._scroll_lines_down()
                    continue

                if len(ch) >= 3 and ch[:2] == '\x1b[':
                    if ch == '\x1b[A':
                        self._confirm_selected = 0
                        self._redraw()
                    elif ch == '\x1b[B':
                        self._confirm_selected = 1
                        self._redraw()
                    elif ch == '\x1b[C':
                        if _in_feedback and self._confirm_cursor < len(self._confirm_buf):
                            self._confirm_cursor += 1
                            self._redraw()
                        elif not _in_feedback:
                            self._switch_tab(1)
                    elif ch == '\x1b[D':
                        if _in_feedback and self._confirm_cursor > 0:
                            self._confirm_cursor -= 1
                            self._redraw()
                        elif not _in_feedback:
                            self._switch_tab(-1)
                    elif ch == '\x1b[5~':
                        self._scroll_up()
                    elif ch == '\x1b[6~':
                        self._scroll_down()
                    elif _in_feedback and ch == '\x1b[H':
                        self._confirm_cursor = 0
                        self._redraw()
                    elif _in_feedback and ch == '\x1b[F':
                        self._confirm_cursor = len(self._confirm_buf)
                        self._redraw()
                    continue

                if ch in ('\n', '\r'):
                    if self.view not in ("main", "whiteboard_split"):
                        self.view = "main"
                        self._redraw()
                        continue
                    if self._confirm_selected == 0:
                        return ""  # continue
                    return "".join(self._confirm_buf)

                if ch in ('\x7f', '\x08'):
                    if self._confirm_selected == 1 and self._confirm_cursor > 0:
                        self._confirm_cursor -= 1
                        del self._confirm_buf[self._confirm_cursor]
                        self._redraw()
                    continue

                if ch == '\x03':
                    # Second ctrl+c during interrupt prompt → quit
                    return "q"

                if ch == '\t':
                    self._confirm_selected = 1 - self._confirm_selected
                    self._redraw()
                    continue

                if self._confirm_selected == 0 and ch in ('r', 'w', '?'):
                    self._process_key(ch)
                    continue

                if ch.isprintable():
                    if self._confirm_selected == 0:
                        self._confirm_selected = 1
                        self._confirm_cursor = 0
                    self._confirm_buf.insert(self._confirm_cursor, ch)
                    self._confirm_cursor += 1
                    self._redraw()

        finally:
            self._confirming = False
            self._redraw()
            self._write('\033[?25l')

    def browse(self):
        """Interactive browse mode for inspect. Blocks until user presses q."""
        self._confirming = True  # prevent bg_loop from stealing keys
        self._browsing = True
        self._nav_step = -1
        self._nav_proposal = False
        self._redraw()

        try:
            while True:
                try:
                    ch = self._key_queue.get(timeout=0.1)
                except queue.Empty:
                    continue

                if ch in ('q', '\x03', '\x04'):
                    break

                if ch in ('scroll_up', 'scroll_down'):
                    if ch == 'scroll_up':
                        self._scroll_lines_up()
                    else:
                        self._scroll_lines_down()
                    continue

                if len(ch) >= 3 and ch[:2] == '\x1b[':
                    tab = self._active_tab
                    if ch == '\x1b[A':
                        if tab.id == "planner":
                            self._nav_up()
                        elif tab.entries:
                            self._tab_nav_up(tab)
                        self._redraw()
                    elif ch == '\x1b[B':
                        if tab.id == "planner":
                            self._nav_down()
                        elif tab.entries:
                            self._tab_nav_down(tab)
                        self._redraw()
                    elif ch == '\x1b[C':
                        self._switch_tab(1)
                    elif ch == '\x1b[D':
                        self._switch_tab(-1)
                    elif ch == '\x1b[5~':
                        self._scroll_up()
                    elif ch == '\x1b[6~':
                        self._scroll_down()
                    continue

                if ch == '\x1b':
                    if self.view != "main":
                        self.view = "main"
                        self._redraw()
                    elif self._nav_step >= 0:
                        self._nav_step = -1
                        self._restore_worker_tabs()
                        self._redraw()
                    elif self._nav_proposal:
                        self._nav_proposal = False
                        self._redraw()
                    elif self._active_tab.nav_idx >= 0:
                        self._active_tab.nav_idx = -1
                        self._redraw()
                    continue

                if ch in ('\n', '\r'):
                    if self.view not in ("main", "whiteboard_split"):
                        self.view = "main"
                        self._redraw()
                    elif self._active_tab.nav_idx >= 0 and self._active_tab.id != "planner":
                        self._open_selected_action_detail()
                        self._redraw()
                    elif self._nav_step >= 0:
                        self._open_selected_step_detail()
                        self._redraw()
                    elif self._nav_proposal:
                        self._open_proposal_detail()
                        self._redraw()
                    elif self._active_tab.nav_idx >= 0:
                        self._open_selected_action_detail()
                        self._redraw()
                    elif self._active_tab.scroll_offset > 0:
                        self._active_tab.scroll_offset = 0
                        self._redraw()
                    continue

                self._process_key(ch)

        except (KeyboardInterrupt, EOFError):
            pass
        finally:
            self._confirming = False
            self._browsing = False
            self._nav_step = -1
            self._nav_proposal = False
            self._restore_worker_tabs()

    def _toggle_trace(self):
        if self.view == "step_detail":
            old_lines = self._build_step_detail_lines()
            old_max = max(len(old_lines) - self._step_detail_avail_rows(), 0)
            old_ratio = (self._step_detail_scroll / old_max) if old_max > 0 else 0.0
            self.trace_visible = not self.trace_visible
            if self._nav_proposal:
                self._refresh_proposal_detail()
            else:
                self._refresh_step_detail()
            new_lines = self._build_step_detail_lines()
            new_max = max(len(new_lines) - self._step_detail_avail_rows(), 0)
            if old_max > 0 and new_max > 0:
                self._step_detail_scroll = int(round(old_ratio * new_max))
            else:
                self._step_detail_scroll = min(self._step_detail_scroll, new_max)
            self._redraw()
            return

        tab = self._active_tab
        max_w = self._main_lines_max_w()
        old_lines = self._build_main_lines(tab, max_w_override=max_w)
        old_max_off = self._max_scroll_offset(old_lines, tab)
        old_ratio = (tab.scroll_offset / old_max_off) if old_max_off > 0 else 0.0
        self.trace_visible = not self.trace_visible
        new_lines = self._build_main_lines(tab, max_w_override=max_w)
        new_max_off = self._max_scroll_offset(new_lines, tab)
        if old_max_off > 0 and new_max_off > 0:
            tab.scroll_offset = int(round(old_ratio * new_max_off))
        else:
            tab.scroll_offset = min(tab.scroll_offset, new_max_off)
        self._scroll_selection_into_view()
        self._redraw()

    def _toggle_view(self, target: str):
        if self.view == target:
            self.view = "main"
        else:
            self.view = target
            if target == "detail":
                self._input_scroll = 0
        self._redraw()
