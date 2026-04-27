from unittest.mock import patch

import pytest

from app.schemas.structured import StructuredLLMResponse
from app.services.llm_service import LLMServiceError
from app.services.structured_llm_service import (
    StructuredLLMServiceError,
    build_structured_fallback_response,
    generate_structured_answer,
)


def test_generate_structured_answer_returns_valid_response() -> None:
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

    with patch("app.services.structured_llm_service.generate_answer", return_value=raw_output):
        result = generate_structured_answer("Explain missing values.")

    assert isinstance(result, StructuredLLMResponse)
    assert result.answer == "Missing values are empty entries."


def test_generate_structured_answer_converts_llm_service_error() -> None:
    with patch(
        "app.services.structured_llm_service.generate_answer",
        side_effect=LLMServiceError("LLM request timed out."),
    ):
        with pytest.raises(StructuredLLMServiceError, match="LLM request timed out."):
            generate_structured_answer("Hello")


def test_generate_structured_answer_retries_after_parse_error() -> None:
    valid_raw_output = """
    {
      "answer": "Missing values are empty entries.",
      "confidence": "high",
      "reasoning_summary": "The user asked for a definition.",
      "next_action": "No tool required.",
      "prompt_version": "v2.1",
      "status": "success"
    }
    """

    with patch(
        "app.services.structured_llm_service.generate_answer",
        side_effect=["{bad json", valid_raw_output],
    ) as mock_generate_answer:
        result = generate_structured_answer("Hello")

    assert mock_generate_answer.call_count == 2
    assert result.status == "success"
    assert result.answer == "Missing values are empty entries."


def test_generate_structured_answer_returns_fallback_after_retry_fails() -> None:
    with patch("app.services.structured_llm_service.generate_answer", return_value="{bad json"):
        result = generate_structured_answer("Hello")

    assert result.status == "failed"
    assert result.confidence == "low"
    assert result.answer == "I could not generate a valid structured response."


def test_build_structured_fallback_response_returns_valid_response() -> None:
    result = build_structured_fallback_response()

    assert isinstance(result, StructuredLLMResponse)
    assert result.status == "failed"
