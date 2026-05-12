# InsightAgent API Examples

This document gives a quick API reference for local demos, README links, and interview walkthroughs.

## Authentication

Public endpoints:
- `GET /health`
- `GET /ready`

Private endpoints require:

```text
x-api-key: <API_KEY>
```

PowerShell setup:

```powershell
$baseUrl = "http://127.0.0.1:8000"
$headers = @{ "x-api-key" = "your-service-api-key-here" }
```

## Endpoint Table

| Method | Endpoint | Purpose | Auth |
| --- | --- | --- | --- |
| GET | `/health` | Basic service status. | Public |
| GET | `/ready` | Dependency readiness checks. | Public |
| POST | `/chat` | Free-form LLM chat. | Required |
| POST | `/chat/structured` | Structured JSON LLM answer. | Required |
| POST | `/chat/memory` | Session-aware chat. | Required |
| POST | `/agent/query` | Agent tool selection and execution. | Required |
| POST | `/sessions` | Create a memory session. | Required |
| GET | `/sessions/{session_id}/messages` | Fetch recent session messages. | Required |
| POST | `/datasets/upload` | Upload and register a CSV dataset. | Required |
| GET | `/datasets/{dataset_id}/summary` | Summarize a stored dataset. | Required |
| POST | `/datasets/{dataset_id}/ask` | Ask a safe natural-language dataset question. | Required |
| POST | `/documents/upload` | Upload, extract, chunk, embed, and index a document. | Required |
| POST | `/documents/{document_id}/ask` | Ask a grounded document question with citations. | Required |

## Health

```powershell
Invoke-RestMethod -Uri "$baseUrl/health" -Method Get
```

Example response:

```json
{
  "status": "ok",
  "service": "InsightAgent",
  "version": "v10"
}
```

## Readiness

```powershell
Invoke-RestMethod -Uri "$baseUrl/ready" -Method Get
```

Example response:

```json
{
  "status": "ready",
  "checks": [
    {
      "name": "llm_config",
      "status": "ready",
      "detail": "LLM API key is configured."
    }
  ]
}
```

If a dependency is unavailable, `/ready` returns HTTP `503`.

## Chat

```powershell
Invoke-RestMethod `
  -Uri "$baseUrl/chat" `
  -Method Post `
  -Headers $headers `
  -ContentType "application/json" `
  -Body '{"message":"Explain what a CSV file is in one sentence."}'
```

Example response shape:

```json
{
  "answer": "A CSV file stores tabular data as comma-separated text.",
  "model": "llama-3.1-8b-instant",
  "latency_ms": 842.12,
  "status": "success"
}
```

## Structured Chat

```powershell
Invoke-RestMethod `
  -Uri "$baseUrl/chat/structured" `
  -Method Post `
  -Headers $headers `
  -ContentType "application/json" `
  -Body '{"message":"How should I handle missing values?"}'
```

Example response shape:

```json
{
  "answer": "Start by measuring where values are missing and whether the pattern is meaningful.",
  "confidence": "medium",
  "reasoning_summary": "The answer gives a safe high-level data-cleaning step.",
  "next_action": "Run missing-value analysis on the dataset.",
  "prompt_version": "v2.1",
  "status": "success"
}
```

## Agent Query

```powershell
Invoke-RestMethod `
  -Uri "$baseUrl/agent/query" `
  -Method Post `
  -Headers $headers `
  -ContentType "application/json" `
  -Body '{"message":"What is 25 * 18?"}'
```

Example response shape:

```json
{
  "answer": "450",
  "confidence": "high",
  "tool_used": "calculator",
  "tool_input": {
    "expression": "25 * 18"
  },
  "tool_output_summary": "450",
  "tool_status": "success",
  "status": "success"
}
```

## Memory Chat

```powershell
Invoke-RestMethod `
  -Uri "$baseUrl/chat/memory" `
  -Method Post `
  -Headers $headers `
  -ContentType "application/json" `
  -Body '{"message":"Remember that my project is InsightAgent."}'
```

Example response shape:

```json
{
  "session_id": "sess_abc123",
  "answer": "Got it.",
  "context_message_count": 0,
  "status": "success"
}
```

## Sessions

Create a session:

```powershell
Invoke-RestMethod `
  -Uri "$baseUrl/sessions" `
  -Method Post `
  -Headers $headers
```

Fetch messages:

```powershell
Invoke-RestMethod `
  -Uri "$baseUrl/sessions/<session_id>/messages" `
  -Method Get `
  -Headers $headers
```

## CSV Dataset Upload

```powershell
Invoke-RestMethod `
  -Uri "$baseUrl/datasets/upload" `
  -Method Post `
  -Headers $headers `
  -Form @{ file = Get-Item ".\sample.csv" }
```

Example response shape:

```json
{
  "dataset_id": "ds_abc123",
  "filename": "sample.csv",
  "rows": 100,
  "columns": 5,
  "status": "uploaded"
}
```

## Dataset Summary

```powershell
Invoke-RestMethod `
  -Uri "$baseUrl/datasets/<dataset_id>/summary" `
  -Method Get `
  -Headers $headers
```

Example response shape:

```json
{
  "dataset_id": "ds_abc123",
  "rows": 100,
  "columns": 5,
  "column_names": ["name", "age", "city"],
  "missing_values": {
    "city": 3
  },
  "numeric_columns": ["age"],
  "categorical_columns": ["name", "city"]
}
```

## Dataset Question

```powershell
Invoke-RestMethod `
  -Uri "$baseUrl/datasets/<dataset_id>/ask" `
  -Method Post `
  -Headers $headers `
  -ContentType "application/json" `
  -Body '{"question":"Which column has the most missing values?"}'
```

Example response shape:

```json
{
  "answer": "The city column has the most missing values.",
  "confidence": "high",
  "dataset_id": "ds_abc123",
  "tool_used": "missing_value_tool",
  "tool_output_summary": "city: 3 missing values",
  "analysis_trace": {
    "intent": "missing_value_analysis",
    "tool_used": "missing_value_tool",
    "columns_used": ["city"],
    "operation": "missing_values"
  },
  "status": "success"
}
```

## Document Upload

```powershell
Invoke-RestMethod `
  -Uri "$baseUrl/documents/upload" `
  -Method Post `
  -Headers $headers `
  -Form @{ file = Get-Item ".\policy.txt" }
```

Example response shape:

```json
{
  "document_id": "doc_abc123",
  "filename": "policy.txt",
  "status": "indexed"
}
```

## Document Question

```powershell
Invoke-RestMethod `
  -Uri "$baseUrl/documents/<document_id>/ask" `
  -Method Post `
  -Headers $headers `
  -ContentType "application/json" `
  -Body '{"question":"What is the refund policy?"}'
```

Example response shape:

```json
{
  "answer": "Refunds are available within 7 days.",
  "confidence": "high",
  "document_id": "doc_abc123",
  "sources": [
    {
      "filename": "policy.txt",
      "chunk_id": "doc_abc123_chunk_0",
      "similarity_score": 0.92,
      "page": null
    }
  ],
  "status": "success"
}
```

Weak context response shape:

```json
{
  "answer": "I do not have enough context to answer that from the uploaded document.",
  "confidence": "low",
  "document_id": "doc_abc123",
  "sources": [],
  "status": "insufficient_context"
}
```

## Common Error Shape

Errors use a consistent response shape:

```json
{
  "error": {
    "code": "INVALID_INPUT",
    "message": "Request validation failed.",
    "request_id": "req_abc123"
  }
}
```

Common cases:
- `401 AUTHENTICATION_REQUIRED`: missing API key
- `403 INVALID_API_KEY`: invalid API key
- `422 INVALID_INPUT`: request validation failed
- `429 RATE_LIMIT_EXCEEDED`: request rate limit exceeded
- `503 LLM_SERVICE_ERROR`: LLM provider unavailable
- `404 DATASET_NOT_FOUND` or `DOCUMENT_NOT_FOUND`: requested resource does not exist
