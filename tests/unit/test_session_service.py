import app.db.database as database_module
import pytest

from app.services.session_service import (
    SessionServiceError,
    append_message,
    create_session,
    format_context_for_llm,
    get_recent_messages,
    session_exists,
)


@pytest.fixture
def isolated_db(monkeypatch, tmp_path):
    db_path = tmp_path / "test_session_service.db"
    monkeypatch.setattr(database_module, "DB_PATH", db_path)
    return db_path


def test_create_session_generates_id_when_missing(isolated_db) -> None:
    session_id = create_session()

    assert isinstance(session_id, str)
    assert len(session_id) > 0
    assert session_exists(session_id) is True


def test_create_session_uses_given_id(isolated_db) -> None:
    session_id = create_session("session-123")
    assert session_id == "session-123"
    assert session_exists("session-123") is True


def test_append_message_stores_messages_in_order(isolated_db) -> None:
    session_id = create_session("session-order")

    append_message(session_id, "user", "Hello", token_estimate=2)
    append_message(session_id, "assistant", "Hi there", token_estimate=3)

    messages = get_recent_messages(session_id, limit=10)

    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Hello"
    assert messages[1]["role"] == "assistant"
    assert messages[1]["content"] == "Hi there"


def test_append_message_rejects_missing_session(isolated_db) -> None:
    with pytest.raises(SessionServiceError, match="Session not found"):
        append_message("missing-session", "user", "Hello")


def test_get_recent_messages_applies_limit(isolated_db) -> None:
    session_id = create_session("session-limit")

    append_message(session_id, "user", "m1")
    append_message(session_id, "assistant", "m2")
    append_message(session_id, "user", "m3")

    messages = get_recent_messages(session_id, limit=2)

    assert len(messages) == 2
    assert messages[0]["content"] == "m2"
    assert messages[1]["content"] == "m3"


def test_format_context_for_llm_returns_role_content_only(isolated_db) -> None:
    session_id = create_session("session-context")
    append_message(session_id, "user", "Question?")
    append_message(session_id, "assistant", "Answer.")

    context = format_context_for_llm(session_id, limit=10)

    assert context == [
        {"role": "user", "content": "Question?"},
        {"role": "assistant", "content": "Answer."},
    ]

