import json
from pathlib import Path

import pytest

from scripts.run_eval import (
    EvalRunnerError,
    build_summary,
    build_score_breakdown,
    load_eval_cases,
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
        {"passed": True, "failure_categories": []},
        {"passed": False, "failure_categories": ["tool_correctness"]},
        {"passed": True, "failure_categories": []},
    ])

    assert summary == {
        "total": 3,
        "passed": 2,
        "failed": 1,
        "pass_rate": 0.6667,
        "failure_categories": {"tool_correctness": 1},
    }
