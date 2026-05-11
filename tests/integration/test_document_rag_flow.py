import app.db.database as database_module
import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.services.document_registry_service import get_document_metadata
from app.services.document_vector_store_service import get_document_chunks


client = TestClient(app)
client.headers.update({"x-api-key": "test-api-key", "x-request-id": "document-rag-test"})


@pytest.fixture(autouse=True)
def isolated_db_and_uploads(monkeypatch, tmp_path):
    db_path = tmp_path / "test_document_rag.db"
    upload_dir = tmp_path / "uploads"
    monkeypatch.setattr(database_module, "DB_PATH", db_path)
    monkeypatch.setattr(settings, "upload_dir", str(upload_dir))
    return db_path


def test_upload_indexes_document_and_ask_returns_grounded_answer() -> None:
    upload_response = client.post(
        "/documents/upload",
        files={
            "file": (
                "policy.txt",
                b"Refunds are available within 7 days. Shipping takes 3 days.",
                "text/plain",
            )
        },
    )
    upload_data = upload_response.json()
    document_id = upload_data["document_id"]

    ask_response = client.post(
        f"/documents/{document_id}/ask",
        json={"question": "What is the refund policy?"},
    )
    ask_data = ask_response.json()

    assert upload_response.status_code == 200
    assert upload_data["status"] == "indexed"
    assert get_document_metadata(document_id)["status"] == "indexed"
    assert len(get_document_chunks(document_id)) > 0
    assert ask_response.status_code == 200
    assert ask_data["status"] == "success"
    assert ask_data["sources"][0]["chunk_id"].startswith(f"{document_id}_chunk_")
    assert "Refunds are available within 7 days" in ask_data["answer"]


def test_upload_returns_controlled_indexing_error_for_empty_extracted_text() -> None:
    response = client.post(
        "/documents/upload",
        files={"file": ("blank.md", b"   ", "text/markdown")},
    )

    assert response.status_code == 400
    assert response.json() == {
        "error": {
            "code": "DOCUMENT_INDEXING_ERROR",
            "message": "No text could be extracted from the document.",
            "request_id": "document-rag-test",
        }
    }
