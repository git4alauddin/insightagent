from pathlib import Path
from unittest.mock import patch

import app.db.database as database_module
import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.services.document_registry_service import DocumentRegistryError, get_document_metadata


client = TestClient(app)
client.headers.update({"x-api-key": "test-api-key", "x-request-id": "document-upload-test"})


@pytest.fixture(autouse=True)
def isolated_db_and_uploads(monkeypatch, tmp_path):
    db_path = tmp_path / "test_document_upload.db"
    upload_dir = tmp_path / "uploads"
    monkeypatch.setattr(database_module, "DB_PATH", db_path)
    monkeypatch.setattr(settings, "upload_dir", str(upload_dir))
    return db_path


def test_upload_txt_document_success_returns_metadata() -> None:
    response = client.post(
        "/documents/upload",
        files={"file": ("policy.txt", b"Refunds are available within 7 days.", "text/plain")},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "indexed"
    assert data["filename"] == "policy.txt"
    assert data["document_id"].startswith("doc_")

    metadata = get_document_metadata(data["document_id"])
    assert metadata["filename"] == "policy.txt"
    assert metadata["file_extension"] == ".txt"
    assert metadata["file_size_bytes"] == 36
    assert metadata["status"] == "indexed"
    assert Path(str(metadata["storage_path"])).exists()


def test_upload_rejects_unsupported_document_type() -> None:
    response = client.post(
        "/documents/upload",
        files={"file": ("image.png", b"png-bytes", "image/png")},
    )

    assert response.status_code == 400
    assert response.json() == {
        "error": {
            "code": "DOCUMENT_VALIDATION_ERROR",
            "message": "Only PDF, TXT, and Markdown documents are supported.",
            "request_id": "document-upload-test",
        }
    }


def test_upload_rejects_empty_document() -> None:
    response = client.post(
        "/documents/upload",
        files={"file": ("empty.txt", b"", "text/plain")},
    )

    assert response.status_code == 400
    assert response.json() == {
        "error": {
            "code": "DOCUMENT_VALIDATION_ERROR",
            "message": "Document file is empty.",
            "request_id": "document-upload-test",
        }
    }


def test_upload_returns_controlled_db_error_when_registry_fails() -> None:
    with patch(
        "app.api.routes_documents.register_document_metadata",
        side_effect=DocumentRegistryError("Database operation failed."),
    ):
        response = client.post(
            "/documents/upload",
            files={"file": ("policy.md", b"# Policy", "text/markdown")},
        )

    assert response.status_code == 503
    assert response.json() == {
        "error": {
            "code": "DOCUMENT_DB_ERROR",
            "message": "Database operation failed.",
            "request_id": "document-upload-test",
        }
    }
