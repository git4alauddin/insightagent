import re

from app.config import settings
from app.schemas.document import DocumentChunk


class DocumentChunkingError(Exception):
    """Raised when document text cannot be safely chunked."""


def clean_document_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def chunk_document_text(
    document_id: str,
    filename: str,
    text: str,
    *,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
    page: int | None = None,
) -> list[DocumentChunk]:
    resolved_chunk_size = (
        settings.document_chunk_size if chunk_size is None else chunk_size
    )
    resolved_chunk_overlap = (
        settings.document_chunk_overlap if chunk_overlap is None else chunk_overlap
    )
    _validate_chunk_settings(resolved_chunk_size, resolved_chunk_overlap)

    cleaned_text = clean_document_text(text)
    if not cleaned_text:
        raise DocumentChunkingError("Document text is empty after cleaning.")

    chunks: list[DocumentChunk] = []
    start = 0

    while start < len(cleaned_text):
        end = min(start + resolved_chunk_size, len(cleaned_text))
        chunk_text = cleaned_text[start:end].strip()

        if chunk_text:
            chunk_index = len(chunks)
            chunks.append(
                DocumentChunk(
                    chunk_id=f"{document_id}_chunk_{chunk_index:04d}",
                    document_id=document_id,
                    filename=filename,
                    chunk_index=chunk_index,
                    text=chunk_text,
                    page=page,
                )
            )

        if end == len(cleaned_text):
            break

        start = end - resolved_chunk_overlap

    return chunks


def _validate_chunk_settings(chunk_size: int, chunk_overlap: int) -> None:
    if chunk_size <= 0:
        raise DocumentChunkingError("Document chunk size must be greater than 0.")

    if chunk_overlap < 0:
        raise DocumentChunkingError("Document chunk overlap cannot be negative.")

    if chunk_overlap >= chunk_size:
        raise DocumentChunkingError(
            "Document chunk overlap must be smaller than chunk size."
        )
