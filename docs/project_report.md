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
