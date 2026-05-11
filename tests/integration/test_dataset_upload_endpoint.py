from unittest.mock import patch

import app.db.database as database_module
import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.services.dataset_registry_service import DatasetRegistryError, get_dataset_metadata


client = TestClient(app)
client.headers.update({"x-api-key": "test-api-key", "x-request-id": "test-request-id"})


@pytest.fixture(autouse=True)
def isolated_db_and_uploads(monkeypatch, tmp_path):
    db_path = tmp_path / "test_dataset_upload.db"
    upload_dir = tmp_path / "uploads"
    monkeypatch.setattr(database_module, "DB_PATH", db_path)
    monkeypatch.setattr(settings, "upload_dir", str(upload_dir))
    return db_path


def test_upload_csv_success_returns_dataset_metadata() -> None:
    csv_content = b"name,age\nalice,30\nbob,41\n"
    response = client.post(
        "/datasets/upload",
        files={"file": ("people.csv", csv_content, "text/csv")},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "uploaded"
    assert data["filename"] == "people.csv"
    assert data["rows"] == 2
    assert data["columns"] == 2
    assert data["dataset_id"].startswith("ds_")

    metadata = get_dataset_metadata(data["dataset_id"])
    assert metadata["filename"] == "people.csv"
    assert metadata["row_count"] == 2
    assert metadata["column_count"] == 2


def test_upload_rejects_non_csv_files() -> None:
    response = client.post(
        "/datasets/upload",
        files={"file": ("notes.txt", b"hello", "text/plain")},
    )

    assert response.status_code == 400
    assert response.json() == {
        "error": {
            "code": "DATASET_VALIDATION_ERROR",
            "message": "Only CSV files are supported.",
            "request_id": "test-request-id",
        }
    }


def test_upload_rejects_empty_csv() -> None:
    response = client.post(
        "/datasets/upload",
        files={"file": ("empty.csv", b"", "text/csv")},
    )

    assert response.status_code == 400
    assert response.json() == {
        "error": {
            "code": "DATASET_VALIDATION_ERROR",
            "message": "CSV file is empty.",
            "request_id": "test-request-id",
        }
    }


def test_upload_rejects_duplicate_columns() -> None:
    csv_content = b"age,age\n20,25\n"
    response = client.post(
        "/datasets/upload",
        files={"file": ("dupe_columns.csv", csv_content, "text/csv")},
    )

    assert response.status_code == 400
    assert response.json() == {
        "error": {
            "code": "DATASET_VALIDATION_ERROR",
            "message": "CSV contains duplicate column names.",
            "request_id": "test-request-id",
        }
    }


def test_upload_returns_controlled_db_error_when_registry_fails() -> None:
    with patch(
        "app.api.routes_datasets.register_dataset_metadata",
        side_effect=DatasetRegistryError("Database operation failed."),
    ):
        response = client.post(
            "/datasets/upload",
            files={"file": ("people.csv", b"name,age\nalice,30\n", "text/csv")},
        )

    assert response.status_code == 503
    assert response.json() == {
        "error": {
            "code": "DATASET_DB_ERROR",
            "message": "Database operation failed.",
            "request_id": "test-request-id",
        }
    }
