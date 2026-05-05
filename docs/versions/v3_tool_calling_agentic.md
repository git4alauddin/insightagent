# V3 - Tool Calling + Agentic Layer

## Version Goal
V3 upgrades InsightAgent from a response-focused backend into an agentic backend.

In V1/V2, the model mostly returned direct answers. In V3, the model first proposes a tool decision, then the backend validates and executes tools safely.

## What We Built
- Agent-level request/response schemas.
- Tool decision schema and parser.
- Tool input schemas.
- Tool registry with explicit allowlist behavior.
- Four tools:
  - calculator
  - date_time
  - text_summarizer
  - file_analyzer
- Tool-router prompt for LLM decision making.
- Agent controller service for orchestration.
- New endpoint: `POST /agent/query`.
- Unit and integration tests for the full V3 flow.

## Why This Matters
V3 is where InsightAgent becomes a controlled agent, not just an LLM wrapper.

Professional rule in this version:
1. LLM decides what might help.
2. Backend decides what is allowed.
3. Backend validates input and executes safely.

## V3 Agent Flow
```text
User message
-> build tool-router prompt
-> LLM returns tool decision JSON
-> parse + validate ToolDecision
-> tool lookup via registry
-> tool input validation
-> tool execution
-> AgentQueryResponse with tool trace
```

## API Contract

Endpoint:
```text
POST /agent/query
```

Request:
```json
{
  "message": "What is 25 * 18?"
}
```

Response shape:
```json
{
  "answer": "Tool 'calculator' completed successfully.",
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

## Files Added
- `app/schemas/agent.py`
- `app/schemas/tools.py`
- `app/tools/registry.py`
- `app/tools/calculator.py`
- `app/tools/date_time.py`
- `app/tools/text_summarizer.py`
- `app/tools/file_analyzer.py`
- `app/prompts/tool_router_v3.py`
- `app/services/tool_decision_parser.py`
- `app/services/agent_controller.py`
- `app/api/routes_agent.py`
- `tests/unit/test_agent_schemas.py`
- `tests/unit/test_calculator_tool.py`
- `tests/unit/test_date_time_tool.py`
- `tests/unit/test_text_summarizer_tool.py`
- `tests/unit/test_file_analyzer_tool.py`
- `tests/unit/test_tool_registry.py`
- `tests/unit/test_tool_router_prompt.py`
- `tests/unit/test_tool_decision_parser.py`
- `tests/unit/test_agent_controller.py`
- `tests/integration/test_agent_endpoint.py`

## Safety Decisions
- Calculator uses AST parsing, not direct `eval()`.
- Tool calls happen only through the registry.
- Tool decisions are validated against `ToolDecision` before execution.
- Tool-specific input is validated before logic runs.
- Tool and controller failures are converted to controlled errors.

## Manual Test Commands

Start server:
```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Calculator path:
```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/agent/query" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"message":"What is 25 * 18?"}'
```

Date-time path:
```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/agent/query" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"message":"Give me the current date and time in UTC."}'
```

Text summarizer path:
```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/agent/query" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"message":"Summarize this text: Machine learning systems improve through iterative training and evaluation."}'
```

File analyzer path:
```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/agent/query" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"message":"Analyze the file at path C:\\Users\\alaud\\OneDrive\\Desktop\\ai-agent-proj\\insightagent\\README.md"}'
```

No-tool path:
```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/agent/query" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"message":"What does API stand for?"}'
```

## Test Status
- Unit and integration tests were added for all V3 components.
- Latest full suite result during V3 completion:

```text
74 passed
```

## What I Learned
- Agentic systems require backend controls beyond prompt quality.
- Tool routing is safer when decision and execution are decoupled.
- Registry + schema validation gives a clean contract boundary.
- Tool trace fields make debugging and interview discussion much stronger.

## Interview Summary
In V3, I designed a controlled tool-calling backend. The LLM returns a JSON tool decision, but the backend validates that decision and executes only allowlisted tools from a registry. Each tool has input validation and controlled error handling. The `/agent/query` endpoint returns a traceable structured response with selected tool details, which made the system safer and more production-style.

