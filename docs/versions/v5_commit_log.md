# V5 Commit Log

This file maps each V5 commit heading to:
- what we implemented
- what was solved/taken care of

## Commit-by-Commit (V5)

### `59d1e2d` - `v5: add dataset upload contracts and validation guardrails`
**What we did**
- Added dataset schemas and upload/summary contract models.
- Added CSV guardrail settings in app config.
- Added dataset service foundation for validation and summary preparation.

**What it solved / took care of**
- Locked API contract first before adding endpoint complexity.
- Established strict validation rules for safe V5 growth.

### `738386c` - `v5: add dataset upload endpoint and safe CSV persistence`
**What we did**
- Added `POST /datasets/upload`.
- Persisted uploaded CSV files and stored dataset metadata in SQLite.
- Added integration tests for success and upload failure paths.

**What it solved / took care of**
- Enabled dataset lifecycle entrypoint with stable `dataset_id`.
- Added reproducible storage + registry foundation for later analysis endpoints.

### `f718355` - `v5: add dataset summary endpoint from stored metadata and CSV`
**What we did**
- Added `GET /datasets/{dataset_id}/summary`.
- Loaded stored CSV safely and returned structured summary output.
- Added integration tests for success/not-found/storage-missing cases.

**What it solved / took care of**
- Enabled deterministic dataset inspection by `dataset_id`.
- Validated that registry + storage + parser layers work end-to-end.

### `f681b46` - `v5: add dataset question schemas and intent routing foundation`
**What we did**
- Added ask-response schemas and analysis trace contract.
- Added intent detection and route-decision services.
- Added unit tests for intent and routing behavior.

**What it solved / took care of**
- Established controlled NLP-to-tool routing before execution.
- Reduced ambiguity in how user questions map to analysis actions.

### `f3f1bc8` - `v5: add safe dataset analysis tools and execution service`
**What we did**
- Added allowlisted pandas analysis tools:
  - summary, missing values, stats, value counts, groupby aggregation
- Added execution orchestrator with controlled error conversion.
- Added unit tests for tool and execution behavior.

**What it solved / took care of**
- Implemented safe analysis core without arbitrary code execution.
- Created traceable and testable execution layer for `/ask`.

### `c8dd3a1` - `v5: add dataset ask endpoint with intent routing and safe analysis execution`
**What we did**
- Added `POST /datasets/{dataset_id}/ask`.
- Connected dataset loading, intent routing, safe execution, and answer building.
- Added unsupported/ambiguous safe fallback response.
- Added integration tests for success, fallback, and not-found cases.

**What it solved / took care of**
- Completed V5 end-to-end natural-language CSV analysis flow.
- Delivered stable response/trace behavior for interview and evaluation readiness.

## Reusable Entry Template

### `<commit_hash>` - `<commit_heading>`
**What we did**
- ...

**What it solved / took care of**
- ...
