from pydantic import BaseModel, field_validator


class CalculatorInput(BaseModel):
    expression: str

    @field_validator("expression")
    @classmethod
    def expression_must_not_be_blank(cls, value: str) -> str:
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError("Expression must not be empty.")
        return cleaned_value


class DateTimeInput(BaseModel):
    query: str = "current_datetime"

    @field_validator("query")
    @classmethod
    def query_must_not_be_blank(cls, value: str) -> str:
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError("Query must not be empty.")
        return cleaned_value


class TextSummarizerInput(BaseModel):
    text: str

    @field_validator("text")
    @classmethod
    def text_must_not_be_blank(cls, value: str) -> str:
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError("Text must not be empty.")
        return cleaned_value


class FileAnalyzerInput(BaseModel):
    file_path: str

    @field_validator("file_path")
    @classmethod
    def file_path_must_not_be_blank(cls, value: str) -> str:
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError("File path must not be empty.")
        return cleaned_value


class ToolExecutionResult(BaseModel):
    output: str
    status: str
