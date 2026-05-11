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

Status: foundation started.

This first V8 chunk creates the evaluation dataset and runner foundation. It does not yet implement full relevance, groundedness, tool-correctness, or citation-accuracy scoring.

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
- optional setup data for dataset/document upload flows
- tags for filtering and future reporting

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
- captures latency
- checks expected status code
- checks expected top-level response keys
- writes JSON results under `evals/results/`
- generates pass/fail summary

Example:
```powershell
.\.venv\Scripts\python scripts\run_eval.py `
  --base-url "http://127.0.0.1:8000" `
  --api-key "your-service-api-key-here"
```

## Deferred On Purpose
Not built in this first V8 chunk:
- relevance scoring
- groundedness scoring
- tool correctness scoring
- citation accuracy scoring
- token/cost tracking
- previous-run regression comparison
- detailed failure categories

## Testing Status
Added unit tests for:
- JSONL eval case loading
- required-field validation
- placeholder response scoring
- missing-key failure detection
- pass-rate summary generation

Latest suite:
```text
213 passed
```

## Interview Explanation
In V8, I started the evaluation layer by adding a JSONL evaluation dataset and a reusable runner. The runner can load cases, validate their structure, call local API endpoints with an API key, run setup uploads for dataset and document flows, capture latency, check response shape, and save a pass-rate summary. This creates the foundation for later quality scoring such as groundedness, citation accuracy, tool correctness, and regression comparison.
