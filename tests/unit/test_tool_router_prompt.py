from app.prompts.tool_router_v3 import (
    TOOL_ROUTER_PROMPT_VERSION,
    build_tool_router_prompt,
)


def test_tool_router_prompt_includes_message_and_tool_names() -> None:
    prompt = build_tool_router_prompt("What is 25 * 18?")

    assert "What is 25 * 18?" in prompt
    assert "calculator" in prompt
    assert "date_time" in prompt
    assert "text_summarizer" in prompt
    assert "file_analyzer" in prompt
    assert "none" in prompt


def test_tool_router_prompt_requires_json_only_output() -> None:
    prompt = build_tool_router_prompt("Summarize this text.")

    assert "Return only valid JSON" in prompt
    assert "no markdown or extra text" in prompt


def test_tool_router_prompt_version_is_set() -> None:
    assert TOOL_ROUTER_PROMPT_VERSION == "v3.1"

