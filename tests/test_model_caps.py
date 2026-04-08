from types import SimpleNamespace

from openprover.model_caps import llm_supports_web_search, supports_web_search


def test_web_search_capability_matches_worker_backend():
    assert supports_web_search("sonnet") is True
    assert supports_web_search("opus") is True
    assert supports_web_search("minimax-m2.5") is False
    assert supports_web_search("leanstral") is False


def test_llm_supports_web_search_uses_model_alias_when_present():
    claude_like = SimpleNamespace(model_alias="sonnet", model="sonnet")
    hf_like = SimpleNamespace(model_alias="minimax-m2.5", model="MiniMaxAI/MiniMax-M2.5")
    legacy_claude = SimpleNamespace(model="opus")

    assert llm_supports_web_search(claude_like) is True
    assert llm_supports_web_search(hf_like) is False
    assert llm_supports_web_search(legacy_claude) is True
