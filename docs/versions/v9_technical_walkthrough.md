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

## 3. Planned Observability Model

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

## 4. Checklist Mapping

Started:
- V9 version boundary
- V9 documentation files
- README version alignment

Pending:
- request tracing across API -> agent -> tool
- request id logging everywhere practical
- endpoint/status/session/tool tracking
- token/cost tracking in runtime logs
- tool usage summary
- error categorization
- metrics summary script
- log format documentation
- request lifecycle trace example
- observability section in README

## 5. Interview Summary
I started V9 by creating the observability version boundary and documentation scaffold. The goal of V9 is to make each request traceable and debuggable across the API, agent, and tool layers, then summarize logs into useful metrics for latency, tools, errors, and cost.
