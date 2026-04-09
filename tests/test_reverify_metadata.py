from pathlib import Path

from openprover.cli import (
    _find_resumable_reverify_dir,
    _find_reverify_targets,
    _is_reverify_row_complete,
    _load_existing_reverify_rows,
    _write_reverify_outputs,
)
from openprover.inspect import _load_call, load_pages
from openprover.llm._base import archive


def test_archive_persists_provider_model_and_effort(tmp_path: Path):
    call_path = tmp_path / "verifier_0_call.md"
    archive(
        "gpt-5.4",
        tmp_path,
        1,
        "verifier_0",
        "prompt",
        "system",
        None,
        {"usage": {}, "stop_reason": "stop"},
        None,
        123,
        call_path,
        result_text="VERDICT: CORRECT",
        provider="codex",
        requested_model="gpt-5.4",
        reasoning_effort="xhigh",
    )

    data = _load_call(call_path)

    assert data is not None
    assert data["provider"] == "codex"
    assert data["requested_model"] == "gpt-5.4"
    assert data["model"] == "gpt-5.4"
    assert data["reasoning_effort"] == "xhigh"


def test_load_pages_includes_verifier_archives(tmp_path: Path):
    run_dir = tmp_path / "run"
    workers_dir = run_dir / "steps" / "step_001" / "workers"
    workers_dir.mkdir(parents=True)

    archive(
        "gpt-5.4",
        run_dir,
        1,
        "worker_0",
        "worker prompt",
        "system",
        None,
        {"usage": {}, "stop_reason": "stop"},
        None,
        100,
        workers_dir / "worker_0_call.md",
        result_text="worker result",
        provider="codex",
        requested_model="gpt-5.4",
        reasoning_effort="high",
    )
    archive(
        "gpt-5.4",
        run_dir,
        2,
        "verifier_0",
        "verify prompt",
        "system",
        None,
        {"usage": {}, "stop_reason": "stop"},
        None,
        120,
        workers_dir / "verifier_0_call.md",
        result_text="VERDICT: CORRECT",
        provider="codex",
        requested_model="gpt-5.4",
        reasoning_effort="xhigh",
    )

    pages = load_pages(run_dir)
    labels = [page["label"] for page in pages]
    verifier_page = next(page for page in pages if page["label"] == "Verify 0 Prompt")

    assert "Verify 0 Prompt" in labels
    assert "Verify 0 Output" in labels
    assert "effort:xhigh" in verifier_page["metadata"]


def test_load_pages_includes_sparse_verifier_archives(tmp_path: Path):
    run_dir = tmp_path / "run"
    workers_dir = run_dir / "steps" / "step_001" / "workers"
    workers_dir.mkdir(parents=True)

    archive(
        "gpt-5.4",
        run_dir,
        2,
        "verifier_1",
        "verify prompt",
        "system",
        None,
        {"usage": {}, "stop_reason": "stop"},
        None,
        120,
        workers_dir / "verifier_1_call.md",
        result_text="VERDICT: CORRECT",
        provider="codex",
        requested_model="gpt-5.4",
        reasoning_effort="xhigh",
    )

    pages = load_pages(run_dir)
    labels = [page["label"] for page in pages]

    assert "Verify 1 Prompt" in labels
    assert "Verify 1 Output" in labels


def test_find_reverify_targets_skips_search_steps(tmp_path: Path):
    run_dir = tmp_path / "run"

    search_workers = run_dir / "steps" / "step_001" / "workers"
    search_workers.mkdir(parents=True)
    (search_workers / "task_0.md").write_text("search task")
    (search_workers / "result_0.md").write_text("search result")
    (search_workers / "search_call.md").write_text("search archive")

    worker_dir = run_dir / "steps" / "step_002" / "workers"
    worker_dir.mkdir(parents=True)
    (worker_dir / "task_0.md").write_text("worker task")
    (worker_dir / "result_0.md").write_text("worker result")
    (worker_dir / "worker_0_call.md").write_text("worker archive")
    (worker_dir / "verifier_result_0.md").write_text("VERDICT: CORRECT")

    targets = _find_reverify_targets(
        run_dir, step_filter=None, worker_filter=None
    )

    assert [(t["step_num"], t["worker_idx"]) for t in targets] == [(2, 0)]


def test_find_reverify_targets_only_includes_previously_correct_items(tmp_path: Path):
    run_dir = tmp_path / "run"

    workers1 = run_dir / "steps" / "step_001" / "workers"
    workers1.mkdir(parents=True)
    (workers1 / "task_0.md").write_text("task 1")
    (workers1 / "result_0.md").write_text("result 1")
    (workers1 / "worker_0_call.md").write_text("worker archive 1")
    (workers1 / "verifier_result_0.md").write_text("Looks good\nVERDICT: CORRECT\n")

    workers2 = run_dir / "steps" / "step_002" / "workers"
    workers2.mkdir(parents=True)
    (workers2 / "task_0.md").write_text("task 2")
    (workers2 / "result_0.md").write_text("result 2")
    (workers2 / "worker_0_call.md").write_text("worker archive 2")
    (workers2 / "verifier_result_0.md").write_text(
        "Needs cleanup\nVERDICT: NEEDS MINOR FIXES - wording\n"
    )

    workers3 = run_dir / "steps" / "step_003" / "workers"
    workers3.mkdir(parents=True)
    (workers3 / "task_0.md").write_text("task 3")
    (workers3 / "result_0.md").write_text("result 3")
    (workers3 / "worker_0_call.md").write_text("worker archive 3")

    targets = _find_reverify_targets(
        run_dir, step_filter=None, worker_filter=None
    )

    assert [(t["step_num"], t["worker_idx"]) for t in targets] == [(1, 0)]
    assert targets[0]["original_verdict"] == "VERDICT: CORRECT"


def test_find_reverify_targets_skips_historically_broken_items(tmp_path: Path):
    run_dir = tmp_path / "run"

    workers1 = run_dir / "steps" / "step_001" / "workers"
    workers1.mkdir(parents=True)
    (workers1 / "task_0.md").write_text("task 1")
    (workers1 / "result_0.md").write_text("result 1")
    (workers1 / "worker_0_call.md").write_text("worker archive 1")
    (workers1 / "verifier_result_0.md").write_text("VERDICT: CORRECT\n")

    workers2 = run_dir / "steps" / "step_002" / "workers"
    workers2.mkdir(parents=True)
    (workers2 / "task_0.md").write_text("task 2")
    (workers2 / "result_0.md").write_text("result 2")
    (workers2 / "worker_0_call.md").write_text("worker archive 2")
    (workers2 / "verifier_result_0.md").write_text(
        "VERDICT: NEEDS MINOR FIXES - wording\n"
    )

    workers3 = run_dir / "steps" / "step_003" / "workers"
    workers3.mkdir(parents=True)
    (workers3 / "task_0.md").write_text("task 3")
    (workers3 / "result_0.md").write_text("result 3")
    (workers3 / "worker_0_call.md").write_text("worker archive 3")
    (workers3 / "verifier_result_0.md").write_text(
        "VERDICT: CRITICALLY FLAWED - wrong proof\n"
    )

    targets = _find_reverify_targets(
        run_dir, step_filter=None, worker_filter=None
    )

    assert [(t["step_num"], t["worker_idx"]) for t in targets] == [(1, 0)]


def test_load_existing_reverify_rows_recovers_completed_items_without_summary(tmp_path: Path):
    out_dir = tmp_path / "run" / "reverify" / "20260401-010203"
    worker_dir = out_dir / "step_005" / "worker_0"
    worker_dir.mkdir(parents=True)
    (worker_dir / "original_verifier_result.md").write_text("VERDICT: CORRECT\n")
    (worker_dir / "reverify_result.md").write_text(
        "This is broken\nVERDICT: NEEDS MINOR FIXES - issue\n"
    )
    (worker_dir / "repaired_worker_output.md").write_text("repaired")
    (worker_dir / "reverify_repaired_result.md").write_text(
        "Looks good now\nVERDICT: CORRECT\n"
    )

    rows = _load_existing_reverify_rows(
        out_dir,
        provider="codex",
        model="gpt-5.4",
        reasoning_effort="xhigh",
    )

    assert len(rows) == 1
    assert rows[0]["step"] == 5
    assert rows[0]["worker"] == 0
    assert rows[0]["new_provider"] == "codex"
    assert rows[0]["new_requested_model"] == "gpt-5.4"
    assert rows[0]["new_reasoning_effort"] == "xhigh"
    assert rows[0]["initial_new_verdict"] == "VERDICT: NEEDS MINOR FIXES - issue"
    assert rows[0]["repaired"] is True
    assert rows[0]["new_verdict"] == "VERDICT: CORRECT"


def test_unrepaired_failed_row_is_not_complete_in_repair_mode():
    row = {
        "step": 5,
        "worker": 0,
        "new_verdict": "VERDICT: NEEDS MINOR FIXES - issue",
        "repaired": False,
    }

    assert _is_reverify_row_complete(row, repair_broken=False) is True
    assert _is_reverify_row_complete(row, repair_broken=True) is False


def test_repaired_or_correct_rows_count_as_complete_in_repair_mode():
    repaired_row = {
        "step": 5,
        "worker": 0,
        "new_verdict": "VERDICT: NEEDS MINOR FIXES - still broken",
        "repaired": True,
    }
    correct_row = {
        "step": 6,
        "worker": 0,
        "new_verdict": "VERDICT: CORRECT",
        "repaired": False,
    }

    assert _is_reverify_row_complete(repaired_row, repair_broken=True) is True
    assert _is_reverify_row_complete(correct_row, repair_broken=True) is True


def test_find_resumable_reverify_dir_matches_latest_with_same_settings(tmp_path: Path):
    run_dir = tmp_path / "run"
    old_dir = run_dir / "reverify" / "20260401-010203"
    new_dir = run_dir / "reverify" / "20260401-020304"
    mismatch_dir = run_dir / "reverify" / "20260401-030405"
    for d in (old_dir, new_dir, mismatch_dir):
        d.mkdir(parents=True)

    _write_reverify_outputs(
        old_dir,
        run_dir=run_dir,
        provider="codex",
        model="gpt-5.4",
        reasoning_effort="xhigh",
        repair_broken=True,
        step_filter=None,
        worker_filter=None,
        summary_rows=[{
            "step": 5,
            "worker": 0,
            "original_provider": "",
            "original_requested_model": "",
            "original_model": "",
            "original_reasoning_effort": "",
            "original_verdict": "VERDICT: CORRECT",
            "new_provider": "codex",
            "new_requested_model": "gpt-5.4",
            "new_model": "gpt-5.4",
            "new_reasoning_effort": "xhigh",
            "new_verdict": "VERDICT: CORRECT",
            "repaired": False,
            "path": str(old_dir / "step_005" / "worker_0"),
        }],
        target_count=2,
    )
    _write_reverify_outputs(
        new_dir,
        run_dir=run_dir,
        provider="codex",
        model="gpt-5.4",
        reasoning_effort="xhigh",
        repair_broken=True,
        step_filter=None,
        worker_filter=None,
        summary_rows=[{
            "step": 9,
            "worker": 0,
            "original_provider": "",
            "original_requested_model": "",
            "original_model": "",
            "original_reasoning_effort": "",
            "original_verdict": "VERDICT: CORRECT",
            "new_provider": "codex",
            "new_requested_model": "gpt-5.4",
            "new_model": "gpt-5.4",
            "new_reasoning_effort": "xhigh",
            "new_verdict": "VERDICT: CORRECT",
            "repaired": False,
            "path": str(new_dir / "step_009" / "worker_0"),
        }],
        target_count=3,
    )
    _write_reverify_outputs(
        mismatch_dir,
        run_dir=run_dir,
        provider="codex",
        model="gpt-5.4",
        reasoning_effort="high",
        repair_broken=True,
        step_filter=None,
        worker_filter=None,
        summary_rows=[],
        target_count=0,
    )

    out_dir, rows = _find_resumable_reverify_dir(
        run_dir,
        provider="codex",
        model="gpt-5.4",
        reasoning_effort="xhigh",
        repair_broken=True,
        step_filter=None,
        worker_filter=None,
    )

    assert out_dir == new_dir
    assert len(rows) == 1
    assert rows[0]["step"] == 9


def test_find_resumable_reverify_dir_allows_repair_run_to_resume_quick_audit_bundle(tmp_path: Path):
    run_dir = tmp_path / "run"
    audit_dir = run_dir / "reverify" / "20260401-010203"
    audit_dir.mkdir(parents=True)

    _write_reverify_outputs(
        audit_dir,
        run_dir=run_dir,
        provider="codex",
        model="gpt-5.4",
        reasoning_effort="xhigh",
        repair_broken=False,
        step_filter=None,
        worker_filter=None,
        summary_rows=[{
            "step": 5,
            "worker": 0,
            "original_provider": "",
            "original_requested_model": "",
            "original_model": "",
            "original_reasoning_effort": "",
            "original_verdict": "VERDICT: CORRECT",
            "new_provider": "codex",
            "new_requested_model": "gpt-5.4",
            "new_model": "gpt-5.4",
            "new_reasoning_effort": "xhigh",
            "new_verdict": "VERDICT: CORRECT",
            "repaired": False,
            "path": str(audit_dir / "step_005" / "worker_0"),
        }],
        target_count=2,
    )

    out_dir, rows = _find_resumable_reverify_dir(
        run_dir,
        provider="codex",
        model="gpt-5.4",
        reasoning_effort="xhigh",
        repair_broken=True,
        step_filter=None,
        worker_filter=None,
    )

    assert out_dir == audit_dir
    assert len(rows) == 1
    assert rows[0]["step"] == 5
