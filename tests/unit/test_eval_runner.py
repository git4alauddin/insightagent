import json
from pathlib import Path

import pytest

from scripts.run_eval import (
    EvalRunnerError,
    build_eval_request_id,
    build_headers,
    build_summary,
    build_score_breakdown,
    compare_eval_results,
    load_eval_cases,
    load_previous_results,
    save_results,
    score_eval_response,
)


def test_load_eval_cases_reads_jsonl_dataset(tmp_path: Path) -> None:
    dataset_path = tmp_path / "cases.jsonl"
    dataset_path.write_text(
        json.dumps(
            {
                "id": "case_1",
                "flow": "chat",
                "method": "POST",
                "endpoint": "/chat",
                "payload": {"message": "Hello"},
                "expected_status": 200,
            }
        )
        + "\n",
        encoding="utf-8",
    )

    cases = load_eval_cases(dataset_path)

    assert len(cases) == 1
    assert cases[0]["id"] == "case_1"


def test_load_eval_cases_reads_bundled_dataset() -> None:
    cases = load_eval_cases(Path("evals/evaluation_dataset.jsonl"))

    assert len(cases) >= 6
    assert {case["flow"] for case in cases} >= {
        "chat",
        "structured_chat",
        "tool_calling",
        "csv_analysis",
        "rag",
    }


def test_load_eval_cases_rejects_missing_required_fields(tmp_path: Path) -> None:
    dataset_path = tmp_path / "cases.jsonl"
    dataset_path.write_text('{"id":"case_1"}\n', encoding="utf-8")

    with pytest.raises(EvalRunnerError, match="missing fields"):
        load_eval_cases(dataset_path)


def test_score_eval_response_passes_when_status_and_keys_match() -> None:
    result = score_eval_response(
        {
            "id": "case_1",
            "flow": "chat",
            "expected_status": 200,
            "expected_keys": ["answer"],
        },
        200,
        {"answer": "Hello"},
        12.5,
    )

    assert result["passed"] is True
    assert result["failure_categories"] == []
    assert result["scores"]["format_validity"]["missing_keys"] == []
    assert result["usage"] == {
        "available": False,
        "input_tokens": None,
        "output_tokens": None,
        "total_tokens": None,
        "estimated_cost_usd": None,
    }
    assert result["trace"] == {
        "request_id": None,
        "response_request_id": None,
        "setup_request_ids": {},
    }


def test_score_eval_response_includes_request_trace_metadata() -> None:
    result = score_eval_response(
        {
            "id": "case_1",
            "flow": "chat",
            "expected_status": 200,
            "expected_keys": ["answer"],
        },
        200,
        {"answer": "Hello"},
        12.5,
        trace={
            "request_id": "eval_case_1_main",
            "response_request_id": "eval_case_1_main",
            "setup_request_ids": {"upload_document": "eval_case_1_setup_document"},
        },
    )

    assert result["trace"] == {
        "request_id": "eval_case_1_main",
        "response_request_id": "eval_case_1_main",
        "setup_request_ids": {"upload_document": "eval_case_1_setup_document"},
    }


def test_build_eval_request_id_sanitizes_case_and_step_names() -> None:
    assert (
        build_eval_request_id("RAG Refund Policy!", "Main Request")
        == "eval_rag_refund_policy_main_request"
    )


def test_build_headers_can_include_request_id() -> None:
    assert build_headers("test-key", request_id="eval_case_main") == {
        "x-api-key": "test-key",
        "x-request-id": "eval_case_main",
    }


def test_score_eval_response_extracts_nested_usage_metadata() -> None:
    result = score_eval_response(
        {
            "id": "case_1",
            "flow": "chat",
            "expected_status": 200,
            "expected_keys": ["answer"],
        },
        200,
        {
            "answer": "Hello",
            "usage": {
                "prompt_tokens": 12,
                "completion_tokens": 8,
                "estimated_cost_usd": 0.0004,
            },
        },
        12.5,
    )

    assert result["usage"] == {
        "available": True,
        "input_tokens": 12,
        "output_tokens": 8,
        "total_tokens": 20,
        "estimated_cost_usd": 0.0004,
    }


def test_score_eval_response_extracts_top_level_usage_metadata() -> None:
    result = score_eval_response(
        {
            "id": "case_1",
            "flow": "chat",
            "expected_status": 200,
            "expected_keys": ["answer"],
        },
        200,
        {
            "answer": "Hello",
            "input_tokens": "10",
            "output_tokens": "5",
            "total_tokens": "15",
            "cost_usd": "0.001",
        },
        12.5,
    )

    assert result["usage"] == {
        "available": True,
        "input_tokens": 10,
        "output_tokens": 5,
        "total_tokens": 15,
        "estimated_cost_usd": 0.001,
    }


def test_score_eval_response_fails_when_expected_key_is_missing() -> None:
    result = score_eval_response(
        {
            "id": "case_1",
            "flow": "chat",
            "expected_status": 200,
            "expected_keys": ["answer"],
        },
        200,
        {"message": "Hello"},
        12.5,
    )

    assert result["passed"] is False
    assert result["failure_categories"] == ["format_validity"]
    assert result["scores"]["format_validity"]["missing_keys"] == ["answer"]


def test_score_eval_response_checks_tool_correctness() -> None:
    result = score_eval_response(
        {
            "id": "case_1",
            "flow": "tool_calling",
            "expected_status": 200,
            "expected_keys": ["answer", "tool_used"],
            "scoring": {"expected_tool_used": "calculator"},
        },
        200,
        {"answer": "450", "tool_used": "date_time"},
        12.5,
    )

    assert result["passed"] is False
    assert result["failure_categories"] == ["tool_correctness"]
    assert result["scores"]["tool_correctness"]["expected"] == "calculator"
    assert result["scores"]["tool_correctness"]["actual"] == "date_time"


def test_score_eval_response_checks_relevance_terms() -> None:
    result = score_eval_response(
        {
            "id": "case_1",
            "flow": "csv_analysis",
            "expected_status": 200,
            "expected_keys": ["answer"],
            "scoring": {"expected_answer_contains": ["missing values", "city"]},
        },
        200,
        {"answer": "The city column has the most missing values."},
        12.5,
    )

    assert result["passed"] is True
    assert result["scores"]["relevance"]["missing_terms"] == []


def test_score_eval_response_fails_when_relevance_terms_are_missing() -> None:
    result = score_eval_response(
        {
            "id": "case_1",
            "flow": "csv_analysis",
            "expected_status": 200,
            "expected_keys": ["answer"],
            "scoring": {"expected_answer_contains": ["missing values", "city"]},
        },
        200,
        {"answer": "The age column has one blank value."},
        12.5,
    )

    assert result["passed"] is False
    assert result["failure_categories"] == ["relevance"]
    assert result["scores"]["relevance"]["missing_terms"] == ["missing values", "city"]


def test_score_eval_response_checks_citation_presence() -> None:
    result = score_eval_response(
        {
            "id": "case_1",
            "flow": "rag",
            "expected_status": 200,
            "expected_keys": ["answer", "sources"],
            "scoring": {
                "require_citations": True,
                "expected_source_filename": "policy.txt",
            },
        },
        200,
        {
            "answer": "Refunds are available.",
            "sources": [{"filename": "policy.txt", "chunk_id": "chunk_1"}],
        },
        12.5,
    )

    assert result["passed"] is True
    assert result["scores"]["citation_presence"]["citation_count"] == 1


def test_score_eval_response_fails_when_required_citations_are_missing() -> None:
    result = score_eval_response(
        {
            "id": "case_1",
            "flow": "rag",
            "expected_status": 200,
            "expected_keys": ["answer", "sources"],
            "scoring": {"require_citations": True},
        },
        200,
        {"answer": "Refunds are available.", "sources": []},
        12.5,
    )

    assert result["passed"] is False
    assert result["failure_categories"] == ["citation_presence"]
    assert result["scores"]["citation_presence"]["citation_count"] == 0


def test_score_eval_response_checks_citation_accuracy() -> None:
    result = score_eval_response(
        {
            "id": "case_1",
            "flow": "rag",
            "expected_status": 200,
            "expected_keys": ["answer", "sources"],
            "setup": {
                "upload_document": {
                    "filename": "policy.txt",
                    "content": "Refunds are available within 7 days.",
                    "content_type": "text/plain",
                }
            },
            "scoring": {
                "require_citations": True,
                "expected_source_filename": "policy.txt",
                "expected_citation_chunk_prefix": "doc_1_chunk_",
                "expected_citation_terms": ["Refunds are available within 7 days"],
            },
        },
        200,
        {
            "answer": "Refunds are available within 7 days.",
            "sources": [
                {
                    "filename": "policy.txt",
                    "chunk_id": "doc_1_chunk_0",
                    "similarity_score": 0.92,
                }
            ],
        },
        12.5,
    )

    assert result["passed"] is True
    assert result["scores"]["citation_accuracy"]["missing_filenames"] == []
    assert result["scores"]["citation_accuracy"]["invalid_chunk_ids"] == []
    assert result["scores"]["citation_accuracy"]["missing_reference_terms"] == []


def test_score_eval_response_fails_when_citation_accuracy_is_wrong() -> None:
    result = score_eval_response(
        {
            "id": "case_1",
            "flow": "rag",
            "expected_status": 200,
            "expected_keys": ["answer", "sources"],
            "setup": {
                "upload_document": {
                    "filename": "policy.txt",
                    "content": "Shipping takes 3 days.",
                    "content_type": "text/plain",
                }
            },
            "scoring": {
                "require_citations": True,
                "expected_source_filename": "policy.txt",
                "expected_citation_chunk_prefix": "doc_1_chunk_",
                "expected_citation_terms": ["Refunds are available within 7 days"],
            },
        },
        200,
        {
            "answer": "Refunds are available within 7 days.",
            "sources": [
                {
                    "filename": "wrong.txt",
                    "chunk_id": "other_doc_chunk_0",
                    "similarity_score": 0.92,
                }
            ],
        },
        12.5,
    )

    assert result["passed"] is False
    assert result["failure_categories"] == ["citation_accuracy"]
    assert result["scores"]["citation_accuracy"]["missing_filenames"] == [
        "policy.txt"
    ]
    assert result["scores"]["citation_accuracy"]["invalid_chunk_ids"] == [
        "other_doc_chunk_0"
    ]
    assert result["scores"]["citation_accuracy"]["missing_reference_terms"] == [
        "Refunds are available within 7 days"
    ]


def test_score_eval_response_checks_groundedness_against_reference_text() -> None:
    result = score_eval_response(
        {
            "id": "case_1",
            "flow": "rag",
            "expected_status": 200,
            "expected_keys": ["answer", "sources"],
            "setup": {
                "upload_document": {
                    "filename": "policy.txt",
                    "content": "Refunds are available within 7 days.",
                    "content_type": "text/plain",
                }
            },
            "scoring": {
                "groundedness_terms": ["Refunds are available within 7 days"]
            },
        },
        200,
        {
            "answer": "Refunds are available within 7 days.",
            "sources": [{"filename": "policy.txt", "chunk_id": "chunk_1"}],
        },
        12.5,
    )

    assert result["passed"] is True
    assert result["scores"]["groundedness"]["missing_from_answer"] == []
    assert result["scores"]["groundedness"]["missing_from_reference"] == []


def test_score_eval_response_fails_when_groundedness_terms_are_not_in_reference() -> None:
    result = score_eval_response(
        {
            "id": "case_1",
            "flow": "rag",
            "expected_status": 200,
            "expected_keys": ["answer", "sources"],
            "setup": {
                "upload_document": {
                    "filename": "policy.txt",
                    "content": "Shipping takes 3 days.",
                    "content_type": "text/plain",
                }
            },
            "scoring": {
                "groundedness_terms": ["Refunds are available within 7 days"]
            },
        },
        200,
        {
            "answer": "Refunds are available within 7 days.",
            "sources": [{"filename": "policy.txt", "chunk_id": "chunk_1"}],
        },
        12.5,
    )

    assert result["passed"] is False
    assert result["failure_categories"] == ["groundedness"]
    assert result["scores"]["groundedness"]["missing_from_reference"] == [
        "Refunds are available within 7 days"
    ]


def test_score_eval_response_checks_insufficient_context_safety() -> None:
    result = score_eval_response(
        {
            "id": "case_1",
            "flow": "rag",
            "expected_status": 200,
            "expected_keys": ["answer", "sources", "status"],
            "scoring": {
                "expected_response_status": "insufficient_context",
                "require_no_citations": True,
            },
        },
        200,
        {
            "answer": "I do not have enough context.",
            "sources": [],
            "status": "insufficient_context",
        },
        12.5,
    )

    assert result["passed"] is True
    assert result["scores"]["insufficient_context_safety"]["citation_count"] == 0


def test_score_eval_response_fails_unsupported_confident_answer_with_citations() -> None:
    result = score_eval_response(
        {
            "id": "case_1",
            "flow": "rag",
            "expected_status": 200,
            "expected_keys": ["answer", "sources", "status"],
            "scoring": {
                "expected_response_status": "insufficient_context",
                "require_no_citations": True,
            },
        },
        200,
        {
            "answer": "The warranty lasts for two years.",
            "sources": [{"filename": "policy.txt", "chunk_id": "chunk_1"}],
            "status": "success",
        },
        12.5,
    )

    assert result["passed"] is False
    assert result["failure_categories"] == [
        "response_status",
        "insufficient_context_safety",
    ]
    assert result["scores"]["response_status"]["actual"] == "success"
    assert result["scores"]["insufficient_context_safety"]["citation_count"] == 1


def test_build_score_breakdown_checks_analysis_intent() -> None:
    scores = build_score_breakdown(
        {
            "id": "case_1",
            "flow": "csv_analysis",
            "expected_status": 200,
            "expected_keys": ["analysis_trace"],
            "scoring": {"expected_analysis_intent": "missing_value_analysis"},
        },
        200,
        {"analysis_trace": {"intent": "missing_value_analysis"}},
    )

    assert scores["analysis_intent"]["passed"] is True


def test_build_summary_counts_pass_fail_and_rate() -> None:
    summary = build_summary([
        {
            "passed": True,
            "failure_categories": [],
            "usage": {
                "available": True,
                "input_tokens": 10,
                "output_tokens": 5,
                "total_tokens": 15,
                "estimated_cost_usd": 0.001,
            },
        },
        {
            "passed": False,
            "failure_categories": ["tool_correctness"],
            "usage": {
                "available": True,
                "input_tokens": 20,
                "output_tokens": 10,
                "total_tokens": 30,
                "estimated_cost_usd": 0.0025,
            },
        },
        {
            "passed": True,
            "failure_categories": [],
            "usage": {
                "available": False,
                "input_tokens": None,
                "output_tokens": None,
                "total_tokens": None,
                "estimated_cost_usd": None,
            },
        },
    ])

    assert summary == {
        "total": 3,
        "passed": 2,
        "failed": 1,
        "pass_rate": 0.6667,
        "failure_categories": {"tool_correctness": 1},
        "usage": {
            "available_cases": 2,
            "unavailable_cases": 1,
            "input_tokens": 30,
            "output_tokens": 15,
            "total_tokens": 45,
            "estimated_cost_usd": 0.0035,
        },
    }


def test_load_previous_results_reads_saved_json(tmp_path: Path) -> None:
    previous_path = tmp_path / "previous.json"
    previous_path.write_text(
        json.dumps({"summary": {"pass_rate": 1.0}, "results": []}),
        encoding="utf-8",
    )

    previous = load_previous_results(previous_path)

    assert previous["summary"]["pass_rate"] == 1.0


def test_load_previous_results_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(EvalRunnerError, match="Previous results not found"):
        load_previous_results(tmp_path / "missing.json")


def test_compare_eval_results_reports_regression_and_improvement() -> None:
    previous_output = {
        "summary": {"pass_rate": 0.5},
        "results": [
            {"id": "case_regressed", "passed": True},
            {"id": "case_improved", "passed": False},
            {"id": "case_removed", "passed": True},
        ],
    }
    current_results = [
        {
            "id": "case_regressed",
            "passed": False,
            "failure_categories": ["format_validity"],
        },
        {"id": "case_improved", "passed": True, "failure_categories": []},
        {"id": "case_added", "passed": True, "failure_categories": []},
    ]

    comparison = compare_eval_results(current_results, previous_output)

    assert comparison == {
        "previous_pass_rate": 0.5,
        "current_pass_rate": 0.6667,
        "pass_rate_delta": 0.1667,
        "new_failures": ["case_regressed"],
        "new_passes": ["case_improved"],
        "added_cases": ["case_added"],
        "removed_cases": ["case_removed"],
    }


def test_save_results_can_include_comparison(tmp_path: Path) -> None:
    results_path = tmp_path / "latest.json"
    save_results(
        [{"id": "case_1", "passed": True, "failure_categories": []}],
        results_path,
        comparison={"pass_rate_delta": 0.25},
    )

    saved = json.loads(results_path.read_text(encoding="utf-8"))

    assert saved["summary"]["passed"] == 1
    assert saved["comparison"]["pass_rate_delta"] == 0.25
