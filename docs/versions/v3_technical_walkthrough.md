# V3 Technical Walkthrough

This document explains V3 file by file so you can revise implementation details quickly and answer interview questions with code-level clarity.

## 1. Core Idea
V3 introduces controlled tool calling.

```text
LLM proposes tool
-> backend validates decision
-> backend validates tool input
-> backend executes allowlisted tool
-> backend returns structured trace
```

## 2. `app/schemas/agent.py`

### Purpose
Defines the agent-level contracts:
- `AgentQueryRequest`
- `ToolDecision`
- `AgentQueryResponse`

### Why It Matters
These schemas prevent loose dict-based flows and keep agent behavior explicit and testable.

### Key Details
- `ToolName` literal restricts tool options to:
  - `calculator`
  - `date_time`
  - `text_summarizer`
  - `file_analyzer`
  - `none`
- `ToolDecision.reason` must be non-empty.
- `AgentQueryResponse` includes trace fields:
  - `tool_used`
  - `tool_input`
  - `tool_output_summary`
  - `tool_status`

## 3. `app/schemas/tools.py`

### Purpose
Defines per-tool input schemas used before tool logic runs.

### Why It Matters
Validation belongs at contract boundaries, not spread through tool code.

### Key Details
- `CalculatorInput(expression)`
- `DateTimeInput(timezone="UTC")`
- `TextSummarizerInput(text)`
- `FileAnalyzerInput(file_path)`

## 4. `app/tools/registry.py`

### Purpose
Central allowlist for all executable tools.

### Why It Matters
The LLM does not execute anything directly. Execution is backend-controlled via registry lookups.

### Key Details
- `TOOL_REGISTRY` stores callable mappings.
- `initialize_tool_registry()` registers known tools at runtime.
- `get_tool()` raises controlled error for unregistered tools.

## 5. Tool Implementations

### `app/tools/calculator.py`
- Safe arithmetic evaluator built on AST traversal.
- Supports controlled operator set.
- Rejects unsupported expressions and divide-by-zero safely.

### `app/tools/date_time.py`
- Validates input with `DateTimeInput`.
- Handles `UTC` safely with `datetime.timezone.utc`.
- Uses `ZoneInfo` for other timezones.

### `app/tools/text_summarizer.py`
- Validates `text` input.
- Deterministic summary strategy (truncate to max words).
- Returns consistent plain text output.

### `app/tools/file_analyzer.py`
- Validates `file_path`.
- Checks existence and file type.
- Returns size, extension, and text metrics (line/word/char counts).

## 6. `app/prompts/tool_router_v3.py`

### Purpose
Defines the system prompt for tool decision generation.

### Why It Matters
Tool decisions need strict format and rules:
- JSON only
- one allowed tool
- tool-specific `tool_input` shape

### Key Details
- `TOOL_ROUTER_PROMPT_VERSION = "v3.1"`
- `build_tool_router_prompt(message)` combines system instructions with user message.

## 7. `app/services/tool_decision_parser.py`

### Purpose
Parses raw LLM decision output and validates into `ToolDecision`.

### Why It Matters
LLM output is external input and must be validated before execution.

### Key Details
- `json.loads` for syntax.
- `ToolDecision.model_validate` for schema.
- Raises `ToolDecisionParseError` on invalid output.

## 8. `app/services/agent_controller.py`

### Purpose
Orchestrates full V3 flow.

### Runtime Flow
```text
initialize_tool_registry()
-> build tool-router prompt
-> LLM decision output
-> parse ToolDecision
-> if tool_name == "none": return skipped response
-> resolve tool from registry
-> execute tool with validated input
-> return AgentQueryResponse
```

### Controlled Errors
- LLM failure -> `AgentControllerError`
- Decision parse failure -> `AgentControllerError`
- Unknown tool -> `AgentControllerError`
- Tool runtime failure -> `AgentControllerError`

## 9. `app/api/routes_agent.py`

### Purpose
Exposes the agentic flow through HTTP.

### Endpoint
`POST /agent/query`

### Behavior
- Input: `AgentQueryRequest`
- Output: `AgentQueryResponse`
- Error mapping: `AgentControllerError` -> HTTP `503` with `AGENT_CONTROLLER_ERROR`

## 10. `app/main.py`

### V3 Update
Includes the new `agent_router`, making `/agent/query` live.

## 11. Tests

### Unit
- `test_agent_schemas.py`
- `test_tools_schemas.py`
- `test_calculator_tool.py`
- `test_date_time_tool.py`
- `test_text_summarizer_tool.py`
- `test_file_analyzer_tool.py`
- `test_tool_registry.py`
- `test_tool_router_prompt.py`
- `test_tool_decision_parser.py`
- `test_agent_controller.py`

### Integration
- `test_agent_endpoint.py`

## 12. Why V3 Is Production-Style
1. LLM reasoning is constrained to structured decision output.
2. Backend owns authorization of tools through registry.
3. Tool input validation happens before execution.
4. Execution errors are converted into controlled API errors.
5. Responses include trace fields for observability and debugging.

## 13. Interview Summary
In V3, I implemented a controlled single-agent backend architecture. The LLM proposes a tool decision in JSON, the backend validates it with Pydantic, executes only allowlisted tools through a registry, and returns a structured traceable response. This separates reasoning from execution and prevents unsafe direct tool calls.

