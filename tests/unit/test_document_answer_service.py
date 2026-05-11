from unittest.mock import patch

import pytest

from app.prompts.document_qa_v7 import (
    DOCUMENT_QA_PROMPT_VERSION,
    build_grounded_document_prompt,
)
from app.schemas.document import DocumentRetrievalResult, RetrievedDocumentChunk
from app.services.document_answer_service import (
    DocumentAnswerError,
    answer_document_question,
    build_answer_from_retrieval,
    build_citations,
    build_grounded_answer_text,
    build_grounded_prompt_from_retrieval,
)
from app.services.document_retrieval_service import DocumentRetrievalError


def _retrieved_chunk(
    chunk_id: str = "doc_123_chunk_0000",
    text: str = "Refunds are available within 7 days.",
    score: float = 0.91,
) -> RetrievedDocumentChunk:
    return RetrievedDocumentChunk(
        chunk_id=chunk_id,
        document_id="doc_123",
        filename="policy.txt",
        chunk_index=0,
        text=text,
        page=2,
        similarity_score=score,
    )


def _retrieval_result(
    chunks: list[RetrievedDocumentChunk],
) -> DocumentRetrievalResult:
    return DocumentRetrievalResult(
        document_id="doc_123",
        question="What is the refund policy?",
        retrieved_chunks=chunks,
        top_k=3,
        similarity_threshold=0.2,
        candidate_count=len(chunks),
    )


def test_build_citations_from_retrieved_chunks() -> None:
    citations = build_citations([_retrieved_chunk()])

    assert citations[0].filename == "policy.txt"
    assert citations[0].chunk_id == "doc_123_chunk_0000"
    assert citations[0].page == 2
    assert citations[0].similarity_score == 0.91


def test_build_answer_from_retrieval_returns_success_with_citations() -> None:
    response = build_answer_from_retrieval(_retrieval_result([_retrieved_chunk()]))

    assert response.status == "success"
    assert response.confidence == "high"
    assert response.sources[0].chunk_id == "doc_123_chunk_0000"
    assert "Refunds are available within 7 days." in response.answer


def test_build_answer_from_retrieval_returns_insufficient_context_without_chunks() -> None:
    response = build_answer_from_retrieval(_retrieval_result([]))

    assert response.status == "insufficient_context"
    assert response.confidence == "low"
    assert response.sources == []
    assert "not have enough context" in response.answer


def test_build_grounded_answer_text_uses_only_retrieved_context() -> None:
    answer = build_grounded_answer_text([
        _retrieved_chunk(text="The policy allows refunds."),
        _retrieved_chunk(
            chunk_id="doc_123_chunk_0001",
            text="Refunds must be requested within 7 days.",
        ),
    ])

    assert "The policy allows refunds." in answer
    assert "Refunds must be requested within 7 days." in answer
    assert "outside knowledge" not in answer.lower()


def test_grounded_prompt_contains_question_context_and_citation_metadata() -> None:
    prompt = build_grounded_document_prompt(
        "What is the refund policy?",
        [_retrieved_chunk()],
    )

    assert DOCUMENT_QA_PROMPT_VERSION == "document_qa_v7"
    assert "Answer only from the provided retrieved document context." in prompt
    assert "What is the refund policy?" in prompt
    assert "doc_123_chunk_0000" in prompt
    assert "policy.txt" in prompt
    assert "Refunds are available within 7 days." in prompt


def test_build_grounded_prompt_from_retrieval() -> None:
    prompt = build_grounded_prompt_from_retrieval(
        _retrieval_result([_retrieved_chunk()])
    )

    assert "What is the refund policy?" in prompt
    assert "doc_123_chunk_0000" in prompt


def test_answer_document_question_uses_retrieval_service() -> None:
    with patch(
        "app.services.document_answer_service.retrieve_relevant_chunks",
        return_value=_retrieval_result([_retrieved_chunk(score=0.7)]),
    ):
        response = answer_document_question("doc_123", "What is the refund policy?")

    assert response.status == "success"
    assert response.confidence == "medium"


def test_answer_document_question_converts_retrieval_errors() -> None:
    with patch(
        "app.services.document_answer_service.retrieve_relevant_chunks",
        side_effect=DocumentRetrievalError("retrieval failed"),
    ):
        with pytest.raises(DocumentAnswerError, match="retrieval failed"):
            answer_document_question("doc_123", "What is the refund policy?")
