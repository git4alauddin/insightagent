# V7 - RAG Document Q&A

## Version Goal
V7 adds document-grounded question answering to InsightAgent.

The target flow is:
- upload a document
- extract text
- split it into chunks
- embed and store chunks
- retrieve relevant chunks for a question
- answer only from retrieved context
- return citations and weak-context fallback when evidence is not enough

## Current Progress

### Document Contracts
Added document schema contracts in `app/schemas/document.py`.

Models:
- `DocumentUploadResponse`
- `DocumentAskRequest`
- `SourceCitation`
- `DocumentAskResponse`

### Document Config
Added document upload guardrail settings:
- `DOCUMENT_MAX_FILE_SIZE_MB`
- `ALLOWED_DOCUMENT_EXTENSIONS`

Default supported extensions:
- `.pdf`
- `.txt`
- `.md`

### Document Upload Endpoint
Added:
```http
POST /documents/upload
```

Current behavior:
- validates file name
- validates extension
- validates non-empty file
- validates file size
- stores the raw file under `uploads/documents/...`
- stores metadata in SQLite
- returns a stable `document_id`

### Text Extraction Service
Added text extraction for:
- `.txt`
- `.md`
- `.pdf`

Behavior:
- TXT/MD files are read as UTF-8 text
- PDF text is extracted with `pypdf`
- empty extracted text returns a controlled extraction error
- unsupported extraction extensions are rejected

## Why This Matters
The first V7 chunk defines the API contract before implementation details.

This keeps the RAG build controlled:
- no parsing before upload contracts are clear
- no embeddings before chunk/source metadata is clear
- no answers without citation structure

## Planned API Surface

Upload document:
```http
POST /documents/upload
```

Current upload response:
```json
{
  "document_id": "doc_123",
  "filename": "policy.txt",
  "status": "uploaded"
}
```

Ask document:
```http
POST /documents/{document_id}/ask
```

## Example Future Response Shape
```json
{
  "answer": "The refund policy is described in the uploaded document.",
  "confidence": "high",
  "document_id": "doc_123",
  "sources": [
    {
      "filename": "policy.pdf",
      "page": 3,
      "chunk_id": "chunk_001",
      "similarity_score": 0.86
    }
  ],
  "status": "success"
}
```

## Deferred On Purpose
Not built in this first V7 chunk:
- chunking
- embeddings
- vector store
- retrieval
- grounded answer generation

## Testing Status
Added schema unit tests for:
- upload response contract
- blank question validation
- citation similarity score validation
- document answer response contract

Added upload endpoint integration tests for:
- successful TXT upload
- unsupported type rejection
- empty document rejection
- database failure handling

Added text extraction unit tests for:
- TXT extraction
- Markdown extraction
- PDF extraction path
- empty extracted text handling
- missing file handling
- unsupported extraction extension handling

Latest suite:
```text
166 passed
```

## Interview Explanation
In V7, I started the RAG layer by defining document Q&A contracts, adding the document upload lifecycle, and introducing text extraction. The backend can now accept supported document files, validate them safely, persist raw files, store metadata, return a stable `document_id`, and extract text from TXT, Markdown, and PDF files. Chunking, embeddings, retrieval, and grounded answers are intentionally deferred to later V7 chunks.
