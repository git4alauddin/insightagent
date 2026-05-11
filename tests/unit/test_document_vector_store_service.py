import sqlite3
from unittest.mock import patch

import app.db.database as database_module
import pytest

from app.schemas.document import DocumentChunk
from app.services.document_vector_store_service import (
    DocumentVectorStoreError,
    get_document_chunks,
    save_document_chunks,
)


@pytest.fixture
def isolated_db(monkeypatch, tmp_path):
    db_path = tmp_path / "test_vector_store.db"
    monkeypatch.setattr(database_module, "DB_PATH", db_path)
    return db_path


def _chunk(chunk_id: str, chunk_index: int, text: str = "Refund policy.") -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id="doc_123",
        filename="policy.txt",
        chunk_index=chunk_index,
        text=text,
    )


def test_save_and_get_document_chunks(isolated_db) -> None:
    chunks = [
        _chunk("doc_123_chunk_0000", 0),
        _chunk("doc_123_chunk_0001", 1, text="Cancellation policy."),
    ]
    embeddings = {
        "doc_123_chunk_0000": [1.0, 0.0],
        "doc_123_chunk_0001": [0.0, 1.0],
    }

    save_document_chunks("doc_123", chunks, embeddings)
    stored_chunks = get_document_chunks("doc_123")

    assert [chunk["chunk_id"] for chunk in stored_chunks] == [
        "doc_123_chunk_0000",
        "doc_123_chunk_0001",
    ]
    assert stored_chunks[0]["embedding"] == [1.0, 0.0]
    assert stored_chunks[1]["text"] == "Cancellation policy."


def test_save_document_chunks_replaces_existing_document_index(isolated_db) -> None:
    save_document_chunks(
        "doc_123",
        [_chunk("doc_123_chunk_0000", 0)],
        {"doc_123_chunk_0000": [1.0]},
    )

    save_document_chunks(
        "doc_123",
        [_chunk("doc_123_chunk_0001", 0, text="Updated policy.")],
        {"doc_123_chunk_0001": [0.5]},
    )

    stored_chunks = get_document_chunks("doc_123")

    assert len(stored_chunks) == 1
    assert stored_chunks[0]["chunk_id"] == "doc_123_chunk_0001"
    assert stored_chunks[0]["text"] == "Updated policy."


def test_save_document_chunks_rejects_empty_chunk_list(isolated_db) -> None:
    with pytest.raises(DocumentVectorStoreError, match="At least one"):
        save_document_chunks("doc_123", [], {})


def test_save_document_chunks_rejects_missing_embedding(isolated_db) -> None:
    with pytest.raises(DocumentVectorStoreError, match="Missing embedding"):
        save_document_chunks("doc_123", [_chunk("doc_123_chunk_0000", 0)], {})


def test_save_document_chunks_rejects_wrong_document_id(isolated_db) -> None:
    with pytest.raises(DocumentVectorStoreError, match="requested document"):
        save_document_chunks("doc_other", [_chunk("doc_123_chunk_0000", 0)], {
            "doc_123_chunk_0000": [1.0],
        })


def test_save_document_chunks_returns_controlled_db_error(isolated_db) -> None:
    with patch(
        "app.services.document_vector_store_service.db_cursor",
        side_effect=sqlite3.Error("db down"),
    ):
        with pytest.raises(DocumentVectorStoreError, match="Database operation failed"):
            save_document_chunks(
                "doc_123",
                [_chunk("doc_123_chunk_0000", 0)],
                {"doc_123_chunk_0000": [1.0]},
            )
