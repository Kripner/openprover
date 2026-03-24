from pathlib import Path

from openprover.budget import Budget
from openprover.llm import QuotaExceeded
from openprover.prover import Prover
from openprover.tui.headless import HeadlessTUI


class _PlannerQuotaLLM:
    model = "fake-planner"
    context_length = 200_000

    def call(self, **_kwargs):
        raise QuotaExceeded("Claude CLI streaming error: You've hit your limit")

    def clear_interrupt(self):
        pass


class _PlannerSpawnLLM:
    model = "fake-planner"
    context_length = 200_000

    def call(self, **_kwargs):
        return {
            "result": (
                "<OPENPROVER_ACTION>\n"
                'action = "spawn"\n'
                'summary = "do work"\n'
                "\n"
                "[[tasks]]\n"
                'summary = "worker task"\n'
                'description = """\n'
                "Investigate.\n"
                '"""\n'
                "</OPENPROVER_ACTION>"
            ),
            "thinking": "",
            "cost": 0.0,
            "duration_ms": 1,
            "raw": {"model": self.model, "stop_reason": "end_turn", "usage": {}},
            "finish_reason": "end_turn",
        }

    def clear_interrupt(self):
        pass


class _WorkerQuotaLLM:
    model = "fake-worker"
    context_length = 200_000

    def __init__(self):
        self.calls = 0

    def call(self, **_kwargs):
        self.calls += 1
        raise QuotaExceeded("Claude CLI streaming error: You've hit your limit")

    def clear_interrupt(self):
        pass

    def clear_soft_interrupt(self):
        pass


def test_run_stops_cleanly_when_planner_hits_quota(tmp_path: Path):
    work_dir = tmp_path / "run"
    tui = HeadlessTUI()
    tui._sync_step_log_line = lambda *_args, **_kwargs: None

    prover = Prover(
        work_dir=work_dir,
        theorem_text="Test theorem",
        mode="prove",
        make_llm=lambda _wd: _PlannerQuotaLLM(),
        model_name="fake",
        budget=Budget("time", 3600),
        autonomous=True,
        verbose=False,
        tui=tui,
    )

    prover.run()

    meta = (work_dir / "steps" / "step_001" / "meta.toml").read_text()
    assert 'status = "quota_exceeded"' in meta
    assert not (work_dir / "DISCUSSION.md").exists()


def test_worker_quota_skips_verifier_and_pauses_run(tmp_path: Path):
    work_dir = tmp_path / "run"
    tui = HeadlessTUI()
    tui._sync_step_log_line = lambda *_args, **_kwargs: None
    worker_llm = _WorkerQuotaLLM()

    prover = Prover(
        work_dir=work_dir,
        theorem_text="Test theorem",
        mode="prove",
        make_llm=lambda _wd: _PlannerSpawnLLM(),
        make_worker_llm=lambda _wd: worker_llm,
        model_name="fake",
        budget=Budget("time", 3600),
        autonomous=True,
        verbose=False,
        tui=tui,
    )

    prover.run()

    meta = (work_dir / "steps" / "step_001" / "meta.toml").read_text()
    assert 'status = "quota_exceeded"' in meta
    assert worker_llm.calls == 1
    assert not (work_dir / "steps" / "step_001" / "workers" / "verifier_result_0.md").exists()
    assert not (work_dir / "DISCUSSION.md").exists()
