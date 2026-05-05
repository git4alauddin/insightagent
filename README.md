# InsightAgent

InsightAgent is a learning-first, production-style FastAPI backend for AI-powered data and document analysis.

## Current Version
V3 - Tool calling + agentic query flow.

Detailed V1 notes: [docs/versions/v1_fastapi_basic_chat.md](docs/versions/v1_fastapi_basic_chat.md)
Detailed V2 notes: [docs/versions/v2_structured_output.md](docs/versions/v2_structured_output.md)
Detailed V3 notes: [docs/versions/v3_tool_calling_agentic.md](docs/versions/v3_tool_calling_agentic.md)

## Project Structure
```text
app/
  main.py
  config.py
  api/
    routes_health.py
    routes_chat.py
    routes_agent.py
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
