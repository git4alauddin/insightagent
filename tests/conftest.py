import pytest

from app.config import settings


@pytest.fixture(autouse=True)
def configure_test_api_key(monkeypatch):
    monkeypatch.setattr(settings, "api_key", "test-api-key")
