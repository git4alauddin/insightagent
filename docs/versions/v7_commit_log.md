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

### `<pending>` - `v7: add document upload endpoint and safe persistence`
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

## Reusable Entry Template

### `<commit_hash>` - `<commit_heading>`
**What we did**
- ...

**What it solved / took care of**
- ...
