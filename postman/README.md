# InsightAgent Postman Collection

This folder contains a Postman collection for exploring the InsightAgent API locally or on Cloud Run.

## Files

- `InsightAgent.postman_collection.json`
- `InsightAgent.local.example.postman_environment.json`
- `InsightAgent.cloud.example.postman_environment.json`

## Setup

1. Import the collection into Postman.
2. Import either the local or cloud example environment.
3. Duplicate the environment if you want to keep private local values.
4. Set `api_key` to your service API key.
5. Select the environment.
6. Run requests in folder order.

## Variables

| Variable | Purpose |
| --- | --- |
| `base_url` | Local or Cloud Run API base URL. |
| `api_key` | Service API key sent as `x-api-key`. |
| `session_id` | Saved after creating a session. |
| `dataset_id` | Saved after uploading a CSV dataset. |
| `document_id` | Saved after uploading a document. |

## Upload Requests

For CSV and document upload requests, choose a local file in Postman before sending.

Do not commit real API keys, generated IDs, or local test files.
