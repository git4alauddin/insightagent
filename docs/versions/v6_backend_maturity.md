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

## Why This Matters
V6 protects costly and state-changing endpoints while keeping health/readiness checks available for uptime checks and deployment platforms.

The backend now fails closed when API key auth is not configured, which is safer than accidentally exposing private endpoints.

## Testing Status
Latest suite after API key auth:

```text
133 passed
```

## Current V6 Checklist Status
- Dockerfile: done.
- `.dockerignore`: done.
- `/ready` endpoint: done.
- Readiness checks for LLM, database, and storage: done.
- API key authentication: done.
- Protected private endpoints: done.
- Public `/health` and `/ready`: done.
- Global exception handler: pending.
- Request ID middleware: pending.
- Structured logging upgrade: pending.
- Rate limiting: pending.
- CORS config: pending.
- Cloud Run deployment: pending.

## Interview Explanation
In V6, I started hardening InsightAgent for deployment. I added a readiness endpoint for dependency checks, containerized the backend with Docker, and added API key authentication for private endpoints. Public health checks remain open, while LLM, agent, session, and dataset routes require a valid `x-api-key` header.
