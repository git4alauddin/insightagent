from unittest.mock import patch

import pytest

from app.services.memory_chat_service import (
    MAX_CONTEXT_MESSAGES,
    MAX_MESSAGE_LENGTH,
    MemoryChatServiceError,
    run_memory_chat,
)


def test_run_memory_chat_creates_new_session_when_missing_session_id() -> None:
    with patch("app.services.memory_chat_service.create_session", return_value="session-new"), patch(
        "app.services.memory_chat_service.append_message"
    ), patch(
        "app.services.memory_chat_service.format_context_for_llm",
        return_value=[{"role": "user", "content": "Hello"}],
    ), patch(
        "app.services.memory_chat_service.generate_answer_from_messages",
        return_value="Hi there",
    ):
        result = run_memory_chat("Hello")

    assert result.session_id == "session-new"
    assert result.answer == "Hi there"
    assert result.context_message_count == 1
    assert result.status == "success"


def test_run_memory_chat_uses_existing_session() -> None:
    with patch("app.services.memory_chat_service.session_exists", return_value=True), patch(
        "app.services.memory_chat_service.append_message"
    ), patch(
        "app.services.memory_chat_service.format_context_for_llm",
        return_value=[{"role": "user", "content": "Hello again"}],
    ) as mock_format_context, patch(
        "app.services.memory_chat_service.generate_answer_from_messages",
        return_value="Welcome back",
    ):
        result = run_memory_chat("Hello again", session_id="session-123")

    mock_format_context.assert_called_once_with("session-123", limit=MAX_CONTEXT_MESSAGES)
    assert result.session_id == "session-123"
    assert result.answer == "Welcome back"


def test_run_memory_chat_rejects_missing_existing_session() -> None:
    with patch("app.services.memory_chat_service.session_exists", return_value=False):
        with pytest.raises(MemoryChatServiceError, match="Session not found"):
            run_memory_chat("Hello", session_id="missing-session")


def test_run_memory_chat_rejects_too_long_message() -> None:
    long_message = "a" * (MAX_MESSAGE_LENGTH + 1)
    with pytest.raises(MemoryChatServiceError, match="Message too long"):
        run_memory_chat(long_message)
