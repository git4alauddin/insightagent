from typing import Literal

from pydantic import BaseModel, field_validator


class DatasetUploadResponse(BaseModel):
    dataset_id: str
    filename: str
    rows: int
    columns: int
    status: Literal["uploaded"]


class DatasetSummaryResponse(BaseModel):
    dataset_id: str
    rows: int
    columns: int
    column_names: list[str]
    missing_values: dict[str, int]
    numeric_columns: list[str]
    categorical_columns: list[str]


class DatasetAskRequest(BaseModel):
    question: str

    @field_validator("question")
    @classmethod
    def question_must_not_be_blank(cls, value: str) -> str:
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError("Question must not be empty.")
        return cleaned_value


class DatasetAnalysisTrace(BaseModel):
    intent: str
    tool_used: str
    columns_used: list[str]
    operation: str


class DatasetAskResponse(BaseModel):
    answer: str
    confidence: Literal["low", "medium", "high"]
    dataset_id: str
    tool_used: str
    tool_output_summary: str
    analysis_trace: DatasetAnalysisTrace
    status: Literal["success", "failed"]

    @field_validator("answer", "tool_output_summary")
    @classmethod
    def response_text_must_not_be_blank(cls, value: str) -> str:
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError("Field must not be empty.")
        return cleaned_value
