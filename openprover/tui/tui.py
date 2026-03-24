"""Terminal UI for OpenProver - ANSI scroll regions, fixed header, tabs."""

import atexit
import queue
import shutil
import signal
import sys
import termios
import threading
import tty

from ._colors import DIM, RESET, HEADER_ROWS
from ._types import _LogEntry, _Tab
from ._text import TextMixin
from ._stream import StreamMixin
from ._nav import NavMixin
from ._tabs import TabsMixin
from ._steps import StepsMixin
from ._input import InputMixin
from ._render import RenderMixin


class TUI(TextMixin, StreamMixin, NavMixin, TabsMixin, StepsMixin,
          InputMixin, RenderMixin):
    supports_streaming = True

    def __init__(self):
        self.rows = 0
        self.cols = 0
        self._resize_pending = False
        self.trace_visible = True
        self.view = "whiteboard_split"
        self.whiteboard = ""
        self.wb_scroll_offset = 0
        self.autonomous = False
        self._old_termios = None
        self._active = False
        self.theorem_name = ""
        self.step_num = 0
        self.budget_status = ""
        self._budget_ref = None  # Budget object reference for live updates
        self._old_sigwinch = None
        # Background key reader
        self._key_queue: queue.Queue[str] = queue.Queue()
        self._bg_thread: threading.Thread | None = None
        self._bg_stop = False
        self._split_dirty = False
        # Step history includes action/summary/detail plus status flags/feedback.
        self.step_entries: list[dict] = []
        self._nav_step = -1  # -1 = options focused, 0..N-1 = step index
        self._nav_proposal = False  # True = proposed action is selected
        self._current_proposal: list[dict] | dict | None = None  # stored by show_proposal
        self._step_detail_text = ""
        self._step_detail_title = ""
        self._step_detail_idx = -1
        self._step_detail_scroll = 0
        self._input_scroll = 0
        # Confirmation state
        self._confirming = False
        self._browsing = False
        self._confirm_accept_label = "accept"
        self._confirm_selected = 0
        self._confirm_buf: list[str] = []
        self._confirm_cursor: int = 0
        # Thread safety for stdout
        self._write_lock = threading.Lock()
        self._key_process_lock = threading.Lock()
        self._ctrl_c_cb = None  # Called directly from bg thread on ctrl+c
        # Frame buffer: when not None, _write_raw appends here instead of stdout
        self._buf: list[str] | None = None
        # Tabs
        self.tabs: list[_Tab] = [_Tab("planner", "Planner"), _Tab("logs", "Logs")]
        self.tabs[0].view = "whiteboard_split"  # planner tab shows whiteboard by default
        self.active_tab_idx = 0
        # Saved worker tabs (when navigating history)
        self._saved_worker_tabs: list[_Tab] | None = None
        # Proposal log range (for cleanup after confirmation)
        self._proposal_log_start: int = -1
        # Transient feedback/replan notice in planner tab.
        self._replan_notice_entry: _LogEntry | None = None
        # Run parameters (shown in help view)
        self.run_params: dict[str, str] = {}

    _content_start = HEADER_ROWS + 1

    @property
    def _active_tab(self) -> _Tab:
        if self.active_tab_idx < len(self.tabs):
            return self.tabs[self.active_tab_idx]
        return self.tabs[0]

    @property
    def _main_visible(self) -> bool:
        return self.view in ("main", "whiteboard_split")

    def _find_tab(self, tab_id: str) -> _Tab:
        for tab in self.tabs:
            if tab.id == tab_id:
                return tab
        return self.tabs[0]

    def _find_tab_or_none(self, tab_id: str) -> _Tab | None:
        for tab in self.tabs:
            if tab.id == tab_id:
                return tab
        return None

    def setup(self, theorem_name: str, work_dir: str,
              step_num: int = 0,
              model_name: str = ""):
        self.theorem_name = theorem_name
        self.work_dir = work_dir
        self.step_num = step_num
        self.model_name = model_name
        size = shutil.get_terminal_size()
        self.cols, self.rows = size.columns, size.lines

        try:
            self._old_termios = termios.tcgetattr(sys.stdin)
            tty.setcbreak(sys.stdin.fileno())
        except (termios.error, OSError):
            self._old_termios = None

        with self._write_lock:
            self._write_raw('\033[?1049h\033[2J\033[?1000h\033[?1006h')
            self._draw_header()
            self._write_raw(self._scroll_region_seq())
            sys.stdout.flush()
        self._write(f'\033[{self._content_start};1H\033[?25l')
        self._active = True

        # Ensure cursor and terminal are restored even on abnormal exit
        atexit.register(self.cleanup)

        self._old_sigwinch = signal.getsignal(signal.SIGWINCH)
        signal.signal(signal.SIGWINCH, self._on_resize)

        self._bg_stop = False
        self._bg_thread = threading.Thread(target=self._bg_loop, daemon=True)
        self._bg_thread.start()

    def cleanup(self):
        if not self._active:
            return
        self._active = False
        self._bg_stop = True
        if self._bg_thread:
            self._bg_thread.join(timeout=0.2)
            self._bg_thread = None
        self._write('\033[?1000l\033[?1006l\033[r\033[?1049l\033[?25h')
        if self._old_termios:
            try:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self._old_termios)
            except (termios.error, OSError):
                pass
            self._old_termios = None
        if self._old_sigwinch is not None:
            try:
                signal.signal(signal.SIGWINCH, self._old_sigwinch)
            except (OSError, ValueError):
                pass

    def _on_resize(self, signum, frame):
        self._resize_pending = True

    def _apply_resize(self):
        self._resize_pending = False
        size = shutil.get_terminal_size()
        self.cols = max(size.columns, 1)
        self.rows = max(size.lines, 1)
        self._write('\033[2J')
        self._write(self._scroll_region_seq())
        self._redraw()

    def _scroll_region_seq(self) -> str:
        if self.rows < self._content_start:
            return '\033[r'
        return f'\033[{self._content_start};{self.rows}r'

    # ── Low-level output ────────────────────────────────────────

    def _write(self, data: str):
        with self._write_lock:
            sys.stdout.write(data)
            sys.stdout.flush()

    def _write_raw(self, data: str):
        """Write without lock - caller must hold _write_lock."""
        if self._buf is not None:
            self._buf.append(data)
        else:
            sys.stdout.write(data)

    # ── Step counter ────────────────────────────────────────────

    def update_step(self, step_num: int):
        self.step_num = step_num
        if self._budget_ref:
            self.budget_status = self._budget_ref.status_str()
        with self._write_lock:
            self._buf = []
            self._write_raw('\033[s')
            self._draw_header()
            self._write_raw('\033[u')
            frame = "".join(self._buf)
            self._buf = None
            sys.stdout.write(frame)
            sys.stdout.flush()

    def update_budget(self, status: str):
        self.budget_status = status
        if not self._active:
            return
        with self._write_lock:
            self._buf = []
            self._write_raw('\033[s')
            self._draw_header()
            self._write_raw('\033[u')
            frame = "".join(self._buf)
            self._buf = None
            sys.stdout.write(frame)
            sys.stdout.flush()

    # ── Logging ─────────────────────────────────────────────────

    def _tab_log(self, tab: _Tab, text: str, step_idx: int = -1):
        entry = _LogEntry(text, step_idx)
        tab.log_lines.append(entry)
        if len(tab.log_lines) > 500:
            tab.log_lines = tab.log_lines[-500:]
        if tab is self._active_tab and self._main_visible:
            if self.view == "whiteboard_split":
                self._split_dirty = True
            elif tab.scroll_offset > 0:
                pass  # Stay where we are; new content is at the bottom
            else:
                self._write(f' {text}\n')

    def log(self, text: str, color: str = "", bold: bool = False, dim: bool = False):
        self._tab_log(self.tabs[0], self._style(text, color, bold, dim))

    def tab_log(self, tab_id: str, text: str, color: str = "", dim: bool = False):
        """Log a line to a specific tab."""
        tab = self._find_tab(tab_id)
        self._tab_log(tab, self._style(text, color, dim=dim))

    def log_trace(self, text: str):
        """Log a trace message to the logs tab (dim style)."""
        tab = self._find_tab("logs")
        if tab.id == "logs":
            self._tab_log(tab, f'{DIM}{text}{RESET}')
