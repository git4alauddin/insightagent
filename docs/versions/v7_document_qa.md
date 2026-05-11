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

Status: complete.

V7 is implemented and verified through automated end-to-end tests. The upload flow now indexes documents immediately, and the ask endpoint can answer against indexed chunks with citations or return `insufficient_context` when evidence is weak.

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
- `DOCUMENT_CHUNK_SIZE`
- `DOCUMENT_CHUNK_OVERLAP`
- `DOCUMENT_EMBEDDING_DIMENSIONS`
- `DOCUMENT_RETRIEVAL_TOP_K`
- `DOCUMENT_SIMILARITY_THRESHOLD`

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
- extracts text
- chunks text
- generates local embeddings
- stores chunk vectors
- marks the document as indexed
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

### Document Chunking Service
Added chunking for extracted document text.

Behavior:
- normalizes whitespace before chunking
- splits text into deterministic overlapping chunks
- uses configurable chunk size and overlap values
- attaches chunk metadata: `chunk_id`, `document_id`, `filename`, `chunk_index`, and optional `page`
- rejects empty cleaned text and invalid chunk settings

### Local Embedding Service
Added deterministic local embedding generation.

Behavior:
- tokenizes chunk text
- hashes tokens into a fixed-size vector
- normalizes the vector for future similarity comparison
- rejects text without tokens
- rejects invalid embedding dimensions

This is intentionally local and deterministic for the portfolio build. It gives us a testable embedding pipeline before adding retrieval behavior.

### Local Vector Store
Added SQLite-backed chunk/vector persistence.

Stored fields:
- `chunk_id`
- `document_id`
- `filename`
- `chunk_index`
- `text`
- `page`
- `embedding_json`
- `created_at`

Behavior:
- saves indexed chunks for a document
- replaces an existing document index during re-indexing
- loads chunks in chunk order
- converts SQLite errors into controlled service errors

### Semantic Retrieval Service
Added semantic retrieval over indexed document chunks.

Behavior:
- embeds the user question
- loads stored chunks and embeddings for a document
- computes cosine similarity
- maps similarity scores into the `0.0` to `1.0` citation range
- filters chunks below `DOCUMENT_SIMILARITY_THRESHOLD`
- returns the top `DOCUMENT_RETRIEVAL_TOP_K` matches
- returns retrieval trace metadata: top-k, threshold, candidate count, chunks, and scores

### Grounded Answer Service
Added service-level grounded document answer generation.

Behavior:
- builds a grounded prompt from retrieved document chunks
- formats retrieved chunk metadata into the prompt context
- builds citations from retrieved chunks
- returns `insufficient_context` when retrieval finds no usable chunks
- returns an extractive answer using only retrieved chunk text
- converts retrieval errors into controlled answer-service errors

This answer behavior is now exposed through `POST /documents/{document_id}/ask`.

### Document Ask Endpoint
Added:
```http
POST /documents/{document_id}/ask
```

Behavior:
- validates the request with `DocumentAskRequest`
- confirms the document exists before answering
- calls the grounded document answer service
- returns `DocumentAskResponse`
- returns `DOCUMENT_NOT_FOUND` for unknown documents
- returns `DOCUMENT_ANSWER_ERROR` for controlled answer-service failures
- preserves weak-context fallback as a normal `200` response with `status="insufficient_context"`

### Automatic Indexing After Upload
Added automatic indexing inside the document upload flow.

Indexing flow:
1. Store raw uploaded file.
2. Register document metadata with `uploaded` status.
3. Extract text from the stored file.
4. Chunk cleaned text.
5. Generate chunk embeddings.
6. Save chunks and vectors.
7. Mark document status as `indexed`.
8. Return upload response with `status="indexed"`.

Controlled indexing failures return:
```json
{
  "error": {
    "code": "DOCUMENT_INDEXING_ERROR",
    "message": "No text could be extracted from the document."
  }
}
```

## Why This Matters
The early V7 chunks define the API contract, indexing foundation, and retrieval layer before answer generation.

This keeps the RAG build controlled:
- no parsing before upload contracts are clear
- no embeddings before chunk/source metadata is clear
- no answers without citation and retrieval evidence

## API Surface

Upload document:
```http
POST /documents/upload
```

Current upload response:
```json
{
  "document_id": "doc_123",
  "filename": "policy.txt",
  "status": "indexed"
}
```

Ask document:
```http
POST /documents/{document_id}/ask
```

Current ask response shape:
```json
{
  "answer": "Based on the retrieved document context: Refunds are available.",
  "confidence": "high",
  "document_id": "doc_123",
  "sources": [
    {
      "filename": "policy.txt",
      "chunk_id": "doc_123_chunk_0000",
      "similarity_score": 0.91,
      "page": 1
    }
  ],
  "status": "success"
}
```

## Citation Response Example
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

## Completion Notes
V7 is complete for the planned backend implementation. The full upload-to-ask RAG path is covered by automated integration tests.

Optional future proof outside this implementation chunk:
- run the same upload and ask flow manually through curl/Postman for demo recording

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

Added chunking unit tests for:
- whitespace cleaning
- single-chunk documents
- overlapping multi-chunk documents
- empty cleaned text handling
- invalid chunk size/overlap handling

Added local indexing unit tests for:
- deterministic embedding generation
- normalized embedding vectors
- chunk embedding generation
- vector store save/load
- document index replacement
- controlled vector store errors

Added semantic retrieval unit tests for:
- cosine similarity scoring
- `0.0` to `1.0` similarity score mapping
- ranked top-k retrieval
- similarity threshold filtering
- blank question handling
- invalid retrieval settings
- vector dimension validation

Added grounded answer unit tests for:
- citation building
- successful grounded answer response
- weak-context fallback
- extractive answer text
- grounded prompt content
- retrieval error conversion

Added document ask endpoint integration tests for:
- successful answer response with citations
- insufficient-context response when no chunks are indexed
- missing document handling
- controlled answer-service error handling

Added end-to-end RAG integration tests for:
- upload indexes document automatically
- uploaded document can be asked immediately
- answer includes citation source from indexed chunk
- indexing errors are controlled

Latest suite:
```text
207 passed
```

## Interview Explanation
In V7, I started the RAG layer by defining document Q&A contracts, adding the document upload lifecycle, introducing text extraction, adding deterministic text chunking, creating a local vector indexing foundation, adding semantic retrieval, building the grounded answer service, exposing the document ask endpoint, and wiring upload-time indexing. The backend can now accept supported document files, validate them safely, persist raw files, store metadata, return a stable indexed `document_id`, extract text from TXT, Markdown, and PDF files, split extracted text into overlapping chunks with citation-ready metadata, generate deterministic local embeddings, persist chunk vectors in SQLite, retrieve the most relevant chunks for a question, build citations, return weak-context fallback when evidence is missing, and expose the end-to-end flow through `POST /documents/{document_id}/ask`.
