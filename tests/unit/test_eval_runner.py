import json
from pathlib import Path

import pytest

from scripts.run_eval import (
    EvalRunnerError,
    build_summary,
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
    assert result["missing_keys"] == []


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
    assert result["missing_keys"] == ["answer"]


def test_build_summary_counts_pass_fail_and_rate() -> None:
    summary = build_summary([
        {"passed": True},
        {"passed": False},
        {"passed": True},
    ])

    assert summary == {
        "total": 3,
        "passed": 2,
        "failed": 1,
        "pass_rate": 0.6667,
    }
