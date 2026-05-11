from fastapi.testclient import TestClient

from app.config import settings
from app.main import app, create_app


def test_docs_are_enabled_by_default() -> None:
    client = TestClient(app)

    response = client.get("/docs")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_openapi_schema_is_enabled_by_default() -> None:
    client = TestClient(app)

    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert response.json()["info"]["title"] == "InsightAgent"


def test_docs_can_be_disabled(monkeypatch) -> None:
    monkeypatch.setattr(settings, "docs_enabled", False)
    client = TestClient(create_app())

    response = client.get("/docs", headers={"x-request-id": "docs-disabled-request"})

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "HTTP_ERROR",
            "message": "Not Found",
            "request_id": "docs-disabled-request",
        }
    }


def test_openapi_schema_can_be_disabled(monkeypatch) -> None:
    monkeypatch.setattr(settings, "docs_enabled", False)
    client = TestClient(create_app())

    response = client.get(
        "/openapi.json",
        headers={"x-request-id": "openapi-disabled-request"},
    )

    assert response.status_code == 404
    assert response.json()["error"]["request_id"] == "openapi-disabled-request"
