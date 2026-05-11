# InsightAgent

InsightAgent is a learning-first, production-style FastAPI backend for AI-powered data and document analysis.

## Current Version
V7 - RAG document Q&A.

Cloud Run deployment is intentionally deferred until the local/containerized backend is fully closed out and ready for an external runtime.

Detailed V1 notes: [docs/versions/v1_fastapi_basic_chat.md](docs/versions/v1_fastapi_basic_chat.md)
V1 commit tracking: [docs/versions/v1_commit_log.md](docs/versions/v1_commit_log.md)
Detailed V2 notes: [docs/versions/v2_structured_output.md](docs/versions/v2_structured_output.md)
V2 commit tracking: [docs/versions/v2_commit_log.md](docs/versions/v2_commit_log.md)
Detailed V3 notes: [docs/versions/v3_tool_calling_agentic.md](docs/versions/v3_tool_calling_agentic.md)
V3 commit tracking: [docs/versions/v3_commit_log.md](docs/versions/v3_commit_log.md)
Detailed V4 notes: [docs/versions/v4_memory_context.md](docs/versions/v4_memory_context.md)
V4 commit tracking: [docs/versions/v4_commit_log.md](docs/versions/v4_commit_log.md)
Detailed V5 notes: [docs/versions/v5_data_analysis_assistant.md](docs/versions/v5_data_analysis_assistant.md)
V5 commit tracking: [docs/versions/v5_commit_log.md](docs/versions/v5_commit_log.md)
Detailed V6 notes: [docs/versions/v6_backend_maturity.md](docs/versions/v6_backend_maturity.md)
V6 technical walkthrough: [docs/versions/v6_technical_walkthrough.md](docs/versions/v6_technical_walkthrough.md)
V6 commit tracking: [docs/versions/v6_commit_log.md](docs/versions/v6_commit_log.md)
Detailed V7 notes: [docs/versions/v7_document_qa.md](docs/versions/v7_document_qa.md)
V7 technical walkthrough: [docs/versions/v7_technical_walkthrough.md](docs/versions/v7_technical_walkthrough.md)
V7 commit tracking: [docs/versions/v7_commit_log.md](docs/versions/v7_commit_log.md)

## Project Structure
```text
app/
  main.py
  config.py
  api/
    cors.py
    dependencies.py
    middleware.py
    rate_limit.py
    routes_health.py
    routes_chat.py
    routes_agent.py
    routes_session.py
    routes_datasets.py
    routes_documents.py
  db/
    database.py
    schema.py
  prompts/
    structured_v2.py
    tool_router_v3.py
  schemas/
    common.py
    chat.py
    structured.py
    agent.py
    tools.py
    dataset.py
    document.py
  services/
    llm_service.py
    structured_llm_service.py
    structured_parser.py
    tool_decision_parser.py
    agent_controller.py
    session_service.py
    memory_chat_service.py
    dataset_service.py
    dataset_registry_service.py
    dataset_intent_service.py
    dataset_analysis_router.py
    dataset_tools_service.py
    dataset_execution_service.py
    dataset_answer_service.py
    document_service.py
    document_registry_service.py
  tools/
    calculator.py
    date_time.py
    text_summarizer.py
    file_analyzer.py
  utils/
    logger.py
tests/
  integration/
  unit/
docs/
  project_report.md
  versions/
    v1_fastapi_basic_chat.md
    v2_structured_output.md
    v3_tool_calling_agentic.md
    v4_memory_context.md
    v5_data_analysis_assistant.md
    v6_backend_maturity.md
    v6_technical_walkthrough.md
    v6_commit_log.md
    v7_document_qa.md
    v7_technical_walkthrough.md
    v7_commit_log.md
```

## Run Locally
Install dependencies:

```bash
pip install -r requirements.txt
```

Start the API:

```bash
uvicorn app.main:app --reload
```

## Run With Docker
Build the image:

```powershell
docker build -t insightagent:v6 .
```

Run the container:

```powershell
docker run --rm -p 8000:8000 `
  -e API_KEY=your-service-api-key-here `
  -e LLM_API_KEY=your-llm-api-key-here `
  insightagent:v6
```

Important production environment variables:

```text
APP_ENV=production
APP_VERSION=v7
DOCS_ENABLED=false
API_KEY=<service-api-key>
LLM_API_KEY=<provider-api-key>
CORS_ALLOWED_ORIGINS=<deployed-frontend-origin>
RATE_LIMIT_ENABLED=true
```

For production deployments, keep `DOCS_ENABLED=false` unless API docs are intentionally exposed.

Check health:

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "ok",
  "service": "InsightAgent",
  "version": "v7"
}
```

Check readiness:

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/ready" `
  -Method Get
```

Protected endpoints require an API key:

```powershell
$headers = @{ "x-api-key" = "your-service-api-key-here" }
```

Send a chat request:

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/chat" `
  -Method Post `
  -Headers $headers `
  -ContentType "application/json" `
  -Body '{"message":"Explain what a CSV file is in one sentence."}'
```

Send a structured chat request:

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/chat/structured" `
  -Method Post `
  -Headers $headers `
  -ContentType "application/json" `
  -Body '{"message":"Explain missing values in a dataset in simple words."}'
```

Send an agent query request:

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/agent/query" `
  -Method Post `
  -Headers $headers `
  -ContentType "application/json" `
  -Body '{"message":"What is 25 * 18?"}'
```

Send a memory chat request:

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/chat/memory" `
  -Method Post `
  -Headers $headers `
  -ContentType "application/json" `
  -Body '{"message":"Hello, this is my first memory message."}'
```

Create a session explicitly:

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/sessions" `
  -Method Post `
  -Headers $headers
```

Get session message history:

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/sessions/<session_id>/messages" `
  -Method Get `
  -Headers $headers
```

Upload a CSV dataset:

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/datasets/upload" `
  -Method Post `
  -Headers $headers `
  -Form @{ file = Get-Item ".\sample.csv" }
```

Get dataset summary:

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/datasets/<dataset_id>/summary" `
  -Method Get `
  -Headers $headers
```

Ask a dataset question:

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/datasets/<dataset_id>/ask" `
  -Method Post `
  -Headers $headers `
  -ContentType "application/json" `
  -Body '{"question":"Which column has the most missing values?"}'
```

Upload a document:

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/documents/upload" `
  -Method Post `
  -Headers $headers `
  -Form @{ file = Get-Item ".\policy.txt" }
```
