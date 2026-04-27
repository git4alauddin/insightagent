from app.prompts.structured_v2 import (
    STRUCTURED_PROMPT_VERSION,
    build_structured_prompt,
)


def test_structured_prompt_includes_user_message_and_version() -> None:
    prompt = build_structured_prompt("Explain missing values.")

    assert "Explain missing values." in prompt
    assert STRUCTURED_PROMPT_VERSION in prompt


def test_structured_prompt_requires_json_only() -> None:
    prompt = build_structured_prompt("Hello")

    assert "Return only valid JSON" in prompt
    assert "Do not include markdown" in prompt
    assert "Do not reveal hidden chain-of-thought" in prompt
