import argparse
from argparse import Namespace

import pytest

from openprover.cli import (
    _display_model,
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
