import pytest

from app.tools.text_summarizer import (
    TextSummarizerToolError,
    summarize_text,
    text_summarizer_tool,
)


def test_summarize_text_returns_same_text_when_short() -> None:
    text = "This is a short text."
    assert summarize_text(text) == text


def test_summarize_text_truncates_long_text() -> None:
    text = "word " * 60
    summary = summarize_text(text.strip(), max_words=10)

    assert summary.endswith("...")
    assert len(summary.split()) == 10


def test_text_summarizer_tool_returns_summary() -> None:
    result = text_summarizer_tool({"text": "This is a concise technical summary input."})
    assert "concise technical summary" in result


def test_text_summarizer_tool_rejects_blank_text() -> None:
    with pytest.raises(TextSummarizerToolError, match="Invalid text_summarizer tool input"):
        text_summarizer_tool({"text": "   "})


def test_text_summarizer_tool_rejects_non_string_text() -> None:
    with pytest.raises(TextSummarizerToolError, match="Invalid text_summarizer tool input"):
        text_summarizer_tool({"text": 123})

