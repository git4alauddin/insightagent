from pathlib import Path

import app.db.database as database_module
import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.services.dataset_registry_service import get_dataset_metadata


client = TestClient(app)


@pytest.fixture(autouse=True)
def isolated_db_and_uploads(monkeypatch, tmp_path):
    db_path = tmp_path / "test_dataset_summary.db"
    upload_dir = tmp_path / "uploads"
    monkeypatch.setattr(database_module, "DB_PATH", db_path)
    monkeypatch.setattr(settings, "upload_dir", str(upload_dir))
    return db_path


def test_dataset_summary_returns_expected_shape() -> None:
    csv_content = b"name,age,city\nalice,30,\nbob,41,kolkata\n"
    upload_response = client.post(
        "/datasets/upload",
        files={"file": ("people.csv", csv_content, "text/csv")},
    )
    dataset_id = upload_response.json()["dataset_id"]

    response = client.get(f"/datasets/{dataset_id}/summary")
    data = response.json()

    assert response.status_code == 200
    assert data["dataset_id"] == dataset_id
    assert data["rows"] == 2
    assert data["columns"] == 3
    assert data["column_names"] == ["name", "age", "city"]
    assert data["missing_values"]["city"] == 1
    assert "age" in data["numeric_columns"]
    assert "name" in data["categorical_columns"]


def test_dataset_summary_returns_not_found_for_unknown_dataset() -> None:
    response = client.get("/datasets/ds_missing/summary")

    assert response.status_code == 404
    assert response.json() == {
        "detail": {
            "error": {
                "code": "DATASET_NOT_FOUND",
                "message": "Dataset not found: ds_missing",
            }
        }
    }


def test_dataset_summary_returns_storage_error_when_file_is_missing() -> None:
    upload_response = client.post(
        "/datasets/upload",
        files={"file": ("people.csv", b"name,age\nalice,30\n", "text/csv")},
    )
    dataset_id = upload_response.json()["dataset_id"]
    metadata = get_dataset_metadata(dataset_id)

    stored_path = Path(str(metadata["storage_path"]))
    stored_path.unlink()

    response = client.get(f"/datasets/{dataset_id}/summary")

    assert response.status_code == 503
    assert response.json() == {
        "detail": {
            "error": {
                "code": "DATASET_STORAGE_ERROR",
                "message": f"Dataset file is missing: {stored_path}",
            }
        }
    }
