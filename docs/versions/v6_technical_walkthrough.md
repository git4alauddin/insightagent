# V6 Technical Walkthrough

This document explains the V6 backend maturity layer file by file.

## 1. Design Intent
V6 makes InsightAgent safer to run as a service.

The current V6 work focuses on:
1. Readiness checks for deployment.
2. Docker runtime setup.
3. API key protection for private endpoints.
4. Consistent structured API errors.
5. Request IDs for traceability.
6. Structured request logging.
7. Environment-aware CORS.
8. Basic rate limiting.
9. Production configuration cleanup.
10. Environment-controlled docs exposure.

## 2. Configuration Cleanup

### `app/config.py`
V6 defaults:
- `app_version = "v6"`
- `app_env = "development"`
- `docs_enabled = True`
- CORS and rate limit settings are environment-driven.

### `.env.example`
Documents the deployable environment shape:
- app identity
- docs exposure
- CORS origins
- API key auth
- LLM configuration
- rate limit settings
- upload settings

### Local `.env`
The local ignored `.env` should set:
```text
APP_VERSION=v6
```

## 3. Docs Exposure

### `app/config.py`
Adds:
- `docs_enabled`

This maps to `DOCS_ENABLED`.

### `app/main.py`
`create_app()` controls FastAPI documentation routes:
```python
docs_url="/docs" if settings.docs_enabled else None
redoc_url="/redoc" if settings.docs_enabled else None
openapi_url="/openapi.json" if settings.docs_enabled else None
```

Development can keep docs enabled.

Production should usually set:
```text
DOCS_ENABLED=false
```

## 4. CORS Configuration

### `app/config.py`
Adds:
- `app_env`
- `cors_allowed_origins`
- `get_cors_allowed_origins()`

`get_cors_allowed_origins()` parses the comma-separated origin list and rejects `*` when `APP_ENV=production`.

### `app/api/cors.py`
Core function:
- `register_cors_middleware(app)`

This adds FastAPI/Starlette `CORSMiddleware` with:
- configured allowed origins
- `GET`, `POST`, and `OPTIONS` methods
- custom headers such as `x-api-key`

### `app/main.py`
Calls:
```python
register_cors_middleware(app)
```

This keeps browser-origin rules centralized during app startup.

## 5. Readiness Layer

### `app/api/routes_health.py`
Adds:
- `GET /health`
- `GET /ready`

`/health` confirms the app process is alive.

`/ready` calls the readiness service and returns `503` if dependencies are not ready.

### `app/services/readiness_service.py`
Core checks:
- `check_llm_config()`
- `check_database()`
- `check_storage()`

This keeps deployment dependency checks outside the route layer.

## 6. Docker Runtime Verification

### `Dockerfile`
The Docker image:
- starts from `python:3.13-slim`
- installs dependencies from `requirements.txt`
- copies the app package into `/app/app`
- creates `/app/uploads`
- exposes port `8000`
- starts Uvicorn with `app.main:app`

### `.dockerignore`
The Docker build excludes:
- Git metadata
- local virtualenv
- `.env`
- SQLite runtime database
- uploads
- cache folders
- tests and docs

### Verification
The image was built and run locally:
```powershell
docker build -t insightagent:v6-verify .
docker run -d --name insightagent-v6-verify -p 18000:8000 `
  -e API_KEY=test-api-key `
  -e LLM_API_KEY=test-llm-key `
  insightagent:v6-verify
```

Verified:
- `/health` returned `status: ok`
- `/ready` returned `status: ready`

## 7. API Key Authentication

### `app/config.py`
Adds:
- `api_key`

The value comes from the `API_KEY` environment variable.

### `app/api/dependencies.py`
Core function:
- `require_api_key(...)`

Behavior:
- reads the `x-api-key` header
- compares it with `settings.api_key`
- returns `401 UNAUTHORIZED` for missing/wrong keys
- returns `503 API_KEY_NOT_CONFIGURED` if the backend was deployed without an API key

The comparison uses `secrets.compare_digest`.

### Protected Routers
Router-level dependency protection was added to:
- `app/api/routes_chat.py`
- `app/api/routes_agent.py`
- `app/api/routes_session.py`
- `app/api/routes_datasets.py`

Public routes remain in:
- `app/api/routes_health.py`

## 8. Rate Limiting

### `app/config.py`
Adds:
- `rate_limit_enabled`
- `rate_limit_requests_per_minute`
- `rate_limit_uploads_per_minute`
- `rate_limit_window_seconds`

### `app/api/rate_limit.py`
Core function:
- `enforce_rate_limit(...)`

Behavior:
- tracks requests in memory
- uses the API key as the main rate-limit identity
- applies a general request limit to private endpoints
- applies a stricter upload limit to `/datasets/upload`
- returns `429 RATE_LIMIT_EXCEEDED` when the limit is crossed

Supporting function:
- `reset_rate_limit_store()`

This exists so tests can clear the in-memory limiter state.

### Protected Routers
Rate limiting is attached alongside API key auth to:
- `app/api/routes_chat.py`
- `app/api/routes_agent.py`
- `app/api/routes_session.py`
- `app/api/routes_datasets.py`

Public health routes are not rate limited.

## 9. Global Error Handling

### `app/api/error_handlers.py`
Core functions:
- `register_exception_handlers(app)`
- `http_exception_handler(...)`
- `validation_exception_handler(...)`
- `unexpected_exception_handler(...)`

Response shape:
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message."
  }
}
```

Behavior:
- controlled `HTTPException` responses keep their custom route error codes
- request body/path validation failures return `INVALID_INPUT`
- unexpected crashes return `INTERNAL_ERROR`
- structured errors include `request_id`
- unexpected errors are logged server-side

### `app/main.py`
Calls:
```python
register_exception_handlers(app)
```

This attaches the handlers once during app startup.

## 10. Request ID Middleware

### `app/api/middleware.py`
Core function:
- `register_request_id_middleware(app)`

Behavior:
- reads incoming `x-request-id`
- generates `req_<uuid>` when no request ID is provided
- stores the value on `request.state.request_id`
- writes the same value back to the `x-request-id` response header
- logs one structured JSON request record after the response is created

### `app/api/error_handlers.py`
The error handlers read `request.state.request_id` and include it in the response body:
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message.",
    "request_id": "req_..."
  }
}
```

This gives clients a stable ID they can share when debugging a failed request.

### Structured Request Log
The middleware emits a JSON log message like:
```json
{
  "event": "request_completed",
  "request_id": "req_...",
  "method": "GET",
  "path": "/health",
  "status_code": 200,
  "latency_ms": 1.23
}
```

This is intentionally simple for V6. V9 can expand this into tool usage, token usage, cost, and richer metrics.

### `app/main.py`
Calls:
```python
register_request_id_middleware(app)
```

## 11. Tests Added/Extended

### Docs Exposure Tests
`tests/integration/test_docs_exposure.py` verifies:
- docs are enabled by default
- OpenAPI schema is enabled by default
- docs can be disabled
- OpenAPI schema can be disabled

### CORS Tests
`tests/integration/test_cors_config.py` verifies:
- configured origins are allowed
- unconfigured origins are rejected
- wildcard origins are rejected in production

### Auth Tests
`tests/integration/test_auth_dependency.py` verifies:
- `/health` is public
- `/ready` is public
- protected endpoints reject missing API keys
- protected endpoints reject invalid API keys
- missing configured `API_KEY` fails closed

### Rate Limit Tests
`tests/integration/test_rate_limit.py` verifies:
- too many private requests return `RATE_LIMIT_EXCEEDED`
- upload endpoints use a stricter limit
- `/health` is not rate limited

### Error Handler Tests
`tests/integration/test_error_handlers.py` verifies:
- validation errors return `INVALID_INPUT`
- unexpected exceptions return safe `INTERNAL_ERROR`

### Request ID Tests
`tests/integration/test_request_id_middleware.py` verifies:
- request IDs are generated when missing
- incoming request IDs are reused
- error responses include the same request ID in headers and body
- request logs include trace fields

### Existing Integration Tests
Existing tests were updated to expect the new V6 error shape:
```json
{
  "error": {
    "code": "...",
    "message": "...",
    "request_id": "..."
  }
}
```

## 12. Checklist Mapping
- `/ready` endpoint: done
- `/health` reports V6 version: done
- `/docs` exposure decision: done
- dependency readiness checks: done
- Dockerfile: done
- `.dockerignore`: done
- Docker image build: done
- Docker runtime verification: done
- CORS config: done
- API key config: done
- private endpoint protection: done
- global exception handling: done
- structured error response: done
- request ID middleware: done
- structured request logging: done
- rate limiting: done
- production env documentation: done
- Cloud Run deployment: deferred

## 13. Interview Summary
In V6, I added production-style backend hardening. The service now has V6 versioned health checks, readiness checks, verified Docker runtime support, environment-aware CORS, configurable API docs exposure, API key protection for private endpoints, basic rate limiting, global exception handlers that return one consistent error format, request IDs for traceability, and structured request logs for basic observability. Controlled route errors preserve their specific error codes, while validation failures and unexpected crashes are converted into safe structured responses.
