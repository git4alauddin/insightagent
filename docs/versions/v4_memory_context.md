# V4 - Memory + Context Handling

## Version Goal
V4 makes InsightAgent session-aware.  
Instead of treating each request as isolated, the backend now stores conversation history and reuses recent context for follow-up answers.

## What We Built
- SQLite database foundation under `app/db/`.
- `sessions` and `messages` tables.
- Session service for:
  - create session
  - check session existence
  - append messages
  - retrieve recent messages
  - build LLM context from memory
- Memory-aware chat endpoint: `POST /chat/memory`.
- Session endpoints:
  - `POST /sessions`
  - `GET /sessions/{session_id}/messages`
- Guardrails:
  - maximum message length
  - bounded context window
  - context usage metadata in response
- Controlled DB error behavior:
  - `SESSION_NOT_FOUND` (404)
  - `SESSION_DB_ERROR` (503)
  - `MEMORY_CHAT_SERVICE_ERROR` (503)

## Why This Matters
Without memory, the assistant is stateless and cannot reliably handle follow-up questions.  
V4 introduces conversation continuity and the foundation needed for later dataset/document workflows.

## API Surface Added In V4
- `POST /chat/memory`
- `POST /sessions`
- `GET /sessions/{session_id}/messages`

## Memory Chat Response Shape
```json
{
  "session_id": "session-123",
  "answer": "assistant reply",
  "context_message_count": 3,
  "status": "success"
}
```

## Context Strategy
- Store user message first.
- Fetch last `MAX_CONTEXT_MESSAGES` messages.
- Send those messages to LLM.
- Store assistant reply.
- Return session ID + context count.

Current constants:
- `MAX_CONTEXT_MESSAGES = 20`
- `MAX_MESSAGE_LENGTH = 5000`

## Data Model Summary
### sessions
- `session_id`
- `created_at`
- `updated_at`
- `title` (optional)
- `status` (`active` default)

### messages
- `id`
- `session_id`
- `role`
- `content`
- `created_at`
- `token_estimate`

## Safety and Error Handling
- Missing session ID in memory chat creates a new session.
- Invalid session ID returns controlled not-found behavior.
- DB failures are converted to controlled service errors.
- Oversized messages are rejected before DB/LLM operations.

## Test Coverage Added In V4
- `tests/unit/test_session_service.py`
- `tests/unit/test_memory_chat_service.py`
- `tests/integration/test_session_endpoints.py`
- `tests/integration/test_memory_chat_flow.py`
- updates in `tests/integration/test_chat_endpoint.py`

Latest suite status after V4 closeout:
```text
93+ tests passing (see current pytest output)
```

## Manual Verification Commands
Create session:
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/sessions" -Method Post
```

Memory chat (new session):
```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/chat/memory" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"message":"Hello, remember this detail."}'
```

Memory chat (existing session):
```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/chat/memory" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"session_id":"<session_id>", "message":"What did I just tell you?"}'
```

Read session messages:
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/sessions/<session_id>/messages" -Method Get
```

## Interview Summary
In V4, I added persistent short-term memory using SQLite-backed sessions and messages. I created a memory-aware chat endpoint that reuses recent context for multi-turn continuity, added explicit session APIs, introduced context and input-size guardrails, and enforced controlled DB error behavior for stable client contracts.

