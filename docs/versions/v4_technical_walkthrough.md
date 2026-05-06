# V4 Technical Walkthrough

This document explains the V4 memory layer file by file.

## 1. Design Intent
V4 introduces short-term conversation memory with three responsibilities:
1. Persist session/message history.
2. Build bounded context for LLM.
3. Expose session state through API endpoints.

## 2. Database Layer

### `app/db/database.py`
- Defines SQLite DB path.
- Creates DB connection with `sqlite3.Row`.
- Provides `db_cursor()` context manager with auto-commit.

### `app/db/schema.py`
- Creates `sessions` and `messages` tables.
- Adds migration-safe column checks using `PRAGMA table_info`.
- Ensures optional session metadata columns exist:
  - `title`
  - `status`

## 3. Session Service

### `app/services/session_service.py`
Core functions:
- `create_session(session_id=None, title=None)`
- `session_exists(session_id)`
- `append_message(session_id, role, content, token_estimate=0)`
- `get_recent_messages(session_id, limit=20)`
- `format_context_for_llm(session_id, limit=20)`

Key behaviors:
- Stores timestamps in UTC ISO format.
- Retrieves message window in chronological order.
- Wraps DB failures as `SessionServiceError("Database operation failed.")`.
- Preserves explicit not-found error for missing sessions.

## 4. Memory Chat Service

### `app/services/memory_chat_service.py`
Core function:
- `run_memory_chat(message, session_id=None)`

Flow:
1. Validate message length (`MAX_MESSAGE_LENGTH`).
2. Resolve session (create or verify existing).
3. Store user message.
4. Build recent context (`MAX_CONTEXT_MESSAGES`).
5. Get LLM answer from message-list API.
6. Store assistant message.
7. Return `MemoryChatResponse` with `context_message_count`.

Guardrails:
- `MAX_CONTEXT_MESSAGES = 20`
- `MAX_MESSAGE_LENGTH = 5000`

Error model:
- Converts session/DB/LLM failures into `MemoryChatServiceError`.

## 5. Schema Updates

### `app/schemas/chat.py`
New models:
- `MemoryChatRequest`
- `MemoryChatResponse`

Notable fields:
- optional `session_id` in request
- `context_message_count` in response

## 6. API Endpoints

### `app/api/routes_chat.py`
New endpoint:
- `POST /chat/memory`

Behavior:
- Calls `run_memory_chat`.
- Returns controlled `MEMORY_CHAT_SERVICE_ERROR` with `503` when needed.

### `app/api/routes_session.py`
New endpoints:
- `POST /sessions`
- `GET /sessions/{session_id}/messages`

Error split:
- `SESSION_NOT_FOUND` -> `404`
- `SESSION_DB_ERROR` -> `503`

### `app/main.py`
Includes `session_router`.

## 7. Tests Added/Extended

### Unit
- `tests/unit/test_session_service.py`
- `tests/unit/test_memory_chat_service.py`

### Integration
- `tests/integration/test_session_endpoints.py`
- `tests/integration/test_memory_chat_flow.py`
- updates in `tests/integration/test_chat_endpoint.py`

What these prove:
- New-session and existing-session paths.
- Message persistence order and limit behavior.
- Context count propagation.
- Controlled not-found and DB error responses.
- Multi-turn continuity with same session ID.

## 8. Checklist Mapping (V4)
- `session_id` support: done.
- SQLite setup and tables: done.
- New/continue session flow: done.
- User/assistant message persistence: done.
- Role/content/time/token storage: done.
- Session metadata storage: done (`title`, `status`).
- Memory retrieval/context builder: done.
- Context limit/trimming strategy: done (recent-window).
- Memory-aware endpoint: done (`/chat/memory`).
- DB error handling: done.
- New/existing session tests/examples: done.

## 9. Interview Summary
In V4, I added a session-aware memory architecture with SQLite-backed history, bounded context retrieval, and controlled error handling. I separated persistence logic into a session service, added dedicated session endpoints, and introduced a memory chat flow that supports multi-turn continuity while keeping context and message size constrained.

