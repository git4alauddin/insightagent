from typing import Literal

from pydantic import BaseModel, Field, field_validator


class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    status: Literal["uploaded", "indexed"]


class DocumentAskRequest(BaseModel):
    question: str

    @field_validator("question")
    @classmethod
    def question_must_not_be_blank(cls, value: str) -> str:
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError("Question must not be empty.")
        return cleaned_value


class SourceCitation(BaseModel):
    filename: str
    chunk_id: str
    similarity_score: float = Field(ge=0.0, le=1.0)
    page: int | None = Field(default=None, ge=1)


class DocumentAskResponse(BaseModel):
    answer: str
    confidence: Literal["low", "medium", "high"]
    document_id: str
    sources: list[SourceCitation]
    status: Literal["success", "insufficient_context", "failed"]

    @field_validator("answer")
    @classmethod
    def answer_must_not_be_blank(cls, value: str) -> str:
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError("Answer must not be empty.")
        return cleaned_value
