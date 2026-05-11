# V9 Technical Walkthrough

This document explains the V9 observability and metrics layer as it grows.

## 1. Design Intent

V9 turns InsightAgent from measurable in evals into traceable at runtime.

The observability layer should answer:
- which request failed?
- which endpoint handled it?
- which session was involved?
- which tool was selected?
- did the tool succeed or fail?
- how long did the request take?
- were token/cost numbers available?
- what error category explains the failure?

## 2. Version Alignment

### `app/config.py`
Updated:
- `app_version = "v9"`

### `.env.example`
Updated:
- `APP_VERSION=v9`

### `tests/integration/test_health.py`
Updated expected health version to `v9`.

### `README.md`
Updated:
- current version label
- Docker image examples
- expected health version
- V9 documentation link

## 3. Request Completion Log

### `app/api/middleware.py`
V9 extends the existing request id middleware.

Current fields:
- `event`
- `request_id`
- `session_id`
- `method`
- `endpoint`
- `path`
- `status_code`
- `status`
- `error_category`
- `latency_ms`

Status mapping:
- `success` for status codes below 400
- `failed` for status codes 400 and above

Error category mapping:
- 401/403 -> `AUTH_ERROR`
- 422 -> `VALIDATION_ERROR`
- 429 -> `RATE_LIMIT_ERROR`
- 5xx -> `INTERNAL_ERROR`
- other 4xx -> `HTTP_ERROR`

Session id is optional and currently resolved from:
- `x-session-id`
- `session_id` query parameter

## 4. Planned Observability Model

The target trace shape is:

```json
{
  "request_id": "req_123",
  "session_id": "sess_456",
  "endpoint": "/agent/query",
  "status": "success",
  "latency_ms": 123.45,
  "tool_used": "calculator",
  "tool_status": "success",
  "input_tokens": null,
  "output_tokens": null,
  "total_tokens": null,
  "estimated_cost_usd": null,
  "error_category": null
}
```

## 5. Checklist Mapping

Started:
- V9 version boundary
- V9 documentation files
- README version alignment
- request completion log enrichment
- request id logging
- endpoint/status tracking
- latency tracking
- basic error categorization
- optional session id tracking

Pending:
- request tracing across API -> agent -> tool
- tool tracking
- token/cost tracking in runtime logs
- tool usage summary
- metrics summary script
- log format documentation
- request lifecycle trace example
- observability section in README

## 6. Tests Added

### `tests/integration/test_request_id_middleware.py`
Verifies:
- request id generation
- incoming request id reuse
- request id propagation to error responses
- successful request completion logs include trace fields
- failed request completion logs include status and error category

## 7. Interview Summary
I started V9 by creating the observability version boundary and documentation scaffold, then enriched request completion logs. The API now logs request id, optional session id, method, endpoint, status code, success/failure status, basic error category, and latency for each request. This creates the runtime trace foundation needed for later tool metrics, log summaries, and request lifecycle examples.
