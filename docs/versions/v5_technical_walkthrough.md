# V5 Technical Walkthrough

This document explains the V5 CSV analysis layer file by file.

## 1. Design Intent
V5 introduces safe dataset analysis with four responsibilities:
1. Validate and persist datasets.
2. Expose dataset inspection APIs.
3. Route natural-language questions to allowlisted analysis tools.
4. Return traceable, structured results.

## 2. Data Contracts

### `app/schemas/dataset.py`
Main models:
- `DatasetUploadResponse`
- `DatasetSummaryResponse`
- `DatasetAskRequest`
- `DatasetAnalysisTrace`
- `DatasetAskResponse`

Key behaviors:
- `DatasetAskRequest.question` trims and rejects blank input.
- `DatasetAskResponse` enforces stable confidence/status and non-blank output fields.

## 3. Dataset Persistence Layer

### `app/db/schema.py`
Adds `datasets` table:
- `dataset_id` (primary key)
- `session_id` (optional)
- `filename`
- `storage_path`
- `row_count`
- `column_count`
- `uploaded_at`

Includes migration-safe column checks via `PRAGMA table_info`.

### `app/services/dataset_registry_service.py`
Core functions:
- `register_dataset_metadata(...)`
- `get_dataset_metadata(dataset_id)`

Error model:
- Wraps SQLite issues as `DatasetRegistryError("Database operation failed.")`.
- Raises explicit not-found error for unknown dataset IDs.

## 4. CSV Validation and Summary Service

### `app/services/dataset_service.py`
Core functions:
- `validate_csv_file(file_name, file_size_bytes)`
- `load_csv_with_checks(temp_path)`
- `build_upload_metadata(...)`
- `build_dataset_summary(...)`

Validation guardrails:
- extension check
- file-size limit
- empty file and empty-data checks
- duplicate column check
- row/column upper bounds
- encoding/parser/read error conversion

## 5. Intent and Routing Layer

### `app/services/dataset_intent_service.py`
Core functions:
- `detect_intent(question)`
- `detect_columns_from_question(question, df_columns)`

Design notes:
- Uses normalized text and token/phrase matching.
- Avoids substring false positives (for example `"min"` inside `"minister"`).
- Outputs controlled intents only.

### `app/services/dataset_analysis_router.py`
Core contract:
- `DatasetRouteDecision`

Core function:
- `build_route_decision(question, df_columns)`

Responsibilities:
- map intent -> tool
- infer operation label
- collect referenced columns
- set confidence heuristics

## 6. Safe Tool Execution Layer

### `app/services/dataset_tools_service.py`
Allowlisted analysis functions:
- `run_dataset_summary`
- `run_missing_value_analysis`
- `run_column_stats`
- `run_value_counts`
- `run_groupby_aggregation`

Safety:
- explicit column existence checks
- numeric-only checks where required
- aggregation allowlist (`mean|sum|count|min|max`)
- controlled failures via `DatasetToolError`

### `app/services/dataset_execution_service.py`
Core function:
- `execute_analysis_tool(dataframe, decision)`

Responsibilities:
- dispatch only known tool names
- reject `none`/unsupported execution path
- convert tool errors into `DatasetExecutionError`
- return:
  - `tool_used`
  - `tool_output`
  - `tool_output_summary`
  - `analysis_trace`

## 7. Answer Composition Layer

### `app/services/dataset_answer_service.py`
Core function:
- `build_dataset_ask_response(...)`

Responsibilities:
- produce stable API response from execution output
- build concise deterministic answer text by intent
- return `DatasetAskResponse` with `analysis_trace`

## 8. API Layer

### `app/api/routes_datasets.py`
Endpoints:
- `POST /datasets/upload`
- `GET /datasets/{dataset_id}/summary`
- `POST /datasets/{dataset_id}/ask`

Flow highlights:
- shared dataset path resolution and existence checks
- controlled error mapping:
  - `DATASET_VALIDATION_ERROR` (`400`)
  - `DATASET_NOT_FOUND` (`404`)
  - `DATASET_ANALYSIS_ERROR` (`400`)
  - `DATASET_DB_ERROR` / `DATASET_STORAGE_ERROR` (`503`)
- safe fallback response for unsupported/ambiguous ask queries

### `app/main.py`
- includes dataset router.

## 9. Tests Added/Extended

### Unit
- `tests/unit/test_dataset_intent_service.py`
- `tests/unit/test_dataset_analysis_router.py`
- `tests/unit/test_dataset_tools_service.py`
- `tests/unit/test_dataset_execution_service.py`

### Integration
- `tests/integration/test_dataset_upload_endpoint.py`
- `tests/integration/test_dataset_summary_endpoint.py`
- `tests/integration/test_dataset_ask_endpoint.py`

What these prove:
- upload validation and metadata persistence
- summary retrieval from stored file
- question routing and safe tool execution
- unsupported-query safe fallback
- controlled error behavior for not-found and analysis failures

## 10. Checklist Mapping (V5)
- upload + validation: done
- dataset registry + metadata: done
- summary endpoint: done
- missing/stats/value-count/groupby tools: done
- natural-language intent routing: done
- dataset ask endpoint: done
- analysis trace + safe fallback: done
- no arbitrary code execution path: done

## 11. Interview Summary
In V5, I built a secure CSV analysis architecture with separated layers for validation, metadata persistence, intent routing, safe tool execution, and structured answer generation. The backend now supports upload, summary, and question-answering over datasets while preserving strict execution control and predictable error contracts.
