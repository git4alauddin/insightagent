from pathlib import Path

import app.db.database as database_module
import pytest

from app.services.document_indexing_service import DocumentIndexingError, index_document
from app.services.document_vector_store_service import get_document_chunks


@pytest.fixture
def isolated_db(monkeypatch, tmp_path):
    db_path = tmp_path / "test_document_indexing.db"
    monkeypatch.setattr(database_module, "DB_PATH", db_path)
    return db_path


def test_index_document_extracts_chunks_embeds_and_stores_vectors(
    isolated_db,
    tmp_path: Path,
) -> None:
    document_path = tmp_path / "policy.txt"
    document_path.write_text(
        "Refunds are available within 7 days. Cancellation rules are separate.",
        encoding="utf-8",
    )

    chunk_count = index_document(
        document_id="doc_123",
        filename="policy.txt",
        storage_path=str(document_path),
        file_extension=".txt",
    )
    stored_chunks = get_document_chunks("doc_123")

    assert chunk_count == 1
    assert stored_chunks[0]["chunk_id"] == "doc_123_chunk_0000"
    assert stored_chunks[0]["filename"] == "policy.txt"
    assert "Refunds are available" in str(stored_chunks[0]["text"])
    assert len(stored_chunks[0]["embedding"]) > 0


def test_index_document_returns_controlled_error_for_unreadable_text(
    isolated_db,
    tmp_path: Path,
) -> None:
    missing_path = tmp_path / "missing.txt"

    with pytest.raises(DocumentIndexingError, match="could not be read"):
        index_document(
            document_id="doc_123",
            filename="missing.txt",
            storage_path=str(missing_path),
            file_extension=".txt",
        )
