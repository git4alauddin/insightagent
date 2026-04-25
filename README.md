# InsightAgent

InsightAgent is a learning-first, production-style FastAPI backend for AI-powered data and document analysis.

## Current Version
V1 - Basic FastAPI + Groq-backed chat API.

Detailed V1 notes: [docs/versions/v1_fastapi_basic_chat.md](docs/versions/v1_fastapi_basic_chat.md)

## Project Structure
```text
app/
  main.py
  config.py
  api/
    routes_health.py
    routes_chat.py
  schemas/
    common.py
    chat.py
  services/
    llm_service.py
  utils/
    logger.py
tests/
docs/
  project_report.md
  versions/
    v1_fastapi_basic_chat.md
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
