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

Status: complete.

V8 now has the evaluation dataset, runner foundation, regression comparison, in-process API proof, optional token/cost metadata, and deterministic scoring for format, tool correctness, CSV intent, citation presence, citation accuracy, relevance, basic groundedness, and insufficient-context safety. The version is complete with model-assisted semantic judging intentionally deferred.

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
- RAG citation accuracy through expected filenames, chunk id prefixes, and citation terms
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
- captures token/cost metadata when response usage is available
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

## How To Evaluate Locally

1. Start the API:
```powershell
uvicorn app.main:app --reload
```

2. Run the eval dataset:
```powershell
.\.venv\Scripts\python scripts\run_eval.py `
  --base-url "http://127.0.0.1:8000" `
  --api-key "your-service-api-key-here"
```

3. Review the result file:
```text
evals/results/latest_eval_results.json
```

4. Compare against a previous result file:
```powershell
.\.venv\Scripts\python scripts\run_eval.py `
  --base-url "http://127.0.0.1:8000" `
  --api-key "your-service-api-key-here" `
  --compare-to "evals/results/previous_eval_results.json"
```

## Result Structure

Saved eval output includes:
- summary total, passed, failed, and pass rate
- summary failure category counts
- summary usage availability, token totals, and cost totals when present
- per-case id, flow, status code, expected status, and latency
- per-case pass/fail result
- per-case score breakdown
- per-case failure categories
- per-case usage metadata
- raw response body for debugging
- optional comparison output

Local results are written under `evals/results/`, which is ignored by Git.

## Current Coverage

The V8 dataset covers:
- chat
- structured output
- tool calling
- CSV analysis
- RAG document Q&A
- negative insufficient-context RAG behavior

## Token And Cost Metadata

Each eval result includes:
```json
{
  "usage": {
    "available": false,
    "input_tokens": null,
    "output_tokens": null,
    "total_tokens": null,
    "estimated_cost_usd": null
  }
}
```

When an endpoint response includes usage metadata, the runner extracts common shapes such as:
- `usage.prompt_tokens`
- `usage.completion_tokens`
- `usage.total_tokens`
- `usage.estimated_cost_usd`
- top-level `input_tokens`, `output_tokens`, `total_tokens`, or `cost_usd`

If usage is unavailable, the runner records `available: false` instead of estimating or inventing values.

The current automated test suite verifies:
- eval case loading
- scoring rules
- result saving
- regression comparison
- in-process CSV/RAG eval execution
- missing citation failure detection
- unsupported confident/cited answer failure detection

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
- RAG scoring passes for citation presence, citation accuracy, relevance, and groundedness
- summary generation reports a clean pass rate
- result saving writes the expected JSON summary

This proves the runner can execute real API flows without starting a separate server during automated tests.

## V8 Closeout

V8 is complete for the planned evaluation layer scope.

Completed:
- evaluation dataset in JSONL
- eval runner script
- local API eval execution
- setup uploads for CSV/RAG eval cases
- response capture
- latency tracking
- token/cost metadata tracking when response usage is available
- result saving
- pass/fail per case
- pass-rate summary
- failure-category summary
- regression comparison
- format validity scoring
- relevance scoring
- groundedness scoring
- tool correctness scoring
- CSV intent scoring
- citation presence scoring
- citation accuracy scoring
- insufficient-context safety checks
- tests for missing citations
- tests for unsupported confident/cited answers
- README/docs evaluation workflow

Honest limitations:
- Full bundled eval execution requires a running API and valid API key.
- LLM-backed chat/structured/tool cases may vary depending on provider/model behavior.
- The automated integration proof focuses on deterministic upload-dependent CSV/RAG eval execution.
- Model-assisted semantic judging is deferred; V8 uses deterministic rule-based checks.
- Deployed API evaluation is supported by `--base-url`. Cloud Run deployment was deferred during V8 and completed later in the dedicated Deployment pass.

## Testing Status
Added unit tests for:
- JSONL eval case loading
- required-field validation
- format-validity scoring
- tool-correctness scoring
- citation-presence scoring
- citation-accuracy scoring
- relevance scoring
- groundedness scoring
- insufficient-context safety scoring
- missing-citation failure detection
- unsupported confident/cited answer failure detection
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
- token/cost metadata extraction when available
- unavailable usage tracking when token/cost data is absent

Latest suite:
```text
232 passed
```

Current documented eval status:
- eval runner executes the bundled dataset against a running API
- in-process integration test proves upload-dependent CSV/RAG eval execution
- results are saved as JSON
- pass/fail is generated per case
- pass-rate and failure-category summaries are generated
- token/cost metadata is tracked when available
- evaluation covers chat, tool, CSV, and RAG flows
- evaluation results are documented in README/docs

## Interview Explanation
In V8, I built the evaluation layer by adding a JSONL evaluation dataset, a reusable runner, rule-based scoring, regression comparison, optional token/cost metadata, and an in-process integration proof. The runner can load cases, validate their structure, call local API endpoints with an API key, run setup uploads for dataset and document flows, capture latency, extract token/cost usage when endpoints provide it, check response shape, score tool selection, check CSV analysis intent, verify answer relevance through expected terms, verify RAG citation presence, check citation accuracy through expected filenames/chunk prefixes/reference terms, check deterministic groundedness against uploaded reference text, detect insufficient-context safety, save a pass-rate summary with failure categories, compare current results against a previous run, and execute deterministic CSV/RAG eval cases through FastAPI `TestClient` in automated tests. V8 is intentionally rule-based and leaves model-assisted semantic judging for a future improvement.
