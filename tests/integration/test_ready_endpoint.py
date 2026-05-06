import app.db.database as database_module
import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app


client = TestClient(app)


@pytest.fixture(autouse=True)
def isolated_dependencies(monkeypatch, tmp_path):
    db_path = tmp_path / "test_ready.db"
    upload_dir = tmp_path / "uploads"
    monkeypatch.setattr(database_module, "DB_PATH", db_path)
    monkeypatch.setattr(settings, "upload_dir", str(upload_dir))
    return db_path


def test_ready_returns_ready_when_dependencies_are_ok(monkeypatch) -> None:
    monkeypatch.setattr(settings, "llm_api_key", "test-key")

    response = client.get("/ready")
    data = response.json()

    assert response.status_code == 200
    assert data["status"] == "ready"
    assert all(check["status"] == "ok" for check in data["checks"])


def test_ready_returns_503_when_llm_config_is_missing(monkeypatch) -> None:
    monkeypatch.setattr(settings, "llm_api_key", "")

    response = client.get("/ready")
    data = response.json()

    assert response.status_code == 503
    assert data["status"] == "not_ready"

    llm_check = next(check for check in data["checks"] if check["name"] == "llm_config")
    assert llm_check["status"] == "failed"
    assert llm_check["detail"] == "LLM API key is missing."
