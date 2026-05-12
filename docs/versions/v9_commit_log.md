# V9 Commit Log

This file maps each V9 commit heading to:
- what we implemented
- what was solved/taken care of

## Commit-by-Commit (V9)

### `5ea3515` - `v9: add observability docs and version scaffold`
**What we did**
- Updated app version defaults to V9.
- Updated `.env.example` to V9.
- Updated health endpoint test expectation to V9.
- Updated README current version, Docker examples, health example, and V9 docs link.
- Added V9 main version documentation.
- Added V9 technical walkthrough.
- Added V9 commit log.
- Added V9 progress section to the project report.

**What it solved / took care of**
- Created a clean V9 boundary after closing V8.
- Prepared dedicated documentation space for observability and metrics work.
- Kept tracing/metrics implementation out of the scaffold chunk.

### `0e4f866` - `v9: fix exception handler typing diagnostics`
**What we did**
- Cast registered exception handlers to FastAPI/Starlette's `ExceptionHandler` type.
- Kept runtime exception behavior unchanged.
- Verified error handler and request ID middleware tests.

**What it solved / took care of**
- Removed IDE/Pylance diagnostics around typed exception handler registration.
- Preserved existing structured error response behavior.

### `e6acfb3` - `v9: enrich request completion logs`
**What we did**
- Added request status to completion logs.
- Added endpoint field while keeping the existing path field.
- Added basic error category mapping for failed requests.
- Added optional session id extraction from `x-session-id` header or `session_id` query parameter.
- Added tests for successful request log fields.
- Added tests for failed request error categorization.

**What it solved / took care of**
- Started the V9 runtime observability layer beyond request IDs.
- Made every request log easier to summarize by status and error category.
- Added a foundation for later metrics summary and request lifecycle examples.

### `2272215` - `v9: add tool trace fields to agent logs`
**What we did**
- Added structured `agent_tool_completed` logs for agent queries.
- Logged request id, tool used, tool status, agent status, and tool output summary.
- Validated agent controller responses before logging.
- Added integration coverage for agent tool trace logs.

**What it solved / took care of**
- Started API -> agent -> tool tracing.
- Covered the first tool-used and tool-status observability fields.
- Prepared agent logs for later tool usage frequency and success/failure metrics.

### `07a09c1` - `v9: add metrics summary script foundation`
**What we did**
- Added `scripts/metrics_summary.py`.
- Parsed both plain JSON log lines and prefixed log lines containing JSON payloads.
- Summarized request totals, success/failure counts, success rate, average latency, endpoint counts, and error categories.
- Summarized agent tool event totals, tool usage counts, tool status counts, and tool success rate.
- Added optional JSON output writing through `--output`.
- Added focused unit coverage for parsing, summary generation, missing log files, and output writing.

**What it solved / took care of**
- Started the V9 metrics summary workflow.
- Turned structured request and agent tool logs into reusable operational metrics.
- Made tool usage frequency and tool success/failure counts measurable from logs.

### `274f1f4` - `v9: document observability proof`
**What we did**
- Added README observability documentation.
- Documented request completion and agent tool log formats.
- Added a request lifecycle trace example that connects request id, endpoint log, tool log, and metrics summary.
- Updated V9 docs with log format guidance and observability proof.
- Updated the project report with the new documentation milestone.

**What it solved / took care of**
- Made the V9 observability behavior explainable from the README.
- Covered the checklist items for log format documentation, request lifecycle trace example, and README observability section.
- Helped show how logs can debug failed requests and summarize runtime behavior.

### `203650c` - `v9: link eval results to request traces`
**What we did**
- Added stable eval request id generation.
- Sent `x-request-id` on each primary eval request.
- Sent setup request ids for dataset and document upload steps.
- Captured the response request id from API responses.
- Added a `trace` block to each saved eval result.
- Documented how eval failures can be connected to runtime request logs.
- Added unit and integration coverage for eval trace metadata.

**What it solved / took care of**
- Linked evaluation results to request logs where possible.
- Made failed eval cases easier to debug through `request_id`.
- Preserved existing eval scoring while adding observability metadata.

### `14b8924` - `v9: summarize usage metrics when available`
**What we did**
- Added nullable token/cost fields to request completion logs.
- Read token/cost data from `request.state.usage` when a route or service provides it.
- Kept unavailable token/cost values as `null`.
- Added usage totals to the metrics summary script.
- Added tests for default unavailable usage and available usage aggregation.
- Updated README and V9 docs with the token/cost behavior.

**What it solved / took care of**
- Covered token/cost observability where usage data is available.
- Avoided fake estimates when providers or endpoints do not expose usage.
- Made metrics summaries include token/cost totals without changing API response contracts.

### `<pending>` - `v9: close observability checklist`
**What we did**
- Marked V9 documentation as complete.
- Added checklist coverage mapping for the V9 implementation and Done When items.
- Updated the project report with V9 closeout status.
- Updated README automated verification count.
- Recorded provider-specific usage extraction as a future improvement, not a blocker.

**What it solved / took care of**
- Closed the V9 observability and metrics milestone.
- Confirmed the checklist is covered by runtime logs, tool traces, metrics summaries, eval trace linking, and README/docs proof.
- Prepared the project to move to V10 portfolio packaging.

## Reusable Entry Template

### `<commit_hash>` - `<commit_heading>`
**What we did**
- ...

**What it solved / took care of**
- ...
