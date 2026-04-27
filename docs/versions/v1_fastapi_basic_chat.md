# V1 - FastAPI + Basic LLM Chat API

## 1. Goal
Build the first working backend version of InsightAgent:
- a clean FastAPI app structure
- configuration from environment variables
- basic logging setup
- `GET /health`
- `POST /chat`
- a Groq-backed LLM service wrapper
- stable Pydantic request/response models
- basic validation, latency tracking, error handling, tests, and documentation

The goal of V1 was not to build the full InsightAgent system. The goal was to create a clean backend foundation that later versions can extend without rewriting everything.

## 2. Final Outcome
V1 now has:
- `GET /health` returning service status
- `POST /chat` accepting a user message and returning an LLM answer
- Groq as the current default LLM provider
- OpenAI Python SDK used as an OpenAI-compatible client for Groq
- `.env` support for secrets and provider settings
- request validation for blank chat messages
- latency tracking for `/chat`
- controlled LLM service errors
- automated tests with no real LLM calls
- `10 passed` test result

Current endpoints:

```text
GET  /health
POST /chat
```

## 3. Build Timeline
### Step 1: Project Structure
We separated the reference planning docs from the real implementation.

Reference docs stayed in:

```text
project details/
```

Implementation lives in:

```text
insightagent/
```

Why:
- keeps planning material separate from source code
- makes the GitHub repo cleaner
- prepares the project for portfolio-style packaging later

### Step 2: FastAPI App Entrypoint
We created `app/main.py`.

Purpose:
- create the FastAPI `app`
- configure logging
- include routers

Learning:
- Uvicorn runs `app.main:app`
- `main.py` should assemble the app, not contain all route logic

### Step 3: App Configuration
We created `app/config.py` with Pydantic settings.

Purpose:
- centralize app settings
- read from `.env`
- avoid hardcoded secrets

Important fields:

```python
app_name
app_version
log_level
llm_provider
llm_model
llm_api_key
llm_base_url
llm_timeout_seconds
```

Learning:
- config should be a single source of truth
- `.env.example` documents required values
- `.env` contains real local secrets and must not be committed

### Step 4: Basic Logging Setup
We created `app/utils/logger.py`.

Purpose:
- define one `configure_logging()` function
- avoid using `print()` as the backend grows

Learning:
- V1 has basic logging only
- structured request logs and request IDs are intentionally deferred to V6/V9

### Step 5: Health Endpoint
We created:
- `app/schemas/common.py`
- `app/api/routes_health.py`

Purpose:
- confirm the app is alive
- prove routing and response models work

Response:

```json
{
  "status": "ok",
  "service": "InsightAgent",
  "version": "v1"
}
```

Learning:
- routes live in route modules
- response shapes should be modeled with Pydantic
- `main.py` includes routers with `app.include_router(...)`

### Step 6: Chat Schemas
We created `app/schemas/chat.py`.

Purpose:
- define the `/chat` API contract before writing endpoint behavior

Request model:

```python
class ChatRequest(BaseModel):
    message: str
```

Response model:

```python
class ChatResponse(BaseModel):
    answer: str
    model: str
    latency_ms: float
    status: str
```

Learning:
- schemas are API contracts
- route behavior should follow the contract, not invent response shapes ad hoc

### Step 7: Chat Input Validation
We added a Pydantic `field_validator` to `ChatRequest`.

Behavior:
- trims leading/trailing whitespace
- rejects blank or whitespace-only messages

Why:
- prevents useless LLM calls
- catches bad input early
- keeps API behavior predictable

Learning:
- validation belongs close to the data model
- bad requests should fail before service/provider logic runs

### Step 8: LLM Configuration
We added LLM-related settings:

```python
llm_provider: str = "groq"
llm_model: str = "llama-3.1-8b-instant"
llm_api_key: str | None = None
llm_base_url: str | None = "https://api.groq.com/openai/v1"
llm_timeout_seconds: float = 30.0
```

Why Groq:
- free-tier friendly for learning
- supports OpenAI-compatible chat completions
- lets us build a real LLM integration without OpenAI billing pressure

Important distinction:
- Groq is the current selected provider
- it is not a fallback provider yet
- true multi-provider failover is deferred

### Step 9: LLM Service Wrapper
We created `app/services/llm_service.py`.

Purpose:
- keep provider/client logic out of route files
- expose one simple function: `generate_answer(message: str) -> str`

Route-level code should not know the SDK details.

Clean flow:

```text
route -> generate_answer(...) -> provider client -> answer
```

Learning:
- routes should stay thin
- service layer owns provider interaction
- changing providers later should not require rewriting route logic

### Step 10: Groq-Backed Chat Endpoint
We created `app/api/routes_chat.py`.

Purpose:
- accept a `ChatRequest`
- call `generate_answer(...)`
- track latency
- return a `ChatResponse`

Response shape:

```json
{
  "answer": "...",
  "model": "llama-3.1-8b-instant",
  "latency_ms": 1234.56,
  "status": "success"
}
```

Learning:
- route owns HTTP concerns
- service owns LLM concerns
- latency tracking can start simple with `time.perf_counter()`

### Step 11: Controlled Error Handling
We added:
- `ErrorDetail`
- `ErrorResponse`
- `LLMServiceError`
- controlled error conversion in the route
- provider error conversion in the service

Current route error shape for LLM service failures:

```json
{
  "detail": {
    "error": {
      "code": "LLM_SERVICE_ERROR",
      "message": "LLM API key is not configured."
    }
  }
}
```

Why `detail` exists:
- FastAPI wraps `HTTPException.detail` inside a top-level `detail` field
- a top-level `{"error": ...}` shape needs a global exception handler
- global exception handling is intentionally deferred to V6 backend maturity

Service-level conversions:
- missing API key -> `LLMServiceError("LLM API key is not configured.")`
- timeout -> `LLMServiceError("LLM request timed out.")`
- connection failure -> `LLMServiceError("LLM provider connection failed.")`
- provider SDK error -> `LLMServiceError("LLM provider request failed.")`
- empty response -> `LLMServiceError("LLM returned an empty response.")`

Learning:
- route should not expose raw SDK exceptions
- provider errors should become app-specific errors first
- stable errors are easier for clients and tests to handle

### Step 12: Testing
We added automated tests for:
- health endpoint
- chat schemas
- chat endpoint success using mocked LLM
- chat endpoint failure using mocked service error
- LLM service missing API key
- LLM service timeout conversion
- LLM service empty response

Current result:

```text
10 passed
```

## 4. Final Project Structure for V1
```text
insightagent/
  app/
    main.py
    config.py
    api/
      routes_health.py
      routes_chat.py
    schemas/
      common.py
      chat.py
    services/
      llm_service.py
    utils/
      logger.py
  tests/
    test_health.py
    test_chat_schemas.py
    test_chat_endpoint.py
    test_llm_service.py
  docs/
    project_report.md
    versions/
      v1_fastapi_basic_chat.md
  .env.example
  .gitignore
  pytest.ini
  requirements.txt
  README.md
```

## 5. File-by-File Explanation
### `app/main.py`
Responsibility:
- create the FastAPI app
- configure logging
- include the health and chat routers

Key learning:
- this file assembles the app
- it should not contain endpoint business logic

### `app/config.py`
Responsibility:
- define app and LLM settings
- load values from environment variables and `.env`

Key learning:
- config prevents hardcoded secrets
- defaults should match the current development provider

### `app/utils/logger.py`
Responsibility:
- configure basic Python logging

Key learning:
- basic logging starts in V1
- structured logging comes later

### `app/schemas/common.py`
Responsibility:
- shared schemas like health and error response models

Current models:
- `HealthResponse`
- `ErrorDetail`
- `ErrorResponse`

### `app/schemas/chat.py`
Responsibility:
- chat request and response contracts
- chat input validation

Key learning:
- request validation should happen before service logic

### `app/api/routes_health.py`
Responsibility:
- define `GET /health`

Key learning:
- health endpoint should be simple and dependency-free in V1

### `app/api/routes_chat.py`
Responsibility:
- define `POST /chat`
- call the LLM service
- track latency
- convert LLM service errors into HTTP errors

Key learning:
- routes are thin HTTP adapters
- they should not directly call provider SDKs

### `app/services/llm_service.py`
Responsibility:
- create the provider client
- call the model
- convert SDK failures into `LLMServiceError`

Key learning:
- the service layer hides provider-specific details from routes

### `pytest.ini`
Responsibility:
- keep pytest focused on `tests/`
- disable pytest cache provider because Windows/OneDrive cache permissions created noise

Key learning:
- test tooling can and should be configured for the local environment

## 6. API Contracts
### `GET /health`
Request:

```text
GET /health
```

Response:

```json
{
  "status": "ok",
  "service": "InsightAgent",
  "version": "v1"
}
```

### `POST /chat`
Request:

```json
{
  "message": "Explain what a CSV file is in one sentence."
}
```

Validation:
- `message` must be present
- `message` must not be blank after trimming

Success response:

```json
{
  "answer": "...",
  "model": "llama-3.1-8b-instant",
  "latency_ms": 1234.56,
  "status": "success"
}
```

Controlled LLM service failure:

```json
{
  "detail": {
    "error": {
      "code": "LLM_SERVICE_ERROR",
      "message": "LLM request timed out."
    }
  }
}
```

## 7. Configuration and Secrets
`.env.example` documents required variables:

```env
APP_NAME=InsightAgent
APP_VERSION=v1
LOG_LEVEL=INFO

LLM_PROVIDER=groq
LLM_MODEL=llama-3.1-8b-instant
LLM_API_KEY=your-api-key-here
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_TIMEOUT_SECONDS=30
```

Local `.env` contains the real key and is ignored by Git.

Important rule:
- commit `.env.example`
- never commit `.env`

We verified `.env` was ignored by Git.

## 8. Testing Strategy
### Why We Mocked the LLM
Real LLM calls are not good automated tests because they:
- require API keys
- depend on network availability
- can hit rate limits
- add cost
- can return variable text

So automated tests mock LLM behavior.

Manual test proves real provider integration.
Automated tests prove backend behavior.

### Test Files
`tests/test_health.py`
- verifies `/health`

`tests/test_chat_schemas.py`
- verifies chat request/response models
- verifies trimming and blank-message rejection

`tests/test_chat_endpoint.py`
- verifies `/chat` success using a mocked LLM
- verifies `/chat` controlled error when service fails

`tests/test_llm_service.py`
- verifies missing API key behavior
- verifies timeout conversion
- verifies empty response handling

### Current Test Command
```powershell
python -m pytest
```

Current result:

```text
10 passed
```

## 9. Issues Faced and Fixes
### PowerShell `curl` Issue
Problem:
- PowerShell aliases `curl` to `Invoke-WebRequest`
- `-H "Content-Type: application/json"` did not work like Unix curl

Fix:
- used `Invoke-RestMethod`

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/chat" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"message":"Explain what a CSV file is in one sentence."}'
```

Learning:
- Windows PowerShell API testing has different command behavior

### OpenAI Billing / Provider Choice
Problem:
- OpenAI API access was not available for free

Fix:
- switched V1 provider to Groq
- used OpenAI-compatible chat completions with Groq base URL

Learning:
- provider choice can change without changing route logic if service separation is clean

### `.env` Secret Safety
Problem:
- real API keys must not enter GitHub

Fix:
- `.env` ignored in `.gitignore`
- `.env.example` committed with placeholders

Learning:
- document required secrets without exposing real secrets

### Pytest Cache Permission Noise
Problem:
- Windows/OneDrive caused pytest cache permission warnings/errors

Fix:
- added `pytest.ini`
- restricted test discovery to `tests/`
- disabled pytest cache provider

Learning:
- test runner configuration is part of project reliability

### `APITimeoutError` Test Construction
Problem:
- `APITimeoutError` expects a request object

Fix:
- created a fake request using `httpx.Request`

```python
APITimeoutError(request=Request("POST", "https://example.test/llm"))
```

Learning:
- tests should mimic real exception shapes when possible

## 10. Git Commit Timeline
Important V1 commits:

```text
v1: add app foundation and health endpoint
v1: add chat request and response schemas
v1: add LLM configuration fields
v1: add Groq-backed chat endpoint
v1: add Groq-backed chat endpoint tests and docs
v1: improve chat input validation
v1: add mocked chat endpoint test and update docs
v1: improve controlled error response shape
v1: handle LLM provider errors
```

Learning:
- V1 was built feature by feature
- each working chunk was reviewed, tested, documented, committed, and pushed

## 11. Checklist Status
Completed:
- FastAPI project structure
- `app/main.py`
- `app/config.py`
- schema modules
- `app/services/llm_service.py`
- `app/utils/logger.py`
- `/health`
- `/chat`
- chat request model
- chat response model
- `.env` support
- `.env.example`
- LLM API key loading from environment
- LLM client wrapper/service
- missing API key handling
- timeout/provider error handling
- latency tracking
- basic logging setup
- basic route-level exception handling
- README startup command
- `/chat` request example
- manual `/health` and `/chat` testing
- automated tests

Done-when status:
- `/health` returns service status: done
- `/chat` accepts a message and returns an LLM answer: done
- response has stable JSON shape: done
- LLM logic is separated from route logic: done
- API key is loaded from environment: done
- no secret is hardcoded: done
- missing config returns controlled service error: done
- LLM failure returns controlled route error: done
- basic logs are available: done at V1 level
- manual API test works: done

## 12. Deferred on Purpose
These are not missing from V1; they belong to later versions:

- structured LLM output -> V2
- prompt versioning -> V2
- tool calling -> V3
- memory/session support -> V4
- global exception handler -> V6
- request IDs -> V6/V9
- structured JSON logs -> V6/V9
- `/ready` endpoint -> V6
- authentication/rate limiting -> V6
- Docker/deployment -> V6

## 13. What I Learned
Backend:
- how a FastAPI app is structured
- how routers keep endpoints modular
- why routes should stay thin
- how services isolate business/provider logic

Validation:
- how Pydantic models define API contracts
- how `field_validator` can clean and reject bad input

Configuration:
- how `.env` and Pydantic settings work
- how to avoid committing secrets
- why `.env.example` matters

LLM integration:
- how to wrap provider calls in a service
- how Groq can be used through an OpenAI-compatible client
- how to convert provider errors into application errors

Testing:
- how to use `TestClient`
- how to mock provider calls
- why real LLM calls should not be in normal unit tests
- how to test error paths directly

Tooling:
- how to handle PowerShell API request quirks
- how to configure pytest for a Windows/OneDrive environment
- how to use Git commits as learning checkpoints

## 14. Interview Explanation
Short version:

> In V1, I built the FastAPI foundation for InsightAgent. I created a clean app structure with separate config, schemas, routes, services, and utilities. The backend has `/health` and `/chat`; `/chat` validates input, calls a Groq-backed LLM service, tracks latency, and returns a stable JSON response. I kept provider logic inside the service layer and added tests with mocked LLM calls so the test suite is deterministic and cost-free.

More detailed version:

> I built V1 as a production-style foundation rather than a quick chatbot wrapper. I used Pydantic settings for environment-based config, kept secrets in `.env`, used Pydantic models for request and response contracts, and separated FastAPI routes from LLM provider logic. Groq is the current provider because it is free-tier friendly, but the route only talks to the service layer, so the provider can change later. I also added validation for blank messages, latency tracking, controlled service errors, and a test suite covering health, schemas, chat success, route failure, and service-layer failure paths.

## 15. Trade-offs
- Used `requirements.txt` for simplicity instead of advanced packaging.
- Used Groq as the default V1 provider because it was practical for learning.
- Used the OpenAI Python SDK because Groq supports OpenAI-compatible chat completions.
- Kept V1 responses plain text; structured output belongs to V2.
- Used route-level `HTTPException` instead of a global exception handler; global handling belongs to V6.
- Kept logging basic; structured logs and request IDs belong to V6/V9.
- Avoided real LLM calls in automated tests to keep tests fast, deterministic, and cost-free.

