import app.db.database as database_module
import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app


client = TestClient(app)
client.headers.update({"x-api-key": "test-api-key", "x-request-id": "test-request-id"})


@pytest.fixture(autouse=True)
def isolated_db_and_uploads(monkeypatch, tmp_path):
    db_path = tmp_path / "test_dataset_ask.db"
    upload_dir = tmp_path / "uploads"
    monkeypatch.setattr(database_module, "DB_PATH", db_path)
    monkeypatch.setattr(settings, "upload_dir", str(upload_dir))
    return db_path


def test_dataset_ask_missing_values_success() -> None:
    csv_content = b"name,age,city\nalice,30,\nbob,,kolkata\ncharlie,40,\n"
    upload_response = client.post(
        "/datasets/upload",
        files={"file": ("people.csv", csv_content, "text/csv")},
    )
    dataset_id = upload_response.json()["dataset_id"]

    response = client.post(
        f"/datasets/{dataset_id}/ask",
        json={"question": "Which column has the most missing values?"},
    )
    data = response.json()

    assert response.status_code == 200
    assert data["status"] == "success"
    assert data["dataset_id"] == dataset_id
    assert data["tool_used"] == "missing_value_tool"
    assert data["analysis_trace"]["intent"] == "missing_value_analysis"
    assert "missing values" in data["answer"].lower()


def test_dataset_ask_groupby_success() -> None:
    csv_content = (
        b"passenger_class,fare\n"
        b"first,100\n"
        b"first,120\n"
        b"second,50\n"
    )
    upload_response = client.post(
        "/datasets/upload",
        files={"file": ("titanic.csv", csv_content, "text/csv")},
    )
    dataset_id = upload_response.json()["dataset_id"]

    response = client.post(
        f"/datasets/{dataset_id}/ask",
        json={"question": "What is the average fare by passenger class?"},
    )
    data = response.json()

    assert response.status_code == 200
    assert data["status"] == "success"
    assert data["tool_used"] == "groupby_aggregation_tool"
    assert data["analysis_trace"]["intent"] == "groupby_aggregation"
    assert data["analysis_trace"]["columns_used"] == ["passenger_class", "fare"]


def test_dataset_ask_dataset_not_found() -> None:
    response = client.post(
        "/datasets/ds_missing/ask",
        json={"question": "Which column has missing values?"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "DATASET_NOT_FOUND",
            "message": "Dataset not found: ds_missing",
            "request_id": "test-request-id",
        }
    }


def test_dataset_ask_unsupported_query_returns_safe_fallback() -> None:
    upload_response = client.post(
        "/datasets/upload",
        files={"file": ("people.csv", b"name,age\nalice,30\n", "text/csv")},
    )
    dataset_id = upload_response.json()["dataset_id"]

    response = client.post(
        f"/datasets/{dataset_id}/ask",
        json={"question": "Who is the prime minister of mars?"},
    )
    data = response.json()

    assert response.status_code == 200
    assert data["status"] == "failed"
    assert data["confidence"] == "low"
    assert data["tool_used"] == "none"
    assert data["analysis_trace"]["intent"] == "unsupported"
