import importlib
import sys
from types import SimpleNamespace

import pytest


def _import_cli_with_stubbed_tty(monkeypatch: pytest.MonkeyPatch):
    dummy_termios = SimpleNamespace(
        TCSADRAIN=0,
        tcgetattr=lambda *args, **kwargs: None,
        tcsetattr=lambda *args, **kwargs: None,
    )
    dummy_tty = SimpleNamespace(setcbreak=lambda *args, **kwargs: None)
    monkeypatch.setitem(sys.modules, "termios", dummy_termios)
    monkeypatch.setitem(sys.modules, "tty", dummy_tty)
    for name in [
        "openprover.cli",
        "openprover.prover",
        "openprover.tui",
        "openprover.tui.tui",
    ]:
        sys.modules.pop(name, None)
    return importlib.import_module("openprover.cli")


def test_no_isolation_requires_web_search_capable_worker(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
    capsys: pytest.CaptureFixture[str],
):
    theorem = tmp_path / "theorem.md"
    theorem.write_text("Prove that 1 = 1.")

    cli = _import_cli_with_stubbed_tty(monkeypatch)
    monkeypatch.setattr(
        cli.sys,
        "argv",
        [
            "openprover",
            "--theorem",
            str(theorem),
            "--planner-model",
            "opus",
            "--worker-model",
            "minimax-m2.5",
            "--no-isolation",
            "--headless",
            "--max-time",
            "1s",
        ],
    )

    with pytest.raises(SystemExit) as exc:
        cli._cmd_prove()

    assert exc.value.code == 2
    err = capsys.readouterr().err
    assert "--no-isolation requires a web-search-capable worker model" in err
