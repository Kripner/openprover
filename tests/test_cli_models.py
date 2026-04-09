import argparse
from argparse import Namespace
from pathlib import Path

import pytest

from openprover.cli import (
    _cmd_reverify,
    _infer_legacy_saved_provider,
    _default_reasoning_effort,
    _display_model,
    _load_run_config,
    _migrate_compatible_run_config,
    _resolve_reasoning_effort,
    _resolve_provider_and_model,
    _restore_saved_provider_model_args,
    _restore_saved_reasoning_effort_args,
)


def _parser() -> argparse.ArgumentParser:
    return argparse.ArgumentParser(prog="openprover")


def test_default_model_selection_uses_claude_sonnet():
    provider, model = _resolve_provider_and_model(
        _parser(),
        provider=None,
        provider_explicit=False,
        model=None,
        model_explicit=False,
        role="planner",
    )

    assert provider == "claude"
    assert model == "sonnet"


def test_codex_provider_without_model_uses_cli_default():
    provider, model = _resolve_provider_and_model(
        _parser(),
        provider="codex",
        provider_explicit=True,
        model=None,
        model_explicit=False,
        role="worker",
    )

    assert provider == "codex"
    assert model == "codex"


def test_codex_provider_accepts_actual_model_name():
    provider, model = _resolve_provider_and_model(
        _parser(),
        provider="codex",
        provider_explicit=True,
        model="gpt-5.4",
        model_explicit=True,
        role="worker",
    )

    assert provider == "codex"
    assert model == "gpt-5.4"


def test_prefixed_codex_model_infers_provider():
    provider, model = _resolve_provider_and_model(
        _parser(),
        provider=None,
        provider_explicit=False,
        model="codex:gpt-5.2",
        model_explicit=True,
        role="worker",
    )

    assert provider == "codex"
    assert model == "gpt-5.2"


def test_codex_provider_rejects_foreign_built_in_alias():
    with pytest.raises(SystemExit):
        _resolve_provider_and_model(
            _parser(),
            provider="codex",
            provider_explicit=True,
            model="opus",
            model_explicit=True,
            role="worker",
        )


def test_display_model_avoids_stale_claude_version_strings():
    assert _display_model("claude", "sonnet") == "sonnet"
    assert _display_model("codex", "gpt-5.2") == "codex gpt-5.2"


def test_claude_reasoning_effort_accepts_high():
    assert _resolve_reasoning_effort(
        _parser(),
        provider="claude",
        reasoning_effort="high",
        role="planner",
    ) == "high"


def test_claude_reasoning_effort_defaults_to_high():
    assert _resolve_reasoning_effort(
        _parser(),
        provider="claude",
        reasoning_effort=None,
        role="planner",
    ) == "high"


def test_codex_reasoning_effort_defaults_to_high():
    assert _resolve_reasoning_effort(
        _parser(),
        provider="codex",
        reasoning_effort=None,
        role="worker",
    ) == "high"


def test_local_reasoning_effort_defaults_to_none():
    assert _resolve_reasoning_effort(
        _parser(),
        provider="local",
        reasoning_effort=None,
        role="worker",
    ) is None


def test_verifier_default_reasoning_effort_uses_strongest_available():
    assert _default_reasoning_effort("claude", "verifier") == "max"
    assert _default_reasoning_effort("codex", "verifier") == "xhigh"
    assert _default_reasoning_effort("local", "verifier") is None


def test_codex_reasoning_effort_accepts_xhigh():
    assert _resolve_reasoning_effort(
        _parser(),
        provider="codex",
        reasoning_effort="xhigh",
        role="worker",
    ) == "xhigh"


def test_local_reasoning_effort_is_rejected():
    with pytest.raises(SystemExit):
        _resolve_reasoning_effort(
            _parser(),
            provider="local",
            reasoning_effort="high",
            role="worker",
        )


def test_resume_explicit_provider_skips_saved_model_and_provider(monkeypatch: pytest.MonkeyPatch):
    args = Namespace(
        planner_model=None,
        worker_model=None,
        planner_provider=None,
        worker_provider=None,
    )
    saved = {
        "planner_model": "opus",
        "worker_model": "opus",
        "planner_provider": "claude",
        "worker_provider": "claude",
    }

    monkeypatch.setattr("openprover.cli.sys.argv", ["openprover", "--provider", "codex"])
    _restore_saved_provider_model_args(args, saved)

    assert args.planner_model is None
    assert args.worker_model is None
    assert args.planner_provider is None
    assert args.worker_provider is None


def test_resume_explicit_model_skips_saved_provider_and_model(monkeypatch: pytest.MonkeyPatch):
    args = Namespace(
        planner_model=None,
        worker_model=None,
        planner_provider=None,
        worker_provider=None,
    )
    saved = {
        "planner_model": "sonnet",
        "worker_model": "sonnet",
        "planner_provider": "claude",
        "worker_provider": "claude",
    }

    monkeypatch.setattr("openprover.cli.sys.argv", ["openprover", "--model", "codex:gpt-5.4"])
    _restore_saved_provider_model_args(args, saved)

    assert args.planner_model is None
    assert args.worker_model is None
    assert args.planner_provider is None
    assert args.worker_provider is None


def test_resume_explicit_provider_skips_saved_reasoning_effort(monkeypatch: pytest.MonkeyPatch):
    args = Namespace(
        planner_reasoning_effort=None,
        worker_reasoning_effort=None,
    )
    saved = {
        "planner_reasoning_effort": "max",
        "worker_reasoning_effort": "max",
    }

    monkeypatch.setattr("openprover.cli.sys.argv", ["openprover", "--provider", "codex"])
    _restore_saved_reasoning_effort_args(args, saved)

    assert args.planner_reasoning_effort is None
    assert args.worker_reasoning_effort is None


def test_resume_without_override_restores_saved_reasoning_effort(monkeypatch: pytest.MonkeyPatch):
    args = Namespace(
        planner_reasoning_effort=None,
        worker_reasoning_effort=None,
    )
    saved = {
        "planner_reasoning_effort": "high",
        "worker_reasoning_effort": "xhigh",
    }

    monkeypatch.setattr("openprover.cli.sys.argv", ["openprover"])
    _restore_saved_reasoning_effort_args(args, saved)

    assert args.planner_reasoning_effort == "high"
    assert args.worker_reasoning_effort == "xhigh"


def test_v100_run_config_is_migrated_to_v101(tmp_path):
    config = tmp_path / "run_config.toml"
    config.write_text(
        'version = "1.0.0"\n'
        'planner_model = "opus"\n'
        'worker_model = "opus"\n'
        'budget_mode = "time"\n'
        'budget_limit = 3600\n'
        'conclude_after = 0.99\n'
        'parallelism = 1\n'
        'give_up_ratio = 0.5\n'
        'isolation = false\n'
        'autonomous = true\n'
        'mode = "prove"\n'
        'lean_project_dir = ""\n'
        'lean_items = false\n'
        'lean_worker_tools = false\n'
        'provider_url = "http://localhost:8000"\n'
        'answer_reserve = 4096\n'
        'history_budget = 0\n'
    )

    saved = _load_run_config(tmp_path)
    migrated = _migrate_compatible_run_config(_parser(), tmp_path, saved)

    assert migrated["version"] == "1.0.1"
    assert migrated["planner_provider"] == "claude"
    assert migrated["worker_provider"] == "claude"
    assert migrated["planner_model"] == "opus"
    assert migrated["worker_model"] == "opus"
    assert "give_up_ratio" not in migrated


def test_v100_codex_run_config_with_explicit_model_is_migrated(tmp_path):
    config = tmp_path / "run_config.toml"
    config.write_text(
        'version = "1.0.0"\n'
        'planner_model = "gpt-5.4"\n'
        'worker_model = "gpt-5.4"\n'
        'budget_mode = "time"\n'
        'budget_limit = 3600\n'
        'conclude_after = 0.99\n'
        'parallelism = 1\n'
        'give_up_ratio = 0.5\n'
        'isolation = true\n'
        'autonomous = false\n'
        'mode = "prove"\n'
        'lean_project_dir = ""\n'
        'lean_items = false\n'
        'lean_worker_tools = false\n'
        'provider_url = "http://localhost:8000"\n'
        'answer_reserve = 4096\n'
        'history_budget = 0\n'
    )

    saved = _load_run_config(tmp_path)
    migrated = _migrate_compatible_run_config(_parser(), tmp_path, saved)

    assert migrated["version"] == "1.0.1"
    assert migrated["planner_provider"] == "codex"
    assert migrated["worker_provider"] == "codex"
    assert migrated["planner_model"] == "gpt-5.4"
    assert migrated["worker_model"] == "gpt-5.4"


def test_legacy_saved_provider_infers_codex_for_explicit_model():
    assert _infer_legacy_saved_provider(None, "gpt-5.4") == "codex"


def test_reverify_uses_migrated_codex_backend_from_v100_run(monkeypatch, tmp_path, capsys):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    (run_dir / "run_config.toml").write_text(
        'version = "1.0.0"\n'
        'planner_model = "gpt-5.4"\n'
        'worker_model = "gpt-5.4"\n'
        'budget_mode = "time"\n'
        'budget_limit = 3600\n'
        'conclude_after = 0.99\n'
        'parallelism = 1\n'
        'give_up_ratio = 0.5\n'
        'isolation = true\n'
        'autonomous = false\n'
        'mode = "prove"\n'
        'lean_project_dir = ""\n'
        'lean_items = false\n'
        'lean_worker_tools = false\n'
        'provider_url = "http://localhost:8000"\n'
        'answer_reserve = 4096\n'
        'history_budget = 0\n'
    )

    captured = {}

    class _DummyClient:
        model = "gpt-5.4"

        def cleanup(self):
            pass

    monkeypatch.setattr(
        "openprover.cli.sys.argv",
        ["openprover", "reverify", str(run_dir), "--no-resume"],
    )
    monkeypatch.setattr(
        "openprover.cli._find_reverify_targets",
        lambda *_args, **_kwargs: [{
            "step_num": 1,
            "worker_idx": 0,
            "task_path": run_dir / "steps" / "step_001" / "workers" / "task_0.md",
            "result_path": run_dir / "steps" / "step_001" / "workers" / "result_0.md",
            "original_verifier_result": run_dir / "steps" / "step_001" / "workers" / "verifier_result_0.md",
            "original_verifier_call": run_dir / "steps" / "step_001" / "workers" / "verifier_0_call.md",
            "original_verdict": "VERDICT: CORRECT",
        }],
    )
    monkeypatch.setattr(
        "openprover.cli._make_client",
        lambda provider, model, _archive_dir, reasoning_effort, **_kwargs: (
            captured.update({
                "provider": provider,
                "model": model,
                "reasoning_effort": reasoning_effort,
            }) or _DummyClient()
        ),
    )
    monkeypatch.setattr(
        "openprover.cli._run_standalone_verifier",
        lambda *_args, **_kwargs: {"result": "VERDICT: CORRECT"},
    )
    monkeypatch.setattr(
        "openprover.cli._load_call",
        lambda _path: None,
        raising=False,
    )

    workers_dir = run_dir / "steps" / "step_001" / "workers"
    workers_dir.mkdir(parents=True)
    (workers_dir / "task_0.md").write_text("task")
    (workers_dir / "result_0.md").write_text("result")
    (workers_dir / "verifier_result_0.md").write_text("VERDICT: CORRECT\n")

    _cmd_reverify()
    capsys.readouterr()

    assert captured["provider"] == "codex"
    assert captured["model"] == "gpt-5.4"
    assert captured["reasoning_effort"] == "xhigh"


def test_reverify_restores_saved_provider_url_and_answer_reserve(monkeypatch, tmp_path, capsys):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    (run_dir / "run_config.toml").write_text(
        'version = "1.0.1"\n'
        'planner_model = "minimax-m2.5"\n'
        'worker_model = "minimax-m2.5"\n'
        'planner_provider = "local"\n'
        'worker_provider = "local"\n'
        'planner_reasoning_effort = ""\n'
        'worker_reasoning_effort = ""\n'
        'budget_mode = "time"\n'
        'budget_limit = 3600\n'
        'conclude_after = 0.99\n'
        'parallelism = 1\n'
        'isolation = true\n'
        'autonomous = false\n'
        'mode = "prove"\n'
        'lean_project_dir = ""\n'
        'lean_items = false\n'
        'lean_worker_tools = false\n'
        'provider_url = "http://localhost:9999"\n'
        'answer_reserve = 8192\n'
        'history_budget = 0\n'
    )

    captured = {}

    class _DummyClient:
        model = "MiniMaxAI/MiniMax-M2.5"

        def cleanup(self):
            pass

    monkeypatch.setattr(
        "openprover.cli.sys.argv",
        ["openprover", "reverify", str(run_dir), "--no-resume"],
    )
    monkeypatch.setattr(
        "openprover.cli._find_reverify_targets",
        lambda *_args, **_kwargs: [{
            "step_num": 1,
            "worker_idx": 0,
            "task_path": run_dir / "steps" / "step_001" / "workers" / "task_0.md",
            "result_path": run_dir / "steps" / "step_001" / "workers" / "result_0.md",
            "original_verifier_result": run_dir / "steps" / "step_001" / "workers" / "verifier_result_0.md",
            "original_verifier_call": run_dir / "steps" / "step_001" / "workers" / "verifier_0_call.md",
            "original_verdict": "VERDICT: CORRECT",
        }],
    )
    monkeypatch.setattr(
        "openprover.cli._make_client",
        lambda provider, model, _archive_dir, reasoning_effort, **kwargs: (
            captured.update({
                "provider": provider,
                "model": model,
                "reasoning_effort": reasoning_effort,
                "provider_url": kwargs["provider_url"],
                "answer_reserve": kwargs["answer_reserve"],
            }) or _DummyClient()
        ),
    )
    monkeypatch.setattr(
        "openprover.cli._run_standalone_verifier",
        lambda *_args, **_kwargs: {"result": "VERDICT: CORRECT"},
    )
    monkeypatch.setattr(
        "openprover.cli._load_call",
        lambda _path: None,
        raising=False,
    )

    workers_dir = run_dir / "steps" / "step_001" / "workers"
    workers_dir.mkdir(parents=True)
    (workers_dir / "task_0.md").write_text("task")
    (workers_dir / "result_0.md").write_text("result")
    (workers_dir / "verifier_result_0.md").write_text("VERDICT: CORRECT\n")

    _cmd_reverify()
    capsys.readouterr()

    assert captured["provider"] == "local"
    assert captured["model"] == "minimax-m2.5"
    assert captured["reasoning_effort"] is None
    assert captured["provider_url"] == "http://localhost:9999"
    assert captured["answer_reserve"] == 8192
