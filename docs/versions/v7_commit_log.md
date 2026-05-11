# V7 Commit Log

This file maps each V7 commit heading to:
- what we implemented
- what was solved/taken care of

## Commit-by-Commit (V7)

### `ec8fb6f` - `v7: add document upload contracts and validation plan`
**What we did**
- Added document configuration values.
- Added document upload and ask schemas.
- Added source citation schema.
- Added document schema tests.
- Added the V7 three-document structure.

**What it solved / took care of**
- Established the RAG API contract before implementation.
- Made citations and weak-context response shape explicit early.

### `363b8f2` - `v7: add document upload endpoint and safe persistence`
**What we did**
- Added `documents` metadata table.
- Added document registry service.
- Added document validation/upload service.
- Added `POST /documents/upload`.
- Added document upload integration tests.
- Updated V7 docs and README examples.

**What it solved / took care of**
- Created the document lifecycle entrypoint.
- Persisted raw uploaded files safely with generated document IDs.
- Stored document metadata for later parsing/chunking/retrieval.

### `1bdfdeb` - `v7: add text extraction for uploaded documents`
**What we did**
- Added `pypdf` dependency.
- Added document text extraction service.
- Supported TXT, Markdown, and PDF extraction paths.
- Added controlled errors for missing, unreadable, empty, and unsupported extraction cases.
- Added document text extraction unit tests.

**What it solved / took care of**
- Converted stored document files into text for the future chunking pipeline.
- Added safe extraction failure behavior before retrieval/answer generation.

### `<pending>` - `v7: add document chunking service`
**What we did**
- Added chunk size and chunk overlap configuration.
- Added `DocumentChunk` schema with source metadata.
- Added text cleaning for whitespace normalization.
- Added deterministic overlapping chunk generation.
- Added chunking unit tests for metadata, overlap, empty text, and invalid config.

**What it solved / took care of**
- Converted extracted text into retrievable chunk units.
- Preserved document/source metadata needed for later citations.
- Added guardrails so invalid chunk settings fail before indexing.

## Reusable Entry Template

### `<commit_hash>` - `<commit_heading>`
**What we did**
- ...

**What it solved / took care of**
- ...
