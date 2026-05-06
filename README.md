# InsightAgent

InsightAgent is a learning-first, production-style FastAPI backend for AI-powered data and document analysis.

## Current Version
V4 - Memory + context handling.

Detailed V1 notes: [docs/versions/v1_fastapi_basic_chat.md](docs/versions/v1_fastapi_basic_chat.md)
Detailed V2 notes: [docs/versions/v2_structured_output.md](docs/versions/v2_structured_output.md)
Detailed V3 notes: [docs/versions/v3_tool_calling_agentic.md](docs/versions/v3_tool_calling_agentic.md)
Detailed V4 notes: [docs/versions/v4_memory_context.md](docs/versions/v4_memory_context.md)
V4 commit tracking: [docs/versions/v4_commit_log.md](docs/versions/v4_commit_log.md)

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
  services/
    llm_service.py
    structured_llm_service.py
    structured_parser.py
    tool_decision_parser.py
    agent_controller.py
    session_service.py
    memory_chat_service.py
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
