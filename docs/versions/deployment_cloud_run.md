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

Remaining:

- Prepare GCP services and secrets.
- Push image to Artifact Registry.
- Deploy to Cloud Run.
- Smoke test deployed endpoints.
- Update README and portfolio status with real deployment state.

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

## Known Deployment Trade-Off

InsightAgent currently uses local SQLite and local file storage. That is acceptable for a portfolio/demo deployment when documented clearly, but Cloud Run local filesystem persistence is not durable across revisions or instances.

Managed database and object storage are future production improvements, not hidden completed work.

## Testing Status

Local container verification complete.
Cloud verification pending.

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

Next verification:

- Cloud Run smoke tests after deployment

## Done When

Deployment is complete when:

- Docker image builds locally. Complete.
- Container smoke tests pass. Complete.
- Cloud Run service is deployed.
- Secrets are managed outside the repo.
- `/health` and `/ready` work on the deployed URL.
- Protected endpoints reject missing/wrong API keys.
- A representative protected endpoint works with the correct API key.
- README and portfolio docs reflect the real deployed state.
- Storage limitations are documented honestly.

## Interview Summary

The deployment pass turns InsightAgent from a locally complete backend into a cloud-verifiable service. I prepared the repo for deployment by keeping generated runtime files out of Git and updating the Docker runtime to use the platform-provided port, which is required for Cloud Run-style environments. The remaining deployment work is to build and push the image, configure secrets, deploy to Cloud Run, smoke test the live API, and document the real production trade-offs around local SQLite and file storage.
