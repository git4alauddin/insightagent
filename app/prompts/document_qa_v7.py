from app.schemas.document import RetrievedDocumentChunk


DOCUMENT_QA_PROMPT_VERSION = "document_qa_v7"

DOCUMENT_QA_SYSTEM_PROMPT = """
You are InsightAgent's document Q&A assistant.
Answer only from the provided retrieved document context.
If the context is not enough, say that there is not enough information.
Do not use outside knowledge.
Do not invent citations.
""".strip()


def build_grounded_document_prompt(
    question: str,
    retrieved_chunks: list[RetrievedDocumentChunk],
) -> str:
    context_blocks = "\n\n".join(
        _format_context_block(chunk)
        for chunk in retrieved_chunks
    )

    return f"""
{DOCUMENT_QA_SYSTEM_PROMPT}

Question:
{question.strip()}

Retrieved context:
{context_blocks}

Return a concise answer grounded only in the retrieved context.
""".strip()


def _format_context_block(chunk: RetrievedDocumentChunk) -> str:
    page_label = f", page {chunk.page}" if chunk.page is not None else ""
    return (
        f"[{chunk.chunk_id} | {chunk.filename}{page_label} | "
        f"score={chunk.similarity_score:.3f}]\n{chunk.text}"
    )
