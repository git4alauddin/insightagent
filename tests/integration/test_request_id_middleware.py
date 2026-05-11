import json
import logging

from fastapi.testclient import TestClient

from app.main import app


def test_request_id_header_is_generated_when_missing() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.headers["x-request-id"].startswith("req_")


def test_request_id_header_reuses_incoming_value() -> None:
    client = TestClient(app)

    response = client.get("/health", headers={"x-request-id": "external-request-123"})

    assert response.status_code == 200
    assert response.headers["x-request-id"] == "external-request-123"


def test_error_response_includes_request_id() -> None:
    client = TestClient(app)

    response = client.post(
        "/chat",
        json={"message": "Hello"},
        headers={"x-request-id": "error-request-123"},
    )

    assert response.status_code == 401
    assert response.headers["x-request-id"] == "error-request-123"
    assert response.json()["error"]["request_id"] == "error-request-123"


def test_request_log_includes_trace_fields(caplog) -> None:
    client = TestClient(app)

    with caplog.at_level(logging.INFO, logger="app.api.middleware"):
        response = client.get(
            "/health",
            headers={
                "x-request-id": "log-request-123",
                "x-session-id": "session-123",
            },
        )

    log_payloads = [
        json.loads(record.message)
        for record in caplog.records
        if record.name == "app.api.middleware"
    ]

    request_log = next(
        payload for payload in log_payloads if payload["event"] == "request_completed"
    )

    assert response.status_code == 200
    assert request_log["request_id"] == "log-request-123"
    assert request_log["session_id"] == "session-123"
    assert request_log["method"] == "GET"
    assert request_log["endpoint"] == "/health"
    assert request_log["path"] == "/health"
    assert request_log["status_code"] == 200
    assert request_log["status"] == "success"
    assert request_log["error_category"] is None
    assert isinstance(request_log["latency_ms"], float)


def test_failed_request_log_includes_error_category(caplog) -> None:
    client = TestClient(app)

    with caplog.at_level(logging.INFO, logger="app.api.middleware"):
        response = client.post(
            "/chat",
            json={"message": "Hello"},
            headers={"x-request-id": "failed-log-request-123"},
        )

    log_payloads = [
        json.loads(record.message)
        for record in caplog.records
        if record.name == "app.api.middleware"
    ]

    request_log = next(
        payload for payload in log_payloads if payload["event"] == "request_completed"
    )

    assert response.status_code == 401
    assert request_log["request_id"] == "failed-log-request-123"
    assert request_log["endpoint"] == "/chat"
    assert request_log["status_code"] == 401
    assert request_log["status"] == "failed"
    assert request_log["error_category"] == "AUTH_ERROR"
