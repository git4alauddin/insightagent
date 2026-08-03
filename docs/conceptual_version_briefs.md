# InsightAgent Conceptual Version Briefs

This guide is for owning the project conceptually before reading the deeper docs. Each version explains what problem was solved, what concept was introduced, and how to describe it clearly in an interview.

## V1: FastAPI + Basic LLM Chat API

V1 turns the idea into a real backend.

The goal was simple: expose an LLM through an API. Instead of calling the model from a script, the project creates a FastAPI app with:

- `/health` to check the backend is running
- `/chat` to send a user message to the LLM and return an answer

The main concept introduced here is layered responsibility:

```text
HTTP route -> Pydantic validation -> service layer -> LLM provider
```

FastAPI handles the web request. Pydantic checks the request and response shape. The LLM service talks to the Groq/OpenAI-compatible API. Config values come from `.env`.

The important design choice: the route does not directly manage the LLM provider. It delegates that to a service. That keeps the app testable and makes later versions easier to add.

Interview explanation:

> In V1, I built the basic FastAPI backend with health and chat endpoints. I used Pydantic for typed request/response contracts, environment-based config for provider settings, and a separate LLM service so HTTP logic stayed separate from model-provider logic.

Useful action check:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method Get
```

In the current V10 app, `/chat` requires `x-api-key` because auth was added later in V6.

## V2: Prompting + Structured Output

V2 makes the LLM response predictable.

The problem was that normal LLM text is flexible but unreliable for backend APIs. A user can ask a question, but the backend needs a stable response shape that clients and tests can trust.

The main concept introduced here is validated structured output:

```text
user message -> prompt asks for JSON -> parse JSON -> validate with Pydantic -> return structured response
```

The model is asked to return fields like `answer`, `confidence`, `reasoning_summary`, `next_action`, `prompt_version`, and `status`. The backend does not blindly trust that output. It parses and validates it. If the model output is invalid, the service retries once, then returns a safe fallback response.

Why this matters: the LLM is treated like an external system. Its output must be validated before becoming an API response.

Interview explanation:

> In V2, I moved from free-form text to structured LLM output. The backend prompts the model for JSON, validates it with Pydantic, retries on invalid output, and falls back safely if validation still fails. This makes the API more predictable and testable.

Useful action check:

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/chat/structured" `
  -Method Post `
  -Headers @{ "x-api-key" = "your-service-api-key" } `
  -ContentType "application/json" `
  -Body '{"message":"How should I handle missing values in a dataset?"}'
```

## V3: Tool Calling + Agentic Layer

V3 adds controlled tool use.

The problem was that an LLM alone is not always the right executor. For calculations, dates, summaries, or file metadata, the backend should use deterministic tools instead of hoping the model answers correctly.

The main concept introduced here is backend-enforced tool orchestration:

```text
user message -> LLM proposes tool decision -> backend validates decision -> registry resolves tool -> tool executes -> traceable response
```

The LLM does not execute code directly. It only proposes a tool name and tool input. The backend checks that the tool is allowlisted, validates the input, and executes the tool itself.

Why this matters: it gives the project an agentic workflow while keeping execution controlled and explainable.

Interview explanation:

> In V3, I added an agent layer where the LLM decides whether a tool is needed, but the backend remains in control. Tool decisions are parsed and validated, tools are resolved from an allowlisted registry, and responses include trace fields like tool used, input, output summary, and status.

Useful action check:

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/agent/query" `
  -Method Post `
  -Headers @{ "x-api-key" = "your-service-api-key" } `
  -ContentType "application/json" `
  -Body '{"message":"What is 25 * 18?"}'
```

## V4: Memory + Context Handling

V4 gives the chat system memory.

The problem was that basic chat is stateless. Each request is independent, so the backend cannot remember previous messages unless it stores conversation history.

The main concept introduced here is bounded session memory:

```text
session created -> messages stored in SQLite -> recent context loaded -> LLM answers with context -> new messages saved
```

SQLite stores sessions and messages. The memory chat service loads recent messages for a session and sends bounded context to the LLM. It does not send unlimited history, because that would increase cost, latency, and risk.

Why this matters: memory is not just "remember everything." It needs persistence, retrieval, limits, and predictable behavior.

Interview explanation:

> In V4, I added SQLite-backed sessions and memory-aware chat. The backend stores conversation messages, retrieves recent bounded context, and uses that context for replies. This made the app support multi-turn conversations while keeping cost and context size controlled.

Useful action check:

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/sessions" `
  -Method Post `
  -Headers @{ "x-api-key" = "your-service-api-key" } `
  -ContentType "application/json" `
  -Body '{"title":"learning session"}'
```

## V5: Data Analysis Assistant

V5 turns the project into a data-analysis backend.

The problem was that users may upload CSV files and ask natural-language questions. But allowing arbitrary code execution would be unsafe.

The main concept introduced here is safe, allowlisted dataset analysis:

```text
CSV upload -> validate file -> store file -> save metadata -> route question to safe analysis operation -> return answer and trace
```

The backend validates file type, size, row count, column count, and content. Questions are routed to supported analysis paths such as summary, missing values, column statistics, value counts, and groupby aggregation.

The LLM does not run pandas code directly. The backend chooses from controlled operations.

Interview explanation:

> In V5, I added CSV upload and safe dataset question answering. The backend validates and stores CSVs, records metadata in SQLite, detects the user's analysis intent, and executes only allowlisted pandas-backed operations. This avoids arbitrary code execution while still supporting useful data analysis.

Useful action check:

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/datasets/<dataset_id>/summary" `
  -Method Get `
  -Headers @{ "x-api-key" = "your-service-api-key" }
```

## V6: Deployment + Backend Maturity

V6 hardens the backend.

The problem was that a demo API needs more than feature endpoints. It needs protection, readiness, consistent errors, deployment behavior, and operational basics.

The main concepts introduced here are backend maturity and production-style API concerns:

```text
request -> CORS/auth/rate limit -> route -> service -> standardized response/error -> request id/log
```

V6 adds API key authentication, CORS settings, rate limiting, readiness checks, global error handlers, request IDs, Docker support, and environment-aware config.

Why this matters: these are cross-cutting concerns. They are not specific to chat, tools, datasets, or documents, but every real backend needs them.

Interview explanation:

> In V6, I hardened the backend with API key auth, CORS, rate limiting, readiness checks, Docker runtime support, global error handling, and request IDs. This moved the project from feature-building toward production-style backend behavior.

Useful action check:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/ready" -Method Get
```

## V7: RAG Document Q&A

V7 adds document question answering with citations.

The problem was that users may want to ask questions about uploaded documents. The LLM should answer from the document, not from general knowledge.

The main concept introduced here is retrieval-augmented generation:

```text
upload document -> extract text -> chunk text -> embed chunks -> store vectors -> retrieve relevant chunks -> answer with citations
```

The backend supports document upload, text extraction, chunking, deterministic local embeddings, SQLite-backed vector storage, semantic retrieval, and grounded answers.

Why this matters: the answer is tied to retrieved evidence. If retrieval is weak, the system can return an insufficient-context response instead of pretending to know.

Interview explanation:

> In V7, I added document RAG. Uploaded documents are extracted, chunked, embedded, and stored. When a user asks a question, the backend retrieves relevant chunks and generates a grounded answer with citations. This keeps document answers evidence-based instead of relying only on model memory.

Useful action check:

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/documents/<document_id>/ask" `
  -Method Post `
  -Headers @{ "x-api-key" = "your-service-api-key" } `
  -ContentType "application/json" `
  -Body '{"question":"What is this document mainly about?"}'
```

## V8: Evaluation Layer

V8 makes behavior measurable.

The problem was that AI systems can change behavior over time. Manual testing is not enough to know whether quality improved or regressed.

The main concept introduced here is repeatable evaluation:

```text
eval dataset -> run cases -> capture responses -> score results -> compare with previous run
```

The project adds a JSONL evaluation dataset, an eval runner, deterministic scoring rules, latency tracking, failure categories, usage metadata when available, and regression comparison.

Why this matters: evaluation gives a way to discuss model quality with evidence instead of vibes.

Interview explanation:

> In V8, I added an evaluation layer with a JSONL dataset, a runner, deterministic scoring, latency capture, and regression comparison. This helped turn AI behavior into something measurable and repeatable.

Useful action check:

```powershell
python scripts/run_eval.py --mode local
```

## V9: Observability + Metrics

V9 makes runtime behavior easier to inspect.

The problem was that once the app has many flows, it becomes hard to debug what happened during a request.

The main concept introduced here is structured observability:

```text
request id -> request log -> optional session id -> tool trace -> metrics summary
```

Every request gets an `x-request-id`. Completion logs include endpoint, method, status code, status, error category, latency, session id, and usage fields when available. Agent requests also emit tool trace logs.

Why this matters: observability connects API behavior to debugging, metrics, and evaluation traces.

Interview explanation:

> In V9, I added request tracing and metrics. Each request gets a request id, structured completion logs capture latency and error category, agent tool logs capture tool usage and status, and a metrics script summarizes request, tool, and usage data from logs.

Useful action check:

```powershell
python scripts/metrics_summary.py --logs logs/app.log
```

## V10: Portfolio Packaging Layer

V10 turns the completed backend into a portfolio case study.

The problem was that a strong project still needs to be easy for others to understand. Recruiters and engineers should be able to quickly see what was built, why it matters, and how it works.

The main concept introduced here is technical communication:

```text
working backend -> README -> architecture docs -> API examples -> trade-offs -> portfolio status
```

V10 adds/refines the README, architecture docs, API examples, trade-offs, portfolio checklist, project report, and final cleanup.

Why this matters: owning a project is not only writing code. It is also being able to explain design, scope, limitations, and future improvements.

Interview explanation:

> In V10, I packaged InsightAgent as a portfolio-ready backend case study. I documented the architecture, API examples, trade-offs, current status, evaluation, observability, and deployment path so both recruiters and engineers can understand the project quickly.

Useful action check:

```powershell
pytest
```

## Deployment Pass: Cloud Run Deployment

The deployment pass proves the backend can run outside the local machine.

The problem was taking a local FastAPI project and making it available as a hosted API.

The main concept introduced here is containerized deployment:

```text
FastAPI app -> Docker image -> Artifact Registry -> Cloud Run -> public HTTPS API
```

Docker packages the app. Artifact Registry stores the image. Secret Manager stores sensitive keys. Cloud Run hosts the service and injects runtime environment variables like `PORT`.

Why this matters: it shows the project is not just local code. It can be built, configured, deployed, and tested in a cloud runtime.

Interview explanation:

> After V10, I deployed the backend to Cloud Run using Docker, Artifact Registry, Secret Manager, and production environment settings. This proved the API could run as a real hosted service while keeping secrets out of the repo.

Useful action check:

```powershell
Invoke-RestMethod -Uri "https://insightagent-1089133393572.us-central1.run.app/health" -Method Get
```
