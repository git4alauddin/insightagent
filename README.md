# InsightAgent

InsightAgent is a learning-first, production-style FastAPI backend for AI-powered data and document analysis.

## Current Version
V2 - Prompting + structured LLM output.

Detailed V1 notes: [docs/versions/v1_fastapi_basic_chat.md](docs/versions/v1_fastapi_basic_chat.md)
Detailed V2 notes: [docs/versions/v2_structured_output.md](docs/versions/v2_structured_output.md)

## Project Structure
```text
app/
  main.py
  config.py
  api/
    routes_health.py
    routes_chat.py
  prompts/
    structured_v2.py
  schemas/
    common.py
    chat.py
    structured.py
  services/
    llm_service.py
    structured_llm_service.py
    structured_parser.py
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
