import pytest
from pydantic import ValidationError

from app.schemas.structured import StructuredLLMResponse


def test_structured_response_accepts_valid_data() -> None:
    response = StructuredLLMResponse(
        answer="Missing values are empty entries in a dataset.",
        confidence="high",
        reasoning_summary="The user asked a conceptual data question.",
        next_action="No tool required.",
        prompt_version="v2.1",
        status="success",
    )

    assert response.confidence == "high"


def test_structured_response_rejects_invalid_confidence() -> None:
    with pytest.raises(ValidationError):
        StructuredLLMResponse(
            answer="Answer.",
            confidence="certain",
            reasoning_summary="Summary.",
            next_action="No tool required.",
            prompt_version="v2.1",
            status="success",
        )


def test_structured_response_rejects_invalid_status() -> None:
    with pytest.raises(ValidationError):
        StructuredLLMResponse(
            answer="Answer.",
            confidence="medium",
            reasoning_summary="Summary.",
            next_action="No tool required.",
            prompt_version="v2.1",
            status="ok",
        )


def test_structured_response_rejects_blank_text_fields() -> None:
    with pytest.raises(ValidationError):
        StructuredLLMResponse(
            answer=" ",
            confidence="low",
            reasoning_summary="Summary.",
            next_action="Retry.",
            prompt_version="v2.1",
            status="failed",
        )
