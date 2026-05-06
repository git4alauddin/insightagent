# V1 Commit Log

This file maps each V1 commit heading to:
- what we implemented
- what was solved/taken care of

## Commit-by-Commit (V1)

### `50c3184` - `v1: add app foundation and health endpoint`
**What we did**
- Created initial FastAPI app structure and app entrypoint.
- Added basic health route and related schema wiring.

**What it solved / took care of**
- Established the backend foundation for all later versions.
- Gave a quick service-alive endpoint for local validation.

### `513e344` - `v1: add chat request and response schemas`
**What we did**
- Added Pydantic request/response models for chat API.
- Defined the first stable `/chat` data contract.

**What it solved / took care of**
- Prevented ad-hoc response shapes.
- Made endpoint behavior testable and consistent.

### `9674002` - `v1: add LLM configuration fields`
**What we did**
- Added LLM settings in configuration (`provider`, `model`, `key`, `base_url`, timeout).

**What it solved / took care of**
- Removed hardcoded provider values from code paths.
- Enabled reproducible local setup using environment variables.

### `131cb73` - `v1: add Groq-backed chat endpoint`
**What we did**
- Integrated Groq-backed LLM service with chat route.
- Added end-to-end request -> LLM -> response flow for `/chat`.

**What it solved / took care of**
- Delivered the first real LLM-powered API behavior.
- Kept provider interaction inside service layer instead of route logic.

### `9689db3` - `v1: add Groq-backed chat endpoint tests and docs`
**What we did**
- Added tests and docs around Groq-backed chat behavior.

**What it solved / took care of**
- Improved confidence in API behavior before future refactors.
- Captured setup and usage clearly for repeatability.

### `662fee5` - `v1: improve chat input validation`
**What we did**
- Tightened request validation for chat input.

**What it solved / took care of**
- Rejected invalid/blank messages early.
- Avoided unnecessary LLM calls and noisy failures.

### `3b75d92` - `v1: add mocked chat endpoint test and update docs`
**What we did**
- Added mocked endpoint test paths and aligned docs.

**What it solved / took care of**
- Allowed deterministic test runs without live LLM dependency.
- Reduced test flakiness/cost/network coupling.

### `24b3325` - `v1: improve controlled error response shape`
**What we did**
- Standardized route-level error response format for chat failures.

**What it solved / took care of**
- Made client-side error handling predictable.
- Reduced ambiguity in failure contracts.

### `5b2ae22` - `v1: handle LLM provider errors and expand docs`
**What we did**
- Added provider-error conversion logic in service layer.
- Expanded docs with failure behavior notes.

**What it solved / took care of**
- Prevented raw provider exceptions leaking to API clients.
- Improved resilience and observability of failure paths.

### `2a7662c` - `v1: add technical walkthrough documentation`
**What we did**
- Added technical walkthrough for V1 internals.

**What it solved / took care of**
- Created strong interview/reference material for architecture discussion.
- Preserved implementation reasoning for future versions.

## Reusable Entry Template

### `<commit_hash>` - `<commit_heading>`
**What we did**
- ...

**What it solved / took care of**
- ...
