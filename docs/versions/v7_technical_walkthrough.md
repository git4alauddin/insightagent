# V7 Technical Walkthrough

This document explains the V7 document Q&A layer file by file as it grows.

## 1. Design Intent
V7 will add RAG-based document question answering.

The important design rule:
- the system should answer from retrieved document context
- if context is weak, it should say there is not enough evidence
- every grounded answer should include source citations

## 2. Configuration

### `app/config.py`
Added:
- `document_max_file_size_mb`
- `allowed_document_extensions`
- `document_chunk_size`
- `document_chunk_overlap`
- `document_embedding_dimensions`
- `document_retrieval_top_k`
- `document_similarity_threshold`

These settings prepare upload validation, deterministic chunking, local vector indexing, and semantic retrieval for PDF, TXT, and Markdown files.

## 3. Database Metadata

### `app/db/schema.py`
Adds `documents` table:
- `document_id`
- `session_id`
- `filename`
- `storage_path`
- `file_extension`
- `file_size_bytes`
- `status`
- `uploaded_at`

The table includes migration-safe column checks through `_ensure_documents_columns(...)`.

### `app/services/document_registry_service.py`
Core functions:
- `register_document_metadata(...)`
- `get_document_metadata(document_id)`
- `update_document_status(document_id, status)`

Responsibilities:
- create tables before metadata operations
- store document metadata in SQLite
- mark documents as `indexed` after upload-time indexing succeeds
- convert SQLite failures into `DocumentRegistryError`
- return explicit not-found errors for missing document IDs

## 4. Upload Validation and Response Service

### `app/services/document_service.py`
Core functions:
- `validate_document_file(file_name, file_size_bytes)`
- `build_document_upload_response(...)`

Validation guardrails:
- extension must be `.pdf`, `.txt`, or `.md`
- file must not be empty
- file size must stay under `DOCUMENT_MAX_FILE_SIZE_MB`

## 5. Data Contracts

### `app/schemas/document.py`
Main models:
- `DocumentUploadResponse`
- `DocumentChunk`
- `DocumentAskRequest`
- `SourceCitation`
- `RetrievedDocumentChunk`
- `DocumentRetrievalResult`
- `DocumentAskResponse`

Key behaviors:
- `DocumentChunk.text` rejects blank chunk text.
- `DocumentChunk.chunk_index` must be zero or greater.
- `DocumentChunk.page` is optional but must be positive when present.
- `DocumentAskRequest.question` trims and rejects blank input.
- `SourceCitation.similarity_score` must be between `0.0` and `1.0`.
- `SourceCitation.page` is optional but must be positive when present.
- `RetrievedDocumentChunk` carries source chunk text and similarity score.
- `DocumentRetrievalResult` carries top-k, threshold, candidate count, and matching chunks.
- `DocumentAskResponse.answer` must not be blank.

## 6. API Layer

### `app/api/routes_documents.py`
Adds:
- `POST /documents/upload`
- `POST /documents/{document_id}/ask`

Upload flow:
1. Read uploaded file bytes.
2. Validate file name, extension, size, and empty content.
3. Generate a `doc_<uuid>` document ID.
4. Store the raw file under `uploads/documents/<session_or_standalone>/`.
5. Register document metadata in SQLite.
6. Index the document.
7. Mark the document as `indexed`.
8. Return `DocumentUploadResponse`.

Ask flow:
1. Validate the request body through `DocumentAskRequest`.
2. Confirm the document exists in SQLite metadata.
3. Call `answer_document_question(...)`.
4. Return `DocumentAskResponse`.

Controlled errors:
- `DOCUMENT_VALIDATION_ERROR` (`400`)
- `DOCUMENT_NOT_FOUND` (`404`)
- `DOCUMENT_DB_ERROR` (`503`)
- `DOCUMENT_STORAGE_ERROR` (`503`)
- `DOCUMENT_INDEXING_ERROR` (`400`)
- `DOCUMENT_ANSWER_ERROR` (`503`)

### `app/main.py`
Includes document router.

## 7. Text Extraction

### `app/services/document_text_service.py`
Core function:
- `extract_document_text(storage_path, file_extension)`

Supported extraction paths:
- `.txt`
- `.md`
- `.pdf`

Behavior:
- TXT and Markdown files are read as UTF-8.
- PDF files are read with `pypdf.PdfReader`.
- missing/unreadable files return `DocumentTextExtractionError`.
- empty extracted text returns `DocumentTextExtractionError`.
- unsupported extensions return `DocumentTextExtractionError`.

## 8. Text Cleaning and Chunking

### `app/services/document_chunking_service.py`
Core functions:
- `clean_document_text(text)`
- `chunk_document_text(...)`

Behavior:
- collapses repeated whitespace into single spaces
- rejects empty text after cleaning
- validates chunk size and overlap settings
- creates deterministic overlapping chunks
- attaches metadata for document ID, filename, chunk index, chunk ID, and optional page

Chunk ID format:
```text
<document_id>_chunk_<zero_padded_index>
```

Example:
```json
{
  "chunk_id": "doc_123_chunk_0000",
  "document_id": "doc_123",
  "filename": "policy.pdf",
  "chunk_index": 0,
  "text": "Refund policy...",
  "page": null
}
```

## 9. Local Embeddings and Vector Store

### `app/services/document_embedding_service.py`
Core functions:
- `generate_embedding(text, dimensions=None)`
- `generate_chunk_embeddings(chunks, dimensions=None)`

Behavior:
- tokenizes text into alphanumeric tokens
- hashes tokens into a fixed-size vector
- normalizes vectors to unit length
- rejects invalid dimensions
- rejects text without tokens

This is a local deterministic embedding foundation. It avoids external API dependency while the retrieval pipeline is still being built.

### `app/db/schema.py`
Adds `document_chunks` table:
- `chunk_id`
- `document_id`
- `filename`
- `chunk_index`
- `text`
- `page`
- `embedding_json`
- `created_at`

### `app/services/document_vector_store_service.py`
Core functions:
- `save_document_chunks(document_id, chunks, embeddings_by_chunk_id)`
- `get_document_chunks(document_id)`

Responsibilities:
- create tables before vector operations
- validate chunks and embeddings before saving
- replace an existing document index during re-indexing
- store embeddings as JSON in SQLite
- load indexed chunks in chunk order
- convert SQLite failures into `DocumentVectorStoreError`

## 10. Semantic Retrieval

### `app/services/document_retrieval_service.py`
Core functions:
- `retrieve_relevant_chunks(document_id, question, top_k=None, similarity_threshold=None)`
- `cosine_similarity(left, right)`
- `similarity_score(left, right)`

Behavior:
- embeds the question with the local embedding service
- loads indexed chunks through the vector store service
- computes cosine similarity between question and chunk vectors
- maps cosine similarity from `-1.0..1.0` into `0.0..1.0`
- filters chunks below the configured similarity threshold
- sorts matches by descending similarity score
- returns only the configured top-k matches

Retrieval result includes:
- `document_id`
- `question`
- `retrieved_chunks`
- `top_k`
- `similarity_threshold`
- `candidate_count`

This gives the later answer endpoint a concrete evidence set and retrieval trace before any LLM answer is generated.

## 11. Grounded Answer Service

### `app/prompts/document_qa_v7.py`
Core values/functions:
- `DOCUMENT_QA_PROMPT_VERSION`
- `DOCUMENT_QA_SYSTEM_PROMPT`
- `build_grounded_document_prompt(question, retrieved_chunks)`

Behavior:
- instructs the assistant to answer only from retrieved context
- tells the assistant to admit insufficient context
- formats chunk ID, filename, page, score, and text into context blocks
- avoids invented citations by making source chunks explicit

### `app/services/document_answer_service.py`
Core functions:
- `answer_document_question(document_id, question)`
- `build_answer_from_retrieval(retrieval_result)`
- `build_citations(retrieved_chunks)`
- `build_grounded_answer_text(retrieved_chunks)`
- `build_grounded_prompt_from_retrieval(retrieval_result)`

Behavior:
- calls semantic retrieval for the document/question pair
- returns `insufficient_context` when no chunks pass retrieval
- builds `SourceCitation` objects from retrieved chunk metadata
- returns a grounded extractive answer using retrieved chunk text only
- maps top similarity score to low/medium/high confidence
- converts retrieval failures into `DocumentAnswerError`

## 12. Public Document Ask Endpoint

### `app/api/routes_documents.py`
The endpoint:
```http
POST /documents/{document_id}/ask
```

Responsibilities:
- keep the endpoint protected by API key and rate limiting through router dependencies
- validate `question` with `DocumentAskRequest`
- verify the document exists before answer generation
- return `DOCUMENT_NOT_FOUND` for unknown document IDs
- return grounded answer responses from `DocumentAskResponse`
- return controlled `DOCUMENT_ANSWER_ERROR` for answer-service failures

Weak retrieval is not treated as an exception. It returns a normal `DocumentAskResponse` with:
```json
{
  "status": "insufficient_context",
  "confidence": "low",
  "sources": []
}
```

## 13. Upload-Time Indexing

### `app/services/document_indexing_service.py`
Core function:
- `index_document(document_id, filename, storage_path, file_extension)`

Flow:
1. Extract text from the stored document.
2. Chunk the extracted text.
3. Generate embeddings for each chunk.
4. Save chunks and vectors in SQLite.
5. Return the number of chunks indexed.

Errors from extraction, chunking, embedding, and vector storage are converted into `DocumentIndexingError`.

### `app/api/routes_documents.py`
The upload endpoint now calls `index_document(...)` after metadata registration.

Successful uploads now return:
```json
{
  "document_id": "doc_123",
  "filename": "policy.txt",
  "status": "indexed"
}
```

This makes the document immediately available for `/documents/{document_id}/ask`.

## 14. Tests Added

### `tests/unit/test_document_schemas.py`
Verifies:
- upload response status contract
- blank question rejection
- citation score validation
- answer response contract
- blank answer rejection

### `tests/integration/test_document_upload_endpoint.py`
Verifies:
- successful document upload
- metadata persistence
- unsupported type rejection
- empty document rejection
- controlled DB error handling

### `tests/unit/test_document_text_service.py`
Verifies:
- TXT extraction
- Markdown extraction
- PDF extraction path
- empty extracted text handling
- missing file handling
- unsupported extraction extension handling

### `tests/unit/test_document_chunking_service.py`
Verifies:
- whitespace cleaning
- single-chunk metadata
- overlapping multi-chunk output
- empty cleaned text handling
- invalid chunk size handling
- invalid chunk overlap handling

### `tests/unit/test_document_embedding_service.py`
Verifies:
- deterministic embedding output
- normalized vectors
- invalid dimension handling
- text-without-token handling
- embedding generation per chunk

### `tests/unit/test_document_vector_store_service.py`
Verifies:
- chunk/vector save and load
- chunk ordering
- index replacement for re-indexing
- empty chunk list rejection
- missing embedding rejection
- wrong document ID rejection
- controlled DB error handling

### `tests/unit/test_document_retrieval_service.py`
Verifies:
- cosine similarity calculation
- similarity score mapping into `0.0..1.0`
- ranked top-k retrieval
- threshold filtering
- blank question rejection
- invalid top-k rejection
- invalid threshold rejection
- vector dimension validation

### `tests/unit/test_document_answer_service.py`
Verifies:
- citation building from retrieved chunks
- successful grounded answer response
- insufficient-context fallback
- extractive grounded answer text
- grounded prompt contents
- retrieval service orchestration
- retrieval error conversion

### `tests/integration/test_document_ask_endpoint.py`
Verifies:
- successful document answer response with citations
- insufficient-context response when no chunks are indexed
- missing document returns `DOCUMENT_NOT_FOUND`
- answer-service failure returns `DOCUMENT_ANSWER_ERROR`

### `tests/unit/test_document_indexing_service.py`
Verifies:
- indexing extracts, chunks, embeds, and stores vectors
- extraction failures return `DocumentIndexingError`

### `tests/integration/test_document_rag_flow.py`
Verifies:
- upload returns indexed status
- uploaded document chunks are stored
- ask works immediately after upload
- answer includes citation source from indexed chunk
- indexing failures return `DOCUMENT_INDEXING_ERROR`

## 15. Checklist Mapping
- document upload endpoint: done
- supported document extensions config: done
- unsupported document-type handling: done
- citation schema: done
- document ask request/response contracts: done
- raw document persistence: done
- document metadata storage: done
- text extraction: done
- empty text extraction handling: done
- text cleaning: done
- chunking: done
- chunk size configuration: done
- chunk overlap configuration: done
- chunk metadata: done
- embedding generation: done
- vector store integration: done
- semantic retrieval: done
- top-k retrieval: done
- similarity threshold: done
- retrieval log with chunks/scores: done
- grounded answer prompt: done
- answer generated only from retrieved context: done
- citation builder: done
- weak-context fallback: done
- `/documents/{document_id}/ask` endpoint: done
- insufficient-context test questions: service-level done
- citation examples in docs: done
- automatic upload-time indexing: done
- RAG flow tested end-to-end: automated test done
- RAG flow manually tested end-to-end: pending

## 16. Interview Summary
I started V7 by defining the document Q&A contracts, implementing safe document upload persistence, adding text extraction, deterministic document chunking, local embedding generation, SQLite-backed vector persistence, semantic retrieval, a grounded answer service, the public document ask endpoint, and automatic upload-time indexing. The backend validates supported document files, stores them with generated IDs, records metadata in SQLite, extracts text from TXT, Markdown, and PDF files, normalizes extracted text, splits it into overlapping chunks with source metadata, generates deterministic local embeddings, stores chunk vectors, marks documents as indexed, retrieves the most relevant chunks for a question using top-k and similarity threshold controls, builds citations from retrieved chunks, returns insufficient-context fallback when evidence is missing, and exposes the answer flow through `POST /documents/{document_id}/ask`.
