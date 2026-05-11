import math

from app.config import settings
from app.schemas.document import DocumentRetrievalResult, RetrievedDocumentChunk
from app.services.document_embedding_service import (
    DocumentEmbeddingError,
    generate_embedding,
)
from app.services.document_vector_store_service import (
    DocumentVectorStoreError,
    get_document_chunks,
)


class DocumentRetrievalError(Exception):
    pass


def retrieve_relevant_chunks(
    document_id: str,
    question: str,
    *,
    top_k: int | None = None,
    similarity_threshold: float | None = None,
) -> DocumentRetrievalResult:
    resolved_top_k = settings.document_retrieval_top_k if top_k is None else top_k
    resolved_threshold = (
        settings.document_similarity_threshold
        if similarity_threshold is None
        else similarity_threshold
    )
    _validate_retrieval_settings(resolved_top_k, resolved_threshold)

    cleaned_question = question.strip()
    if not cleaned_question:
        raise DocumentRetrievalError("Question must not be empty.")

    try:
        question_embedding = generate_embedding(cleaned_question)
        stored_chunks = get_document_chunks(document_id)
    except (DocumentEmbeddingError, DocumentVectorStoreError) as exc:
        raise DocumentRetrievalError(str(exc)) from exc

    scored_chunks = [
        _build_retrieved_chunk(chunk, question_embedding)
        for chunk in stored_chunks
    ]
    matching_chunks = [
        chunk
        for chunk in scored_chunks
        if chunk.similarity_score >= resolved_threshold
    ]
    matching_chunks.sort(key=lambda chunk: chunk.similarity_score, reverse=True)

    return DocumentRetrievalResult(
        document_id=document_id,
        question=cleaned_question,
        retrieved_chunks=matching_chunks[:resolved_top_k],
        top_k=resolved_top_k,
        similarity_threshold=resolved_threshold,
        candidate_count=len(stored_chunks),
    )


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right:
        raise DocumentRetrievalError("Vectors must not be empty.")

    if len(left) != len(right):
        raise DocumentRetrievalError("Vectors must have the same dimensions.")

    left_magnitude = math.sqrt(sum(value * value for value in left))
    right_magnitude = math.sqrt(sum(value * value for value in right))
    if left_magnitude == 0 or right_magnitude == 0:
        raise DocumentRetrievalError("Vectors must not have zero magnitude.")

    dot_product = sum(
        left_value * right_value
        for left_value, right_value in zip(left, right)
    )
    return dot_product / (left_magnitude * right_magnitude)


def similarity_score(left: list[float], right: list[float]) -> float:
    cosine_score = cosine_similarity(left, right)
    bounded_cosine = max(-1.0, min(1.0, cosine_score))
    return (bounded_cosine + 1.0) / 2.0


def _build_retrieved_chunk(
    stored_chunk: dict[str, object],
    question_embedding: list[float],
) -> RetrievedDocumentChunk:
    embedding = stored_chunk["embedding"]
    if not isinstance(embedding, list):
        raise DocumentRetrievalError("Stored chunk embedding is invalid.")

    return RetrievedDocumentChunk(
        chunk_id=str(stored_chunk["chunk_id"]),
        document_id=str(stored_chunk["document_id"]),
        filename=str(stored_chunk["filename"]),
        chunk_index=int(stored_chunk["chunk_index"]),
        text=str(stored_chunk["text"]),
        page=stored_chunk["page"],
        similarity_score=similarity_score(question_embedding, embedding),
    )


def _validate_retrieval_settings(top_k: int, similarity_threshold: float) -> None:
    if top_k <= 0:
        raise DocumentRetrievalError("Retrieval top_k must be greater than 0.")

    if not 0.0 <= similarity_threshold <= 1.0:
        raise DocumentRetrievalError(
            "Similarity threshold must be between 0.0 and 1.0."
        )
