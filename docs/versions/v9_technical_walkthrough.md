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

## 5. Agent Tool Trace

### `app/api/routes_agent.py`
V9 adds a structured agent tool trace after successful agent controller execution.

Current fields:
- `event`
- `request_id`
- `tool_used`
- `tool_status`
- `agent_status`
- `tool_output_summary`

Current event:

```json
{
  "event": "agent_tool_completed",
  "request_id": "agent-log-request-123",
  "tool_used": "calculator",
  "tool_status": "success",
  "agent_status": "success",
  "tool_output_summary": "450"
}
```

This is intentionally route-level for now because the route has access to the request id and the validated response object.

## 6. Metrics Summary Script

### `scripts/metrics_summary.py`
V9 adds a small log summarizer for structured JSON logs.

Core functions:
- `extract_json_payload(line)` reads plain JSON log lines and prefixed runtime log lines.
- `load_log_events(log_path)` loads valid JSON event payloads and skips non-JSON noise.
- `build_metrics_summary(events)` splits request logs and agent tool logs into separate summaries.
- `save_summary(summary, output_path)` writes a reusable JSON report.

Request metrics currently include:
- total requests
- successful requests
- failed requests
- success rate
- average latency
- endpoint counts
- error category counts

Agent tool metrics currently include:
- total tool events
- successful tool events
- failed tool events
- success rate
- tool usage counts
- tool status counts

CLI example:

```powershell
.\.venv\Scripts\python scripts\metrics_summary.py --logs logs\app.log --output logs\metrics_summary.json
```

## 7. Checklist Mapping

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
- API -> agent -> tool tracing
- tool used tracking
- tool status tracking
- metrics summary script
- tool usage summary
- tool success/failure summary
- error categories visible in summaries

Pending:
- deeper service-level tool execution tracing
- token/cost tracking in runtime logs
- log format documentation
- request lifecycle trace example
- observability section in README

## 8. Tests Added

### `tests/integration/test_request_id_middleware.py`
Verifies:
- request id generation
- incoming request id reuse
- request id propagation to error responses
- successful request completion logs include trace fields
- failed request completion logs include status and error category

### `tests/integration/test_agent_endpoint.py`
Verifies:
- agent query success response
- controlled agent errors
- agent tool trace log includes request id, tool used, tool status, agent status, and output summary

### `tests/unit/test_metrics_summary.py`
Verifies:
- JSON payload extraction from plain and prefixed log lines
- invalid log lines are skipped
- missing log files return controlled errors
- request metrics are summarized
- agent tool metrics are summarized
- summary JSON can be written to disk

## 9. Interview Summary
I started V9 by creating the observability version boundary and documentation scaffold, then enriched request completion logs, agent tool trace logs, and a metrics summary script. The API now logs request id, optional session id, method, endpoint, status code, success/failure status, basic error category, and latency for each request. Agent queries also emit tool trace logs with tool used, tool status, agent status, and output summary. The metrics script parses those logs and summarizes request volume, success/failure rate, average latency, endpoint activity, error categories, tool usage, and tool success/failure counts.
