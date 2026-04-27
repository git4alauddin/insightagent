# V1 Technical Walkthrough

This document explains the V1 codebase file by file. The goal is to make the implementation easy to revise, debug, and explain in interviews.

## 1. `app/main.py`

### Purpose
`main.py` is the FastAPI application entrypoint. This is the file Uvicorn loads when we run:

```bash
uvicorn app.main:app --reload
```

In `app.main:app`:
- `app` before the dot refers to the `app/` package folder
- `main` refers to `main.py`
- the final `app` refers to the FastAPI object inside the file

### Code
```python
from fastapi import FastAPI

from app.api.routes_chat import router as chat_router
from app.api.routes_health import router as health_router
from app.config import settings
from app.utils.logger import configure_logging


configure_logging()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

app.include_router(health_router)
app.include_router(chat_router)
```

### Explanation
```python
from fastapi import FastAPI
```
Imports the FastAPI class used to create the backend app.

```python
from app.api.routes_chat import router as chat_router
from app.api.routes_health import router as health_router
```
Imports the route groups from separate files. The aliases make each router's purpose obvious.

```python
from app.config import settings
```
Imports centralized app settings instead of hardcoding app name/version.

```python
from app.utils.logger import configure_logging
```
Imports the logging setup function.

```python
configure_logging()
```
Configures application logging during startup.

```python
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)
```
Creates the FastAPI app object. This is the object Uvicorn runs.

```python
app.include_router(health_router)
app.include_router(chat_router)
```
Registers `/health` and `/chat` with the main app.

### Design Decision
`main.py` is intentionally small. It assembles the app but does not contain route logic, schema definitions, or LLM provider logic.

### Interview Explanation
`main.py` is the application entrypoint. I kept it responsible only for creating the FastAPI app, configuring logging, and including routers. This keeps the backend modular because endpoint logic lives in route files and provider logic lives in services.

## 2. `app/config.py`

### Purpose
`config.py` centralizes project settings and reads environment variables from `.env`.

### Code
```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "InsightAgent"
    app_version: str = "v1"
    log_level: str = "INFO"

    llm_provider: str = "groq"
    llm_model: str = "llama-3.1-8b-instant"
    llm_api_key: str | None = None
    llm_base_url: str | None = "https://api.groq.com/openai/v1"
    llm_timeout_seconds: float = 30.0

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
```

### Explanation
```python
from pydantic_settings import BaseSettings, SettingsConfigDict
```
Imports the tools used to define environment-driven settings.

```python
class Settings(BaseSettings):
```
Defines the settings model. `BaseSettings` allows values to come from environment variables.

```python
app_name: str = "InsightAgent"
app_version: str = "v1"
log_level: str = "INFO"
```
Stores basic app metadata and logging level.

```python
llm_provider: str = "groq"
llm_model: str = "llama-3.1-8b-instant"
llm_api_key: str | None = None
llm_base_url: str | None = "https://api.groq.com/openai/v1"
llm_timeout_seconds: float = 30.0
```
Stores LLM provider settings. The real API key comes from `.env`, not source code.

```python
model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
```
Tells Pydantic settings to load values from `.env`.

```python
settings = Settings()
```
Creates one reusable settings object that other files can import.

### Design Decision
Config values are kept in one place so routes and services do not hardcode names, models, keys, URLs, or timeouts.

### Interview Explanation
I used Pydantic settings to centralize configuration and keep secrets out of code. `.env.example` documents required variables, while the real `.env` stays local and ignored by Git.

## 3. `app/utils/logger.py`

### Purpose
`logger.py` configures Python's built-in logging system.

### Code
```python
import logging

from app.config import settings


def configure_logging() -> None:
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )
```

### Explanation
```python
import logging
```
Imports Python's standard logging module.

```python
from app.config import settings
```
Allows logging to use the configured log level.

```python
def configure_logging() -> None:
```
Defines a setup function. It returns nothing because its job is configuration.

```python
logging.basicConfig(...)
```
Sets default logging behavior for the app.

```python
level=settings.log_level
```
Controls which logs are shown, such as `INFO`, `DEBUG`, or `ERROR`.

```python
format="%(asctime)s %(levelname)s %(name)s - %(message)s"
```
Defines how log lines appear.

### Design Decision
Logging is centralized so future files can use Python logging without redefining logging behavior.

### Interview Explanation
I added a small logging utility in V1 to establish centralized logging early. It is basic now, but it can evolve later into structured logs with request IDs, latency, tool usage, and cost tracking.

## 4. `app/schemas/common.py`

### Purpose
`common.py` stores shared Pydantic schemas used across the app.

### Code
```python
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail
```

### Explanation
```python
class HealthResponse(BaseModel):
```
Defines the response contract for `/health`.

```python
status: str
service: str
version: str
```
These fields make the health response stable and predictable.

```python
class ErrorDetail(BaseModel):
```
Defines the inner structure of an error.

```python
class ErrorResponse(BaseModel):
    error: ErrorDetail
```
Defines the app-level error shape used for controlled failures.

### Design Decision
Shared schemas live in `common.py` so they can be reused by multiple routes later.

### Interview Explanation
I used Pydantic models for health and error responses so API responses have explicit, typed contracts instead of loose dictionaries.

## 5. `app/schemas/chat.py`

### Purpose
`chat.py` defines request and response schemas for `/chat`.

### Code
```python
from pydantic import BaseModel, field_validator


class ChatRequest(BaseModel):
    message: str

    @field_validator("message")
    @classmethod
    def message_must_not_be_blank(cls, value: str) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("Message must not be empty.")

        return cleaned_value


class ChatResponse(BaseModel):
    answer: str
    model: str
    latency_ms: float
    status: str
```

### Explanation
```python
class ChatRequest(BaseModel):
    message: str
```
Defines the incoming `/chat` request body.

```python
@field_validator("message")
```
Runs custom validation on the `message` field.

```python
cleaned_value = value.strip()
```
Removes leading and trailing whitespace.

```python
if not cleaned_value:
    raise ValueError("Message must not be empty.")
```
Rejects empty or whitespace-only messages before the LLM is called.

```python
return cleaned_value
```
Stores the trimmed message in the validated request model.

```python
class ChatResponse(BaseModel):
```
Defines the stable response shape for `/chat`.

### Design Decision
Validation belongs in the schema because the route should receive clean, validated input.

### Interview Explanation
I used Pydantic validation to reject blank messages before calling the LLM. This avoids wasted provider calls and keeps the route simpler.

## 6. `app/api/routes_health.py`

### Purpose
`routes_health.py` defines the public health endpoint.

### Code
```python
from fastapi import APIRouter

from app.config import settings
from app.schemas.common import HealthResponse


router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        version=settings.app_version,
    )
```

### Explanation
```python
router = APIRouter(tags=["health"])
```
Creates a route group for health endpoints.

```python
@router.get("/health", response_model=HealthResponse)
```
Registers a `GET /health` endpoint and declares its response model.

```python
def health_check() -> HealthResponse:
```
Defines the route function.

```python
return HealthResponse(...)
```
Returns a typed response using app settings.

### Design Decision
The health route is dependency-free in V1. It only confirms the app is alive. Deeper dependency checks belong to `/ready` in a later deployment version.

### Interview Explanation
I added `/health` as a simple public endpoint to verify the API is running. It returns a stable Pydantic response and does not depend on external services.

## 7. `app/api/routes_chat.py`

### Purpose
`routes_chat.py` defines the `POST /chat` endpoint.

### Code
```python
import time

from fastapi import APIRouter, HTTPException

from app.config import settings
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm_service import LLMServiceError, generate_answer


router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    start_time = time.perf_counter()

    try:
        answer = generate_answer(request.message)
    except LLMServiceError as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "error": {
                    "code": "LLM_SERVICE_ERROR",
                    "message": str(exc),
                }
            },
        ) from exc

    latency_ms = (time.perf_counter() - start_time) * 1000

    return ChatResponse(
        answer=answer,
        model=settings.llm_model,
        latency_ms=round(latency_ms, 2),
        status="success",
    )
```

### Explanation
```python
import time
```
Used for latency tracking.

```python
from fastapi import APIRouter, HTTPException
```
Imports routing and HTTP error tools.

```python
from app.schemas.chat import ChatRequest, ChatResponse
```
Imports the request and response contracts.

```python
from app.services.llm_service import LLMServiceError, generate_answer
```
Imports the service-layer function and error type.

```python
start_time = time.perf_counter()
```
Starts a high-resolution timer.

```python
answer = generate_answer(request.message)
```
Calls the LLM service. The route does not directly create a provider client.

```python
except LLMServiceError as exc:
```
Catches controlled service-layer failures.

```python
raise HTTPException(status_code=503, detail={...}) from exc
```
Turns service failure into an HTTP error response.

```python
latency_ms = (time.perf_counter() - start_time) * 1000
```
Calculates request latency in milliseconds.

```python
return ChatResponse(...)
```
Returns a stable response model.

### Design Decision
The route owns HTTP concerns and delegates LLM work to `llm_service.py`.

### Interview Explanation
The `/chat` route validates input through Pydantic, delegates model interaction to the service layer, tracks latency, and returns a stable response. It catches `LLMServiceError` so provider failures become controlled HTTP responses.

## 8. `app/services/llm_service.py`

### Purpose
`llm_service.py` owns LLM provider interaction.

### Code
```python
from openai import APIConnectionError, APITimeoutError, OpenAI, OpenAIError

from app.config import settings


class LLMServiceError(Exception):
    pass


def generate_answer(message: str) -> str:
    if not settings.llm_api_key:
        raise LLMServiceError("LLM API key is not configured.")

    client = OpenAI(
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        timeout=settings.llm_timeout_seconds,
    )

    try:
        response = client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {"role": "user", "content": message},
            ],
        )
    except APITimeoutError as exc:
        raise LLMServiceError("LLM request timed out.") from exc
    except APIConnectionError as exc:
        raise LLMServiceError("LLM provider connection failed.") from exc
    except OpenAIError as exc:
        raise LLMServiceError("LLM provider request failed.") from exc

    answer = response.choices[0].message.content

    if not answer:
        raise LLMServiceError("LLM returned an empty response.")

    return answer
```

### Explanation
```python
from openai import APIConnectionError, APITimeoutError, OpenAI, OpenAIError
```
Imports the OpenAI-compatible client and relevant SDK error types.

```python
class LLMServiceError(Exception):
    pass
```
Defines an app-specific error type for LLM service failures.

```python
if not settings.llm_api_key:
```
Checks that the API key is configured before creating a client.

```python
client = OpenAI(...)
```
Creates the provider client. With Groq, `base_url` points to Groq's OpenAI-compatible endpoint.

```python
response = client.chat.completions.create(...)
```
Calls the chat completions endpoint.

```python
except APITimeoutError as exc:
```
Converts provider timeout errors into app-specific errors.

```python
except APIConnectionError as exc:
```
Converts provider connection failures into app-specific errors.

```python
except OpenAIError as exc:
```
Converts other OpenAI-compatible SDK errors into app-specific errors.

```python
answer = response.choices[0].message.content
```
Extracts the model answer from the provider response.

```python
if not answer:
```
Rejects empty model responses.

### Design Decision
Provider SDK errors are converted inside the service so route code only handles `LLMServiceError`.

### Interview Explanation
I wrapped LLM provider interaction in a service function. This keeps provider-specific client setup and errors out of the route layer. The service converts SDK failures into one app-specific error type, making the API easier to control and test.

## 9. Tests

### `tests/test_health.py`
Tests that `/health` returns:
- status code `200`
- stable service JSON

### `tests/test_chat_schemas.py`
Tests:
- normal message accepted
- whitespace trimmed
- blank message rejected
- numeric latency accepted in `ChatResponse`

### `tests/test_chat_endpoint.py`
Tests:
- `/chat` success response with mocked LLM answer
- `/chat` controlled `503` when LLM service fails

Important mocking detail:
```python
patch("app.api.routes_chat.generate_answer", ...)
```
We patch where the function is used, not where it was originally defined.

### `tests/test_llm_service.py`
Tests:
- missing API key raises `LLMServiceError`
- timeout error is converted to `LLMServiceError`
- empty provider response is rejected

Important test detail:
```python
APITimeoutError(request=Request("POST", "https://example.test/llm"))
```
`APITimeoutError` expects a request object, so the test uses `httpx.Request`.

## 10. Final Mental Model
```text
main.py
  creates FastAPI app
  includes routers

routes/
  handle HTTP requests and responses

schemas/
  define request/response contracts
  validate input

services/
  contain provider/business logic

config.py
  loads environment-driven settings

logger.py
  configures logging

tests/
  protect endpoint, schema, and service behavior
```

## 11. V1 Codebase Interview Summary
In V1, the codebase is organized around separation of concerns. `main.py` assembles the FastAPI app, route files define HTTP endpoints, schema files define request/response contracts, and the LLM service owns provider interaction. Config is loaded through Pydantic settings, secrets stay in `.env`, and tests use mocking so LLM-dependent behavior remains deterministic. This gives the project a clean backend foundation before adding structured outputs, tools, memory, data analysis, and RAG in later versions.

