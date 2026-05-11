# V6 Commit Log

This file maps each V6 commit heading to:
- what we implemented
- what was solved/taken care of

## Commit-by-Commit (V6)

### `af19cc2` - `v6: add readiness endpoint with dependency health checks`
**What we did**
- Added `GET /ready`.
- Added readiness checks for LLM config, database connectivity, and upload storage.
- Added tests for ready and not-ready behavior.

**What it solved / took care of**
- Separated liveness from dependency readiness.
- Prepared the backend for deployment platforms that need readiness checks.

### `ede877d` - `v6: add Dockerfile and dockerignore for containerized runtime`
**What we did**
- Added a Dockerfile for running the FastAPI app in a container.
- Added `.dockerignore` to keep secrets, caches, uploads, docs, and tests out of the runtime image.

**What it solved / took care of**
- Made the backend container-ready.
- Reduced image noise and avoided copying local-only files.

### `<pending>` - `v6: add API key authentication for private endpoints`
**What we did**
- Added `API_KEY` config.
- Added shared `x-api-key` authentication dependency.
- Protected chat, agent, session, and dataset routers.
- Kept `/health` and `/ready` public.
- Added auth tests for missing, invalid, and unconfigured keys.

**What it solved / took care of**
- Protected costly and state-changing endpoints.
- Made missing auth configuration fail closed.

### `<pending>` - `v6: add global exception handling and structured errors`
**What we did**
- Added global exception handlers.
- Converted controlled `HTTPException` responses into a clean `{"error": ...}` shape.
- Converted validation failures into `INVALID_INPUT`.
- Converted unexpected crashes into safe `INTERNAL_ERROR` responses.
- Added focused error handler tests.

**What it solved / took care of**
- Gave the API one consistent error contract.
- Prevented internal exception details from leaking to clients.

## Reusable Entry Template

### `<commit_hash>` - `<commit_heading>`
**What we did**
- ...

**What it solved / took care of**
- ...
