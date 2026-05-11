# V8 - Evaluation Layer

## Version Goal
V8 adds a measurable evaluation layer for InsightAgent.

The target flow is:
- define evaluation cases in JSONL
- call local or deployed API endpoints
- capture responses and latency
- score response shape and later quality dimensions
- save evaluation results
- summarize pass rate and failures

## Current Progress

Status: scoring layer expanding.

V8 now has the evaluation dataset, runner foundation, regression comparison, in-process API proof, and deterministic scoring for format, tool correctness, CSV intent, citations, relevance, and basic groundedness. It does not yet implement token/cost tracking or semantic citation accuracy.

## Evaluation Dataset

Added:
```text
evals/evaluation_dataset.jsonl
```

Initial case coverage:
- basic chat
- structured chat
- tool calling
- CSV analysis
- RAG document Q&A
- insufficient-context RAG case

Each case includes:
- `id`
- `flow`
- `method`
- `endpoint`
- `payload`
- `expected_status`
- `expected_keys`
- `scoring`
- optional setup data for dataset/document upload flows
- tags for filtering and future reporting

## Scoring Rules

Added rule-based scoring metadata per case.

Current checks:
- HTTP status
- format validity through required top-level keys
- response `status` value
- answer relevance through expected answer terms
- expected tool selection
- expected CSV analysis intent
- RAG citation presence
- RAG source filename match
- RAG groundedness through configured terms checked against answer and reference document text
- insufficient-context safety through no returned citations
- failure category output

## Evaluation Runner

Added:
```text
scripts/run_eval.py
```

Current behavior:
- loads JSONL evaluation cases
- validates required case fields
- supports local API base URL
- sends `x-api-key`
- handles dataset/document setup uploads
- calls target endpoints
- can run against an existing in-process test client
- captures latency
- checks expected status code
- checks expected top-level response keys
- runs rule-based scoring checks from case metadata
- returns failure categories per case
- writes JSON results under `evals/results/`
- generates pass/fail summary

Example:
```powershell
.\.venv\Scripts\python scripts\run_eval.py `
  --base-url "http://127.0.0.1:8000" `
  --api-key "your-service-api-key-here"
```

Regression comparison:
```powershell
.\.venv\Scripts\python scripts\run_eval.py `
  --base-url "http://127.0.0.1:8000" `
  --api-key "your-service-api-key-here" `
  --compare-to "evals/results/previous_eval_results.json"
```

Comparison output includes:
- previous pass rate
- current pass rate
- pass-rate delta
- newly failing cases
- newly passing cases
- added cases
- removed cases

## In-Process Integration Proof

Added:
```text
tests/integration/test_eval_runner_flow.py
```

This test runs deterministic CSV and RAG evaluation cases through FastAPI `TestClient`.

It verifies:
- setup uploads create the needed dataset/document ids
- placeholder endpoints are replaced before the ask request
- CSV analysis scoring passes for missing-value intent and tool selection
- CSV relevance scoring passes for expected answer terms
- RAG scoring passes for citation/source presence, relevance, and groundedness
- summary generation reports a clean pass rate
- result saving writes the expected JSON summary

This proves the runner can execute real API flows without starting a separate server during automated tests.

## Deferred On Purpose
Not built in this first V8 chunk:
- token/cost tracking
- semantic citation accuracy beyond filename/source presence

## Testing Status
Added unit tests for:
- JSONL eval case loading
- required-field validation
- format-validity scoring
- tool-correctness scoring
- citation-presence scoring
- relevance scoring
- groundedness scoring
- insufficient-context safety scoring
- analysis-intent scoring
- missing-key failure detection
- pass-rate summary generation
- failure-category summary generation
- previous-result loading
- regression comparison
- new failure/new pass detection
- added/removed case detection
- in-process CSV and RAG eval execution
- eval result saving through an integration test

Latest suite:
```text
226 passed
```

## Interview Explanation
In V8, I started the evaluation layer by adding a JSONL evaluation dataset, a reusable runner, rule-based scoring, regression comparison, and an in-process integration proof. The runner can load cases, validate their structure, call local API endpoints with an API key, run setup uploads for dataset and document flows, capture latency, check response shape, score tool selection, check CSV analysis intent, verify answer relevance through expected terms, verify basic RAG citation presence, check deterministic groundedness against uploaded reference text, detect insufficient-context safety, save a pass-rate summary with failure categories, compare current results against a previous run, and execute deterministic CSV/RAG eval cases through FastAPI `TestClient` in automated tests. This creates the foundation for later semantic citation accuracy and token/cost tracking.
