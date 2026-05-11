from unittest.mock import patch

import app.db.database as database_module
import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.schemas.document import DocumentAskResponse, SourceCitation
from app.services.document_answer_service import DocumentAnswerError
from app.services.document_registry_service import register_document_metadata


client = TestClient(app)
client.headers.update({"x-api-key": "test-api-key", "x-request-id": "document-ask-test"})


@pytest.fixture(autouse=True)
def isolated_db_and_uploads(monkeypatch, tmp_path):
    db_path = tmp_path / "test_document_ask.db"
    upload_dir = tmp_path / "uploads"
    monkeypatch.setattr(database_module, "DB_PATH", db_path)
    monkeypatch.setattr(settings, "upload_dir", str(upload_dir))
    return db_path


def _register_document(document_id: str = "doc_123") -> str:
    register_document_metadata(
        document_id=document_id,
        filename="policy.txt",
        storage_path="uploads/documents/standalone/doc_123.txt",
        file_extension=".txt",
        file_size_bytes=36,
    )
    return document_id


def test_document_ask_success_returns_answer_and_citations() -> None:
    document_id = _register_document()

    with patch(
        "app.api.routes_documents.answer_document_question",
        return_value=DocumentAskResponse(
            answer="Based on the retrieved document context: Refunds are available.",
            confidence="high",
            document_id=document_id,
            sources=[
                SourceCitation(
                    filename="policy.txt",
                    chunk_id="doc_123_chunk_0000",
                    page=1,
                    similarity_score=0.91,
                )
            ],
            status="success",
        ),
    ):
        response = client.post(
            f"/documents/{document_id}/ask",
            json={"question": "What is the refund policy?"},
        )

    data = response.json()
    assert response.status_code == 200
    assert data["status"] == "success"
    assert data["document_id"] == document_id
    assert data["sources"][0]["chunk_id"] == "doc_123_chunk_0000"


def test_document_ask_returns_insufficient_context_without_indexed_chunks() -> None:
    document_id = _register_document()

    response = client.post(
        f"/documents/{document_id}/ask",
        json={"question": "What is the refund policy?"},
    )

    data = response.json()
    assert response.status_code == 200
    assert data["status"] == "insufficient_context"
    assert data["confidence"] == "low"
    assert data["sources"] == []


def test_document_ask_missing_document_returns_controlled_404() -> None:
    response = client.post(
        "/documents/doc_missing/ask",
        json={"question": "What is the refund policy?"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "DOCUMENT_NOT_FOUND",
            "message": "Document not found: doc_missing",
            "request_id": "document-ask-test",
        }
    }


def test_document_ask_returns_controlled_answer_error() -> None:
    document_id = _register_document()

    with patch(
        "app.api.routes_documents.answer_document_question",
        side_effect=DocumentAnswerError("retrieval failed"),
    ):
        response = client.post(
            f"/documents/{document_id}/ask",
            json={"question": "What is the refund policy?"},
        )

    assert response.status_code == 503
    assert response.json() == {
        "error": {
            "code": "DOCUMENT_ANSWER_ERROR",
            "message": "retrieval failed",
            "request_id": "document-ask-test",
        }
    }
