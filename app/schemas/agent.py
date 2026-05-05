from typing import Any, Literal

from pydantic import BaseModel, field_validator


ToolName = Literal["calculator", "date_time", "text_summarizer", "file_analyzer", "none"]
ToolStatus = Literal["success", "failed", "skipped"]


class AgentQueryRequest(BaseModel):
    message: str

    @field_validator("message")
    @classmethod
    def message_must_not_be_blank(cls, value: str) -> str:
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError("Message must not be empty.")
        return cleaned_value


class ToolDecision(BaseModel):
    tool_name: ToolName
    tool_input: dict[str, Any]
    reason: str

    @field_validator("reason")
    @classmethod
    def reason_must_not_be_blank(cls, value: str) -> str:
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError("Reason must not be empty.")
        return cleaned_value


class AgentQueryResponse(BaseModel):
    answer: str
    confidence: Literal["low", "medium", "high"]
    tool_used: ToolName
    tool_input: dict[str, Any]
    tool_output_summary: str
    tool_status: ToolStatus
    status: Literal["success", "failed"]

    @field_validator("answer", "tool_output_summary")
    @classmethod
    def response_text_fields_must_not_be_blank(cls, value: str) -> str:
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError("Field must not be empty.")
        return cleaned_value
