from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.api.rate_limit import reset_rate_limit_store
from app.config import settings
from app.main import app


@pytest.fixture(autouse=True)
def enable_rate_limits(monkeypatch):
    reset_rate_limit_store()
    monkeypatch.setattr(settings, "rate_limit_enabled", True)
    monkeypatch.setattr(settings, "rate_limit_window_seconds", 60)
    yield
    reset_rate_limit_store()


def test_rate_limit_rejects_too_many_private_requests(monkeypatch) -> None:
    monkeypatch.setattr(settings, "rate_limit_requests_per_minute", 2)
    client = TestClient(app)
    headers = {"x-api-key": "test-api-key", "x-request-id": "rate-limit-request"}

    with patch("app.api.routes_chat.generate_answer", return_value="Mock answer."):
        first = client.post("/chat", json={"message": "Hello"}, headers=headers)
        second = client.post("/chat", json={"message": "Hello"}, headers=headers)
        third = client.post("/chat", json={"message": "Hello"}, headers=headers)

    assert first.status_code == 200
    assert second.status_code == 200
    assert third.status_code == 429
    assert third.json() == {
        "error": {
            "code": "RATE_LIMIT_EXCEEDED",
            "message": "Rate limit exceeded. Please retry later.",
            "request_id": "rate-limit-request",
        }
    }


def test_upload_endpoint_uses_stricter_upload_limit(monkeypatch) -> None:
    monkeypatch.setattr(settings, "rate_limit_requests_per_minute", 100)
    monkeypatch.setattr(settings, "rate_limit_uploads_per_minute", 1)
    client = TestClient(app)
    headers = {"x-api-key": "test-api-key", "x-request-id": "upload-limit-request"}

    first = client.post(
        "/datasets/upload",
        files={"file": ("notes.txt", b"hello", "text/plain")},
        headers=headers,
    )
    second = client.post(
        "/datasets/upload",
        files={"file": ("notes.txt", b"hello", "text/plain")},
        headers=headers,
    )

    assert first.status_code == 400
    assert second.status_code == 429
    assert second.json()["error"]["code"] == "RATE_LIMIT_EXCEEDED"


def test_public_health_is_not_rate_limited(monkeypatch) -> None:
    monkeypatch.setattr(settings, "rate_limit_requests_per_minute", 1)
    client = TestClient(app)

    first = client.get("/health")
    second = client.get("/health")

    assert first.status_code == 200
    assert second.status_code == 200
