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


class MemoryChatRequest(BaseModel):
    message: str
    session_id: str | None = None

    @field_validator("message")
    @classmethod
    def memory_message_must_not_be_blank(cls, value: str) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("Message must not be empty.")

        return cleaned_value

    @field_validator("session_id")
    @classmethod
    def session_id_must_not_be_blank_if_provided(cls, value: str | None) -> str | None:
        if value is None:
            return None

        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError("Session ID must not be empty.")

        return cleaned_value


class MemoryChatResponse(BaseModel):
    session_id: str
    answer: str
    context_message_count: int
    status: str
