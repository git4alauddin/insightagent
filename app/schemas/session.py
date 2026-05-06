from pydantic import BaseModel


class CreateSessionResponse(BaseModel):
    session_id: str
    status: str


class SessionMessageItem(BaseModel):
    role: str
    content: str
    created_at: str
    token_estimate: int


class SessionMessagesResponse(BaseModel):
    session_id: str
    messages: list[SessionMessageItem]
    status: str

