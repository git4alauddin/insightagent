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

These settings prepare upload validation and deterministic chunking for PDF, TXT, and Markdown files.

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

Responsibilities:
- create tables before metadata operations
- store document metadata in SQLite
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
- `DocumentAskResponse`

Key behaviors:
- `DocumentChunk.text` rejects blank chunk text.
- `DocumentChunk.chunk_index` must be zero or greater.
- `DocumentChunk.page` is optional but must be positive when present.
- `DocumentAskRequest.question` trims and rejects blank input.
- `SourceCitation.similarity_score` must be between `0.0` and `1.0`.
- `SourceCitation.page` is optional but must be positive when present.
- `DocumentAskResponse.answer` must not be blank.

## 6. API Layer

### `app/api/routes_documents.py`
Adds:
- `POST /documents/upload`

Flow:
1. Read uploaded file bytes.
2. Validate file name, extension, size, and empty content.
3. Generate a `doc_<uuid>` document ID.
4. Store the raw file under `uploads/documents/<session_or_standalone>/`.
5. Register document metadata in SQLite.
6. Return `DocumentUploadResponse`.

Controlled errors:
- `DOCUMENT_VALIDATION_ERROR` (`400`)
- `DOCUMENT_DB_ERROR` (`503`)
- `DOCUMENT_STORAGE_ERROR` (`503`)

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

## 9. Tests Added

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

## 10. Checklist Mapping
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
- embeddings: pending
- vector store: pending
- retrieval: pending
- grounded answer generation: pending

## 11. Interview Summary
I started V7 by defining the document Q&A contracts, implementing safe document upload persistence, adding text extraction, and adding deterministic document chunking. The backend validates supported document files, stores them with generated IDs, records metadata in SQLite, extracts text from TXT, Markdown, and PDF files, normalizes extracted text, and splits it into overlapping chunks with source metadata. This creates the foundation for the later RAG pipeline: embeddings, retrieval, and grounded answer generation.
