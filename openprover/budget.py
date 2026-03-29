"""Budget tracking for proving sessions (token or time limits)."""

import re
import time


def _fmt_tokens(n: int) -> str:
    """Format token count: 500, 12.3k, 1.2M."""
    if n < 1000:
        return str(n)
    if n < 1_000_000:
        k = n / 1000
        return f"{k:.1f}k" if k < 100 else f"{k:.0f}k"
    m = n / 1_000_000
    return f"{m:.1f}M" if m < 100 else f"{m:.0f}M"


def _fmt_duration(secs: int) -> str:
    """Format seconds: 45s, 14m, 1h12m."""
    if secs < 60:
        return f"{secs}s"
    m = secs // 60
    s = secs % 60
    if m < 60:
        return f"{m}m{s}s" if s else f"{m}m"
    h = m // 60
    rm = m % 60
    return f"{h}h{rm}m" if rm else f"{h}h"


def parse_duration(s: str) -> int:
    """Parse duration string to seconds.

    Accepts: '30m', '2h', '1h30m', '90s', '1800' (plain seconds).
    """
    s = s.strip()
    # Plain integer → seconds
    if s.isdigit():
        return int(s)
    m = re.fullmatch(r'(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?', s)
    if not m or not any(m.groups()):
        raise ValueError(f"Invalid duration: {s!r} (expected e.g. '30m', '2h', '1h30m')")
    hours = int(m.group(1) or 0)
    mins = int(m.group(2) or 0)
    secs = int(m.group(3) or 0)
    total = hours * 3600 + mins * 60 + secs
    if total <= 0:
        raise ValueError(f"Duration must be positive: {s!r}")
    return total


class Budget:
    """Tracks resource budget (output tokens or wall-clock time)."""

    def __init__(self, mode: str, limit: int,
                 conclude_after: float = 0.99):
        assert mode in ("tokens", "time"), f"Invalid budget mode: {mode}"
        self.mode = mode
        self.limit = limit
        self.conclude_after = conclude_after
        self.total_output_tokens = 0
        self.start_time = time.monotonic()

    def fraction_spent(self) -> float:
        if self.mode == "tokens":
            return self.total_output_tokens / max(self.limit, 1)
        else:
            elapsed = time.monotonic() - self.start_time
            return elapsed / max(self.limit, 1)

    def is_exhausted(self) -> bool:
        return self.fraction_spent() >= 1.0

    def should_conclude(self) -> bool:
        return self.fraction_spent() >= self.conclude_after

    def add_output_tokens(self, n: int):
        self.total_output_tokens += n

    def status_str(self) -> str:
        """Short status for header display."""
        if self.mode == "tokens":
            return f"{_fmt_tokens(self.total_output_tokens)}/{_fmt_tokens(self.limit)} tok"
        else:
            elapsed = int(time.monotonic() - self.start_time)
            return f"{_fmt_duration(elapsed)}/{_fmt_duration(self.limit)}"

    def summary_str(self) -> str:
        """Longer status for prompts."""
        pct = int(self.fraction_spent() * 100)
        if self.mode == "tokens":
            return (f"{_fmt_tokens(self.total_output_tokens)}/{_fmt_tokens(self.limit)} "
                    f"output tokens used ({pct}%)")
        else:
            elapsed = int(time.monotonic() - self.start_time)
            return f"{_fmt_duration(elapsed)}/{_fmt_duration(self.limit)} elapsed ({pct}%)"

    def limit_str(self) -> str:
        """Human-readable limit for run_params display."""
        if self.mode == "tokens":
            return f"{_fmt_tokens(self.limit)} tokens"
        else:
            return _fmt_duration(self.limit)
