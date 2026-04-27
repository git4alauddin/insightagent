# V1 - FastAPI + Basic LLM Chat API

## Goal
Build the base backend for InsightAgent with a clean FastAPI structure, configuration loading, logging setup, a health endpoint, and a basic LLM-backed chat endpoint.

## Current Status
In progress. The main V1 backend flow is working locally:
- `GET /health`
- `POST /chat`
- Groq-backed LLM service wrapper
- Pydantic request and response models
- blank-message validation for chat input
- latency tracking for `/chat`
- basic automated tests

Remaining V1 polish:
- Improve controlled exception handling shape.
- Add clearer V1 completion checklist status.

## What We Built
Current structure:

```text
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
```

Endpoints:

```text
GET /health
POST /chat
```

`GET /health` response:

```json
{
  "status": "ok",
  "service": "InsightAgent",
  "version": "v1"
}
```

`POST /chat` request:

```json
{
  "message": "Explain what a CSV file is in one sentence."
}
```

Validation:
- `message` is required.
- blank or whitespace-only messages are rejected.
- leading/trailing whitespace is trimmed before processing.

`POST /chat` response shape:

```json
{
  "answer": "...",
  "model": "llama-3.1-8b-instant",
  "latency_ms": 1234.56,
  "status": "success"
}
```

## Why We Built It
- `/health` proves the API is alive before adding LLM complexity.
- `/chat` proves the backend can accept validated input, call an LLM service, and return a stable response.
- input validation prevents empty messages from wasting LLM calls.
- Separating routes, schemas, config, logging, and services gives the project a maintainable backend shape.
- Groq is used as the V1 LLM provider because it is free-tier friendly for learning.

## Key Concepts Learned
- FastAPI app creation and router registration.
- Pydantic request and response models.
- Pydantic field validation with `field_validator`.
- Environment-driven configuration with `.env`.
- Keeping secrets out of code and GitHub.
- Service-layer separation: route code calls `llm_service`, not the provider client directly.
- Basic latency tracking with `time.perf_counter()`.
- PowerShell API testing with `Invoke-RestMethod`.

## API Design
### `GET /health`
Purpose:
- Return service status.
- Stay public and dependency-free.
- Confirm the app can boot successfully.

### `POST /chat`
Purpose:
- Accept a user message.
- Send the message through the LLM service wrapper.
- Return an answer, model name, latency, and status.

Failure behavior:
- Blank messages fail Pydantic validation before the LLM service is called.
- If the LLM service raises `LLMServiceError`, the route returns HTTP `503`.

## Implementation Notes
- `app/main.py` creates the FastAPI app and includes routers.
- `app/config.py` stores app and LLM settings using Pydantic settings.
- `app/api/routes_health.py` owns the health route.
- `app/api/routes_chat.py` owns the chat route.
- `app/schemas/common.py` defines shared response schemas.
- `app/schemas/chat.py` defines chat request and response schemas.
- `app/services/llm_service.py` owns provider/client interaction.
- `app/utils/logger.py` centralizes logging setup.
- `pytest.ini` keeps test discovery focused on `tests/` and avoids local pytest cache permission noise.

## Testing
Manual tests performed:
- Started the API with Uvicorn.
- Called `/health` in the browser.
- Called `/chat` with PowerShell `Invoke-RestMethod`.
- Confirmed Groq returned a real answer.
- Confirmed `.env` is ignored by Git.

Automated tests:
- `/health` returns the expected service status.
- `/chat` returns a stable response using a mocked LLM call.
- `ChatRequest` accepts a normal message.
- `ChatRequest` trims leading/trailing whitespace.
- `ChatRequest` rejects blank messages.
- `ChatResponse` accepts numeric latency.

Current test result:

```text
6 passed
```

Manual `/chat` test command:

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/chat" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"message":"Explain what a CSV file is in one sentence."}'
```

## Interview Explanation
In V1, I built the FastAPI foundation for InsightAgent. I separated app setup, config, logging, schemas, routes, and LLM service logic. The `/health` endpoint confirms the backend is running, while `/chat` accepts a validated message, rejects blank input, calls a Groq-backed LLM service, tracks latency, and returns a stable JSON response. I kept provider details inside the service layer so the route remains simple and easier to change later.

## Trade-offs
- I used `requirements.txt` for simple reproducibility instead of advanced packaging.
- I used Groq as the default V1 provider because it is easier to test during learning.
- I used the OpenAI Python SDK because Groq supports OpenAI-compatible chat completions.
- I kept the V1 response plain text only; structured output belongs to V2.
- `/health` does not check external dependencies because readiness checks belong to a later deployment phase.
- I avoided testing real LLM calls in automated tests because they depend on external service availability, API keys, latency, and rate limits.
- I tested `/chat` with a mocked LLM function so endpoint behavior stays deterministic and cost-free.
