import pytest

from app.services.structured_parser import (
    StructuredOutputParseError,
    parse_structured_response,
)


def test_parse_structured_response_accepts_valid_json() -> None:
    raw_output = """
    {
      "answer": "Missing values are empty entries.",
      "confidence": "high",
      "reasoning_summary": "The user asked for a definition.",
      "next_action": "No tool required.",
      "prompt_version": "v2.1",
      "status": "success"
    }
    """

    result = parse_structured_response(raw_output)

    assert result.answer == "Missing values are empty entries."
    assert result.confidence == "high"


def test_parse_structured_response_rejects_invalid_json() -> None:
    with pytest.raises(StructuredOutputParseError, match="not valid JSON"):
        parse_structured_response("{bad json")


def test_parse_structured_response_rejects_invalid_schema() -> None:
    raw_output = """
    {
      "answer": "Answer.",
      "confidence": "certain",
      "reasoning_summary": "Summary.",
      "next_action": "No tool required.",
      "prompt_version": "v2.1",
      "status": "success"
    }
    """

    with pytest.raises(StructuredOutputParseError, match="expected schema"):
        parse_structured_response(raw_output)