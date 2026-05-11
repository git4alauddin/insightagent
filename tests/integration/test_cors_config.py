import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import app


def test_cors_preflight_allows_configured_origin() -> None:
    client = TestClient(app)

    response = client.options(
        "/chat",
        headers={
            "origin": "http://localhost:3000",
            "access-control-request-method": "POST",
            "access-control-request-headers": "content-type,x-api-key",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert "POST" in response.headers["access-control-allow-methods"]


def test_cors_does_not_allow_unconfigured_origin() -> None:
    client = TestClient(app)

    response = client.options(
        "/chat",
        headers={
            "origin": "https://unknown.example.com",
            "access-control-request-method": "POST",
        },
    )

    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers


def test_production_cors_rejects_wildcard_origin() -> None:
    settings = Settings(app_env="production", cors_allowed_origins="*")

    with pytest.raises(ValueError, match="Wildcard CORS origins"):
        settings.get_cors_allowed_origins()
