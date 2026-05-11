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
