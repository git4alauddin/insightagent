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

V9 now has the version boundary, documentation scaffold, enriched request completion logs, agent tool trace logs, metrics summary script foundation, log format documentation, request lifecycle example, README observability proof, and eval-to-request trace linking. Runtime tracing will continue in small follow-up chunks.

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

## Log Format Documentation

InsightAgent emits structured JSON payloads inside Python log records. The metrics summary script supports both:
- plain JSON lines
- standard prefixed log lines that contain a JSON payload

Core event names:
- `request_completed`
- `agent_tool_completed`

Request log fields:
- `event`: always `request_completed`
- `request_id`: request trace id returned in `x-request-id`
- `session_id`: optional session id from `x-session-id` or query parameter
- `method`: HTTP method
- `endpoint`: request URL path used for metrics grouping
- `path`: same path retained for compatibility with earlier request logs
- `status_code`: HTTP status code
- `status`: `success` or `failed`
- `error_category`: categorized failure reason, or `null`
- `latency_ms`: request duration in milliseconds

Agent tool log fields:
- `event`: always `agent_tool_completed`
- `request_id`: same request id as the API request
- `tool_used`: selected agent tool
- `tool_status`: tool execution status
- `agent_status`: overall agent response status
- `tool_output_summary`: short tool result summary

## Request Lifecycle Trace Example

Example request:

```text
POST /agent/query
x-request-id: req_demo_001
```

Example API response includes:

```text
x-request-id: req_demo_001
```

Example request completion log:

```json
{
  "event": "request_completed",
  "request_id": "req_demo_001",
  "session_id": null,
  "method": "POST",
  "endpoint": "/agent/query",
  "path": "/agent/query",
  "status_code": 200,
  "status": "success",
  "error_category": null,
  "latency_ms": 18.5
}
```

Example agent tool log:

```json
{
  "event": "agent_tool_completed",
  "request_id": "req_demo_001",
  "tool_used": "calculator",
  "tool_status": "success",
  "agent_status": "success",
  "tool_output_summary": "450"
}
```

Debugging path:
- use `request_id` to find all events for one API call
- use `endpoint`, `status`, and `error_category` to understand request failure
- use `tool_used` and `tool_status` to understand agent execution
- use `latency_ms` to identify slow requests
- run `scripts/metrics_summary.py` to summarize repeated behavior over many requests

## Evaluation Result Trace Linking

The V8 eval runner now contributes to V9 observability by sending stable request ids and storing them in saved results.

Primary eval request id format:

```text
eval_<case_id>_main
```

Setup request id formats:

```text
eval_<case_id>_setup_dataset
eval_<case_id>_setup_document
```

Saved per-case result trace shape:

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

This links evaluation failures to runtime logs:
- find the failed case id in the eval result file
- copy `trace.request_id`
- search runtime logs for the matching `request_id`
- inspect `request_completed`, `agent_tool_completed`, and error category fields for that request

## Deferred To Follow-Up Chunks

Not implemented in this scaffold chunk:
- token/cost runtime logging
- deeper service-level token/cost fields where available

## Testing Status

The scaffold will be verified through:
- focused health endpoint test
- full test suite
- focused request ID middleware tests
- focused agent endpoint trace tests
- focused metrics summary tests
- focused eval runner trace tests
- README/docs review against V9 checklist

## Interview Explanation
In V9, I started the observability layer by creating the version boundary, documentation scaffold, enriched request completion logs, agent tool trace logs, a metrics summary script, README/docs observability proof, and eval-to-request trace linking. This prepares the project to explain runtime behavior through request status, endpoint activity, latency, error categories, request lifecycle traces, tool usage metrics, and failed-eval debugging without mixing observability work into the completed V8 evaluation layer.
