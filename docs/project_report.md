# InsightAgent Project Report

## Project Goal
Production-style FastAPI backend for AI-powered data and document analysis.

## Build Strategy
Learning-first, version-by-version implementation.

## V1 Progress

### What We Built
- Created the initial implementation directory separate from the reference docs.
- Added the FastAPI app foundation.
- Added central app and LLM configuration.
- Added basic logging setup.
- Added `GET /health`.
- Added chat request and response schemas.
- Added a Groq-backed LLM service wrapper.
- Added `POST /chat` with latency tracking.

### Why We Built It
- To keep reference planning separate from production code.
- To create a clean backend foundation before future versions.
- To keep route logic separate from LLM provider logic.
- To support a learning-first workflow: brief, strategy, implementation, review, test, document, commit.

### Files Added
- `app/main.py`
- `app/config.py`
- `app/api/routes_health.py`
- `app/api/routes_chat.py`
- `app/schemas/common.py`
- `app/schemas/chat.py`
- `app/services/llm_service.py`
- `app/utils/logger.py`
- `requirements.txt`
- `.env.example`
- `README.md`

### Tests Performed
- Ran the FastAPI app locally with Uvicorn.
- Tested `/health` manually.
- Tested `/chat` manually with PowerShell `Invoke-RestMethod`.
- Verified Groq returned a real answer.
- Verified `.env` is ignored by Git.

### What I Learned
- How FastAPI app setup and routers work.
- How Pydantic models define API contracts.
- How to load config from environment variables.
- Why secrets should stay in `.env` and out of GitHub.
- How to separate route logic from service/provider logic.
- How to track basic request latency.

### Interview Explanation
- In V1, I built a clean FastAPI backend foundation with `/health` and `/chat`. I used Pydantic for request/response contracts, Pydantic settings for environment-based config, and a service layer to isolate Groq-backed LLM calls from route logic. This keeps the backend easier to test, explain, and extend in later versions.

## V2 Progress

### What We Built
- Added structured LLM response schemas.
- Added a versioned structured prompt template.
- Added a parser for validating raw LLM JSON output.
- Added a structured LLM service.
- Added retry once when structured output parsing/validation fails.
- Added fallback structured response when retry still fails.
- Added `POST /chat/structured`.
- Organized tests into `unit/` and `integration/`.
- Added unit and integration coverage for the structured workflow.

### Why We Built It
- To move from free-form LLM text to a predictable backend contract.
- To validate LLM output before returning it from the API.
- To keep the API response predictable even when the model returns invalid JSON.
- To prepare the project for future data and document analysis workflows.
- To keep prompting, parsing, business flow, and routing in separate layers.

### Files Added
- `app/schemas/structured.py`
- `app/prompts/structured_v2.py`
- `app/services/structured_parser.py`
- `app/services/structured_llm_service.py`
- `tests/unit/test_structured_schemas.py`
- `tests/unit/test_structured_prompt.py`
- `tests/unit/test_structured_parser.py`
- `tests/unit/test_structured_llm_service.py`
- `docs/versions/v2_structured_output.md`

### Tests Performed
- Ran unit tests for schema, prompt, parser, structured service, retry, and fallback behavior.
- Ran integration tests for `/chat/structured`.
- Ran the full test suite with `27 passed`.
- Manually tested `/chat/structured` with the real configured LLM provider.

### What I Learned
- LLM responses should be validated like any other external input.
- Pydantic schemas can turn model output into a reliable API contract.
- Prompt versioning helps track changes in LLM behavior.
- Retry/fallback behavior makes structured output safer than a single-shot parse.
- Mocking the LLM keeps tests reliable and cost-free.
- Integration tests prove that route, service, parser, and schema layers work together.

### Interview Explanation
- In V2, I added structured output support. The API now has a `/chat/structured` endpoint that asks the LLM for JSON, parses it, validates it with Pydantic, retries once on invalid output, and returns a fallback structured response if retry still fails. I separated prompt construction, parsing, service logic, and routing so the feature is easier to test and extend.
