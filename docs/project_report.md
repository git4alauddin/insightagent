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
- Verified Docker image build and runtime.
- Aligned app version reporting to V6.
- Added environment-controlled docs exposure.
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
- Added structured request logging with request ID, method, path, status code, and latency.
- Added environment-aware CORS configuration.
- Added basic in-memory rate limiting for private endpoints.

### Why We Built It
- To protect costly LLM and data endpoints.
- To avoid exposing private API behavior during deployment.
- To keep deployment health checks publicly reachable.
- To prove the containerized backend can actually start and serve health/readiness endpoints.
- To keep `/health` and documentation aligned with the active project version.
- To keep interactive API docs available in development but optionally disabled in production.
- To fail closed when authentication is not configured.
- To give API clients one predictable error contract.
- To prevent internal exception details from leaking in responses.
- To make requests traceable across client responses and future logs.
- To make each API request easier to debug during deployment.
- To allow browser clients safely without using wildcard CORS in production.
- To reduce accidental loops and basic abuse on costly endpoints.

### Tests Performed
- Ran the full test suite after auth changes.
- Ran the full test suite after global exception handling.
- Ran the full test suite after request ID middleware.
- Ran the full test suite after structured request logging.
- Ran the full test suite after CORS configuration.
- Ran the full test suite after rate limiting.
- Built Docker image `insightagent:v6-verify`.
- Ran a temporary container on host port `18000`.
- Verified `/health` returned `ok`.
- Verified `/ready` returned `ready`.
- Ran the full suite after version/config cleanup.
- Ran the full suite after docs exposure configuration.
- Current suite status: `149 passed`.

### What I Learned
- Authentication can be centralized as a FastAPI dependency.
- Router-level dependencies are useful when an entire endpoint group should be protected.
- Health/readiness endpoints usually stay public for infrastructure checks.
- Missing auth configuration should be treated as a deployment error, not as permission to expose the API.
- FastAPI exception handlers can preserve custom route errors while standardizing the response shape.
- Unexpected errors should be logged internally and returned as safe generic API errors.
- Request IDs are a small feature that make debugging much easier once logs and metrics grow.
- Structured logs can start simple and grow later into a fuller observability layer.
- CORS should be environment-aware because development and production have different safety needs.
- In-memory rate limiting is enough for local V6 learning, while Redis or a gateway would be better for multi-instance production.
- Docker verification should test the running container, not only whether the Dockerfile exists.
- Deployment work can be split from backend hardening when cloud setup would distract from local correctness.
- `/docs` exposure should be a deliberate environment decision, not an accidental default.

### Interview Explanation
- In V6, I hardened the backend for deployment-style use. I aligned app version reporting to V6, added readiness checks, verified Docker runtime support, environment-aware CORS, configurable API docs exposure, API key authentication, rate limiting, centralized exception handling, request IDs, and structured request logging. Private routes are protected at the router level, `/health` and `/ready` stay public for deployment checks, and API errors now use one consistent structured response with a traceable request ID.

## V7 Progress

Status: complete.

V7 is implemented and verified through automated end-to-end upload-to-ask RAG tests.

### What We Built
- Added document Q&A schema contracts.
- Added source citation schema.
- Added document upload guardrail config.
- Added `POST /documents/upload`.
- Added document metadata table and registry service.
- Added safe raw document persistence.
- Added text extraction service for TXT, Markdown, and PDF files.
- Added text cleaning and deterministic document chunking.
- Added document chunk metadata with document ID, filename, chunk index, chunk ID, and optional page.
- Added deterministic local embedding generation.
- Added SQLite-backed chunk/vector storage.
- Added semantic retrieval over indexed document chunks.
- Added retrieval trace metadata with top-k, similarity threshold, candidate count, and scored chunks.
- Added grounded document answer prompt builder.
- Added citation builder and weak-context fallback.
- Added service-level grounded document answer response generation.
- Added `POST /documents/{document_id}/ask`.
- Added controlled document ask errors for missing documents and answer-service failures.
- Added automatic upload-time document indexing.
- Added controlled document indexing errors.
- Added end-to-end upload-to-ask RAG behavior.
- Added unit tests for document schemas.
- Added integration tests for document upload.
- Added integration tests for document ask.
- Added unit tests for document text extraction and chunking.
- Added unit tests for embedding generation and vector store behavior.
- Added unit tests for semantic retrieval behavior.
- Added unit tests for grounded answer behavior.
- Added end-to-end integration tests for upload-to-ask RAG flow.
- Added V7 documentation files:
  - `docs/versions/v7_document_qa.md`
  - `docs/versions/v7_technical_walkthrough.md`
  - `docs/versions/v7_commit_log.md`

### Why We Built It
- To start RAG with stable API contracts before parsing, chunking, embeddings, and retrieval.
- To make citations part of the response design from the beginning.
- To keep weak-context and grounded-answer behavior explicit before answer generation is implemented.
- To create the document lifecycle entrypoint before text extraction and indexing.
- To convert stored documents into text before chunking and retrieval.
- To convert extracted text into citation-ready chunks before embeddings and retrieval.
- To persist chunk vectors locally before adding semantic retrieval and answer generation.
- To retrieve evidence chunks before allowing the backend to generate grounded answers.
- To convert retrieval evidence into citations and safe answer responses before exposing a public ask endpoint.
- To expose the document Q&A flow through a protected API endpoint.
- To make uploaded documents immediately searchable and askable.

### Tests Performed
- Added unit tests for document schemas.
- Added integration tests for upload success and failure paths.
- Added unit tests for document text extraction.
- Added unit tests for document chunking behavior and invalid settings.
- Added unit tests for local embedding and vector store behavior.
- Added unit tests for semantic retrieval ranking, thresholding, and validation.
- Added unit tests for grounded prompts, citations, answer responses, and weak-context fallback.
- Added integration tests for successful document ask, weak context, missing documents, and answer errors.
- Added unit tests for document indexing service.
- Added end-to-end integration tests for upload-to-ask RAG flow.
- Full suite status after upload-time indexing: `207 passed`.

### What I Learned
- RAG systems need source/citation contracts early, not as an afterthought.
- Response schemas help define what “grounded answer” means before model logic is added.
- Upload and metadata persistence should be stable before parsing/chunking logic is introduced.
- Text extraction needs controlled failure behavior because unreadable or empty documents are common in real RAG systems.
- Chunking needs deterministic output and metadata because retrieval and citations depend on stable source units.
- A local deterministic embedding layer is useful for building and testing retrieval plumbing without depending on external embedding APIs.
- Vector storage needs replacement behavior so a document can be safely re-indexed.
- Retrieval should expose trace metadata so answer quality can be debugged before the LLM generation step.
- Similarity thresholds are the basis for weak-context fallback.
- Citations should be built from backend retrieval metadata, not invented by the answer layer.
- Weak-context fallback should happen before any confident answer is returned.
- Endpoint wiring should preserve weak-context fallback as a valid response, not an exception.
- Upload-time indexing is what turns document upload from storage into a usable RAG workflow.

### Interview Explanation
- In V7, I started the document Q&A layer by defining contracts, adding the upload lifecycle, implementing text extraction, deterministic chunking, local embeddings, vector persistence, semantic retrieval, grounded answer generation, the public document ask endpoint, and automatic upload-time indexing. I added schemas for document uploads, document questions, source citations, grounded answer responses, document chunks, and retrieval results, implemented safe raw document upload persistence with SQLite metadata, added extraction paths for TXT, Markdown, and PDF files, split cleaned text into overlapping metadata-rich chunks, generated deterministic local embeddings, stored vectors in SQLite, retrieved ranked evidence chunks with similarity scores, built citations from retrieved chunks, added weak-context fallback so unsupported questions do not produce confident answers, exposed the flow through `POST /documents/{document_id}/ask`, and made upload-to-ask work end-to-end in automated tests.

## V8 Progress

Status: complete.

### What We Built
- Updated app version reporting to V8.
- Added `evals/evaluation_dataset.jsonl`.
- Added initial evaluation cases for chat, structured output, tool calling, CSV analysis, RAG, and insufficient-context RAG.
- Added `scripts/run_eval.py`.
- Added setup upload support for dataset and document evaluation cases.
- Added basic status/shape scoring.
- Added rule-based scoring for relevance, tool correctness, CSV intent, citation presence, citation accuracy, groundedness, and insufficient-context safety.
- Added failure category summaries.
- Added regression comparison against previous eval results.
- Added in-process eval execution against FastAPI `TestClient`.
- Added optional token/cost usage metadata in eval results.
- Added README documentation for local eval execution, result structure, comparison workflow, and current coverage.
- Closed V8 with checklist mapping, limitations, and completion notes.
- Added latency capture.
- Added JSON result output under `evals/results/`.
- Added unit tests for eval case loading, validation, scoring, and summary generation.
- Added an integration test proving CSV and RAG eval cases can run end-to-end through the evaluator.
- Added V8 documentation files:
  - `docs/versions/v8_evaluation_layer.md`
  - `docs/versions/v8_technical_walkthrough.md`
  - `docs/versions/v8_commit_log.md`

### Why We Built It
- To make project behavior measurable instead of only manually checked.
- To prepare repeatable evaluation runs across chat, tools, CSV, and RAG.
- To create a dataset format that can grow with new cases.
- To build a runner foundation before adding advanced scoring.
- To make failures easier to debug by categorizing scoring failures.
- To detect pass-rate changes and newly failing cases across eval runs.
- To prove upload-dependent eval cases can execute against the real API in automated tests.
- To add deterministic answer-quality checks before introducing model-assisted evaluation.
- To make RAG citation failures more specific than simple source presence.
- To make evaluation usable from the README without reading the runner internals.
- To track token/cost metadata when endpoints expose it without inventing estimates when unavailable.
- To close the evaluation version honestly before moving into observability.

### Tests Performed
- Added unit tests for the eval runner foundation.
- Added unit tests for scoring rules and failure categories.
- Added unit tests for relevance and groundedness scoring.
- Added unit tests for citation accuracy, missing citation failures, and unsupported confident/cited answer failures.
- Added unit tests for nested and top-level token/cost usage metadata extraction.
- Added unit tests for regression comparison behavior.
- Added in-process integration coverage for CSV and RAG eval execution.
- Documented the evaluation workflow and current results in README/docs.
- Completed V8 closeout documentation.
- Full suite status at V8 closeout: `232 passed`.

### What I Learned
- Evaluation needs a stable dataset format before scoring gets sophisticated.
- Setup steps are necessary for CSV and RAG cases because those flows depend on uploaded resources.
- Even simple status/shape scoring is useful as a first regression signal.
- Rule-based scoring can catch important regressions before introducing model-assisted evaluation.
- Comparing current and previous result files helps separate new regressions from known failures.
- Testing the runner against FastAPI `TestClient` catches wiring issues that unit-level scoring tests cannot see.
- Basic groundedness can be measured deterministically by checking expected terms against both the answer and reference text.
- Splitting citation presence from citation accuracy makes eval failures easier to diagnose.
- Good evaluation docs need to explain both how to run the tool and how to interpret the result JSON.
- Usage tracking should distinguish unavailable metadata from real zero-token or zero-cost values.
- A version is not complete until docs, tests, checklist mapping, and known limitations are all clear.

### Known Limitations / Deferred
- Full bundled eval execution requires a running API and valid API key.
- LLM-backed cases can vary with provider/model behavior.
- Model-assisted semantic judging is deferred.
- Deployed Cloud Run eval is supported by configurable `--base-url`, but Cloud Run deployment itself remains deferred.

### Interview Explanation
- In V8, I built the evaluation layer by adding a JSONL evaluation dataset, a reusable runner, deterministic scoring rules, regression comparison, optional token/cost metadata, an in-process integration proof, and README-level evaluation workflow documentation. The runner can load and validate cases, call local API endpoints with an API key, upload setup files for CSV and RAG cases, capture latency, extract token/cost usage when endpoint responses expose it, check expected response status and keys, verify answer relevance through expected terms, score tool correctness, check CSV analysis intent, verify RAG citation presence, check deterministic citation accuracy through expected filenames/chunk prefixes/reference terms, check deterministic groundedness against uploaded reference text, validate insufficient-context safety, fail RAG answers without citations, fail unsupported confident/cited answers, save a JSON result summary with failure categories and usage totals, compare current results against previous runs, and run deterministic CSV/RAG eval cases against FastAPI `TestClient` in automated tests. The README explains how to run evals, compare results, and interpret the saved result JSON. V8 is complete with model-assisted judging and Cloud Run execution left as honest future improvements.

## V9 Progress

Status: complete.

### What We Built
- Updated app version reporting to V9.
- Updated `.env.example` to `APP_VERSION=v9`.
- Updated health endpoint test expectation to V9.
- Updated README current version, Docker image examples, health response example, and V9 docs link.
- Fixed exception handler type diagnostics without changing runtime error behavior.
- Enriched request completion logs with request status, endpoint, optional session id, error category, and latency.
- Added agent tool trace logs with request id, tool used, tool status, agent status, and output summary.
- Added a metrics summary script for structured request and agent tool logs.
- Added README observability proof with log shapes, lifecycle example, and metrics summary command.
- Linked eval results to request traces through stable `x-request-id` values and saved trace metadata.
- Added nullable token/cost fields to request completion logs and usage totals to metrics summaries.
- Closed V9 with checklist coverage mapping and future-improvement notes.
- Cleaned up metrics summary typing diagnostics for usage sums and status-code handling.
- Added V9 documentation files:
  - `docs/versions/v9_observability_metrics.md`
  - `docs/versions/v9_technical_walkthrough.md`
  - `docs/versions/v9_commit_log.md`

### Why We Built It
- To create a clean V9 boundary after closing V8.
- To give request tracing, structured logs, metrics, and observability work dedicated docs.
- To avoid mixing observability implementation into the completed evaluation layer.
- To make every request log easier to summarize by success/failure and error category.
- To start tracing the API -> agent -> tool path before building metrics summaries.
- To turn structured logs into reusable request and tool usage metrics.
- To make the observability behavior understandable from the README without reading implementation files.
- To make failed eval cases easier to connect back to runtime request logs.
- To record token/cost data when available without inventing values when unavailable.

### Tests Performed
- Health endpoint test verified V9 version reporting.
- Request ID middleware tests verify enriched request completion logs.
- Error handler tests verified the typing diagnostic fix did not change error behavior.
- Agent endpoint tests verify tool trace log fields.
- Metrics summary tests verify JSON log parsing, request summaries, tool summaries, and output writing.
- Eval runner tests verify stable request id generation and saved trace metadata.
- Eval runner flow tests verify CSV/RAG eval traces through in-process API calls.
- Request middleware tests verify nullable and available usage logging.
- Metrics summary tests verify usage aggregation when token/cost fields exist.
- Focused metrics summary tests verified the post-closeout typing cleanup.
- README/docs were reviewed against the V9 checklist for log format documentation, request lifecycle trace example, and observability proof.
- Full suite status at V9 closeout: `247 passed`.

### What I Learned
- Version boundaries make it easier to explain which capabilities belong to which milestone.
- Observability should be introduced with a clear trace model before adding metrics scripts or log analysis.
- Request logs become much more useful once status and error category are explicit fields.
- Tool metrics need a stable tool trace event before frequency and success-rate summaries can be reliable.
- Metrics scripts are simpler and more reliable when runtime logs use stable event names and fields.
- A request lifecycle example makes observability easier to explain than field lists alone.
- Evaluation results become much more useful when each failed case carries a request id that can be searched in logs.
- Usage observability should distinguish unavailable metadata from real zero values.

### Interview Explanation
- In V9, I built the observability and metrics layer by creating the version boundary, enriched request completion logs, agent tool trace logs, a metrics summary script, README-level observability proof, eval-to-request trace linking, and token/cost summaries where usage data is available. The API logs request id, optional session id, method, endpoint, status code, success/failure status, basic error category, latency, and nullable usage fields for each request. Agent queries emit tool trace logs with request id, tool used, tool status, agent status, and output summary. The metrics script reports request totals, success/failure rate, average latency, endpoint counts, error categories, tool usage, tool success/failure counts, and usage totals when available. Eval results store stable request ids so failed cases can be searched in runtime logs.
