from unittest.mock import patch

import app.db.database as database_module
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.session_service import SessionServiceError, append_message, create_session


client = TestClient(app)
client.headers.update({"x-api-key": "test-api-key", "x-request-id": "test-request-id"})


@pytest.fixture(autouse=True)
def isolated_db(monkeypatch, tmp_path):
    db_path = tmp_path / "test_session_endpoints.db"
    monkeypatch.setattr(database_module, "DB_PATH", db_path)
    return db_path


def test_create_session_returns_session_id() -> None:
    response = client.post("/sessions")

    data = response.json()
    assert response.status_code == 200
    assert data["status"] == "success"
    assert isinstance(data["session_id"], str)
    assert len(data["session_id"]) > 0


def test_create_session_accepts_optional_title(isolated_db) -> None:
    response = client.post("/sessions", json={"title": "Postman study"})

    data = response.json()
    assert response.status_code == 200
    assert data["status"] == "success"

    with database_module.db_cursor() as cursor:
        cursor.execute(
            "SELECT title FROM sessions WHERE session_id = ?",
            (data["session_id"],),
        )
        row = cursor.fetchone()

    assert row["title"] == "Postman study"


def test_create_session_returns_controlled_db_error_when_service_fails() -> None:
    with patch(
        "app.api.routes_session.create_session",
        side_effect=SessionServiceError("Database operation failed."),
    ):
        response = client.post("/sessions")

    assert response.status_code == 503
    assert response.json() == {
        "error": {
            "code": "SESSION_DB_ERROR",
            "message": "Database operation failed.",
            "request_id": "test-request-id",
        }
    }


def test_get_session_messages_returns_messages() -> None:
    session_id = create_session("session-endpoint-1")
    append_message(session_id, "user", "Hello", token_estimate=1)
    append_message(session_id, "assistant", "Hi there", token_estimate=2)

    response = client.get(f"/sessions/{session_id}/messages")
    data = response.json()

    assert response.status_code == 200
    assert data["session_id"] == session_id
    assert data["status"] == "success"
    assert len(data["messages"]) == 2
    assert data["messages"][0]["role"] == "user"
    assert data["messages"][0]["content"] == "Hello"
    assert data["messages"][1]["role"] == "assistant"
    assert data["messages"][1]["content"] == "Hi there"


def test_get_session_messages_returns_controlled_error_for_missing_session() -> None:
    response = client.get("/sessions/missing-session/messages")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "SESSION_NOT_FOUND",
            "message": "Session not found: missing-session",
            "request_id": "test-request-id",
        }
    }


def test_get_session_messages_returns_controlled_db_error_for_service_error() -> None:
    with patch(
        "app.api.routes_session.get_recent_messages",
        side_effect=SessionServiceError("Database operation failed."),
    ):
        response = client.get("/sessions/session-123/messages")

    assert response.status_code == 503
    assert response.json() == {
        "error": {
            "code": "SESSION_DB_ERROR",
            "message": "Database operation failed.",
            "request_id": "test-request-id",
        }
    }
