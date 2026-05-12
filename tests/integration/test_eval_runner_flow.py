import json
from pathlib import Path

import app.db.database as database_module
import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from scripts.run_eval import build_summary, run_eval_cases_with_client, save_results


@pytest.fixture(autouse=True)
def isolated_db_and_uploads(monkeypatch, tmp_path):
    db_path = tmp_path / "test_eval_runner_flow.db"
    upload_dir = tmp_path / "uploads"
    monkeypatch.setattr(database_module, "DB_PATH", db_path)
    monkeypatch.setattr(settings, "upload_dir", str(upload_dir))
    monkeypatch.setattr(settings, "api_key", "test-api-key")
    return db_path


def test_eval_runner_executes_csv_and_rag_cases_in_process(tmp_path: Path) -> None:
    cases = [
        {
            "id": "csv_missing_values_in_process",
            "flow": "csv_analysis",
            "method": "POST",
            "endpoint": "/datasets/{dataset_id}/ask",
            "setup": {
                "upload_dataset": {
                    "filename": "people.csv",
                    "content": "name,age,city\nalice,30,\nbob,,kolkata\ncharlie,40,\n",
                    "content_type": "text/csv",
                }
            },
            "payload": {"question": "Which column has the most missing values?"},
            "expected_status": 200,
            "expected_keys": [
                "answer",
                "dataset_id",
                "tool_used",
                "analysis_trace",
                "status",
            ],
            "scoring": {
                "expected_response_status": "success",
                "expected_tool_used": "missing_value_tool",
                "expected_analysis_intent": "missing_value_analysis",
                "expected_answer_contains": ["missing values"],
            },
        },
        {
            "id": "rag_refund_policy_in_process",
            "flow": "rag",
            "method": "POST",
            "endpoint": "/documents/{document_id}/ask",
            "setup": {
                "upload_document": {
                    "filename": "policy.txt",
                    "content": "Refunds are available within 7 days. Shipping takes 3 days.",
                    "content_type": "text/plain",
                }
            },
            "payload": {"question": "What is the refund policy?"},
            "expected_status": 200,
            "expected_keys": ["answer", "document_id", "sources", "status"],
            "scoring": {
                "expected_response_status": "success",
                "require_citations": True,
                "expected_source_filename": "policy.txt",
                "expected_citation_terms": ["Refunds are available within 7 days"],
                "expected_answer_contains": ["Refunds are available within 7 days"],
                "groundedness_terms": ["Refunds are available within 7 days"],
            },
        },
    ]
    client = TestClient(app)

    results = run_eval_cases_with_client(cases, client, api_key="test-api-key")
    summary = build_summary(results)
    results_path = tmp_path / "latest_eval_results.json"
    save_results(results, results_path)
    saved = json.loads(results_path.read_text(encoding="utf-8"))

    assert summary == {
        "total": 2,
        "passed": 2,
        "failed": 0,
        "pass_rate": 1.0,
        "failure_categories": {},
        "usage": {
            "available_cases": 0,
            "unavailable_cases": 2,
            "input_tokens": None,
            "output_tokens": None,
            "total_tokens": None,
            "estimated_cost_usd": None,
        },
    }
    assert [result["id"] for result in results] == [
        "csv_missing_values_in_process",
        "rag_refund_policy_in_process",
    ]
    assert all(result["passed"] for result in results)
    assert results[0]["trace"] == {
        "request_id": "eval_csv_missing_values_in_process_main",
        "response_request_id": "eval_csv_missing_values_in_process_main",
        "setup_request_ids": {
            "upload_dataset": "eval_csv_missing_values_in_process_setup_dataset"
        },
    }
    assert results[1]["trace"] == {
        "request_id": "eval_rag_refund_policy_in_process_main",
        "response_request_id": "eval_rag_refund_policy_in_process_main",
        "setup_request_ids": {
            "upload_document": "eval_rag_refund_policy_in_process_setup_document"
        },
    }
    assert saved["summary"] == summary
    assert saved["results"][0]["trace"]["request_id"] == (
        "eval_csv_missing_values_in_process_main"
    )
