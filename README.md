# InsightAgent

InsightAgent is a learning-first, production-style FastAPI backend for AI-powered data and document analysis.

## Current Version
**V9 - Observability + Metrics**

Cloud Run deployment is intentionally deferred until the local/containerized backend is fully closed out and ready for an external runtime.

Version notes:
- [V1 – FastAPI Basic Chat](docs/versions/v1_fastapi_basic_chat.md)
- [V2 – Structured Output](docs/versions/v2_structured_output.md)
- [V3 – Tool Calling / Agentic Layer](docs/versions/v3_tool_calling_agentic.md)
- [V4 – Memory and Context](docs/versions/v4_memory_context.md)
- [V5 – Data Analysis Assistant](docs/versions/v5_data_analysis_assistant.md)
- [V6 – Backend Maturity](docs/versions/v6_backend_maturity.md)
- [V7 – Document Q&A](docs/versions/v7_document_qa.md)
- [V8 - Evaluation Layer](docs/versions/v8_evaluation_layer.md)
- [V9 - Observability + Metrics](docs/versions/v9_observability_metrics.md)

## Project Structure
```text
app/                  # Core FastAPI application
  api/                # Route handlers, middleware, auth, CORS, rate limiting
  db/                 # SQLite setup and schema definitions
  prompts/            # Versioned prompt templates for structured and agent flows
  schemas/            # Pydantic request/response contracts
  services/           # Business logic for LLM, memory, datasets, and documents
  tools/              # Allowlisted backend tools used by the agent layer
  utils/              # Shared utilities such as logging
  main.py             # FastAPI app entrypoint
  config.py           # Environment-driven configuration

tests/                # Unit and integration test suites

docs/                 # Project report and version-wise build notes
evals/                # Evaluation datasets and generated result files
scripts/              # Utility scripts such as eval runner

requirements.txt      # Python dependencies
Dockerfile            # Container runtime definition
```

## Run Locally
Install dependencies:

```bash
pip install -r requirements.txt
```

Start the API:

```bash
uvicorn app.main:app --reload
```

## Run With Docker
Build the image:

```powershell
docker build -t insightagent:v9 .
```

Run the container:

```powershell
docker run --rm -p 8000:8000 `
  -e API_KEY=your-service-api-key-here `
  -e LLM_API_KEY=your-llm-api-key-here `
  insightagent:v9
```

Important production environment variables:

```text
APP_ENV=production
APP_VERSION=v9
DOCS_ENABLED=false
API_KEY=<service-api-key>
LLM_API_KEY=<provider-api-key>
CORS_ALLOWED_ORIGINS=<deployed-frontend-origin>
RATE_LIMIT_ENABLED=true
```

For production deployments, keep `DOCS_ENABLED=false` unless API docs are intentionally exposed.

Check health:

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "ok",
  "service": "InsightAgent",
  "version": "v9"
}
```

Check readiness:

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/ready" `
  -Method Get
```

Protected endpoints require an API key:

```powershell
$headers = @{ "x-api-key" = "your-service-api-key-here" }
```

Send a chat request:

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/chat" `
  -Method Post `
  -Headers $headers `
  -ContentType "application/json" `
  -Body '{"message":"Explain what a CSV file is in one sentence."}'
```

Send a structured chat request:

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/chat/structured" `
  -Method Post `
  -Headers $headers `
  -ContentType "application/json" `
  -Body '{"message":"Explain missing values in a dataset in simple words."}'
```

Send an agent query request:

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/agent/query" `
  -Method Post `
  -Headers $headers `
  -ContentType "application/json" `
  -Body '{"message":"What is 25 * 18?"}'
```

Send a memory chat request:

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/chat/memory" `
  -Method Post `
  -Headers $headers `
  -ContentType "application/json" `
  -Body '{"message":"Hello, this is my first memory message."}'
```

Create a session explicitly:

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/sessions" `
  -Method Post `
  -Headers $headers
```

Get session message history:

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/sessions/<session_id>/messages" `
  -Method Get `
  -Headers $headers
```

Upload a CSV dataset:

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/datasets/upload" `
  -Method Post `
  -Headers $headers `
  -Form @{ file = Get-Item ".\sample.csv" }
```

Get dataset summary:

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/datasets/<dataset_id>/summary" `
  -Method Get `
  -Headers $headers
```

Ask a dataset question:

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/datasets/<dataset_id>/ask" `
  -Method Post `
  -Headers $headers `
  -ContentType "application/json" `
  -Body '{"question":"Which column has the most missing values?"}'
```

Upload a document:

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/documents/upload" `
  -Method Post `
  -Headers $headers `
  -Form @{ file = Get-Item ".\policy.txt" }
```

Ask a document question:

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/documents/<document_id>/ask" `
  -Method Post `
  -Headers $headers `
  -ContentType "application/json" `
  -Body '{"question":"What is the refund policy?"}'
```

## Observability
V9 adds structured runtime logs and a metrics summary workflow.

Every request receives an `x-request-id` response header. If the client provides `x-request-id`, the API reuses it; otherwise the middleware generates one.

Request completion logs use this JSON payload shape:

```json
{
  "event": "request_completed",
  "request_id": "req_123",
  "session_id": "session-123",
  "method": "POST",
  "endpoint": "/agent/query",
  "path": "/agent/query",
  "status_code": 200,
  "status": "success",
  "error_category": null,
  "latency_ms": 12.34,
  "input_tokens": null,
  "output_tokens": null,
  "total_tokens": null,
  "estimated_cost_usd": null
}
```

Agent requests also emit tool trace logs:

```json
{
  "event": "agent_tool_completed",
  "request_id": "req_123",
  "tool_used": "calculator",
  "tool_status": "success",
  "agent_status": "success",
  "tool_output_summary": "450"
}
```

The same request id connects the API request log and the agent tool log.

Example lifecycle:

```text
Client POST /agent/query with x-request-id=req_demo_001
API returns x-request-id=req_demo_001
Log event 1: request_completed for /agent/query
Log event 2: agent_tool_completed for calculator
Metrics script summarizes request success rate, endpoint counts, latency, error categories, tool usage, and tool status.
```

Summarize logs:

```powershell
.\.venv\Scripts\python scripts\metrics_summary.py `
  --logs logs\app.log `
  --output logs\metrics_summary.json
```

The output includes:
- request totals and success/failure rate
- average request latency
- endpoint counts
- error category counts
- tool usage counts
- tool success/failure counts
- token/cost totals when log events expose them

## Run Evaluations
Start the API locally, then run the V8 evaluation dataset:

```powershell
.\.venv\Scripts\python scripts\run_eval.py `
  --base-url "http://127.0.0.1:8000" `
  --api-key "your-service-api-key-here"
```

The runner loads `evals/evaluation_dataset.jsonl`, calls the configured API cases, captures latency, scores each response, and writes results under `evals/results/`.

Current V8 coverage:
- chat and structured chat response shape
- tool calling correctness
- CSV analysis intent and answer relevance
- RAG citation presence, citation accuracy, groundedness, and insufficient-context safety
- negative cases for missing citations and unsupported confident answers

The saved result file includes:
- `summary.total`
- `summary.passed`
- `summary.failed`
- `summary.pass_rate`
- `summary.failure_categories`
- `summary.usage` with available/unavailable usage counts and token/cost totals when present
- per-case HTTP status, latency, pass/fail result, score breakdown, failure categories, request trace metadata, optional usage metadata, and response body

Each eval case sends a stable `x-request-id` such as `eval_rag_refund_policy_main`. Saved results include a `trace` block so eval failures can be connected back to runtime request logs:

```json
{
  "trace": {
    "request_id": "eval_rag_refund_policy_main",
    "response_request_id": "eval_rag_refund_policy_main",
    "setup_request_ids": {
      "upload_document": "eval_rag_refund_policy_setup_document"
    }
  }
}
```

`evals/results/` is ignored by Git so local evaluation runs do not create commit noise.

Compare against a previous run:

```powershell
.\.venv\Scripts\python scripts\run_eval.py `
  --base-url "http://127.0.0.1:8000" `
  --api-key "your-service-api-key-here" `
  --compare-to "evals/results/previous_eval_results.json"
```

Comparison output reports pass-rate delta, newly failing cases, newly passing cases, added cases, and removed cases.

Current automated verification:

```text
245 passed
```
