# Deployment - Cloud Run Completion

## Goal

Deploy InsightAgent outside the local machine, verify the containerized backend works in a cloud runtime, and document the remaining production trade-offs honestly.

This deployment pass sits after V10. V1 through V10 built and packaged the backend; this pass proves the service can run as a deployed API.

## Current Status

Status: in progress.

Completed:

- Repo cleanup for local runtime artifacts.
- Docker runtime updated to respect the platform-provided `PORT`.
- Local `insightagent.db` artifact removed.
- Docker image builds locally.
- Local production-like container smoke tests pass.
- Cloud Build pushed the deployment image to Artifact Registry.
- Cloud Run service deployed successfully.
- Cloud Run public smoke tests pass.
- Cloud Run authenticated smoke test passes.

Remaining:

- Update README and portfolio status with real deployment state.
- Record final storage limitation and deployment completion notes.

## What We Changed First

The first deployment chunk prepared the repository and Docker runtime:

- `.gitignore` now ignores local DB, upload, and log artifacts.
- `Dockerfile` now starts Uvicorn on `${PORT:-8000}`.
- The local generated `insightagent.db` file was removed.

## Why It Matters

Cloud runtimes inject their own port configuration. Hardcoding only `8000` works locally, but the container should respect the runtime environment when deployed.

Local artifacts also should not enter the repository because they can create noisy commits, leak runtime state, or confuse reviewers about what is source code versus generated state.

## Deployment Scope

This deployment pass covers:

- repo hygiene
- production configuration review
- Docker verification
- Cloud Run setup
- Secret Manager usage
- Artifact Registry image push
- Cloud Run deployment
- deployed smoke tests
- storage limitation documentation
- final portfolio status update

## Deployed Service

Cloud Run URL:

```text
https://insightagent-1089133393572.us-central1.run.app
```

Artifact Registry image:

```text
us-central1-docker.pkg.dev/insightagent-496120/insightagent/insightagent:v10
```

## Known Deployment Trade-Off

InsightAgent currently uses local SQLite and local file storage. That is acceptable for a portfolio/demo deployment when documented clearly, but Cloud Run local filesystem persistence is not durable across revisions or instances.

Managed database and object storage are future production improvements, not hidden completed work.

## Testing Status

Local container verification complete.
Cloud Run verification complete.

Current deployment verification completed:

- Latest deployment-prep commit confirmed: `7a6dec6 deploy: prepare repo and docker runtime for cloud`
- Docker image built successfully as `insightagent:deploy-verify`.
- Temporary container ran with production-like settings:
  - `PORT=8080`
  - `APP_ENV=production`
  - `APP_VERSION=v10`
  - `DOCS_ENABLED=false`
  - `API_KEY=deploy-test-key`
  - `RATE_LIMIT_ENABLED=true`
- `GET /health` returned `ok`.
- `GET /ready` returned `ready`.
- `GET /docs` returned `404`, confirming docs were disabled.
- `POST /chat` without API key returned `401` with structured `UNAUTHORIZED` error.
- `POST /sessions` with valid API key returned `success`.
- Cloud Build completed successfully with image `us-central1-docker.pkg.dev/insightagent-496120/insightagent/insightagent:v10`.
- First Cloud Run revision failed to start because production config rejected wildcard CORS.
- `CORS_ALLOWED_ORIGINS` was changed to a non-wildcard value.
- Cloud Run deployment then succeeded.
- Deployed `GET /health` returned `ok`.
- Deployed `GET /ready` returned `ready`.
- Deployed `GET /docs` returned `404`.
- Deployed `POST /chat` without API key returned `401`.
- Deployed `POST /sessions` with Secret Manager API key returned `success`.

## Done When

Deployment is complete when:

- Docker image builds locally. Complete.
- Container smoke tests pass. Complete.
- Cloud Run service is deployed. Complete.
- Secrets are managed outside the repo. Complete.
- `/health` and `/ready` work on the deployed URL. Complete.
- Protected endpoints reject missing/wrong API keys. Complete.
- A representative protected endpoint works with the correct API key. Complete.
- README and portfolio docs reflect the real deployed state.
- Storage limitations are documented honestly.

## Interview Summary

The deployment pass turns InsightAgent from a locally complete backend into a cloud-verifiable service. I prepared the repo for deployment by keeping generated runtime files out of Git and updating the Docker runtime to use the platform-provided port, built and pushed the container image through Google Cloud, configured Cloud Run with Secret Manager-backed API keys, fixed a production CORS startup issue, and smoke-tested the live service for health, readiness, disabled docs, auth failure, and authenticated session creation.
