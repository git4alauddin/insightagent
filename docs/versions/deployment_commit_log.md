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

### `<pending>` - `deploy: verify docker runtime locally`

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
