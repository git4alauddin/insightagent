import math

import pytest

from app.schemas.document import DocumentChunk
from app.services.document_embedding_service import (
    DocumentEmbeddingError,
    generate_chunk_embeddings,
    generate_embedding,
)


def test_generate_embedding_is_deterministic_and_normalized() -> None:
    first = generate_embedding("Refunds are available within 7 days.", dimensions=16)
    second = generate_embedding("Refunds are available within 7 days.", dimensions=16)

    assert first == second
    assert len(first) == 16
    assert math.isclose(
        math.sqrt(sum(value * value for value in first)),
        1.0,
        rel_tol=1e-9,
    )


def test_generate_embedding_rejects_text_without_tokens() -> None:
    with pytest.raises(DocumentEmbeddingError, match="at least one token"):
        generate_embedding("   ... !!!   ", dimensions=16)


def test_generate_embedding_rejects_invalid_dimensions() -> None:
    with pytest.raises(DocumentEmbeddingError, match="greater than 0"):
        generate_embedding("Refund policy", dimensions=0)


def test_generate_chunk_embeddings_returns_embedding_per_chunk() -> None:
    chunks = [
        DocumentChunk(
            chunk_id="doc_123_chunk_0000",
            document_id="doc_123",
            filename="policy.txt",
            chunk_index=0,
            text="Refund policy.",
        ),
        DocumentChunk(
            chunk_id="doc_123_chunk_0001",
            document_id="doc_123",
            filename="policy.txt",
            chunk_index=1,
            text="Cancellation policy.",
        ),
    ]

    embeddings = generate_chunk_embeddings(chunks, dimensions=8)

    assert sorted(embeddings) == ["doc_123_chunk_0000", "doc_123_chunk_0001"]
    assert len(embeddings["doc_123_chunk_0000"]) == 8
