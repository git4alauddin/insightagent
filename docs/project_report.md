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

## V3 Progress

### What We Built
- Added agent schemas for request, tool decision, and response contracts.
- Added dedicated tool input schemas.
- Added a tool registry and controlled initialization path.
- Added safe `calculator` tool (AST-based, no direct `eval()`).
- Added `date_time` tool with timezone handling.
- Added `text_summarizer` tool with deterministic summary behavior.
- Added `file_analyzer` tool for basic metadata and text stats.
- Added tool-router prompt template for LLM tool selection.
- Added tool decision parser with JSON + schema validation.
- Added agent controller service that orchestrates tool decision and execution.
- Added `POST /agent/query` endpoint.
- Added unit and integration tests for all V3 components.

### Why We Built It
- To move from "LLM answers directly" to a controlled agentic workflow.
- To separate reasoning (tool selection) from execution (backend-enforced tool calls).
- To validate tool decisions and tool inputs before any execution.
- To keep tool usage observable through explicit tool trace fields.
- To establish a stable foundation for V4/V5/V7 features that depend on tool orchestration.

### Files Added
- `app/schemas/agent.py`
- `app/schemas/tools.py`
- `app/tools/registry.py`
- `app/tools/calculator.py`
- `app/tools/date_time.py`
- `app/tools/text_summarizer.py`
- `app/tools/file_analyzer.py`
- `app/prompts/tool_router_v3.py`
- `app/services/tool_decision_parser.py`
- `app/services/agent_controller.py`
- `app/api/routes_agent.py`
- `tests/unit/test_agent_schemas.py`
- `tests/unit/test_calculator_tool.py`
- `tests/unit/test_date_time_tool.py`
- `tests/unit/test_text_summarizer_tool.py`
- `tests/unit/test_file_analyzer_tool.py`
- `tests/unit/test_tool_registry.py`
- `tests/unit/test_tool_router_prompt.py`
- `tests/unit/test_tool_decision_parser.py`
- `tests/unit/test_agent_controller.py`
- `tests/integration/test_agent_endpoint.py`
- `docs/versions/v3_tool_calling_agentic.md`

### Tests Performed
- Ran unit tests for all tool implementations and schema validations.
- Ran unit tests for tool-router prompt and decision parser.
- Ran unit tests for agent controller success/failure paths.
- Ran integration tests for `/agent/query`.
- Ran full test suite with `74 passed`.

### What I Learned
- The LLM should propose tool use, not execute tools directly.
- A registry pattern is key for backend-side tool allowlisting.
- Tool input validation should be explicit and schema-driven.
- Tool execution paths need controlled error conversion.
- Agent responses should include trace fields (`tool_used`, `tool_input`, `tool_output_summary`, `tool_status`) for debugging and interview explainability.

### Interview Explanation
- In V3, I introduced an agentic tool-calling layer. The LLM is prompted to return a JSON tool decision, which is parsed and validated with Pydantic before execution. The backend then resolves tools through a registry, validates input, executes safely, and returns a structured traceable response through `/agent/query`. This keeps tool execution controlled, testable, and production-oriented.

## V4 Progress

### What We Built
- Added SQLite database foundation under `app/db/`.
- Added core `sessions` and `messages` tables.
- Added migration-safe session metadata columns (`title`, `status`).
- Added session service for create/check/store/retrieve context flow.
- Added memory-aware chat endpoint: `POST /chat/memory`.
- Added session endpoints:
  - `POST /sessions`
  - `GET /sessions/{session_id}/messages`
- Added memory guardrails:
  - max context message limit
  - max message length limit
  - context message count in memory response
- Added controlled DB error handling for session service and session endpoints.

### Files Added
- `app/db/database.py`
- `app/db/schema.py`
- `app/schemas/session.py`
- `app/services/session_service.py`
- `app/services/memory_chat_service.py`
- `app/api/routes_session.py`
- `tests/unit/test_session_service.py`
- `tests/unit/test_memory_chat_service.py`
- `tests/integration/test_session_endpoints.py`
- `tests/integration/test_memory_chat_flow.py`
- `docs/versions/v4_memory_context.md`
- `docs/versions/v4_technical_walkthrough.md`

### Why We Built It
- To support multi-turn, session-based conversations.
- To make memory behavior observable and bounded.
- To ensure DB failures return controlled API responses instead of raw exceptions.

### Tests Performed
- Added unit tests for session service and memory chat service.
- Added integration tests for session endpoints and memory chat endpoint.
- Added DB failure-path tests for controlled error behavior.
- Added multi-turn memory flow integration coverage.
- Full suite currently passes (`93 passed`).

### What I Learned
- Memory features require both data modeling and operational safety controls.
- Clear error classification (`not found` vs `db error`) improves client behavior.
- Context trimming is essential for predictable LLM cost and latency.

### Interview Explanation
- In V4, I introduced session persistence and memory-aware chat. I created SQLite-backed session/message storage, added session APIs, and wired a memory endpoint that reuses recent context for replies. I also added guardrails and controlled DB error handling to keep the API predictable in failure scenarios.

## V5 Progress

### What We Built
- Added dataset upload contracts and validation guardrails.
- Added `POST /datasets/upload` with safe file persistence.
- Added dataset registry metadata in SQLite (`datasets` table).
- Added `GET /datasets/{dataset_id}/summary`.
- Added dataset ask schemas and analysis trace contract.
- Added intent routing foundation for natural-language dataset questions.
- Added safe analysis tools:
  - dataset summary
  - missing value analysis
  - column stats
  - value counts
  - groupby aggregation
- Added execution orchestration service for safe tool dispatch.
- Added `POST /datasets/{dataset_id}/ask`.
- Added safe fallback behavior for unsupported/ambiguous questions.

### Why We Built It
- To evolve InsightAgent from general LLM backend into practical data analysis backend.
- To keep data analysis execution safe and deterministic.
- To separate routing logic from execution logic for easier testing and debugging.
- To expose traceable analysis behavior for interviews and future observability layers.

### Files Added
- `app/schemas/dataset.py`
- `app/api/routes_datasets.py`
- `app/services/dataset_service.py`
- `app/services/dataset_registry_service.py`
- `app/services/dataset_intent_service.py`
- `app/services/dataset_analysis_router.py`
- `app/services/dataset_tools_service.py`
- `app/services/dataset_execution_service.py`
- `app/services/dataset_answer_service.py`
- `tests/integration/test_dataset_upload_endpoint.py`
- `tests/integration/test_dataset_summary_endpoint.py`
- `tests/integration/test_dataset_ask_endpoint.py`
- `tests/unit/test_dataset_intent_service.py`
- `tests/unit/test_dataset_analysis_router.py`
- `tests/unit/test_dataset_tools_service.py`
- `tests/unit/test_dataset_execution_service.py`
- `docs/versions/v5_data_analysis_assistant.md`
- `docs/versions/v5_technical_walkthrough.md`
- `docs/versions/v5_commit_log.md`

### Tests Performed
- Added integration tests for upload, summary, and ask endpoints.
- Added unit tests for intent detection, routing, tool behavior, and execution service.
- Added regression case for intent false-positive prevention (`"minister"` vs `"min"` token matching).
- Full suite status after V5 closeout: `126 passed`.

### What I Learned
- Safety comes from backend control, not prompt instructions alone.
- Dataset analysis needs strict validation before any processing.
- Intent routing can produce subtle NLP bugs unless token/phrase matching is carefully designed.
- Structured traces (`intent`, `tool_used`, `columns_used`, `operation`) make analysis flows explainable.
- Clear layer boundaries (registry/routing/execution/answer) keep growth manageable.

### Interview Explanation
- In V5, I implemented a safe CSV analysis architecture. Users can upload datasets, fetch summaries, and ask natural-language questions against stored datasets. The backend maps questions to allowlisted analysis tools and executes pandas operations through controlled services, with structured output and analysis trace. Unsupported questions return safe fallback responses, and no arbitrary Python execution path exists.

## V6 Progress

### What We Built
- Added `GET /ready` for dependency readiness checks.
- Added Docker runtime files.
- Added API key configuration through `API_KEY`.
- Added shared `x-api-key` auth dependency.
- Protected chat, agent, session, and dataset endpoints.
- Kept `/health` and `/ready` public.
- Added tests for missing, invalid, and unconfigured API key behavior.
- Added global exception handlers.
- Standardized API error responses to `{"error": {"code": "...", "message": "..."}}`.
- Added `INVALID_INPUT` handling for request validation errors.
- Added safe `INTERNAL_ERROR` handling for unexpected backend errors.
- Added request ID middleware.
- Added `x-request-id` response headers.
- Added `request_id` to structured error responses.

### Why We Built It
- To protect costly LLM and data endpoints.
- To avoid exposing private API behavior during deployment.
- To keep deployment health checks publicly reachable.
- To fail closed when authentication is not configured.
- To give API clients one predictable error contract.
- To prevent internal exception details from leaking in responses.
- To make requests traceable across client responses and future logs.

### Tests Performed
- Ran the full test suite after auth changes.
- Ran the full test suite after global exception handling.
- Ran the full test suite after request ID middleware.
- Current suite status: `138 passed`.

### What I Learned
- Authentication can be centralized as a FastAPI dependency.
- Router-level dependencies are useful when an entire endpoint group should be protected.
- Health/readiness endpoints usually stay public for infrastructure checks.
- Missing auth configuration should be treated as a deployment error, not as permission to expose the API.
- FastAPI exception handlers can preserve custom route errors while standardizing the response shape.
- Unexpected errors should be logged internally and returned as safe generic API errors.
- Request IDs are a small feature that make debugging much easier once logs and metrics grow.

### Interview Explanation
- In V6, I started hardening the backend for deployment. I added readiness checks, containerized the service, introduced API key authentication, centralized exception handling, and added request IDs. Private routes are protected at the router level, `/health` and `/ready` stay public for deployment checks, and API errors now use one consistent structured response with a traceable request ID.
