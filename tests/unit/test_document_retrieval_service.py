from unittest.mock import patch

import pytest

from app.services.document_retrieval_service import (
    DocumentRetrievalError,
    cosine_similarity,
    retrieve_relevant_chunks,
    similarity_score,
)


def test_cosine_similarity_returns_expected_score() -> None:
    assert cosine_similarity([1.0, 0.0], [1.0, 0.0]) == 1.0
    assert cosine_similarity([1.0, 0.0], [0.0, 1.0]) == 0.0


def test_similarity_score_maps_cosine_to_zero_one_range() -> None:
    assert similarity_score([1.0, 0.0], [1.0, 0.0]) == 1.0
    assert similarity_score([1.0, 0.0], [-1.0, 0.0]) == 0.0


def test_retrieve_relevant_chunks_returns_ranked_top_k_matches() -> None:
    stored_chunks = [
        {
            "chunk_id": "doc_123_chunk_0000",
            "document_id": "doc_123",
            "filename": "policy.txt",
            "chunk_index": 0,
            "text": "Refund policy.",
            "page": None,
            "embedding": [1.0, 0.0],
        },
        {
            "chunk_id": "doc_123_chunk_0001",
            "document_id": "doc_123",
            "filename": "policy.txt",
            "chunk_index": 1,
            "text": "Cancellation policy.",
            "page": 2,
            "embedding": [0.0, 1.0],
        },
    ]

    with (
        patch(
            "app.services.document_retrieval_service.generate_embedding",
            return_value=[1.0, 0.0],
        ),
        patch(
            "app.services.document_retrieval_service.get_document_chunks",
            return_value=stored_chunks,
        ),
    ):
        result = retrieve_relevant_chunks(
            "doc_123",
            "refund",
            top_k=1,
            similarity_threshold=0.0,
        )

    assert result.candidate_count == 2
    assert len(result.retrieved_chunks) == 1
    assert result.retrieved_chunks[0].chunk_id == "doc_123_chunk_0000"
    assert result.retrieved_chunks[0].similarity_score == 1.0


def test_retrieve_relevant_chunks_applies_similarity_threshold() -> None:
    stored_chunks = [
        {
            "chunk_id": "doc_123_chunk_0000",
            "document_id": "doc_123",
            "filename": "policy.txt",
            "chunk_index": 0,
            "text": "Unrelated policy.",
            "page": None,
            "embedding": [-1.0, 0.0],
        }
    ]

    with (
        patch(
            "app.services.document_retrieval_service.generate_embedding",
            return_value=[1.0, 0.0],
        ),
        patch(
            "app.services.document_retrieval_service.get_document_chunks",
            return_value=stored_chunks,
        ),
    ):
        result = retrieve_relevant_chunks(
            "doc_123",
            "refund",
            top_k=3,
            similarity_threshold=0.1,
        )

    assert result.retrieved_chunks == []
    assert result.candidate_count == 1


def test_retrieve_relevant_chunks_rejects_blank_question() -> None:
    with pytest.raises(DocumentRetrievalError, match="Question must not be empty"):
        retrieve_relevant_chunks("doc_123", "   ")


def test_retrieve_relevant_chunks_rejects_invalid_top_k() -> None:
    with pytest.raises(DocumentRetrievalError, match="greater than 0"):
        retrieve_relevant_chunks("doc_123", "refund", top_k=0)


def test_retrieve_relevant_chunks_rejects_invalid_threshold() -> None:
    with pytest.raises(DocumentRetrievalError, match="between 0.0 and 1.0"):
        retrieve_relevant_chunks("doc_123", "refund", similarity_threshold=1.2)


def test_cosine_similarity_rejects_mismatched_dimensions() -> None:
    with pytest.raises(DocumentRetrievalError, match="same dimensions"):
        cosine_similarity([1.0], [1.0, 0.0])
