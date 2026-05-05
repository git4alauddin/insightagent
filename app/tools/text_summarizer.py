from pydantic import ValidationError

from app.schemas.tools import TextSummarizerInput


class TextSummarizerToolError(Exception):
    pass


MAX_SUMMARY_WORDS = 40


def summarize_text(text: str, max_words: int = MAX_SUMMARY_WORDS) -> str:
    words = text.split()
    if len(words) <= max_words:
        return " ".join(words)
    return " ".join(words[:max_words]) + "..."


def text_summarizer_tool(tool_input: dict[str, object]) -> str:
    try:
        validated_input = TextSummarizerInput.model_validate(tool_input)
    except ValidationError as exc:
        raise TextSummarizerToolError("Invalid text_summarizer tool input.") from exc

    return summarize_text(validated_input.text)

