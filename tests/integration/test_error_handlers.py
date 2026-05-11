from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


def test_validation_error_returns_structured_invalid_input() -> None:
    client = TestClient(app)
    client.headers.update({"x-api-key": "test-api-key"})

    response = client.post("/chat", json={})

    assert response.status_code == 422
    assert response.json() == {
        "error": {
            "code": "INVALID_INPUT",
            "message": "Request validation failed.",
        }
    }


def test_unexpected_error_returns_safe_internal_error() -> None:
    client = TestClient(app, raise_server_exceptions=False)
    client.headers.update({"x-api-key": "test-api-key"})

    with patch(
        "app.api.routes_chat.generate_answer",
        side_effect=RuntimeError("database password leaked here"),
    ):
        response = client.post("/chat", json={"message": "Hello"})

    assert response.status_code == 500
    assert response.json() == {
        "error": {
            "code": "INTERNAL_ERROR",
            "message": "An unexpected error occurred.",
        }
    }
