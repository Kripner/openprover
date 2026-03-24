"""Non-interactive TUI that prints logs to stdout and errors to stderr."""

import sys


class HeadlessTUI:
    """Non-interactive TUI that prints logs to stdout and errors to stderr."""

    supports_streaming = False

    def __init__(self):
        self._autonomous = True
        self.whiteboard = ""
        self.wb_scroll_offset = 0
        self.step_entries: list[dict] = []
        self.trace_visible = False
        self.budget_status = ""
        self._budget_ref = None

    @property
    def autonomous(self) -> bool:
        return True

    @autonomous.setter
    def autonomous(self, value: bool):
        pass

    def setup(self, theorem_name: str, work_dir: str,
              step_num: int = 0,
              model_name: str = ""):
        print(f"[openprover] {theorem_name}", flush=True)
        print(f"[openprover] {work_dir} | {model_name}", flush=True)

    def cleanup(self):
        pass

    def log(self, text: str, color: str = "", bold: bool = False,
            dim: bool = False):
        if color == "red":
            print(f"[error] {text}", file=sys.stderr, flush=True)
        else:
            print(f"[log] {text}", flush=True)

    def tab_log(self, tab_id: str, text: str, color: str = "",
                dim: bool = False):
        pass

    def log_trace(self, text: str):
        pass

    def stream_start(self, label: str = "thinking", tab: str = "planner"):
        pass

    def stream_text(self, text: str, kind: str = "text",
                    tab: str = "planner"):
        pass

    def stream_end(self, tab: str = "planner"):
        pass

    def step_complete(self, step_num: int,
                      action: str, summary: str, detail: str = "",
                      rejected: bool = False, interrupted: bool = False,
                      feedback: str = "",
                      plans: list[dict] | None = None) -> int:
        suffix = []
        if rejected:
            suffix.append("rejected")
        if interrupted:
            suffix.append("interrupted")
        if feedback.strip():
            suffix.append(f"feedback: {feedback.strip()}")
        tail = f" [{' | '.join(suffix)}]" if suffix else ""
        budget = getattr(self, 'budget_status', '')
        label = f"step {step_num} \u00b7 {budget}" if budget else f"step {step_num}"
        print(f"[{label}] {action} \u2014 {summary}{tail}",
              flush=True)
        idx = len(self.step_entries)
        self.step_entries.append({
            "action": action, "summary": summary,
            "step_num": step_num, "detail": detail,
            "action_output": "",
            "rejected": rejected, "interrupted": interrupted,
            "feedback": feedback.strip(),
        })
        return idx

    def update_step(self, step_num: int):
        pass

    def _sync_step_log_line(self, step_idx: int):
        # The interactive TUI redraws an in-place step status line; headless
        # output is append-only, so there is nothing to synchronize here.
        pass

    def update_budget(self, status: str):
        self.budget_status = status

    def update_step_detail(self, step_idx: int, detail: str):
        if 0 <= step_idx < len(self.step_entries):
            self.step_entries[step_idx]["detail"] = detail

    def update_step_status(
            self,
            step_idx: int,
            *,
            rejected: bool | None = None,
            interrupted: bool | None = None,
            feedback: str | None = None,
            detail_append: str = "",
    ):
        if not (0 <= step_idx < len(self.step_entries)):
            return
        entry = self.step_entries[step_idx]
        if rejected is not None:
            entry["rejected"] = rejected
        if interrupted is not None:
            entry["interrupted"] = interrupted
        if feedback is not None:
            entry["feedback"] = feedback.strip()
        if detail_append:
            base = entry.get("detail", "")
            entry["detail"] = f"{base}\n\n{detail_append}".strip() if base else detail_append

    def append_step_action_output(self, step_num: int, text: str):
        if not text:
            return
        for entry in reversed(self.step_entries):
            if entry.get("step_num") == step_num:
                prev = entry.get("action_output", "")
                entry["action_output"] = (
                    f"{prev}\n\n{text}".strip() if prev else text
                )
                break

    def show_proposal(self, plans: list[dict] | dict):
        pass

    def show_replan_notice(self, text: str):
        print(f"[log] {text}", flush=True)

    def clear_replan_notice(self):
        pass

    def get_confirmation(self) -> str:
        return ""

    def show_interrupt_options(self):
        pass

    def get_interrupt_response(self) -> str:
        return ""

    def add_worker_tab(self, tab_id: str, label: str,
                       task_description: str = ""):
        return None

    def mark_worker_done(self, tab_id: str):
        pass

    def snapshot_worker_tabs(self, step_num: int):
        pass

    def set_waiting_status(self, text: str):
        pass

    def worker_output(self, tab_id: str, text: str):
        pass

    def start_worker_action(self, tab_id: str, tool: str, args: dict):
        print(f"[action] {tool} \u2014 running\u2026", flush=True)

    def add_worker_action(self, tab_id: str, tool: str, args: dict,
                          result: str, status: str, duration_ms: int = 0):
        dur = f" ({duration_ms / 1000:.1f}s)" if duration_ms else ""
        print(f"[action] {tool} \u2014 {status}{dur}", flush=True)

    def clear_worker_tabs(self):
        pass

    def browse(self):
        pass

    def interrupt(self):
        pass
