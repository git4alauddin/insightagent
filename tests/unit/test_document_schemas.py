import pytest
from pydantic import ValidationError

from app.schemas.document import (
    DocumentAskRequest,
    DocumentAskResponse,
    DocumentUploadResponse,
    SourceCitation,
)


def test_document_upload_response_accepts_uploaded_status() -> None:
    response = DocumentUploadResponse(
        document_id="doc_123",
        filename="policy.pdf",
        status="uploaded",
    )

    assert response.document_id == "doc_123"
    assert response.status == "uploaded"


def test_document_ask_request_rejects_blank_question() -> None:
    with pytest.raises(ValidationError):
        DocumentAskRequest(question="   ")


def test_source_citation_validates_similarity_score_range() -> None:
    citation = SourceCitation(
        filename="policy.pdf",
        chunk_id="chunk_001",
        page=3,
        similarity_score=0.86,
    )

    assert citation.page == 3
    assert citation.similarity_score == 0.86


def test_source_citation_rejects_invalid_similarity_score() -> None:
    with pytest.raises(ValidationError):
        SourceCitation(
            filename="policy.pdf",
            chunk_id="chunk_001",
            similarity_score=1.5,
        )


def test_document_ask_response_accepts_sources() -> None:
    response = DocumentAskResponse(
        answer="The refund policy is described in the uploaded document.",
        confidence="high",
        document_id="doc_123",
        sources=[
            SourceCitation(
                filename="policy.pdf",
                chunk_id="chunk_001",
                page=1,
                similarity_score=0.91,
            )
        ],
        status="success",
    )

    assert response.sources[0].chunk_id == "chunk_001"
    assert response.status == "success"


def test_document_ask_response_rejects_blank_answer() -> None:
    with pytest.raises(ValidationError):
        DocumentAskResponse(
            answer="",
            confidence="low",
            document_id="doc_123",
            sources=[],
            status="failed",
        )
