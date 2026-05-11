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

### `de114ec` - `v8: add evaluation scoring rules`
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

### `243deaa` - `v8: add eval regression comparison`
**What we did**
- Added previous result loading.
- Added eval result comparison helper.
- Added `--compare-to` CLI option.
- Added pass-rate delta output.
- Added newly failing and newly passing case detection.
- Added added/removed case detection.
- Added comparison output in saved result files.
- Added unit tests for comparison behavior.

**What it solved / took care of**
- Made eval runs comparable over time.
- Added the first regression signal for V8.
- Helped identify which cases got worse, improved, were added, or disappeared.

### `ae44872` - `v8: add eval runner integration proof`
**What we did**
- Added an eval runner helper that can execute cases with an existing client.
- Kept the normal CLI path working through the same runner helper.
- Added an in-process FastAPI integration test for CSV and RAG eval cases.
- Verified setup uploads, placeholder endpoint replacement, scoring, summary generation, and result saving together.

**What it solved / took care of**
- Proved the evaluator can drive real API flows without requiring a separate uvicorn process in tests.
- Covered upload-dependent evaluation cases end-to-end.
- Made the eval runner safer to refactor because API execution is now tested beyond unit-level scoring.

### `e907a91` - `v8: add relevance and groundedness scoring`
**What we did**
- Added answer relevance scoring through expected answer terms.
- Added RAG groundedness scoring through configured terms checked against both answer text and reference document text.
- Added relevance and groundedness metadata to deterministic CSV/RAG eval cases.
- Added unit tests for passing and failing relevance checks.
- Added unit tests for passing and failing groundedness checks.
- Extended the in-process eval proof to exercise relevance and groundedness scoring.

**What it solved / took care of**
- Started measuring whether answers contain expected task-specific content.
- Added a deterministic groundedness signal for RAG without using model-assisted judging.
- Made eval failure categories more useful for answer-quality regressions.

### `c8dac7c` - `v8: add citation accuracy and safety failure tests`
**What we did**
- Split RAG citation scoring into citation presence and citation accuracy.
- Added deterministic citation accuracy checks for expected filenames, chunk id prefixes, and expected citation terms.
- Added citation-term metadata to the positive RAG eval case.
- Added tests proving RAG answers without citations fail.
- Added tests proving unsupported confident/cited answers fail.
- Extended the in-process eval proof to exercise citation accuracy metadata.

**What it solved / took care of**
- Made citation failures easier to diagnose.
- Covered V8 checklist items for missing citations and unsafe unsupported answers.
- Added a stricter citation accuracy signal before adding semantic citation judging.

### `5a8586a` - `v8: document evaluation workflow and results`
**What we did**
- Expanded README evaluation instructions.
- Documented local eval execution and regression comparison commands.
- Documented current V8 eval coverage.
- Documented saved result file structure.
- Documented current automated verification status.
- Updated V8 docs and project report with evaluation workflow/results guidance.

**What it solved / took care of**
- Covered the V8 checklist item for documenting the evaluation process.
- Made eval results easier to interpret without reading the runner code.
- Clarified what the current eval layer measures and what is still pending.

### `f78e310` - `v8: add token and cost metadata to eval results`
**What we did**
- Added per-case optional usage metadata to eval results.
- Added token/cost extraction from common response shapes.
- Added summary usage totals for available cases.
- Preserved unavailable usage cleanly when endpoints do not return token/cost data.
- Added tests for nested provider-style usage metadata.
- Added tests for top-level usage metadata.
- Updated docs to describe usage metadata in saved eval results.

**What it solved / took care of**
- Covered the V8 checklist item for tracking token/cost if available.
- Made eval results future-ready for endpoints that expose provider usage.
- Kept current deterministic endpoints honest by marking usage unavailable instead of inventing estimates.

### `00b46ae` - `v8: close out evaluation layer documentation`
**What we did**
- Marked V8 as complete in the version documentation.
- Added a V8 closeout summary.
- Tightened checklist mapping from started/basic to done where implementation is complete.
- Documented honest limitations for live LLM evals, deployed evals, and model-assisted judging.
- Updated the project report with V8 completion status.

**What it solved / took care of**
- Closed the version cleanly before moving to V9.
- Made it clear what V8 proves today and what remains future work.
- Preserved an honest portfolio story instead of overstating evaluation maturity.

## Reusable Entry Template

### `<commit_hash>` - `<commit_heading>`
**What we did**
- ...

**What it solved / took care of**
- ...
