# V3 Commit Log

This file maps each V3 commit heading to:
- what we implemented
- what was solved/taken care of

## Commit-by-Commit (V3)

### `f17fd33` - `v3: add agent schemas and tool registry foundation`
**What we did**
- Added initial agent request/response schemas.
- Added tool schema and registry foundation.

**What it solved / took care of**
- Established contract boundaries for agent orchestration.
- Created allowlisted tool-dispatch foundation.

### `b320c27` - `v3: add date_time tool with schema validation and tests`
**What we did**
- Added `date_time` tool implementation with validation and tests.

**What it solved / took care of**
- Introduced safe, deterministic utility tool execution.
- Proven pattern for adding future tools with test coverage.

### `b44fc40` - `v3: add text_summarizer tool and registry wiring`
**What we did**
- Added `text_summarizer` tool and connected it through registry.

**What it solved / took care of**
- Expanded agent capability beyond numeric/date tools.
- Verified registry-driven tool routing approach.

### `37d19f1` - `v3: add file_analyzer tool and registry wiring`
**What we did**
- Added `file_analyzer` tool and registry integration.

**What it solved / took care of**
- Enabled controlled file-content analysis workflow.
- Moved InsightAgent closer to document/data use cases.

### `a92f667` - `v3: add tool router prompt and decision parser`
**What we did**
- Added tool-router prompt and parser for model-generated tool decisions.

**What it solved / took care of**
- Separated "LLM suggests tool" from "backend validates tool decision."
- Improved reliability of tool invocation pipeline.

### `4b9f040` - `v3: add agent controller service`
**What we did**
- Added controller service to orchestrate decision -> validation -> execution flow.

**What it solved / took care of**
- Centralized agent business logic outside route handlers.
- Made endpoint layer cleaner and easier to maintain.

### `5f5bab4` - `v3: add /agent/query endpoint with integration tests`
**What we did**
- Added `POST /agent/query` plus integration tests.

**What it solved / took care of**
- Exposed the full agentic flow as an API contract.
- Validated end-to-end behavior across parsing, registry, and tools.

### `ef2ccf8` - `v3: finalize agentic layer documentation`
**What we did**
- Finalized V3 documentation of architecture and behavior.

**What it solved / took care of**
- Captured technical reasoning for interview and future onboarding.
- Improved traceability of V3 design decisions.

## Reusable Entry Template

### `<commit_hash>` - `<commit_heading>`
**What we did**
- ...

**What it solved / took care of**
- ...
