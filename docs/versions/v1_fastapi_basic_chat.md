# V1 - FastAPI + Basic LLM Chat API

## Goal
Build the base backend for InsightAgent with a clean FastAPI structure, configuration loading, logging setup, a health endpoint, and then a basic LLM-backed chat endpoint.

## Current Status
In progress.

Completed so far:
- Created the implementation project directory.
- Added the initial folder and documentation structure.
- Created placeholder files for the V1 backend modules.

Not built yet:
- FastAPI app entrypoint.
- `/health` endpoint.
- Config and logging implementation.
- `/chat` endpoint.
- LLM service wrapper.
- Chat request and response schemas.
- LLM error and timeout handling.
- Manual API test results.

## What We Built
Initial structure:

```text
app/
  main.py
  config.py
  api/
    routes_health.py
  schemas/
    common.py
  services/
  utils/
    logger.py
```

Planned first endpoint:

```text
GET /health
```

Expected response:

```json
{
  "status": "ok",
  "service": "InsightAgent",
  "version": "v1"
}
```

## Why We Built It
- A health endpoint proves the API is alive before adding LLM complexity.
- Separating routes, schemas, services, and utilities gives the project a maintainable backend shape.
- Configuration and logging are added early because every later feature will depend on them.

## Key Concepts Learned
- Pending. We will fill this after rebuilding the code step by step.

## API Design
### `GET /health`
Purpose:
- Return service status.
- Stay public and dependency-free.
- Confirm the app can boot successfully.

Response model:
- `status`: service state.
- `service`: application name.
- `version`: current project version.

## Implementation Notes
- `app/main.py` will create the FastAPI app and include routers.
- `app/config.py` will store app settings using Pydantic settings.
- `app/api/routes_health.py` will own the health route.
- `app/schemas/common.py` will define shared response schemas.
- `app/utils/logger.py` will centralize logging setup.

## Testing
Pending:
- Install dependencies.
- Start Uvicorn.
- Call `/health` from browser or curl.
- Add automated test for `/health`.

Manual test command:

```bash
curl http://127.0.0.1:8000/health
```

## Interview Explanation
Pending. We will write this after implementing and testing the first V1 slice ourselves.

## Trade-offs
- I kept the setup simple with `requirements.txt` instead of introducing advanced packaging early.
- I added only the folders needed for V1 so the project does not pretend to have future features before they exist.
- `/health` does not check external dependencies because readiness checks will come later in the deployment phase.
