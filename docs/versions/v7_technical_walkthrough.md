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

These settings prepare upload validation for PDF, TXT, and Markdown files.

## 3. Data Contracts

### `app/schemas/document.py`
Main models:
- `DocumentUploadResponse`
- `DocumentAskRequest`
- `SourceCitation`
- `DocumentAskResponse`

Key behaviors:
- `DocumentAskRequest.question` trims and rejects blank input.
- `SourceCitation.similarity_score` must be between `0.0` and `1.0`.
- `SourceCitation.page` is optional but must be positive when present.
- `DocumentAskResponse.answer` must not be blank.

## 4. Tests Added

### `tests/unit/test_document_schemas.py`
Verifies:
- upload response status contract
- blank question rejection
- citation score validation
- answer response contract
- blank answer rejection

## 5. Checklist Mapping
- document upload endpoint: pending
- supported document extensions config: started
- citation schema: done
- document ask request/response contracts: done
- text extraction: pending
- chunking: pending
- embeddings: pending
- vector store: pending
- retrieval: pending
- grounded answer generation: pending

## 6. Interview Summary
I started V7 by defining the document Q&A contracts before implementing the RAG pipeline. The schemas make the expected upload response, question input, citation format, and grounded answer response explicit, which reduces ambiguity before adding parsing, chunking, embeddings, and retrieval.
