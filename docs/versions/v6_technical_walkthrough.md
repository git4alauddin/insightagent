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

## 2. Readiness Layer

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

## 3. API Key Authentication

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

## 4. Global Error Handling

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

## 5. Request ID Middleware

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

## 6. Tests Added/Extended

### Auth Tests
`tests/integration/test_auth_dependency.py` verifies:
- `/health` is public
- `/ready` is public
- protected endpoints reject missing API keys
- protected endpoints reject invalid API keys
- missing configured `API_KEY` fails closed

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

## 7. Checklist Mapping
- `/ready` endpoint: done
- dependency readiness checks: done
- Dockerfile: done
- `.dockerignore`: done
- API key config: done
- private endpoint protection: done
- global exception handling: done
- structured error response: done
- request ID middleware: done
- structured request logging: done
- rate limiting: pending
- CORS config: pending

## 8. Interview Summary
In V6, I added production-style backend hardening. The service now has readiness checks, Docker runtime support, API key protection for private endpoints, global exception handlers that return one consistent error format, request IDs for traceability, and structured request logs for basic observability. Controlled route errors preserve their specific error codes, while validation failures and unexpected crashes are converted into safe structured responses.
