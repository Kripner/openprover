"""Backend capability helpers shared across the CLI and prover."""

HF_MODEL_MAP = {
    "minimax-m2.5": "MiniMaxAI/MiniMax-M2.5",
}
MISTRAL_MODEL_MAP = {
    "leanstral": "labs-leanstral-2603",
}

VLLM_MODELS = {"minimax-m2.5"}  # served via vLLM (standard OpenAI API)
MISTRAL_MODELS = {"leanstral"}  # Mistral Conversations API
CLAUDE_MODELS = {"sonnet", "opus"}
TOOL_CAPABLE_MODELS = VLLM_MODELS | CLAUDE_MODELS | MISTRAL_MODELS


def supports_web_search(model_alias: str) -> bool:
    """Whether a worker model can execute literature_search with web access."""
    return model_alias in CLAUDE_MODELS


def llm_supports_web_search(llm) -> bool:
    """Runtime web-search capability derived from the same model-alias rules."""
    model_alias = getattr(llm, "model_alias", getattr(llm, "model", ""))
    return supports_web_search(model_alias)
