# V5 - Data Analysis Assistant

## Version Goal
V5 turns InsightAgent into a safe CSV analysis backend.

Instead of free-form code generation, V5 follows a controlled flow:
- upload CSV
- validate + persist metadata
- route natural-language question to a safe allowlisted analysis tool
- return structured answer with analysis trace

## What We Built
- `POST /datasets/upload` for CSV upload.
- Upload guardrails:
  - file extension check
  - max file size check
  - empty CSV check
  - duplicate column check
  - row/column limit checks
  - encoding/parse error handling
- Dataset registry in SQLite (`datasets` table).
- `GET /datasets/{dataset_id}/summary`.
- Dataset question schema + analysis trace schema.
- Intent detection + column detection from natural language.
- Safe pandas tool layer:
  - dataset summary
  - missing value analysis
  - column stats
  - value counts
  - groupby aggregation
- Tool execution orchestrator (allowlisted execution only).
- `POST /datasets/{dataset_id}/ask`.
- Safe fallback for unsupported/ambiguous questions.

## Why This Matters
V5 is where InsightAgent becomes a real data-assistant backend.

The key production decision in V5:
- LLM-style intent routing logic can suggest analysis intent.
- Backend executes only predefined safe tools.
- No arbitrary Python execution (`exec` / `eval`) path exists.

## API Surface Added In V5
- `POST /datasets/upload`
- `GET /datasets/{dataset_id}/summary`
- `POST /datasets/{dataset_id}/ask`

## Example Response Shapes

Upload:
```json
{
  "dataset_id": "ds_123",
  "filename": "people.csv",
  "rows": 100,
  "columns": 8,
  "status": "uploaded"
}
```

Summary:
```json
{
  "dataset_id": "ds_123",
  "rows": 100,
  "columns": 8,
  "column_names": ["age", "fare", "city"],
  "missing_values": {"age": 3, "fare": 0, "city": 1},
  "numeric_columns": ["age", "fare"],
  "categorical_columns": ["city"]
}
```

Ask:
```json
{
  "answer": "The column with the most missing values is age with 3 missing entries.",
  "confidence": "high",
  "dataset_id": "ds_123",
  "tool_used": "missing_value_tool",
  "tool_output_summary": "age has 3 missing values.",
  "analysis_trace": {
    "intent": "missing_value_analysis",
    "tool_used": "missing_value_tool",
    "columns_used": ["age"],
    "operation": "count_nulls"
  },
  "status": "success"
}
```

## Safety and Error Handling
- Unsupported file type -> `DATASET_VALIDATION_ERROR` (`400`)
- Invalid CSV content/shape -> `DATASET_VALIDATION_ERROR` (`400`)
- Dataset not found -> `DATASET_NOT_FOUND` (`404`)
- Storage/DB issues -> `DATASET_STORAGE_ERROR` / `DATASET_DB_ERROR` (`503`)
- Invalid/unsafe analysis request path -> safe failed response or controlled `DATASET_ANALYSIS_ERROR` (`400`)

## Checklist Mapping (V5)
- CSV upload endpoint: done.
- File type/size/empty validation: done.
- Row/column limits: done.
- Duplicate columns + encoding/parse handling: done.
- Dataset metadata storage/registry: done.
- Dataset summary endpoint: done.
- Safe analysis tools: done.
- Intent mapping: done.
- Dataset ask endpoint: done.
- Analysis trace: done.
- Unsupported/ambiguous safe handling: done.
- No arbitrary Python execution path: done.

## Test Coverage Added In V5
- `tests/integration/test_dataset_upload_endpoint.py`
- `tests/integration/test_dataset_summary_endpoint.py`
- `tests/integration/test_dataset_ask_endpoint.py`
- `tests/unit/test_dataset_intent_service.py`
- `tests/unit/test_dataset_analysis_router.py`
- `tests/unit/test_dataset_tools_service.py`
- `tests/unit/test_dataset_execution_service.py`

Latest suite status after V5 closeout:
```text
126 passed
```

## Manual Verification Commands
Upload dataset:
```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/datasets/upload" `
  -Method Post `
  -Form @{ file = Get-Item ".\sample.csv" }
```

Get summary:
```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/datasets/<dataset_id>/summary" `
  -Method Get
```

Ask dataset question:
```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/datasets/<dataset_id>/ask" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"question":"Which column has the most missing values?"}'
```

## Interview Summary
In V5, I implemented a safe natural-language CSV analysis layer. I added upload and dataset registry endpoints, introduced strict CSV validation and metadata persistence, and built a deterministic intent-to-tool pipeline for pandas-based analysis. The `/datasets/{dataset_id}/ask` endpoint now returns structured answers with analysis trace, while unsupported requests and failure paths are handled through controlled responses.
