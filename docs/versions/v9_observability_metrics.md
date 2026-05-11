# V9 - Observability + Metrics

## Version Goal
V9 adds the observability layer for InsightAgent.

The target flow is:
- trace each API request with a request id
- carry useful context through agent and tool flows
- log endpoint, status, latency, session id, tool usage, token/cost metadata where available
- categorize errors
- summarize runtime logs into metrics
- document the request lifecycle and observability proof

## Current Progress

Status: started.

V9 now has the version boundary, documentation scaffold, enriched request completion logs, agent tool trace logs, and a metrics summary script foundation. Runtime tracing will continue in small follow-up chunks.

## Planned Scope

From the V9 checklist, the version should cover:
- request tracing across API -> agent -> tool
- request id logging everywhere practical
- endpoint and status tracking
- session id tracking where available
- tool used and tool status tracking
- latency tracking
- token/cost tracking where available
- tool usage frequency and success/failure tracking
- error categorization
- metrics summary script
- log format documentation
- request lifecycle trace example
- README observability section

## Initial Version Boundary

Updated:
- app version default to `v9`
- `.env.example` to `APP_VERSION=v9`
- health endpoint test expectation to `v9`
- README current version and V9 docs link

## Request Completion Logs

Every request already has a request id from the V6 middleware. V9 extends the completion log with fields that are useful for observability and metrics.

Current completion log shape:

```json
{
  "event": "request_completed",
  "request_id": "req_123",
  "session_id": "session-123",
  "method": "GET",
  "endpoint": "/health",
  "path": "/health",
  "status_code": 200,
  "status": "success",
  "error_category": null,
  "latency_ms": 12.34
}
```

For failed requests, `status` becomes `failed` and `error_category` is populated from status code.

Current categories:
- `AUTH_ERROR` for 401/403
- `VALIDATION_ERROR` for 422
- `RATE_LIMIT_ERROR` for 429
- `INTERNAL_ERROR` for 5xx
- `HTTP_ERROR` for other 4xx responses

Session id is optional and is read from:
- `x-session-id` header
- `session_id` query parameter

## Agent Tool Trace Logs

Agent queries now emit a dedicated tool trace log after the agent controller returns.

Current agent tool log shape:

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

This creates the first API -> agent -> tool trace signal and gives the later metrics summary script a stable event for tool usage frequency and tool success/failure reporting.

## Metrics Summary Script

`scripts/metrics_summary.py` turns structured log lines into a small JSON metrics report.

It accepts:
- plain JSON log lines
- prefixed runtime log lines where the JSON payload appears after timestamp/logger text

Example command:

```powershell
.\.venv\Scripts\python scripts\metrics_summary.py --logs logs\app.log
```

Optional output file:

```powershell
.\.venv\Scripts\python scripts\metrics_summary.py --logs logs\app.log --output logs\metrics_summary.json
```

Current summary shape:

```json
{
  "requests": {
    "total": 3,
    "successful": 2,
    "failed": 1,
    "success_rate": 0.6667,
    "average_latency_ms": 20.0,
    "endpoint_counts": {
      "/agent/query": 2,
      "/health": 1
    },
    "error_categories": {
      "AUTH_ERROR": 1
    }
  },
  "agent_tools": {
    "total": 3,
    "successful": 2,
    "failed": 1,
    "success_rate": 0.6667,
    "tool_usage": {
      "calculator": 2,
      "date_time": 1
    },
    "tool_status_counts": {
      "failed": 1,
      "success": 2
    }
  }
}
```

This gives V9 a first reusable way to prove:
- request success/failure rate
- endpoint activity
- average latency
- visible error categories
- tool usage frequency
- tool success/failure counts

## Deferred To Follow-Up Chunks

Not implemented in this scaffold chunk:
- observability README proof
- request lifecycle trace examples
- token/cost runtime logging

## Testing Status

The scaffold will be verified through:
- focused health endpoint test
- full test suite
- focused request ID middleware tests
- focused agent endpoint trace tests
- focused metrics summary tests

## Interview Explanation
In V9, I started the observability layer by creating the version boundary, documentation scaffold, enriched request completion logs, agent tool trace logs, and a metrics summary script. This prepares the project to explain runtime behavior through request status, endpoint activity, latency, error categories, and tool usage metrics without mixing observability work into the completed V8 evaluation layer.
