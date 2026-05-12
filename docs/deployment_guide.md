# InsightAgent Deployment Guide

This guide documents how InsightAgent was deployed to Google Cloud Run and why each deployment step mattered.

It is written as a practical reference for repeating or explaining the deployment journey.

## Final Deployment Result

Live API:

```text
https://insightagent-1089133393572.us-central1.run.app
```

Container image:

```text
us-central1-docker.pkg.dev/insightagent-496120/insightagent/insightagent:v10
```

Cloud project:

```text
insightagent-496120
```

Region:

```text
us-central1
```

## Why Cloud Run

Cloud Run was chosen because it fits the project well:

- deploys a Dockerized FastAPI backend
- scales down when unused
- works well for portfolio APIs
- supports environment variables and Secret Manager
- provides a public HTTPS URL without managing servers

The goal was not to build complex cloud infrastructure. The goal was to prove the completed backend can run outside the local machine with production-style configuration.

## Deployment Components

The deployment used:

- Docker for packaging the FastAPI app
- Artifact Registry for storing the container image
- Cloud Build for building and pushing the image
- Secret Manager for API keys
- Cloud Run for hosting the deployed service

## 1. Repo And Docker Readiness

Before deploying, the repo needed to avoid committing local runtime artifacts.

`.gitignore` was updated to ignore:

```text
insightagent.db
uploads/
logs/
```

Why:

- `insightagent.db` is local SQLite runtime state
- `uploads/` contains user-uploaded files
- `logs/` contains generated runtime logs
- none of these should be source-controlled

The Docker startup command was updated to respect Cloud Run's runtime port:

```dockerfile
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
```

Why:

- Cloud Run injects `PORT=8080`
- local Docker can still default to `8000`
- one image can work locally and in Cloud Run

## 2. Local Docker Verification

The image was built locally:

```powershell
docker build -t insightagent:deploy-verify .
```

The container was run locally with production-like settings:

```powershell
docker run --rm -d --name insightagent-deploy-verify -p 18080:8080 `
  -e PORT=8080 `
  -e APP_ENV=production `
  -e APP_VERSION=v10 `
  -e DOCS_ENABLED=false `
  -e API_KEY=deploy-test-key `
  -e LLM_API_KEY=dummy-key `
  -e RATE_LIMIT_ENABLED=true `
  insightagent:deploy-verify
```

Smoke tests:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:18080/health
Invoke-RestMethod -Uri http://127.0.0.1:18080/ready
```

Docs-disabled check:

```powershell
try {
  Invoke-RestMethod -Uri http://127.0.0.1:18080/docs
} catch {
  $_.Exception.Response.StatusCode.value__
}
```

Missing API-key check:

```powershell
try {
  Invoke-RestMethod -Method Post `
    -Uri http://127.0.0.1:18080/chat `
    -ContentType "application/json" `
    -Body '{"message":"hello"}'
} catch {
  $_.Exception.Response.StatusCode.value__
  $_.ErrorDetails.Message
}
```

Valid API-key check:

```powershell
$headers = @{ "x-api-key" = "deploy-test-key" }

Invoke-RestMethod -Method Post `
  -Uri http://127.0.0.1:18080/sessions `
  -Headers $headers `
  -ContentType "application/json" `
  -Body '{"title":"deploy smoke"}'
```

Container cleanup:

```powershell
docker stop insightagent-deploy-verify
```

What this proved:

- Docker image builds
- app starts inside the container
- app respects `PORT`
- `/health` and `/ready` work
- production docs can be disabled
- private endpoints reject missing API keys
- authenticated private endpoint works

## 3. Google Cloud Setup

In Google Cloud Console, the project was selected:

```text
insightagent-496120
```

Required services:

- Cloud Run API
- Artifact Registry API
- Secret Manager API
- Cloud Build API

These can be enabled through the GUI or Cloud Shell:

```bash
gcloud services enable cloudbuild.googleapis.com artifactregistry.googleapis.com run.googleapis.com secretmanager.googleapis.com
```

## 4. Secret Manager

Two secrets were created in Secret Manager:

```text
insightagent-api-key
insightagent-llm-api-key
```

Why:

- `insightagent-api-key` becomes the deployed service API key used by clients through `x-api-key`
- `insightagent-llm-api-key` is used internally by the backend to call the LLM provider
- secrets should not be committed into Git or hardcoded into Docker images

Important safety note:

If a real provider key appears in chat, screenshots, logs, or shared context, rotate it and update Secret Manager.

## 5. Artifact Registry

Artifact Registry repository:

```text
Name: insightagent
Format: Docker
Region: us-central1
```

Why:

- Cloud Run deploys from a container image
- Artifact Registry stores that image in the same region
- image version/tag gives a stable deployment target

## 6. Build And Push Image

Cloud Shell was used with the GitHub repo:

```bash
gcloud config set project insightagent-496120
gcloud auth configure-docker us-central1-docker.pkg.dev

git clone https://github.com/git4alauddin/insightagent.git
cd insightagent
```

Manual Docker build/push path:

```bash
docker build -t us-central1-docker.pkg.dev/insightagent-496120/insightagent/insightagent:v10 .

docker push us-central1-docker.pkg.dev/insightagent-496120/insightagent/insightagent:v10
```

If direct Docker push has network or auth issues, Cloud Build can build and push:

```bash
gcloud builds submit \
  --tag us-central1-docker.pkg.dev/insightagent-496120/insightagent/insightagent:v10
```

Final Cloud Build result:

```text
STATUS: SUCCESS
IMAGES: us-central1-docker.pkg.dev/insightagent-496120/insightagent/insightagent:v10
```

## 7. Cloud Run GUI Deployment

Cloud Run setup:

```text
Service name: insightagent
Region: us-central1
Image: us-central1-docker.pkg.dev/insightagent-496120/insightagent/insightagent:v10
Authentication: allow unauthenticated invocations
```

Why allow unauthenticated invocations:

- Cloud Run public access exposes the service URL
- the app still protects private endpoints using `x-api-key`
- `/health` and `/ready` stay publicly reachable for service checks

Environment variables:

```text
APP_ENV=production
APP_VERSION=v10
DOCS_ENABLED=false
RATE_LIMIT_ENABLED=true
CORS_ALLOWED_ORIGINS=<non-wildcard-origin>
```

Secrets mapped as environment variables:

```text
API_KEY -> insightagent-api-key:latest
LLM_API_KEY -> insightagent-llm-api-key:latest
```

## 8. Startup Issue And Fix

Initial Cloud Run deployment failed with a generic message:

```text
The user-provided container failed to start and listen on the port defined by PORT=8080.
```

Root cause:

```text
APP_ENV=production
CORS_ALLOWED_ORIGINS=*
```

The app intentionally rejects wildcard CORS origins in production.

Why this is good:

- wildcard CORS in production can be unsafe
- the backend fails fast instead of silently accepting unsafe config

Why Cloud Run message looked confusing:

- the app crashed during startup
- because the app exited before listening on `PORT=8080`, Cloud Run reported it as a port/startup failure

Fix:

```text
CORS_ALLOWED_ORIGINS=<specific non-wildcard origin>
```

After redeploying with a non-wildcard CORS origin, Cloud Run started successfully.

## 9. Cloud Run Smoke Tests

Live URL:

```text
https://insightagent-1089133393572.us-central1.run.app
```

Health:

```powershell
Invoke-RestMethod -Uri https://insightagent-1089133393572.us-central1.run.app/health
```

Result:

```text
status: ok
service: InsightAgent
version: v10
```

Readiness:

```powershell
Invoke-RestMethod -Uri https://insightagent-1089133393572.us-central1.run.app/ready
```

Result:

```text
status: ready
```

Docs disabled:

```powershell
try {
  Invoke-RestMethod -Uri https://insightagent-1089133393572.us-central1.run.app/docs
} catch {
  $_.Exception.Response.StatusCode.value__
}
```

Expected:

```text
404
```

Unauthorized private endpoint:

```powershell
try {
  Invoke-RestMethod -Method Post `
    -Uri https://insightagent-1089133393572.us-central1.run.app/chat `
    -ContentType "application/json" `
    -Body '{"message":"hello"}'
} catch {
  $_.Exception.Response.StatusCode.value__
  $_.ErrorDetails.Message
}
```

Expected:

```text
401
UNAUTHORIZED
```

Authenticated smoke test from Cloud Shell:

```bash
API_KEY=$(gcloud secrets versions access latest --secret=insightagent-api-key)

curl -s -X POST \
  "https://insightagent-1089133393572.us-central1.run.app/sessions" \
  -H "x-api-key: ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"title":"cloud smoke"}'
```

Result:

```json
{
  "session_id": "3c4ee7ce-11ff-43b1-83a3-694318077d30",
  "status": "success"
}
```

What this proved:

- deployed public health endpoint works
- deployed readiness endpoint works
- production docs are disabled
- protected endpoints reject missing API keys
- Secret Manager-backed API key works
- deployed app can create session state

## 10. Storage Limitation

InsightAgent currently uses:

- local SQLite
- local upload storage

On Cloud Run, local filesystem persistence is not durable across instances, revisions, or restarts.

Current portfolio decision:

- acceptable for demo/portfolio deployment
- documented as a limitation

Production upgrade path:

- PostgreSQL for sessions/dataset/document metadata
- Cloud Storage for uploaded files
- managed vector database or pgvector for larger RAG workloads

## 11. Deployment Completion Checklist

Completed:

- repo cleanup for deployment artifacts
- Docker runtime respects `PORT`
- local Docker image builds
- local production-like container smoke tests pass
- GCP project configured
- Artifact Registry image created
- Secret Manager keys configured
- Cloud Run service deployed
- production CORS issue fixed
- deployed health/readiness pass
- deployed docs are disabled
- deployed auth failure path works
- deployed authenticated endpoint works
- README and deployment docs updated

Remaining optional portfolio tasks:

- rotate any provider key exposed during chat/screenshots
- record demo video or screenshots
- choose and add final license

## Interview Explanation

After completing the backend, I deployed InsightAgent to Cloud Run to prove it works outside the local machine. I first cleaned the repo so local artifacts like SQLite DB files, uploads, and logs would not be committed. Then I updated the Docker runtime to respect Cloud Run's injected `PORT` while preserving local defaults. I built and smoke-tested the image locally with production-style settings, then used Cloud Build and Artifact Registry to produce the deployable image. In Cloud Run, I configured production env vars and mapped API secrets from Secret Manager. The first revision failed because production CORS rejected a wildcard origin, which was a good safety check; after replacing it with a specific origin, the service deployed successfully. I verified the live API through health, readiness, disabled docs, unauthorized access, and authenticated session creation checks.
