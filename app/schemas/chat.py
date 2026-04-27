from pydantic import BaseModel, field_validator


class ChatRequest(BaseModel):
    message: str

    @field_validator("message")
    @classmethod
    def message_must_not_be_blank(cls, value: str) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("Message must not be empty.")

        return cleaned_value


class ChatResponse(BaseModel):
    answer: str
    model: str
    latency_ms: float
    status: str