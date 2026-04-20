#!/usr/bin/env python3
"""Sanity-check a benchmark result directory.

For each entry in results.json:
  - proved   → ensure PROOF.lean exists, is non-empty, declares the
               expected theorem name, and imports Mathlib.
  - not_proved → ensure no PROOF.lean (a leftover is a bug); ensure
               trace.log shows a genuine attempt (not a silent-error
               loop where every LLM call failed).
  - error    → classify the recorded error so the user knows whether
               the failure is transient (retryable) or structural.

Optionally run `lake env lean` on a sample of PROOF.lean files to
re-verify that the proofs actually compile against the Lean project.
This requires the Lean project dir to be available locally (or use
--remote-host HOST:/path/to/project to verify on a remote machine).

Usage:
    check_benchmark.py results/proofnet-kimi-baseline
    check_benchmark.py results/proofnet-kimi-openprover --verify 5
    check_benchmark.py results/* --verify all --remote-host hyperion3:~/openprover/proofnet/ProofNet
"""

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from collections import Counter


# --- Heuristic for silent errors (copied from audit_silent_errors.py) ---

ERROR_RE = re.compile(r"^\d\d:\d\d:\d\d\s+(Planner|Worker) error:", re.MULTILINE)
CALL_RE = re.compile(r"^\d\d:\d\d:\d\d\s+\[(planner|worker)_\S+\]\s+calling", re.MULTILINE)


def classify_trace_openprover(trace: str) -> tuple[str, dict]:
    """Classify an openprover trace.log as ok/silent_error/no_trace."""
    calls = [m.start() for m in CALL_RE.finditer(trace)]
    errors = [m.start() for m in ERROR_RE.finditer(trace)]
    if not calls:
        return ("no_trace", {"calls": 0, "errors": len(errors)})
    failed_calls = 0
    for call_pos in calls:
        window = trace[call_pos:call_pos + 2000]
        if ERROR_RE.search(window):
            next_call_rel = CALL_RE.search(window[10:])
            err = ERROR_RE.search(window)
            if next_call_rel is None or err.start() < (next_call_rel.start() + 10):
                failed_calls += 1
    productive = len(calls) - failed_calls
    info = {"calls": len(calls), "errors": len(errors),
            "failed_calls": failed_calls, "productive_calls": productive}
    if productive == 0 and failed_calls >= 5:
        err_match = ERROR_RE.search(trace)
        if err_match:
            info["sample_error"] = trace[err_match.start():err_match.start() + 200].splitlines()[0]
        return ("silent_error", info)
    return ("ok", info)


# --- Baseline silent-error heuristic ---

def classify_trace_baseline(log: str) -> tuple[str, dict]:
    """Baseline uses log.txt. Look for turn counts and LLM/provider errors."""
    turns = len(re.findall(r"^turn \d+:", log, re.MULTILINE))
    # Baseline's is_rate_limited_error / is_transient_error patterns
    # would be logged as "rate/spending limit hit" or "transient error".
    rate = len(re.findall(r"rate.*limit|spending limit|429", log, re.IGNORECASE))
    transient = len(re.findall(r"transient error|timed out", log, re.IGNORECASE))
    info = {"turns": turns, "rate_hits": rate, "transient_hits": transient}
    # A baseline run with 0 turns is suspicious
    if turns == 0 and ("error" in log.lower() or "failed" in log.lower()):
        return ("silent_error", info)
    return ("ok", info)


# --- Structural checks for PROOF.lean ---

def _strip_lean_comments(text: str) -> str:
    """Strip `-- …` line comments and `/- … -/` block comments from Lean source."""
    # Block comments (non-greedy, multiline)
    text = re.sub(r"/-.*?-/", "", text, flags=re.DOTALL)
    # Line comments
    text = re.sub(r"--[^\n]*", "", text)
    return text


def check_proof_lean(proof_path: Path, expected_thm: str) -> list[str]:
    """Return a list of structural issues (empty if all good).

    Checks:
    - file exists and is non-empty
    - has `import Mathlib` (direct or via a specific Mathlib submodule)
    - no `sorry` in non-comment code
    - declares the expected name as `theorem`, `lemma`, `def`, or `example`
      (all four are valid forms in Mathlib — `def` is used for
      theorems whose conclusion is a structure rather than a Prop)
    - flag if the file declares some OTHER top-level name but not the
      expected one (this catches openprover runs where the model
      renamed the theorem to something it found easier to prove —
      Lean still compiles but the benchmark task wasn't actually done)
    """
    issues = []
    if not proof_path.is_file():
        return ["missing PROOF.lean"]
    text = proof_path.read_text(errors="replace")
    if not text.strip():
        return ["PROOF.lean is empty"]
    # Allow any Mathlib import (full or submodule)
    if not re.search(r"^\s*import\s+Mathlib(\.|$|\s)", text, re.MULTILINE):
        issues.append("no 'import Mathlib'")

    code = _strip_lean_comments(text)
    if re.search(r"\bsorry\b", code):
        issues.append("contains 'sorry' in non-comment code")

    # Match named declarations: theorem / lemma / def followed by a Lean
    # identifier (starts with letter/_, may contain letters/digits/_/').
    # Anonymous `example` declarations don't carry a name and are tracked
    # separately so we can flag them as "should have been a named proof".
    ident = r"[a-zA-Z_][a-zA-Z0-9_']*"
    decl_re = rf"^\s*(?:theorem|lemma|def)\s+({ident})"
    decls = re.findall(decl_re, code, re.MULTILINE)
    has_anonymous_example = bool(
        re.search(r"^\s*example\b", code, re.MULTILINE)
    )

    if expected_thm not in decls:
        if has_anonymous_example and not decls:
            issues.append(
                f"uses anonymous `example` instead of declaring '{expected_thm}'"
            )
        elif decls:
            issues.append(
                f"expected '{expected_thm}' but declares: {', '.join(decls[:5])}"
                + ("..." if len(decls) > 5 else "")
            )
        else:
            issues.append("no theorem/lemma/def declaration found")
    return issues


# --- Error classification ---

def classify_error(error_msg: str) -> str:
    """Return a category for a recorded error message."""
    m = error_msg.lower()
    if "429" in m or "rate limit" in m or "spending" in m or "quota" in m:
        return "rate_limit"
    if "403" in m or "key limit" in m:
        return "403_key_limit"
    if "502" in m or "503" in m or "504" in m:
        return "5xx_gateway"
    if "timed out" in m or "timeout" in m or "keep-alive" in m:
        return "timeout"
    if "connection" in m and ("reset" in m or "aborted" in m):
        return "connection"
    if "unparseable body" in m or "json decode" in m:
        return "parse_error"
    if "hard timeout" in m:
        return "harness_hard_timeout"
    if "ename" in m or "enametoolong" in m:
        return "OS_error"
    if "llm errors" in m:
        return "max_consecutive_llm_errors"
    return "other"


# --- Main check ---

def check_benchmark(bench_dir: Path, verify_n: int, verify_cmd_template: str | None):
    results_path = bench_dir / "results.json"
    runs_dir = bench_dir / "runs"
    if not results_path.is_file():
        print(f"{bench_dir}: no results.json", file=sys.stderr)
        return 1
    if not runs_dir.is_dir():
        print(f"{bench_dir}: no runs/", file=sys.stderr)
        return 1

    data = json.load(open(results_path))
    names = [r["name"] for r in data]
    dupes = [n for n, c in Counter(names).items() if c > 1]

    total = len(data)
    by_status = Counter(r["status"] for r in data)
    print(f"\n== {bench_dir} ==")
    print(f"Entries: {total}  ({dict(by_status)})")
    if dupes:
        print(f"  [ERROR] duplicate names: {dupes}")

    # Per-entry structural checks
    proved_issues = []        # proved but structural issue with PROOF.lean
    not_proved_has_proof = [] # not_proved but PROOF.lean exists
    silent_errors = []        # not_proved but trace shows silent errors
    error_categories = Counter()
    missing_run_dir = []

    for entry in data:
        name = entry["name"]
        run = runs_dir / name
        status = entry["status"]

        if not run.is_dir():
            missing_run_dir.append(name)
            continue

        proof = run / "PROOF.lean"

        if status == "proved":
            issues = check_proof_lean(proof, name)
            if issues:
                proved_issues.append((name, issues))

        elif status == "not_proved":
            if proof.exists():
                not_proved_has_proof.append(name)
            # Trace check
            trace_p = run / "trace.log"  # openprover
            log_p = run / "log.txt"      # baseline
            if trace_p.is_file():
                verdict, info = classify_trace_openprover(
                    trace_p.read_text(errors="replace"))
                if verdict == "silent_error":
                    silent_errors.append((name, info))
            elif log_p.is_file():
                verdict, info = classify_trace_baseline(
                    log_p.read_text(errors="replace"))
                if verdict == "silent_error":
                    silent_errors.append((name, info))

        elif status == "error":
            category = classify_error(entry.get("error", ""))
            error_categories[category] += 1

    # ── Report ────────────────────────────────────────────────────
    ok_lines = []
    issues_found = False

    if missing_run_dir:
        issues_found = True
        print(f"\n[ERROR] {len(missing_run_dir)} entries have no run dir:")
        for n in missing_run_dir[:5]:
            print(f"  {n}")
        if len(missing_run_dir) > 5:
            print(f"  ... and {len(missing_run_dir)-5} more")
    else:
        ok_lines.append(f"  [OK] every entry has a run dir")

    if proved_issues:
        issues_found = True
        print(f"\n[WARN] {len(proved_issues)} proved entries have issues with PROOF.lean:")
        for n, issues in proved_issues[:10]:
            print(f"  {n}: {', '.join(issues)}")
        if len(proved_issues) > 10:
            print(f"  ... and {len(proved_issues)-10} more")
    elif by_status.get("proved", 0) > 0:
        ok_lines.append(f"  [OK] all {by_status['proved']} 'proved' entries have valid PROOF.lean (imports Mathlib, declares theorem, no 'sorry')")

    if not_proved_has_proof:
        issues_found = True
        print(f"\n[ERROR] {len(not_proved_has_proof)} 'not_proved' entries have a PROOF.lean (contradiction):")
        for n in not_proved_has_proof[:5]:
            print(f"  {n}")
    elif by_status.get("not_proved", 0) > 0:
        ok_lines.append(f"  [OK] no 'not_proved' entry has a stray PROOF.lean")

    if silent_errors:
        issues_found = True
        print(f"\n[WARN] {len(silent_errors)} 'not_proved' entries look like silent errors:")
        for n, info in silent_errors[:10]:
            sample = info.get("sample_error", "")[:100]
            print(f"  {n}: {info.get('failed_calls', '?')}/{info.get('calls', '?')} failed | {sample}")
        if len(silent_errors) > 10:
            print(f"  ... and {len(silent_errors)-10} more")
    elif by_status.get("not_proved", 0) > 0:
        ok_lines.append(f"  [OK] all {by_status['not_proved']} 'not_proved' entries show genuine prover attempts")

    if error_categories:
        print(f"\n[INFO] Error categories ({sum(error_categories.values())} total):")
        for cat, count in error_categories.most_common():
            print(f"  {count:3d}  {cat}")

    if ok_lines:
        print("\nSanity checks passed:")
        for line in ok_lines:
            print(line)

    # ── Optional: actually run lean on a sample of proofs ─────────
    if verify_n and verify_cmd_template:
        proved_entries = [r for r in data if r["status"] == "proved"]
        if not proved_entries:
            print("\n[verify] no proved entries to verify")
        else:
            import random
            random.seed(42)
            if verify_n == "all":
                sample = proved_entries
            else:
                sample = random.sample(proved_entries,
                                       min(int(verify_n), len(proved_entries)))
            print(f"\n[verify] Lean-verifying {len(sample)} of {len(proved_entries)} proofs...")
            ok = 0
            fails = []
            for entry in sample:
                name = entry["name"]
                proof = runs_dir / name / "PROOF.lean"
                if not proof.is_file():
                    fails.append((name, "no PROOF.lean"))
                    continue
                success, detail = verify_lean(proof, verify_cmd_template)
                if success:
                    ok += 1
                    print(f"  ✓ {name}")
                else:
                    fails.append((name, detail))
                    print(f"  ✗ {name}: {detail[:200]}")
            print(f"\n[verify] {ok}/{len(sample)} proofs compile cleanly")
            if fails:
                issues_found = True

    return 1 if issues_found else 0


def verify_lean(proof_path: Path, cmd_template: str) -> tuple[bool, str]:
    """Run `lake env lean` (or a user-provided command) on PROOF.lean.

    cmd_template uses {proof} as a placeholder for the proof file path.
    Examples:
        "lake env lean {proof}"  (run locally, cwd=lean project)
        "ssh hyperion3 'cd ~/openprover/proofnet/ProofNet && lake env lean -' < {proof}"
    """
    if "{proof}" not in cmd_template:
        return (False, f"cmd template missing {{proof}}: {cmd_template}")

    # If remote, we need to pipe the proof over stdin or scp it.
    # Simplest: scp proof to /tmp on remote, run lean, rm.
    if cmd_template.startswith("ssh "):
        host_match = re.match(r"ssh\s+(\S+)", cmd_template)
        if not host_match:
            return (False, "bad remote cmd")
        host = host_match.group(1)
        # Extract the inner command (between quotes)
        inner_match = re.search(r"ssh\s+\S+\s+'([^']+)'", cmd_template)
        if not inner_match:
            return (False, "bad remote cmd (no quoted inner)")
        inner = inner_match.group(1)
        # Upload proof to /tmp on remote
        remote_path = f"/tmp/check_proof_{proof_path.parent.name}.lean"
        try:
            subprocess.run(
                ["scp", "-q", str(proof_path), f"{host}:{remote_path}"],
                check=True, timeout=30,
            )
            run_cmd = inner.replace("{proof}", remote_path)
            result = subprocess.run(
                ["ssh", host, run_cmd],
                capture_output=True, text=True, timeout=300,
            )
            subprocess.run(["ssh", host, f"rm -f {remote_path}"],
                          timeout=30, capture_output=True)
            combined = result.stdout + result.stderr
            if result.returncode == 0 and "error" not in combined.lower():
                return (True, "")
            return (False, combined[-500:])
        except subprocess.TimeoutExpired:
            return (False, "lean timeout")
        except Exception as e:
            return (False, f"{type(e).__name__}: {e}")
    else:
        try:
            result = subprocess.run(
                cmd_template.replace("{proof}", str(proof_path)),
                shell=True, capture_output=True, text=True, timeout=300,
            )
            combined = result.stdout + result.stderr
            if result.returncode == 0 and "error" not in combined.lower():
                return (True, "")
            return (False, combined[-500:])
        except Exception as e:
            return (False, f"{type(e).__name__}: {e}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bench_dirs", nargs="+", type=Path,
                    help="benchmark directories to check")
    ap.add_argument("--verify", metavar="N",
                    help="re-verify N random proofs (or 'all') using Lean")
    ap.add_argument("--verify-cmd",
                    default="ssh hyperion3 'cd ~/openprover/proofnet/ProofNet && lake env lean {proof}'",
                    help="shell command to run, {proof} is replaced with the PROOF.lean path")
    args = ap.parse_args()

    rc = 0
    for d in args.bench_dirs:
        rc |= check_benchmark(d.resolve(), args.verify, args.verify_cmd)
    sys.exit(rc)


if __name__ == "__main__":
    main()
