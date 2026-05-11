import pytest

from app.services.document_chunking_service import (
    DocumentChunkingError,
    chunk_document_text,
    clean_document_text,
)


def test_clean_document_text_collapses_whitespace() -> None:
    text = clean_document_text(" Refunds\n\nare\tavailable.  ")

    assert text == "Refunds are available."


def test_chunks_short_document_into_single_chunk_with_metadata() -> None:
    chunks = chunk_document_text(
        document_id="doc_123",
        filename="policy.txt",
        text="Refunds are available within 7 days.",
        chunk_size=100,
        chunk_overlap=10,
        page=2,
    )

    assert len(chunks) == 1
    assert chunks[0].chunk_id == "doc_123_chunk_0000"
    assert chunks[0].chunk_index == 0
    assert chunks[0].document_id == "doc_123"
    assert chunks[0].filename == "policy.txt"
    assert chunks[0].page == 2


def test_chunks_long_document_with_overlap() -> None:
    chunks = chunk_document_text(
        document_id="doc_abc",
        filename="policy.md",
        text="abcdefghijklmnopqrstuvwxyz",
        chunk_size=10,
        chunk_overlap=3,
    )

    assert [chunk.text for chunk in chunks] == [
        "abcdefghij",
        "hijklmnopq",
        "opqrstuvwx",
        "vwxyz",
    ]
    assert chunks[0].text[-3:] == chunks[1].text[:3]
    assert chunks[1].text[-3:] == chunks[2].text[:3]


def test_rejects_empty_text_after_cleaning() -> None:
    with pytest.raises(DocumentChunkingError, match="empty after cleaning"):
        chunk_document_text(
            document_id="doc_empty",
            filename="empty.txt",
            text=" \n\t ",
        )


def test_rejects_zero_chunk_size() -> None:
    with pytest.raises(DocumentChunkingError, match="greater than 0"):
        chunk_document_text(
            document_id="doc_123",
            filename="policy.txt",
            text="Some text",
            chunk_size=0,
            chunk_overlap=0,
        )


def test_rejects_negative_chunk_overlap() -> None:
    with pytest.raises(DocumentChunkingError, match="cannot be negative"):
        chunk_document_text(
            document_id="doc_123",
            filename="policy.txt",
            text="Some text",
            chunk_size=10,
            chunk_overlap=-1,
        )


def test_rejects_overlap_that_is_not_smaller_than_chunk_size() -> None:
    with pytest.raises(DocumentChunkingError, match="smaller than chunk size"):
        chunk_document_text(
            document_id="doc_123",
            filename="policy.txt",
            text="Some text",
            chunk_size=10,
            chunk_overlap=10,
        )
