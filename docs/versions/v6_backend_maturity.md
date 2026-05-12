# V6 - Backend Maturity and Deployment Hardening

## Version Goal
V6 moves InsightAgent from a local learning backend toward a deployable service.

The version focuses on:
- containerized runtime
- readiness checks
- API key authentication
- production-style error handling and request controls
- deployment preparation

## Final Outcome
V6 now provides a locally verified, container-ready backend with protected private endpoints, readiness checks, structured errors, request IDs, structured request logs, environment-aware CORS, and basic in-memory rate limiting.

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

Docker verification performed:
```powershell
docker build -t insightagent:v6-verify .
docker run -d --name insightagent-v6-verify -p 18000:8000 `
  -e API_KEY=test-api-key `
  -e LLM_API_KEY=test-llm-key `
  insightagent:v6-verify
```

Verified endpoints:
- `GET http://127.0.0.1:18000/health` -> `status: ok`
- `GET http://127.0.0.1:18000/ready` -> `status: ready`

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

### Basic Rate Limiting
Added in-memory rate limiting in `app/api/rate_limit.py`.

Config values:
- `RATE_LIMIT_ENABLED`
- `RATE_LIMIT_REQUESTS_PER_MINUTE`
- `RATE_LIMIT_UPLOADS_PER_MINUTE`
- `RATE_LIMIT_WINDOW_SECONDS`

Behavior:
- private endpoints are rate limited by API key
- `/datasets/upload` uses the stricter upload limit
- `/health` and `/ready` are not rate limited
- exceeded limits return `429 RATE_LIMIT_EXCEEDED`

This is intentionally simple for V6. A distributed store such as Redis would be a future production upgrade.

### Production Configuration Cleanup
The app version now defaults to `v6`.

Important environment variables for production-style runs:
- `APP_ENV=production`
- `APP_VERSION=v6`
- `DOCS_ENABLED=false`
- `API_KEY`
- `LLM_API_KEY`
- `CORS_ALLOWED_ORIGINS`
- `RATE_LIMIT_ENABLED=true`

### Docs Exposure Decision
FastAPI docs are controlled by `DOCS_ENABLED`.

Behavior:
- development default: `/docs`, `/redoc`, and `/openapi.json` are enabled
- production recommendation: set `DOCS_ENABLED=false`
- when disabled, docs/schema routes return the standard structured 404 response

## Why This Matters
V6 protects costly and state-changing endpoints while keeping health/readiness checks available for uptime checks and deployment platforms.

The backend now fails closed when API key auth is not configured, which is safer than accidentally exposing private endpoints.

Global exception handling gives clients one consistent error format and prevents raw internal errors from leaking through API responses.

Request IDs make each API call traceable across responses, logs, and later observability work.

Structured request logs make latency, status codes, and request paths visible without adding a full observability stack yet.

CORS config keeps browser access controlled and environment-aware.

Rate limiting reduces accidental loops and basic abuse risk on costly or state-changing endpoints.

## Testing Status
Latest automated test suite after docs exposure configuration:

```text
149 passed
```

Docker verification:
```text
image build: passed
container runtime: passed
/health: ok
/ready: ready
```

Version alignment:
```text
/health version: v6
```

## Current V6 Checklist Status
- Dockerfile: done.
- `.dockerignore`: done.
- Docker image build verified: done.
- Docker runtime verified: done.
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
- Rate limiting: done.
- `APP_VERSION=v6`: done.
- `/docs` exposure decision: done.
- Environment-controlled docs exposure: done.
- Production env documentation: done.
- Cloud Run deployment: deferred on purpose at V6 closeout, completed later in the dedicated Deployment pass.

## Deferred On Purpose
Cloud Run deployment was not completed in the local V6 closeout. It was completed later in the dedicated Deployment pass.

Reason:
- the backend is now container-ready and verified locally
- actual Cloud Run deployment requires cloud project configuration, Artifact Registry setup, service account/environment setup, and external endpoint verification
- this can be done as a separate deployment chunk without changing the local backend architecture

## Interview Explanation
In V6, I hardened InsightAgent for deployment-style use. I added readiness checks, aligned the app version to V6, containerized and verified the backend with Docker, protected private endpoints with API key authentication, centralized API error handling, added request IDs for traceability, introduced structured request logs, configured environment-aware CORS, added basic in-memory rate limiting, and made API docs exposure environment-controlled. Public health checks remain open, while private routes require a valid `x-api-key` header and errors return a consistent structured response with a request ID.
