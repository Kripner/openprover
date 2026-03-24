import io
import json
import time

import pytest

from openprover.llm.codex import (
    CodexClient,
    _codex_mcp_overrides,
    _compose_prompt,
    _estimate_cost_usd,
    _extract_tool_result_text,
    _find_codex_bin,
    _infer_context_length,
    _infer_tool_status,
)


def test_compose_prompt_embeds_system_prompt():
    text = _compose_prompt("system rules", "user request")
    _, payload_text = text.split("\n\n", 1)
    payload = json.loads(payload_text)
    assert payload == {
        "system_prompt": "system rules",
        "user_prompt": "user request",
    }


def test_compose_prompt_escapes_delimiter_like_content():
    text = _compose_prompt(
        "contains ======== USER PROMPT ========",
        'and {"type":"agent_message"}',
    )
    _, payload_text = text.split("\n\n", 1)
    payload = json.loads(payload_text)
    assert payload["system_prompt"] == "contains ======== USER PROMPT ========"
    assert payload["user_prompt"] == 'and {"type":"agent_message"}'


def test_codex_mcp_overrides_accepts_claude_style_config():
    overrides = _codex_mcp_overrides({
        "mcpServers": {
            "lean_tools": {
                "command": "python",
                "args": ["-m", "openprover.lean.mcp_server"],
                "env": {
                    "LEAN_PROJECT_DIR": "C:/lean/project",
                    "LEAN_WORK_DIR": "C:/lean/work",
                },
            }
        }
    })

    assert overrides == [
        "-c", 'mcp_servers.lean_tools.command="python"',
        "-c", 'mcp_servers.lean_tools.args=["-m", "openprover.lean.mcp_server"]',
        "-c", 'mcp_servers.lean_tools.env.LEAN_PROJECT_DIR="C:/lean/project"',
        "-c", 'mcp_servers.lean_tools.env.LEAN_WORK_DIR="C:/lean/work"',
    ]


def test_find_codex_bin_prefers_native_binary_on_non_windows(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("openprover.llm.codex.sys.platform", "linux")

    def fake_which(name: str) -> str | None:
        mapping = {
            "codex": "/home/idras/.nvm/versions/node/v24.14.0/bin/codex",
            "codex.cmd": "/mnt/c/Users/idras/AppData/Roaming/npm/codex.cmd",
        }
        return mapping.get(name)

    monkeypatch.setattr("openprover.llm.codex.shutil.which", fake_which)
    assert _find_codex_bin() == "/home/idras/.nvm/versions/node/v24.14.0/bin/codex"


def test_build_cmd_includes_reasoning_effort_override(tmp_path):
    client = CodexClient("gpt-5.4", tmp_path, reasoning_effort="xhigh")

    cmd, schema_path = client._build_cmd(web_search=False, json_schema=None)

    assert schema_path is None
    assert "-m" in cmd
    assert "gpt-5.4" in cmd
    assert '-c' in cmd
    assert 'model_reasoning_effort="xhigh"' in cmd


def test_infer_context_length_uses_gpt5_family_window():
    assert _infer_context_length("gpt-5.2-codex") == 400_000
    assert _infer_context_length("codex") == 200_000


def test_estimate_cost_uses_known_pricing():
    cost = _estimate_cost_usd("gpt-5.2-codex", {
        "input_tokens": 1000,
        "cached_input_tokens": 100,
        "output_tokens": 50,
    })

    assert cost == pytest.approx(0.0022925)


def test_soft_interrupt_is_advisory(monkeypatch: pytest.MonkeyPatch, tmp_path):
    client = CodexClient("gpt-5.2-codex", tmp_path)
    called = False

    def fake_kill_active_procs():
        nonlocal called
        called = True

    monkeypatch.setattr(client, "_kill_active_procs", fake_kill_active_procs)

    client.soft_interrupt()

    assert client._soft_interrupted.is_set()
    assert called is False


def test_collect_events_keeps_completed_output_after_soft_interrupt(tmp_path):
    class _FakeProc:
        def __init__(self):
            self.stdout = io.StringIO(
                '{"type":"item.completed","item":{"type":"agent_message","text":"done"}}\n'
                '{"type":"turn.completed","usage":{"input_tokens":1000,"cached_input_tokens":100,"output_tokens":50}}\n'
            )
            self.stderr = io.StringIO("")
            self.returncode = 0

        def wait(self):
            return self.returncode

    client = CodexClient("gpt-5.2-codex", tmp_path)
    client.soft_interrupt()

    result = client._collect_events(
        proc=_FakeProc(),
        call_num=1,
        label="worker_0",
        prompt="prompt",
        system_prompt="system",
        json_schema=None,
        archive_path=None,
        start=time.time(),
        stream_callback=None,
        tool_callback=None,
        tool_start_callback=None,
    )

    assert result["result"] == "done"
    assert result["finish_reason"] == "stop"
    assert result["cost"] == pytest.approx(0.0022925)
    assert client._soft_interrupted.is_set() is False


def test_extract_tool_result_text_reads_mcp_text_content():
    result = {
        "content": [
            {"type": "text", "text": "First line"},
            {"type": "text", "text": "Second line"},
        ]
    }

    assert _extract_tool_result_text(result) == "First line\nSecond line"


def test_infer_tool_status_matches_existing_lean_conventions():
    assert _infer_tool_status("lean_verify", "OK - no errors", False) == "ok"
    assert _infer_tool_status("lean_verify", "12:3: error: bad code", False) == "error"
    assert _infer_tool_status("lean_verify", "contains sorry", False) == "partial"
    assert _infer_tool_status("lean_store", "OK - stored", False) == "ok"
    assert _infer_tool_status("lean_store", "Store rejected", False) == "error"
