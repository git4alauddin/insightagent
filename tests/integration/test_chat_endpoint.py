from unittest.mock import patch

from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.services.llm_service import LLMServiceError


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


def test_chat_returns_controlled_error_when_llm_fails() -> None:
    with patch(
        "app.api.routes_chat.generate_answer",
        side_effect=LLMServiceError("LLM API key is not configured."),
    ):
        response = client.post("/chat", json={"message": "Hello"})

    assert response.status_code == 503
    assert response.json() == {
        "detail": {
            "error": {
                "code": "LLM_SERVICE_ERROR",
                "message": "LLM API key is not configured.",
            }
        }
    }
