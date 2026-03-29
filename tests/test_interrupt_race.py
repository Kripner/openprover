"""Playground: verify ctrl+c / soft-interrupt mechanics.

Run directly:  python tests/test_interrupt_race.py
"""

import os
import signal
import subprocess
import threading
import time


def check(label: str, ok: bool):
    status = "\033[32mPASS\033[0m" if ok else "\033[31mFAIL\033[0m"
    print(f"  [{status}] {label}")
    if not ok:
        raise AssertionError(label)


# ── 1. os.killpg unblocks readline() ─────────────────────────────────────────

def test_kill_unblocks_readline():
    """Killing a subprocess (SIGKILL) must immediately unblock readline()."""
    proc = subprocess.Popen(
        ["python3", "-c",
         "import time,sys\n"
         "for i in range(200):\n"
         "    print(i, flush=True)\n"
         "    time.sleep(0.02)\n"],
        stdout=subprocess.PIPE, text=True, bufsize=1,
        start_new_session=True,
    )
    lines: list[str] = []
    done = threading.Event()

    def reader():
        while True:
            line = proc.stdout.readline()
            if not line:
                break
            lines.append(line)
        done.set()

    threading.Thread(target=reader, daemon=True).start()
    time.sleep(0.15)   # collect ~7 lines

    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except (OSError, ProcessLookupError):
        proc.kill()
    proc.wait()

    done.wait(timeout=2.0)
    check("readline() unblocked within 2s", done.is_set())
    check("partial output (not all 200 lines)", 0 < len(lines) < 200)
    check("returncode < 0 (killed by signal)", proc.returncode < 0)
    print(f"     {len(lines)} lines read, returncode={proc.returncode}")


# ── 2. Multi-worker clear_soft_interrupt race ─────────────────────────────────

def test_multiworker_race():
    """
    Bug: with parallelism>1, Worker-A calls clear_soft_interrupt() before
    Worker-B's fallback check runs → Worker-B sees the flag cleared and raises
    RuntimeError instead of starting Phase 2.

    Fix: also treat proc.returncode<0 with no result as soft_interrupted.
    """
    flag = threading.Event()
    results_broken = [None, None]
    results_fixed  = [None, None]

    def worker_broken(idx, delay):
        flag.wait()
        time.sleep(delay)
        # Current fallback: only check flag
        soft = flag.is_set()
        if soft:
            flag.clear()          # Worker-A clears before Worker-B checks
            results_broken[idx] = "phase2"
        else:
            results_broken[idx] = "RuntimeError"

    def worker_fixed(idx, delay, returncode):
        flag.wait()
        time.sleep(delay)
        # Fixed fallback: also check returncode
        soft = flag.is_set() or (returncode < 0)
        if soft:
            flag.clear()
            results_fixed[idx] = "phase2"
        else:
            results_fixed[idx] = "RuntimeError"

    TRIALS = 500
    broken_wrong = 0
    fixed_wrong  = 0

    for _ in range(TRIALS):
        flag.clear()
        results_broken[:] = [None, None]
        results_fixed[:] = [None, None]

        # Worker 0 is faster → clears the flag before Worker 1 checks it
        threads = [
            threading.Thread(target=worker_broken, args=(0, 0.0)),
            threading.Thread(target=worker_broken, args=(1, 5e-5)),
        ]
        for t in threads: t.start()
        time.sleep(0.001)
        flag.set()
        for t in threads: t.join()
        if results_broken[1] == "RuntimeError":
            broken_wrong += 1

        flag.clear()
        threads = [
            threading.Thread(target=worker_fixed, args=(0, 0.0, -9)),
            threading.Thread(target=worker_fixed, args=(1, 5e-5, -9)),
        ]
        for t in threads: t.start()
        time.sleep(0.001)
        flag.set()
        for t in threads: t.join()
        if results_fixed[1] == "RuntimeError":
            fixed_wrong += 1

    pct = broken_wrong / TRIALS * 100
    print(f"     broken: {broken_wrong}/{TRIALS} Worker-1 RuntimeError ({pct:.0f}%)")
    check("race is observable in broken version", broken_wrong > 0)
    check("fixed version: no RuntimeError", fixed_wrong == 0)


# ── main ──────────────────────────────────────────────────────────────────────

print("\n── test_kill_unblocks_readline")
test_kill_unblocks_readline()

print("\n── test_multiworker_race")
test_multiworker_race()

print("\n\033[32mall tests passed\033[0m\n")
