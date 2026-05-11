# V6 - Backend Maturity and Deployment Hardening

## Version Goal
V6 moves InsightAgent from a local learning backend toward a deployable service.

The version focuses on:
- containerized runtime
- readiness checks
- API key authentication
- production-style error handling and request controls
- deployment preparation

## Progress So Far

### Readiness Endpoint
Added `GET /ready` to check whether required dependencies are available before serving production traffic.

Current readiness checks:
- LLM config is present
- SQLite database is reachable
- upload storage path is available

### Docker Runtime
Added:
- `Dockerfile`
- `.dockerignore`

The container runs the FastAPI app through Uvicorn and prepares the upload directory.

### API Key Authentication
Added a shared auth dependency in `app/api/dependencies.py`.

Protected endpoint groups:
- `/chat`
- `/chat/structured`
- `/chat/memory`
- `/agent/query`
- `/sessions`
- `/datasets/*`

Public endpoint groups:
- `/health`
- `/ready`

Auth behavior:
- missing or invalid `x-api-key` -> `401 UNAUTHORIZED`
- missing server-side `API_KEY` config -> `503 API_KEY_NOT_CONFIGURED`

### Global Exception Handling
Added a central error handler registration path in `app/api/error_handlers.py`.

All API errors now use this response shape:
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message."
  }
}
```

Handled cases:
- controlled route errors keep their existing codes, such as `DATASET_NOT_FOUND` or `UNAUTHORIZED`
- request validation errors return `INVALID_INPUT`
- unexpected backend errors return `INTERNAL_ERROR`

Unexpected errors are logged but returned safely without exposing internal exception details.

### Request ID Middleware
Added request ID middleware in `app/api/middleware.py`.

Behavior:
- reuses an incoming `x-request-id` header when provided
- generates a new `req_<uuid>` value when missing
- adds `x-request-id` to every response header
- includes `request_id` in structured error responses

This prepares the backend for traceable logs and easier debugging.

### Structured Request Logging
The request middleware now logs one structured JSON record after each request.

Example fields:
```json
{
  "event": "request_completed",
  "request_id": "req_123",
  "method": "POST",
  "path": "/chat",
  "status_code": 200,
  "latency_ms": 42.5
}
```

This creates a simple request audit trail and prepares the project for V9 observability metrics.

### Environment-Aware CORS
Added CORS configuration in `app/api/cors.py`.

Config values:
- `APP_ENV`
- `CORS_ALLOWED_ORIGINS`

Behavior:
- allows configured frontend origins
- rejects unconfigured origins
- rejects wildcard `*` origins in production

This keeps local frontend development possible without leaving production CORS overly permissive.

## Why This Matters
V6 protects costly and state-changing endpoints while keeping health/readiness checks available for uptime checks and deployment platforms.

The backend now fails closed when API key auth is not configured, which is safer than accidentally exposing private endpoints.

Global exception handling gives clients one consistent error format and prevents raw internal errors from leaking through API responses.

Request IDs make each API call traceable across responses, logs, and later observability work.

Structured request logs make latency, status codes, and request paths visible without adding a full observability stack yet.

CORS config keeps browser access controlled and environment-aware.

## Testing Status
Latest suite after CORS configuration:

```text
142 passed
```

## Current V6 Checklist Status
- Dockerfile: done.
- `.dockerignore`: done.
- `/ready` endpoint: done.
- Readiness checks for LLM, database, and storage: done.
- API key authentication: done.
- Protected private endpoints: done.
- Public `/health` and `/ready`: done.
- Global exception handler: done.
- Structured error response: done.
- Request ID middleware: done.
- Structured logging upgrade: done.
- CORS config: done.
- Rate limiting: pending.
- Cloud Run deployment: pending.

## Interview Explanation
In V6, I started hardening InsightAgent for deployment. I added a readiness endpoint for dependency checks, containerized the backend with Docker, protected private endpoints with API key authentication, centralized API error handling, added request IDs for traceability, introduced structured request logs, and configured environment-aware CORS. Public health checks remain open, while private routes require a valid `x-api-key` header and errors return a consistent structured response with a request ID.
