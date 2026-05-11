from app.services.document_chunking_service import (
    DocumentChunkingError,
    chunk_document_text,
)
from app.services.document_embedding_service import (
    DocumentEmbeddingError,
    generate_chunk_embeddings,
)
from app.services.document_text_service import (
    DocumentTextExtractionError,
    extract_document_text,
)
from app.services.document_vector_store_service import (
    DocumentVectorStoreError,
    save_document_chunks,
)


class DocumentIndexingError(Exception):
    pass


def index_document(
    document_id: str,
    filename: str,
    storage_path: str,
    file_extension: str,
) -> int:
    try:
        extracted_text = extract_document_text(storage_path, file_extension)
        chunks = chunk_document_text(
            document_id=document_id,
            filename=filename,
            text=extracted_text,
        )
        embeddings_by_chunk_id = generate_chunk_embeddings(chunks)
        save_document_chunks(document_id, chunks, embeddings_by_chunk_id)
    except (
        DocumentTextExtractionError,
        DocumentChunkingError,
        DocumentEmbeddingError,
        DocumentVectorStoreError,
    ) as exc:
        raise DocumentIndexingError(str(exc)) from exc

    return len(chunks)
