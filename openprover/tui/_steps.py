"""Step tracking, proposals, and detail views for the TUI."""

from ._colors import (
    DIM, BOLD, RESET, WHITE, BLUE, GREEN, YELLOW, RED, CYAN, MAGENTA,
    ACTION_STYLE, TOOL_STYLE,
)
from ._types import _LogEntry, _Tab


class StepsMixin:

    def show_proposal(self, plans: list[dict] | dict):
        # Normalize: accept a single dict for backward compat
        if isinstance(plans, dict):
            plans = [plans]
        planner = self.tabs[0]
        self.clear_replan_notice()
        self._current_proposal = plans
        self._proposal_log_start = len(planner.log_lines)
        sep = self._dim_separator()
        self._tab_log(planner, sep)
        label = "Next step:" if len(plans) == 1 else f"Next step ({len(plans)} actions):"
        self._tab_log(planner, f'{DIM}{label}{RESET}')

        for plan in plans:
            self._log_single_proposal(planner, plan)

    def _log_single_proposal(self, planner, plan: dict):
        action = plan.get("action", "")
        summary = plan.get("summary", "")
        color = ACTION_STYLE.get(action, "")
        self._tab_log(planner, f'{color}▸{RESET} {BOLD}{action}{RESET} {DIM}-{RESET} {summary}')

        # Show action-specific details
        if action == "spawn":
            tasks = plan.get("tasks", [])
            for i, task in enumerate(tasks):
                task_summary = task.get("summary", "").strip()
                label = task_summary if task_summary else "(no summary)"
                self._tab_log(planner, f'  {DIM}[{i}]{RESET} {label}')

        elif action == "literature_search":
            query = plan.get("search_query", "")
            context = plan.get("search_context", "")
            if query:
                self._tab_log(planner, f'  {DIM}Query:{RESET}   {query}')
            if context:
                self._tab_log(planner, f'  {DIM}Context:{RESET} {context.strip().splitlines()[0]}')
                for line in context.strip().splitlines()[1:]:
                    self._tab_log(planner, f'          {line}')

        elif action == "write_items":
            items = plan.get("items", [])
            for item in items:
                slug = item.get("slug", "?")
                content = item.get("content", "")
                ext = ".lean" if item.get("format") == "lean" else ".md"
                if content:
                    first_line = content.strip().splitlines()[0] if content.strip() else ""
                    self._tab_log(planner, f'  {DIM}•{RESET} {slug}{ext} {DIM}-- {first_line}{RESET}')
                else:
                    self._tab_log(planner, f'  {DIM}•{RESET} {slug}{ext} {DIM}(delete){RESET}')

        elif action == "read_items":
            slugs = plan.get("read", [])
            if slugs:
                self._tab_log(planner, f'  {DIM}{", ".join(slugs)}{RESET}')

        elif action == "write_whiteboard":
            wb = plan.get("whiteboard", "")
            if wb:
                lines = wb.strip().splitlines()
                for line in lines[:6]:
                    self._tab_log(planner, f'  {DIM}{line}{RESET}')
                if len(lines) > 6:
                    self._tab_log(planner, f'  {DIM}… ({len(lines) - 6} more lines){RESET}')

        elif action == "submit_proof":
            val = plan.get("proof_slug")
            if val:
                self._tab_log(planner, f'  {DIM}proof_slug: {val}{RESET}')

        elif action == "submit_lean_proof":
            val = plan.get("lean_proof_slug")
            if val:
                self._tab_log(planner, f'  {DIM}lean_proof_slug: {val}{RESET}')

    def _format_step_line(self, entry: dict) -> str:
        plans = entry.get("plans") or []
        action = entry.get("action", "")
        summary = entry.get("summary", "")

        # Render multi-action steps: show each action on its own line
        if len(plans) > 1:
            lines_parts: list[str] = []
            for plan in plans:
                a = plan.get("action", "")
                s = plan.get("summary", "")
                c = ACTION_STYLE.get(a, "")
                if a == "spawn":
                    # Use per-task summaries for spawn, one per line
                    task_summaries = [
                        t.get("summary", "").strip()
                        for t in plan.get("tasks", [])
                        if t.get("summary", "").strip()
                    ]
                    if task_summaries:
                        lines_parts.append(f'{c}■{RESET} {BOLD}{a}{RESET}')
                        for ts in task_summaries:
                            lines_parts.append(f'  {DIM}•{RESET} {ts}')
                        continue
                lines_parts.append(f'{c}■{RESET} {BOLD}{a}{RESET} {DIM}-{RESET} {s}')
            line = "\n".join(lines_parts)
        else:
            color = ACTION_STYLE.get(action, "")
            line = f'{color}■{RESET} {BOLD}{action}{RESET} {DIM}-{RESET} {summary}'

        # Show per-worker task summaries with verdicts for spawn actions
        if action == "spawn":
            worker_tabs = entry.get("worker_tabs") or []
            verdicts = entry.get("verdicts") or {}
            widx = 0
            for tab in worker_tabs:
                label = getattr(tab, "label", "")
                if not label.startswith("Worker"):
                    continue  # skip verifier tabs
                line += f'\n  {DIM}•{RESET} {label}'
                verdict = verdicts.get(widx, "")
                if verdict:
                    if "CORRECT" in verdict and "FLAWED" not in verdict:
                        line += f'\n    {GREEN}{verdict}{RESET}'
                    elif "CRITICALLY FLAWED" in verdict:
                        line += f'\n    {RED}{verdict}{RESET}'
                    else:
                        line += f'\n    {YELLOW}{verdict}{RESET}'
                widx += 1
        labels: list[str] = []
        feedback = (entry.get("feedback") or "").strip()
        if entry.get("rejected"):
            if feedback:
                labels.append(f"{YELLOW}rejected with feedback:{RESET} {GREEN}{feedback}{RESET}")
            else:
                labels.append(f"{YELLOW}rejected{RESET}")
        elif entry.get("interrupted"):
            if feedback:
                labels.append(f"{YELLOW}interrupted with feedback:{RESET} {GREEN}{feedback}{RESET}")
            else:
                labels.append(f"{YELLOW}interrupted{RESET}")
        elif feedback:
            labels.append(f"{YELLOW}feedback:{RESET} {GREEN}{feedback}{RESET}")
        if labels:
            line += "\n" + "  " + f' {DIM}·{RESET} '.join(labels)
        return line

    def _sync_step_log_line(self, step_idx: int):
        if not (0 <= step_idx < len(self.step_entries)):
            return
        line = self._format_step_line(self.step_entries[step_idx])
        planner = self.tabs[0]
        for log_entry in planner.log_lines:
            if log_entry.step_idx == step_idx:
                log_entry.text = line
                break

    def step_complete(self, step_num: int,
                      action: str, summary: str, detail: str = "",
                      rejected: bool = False, interrupted: bool = False,
                      feedback: str = "",
                      plans: list[dict] | None = None) -> int:
        planner = self.tabs[0]
        trace = planner.last_trace
        output = planner.last_output
        planner.last_trace = ""
        planner.last_output = ""
        idx = len(self.step_entries)
        entry = {
            "action": action,
            "summary": summary,
            "step_num": step_num,
            "detail": detail,
            "trace": trace,
            "output": output,
            "action_output": "",
            "rejected": rejected,
            "interrupted": interrupted,
            "feedback": feedback.strip(),
            "whiteboard": getattr(self, "whiteboard", ""),
            "plans": plans or [],
        }
        line = self._format_step_line(entry)
        self._tab_log(planner, line, step_idx=idx)
        self.step_entries.append(entry)
        self.update_step(step_num)
        if self._main_visible:
            self._redraw()
        return idx

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
        self._sync_step_log_line(step_idx)
        if self._main_visible:
            self._redraw()

    def append_step_action_output(self, step_num: int, text: str):
        """Append action-produced output to a step entry by step number."""
        if not text:
            return
        for entry in reversed(self.step_entries):
            if entry.get("step_num") == step_num:
                prev = entry.get("action_output", "")
                entry["action_output"] = (
                    f"{prev}\n\n{text}".strip() if prev else text
                )
                break

    def _open_selected_step_detail(self):
        if self._nav_step < 0:
            return
        self._step_detail_idx = self._nav_step
        self._step_detail_scroll = 0
        self._refresh_step_detail()
        self.view = "step_detail"

    def _open_proposal_detail(self):
        """Open detail view for the currently proposed action."""
        if not self._current_proposal:
            return
        self._step_detail_scroll = 0
        self._refresh_proposal_detail()
        self.view = "step_detail"

    def _refresh_proposal_detail(self):
        """Build detail text for the current proposal (list of plans)."""
        proposals = self._current_proposal
        if not proposals:
            self._step_detail_title = "Proposal"
            self._step_detail_text = "  (no proposal)"
            return

        # Normalize: _current_proposal can be list[dict] or dict (legacy)
        if isinstance(proposals, dict):
            proposals = [proposals]

        # Title from the primary (last) plan
        primary = proposals[-1]
        action = primary.get("action", "")
        summary = primary.get("summary", "")
        action_color = ACTION_STYLE.get(action, WHITE)
        count_label = f" ({len(proposals)} actions)" if len(proposals) > 1 else ""
        self._step_detail_title = (
            f"Proposed{count_label}: {action_color}{action}{RESET} {DIM}-{RESET} {summary}"
            f"  {YELLOW}● proposed{RESET}"
        )

        parts: list[str] = []

        def add_section(title: str, lines: list[str], color: str = BLUE):
            if not lines:
                return
            if parts:
                parts.append(f"  {DIM}{'─' * max(self.cols - 4, 20)}{RESET}")
                parts.append("")
            parts.append(f"  {color}{BOLD}{title}{RESET}")
            for line in lines:
                parts.append(f"  {line}" if line else "")

        # Planner Output - includes reasoning when trace_visible
        planner = self.tabs[0]
        trace = (planner.last_trace or "").rstrip()
        output = (planner.last_output or "").rstrip()
        planner_lines: list[str] = []
        if trace:
            if self.trace_visible:
                for line in trace.splitlines():
                    planner_lines.append(f"{DIM}{line}{RESET}")
                if output:
                    planner_lines.append("")
            else:
                tok = self._approx_token_label(trace)
                planner_lines.append(f"{DIM}[reasoning - {tok}]{RESET}")
                if output:
                    planner_lines.append("")
        if output:
            for is_toml, segment in self._iter_toml_segments(output):
                if is_toml and not self.trace_visible:
                    tok = self._approx_token_label(segment)
                    planner_lines.append(f"{DIM}[action - {tok}]{RESET}")
                    continue
                for line in segment.splitlines():
                    planner_lines.append(
                        f"{DIM}{line}{RESET}" if is_toml else line)
        if planner_lines:
            add_section("Planner Output", planner_lines, color=BLUE)

        # Show detail for each plan in the batch
        for plan_idx, plan in enumerate(proposals):
            plan_action = plan.get("action", "")
            plan_summary = plan.get("summary", "")
            section_prefix = f"Action {plan_idx + 1}: " if len(proposals) > 1 else ""

            detail_lines: list[str] = []
            if plan_action == "spawn":
                tasks = plan.get("tasks", [])
                for i, task in enumerate(tasks):
                    task_summary = task.get("summary", "").strip()
                    desc = task.get("description", "").strip()
                    header = f"[{i}] {task_summary}" if task_summary else f"[{i}]"
                    if desc:
                        detail_lines.append(header)
                        for line in desc.splitlines():
                            detail_lines.append(f"    {line}")
                    else:
                        detail_lines.append(f"{header} (no description)")
            elif plan_action == "literature_search":
                query = plan.get("search_query", "")
                context = plan.get("search_context", "")
                if query:
                    detail_lines.append(f"Query:   {query}")
                if context:
                    for line in context.strip().splitlines():
                        detail_lines.append(f"Context: {line}")
            elif plan_action == "write_items":
                items = plan.get("items", [])
                for item in items:
                    slug = item.get("slug", "?")
                    content = item.get("content", "")
                    ext = ".lean" if item.get("format") == "lean" else ".md"
                    if content:
                        first = content.strip().splitlines()[0] if content.strip() else ""
                        detail_lines.append(f"• {slug}{ext} - {first}")
                    else:
                        detail_lines.append(f"• {slug}{ext} (delete)")
            elif plan_action == "read_items":
                slugs = plan.get("read", [])
                if slugs:
                    detail_lines.append(", ".join(slugs))
            elif plan_action == "write_whiteboard":
                wb = plan.get("whiteboard", "")
                if wb:
                    for line in wb.strip().splitlines()[:8]:
                        detail_lines.append(line)

            if detail_lines:
                ac = ACTION_STYLE.get(plan_action, WHITE)
                add_section(
                    f"{section_prefix}{ac}{plan_action}{RESET} {DIM}-{RESET} {plan_summary}",
                    detail_lines, color=CYAN,
                )

            # Per-item full content sections for write_items
            if plan_action == "write_items":
                items = plan.get("items", [])
                for item in items:
                    slug = item.get("slug", "?")
                    content = item.get("content", "")
                    ext = ".lean" if item.get("format") == "lean" else ".md"
                    if content:
                        item_lines = content.rstrip().splitlines()
                        add_section(f"{slug}{ext}", item_lines, color=GREEN)
                    else:
                        add_section(f"{slug}{ext}", [f"{DIM}(delete){RESET}"], color=RED)

        self._step_detail_text = "\n".join(parts) if parts else "  (no detail)"
        self._step_detail_scroll = min(
            self._step_detail_scroll,
            self._step_detail_max_scroll(),
        )

    @staticmethod
    def _step_detail_section_title(action: str) -> str:
        return {
            "spawn": "Worker Plan",
            "literature_search": "Literature Search",
            "read_items": "Reading Notes",
            "write_items": "Writing Notes",
            "read_theorem": "Theorem Analysis",
            "submit_proof": "Submission",
            "submit_lean_proof": "Lean Submission",
        }.get(action, "Step Details")

    def _refresh_step_detail(self):
        if not (0 <= self._step_detail_idx < len(self.step_entries)):
            self._step_detail_title = "Step Detail"
            self._step_detail_text = "(no detail)"
            return

        entry = self.step_entries[self._step_detail_idx]
        action = entry.get("action", "")
        summary = entry.get("summary", "")
        action_color = ACTION_STYLE.get(action, WHITE)

        # Build inline status indicator for title
        feedback = (entry.get("feedback") or "").strip()
        if entry.get("rejected"):
            if feedback:
                status_badge = (
                    f"{YELLOW}● rejected:{RESET} {GREEN}{feedback}{RESET}"
                )
            else:
                status_badge = f"{YELLOW}● rejected{RESET}"
        elif entry.get("interrupted"):
            if feedback:
                status_badge = (
                    f"{YELLOW}● interrupted with feedback:{RESET} {GREEN}{feedback}{RESET}"
                )
            else:
                status_badge = f"{YELLOW}● interrupted{RESET}"
        elif feedback:
            status_badge = f"{YELLOW}● feedback:{RESET} {GREEN}{feedback}{RESET}"
        else:
            worker_tabs = entry.get("worker_tabs") or []
            if action == "spawn" and worker_tabs and not all(
                getattr(t, "done", True) for t in worker_tabs
            ):
                status_badge = f"{CYAN}● workers running{RESET}"
            else:
                status_badge = f"{GREEN}● completed{RESET}"

        plans = entry.get("plans") or []
        if len(plans) > 1:
            action_labels = []
            for p in plans:
                a = p.get("action", "")
                ac = ACTION_STYLE.get(a, WHITE)
                action_labels.append(f"{ac}{a}{RESET}")
            self._step_detail_title = (
                f"Step {entry.get('step_num', '?')}: "
                + f" {DIM}+{RESET} ".join(action_labels)
                + f"  {status_badge}"
            )
        else:
            self._step_detail_title = (
                f"Step {entry.get('step_num', '?')}: "
                f"{action_color}{action}{RESET} {DIM}-{RESET} {summary}"
                f"  {status_badge}"
            )

        parts: list[str] = []

        def add_section(title: str, lines: list[str], color: str = BLUE):
            if not lines:
                return
            if parts:
                parts.append(f"  {DIM}{'─' * max(self.cols - 4, 20)}{RESET}")
                parts.append("")
            parts.append(f"  {color}{BOLD}{title}{RESET}")
            for line in lines:
                parts.append(f"  {line}" if line else "")

        # Planner Output - includes reasoning when trace_visible
        trace = (entry.get("trace") or "").rstrip()
        output = (entry.get("output") or "").rstrip()
        planner_lines: list[str] = []
        if trace:
            if self.trace_visible:
                for line in trace.splitlines():
                    planner_lines.append(f"{DIM}{line}{RESET}")
                if output:
                    planner_lines.append("")
            else:
                tok = self._approx_token_label(trace)
                planner_lines.append(f"{DIM}[reasoning - {tok}]{RESET}")
                if output:
                    planner_lines.append("")
        if output:
            for is_toml, segment in self._iter_toml_segments(output):
                if is_toml and not self.trace_visible:
                    tok = self._approx_token_label(segment)
                    planner_lines.append(f"{DIM}[action - {tok}]{RESET}")
                    continue
                for line in segment.splitlines():
                    planner_lines.append(
                        f"{DIM}{line}{RESET}" if is_toml else line)
        if planner_lines:
            add_section("Planner Output", planner_lines, color=BLUE)

        # Show non-spawn actions from the plans list (multi-action steps)
        if len(plans) > 1:
            for plan in plans:
                pa = plan.get("action", "")
                ps = plan.get("summary", "")
                if pa == "spawn":
                    continue  # spawn is shown separately below
                pac = ACTION_STYLE.get(pa, WHITE)
                detail_lines: list[str] = []
                if pa == "write_whiteboard":
                    wb = plan.get("whiteboard", "")
                    if wb:
                        for wline in wb.strip().splitlines()[:10]:
                            detail_lines.append(wline)
                        total = len(wb.strip().splitlines())
                        if total > 10:
                            detail_lines.append(f"{DIM}… ({total - 10} more lines){RESET}")
                elif pa == "write_items":
                    items = plan.get("items", [])
                    for item in items:
                        slug = item.get("slug", "?")
                        content = item.get("content", "")
                        ext = ".lean" if item.get("format") == "lean" else ".md"
                        if content:
                            first = content.strip().splitlines()[0] if content.strip() else ""
                            detail_lines.append(f"• {slug}{ext} - {first}")
                        else:
                            detail_lines.append(f"• {slug}{ext} (delete)")
                elif pa == "read_items":
                    slugs = plan.get("read", [])
                    if slugs:
                        detail_lines.append(", ".join(slugs))
                if detail_lines:
                    add_section(
                        f"{pac}{pa}{RESET} {DIM}-{RESET} {ps}",
                        detail_lines, color=CYAN,
                    )
        else:
            # Single-action step: show detail string
            detail = (entry.get("detail") or "").strip()
            if detail:
                add_section("Action Input", detail.splitlines(), color=CYAN)

        if action == "spawn":
            worker_tabs = entry.get("worker_tabs") or []
            # Group worker and verifier tabs by worker index
            workers: dict[str, _Tab] = {}
            verifiers: dict[str, _Tab] = {}
            for tab in worker_tabs:
                label = getattr(tab, "label", "").strip() or "Worker"
                if label.startswith("Verify"):
                    v_idx = label.split()[-1] if " " in label else "0"
                    verifiers[v_idx] = tab
                else:
                    w_idx = label.split()[-1] if " " in label else "0"
                    workers[w_idx] = tab

            def _tab_output_lines(tab: _Tab) -> list[str]:
                """Extract output lines from a tab, dimming reasoning traces."""
                result: list[str] = []
                for log_entry in (getattr(tab, "log_lines", []) or []):
                    text = getattr(log_entry, "text", "")
                    if not text or text == self._dim_separator():
                        continue
                    is_trace = getattr(log_entry, "is_trace", False)
                    if is_trace:
                        if self.trace_visible:
                            for line in text.splitlines():
                                result.append(f"{DIM}{line}{RESET}")
                        else:
                            tok = self._approx_token_label(text)
                            result.append(f"{DIM}[reasoning - {tok}]{RESET}")
                    else:
                        result.append(text)
                return result

            for w_idx in sorted(workers.keys()):
                wtab = workers[w_idx]
                task_description = getattr(wtab, "task_description", "").strip()
                if task_description:
                    add_section(
                        f"Worker {w_idx} Input",
                        task_description.splitlines(),
                        color=CYAN,
                    )
                out_lines = _tab_output_lines(wtab)
                if out_lines:
                    add_section(f"Worker {w_idx} Output", out_lines, color=MAGENTA)
                vtab = verifiers.get(w_idx)
                if vtab:
                    v_lines = _tab_output_lines(vtab)
                    if v_lines:
                        add_section(f"Worker {w_idx} Verification", v_lines, color=MAGENTA)

        action_output = (entry.get("action_output") or "").rstrip()
        # Per-item full content sections for write_items (before action output
        # so content appears before verification errors).  Show whenever the
        # entry carries write_items data, not only when the *primary* action
        # is "write_items" -- multi-action steps (write_items + spawn) set
        # the primary action to "spawn" but still populate this field.
        if entry.get("write_items"):
            items = entry.get("write_items") or []
            for item in items:
                slug = item.get("slug", "?")
                content = item.get("content", "")
                ext = ".lean" if item.get("format") == "lean" else ".md"
                if content:
                    item_lines = content.rstrip().splitlines()
                    add_section(f"{slug}{ext}", item_lines, color=GREEN)
                else:
                    add_section(f"{slug}{ext}", [f"{DIM}(delete){RESET}"], color=RED)

        # Show action_output for non-spawn actions, or when a multi-action
        # step has write_items output (e.g. lean verification results).
        if action_output and (action != "spawn" or entry.get("write_items")):
            output_title = {
                "read_theorem": "Theorem Content",
                "read_items": "Items Content",
            }.get(action, "Action Output")
            add_section(output_title, action_output.splitlines(), color=MAGENTA)

        self._step_detail_text = "\n".join(parts) if parts else "  (no detail)"
        self._step_detail_scroll = min(
            self._step_detail_scroll,
            self._step_detail_max_scroll(),
        )

    def _refresh_action_detail(self, tab: _Tab):
        """Build detail page for a worker tool call entry."""
        if not (0 <= self._step_detail_idx < len(tab.entries)):
            self._step_detail_title = "Action Detail"
            self._step_detail_text = "(no detail)"
            return

        entry = tab.entries[self._step_detail_idx]
        tool = entry.get("tool", "?")
        tool_color = TOOL_STYLE.get(tool, WHITE)

        # Inline status + duration in title
        status = entry.get("status", "")
        duration_ms = entry.get("duration_ms", 0)
        dur_text = f" ({duration_ms / 1000:.1f}s)" if duration_ms else ""
        if status == "running":
            status_badge = f"{YELLOW}● running…{RESET}"
        elif status == "ok":
            if tool == "lean_search":
                status_badge = dur_text.strip() if dur_text else ""
            else:
                status_badge = f"{GREEN}● succeeded{RESET}{dur_text}"
        elif status == "partial":
            status_badge = f"{YELLOW}● partial (sorry){RESET}{dur_text}"
        else:
            status_badge = f"{RED}● failed{RESET}{dur_text}"
        self._step_detail_title = (
            f"{tool_color}{tool}{RESET}  {status_badge}"
        )

        parts: list[str] = []

        def add_section(title: str, lines: list[str], color: str = BLUE):
            if not lines:
                return
            if parts:
                parts.append(f"  {DIM}{'─' * max(self.cols - 4, 20)}{RESET}")
                parts.append("")
            parts.append(f"  {color}{BOLD}{title}{RESET}")
            for line in lines:
                parts.append(f"  {line}" if line else "")

        # Action Input (arguments)
        args = entry.get("args", {})
        store_prefix = args.get("_store_prefix", "")
        input_lines: list[str] = []
        if store_prefix:
            for line in store_prefix.splitlines():
                input_lines.append(f"{DIM}{line}{RESET}")
        if "code" in args:
            input_lines.extend(args["code"].splitlines())
        if "query" in args:
            input_lines.append(args["query"])
        # Show any other args as key: value
        for key, val in args.items():
            if key in ("code", "query", "_store_prefix"):
                continue
            val_str = str(val)
            if len(val_str) > 200:
                val_str = val_str[:200] + "…"
            input_lines.append(f"{DIM}{key}:{RESET} {val_str}")
        if input_lines:
            add_section("Action Input", input_lines, color=CYAN)

        # Action Output (result)
        result = entry.get("result", "")
        if result:
            add_section("Action Output", result.splitlines(), color=MAGENTA)

        self._step_detail_text = "\n".join(parts) if parts else "  (no detail)"
        self._step_detail_scroll = min(
            self._step_detail_scroll,
            self._step_detail_max_scroll(),
        )

    def _clear_proposal(self):
        """Remove detailed proposal lines, keeping only a compact summary."""
        self._current_proposal = None
        self._nav_proposal = False
        if self._proposal_log_start < 0:
            return
        planner = self.tabs[0]
        planner.log_lines = planner.log_lines[:self._proposal_log_start]
        self._proposal_log_start = -1

    def show_replan_notice(self, text: str):
        """Show a transient notice cleared when next proposal appears."""
        planner = self.tabs[0]
        self.clear_replan_notice()
        entry = _LogEntry(self._style(text, color="yellow"))
        planner.log_lines.append(entry)
        if len(planner.log_lines) > 500:
            planner.log_lines = planner.log_lines[-500:]
            if entry not in planner.log_lines:
                self._replan_notice_entry = None
            else:
                self._replan_notice_entry = entry
        else:
            self._replan_notice_entry = entry
        if planner is self._active_tab and self._main_visible:
            if self.view == "whiteboard_split":
                self._split_dirty = True
            elif planner.scroll_offset > 0:
                pass  # Stay where we are; new content is at the bottom
            else:
                self._write(f' {entry.text}\n')

    def clear_replan_notice(self):
        entry = self._replan_notice_entry
        if entry is None:
            return
        planner = self.tabs[0]
        try:
            planner.log_lines.remove(entry)
        except ValueError:
            pass
        self._replan_notice_entry = None
        if planner is self._active_tab and self._main_visible:
            self._redraw()
