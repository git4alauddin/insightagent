from unittest.mock import patch

from fastapi.testclient import TestClient

from app.config import settings
from app.main import app


client = TestClient(app)


def test_chat_returns_llm_answer() -> None:
    with patch("app.api.routes_chat.generate_answer", return_value="Mock answer."):
        response = client.post("/chat", json={"message": "Hello"})

    data = response.json()

    assert response.status_code == 200
    assert data["answer"] == "Mock answer."
    assert data["model"] == settings.llm_model
    assert isinstance(data["latency_ms"], float)
    assert data["status"] == "success"
