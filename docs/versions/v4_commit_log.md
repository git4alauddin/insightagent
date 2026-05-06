# V4 Commit Log

This file maps each V4 commit heading to:
- what we implemented
- what was solved/taken care of

Use this as a quick recall sheet for interview prep and progress tracking.

## Commit-by-Commit (V4)

### `d032c98` - `v4: add sqlite foundation and core tables`
**What we did**
- Added SQLite setup and base DB utilities.
- Created core `sessions` and `messages` tables.

**What it solved / took care of**
- Established persistent storage for chat memory.
- Created the data foundation required for session-aware behavior.

### `689405a` - `v4: add session service for memory persistence`
**What we did**
- Added service-layer functions for session and message operations.
- Centralized read/write memory logic in one place.

**What it solved / took care of**
- Prevented DB logic from leaking into API routes.
- Gave us a reusable memory abstraction for current and future flows.

### `38ff0f6` - `v4: add memory-aware chat endpoint and session flow`
**What we did**
- Added memory chat endpoint flow.
- Connected request -> memory lookup -> LLM response -> memory write-back.

**What it solved / took care of**
- Enabled multi-turn continuity instead of stateless replies.
- Made follow-up questions context-aware.

### `0a618c1` - `v4: add session endpoints for creation and history retrieval`
**What we did**
- Added session lifecycle endpoints (`create`, `history` retrieval).

**What it solved / took care of**
- Made session control explicit for clients.
- Enabled inspection/debug of conversation history by session.

### `b94bd34` - `v4: harden memory chat with limits and context metadata`
**What we did**
- Added message length/context window safeguards.
- Added context usage metadata in response.

**What it solved / took care of**
- Reduced runaway prompt size and unstable memory behavior.
- Improved observability of how much prior context was used.

### `383e229` - `v4: add session metadata and controlled DB error handling`
**What we did**
- Added session metadata fields and explicit DB error mapping.
- Standardized controlled error responses for memory/session operations.

**What it solved / took care of**
- Improved reliability and client-side error predictability.
- Prepared the contract for production-style failure handling.

## Reusable Entry Template (for next versions)

### `<commit_hash>` - `<commit_heading>`
**What we did**
- ...

**What it solved / took care of**
- ...
