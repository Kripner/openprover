"""Data classes for TUI log entries and tabs."""


class _LogEntry:
    """A line in the log. step_idx >= 0 marks completed-step lines."""
    __slots__ = ("text", "step_idx", "is_trace", "is_output")

    def __init__(self, text: str, step_idx: int = -1, is_trace: bool = False,
                 is_output: bool = False):
        self.text = text
        self.step_idx = step_idx
        self.is_trace = is_trace
        self.is_output = is_output


class _Tab:
    """A tab with its own log buffer and streaming state."""
    __slots__ = ("id", "label", "log_lines", "trace_buf", "output_buf",
                 "stream_segments",
                 "scroll_offset", "view",
                 "streaming", "spinner_label", "spinner_tick", "spinner_time",
                 "spinner_start", "spinner_tokens", "last_trace", "last_output",
                 "toml_pending", "toml_close_tag", "output_non_toml_seen",
                 "output_toml_seen", "show_toml", "is_waiting",
                 "done", "task_description", "task_summary",
                 "worker_task", "worker_output",
                 "entries", "nav_idx",
                 "pending_actions")

    def __init__(self, tab_id: str, label: str, task_description: str = ""):
        self.id = tab_id
        self.label = label
        self.log_lines: list[_LogEntry] = []
        self.trace_buf: list[str] = []
        self.output_buf: list[str] = []
        # Ordered segments preserving think/output interleaving:
        # each element is (kind, chunks) where kind is "thinking" or "text"
        self.stream_segments: list[tuple[str, list[str]]] = []
        self.scroll_offset = 0
        self.view = "main"
        self.streaming = False
        self.spinner_label = ""
        self.spinner_tick = 0
        self.spinner_time = 0.0
        self.spinner_start = 0.0
        self.spinner_tokens = 0
        self.last_trace = ""
        self.last_output = ""
        self.toml_pending = ""
        self.toml_close_tag = ""
        self.output_non_toml_seen = False
        self.output_toml_seen = False
        self.show_toml = False
        self.is_waiting = False
        self.done = False
        self.task_description = task_description
        self.task_summary = ""     # short summary from spawn action
        self.worker_task = ""      # for verifier tabs: the original worker's task
        self.worker_output = ""    # for verifier tabs: the worker's output being verified
        # Navigable entries (action entries for worker tabs)
        self.entries: list[dict] = []
        self.nav_idx: int = -1  # -1 = none selected, 0..N-1 = entry index
        # In-progress action tracking: entry_idx → log_line_idx
        self.pending_actions: dict[int, int] = {}
