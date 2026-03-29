import pytest

from openprover.llm import QuotaExceeded
from openprover.llm.codex import CodexClient, _infer_context_length


def _make_client(monkeypatch: pytest.MonkeyPatch, tmp_path, **kwargs) -> CodexClient:
    monkeypatch.setattr(CodexClient, "_start_server", lambda self: None)
    client = CodexClient("gpt-5.4", tmp_path, **kwargs)
    monkeypatch.setattr(client, "_ensure_server", lambda: None)
    return client


def test_infer_context_length_uses_gpt5_family_window():
    assert _infer_context_length("gpt-5.4") == 400_000
    assert _infer_context_length("codex") == 200_000


def test_codex_client_is_tool_capable(monkeypatch: pytest.MonkeyPatch, tmp_path):
    client = _make_client(monkeypatch, tmp_path)

    assert client.supports_mcp_tools is True
    assert client.answer_reserve == 4096


def test_call_uses_requested_reasoning_effort(monkeypatch: pytest.MonkeyPatch, tmp_path):
    requests: list[tuple[str, dict]] = []
    client = _make_client(monkeypatch, tmp_path, reasoning_effort="xhigh")

    def fake_rpc_request(method: str, params: dict) -> dict:
        requests.append((method, params))
        if method == "thread/start":
            return {"thread": {"id": "thread-1"}}
        if method == "turn/start":
            return {"turn": {"id": "turn-1"}}
        raise AssertionError(f"unexpected RPC method: {method}")

    monkeypatch.setattr(client, "_rpc_request", fake_rpc_request)
    monkeypatch.setattr(
        client,
        "_wait_for_turn_completed",
        lambda *args, **kwargs: (
            {"turn": {"id": "turn-1", "status": "completed"}, "items": []},
            {"result_parts": ["final answer"], "thinking_parts": ["reasoning"]},
        ),
    )

    result = client.call(
        prompt="prompt",
        system_prompt="system",
        label="worker_0",
    )

    assert result["result"] == "final answer"
    assert result["thinking"] == "reasoning"
    assert result["finish_reason"] == "stop"
    turn_start = next(params for method, params in requests if method == "turn/start")
    assert turn_start["effort"] == "xhigh"


def test_soft_interrupt_returns_soft_interrupted_finish_reason(
    monkeypatch: pytest.MonkeyPatch, tmp_path
):
    client = _make_client(monkeypatch, tmp_path)
    client.soft_interrupt()

    def fake_rpc_request(method: str, _params: dict) -> dict:
        if method == "thread/start":
            return {"thread": {"id": "thread-1"}}
        if method == "turn/start":
            return {"turn": {"id": "turn-1"}}
        raise AssertionError(f"unexpected RPC method: {method}")

    monkeypatch.setattr(client, "_rpc_request", fake_rpc_request)
    monkeypatch.setattr(
        client,
        "_wait_for_turn_completed",
        lambda *args, **kwargs: (
            {"turn": {"id": "turn-1", "status": "interrupted"}, "items": []},
            {"result_parts": ["partial output"], "thinking_parts": []},
        ),
    )

    result = client.call(
        prompt="prompt",
        system_prompt="system",
        label="worker_0",
    )

    assert result["result"] == "partial output"
    assert result["finish_reason"] == "soft_interrupted"


def test_call_raises_quota_exceeded(monkeypatch: pytest.MonkeyPatch, tmp_path):
    client = _make_client(monkeypatch, tmp_path)

    monkeypatch.setattr(
        client,
        "_rpc_request",
        lambda _method, _params: (_ for _ in ()).throw(
            RuntimeError("Too many requests: rate limit hit")
        ),
    )

    with pytest.raises(QuotaExceeded, match="Too many requests"):
        client.call(
            prompt="prompt",
            system_prompt="system",
            label="worker_0",
        )
