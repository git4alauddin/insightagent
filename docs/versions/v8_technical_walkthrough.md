# V8 Technical Walkthrough

This document explains the V8 evaluation layer as it grows.

## 1. Design Intent

V8 turns InsightAgent from "features work in tests" into "features can be measured repeatedly."

The evaluation layer should eventually answer:
- did the API return the right shape?
- did the agent choose the right tool?
- did CSV analysis use the right operation?
- did RAG answers cite evidence?
- did unsupported questions avoid confident answers?
- did latency regress?

## 2. Version Alignment

### `app/config.py`
Updated:
- `app_version = "v8"`

### `.env.example`
Updated:
- `APP_VERSION=v8`

### `tests/integration/test_health.py`
Updated expected health version to `v8`.

## 3. Evaluation Dataset

### `evals/evaluation_dataset.jsonl`
The dataset is JSONL so cases can be appended without rewriting one large JSON array.

Initial flows:
- `chat`
- `structured_chat`
- `tool_calling`
- `csv_analysis`
- `rag`

Important fields:
- `id`: stable case identifier
- `flow`: feature area
- `method`: HTTP method
- `endpoint`: endpoint path, with placeholders when setup creates IDs
- `setup`: optional upload setup for datasets/documents
- `payload`: request body
- `expected_status`: expected HTTP status
- `expected_keys`: required top-level response keys
- `tags`: reporting/filtering metadata

## 4. Evaluation Runner

### `scripts/run_eval.py`
Core functions:
- `load_eval_cases(dataset_path)`
- `validate_eval_case(case, line_number)`
- `run_eval_cases(cases, base_url, api_key, timeout_seconds)`
- `run_eval_case(client, case, api_key)`
- `prepare_case(client, case, api_key)`
- `upload_setup_file(...)`
- `score_eval_response(case, status_code, response_body, latency_ms)`
- `build_summary(results)`
- `save_results(results, results_path)`

Current scoring is intentionally simple:
- expected HTTP status must match
- expected top-level keys must exist

This gives us a stable runner before adding subjective or model-assisted scoring.

## 5. Result Output

Default output:
```text
evals/results/latest_eval_results.json
```

The output includes:
- summary total
- passed count
- failed count
- pass rate
- per-case status
- latency
- response body
- missing response keys

`evals/results/` is ignored by Git so local eval runs do not create commit noise.

## 6. Tests Added

### `tests/unit/test_eval_runner.py`
Verifies:
- JSONL cases load correctly
- missing required fields are rejected
- response shape scoring passes when expected keys exist
- response shape scoring fails when expected keys are missing
- summary pass/fail counts and pass rate are correct

## 7. Checklist Mapping
- evaluation dataset JSONL: started
- chat/structured-output test cases: started
- tool-calling test cases: started
- CSV-analysis test cases: started
- RAG test cases: started
- negative/insufficient-context cases: started
- `scripts/run_eval.py`: started
- call local/deployed API from eval runner: local API supported
- capture response: done
- track latency: done
- save evaluation result file: done
- pass-rate summary: basic done
- relevance scoring: pending
- groundedness scoring: pending
- tool correctness scoring: pending
- format validity scoring: basic shape scoring started
- citation accuracy scoring: pending
- token/cost tracking: pending
- failure-category summary: pending
- regression comparison: pending

## 8. Interview Summary
I started V8 by creating the evaluation dataset and runner foundation. Evaluation cases are stored as JSONL, the runner can call the local API with setup uploads for CSV and RAG flows, capture latency and responses, check basic status/shape expectations, and save a result summary. This creates the measurement layer that can later grow into groundedness, citation accuracy, tool correctness, and regression scoring.
