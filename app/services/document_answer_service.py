from app.prompts.document_qa_v7 import build_grounded_document_prompt
from app.schemas.document import (
    DocumentAskResponse,
    DocumentRetrievalResult,
    RetrievedDocumentChunk,
    SourceCitation,
)
from app.services.document_retrieval_service import (
    DocumentRetrievalError,
    retrieve_relevant_chunks,
)


INSUFFICIENT_CONTEXT_ANSWER = (
    "I do not have enough context in the uploaded document to answer that question."
)


class DocumentAnswerError(Exception):
    pass


def answer_document_question(document_id: str, question: str) -> DocumentAskResponse:
    try:
        retrieval_result = retrieve_relevant_chunks(document_id, question)
    except DocumentRetrievalError as exc:
        raise DocumentAnswerError(str(exc)) from exc

    return build_answer_from_retrieval(retrieval_result)


def build_answer_from_retrieval(
    retrieval_result: DocumentRetrievalResult,
) -> DocumentAskResponse:
    if not retrieval_result.retrieved_chunks:
        return DocumentAskResponse(
            answer=INSUFFICIENT_CONTEXT_ANSWER,
            confidence="low",
            document_id=retrieval_result.document_id,
            sources=[],
            status="insufficient_context",
        )

    return DocumentAskResponse(
        answer=build_grounded_answer_text(retrieval_result.retrieved_chunks),
        confidence=_confidence_from_similarity(retrieval_result.retrieved_chunks[0]),
        document_id=retrieval_result.document_id,
        sources=build_citations(retrieval_result.retrieved_chunks),
        status="success",
    )


def build_citations(
    retrieved_chunks: list[RetrievedDocumentChunk],
) -> list[SourceCitation]:
    return [
        SourceCitation(
            filename=chunk.filename,
            chunk_id=chunk.chunk_id,
            similarity_score=chunk.similarity_score,
            page=chunk.page,
        )
        for chunk in retrieved_chunks
    ]


def build_grounded_answer_text(
    retrieved_chunks: list[RetrievedDocumentChunk],
    max_answer_chars: int = 900,
) -> str:
    context_text = " ".join(chunk.text.strip() for chunk in retrieved_chunks)
    trimmed_context = context_text[:max_answer_chars].rstrip()
    if len(context_text) > max_answer_chars:
        trimmed_context = f"{trimmed_context}..."

    return f"Based on the retrieved document context: {trimmed_context}"


def build_grounded_prompt_from_retrieval(
    retrieval_result: DocumentRetrievalResult,
) -> str:
    return build_grounded_document_prompt(
        retrieval_result.question,
        retrieval_result.retrieved_chunks,
    )


def _confidence_from_similarity(top_chunk: RetrievedDocumentChunk) -> str:
    if top_chunk.similarity_score >= 0.8:
        return "high"

    if top_chunk.similarity_score >= 0.5:
        return "medium"

    return "low"
