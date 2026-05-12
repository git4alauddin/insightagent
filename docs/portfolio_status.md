# InsightAgent Portfolio Status

This file maps the V10 portfolio checklist to the public repository state.

## Public Repo Status

| Checklist Item | Status | Repo Evidence |
| --- | --- | --- |
| Clean final repo structure | Complete | `app/`, `tests/`, `docs/`, `evals/`, and `scripts/` are separated by responsibility. |
| Professional README | Complete | `README.md` is the main portfolio entrypoint. |
| Recruiter-facing summary | Complete | README project snapshot and capability summary. |
| Engineer-facing technical overview | Complete | `docs/architecture.md`. |
| Architecture diagram under `docs/` | Complete | Mermaid architecture diagrams in `docs/architecture.md`. |
| API endpoint table | Complete | README API table and `docs/api_examples.md`. |
| API request/response examples | Complete | `docs/api_examples.md`. |
| Local setup instructions | Complete | README Quick Start section. |
| Docker run instructions | Complete | README Docker section. |
| Deployment instructions | In progress | Docker and production env settings are documented; local container verification has passed. |
| `.env.example` | Complete | `.env.example`. |
| Evaluation section | Complete | README Evaluation section and V8 docs. |
| How to evaluate locally | Complete | README Evaluation command. |
| Observability examples | Complete | README Observability section and V9 docs. |
| Trade-offs section | Complete | README Trade-Offs section and `docs/tradeoffs.md`. |
| Limitations section | Complete | `docs/tradeoffs.md`. |
| Future improvements section | Complete | `docs/tradeoffs.md`. |
| Demo script | Local-only | Kept outside the repo for recording guidance. |
| Screenshots or recorded demo link | Deferred | To be added after recording. |
| Resume bullets | Local-only | Kept outside the repo for personal job material. |
| Interview pitch | Local-only | Kept outside the repo for personal preparation. |
| License | Deferred | Add only after choosing the intended license. |
| Cloud Run deployment link | In progress | Deployment prep and local Docker verification are complete; live Cloud Run URL is still pending. |
| Final cleanup of unused files/dependencies | Complete | Tracked files were scanned; generated/runtime files are ignored and requirements are in use. |

## Current Verification Evidence

```text
247 passed
```

The automated suite covers API contracts, service behavior, tools, memory, CSV analysis, document Q&A, evaluation, auth, errors, request middleware, observability, and metrics summaries.

## Public Demo Readiness

The repository is ready for a recorded walkthrough of:
- project overview
- local health/readiness
- chat and structured output
- agent tool calling
- CSV upload and analysis
- document upload and grounded Q&A
- evaluation runner
- request tracing and metrics summary
- architecture and trade-offs

The actual recording script is intentionally kept outside the repository.

## Remaining Public Portfolio Items

- Record and publish a demo video or screenshots.
- Add the demo link to README after publishing.
- Add a license if the repo will be shared publicly with reuse permissions.
- Complete Cloud Run deployment and add the live URL when cloud smoke tests pass.

## Hygiene Notes

- `docs/demo_script.md` is not tracked.
- `docs/resume_interview.md` is not tracked.
- `.env`, virtual environment files, Python caches, pytest caches, logs, uploads, and eval result files are ignored.
- No stale V10 commit placeholders remain except the current in-progress commit entry.
