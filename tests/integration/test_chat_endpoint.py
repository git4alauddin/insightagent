from unittest.mock import patch

from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.services.llm_service import LLMServiceError
from app.services.memory_chat_service import MemoryChatServiceError
from app.services.structured_llm_service import (
    StructuredLLMServiceError,
    build_structured_fallback_response,
)


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


def test_structured_chat_returns_structured_answer() -> None:
    structured_answer = {
        "answer": "Missing values are empty entries in a dataset.",
        "confidence": "high",
        "reasoning_summary": "The user asked for a simple explanation.",
        "next_action": "No tool required.",
        "prompt_version": "v2.1",
        "status": "success",
    }

    with patch(
        "app.api.routes_chat.generate_structured_answer",
        return_value=structured_answer,
    ):
        response = client.post(
            "/chat/structured",
            json={"message": "Explain missing values."},
        )

    assert response.status_code == 200
    assert response.json() == structured_answer


def test_structured_chat_returns_controlled_error_when_service_fails() -> None:
    with patch(
        "app.api.routes_chat.generate_structured_answer",
        side_effect=StructuredLLMServiceError("LLM request timed out."),
    ):
        response = client.post(
            "/chat/structured",
            json={"message": "Explain missing values."},
        )

    assert response.status_code == 503
    assert response.json() == {
        "detail": {
            "error": {
                "code": "STRUCTURED_LLM_SERVICE_ERROR",
                "message": "LLM request timed out.",
            }
        }
    }


def test_structured_chat_can_return_fallback_response() -> None:
    fallback_response = build_structured_fallback_response()

    with patch(
        "app.api.routes_chat.generate_structured_answer",
        return_value=fallback_response,
    ):
        response = client.post(
            "/chat/structured",
            json={"message": "Explain missing values."},
        )

    assert response.status_code == 200
    assert response.json()["status"] == "failed"
    assert response.json()["confidence"] == "low"


def test_memory_chat_returns_response_with_session_id() -> None:
    mock_response = {
        "session_id": "session-123",
        "answer": "Memory-aware reply.",
        "context_message_count": 3,
        "status": "success",
    }

    with patch("app.api.routes_chat.run_memory_chat", return_value=mock_response):
        response = client.post(
            "/chat/memory",
            json={"message": "Hello from memory chat", "session_id": "session-123"},
        )

    assert response.status_code == 200
    assert response.json() == mock_response


def test_memory_chat_returns_controlled_error_when_service_fails() -> None:
    with patch(
        "app.api.routes_chat.run_memory_chat",
        side_effect=MemoryChatServiceError("Session not found: missing-session"),
    ):
        response = client.post(
            "/chat/memory",
            json={"message": "Hello", "session_id": "missing-session"},
        )

    assert response.status_code == 503
    assert response.json() == {
        "detail": {
            "error": {
                "code": "MEMORY_CHAT_SERVICE_ERROR",
                "message": "Session not found: missing-session",
            }
        }
    }


def test_memory_chat_returns_controlled_error_when_message_too_long() -> None:
    long_message = "a" * 5001
    response = client.post("/chat/memory", json={"message": long_message})

    assert response.status_code == 503
    assert response.json() == {
        "detail": {
            "error": {
                "code": "MEMORY_CHAT_SERVICE_ERROR",
                "message": "Message too long.",
            }
        }
    }
