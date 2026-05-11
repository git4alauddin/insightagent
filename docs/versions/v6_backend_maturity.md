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

## Why This Matters
V6 protects costly and state-changing endpoints while keeping health/readiness checks available for uptime checks and deployment platforms.

The backend now fails closed when API key auth is not configured, which is safer than accidentally exposing private endpoints.

Global exception handling gives clients one consistent error format and prevents raw internal errors from leaking through API responses.

Request IDs make each API call traceable across responses, logs, and later observability work.

## Testing Status
Latest suite after request ID middleware:

```text
138 passed
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
- Structured logging upgrade: pending.
- Rate limiting: pending.
- CORS config: pending.
- Cloud Run deployment: pending.

## Interview Explanation
In V6, I started hardening InsightAgent for deployment. I added a readiness endpoint for dependency checks, containerized the backend with Docker, protected private endpoints with API key authentication, centralized API error handling, and added request IDs for traceability. Public health checks remain open, while private routes require a valid `x-api-key` header and errors return a consistent structured response with a request ID.
