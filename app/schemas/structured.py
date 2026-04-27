from typing import Literal

from pydantic import BaseModel, field_validator


ConfidenceLevel = Literal["low", "medium", "high"]
Status = Literal["success", "failed"]


class StructuredLLMResponse(BaseModel):
    answer: str
    confidence: ConfidenceLevel
    reasoning_summary: str
    next_action: str
    prompt_version: str
    status: Status

    @field_validator("answer", "reasoning_summary", "next_action", "prompt_version", "status")
    @classmethod
    def text_fields_must_not_be_blank(cls, value: str) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("Field must not be empty.")

        return cleaned_value
