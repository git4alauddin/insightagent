from unittest.mock import patch

import app.db.database as database_module
import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)
client.headers.update({"x-api-key": "test-api-key"})


@pytest.fixture(autouse=True)
def isolated_db(monkeypatch, tmp_path):
    db_path = tmp_path / "test_memory_chat_flow.db"
    monkeypatch.setattr(database_module, "DB_PATH", db_path)
    return db_path


def test_memory_chat_multi_turn_uses_same_session_context() -> None:
    with patch(
        "app.services.memory_chat_service.generate_answer_from_messages",
        return_value="assistant-reply",
    ):
        first = client.post(
            "/chat/memory",
            json={"message": "Hello, remember this."},
        )

        assert first.status_code == 200
        first_data = first.json()
        session_id = first_data["session_id"]
        assert first_data["status"] == "success"
        assert first_data["context_message_count"] == 1

        second = client.post(
            "/chat/memory",
            json={"session_id": session_id, "message": "What did I say earlier?"},
        )

    assert second.status_code == 200
    second_data = second.json()
    assert second_data["session_id"] == session_id
    assert second_data["status"] == "success"
    assert second_data["context_message_count"] >= 3
