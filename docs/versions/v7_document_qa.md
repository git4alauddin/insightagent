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
- document upload route
- file persistence
- PDF/TXT/MD parsing
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

## Interview Explanation
In V7, I started the RAG layer by defining document Q&A contracts first. I added schemas for document uploads, document questions, source citations, and grounded answers. This gives the backend a clear response shape with citations before implementing parsing, embeddings, retrieval, and answer generation.
