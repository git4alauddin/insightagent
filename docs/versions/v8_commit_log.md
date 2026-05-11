# V8 Commit Log

This file maps each V8 commit heading to:
- what we implemented
- what was solved/taken care of

## Commit-by-Commit (V8)

### `52de6ae` - `v8: add evaluation dataset and runner foundation`
**What we did**
- Updated app version defaults to V8.
- Added JSONL evaluation dataset.
- Added initial cases for chat, structured output, tool calling, CSV analysis, RAG, and insufficient context.
- Added `scripts/run_eval.py`.
- Added setup upload support for dataset/document eval cases.
- Added basic status/shape scoring.
- Added latency capture and JSON result output.
- Added eval runner unit tests.
- Added V8 version documentation structure.

**What it solved / took care of**
- Created the foundation for repeatable evaluation runs.
- Gave V8 a measurable dataset format before adding advanced scoring.
- Prepared the project for pass-rate summaries, failure analysis, and regression tracking.

### `<pending>` - `v8: add evaluation scoring rules`
**What we did**
- Added per-case `scoring` metadata to the evaluation dataset.
- Added status and format-validity scoring.
- Added tool correctness scoring.
- Added CSV analysis intent scoring.
- Added RAG citation presence scoring.
- Added insufficient-context safety scoring.
- Added failure category summaries.
- Added unit tests for scoring rules and failure categories.

**What it solved / took care of**
- Made eval results more useful than status/key checks alone.
- Started detecting wrong tool selection and missing citations.
- Added failure categories that can support later debugging and regression tracking.

## Reusable Entry Template

### `<commit_hash>` - `<commit_heading>`
**What we did**
- ...

**What it solved / took care of**
- ...
