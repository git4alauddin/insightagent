import app.db.database as database_module
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.session_service import append_message, create_session


client = TestClient(app)


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
        "detail": {
            "error": {
                "code": "SESSION_NOT_FOUND",
                "message": "Session not found: missing-session",
            }
        }
    }

