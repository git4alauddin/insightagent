from app.schemas.chat import MemoryChatResponse
from app.services.llm_service import LLMServiceError, generate_answer_from_messages
from app.services.session_service import (
    SessionServiceError,
    append_message,
    create_session,
    format_context_for_llm,
    session_exists,
)


class MemoryChatServiceError(Exception):
    pass


MAX_CONTEXT_MESSAGES = 20
MAX_MESSAGE_LENGTH = 5000


def _estimate_tokens(content: str) -> int:
    return len(content.split())


def run_memory_chat(message: str, session_id: str | None = None) -> MemoryChatResponse:
    if len(message.strip()) > MAX_MESSAGE_LENGTH:
        raise MemoryChatServiceError("Message too long.")

    if session_id is None:
        resolved_session_id = create_session()
    else:
        if not session_exists(session_id):
            raise MemoryChatServiceError(f"Session not found: {session_id}")
        resolved_session_id = session_id

    try:
        append_message(
            session_id=resolved_session_id,
            role="user",
            content=message,
            token_estimate=_estimate_tokens(message),
        )
    except SessionServiceError as exc:
        raise MemoryChatServiceError(str(exc)) from exc

    context_messages = format_context_for_llm(resolved_session_id, limit=MAX_CONTEXT_MESSAGES)

    try:
        assistant_answer = generate_answer_from_messages(context_messages)
    except LLMServiceError as exc:
        raise MemoryChatServiceError(str(exc)) from exc

    try:
        append_message(
            session_id=resolved_session_id,
            role="assistant",
            content=assistant_answer,
            token_estimate=_estimate_tokens(assistant_answer),
        )
    except SessionServiceError as exc:
        raise MemoryChatServiceError(str(exc)) from exc

    return MemoryChatResponse(
        session_id=resolved_session_id,
        answer=assistant_answer,
        context_message_count=len(context_messages),
        status="success",
    )
