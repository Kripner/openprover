import os
from pathlib import Path

from openprover.inspect import InspectTUI
from openprover.tui import TUI


def test_tui_resize_is_deferred(monkeypatch):
    tui = TUI()
    tui.rows = 24
    tui.cols = 80
    writes = []
    redraws = []

    monkeypatch.setattr(
        "openprover.tui.tui.shutil.get_terminal_size",
        lambda: os.terminal_size((100, 40)),
    )
    monkeypatch.setattr(tui, "_write", lambda data: writes.append(data))
    monkeypatch.setattr(tui, "_redraw", lambda: redraws.append("redraw"))

    tui._on_resize(None, None)

    assert tui._resize_pending is True
    assert writes == []
    assert redraws == []

    tui._apply_resize()

    assert tui._resize_pending is False
    assert tui.cols == 100
    assert tui.rows == 40
    assert writes == ["\033[2J", f"\033[{tui._content_start};40r"]
    assert redraws == ["redraw"]


def test_tui_resize_uses_default_scroll_region_for_tiny_terminal(monkeypatch):
    tui = TUI()
    tui.rows = 24
    tui.cols = 80
    writes = []

    monkeypatch.setattr(
        "openprover.tui.tui.shutil.get_terminal_size",
        lambda: os.terminal_size((12, 2)),
    )
    monkeypatch.setattr(tui, "_write", lambda data: writes.append(data))
    monkeypatch.setattr(tui, "_redraw", lambda: None)

    tui._apply_resize()

    assert tui.cols == 12
    assert tui.rows == 2
    assert writes == ["\033[2J", "\033[r"]


def test_tui_resize_pending_survives_resize_during_redraw(monkeypatch):
    tui = TUI()
    tui.rows = 24
    tui.cols = 80

    monkeypatch.setattr(
        "openprover.tui.tui.shutil.get_terminal_size",
        lambda: os.terminal_size((100, 40)),
    )
    monkeypatch.setattr(tui, "_write", lambda data: None)
    monkeypatch.setattr(tui, "_redraw", lambda: setattr(tui, "_resize_pending", True))

    tui._resize_pending = True
    tui._apply_resize()

    assert tui._resize_pending is True


def test_inspect_resize_is_deferred(monkeypatch):
    tui = InspectTUI([], run_dir=Path("/tmp/test-run"))
    tui.rows = 24
    tui.cols = 80
    draws = []

    monkeypatch.setattr(
        "openprover.inspect.shutil.get_terminal_size",
        lambda: os.terminal_size((90, 30)),
    )
    monkeypatch.setattr(tui, "_draw", lambda: draws.append("draw"))

    tui._on_resize(None, None)

    assert tui._resize_pending is True
    assert draws == []

    tui._apply_resize()

    assert tui._resize_pending is False
    assert tui.cols == 90
    assert tui.rows == 30
    assert draws == ["draw"]


def test_inspect_resize_pending_survives_resize_during_draw(monkeypatch):
    tui = InspectTUI([], run_dir=Path("/tmp/test-run"))
    tui.rows = 24
    tui.cols = 80

    monkeypatch.setattr(
        "openprover.inspect.shutil.get_terminal_size",
        lambda: os.terminal_size((90, 30)),
    )
    monkeypatch.setattr(tui, "_draw", lambda: setattr(tui, "_resize_pending", True))

    tui._resize_pending = True
    tui._apply_resize()

    assert tui._resize_pending is True
