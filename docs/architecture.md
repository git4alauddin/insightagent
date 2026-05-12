# InsightAgent Architecture

InsightAgent is a production-style FastAPI backend for AI-powered chat, tool calling, CSV analysis, document Q&A, evaluation, and observability.

## High-Level Flow

```text
Client / API user
  |
  v
FastAPI application
  |
  +-- API middleware
  |     +-- request id
  |     +-- structured request logging
  |     +-- CORS
  |     +-- rate limiting
  |
  +-- API routers
  |     +-- health / readiness
  |     +-- chat / structured chat
  |     +-- agent query
  |     +-- sessions and memory
  |     +-- CSV datasets
  |     +-- documents and RAG
  |
  +-- Service layer
  |     +-- LLM calls
  |     +-- agent controller
  |     +-- memory/session services
  |     +-- dataset analysis services
  |     +-- document indexing/retrieval services
  |
  +-- Persistence
  |     +-- SQLite metadata and message history
  |     +-- local upload storage
  |     +-- SQLite-backed local vector storage
  |
  v
Structured API responses + logs + eval results
```

## Main Components

| Area | Responsibility |
| --- | --- |
| `app/main.py` | Builds the FastAPI app, registers middleware, and includes routers. |
| `app/config.py` | Loads environment-driven configuration through Pydantic settings. |
| `app/api/` | Owns HTTP routes, auth dependency, CORS, rate limiting, error handling, and request logging. |
| `app/schemas/` | Defines stable Pydantic contracts for request and response bodies. |
| `app/services/` | Contains business logic for LLM calls, memory, CSV analysis, document indexing, retrieval, evaluation support, and readiness checks. |
| `app/tools/` | Holds allowlisted tools used by the agent controller. |
| `app/db/` | Initializes SQLite tables for sessions, messages, datasets, documents, and vectors. |
| `scripts/` | Contains operational scripts for evaluation and metrics summaries. |
| `tests/` | Contains unit and integration coverage for API behavior and internal services. |

## Request Lifecycle

```text
HTTP request
  -> request id middleware assigns/reuses x-request-id
  -> auth/rate limiting/CORS checks run where applicable
  -> router validates request body with Pydantic
  -> service layer performs controlled work
  -> response schema returns stable JSON
  -> middleware logs request_completed with latency/status/error category
```

Private endpoints require `x-api-key`. Public endpoints such as `/health` and `/ready` remain available for health checks.

## Agent Workflow

```text
POST /agent/query
  -> agent controller asks LLM for a tool decision
  -> tool decision is parsed and validated
  -> registry checks the selected tool is allowlisted
  -> tool input is validated
  -> backend executes the selected tool safely
  -> response includes answer and tool trace
  -> route logs agent_tool_completed
```

The agent can use:
- `calculator`
- `date_time`
- `text_summarizer`
- `file_analyzer`
- `none` path for direct answers

Tool execution is backend-controlled. The LLM does not execute arbitrary Python.

## CSV Analysis Workflow

```text
POST /datasets/upload
  -> validate file type, size, rows, columns, encoding, and empty content
  -> store file safely
  -> save dataset metadata

POST /datasets/{dataset_id}/ask
  -> detect analysis intent
  -> route to allowlisted pandas-backed analysis service
  -> validate columns and operation
  -> return answer plus analysis trace
```

Supported analysis paths include dataset summary, missing values, column statistics, value counts, and groupby aggregation.

## Document Q&A Workflow

```text
POST /documents/upload
  -> validate file
  -> persist raw document
  -> extract text from TXT/MD/PDF
  -> clean and chunk text
  -> generate deterministic local embeddings
  -> store chunk vectors

POST /documents/{document_id}/ask
  -> retrieve relevant chunks
  -> apply similarity threshold
  -> build grounded answer from retrieved context
  -> return answer with citations
```

Weak retrieval returns an insufficient-context response instead of a confident unsupported answer.

## Evaluation And Observability

Evaluation:
- `evals/evaluation_dataset.jsonl` stores evaluation cases.
- `scripts/run_eval.py` runs local/deployed API cases.
- Results include pass/fail, score breakdowns, latency, optional usage metadata, and request trace ids.

Observability:
- every request receives an `x-request-id`
- request logs include endpoint, status, latency, error category, optional session id, and nullable usage fields
- agent logs include tool used and tool status
- `scripts/metrics_summary.py` summarizes request, error, latency, tool, and usage metrics from logs

## Key Trade-Offs

- SQLite keeps local development simple; PostgreSQL would be a better production database.
- Local file storage is easy to inspect; cloud object storage would be better for multi-instance deployments.
- Deterministic local embeddings make tests reliable; production RAG may benefit from managed embedding APIs or vector databases.
- API key auth is simple and suitable for a backend demo; OAuth/JWT would be stronger for user-level access control.
- Rule-based evaluation is deterministic; LLM-as-judge could add semantic scoring later.
- Controlled tool execution is safer than arbitrary Python execution, but intentionally limits flexibility.
