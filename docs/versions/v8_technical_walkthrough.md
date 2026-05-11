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
- `run_eval_cases_with_client(cases, client, api_key)`
- `run_eval_case(client, case, api_key)`
- `prepare_case(client, case, api_key)`
- `upload_setup_file(...)`
- `score_eval_response(case, status_code, response_body, latency_ms)`
- `build_summary(results)`
- `save_results(results, results_path)`

Current scoring is intentionally simple:
- expected HTTP status must match
- expected top-level keys must exist
- optional response `status` must match
- optional `tool_used` must match
- optional CSV `analysis_trace.intent` must match
- optional RAG citations must be present
- optional RAG source filename must match
- optional insufficient-context cases must return no citations

This gives us deterministic rule-based scoring before adding subjective or model-assisted scoring.

## 5. Scoring Rules

### `score_eval_response(...)`
Builds the final per-case result:
- HTTP status
- latency
- pass/fail result
- score breakdown
- failure categories
- raw response body

### `build_score_breakdown(...)`
Runs only the scoring checks requested by each case.

Supported checks:
- `http_status`
- `format_validity`
- `response_status`
- `tool_correctness`
- `analysis_intent`
- `citation_presence`
- `insufficient_context_safety`

### `build_failure_categories(...)`
Returns the failed score names for each case.

This makes eval output easier to debug because failures say what kind of problem happened instead of only returning `passed=false`.

## 6. Regression Comparison

### `load_previous_results(previous_results_path)`
Loads a previously saved JSON result file.

Controlled errors:
- missing previous result file
- invalid JSON

### `compare_eval_results(current_results, previous_output)`
Compares the current run to a previous run.

Comparison output:
- `previous_pass_rate`
- `current_pass_rate`
- `pass_rate_delta`
- `new_failures`
- `new_passes`
- `added_cases`
- `removed_cases`

### CLI
Use:
```powershell
.\.venv\Scripts\python scripts\run_eval.py `
  --api-key "your-service-api-key-here" `
  --compare-to "evals/results/previous_eval_results.json"
```

When comparison is enabled, the saved result file includes a top-level `comparison` object.

## 7. In-Process Integration Proof

### `run_eval_cases_with_client(...)`
Runs evaluation cases with an already-created client.

This keeps the production CLI path and the integration-test path aligned:
```text
CLI creates httpx.Client -> run_eval_cases_with_client(...)
Test creates TestClient -> run_eval_cases_with_client(...)
```

### `tests/integration/test_eval_runner_flow.py`
Verifies the evaluator can drive real API flows without launching a server.

The test covers:
- CSV setup upload
- document setup upload
- endpoint placeholder replacement
- protected endpoint API-key headers
- CSV missing-value ask flow
- RAG grounded ask flow
- scoring and pass-rate summary
- saved result JSON output

## 8. Result Output

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
- score breakdown
- failure categories
- optional regression comparison

`evals/results/` is ignored by Git so local eval runs do not create commit noise.

## 9. Tests Added

### `tests/unit/test_eval_runner.py`
Verifies:
- JSONL cases load correctly
- missing required fields are rejected
- response shape scoring passes when expected keys exist
- response shape scoring fails when expected keys are missing
- tool correctness is checked
- citation presence is checked
- insufficient-context safety is checked
- CSV analysis intent is checked
- summary pass/fail counts and pass rate are correct
- failure category counts are summarized
- previous result files load correctly
- missing previous result file is handled safely
- regression and improvement comparison works
- saved result files can include comparison output

### `tests/integration/test_eval_runner_flow.py`
Verifies:
- the runner executes upload-dependent CSV and RAG cases against FastAPI `TestClient`
- eval scoring passes against real API responses
- result summaries and saved output are generated from integration results

## 10. Checklist Mapping
- evaluation dataset JSONL: started
- chat/structured-output test cases: started
- tool-calling test cases: started
- CSV-analysis test cases: started
- RAG test cases: started
- negative/insufficient-context cases: started
- `scripts/run_eval.py`: started
- call local/deployed API from eval runner: local API supported, in-process API proven
- capture response: done
- track latency: done
- save evaluation result file: done
- pass-rate summary: basic done
- failure-category summary: basic done
- regression comparison note: basic done
- tool correctness scoring: basic done
- format validity scoring: basic done
- citation presence scoring: basic done
- insufficient-context safety scoring: basic done
- relevance scoring: pending
- groundedness scoring: pending
- citation semantic accuracy scoring: pending
- token/cost tracking: pending

## 11. Interview Summary
I started V8 by creating the evaluation dataset, runner foundation, deterministic scoring rules, regression comparison, and in-process integration proof. Evaluation cases are stored as JSONL, the runner can call the local API with setup uploads for CSV and RAG flows, capture latency and responses, check status/shape expectations, verify tool selection, check CSV analysis intent, check basic citation presence, validate insufficient-context safety, save a result summary with failure categories, compare the current run against previous results to identify pass-rate delta/new failures/new passes/added cases/removed cases, and run deterministic CSV/RAG cases against FastAPI `TestClient` during automated tests. This creates the measurement layer that can later grow into groundedness, semantic citation accuracy, and token/cost tracking.
