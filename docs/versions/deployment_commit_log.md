# Deployment Commit Log

### `7a6dec6` - `deploy: prepare repo and docker runtime for cloud`

**What we did**

- Added local runtime artifacts to `.gitignore`.
- Ignored `insightagent.db`, `uploads/`, and `logs/`.
- Updated the Docker startup command to use `${PORT:-8000}`.
- Removed the generated local `insightagent.db` artifact.

**What it solved / took care of**

- Prevented local DB/upload/log state from entering Git.
- Made the container more compatible with Cloud Run's runtime port model.
- Preserved local Docker behavior through the `8000` default.
- Created a cleaner starting point for Docker and Cloud Run verification.

### `9f9cfb4` - `deploy: verify docker runtime locally`

**What we did**

- Built Docker image `insightagent:deploy-verify`.
- Ran the container locally with production-like settings and `PORT=8080`.
- Verified `/health`, `/ready`, disabled docs, missing API-key failure, and valid API-key success.
- Stopped the temporary verification container.

**What it solved / took care of**

- Proved the image builds successfully.
- Proved the app starts correctly inside the container.
- Proved the container respects runtime port configuration.
- Proved production docs disabling and API-key protection work in the container runtime.

### `<pending>` - `deploy: verify cloud run deployment`

**What we did**

- Built and pushed the deployment image through Google Cloud Build.
- Deployed image `us-central1-docker.pkg.dev/insightagent-496120/insightagent/insightagent:v10` to Cloud Run.
- Fixed the production startup failure caused by wildcard CORS in production config.
- Verified deployed `/health`, `/ready`, disabled `/docs`, unauthorized `/chat`, and authenticated `/sessions`.

**What it solved / took care of**

- Proved the project runs outside the local machine.
- Confirmed Secret Manager-backed `API_KEY` works with Cloud Run.
- Confirmed the app fails safely on unauthenticated protected endpoints.
- Confirmed production docs exposure is disabled on the live service.
