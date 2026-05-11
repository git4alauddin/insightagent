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

V9 now has the version boundary, documentation scaffold, and enriched request completion logs. Runtime tracing will continue in small follow-up chunks.

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

## Deferred To Follow-Up Chunks

Not implemented in this scaffold chunk:
- metrics summary script
- observability README proof
- request lifecycle trace examples

## Testing Status

The scaffold will be verified through:
- focused health endpoint test
- full test suite
- focused request ID middleware tests

## Interview Explanation
In V9, I started the observability layer by creating the version boundary and documentation scaffold. This prepares the project to add request-level tracing, structured runtime logs, tool and error metrics, token/cost visibility, and a metrics summary workflow without mixing observability work into the completed V8 evaluation layer.
