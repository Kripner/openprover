from openprover.llm.claude import LLMClient


def test_build_cmd_includes_effort_flag(tmp_path):
    client = LLMClient("sonnet", tmp_path, reasoning_effort="high")

    cmd = client._build_cmd(
        system_prompt="system",
        json_schema=None,
        web_search=False,
        use_streaming=False,
    )

    assert "--effort" in cmd
    assert "high" in cmd
