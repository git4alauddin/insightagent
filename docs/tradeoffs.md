# InsightAgent Trade-Offs, Limitations, And Future Improvements

This document captures the engineering judgment behind InsightAgent and the honest boundaries of the current implementation.

## Design Trade-Offs

| Choice | Why It Was Chosen | Production Alternative |
| --- | --- | --- |
| FastAPI backend | Fast, typed, Python-native API framework with strong Pydantic support. | Keep FastAPI, add deployment hardening and OpenTelemetry. |
| SQLite metadata store | Simple local persistence for sessions, messages, datasets, documents, and vectors. | PostgreSQL for multi-user, concurrent, deployed workloads. |
| Local upload storage | Easy to inspect during local development and portfolio demos. | Cloud object storage such as Google Cloud Storage or S3. |
| Deterministic local embeddings | Reliable tests without external embedding calls or cost. | Managed embeddings and a dedicated vector database for larger RAG workloads. |
| SQLite-backed vector storage | Good enough for local RAG plumbing and deterministic tests. | Chroma, Qdrant, Weaviate, Pinecone, or pgvector for production retrieval. |
| API key authentication | Simple protection for costly/private endpoints. | OAuth/JWT with user-level identity and permissions. |
| Rule-based evaluation | Deterministic and easy to run repeatedly. | Add LLM-as-judge for semantic scoring after deterministic checks. |
| Controlled tool execution | Safer than arbitrary Python execution. | Keep controlled execution; add more vetted tools over time. |
| In-memory rate limiting | Lightweight local protection. | Redis-backed rate limiting or gateway-level throttling for multi-instance deployments. |

## Current Limitations

- Cloud Run deployment is documented as a target but intentionally deferred.
- API key authentication is service-level, not user-level.
- Uploads are stored locally, so multi-instance deployment would need shared storage.
- SQLite is not ideal for high-concurrency production traffic.
- PDF extraction quality depends on document formatting.
- Large CSV and document files are intentionally limited.
- RAG quality depends on extraction, chunking, embedding, and retrieval quality.
- The system avoids arbitrary Python execution, which limits flexibility but improves safety.
- Evaluation coverage is useful but still small compared with a production benchmark suite.
- Token/cost fields are recorded only when usage metadata is available; the app does not invent estimates.
- The current backend does not include a frontend dashboard.

## Future Improvements

High-value next steps:
- Deploy to Google Cloud Run and publish the live URL.
- Add PostgreSQL for persistent multi-user data.
- Add cloud object storage for uploaded datasets and documents.
- Add a managed vector database or pgvector.
- Add JWT/OAuth authentication.
- Add streaming responses for chat and document answers.
- Add a small frontend dashboard for uploads, questions, evals, and metrics.
- Add OpenTelemetry traces and structured log export.
- Add LLM-as-judge evaluation for semantic scoring.
- Expand the evaluation dataset with more positive and negative cases.
- Add role-based access control for sessions, datasets, and documents.

## Portfolio Explanation

These choices keep the project focused on backend architecture, safety, evaluation, and observability without overbuilding infrastructure too early.

The current system is strong as a local and containerized AI backend case study. The future improvements describe the path from portfolio backend to production-ready service.
