# InsightAgent

InsightAgent is a learning-first, production-style FastAPI backend for AI-powered data and document analysis.

## Current Version
V5 - CSV data analysis assistant.

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

## Project Structure
```text
app/
  main.py
  config.py
  api/
    routes_health.py
    routes_chat.py
    routes_agent.py
    routes_session.py
    routes_datasets.py
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

Check health:

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "ok",
  "service": "InsightAgent",
  "version": "v1"
}
```

Send a chat request:

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/chat" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"message":"Explain what a CSV file is in one sentence."}'
```

Send a structured chat request:

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/chat/structured" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"message":"Explain missing values in a dataset in simple words."}'
```

Send an agent query request:

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/agent/query" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"message":"What is 25 * 18?"}'
```

Send a memory chat request:

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/chat/memory" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"message":"Hello, this is my first memory message."}'
```

Create a session explicitly:

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/sessions" `
  -Method Post
```

Get session message history:

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/sessions/<session_id>/messages" `
  -Method Get
```

Upload a CSV dataset:

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/datasets/upload" `
  -Method Post `
  -Form @{ file = Get-Item ".\sample.csv" }
```

Get dataset summary:

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/datasets/<dataset_id>/summary" `
  -Method Get
```

Ask a dataset question:

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/datasets/<dataset_id>/ask" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"question":"Which column has the most missing values?"}'
```
