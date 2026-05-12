# InsightAgent

InsightAgent is a production-style FastAPI backend for AI-powered chat, tool use, CSV analysis, document Q&A, evaluation, and observability.

## Project Snapshot

InsightAgent demonstrates how an AI backend can move beyond a simple chat wrapper into a safer, testable application architecture. It includes structured LLM responses, controlled tool calling, session memory, safe dataset analysis, local RAG-style document Q&A with citations, an evaluation runner, request tracing, metrics summaries, Docker support, and portfolio-ready documentation.

**Current Version:** V10 - Portfolio Packaging

Cloud Run deployment is intentionally deferred until the local and containerized backend are fully closed out for an external runtime.

## What It Demonstrates

- FastAPI backend design with separated routes, schemas, services, tools, prompts, and persistence.
- Environment-driven configuration with no hardcoded secrets.
- LLM chat and structured JSON output with validation, retry, and fallback behavior.
- Backend-controlled agent tools for calculator, date/time, summarization, and file analysis.
- SQLite-backed session memory with bounded context retrieval.
- Safe CSV upload, metadata tracking, and allowlisted analysis operations.
- Document upload, extraction, chunking, local embeddings, semantic retrieval, citations, and weak-context fallback.
- Evaluation dataset and runner for chat, tools, CSV, and RAG flows.
- Request IDs, structured logs, agent tool traces, and metrics summary reporting.
- Docker-ready runtime and production-aware API configuration.

## Documentation Map

| Area | Link |
| --- | --- |
| Architecture overview | [docs/architecture.md](docs/architecture.md) |
| API examples | [docs/api_examples.md](docs/api_examples.md) |
| Trade-offs and limitations | [docs/tradeoffs.md](docs/tradeoffs.md) |
| Project report | [docs/project_report.md](docs/project_report.md) |
| V10 notes | [docs/versions/v10_portfolio_packaging.md](docs/versions/v10_portfolio_packaging.md) |

Version history:

- [V1 - FastAPI Basic Chat](docs/versions/v1_fastapi_basic_chat.md)
- [V2 - Structured Output](docs/versions/v2_structured_output.md)
- [V3 - Tool Calling / Agentic Layer](docs/versions/v3_tool_calling_agentic.md)
- [V4 - Memory and Context](docs/versions/v4_memory_context.md)
- [V5 - Data Analysis Assistant](docs/versions/v5_data_analysis_assistant.md)
- [V6 - Backend Maturity](docs/versions/v6_backend_maturity.md)
- [V7 - Document Q&A](docs/versions/v7_document_qa.md)
- [V8 - Evaluation Layer](docs/versions/v8_evaluation_layer.md)
- [V9 - Observability + Metrics](docs/versions/v9_observability_metrics.md)
- [V10 - Portfolio Packaging](docs/versions/v10_portfolio_packaging.md)

## Architecture

```text
Client
  -> FastAPI routes
  -> Pydantic schemas
  -> service layer
  -> LLM provider / tool registry / SQLite / local file storage
  -> structured response with request trace metadata
```

The backend is organized around explicit contracts and controlled execution. The LLM can propose structured output or tool decisions, but backend services validate responses, route only to allowlisted tools, enforce dataset/document guardrails, and return predictable API shapes.

For the deeper system walkthrough, see [docs/architecture.md](docs/architecture.md).

## Tech Stack

- Python
- FastAPI
- Pydantic
- SQLite
- pandas
- OpenAI-compatible LLM client flow through environment configuration
- pytest
- Docker

## Project Structure

```text
app/
  api/          # routes, dependencies, middleware, errors, CORS, rate limiting
  db/           # SQLite connection and schema setup
  prompts/      # versioned prompt builders
  schemas/      # Pydantic API contracts
  services/     # LLM, memory, CSV, document, eval support logic
  tools/        # allowlisted backend tools
  utils/        # logging helpers

docs/           # portfolio docs, project report, version notes
evals/          # evaluation dataset
scripts/        # evaluation and metrics utilities
tests/          # unit and integration tests
```

## Quick Start

Install dependencies:

```bash
pip install -r requirements.txt
```

Create local environment values from `.env.example`, then set at least:

```text
API_KEY=<service-api-key>
LLM_API_KEY=<provider-api-key>
APP_VERSION=v10
```

Start the API:

```bash
uvicorn app.main:app --reload
```

Check health:

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "ok",
  "service": "InsightAgent",
  "version": "v10"
}
```

Protected endpoints require an API key:

```powershell
$headers = @{ "x-api-key" = "your-service-api-key-here" }
```

## Docker

Build the image:

```powershell
docker build -t insightagent:v10 .
```

Run the container:

```powershell
docker run --rm -p 8000:8000 `
  -e API_KEY=your-service-api-key-here `
  -e LLM_API_KEY=your-llm-api-key-here `
  insightagent:v10
```

Production-oriented settings:

```text
APP_ENV=production
APP_VERSION=v10
DOCS_ENABLED=false
API_KEY=<service-api-key>
LLM_API_KEY=<provider-api-key>
CORS_ALLOWED_ORIGINS=<deployed-frontend-origin>
RATE_LIMIT_ENABLED=true
```

For production deployments, keep `DOCS_ENABLED=false` unless interactive API docs are intentionally exposed.

## Core API Surface

| Endpoint | Purpose | Auth |
| --- | --- | --- |
| `GET /health` | Public liveness check | No |
| `GET /ready` | Public dependency readiness check | No |
| `POST /chat` | Basic LLM chat | Yes |
| `POST /chat/structured` | Validated structured LLM response | Yes |
| `POST /agent/query` | Controlled tool-calling agent flow | Yes |
| `POST /sessions` | Create a memory session | Yes |
| `POST /chat/memory` | Memory-aware chat | Yes |
| `GET /sessions/{session_id}/messages` | Read session history | Yes |
| `POST /datasets/upload` | Upload CSV dataset | Yes |
| `GET /datasets/{dataset_id}/summary` | Dataset summary | Yes |
| `POST /datasets/{dataset_id}/ask` | Safe CSV analysis Q&A | Yes |
| `POST /documents/upload` | Upload document for Q&A | Yes |
| `POST /documents/{document_id}/ask` | Grounded document Q&A with citations | Yes |

Full request and response examples are in [docs/api_examples.md](docs/api_examples.md).

## Evaluation

Run the V8 evaluation dataset against a local API:

```powershell
.\.venv\Scripts\python scripts\run_eval.py `
  --base-url "http://127.0.0.1:8000" `
  --api-key "your-service-api-key-here"
```

The runner loads `evals/evaluation_dataset.jsonl`, executes configured API cases, scores responses, captures latency, records trace metadata, and writes local results under `evals/results/`.

Current evaluation coverage includes chat response shape, structured output, tool correctness, CSV analysis intent, RAG citation checks, groundedness checks, and insufficient-context safety.

## Observability

Every request receives an `x-request-id` response header. Request completion logs include endpoint, status code, success/failure status, optional session id, latency, error category, and nullable token/cost fields when available.

Agent requests also emit tool trace logs with request id, selected tool, tool status, agent status, and output summary.

Summarize structured logs:

```powershell
.\.venv\Scripts\python scripts\metrics_summary.py `
  --logs logs\app.log `
  --output logs\metrics_summary.json
```

The summary reports request totals, success/failure rate, endpoint counts, average latency, error categories, tool usage, tool success/failure counts, and usage totals when log events expose them.

## Verification

Current automated test status:

```text
247 passed
```

The test suite covers route contracts, services, schemas, tool behavior, dataset workflows, document Q&A, evaluation logic, error handling, auth, request middleware, observability, and metrics summaries.

## Trade-Offs

InsightAgent intentionally favors clear local architecture over external infrastructure complexity. SQLite, deterministic local embeddings, rule-based evaluation checks, and in-memory rate limiting keep the project easy to run, inspect, and test while still showing production-style boundaries.

Cloud deployment, managed vector databases, distributed rate limiting, model-assisted evaluation, richer file parsing, and frontend UX are documented as future improvements instead of hidden behind unfinished implementation.

See [docs/tradeoffs.md](docs/tradeoffs.md) for the full limitations and roadmap discussion.
