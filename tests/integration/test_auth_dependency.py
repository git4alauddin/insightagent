from fastapi.testclient import TestClient

from app.config import settings
from app.main import app


def test_public_health_does_not_require_api_key() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200


def test_public_ready_does_not_require_api_key(monkeypatch) -> None:
    monkeypatch.setattr(settings, "llm_api_key", "test-llm-key")
    client = TestClient(app)

    response = client.get("/ready")

    assert response.status_code == 200


def test_protected_endpoint_rejects_missing_api_key() -> None:
    client = TestClient(app)

    response = client.post("/chat", json={"message": "Hello"})

    assert response.status_code == 401
    assert response.json() == {
        "error": {
            "code": "UNAUTHORIZED",
            "message": "A valid x-api-key header is required.",
        }
    }


def test_protected_endpoint_rejects_invalid_api_key() -> None:
    client = TestClient(app)

    response = client.post(
        "/chat",
        json={"message": "Hello"},
        headers={"x-api-key": "wrong-key"},
    )

    assert response.status_code == 401
    assert response.json() == {
        "error": {
            "code": "UNAUTHORIZED",
            "message": "A valid x-api-key header is required.",
        }
    }


def test_protected_endpoint_fails_closed_when_api_key_is_not_configured(monkeypatch) -> None:
    monkeypatch.setattr(settings, "api_key", None)
    client = TestClient(app)

    response = client.post(
        "/chat",
        json={"message": "Hello"},
        headers={"x-api-key": "test-api-key"},
    )

    assert response.status_code == 503
    assert response.json() == {
        "error": {
            "code": "API_KEY_NOT_CONFIGURED",
            "message": "API key authentication is not configured.",
        }
    }
