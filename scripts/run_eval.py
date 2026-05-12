import argparse
import json
import time
from pathlib import Path
from typing import Any

import httpx


DEFAULT_BASE_URL = "http://127.0.0.1:8000"
DEFAULT_DATASET_PATH = Path("evals/evaluation_dataset.jsonl")
DEFAULT_RESULTS_PATH = Path("evals/results/latest_eval_results.json")
REQUEST_ID_HEADER = "x-request-id"


class EvalRunnerError(Exception):
    pass


def load_eval_cases(dataset_path: Path) -> list[dict[str, Any]]:
    if not dataset_path.exists():
        raise EvalRunnerError(f"Evaluation dataset not found: {dataset_path}")

    cases: list[dict[str, Any]] = []
    lines = dataset_path.read_text(encoding="utf-8").splitlines()
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue

        try:
            case = json.loads(line)
        except json.JSONDecodeError as exc:
            raise EvalRunnerError(f"Invalid JSONL at line {line_number}.") from exc

        validate_eval_case(case, line_number)
        cases.append(case)

    return cases


def validate_eval_case(case: dict[str, Any], line_number: int) -> None:
    required_fields = {
        "id",
        "flow",
        "method",
        "endpoint",
        "payload",
        "expected_status",
    }
    missing_fields = sorted(required_fields - set(case))
    if missing_fields:
        raise EvalRunnerError(
            f"Evaluation case line {line_number} missing fields: "
            f"{', '.join(missing_fields)}"
        )


def run_eval_cases(
    cases: list[dict[str, Any]],
    *,
    base_url: str,
    api_key: str,
    timeout_seconds: float = 30.0,
) -> list[dict[str, Any]]:
    with httpx.Client(base_url=base_url, timeout=timeout_seconds) as client:
        return run_eval_cases_with_client(cases, client, api_key=api_key)


def run_eval_cases_with_client(
    cases: list[dict[str, Any]],
    client: Any,
    *,
    api_key: str,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for case in cases:
        results.append(run_eval_case(client, case, api_key=api_key))
    return results


def run_eval_case(
    client: Any,
    case: dict[str, Any],
    *,
    api_key: str,
) -> dict[str, Any]:
    prepared_case = prepare_case(client, case, api_key=api_key)
    request_id = prepared_case["trace"]["request_id"]
    started_at = time.perf_counter()
    response = client.request(
        prepared_case["method"],
        prepared_case["endpoint"],
        headers=build_headers(api_key, request_id=request_id),
        json=prepared_case["payload"],
    )
    latency_ms = round((time.perf_counter() - started_at) * 1000, 2)

    try:
        response_body: Any = response.json()
    except ValueError:
        response_body = response.text

    trace = {
        **prepared_case["trace"],
        "response_request_id": response.headers.get(REQUEST_ID_HEADER),
    }
    return score_eval_response(
        case,
        response.status_code,
        response_body,
        latency_ms,
        trace=trace,
    )


def prepare_case(
    client: Any,
    case: dict[str, Any],
    *,
    api_key: str,
) -> dict[str, Any]:
    endpoint = str(case["endpoint"])
    setup = case.get("setup", {})
    case_id = str(case["id"])
    setup_request_ids: dict[str, str | None] = {}

    if "upload_dataset" in setup:
        request_id = build_eval_request_id(case_id, "setup_dataset")
        dataset_id = upload_setup_file(
            client,
            "/datasets/upload",
            setup["upload_dataset"],
            api_key=api_key,
            id_key="dataset_id",
            request_id=request_id,
        )
        endpoint = endpoint.replace("{dataset_id}", dataset_id)
        setup_request_ids["upload_dataset"] = request_id

    if "upload_document" in setup:
        request_id = build_eval_request_id(case_id, "setup_document")
        document_id = upload_setup_file(
            client,
            "/documents/upload",
            setup["upload_document"],
            api_key=api_key,
            id_key="document_id",
            request_id=request_id,
        )
        endpoint = endpoint.replace("{document_id}", document_id)
        setup_request_ids["upload_document"] = request_id

    return {
        "method": case["method"],
        "endpoint": endpoint,
        "payload": case["payload"],
        "trace": {
            "request_id": build_eval_request_id(case_id, "main"),
            "response_request_id": None,
            "setup_request_ids": setup_request_ids,
        },
    }


def upload_setup_file(
    client: Any,
    endpoint: str,
    upload_spec: dict[str, str],
    *,
    api_key: str,
    id_key: str,
    request_id: str,
) -> str:
    files = {
        "file": (
            upload_spec["filename"],
            upload_spec["content"].encode("utf-8"),
            upload_spec["content_type"],
        )
    }
    response = client.post(
        endpoint,
        headers=build_headers(api_key, request_id=request_id),
        files=files,
    )
    response.raise_for_status()
    response_body = response.json()
    return str(response_body[id_key])


def score_eval_response(
    case: dict[str, Any],
    status_code: int,
    response_body: Any,
    latency_ms: float,
    trace: dict[str, Any] | None = None,
) -> dict[str, Any]:
    expected_status = int(case["expected_status"])
    scores = build_score_breakdown(case, status_code, response_body)
    failure_categories = build_failure_categories(scores)
    passed = not failure_categories

    return {
        "id": case["id"],
        "flow": case["flow"],
        "status_code": status_code,
        "expected_status": expected_status,
        "latency_ms": latency_ms,
        "passed": passed,
        "scores": scores,
        "failure_categories": failure_categories,
        "trace": normalize_trace_metadata(trace),
        "usage": extract_usage_metadata(response_body),
        "response": response_body,
    }


def normalize_trace_metadata(trace: dict[str, Any] | None) -> dict[str, Any]:
    if trace is None:
        return {
            "request_id": None,
            "response_request_id": None,
            "setup_request_ids": {},
        }

    setup_request_ids = trace.get("setup_request_ids", {})
    if not isinstance(setup_request_ids, dict):
        setup_request_ids = {}

    return {
        "request_id": trace.get("request_id"),
        "response_request_id": trace.get("response_request_id"),
        "setup_request_ids": setup_request_ids,
    }


def build_score_breakdown(
    case: dict[str, Any],
    status_code: int,
    response_body: Any,
) -> dict[str, dict[str, Any]]:
    expected_status = int(case["expected_status"])
    scoring = case.get("scoring", {})

    scores = {
        "http_status": {
            "passed": status_code == expected_status,
            "expected": expected_status,
            "actual": status_code,
        },
        "format_validity": score_format_validity(case, response_body),
    }

    if "expected_response_status" in scoring:
        scores["response_status"] = score_response_status(scoring, response_body)

    if "expected_answer_contains" in scoring:
        scores["relevance"] = score_relevance(scoring, response_body)

    if "expected_tool_used" in scoring:
        scores["tool_correctness"] = score_tool_correctness(scoring, response_body)

    if "expected_analysis_intent" in scoring:
        scores["analysis_intent"] = score_analysis_intent(scoring, response_body)

    if scoring.get("require_citations"):
        scores["citation_presence"] = score_citation_presence(scoring, response_body)

    if has_citation_accuracy_expectations(scoring):
        scores["citation_accuracy"] = score_citation_accuracy(
            case,
            scoring,
            response_body,
        )

    if "groundedness_terms" in scoring:
        scores["groundedness"] = score_groundedness(case, scoring, response_body)

    if scoring.get("require_no_citations"):
        scores["insufficient_context_safety"] = score_no_citations(response_body)

    return scores


def score_format_validity(
    case: dict[str, Any],
    response_body: Any,
) -> dict[str, Any]:
    expected_keys = case.get("expected_keys", [])
    missing_keys = [
        key
        for key in expected_keys
        if not isinstance(response_body, dict) or key not in response_body
    ]

    return {
        "passed": not missing_keys,
        "missing_keys": missing_keys,
    }


def score_response_status(
    scoring: dict[str, Any],
    response_body: Any,
) -> dict[str, Any]:
    expected_status = scoring["expected_response_status"]
    actual_status = (
        response_body.get("status")
        if isinstance(response_body, dict)
        else None
    )
    return {
        "passed": actual_status == expected_status,
        "expected": expected_status,
        "actual": actual_status,
    }


def score_relevance(
    scoring: dict[str, Any],
    response_body: Any,
) -> dict[str, Any]:
    expected_terms = normalize_expected_terms(scoring["expected_answer_contains"])
    answer = extract_answer_text(response_body)
    normalized_answer = normalize_text(answer)
    missing_terms = [
        term for term in expected_terms if normalize_text(term) not in normalized_answer
    ]

    return {
        "passed": not missing_terms,
        "expected_terms": expected_terms,
        "missing_terms": missing_terms,
    }


def score_tool_correctness(
    scoring: dict[str, Any],
    response_body: Any,
) -> dict[str, Any]:
    expected_tool = scoring["expected_tool_used"]
    actual_tool = response_body.get("tool_used") if isinstance(response_body, dict) else None
    return {
        "passed": actual_tool == expected_tool,
        "expected": expected_tool,
        "actual": actual_tool,
    }


def score_analysis_intent(
    scoring: dict[str, Any],
    response_body: Any,
) -> dict[str, Any]:
    expected_intent = scoring["expected_analysis_intent"]
    trace = (
        response_body.get("analysis_trace", {})
        if isinstance(response_body, dict)
        else {}
    )
    actual_intent = trace.get("intent") if isinstance(trace, dict) else None
    return {
        "passed": actual_intent == expected_intent,
        "expected": expected_intent,
        "actual": actual_intent,
    }


def score_citation_presence(
    scoring: dict[str, Any],
    response_body: Any,
) -> dict[str, Any]:
    sources = response_body.get("sources", []) if isinstance(response_body, dict) else []
    valid_sources = sources if isinstance(sources, list) else []
    has_citations = bool(valid_sources)

    return {
        "passed": has_citations,
        "citation_count": len(valid_sources),
    }


def score_citation_accuracy(
    case: dict[str, Any],
    scoring: dict[str, Any],
    response_body: Any,
) -> dict[str, Any]:
    sources = response_body.get("sources", []) if isinstance(response_body, dict) else []
    valid_sources = [source for source in sources if isinstance(source, dict)]
    expected_filenames = get_expected_citation_filenames(scoring)
    actual_filenames = {
        str(source.get("filename"))
        for source in valid_sources
        if source.get("filename") is not None
    }
    missing_filenames = [
        filename for filename in expected_filenames if filename not in actual_filenames
    ]

    expected_chunk_prefix = scoring.get("expected_citation_chunk_prefix")
    invalid_chunk_ids: list[str] = []
    if expected_chunk_prefix is not None:
        prefix = str(expected_chunk_prefix)
        invalid_chunk_ids = [
            str(source.get("chunk_id"))
            for source in valid_sources
            if not str(source.get("chunk_id", "")).startswith(prefix)
        ]

    expected_terms = normalize_expected_terms(scoring.get("expected_citation_terms", []))
    reference_text = normalize_text(extract_reference_text(case, scoring))
    missing_reference_terms = [
        term for term in expected_terms if normalize_text(term) not in reference_text
    ]

    return {
        "passed": (
            bool(valid_sources)
            and not missing_filenames
            and not invalid_chunk_ids
            and not missing_reference_terms
        ),
        "expected_filenames": expected_filenames,
        "actual_filenames": sorted(actual_filenames),
        "missing_filenames": missing_filenames,
        "expected_chunk_prefix": expected_chunk_prefix,
        "invalid_chunk_ids": invalid_chunk_ids,
        "expected_terms": expected_terms,
        "missing_reference_terms": missing_reference_terms,
    }


def score_groundedness(
    case: dict[str, Any],
    scoring: dict[str, Any],
    response_body: Any,
) -> dict[str, Any]:
    groundedness_terms = normalize_expected_terms(scoring["groundedness_terms"])
    answer = normalize_text(extract_answer_text(response_body))
    reference_text = normalize_text(extract_reference_text(case, scoring))
    missing_from_answer = [
        term for term in groundedness_terms if normalize_text(term) not in answer
    ]
    missing_from_reference = [
        term for term in groundedness_terms if normalize_text(term) not in reference_text
    ]

    return {
        "passed": not missing_from_answer and not missing_from_reference,
        "expected_terms": groundedness_terms,
        "missing_from_answer": missing_from_answer,
        "missing_from_reference": missing_from_reference,
    }


def score_no_citations(response_body: Any) -> dict[str, Any]:
    sources = response_body.get("sources", []) if isinstance(response_body, dict) else []
    valid_sources = sources if isinstance(sources, list) else []
    return {
        "passed": valid_sources == [],
        "citation_count": len(valid_sources),
    }


def normalize_expected_terms(value: Any) -> list[str]:
    if value is None:
        return []

    if isinstance(value, str):
        return [value]

    if isinstance(value, list):
        return [str(term) for term in value]

    return [str(value)]


def has_citation_accuracy_expectations(scoring: dict[str, Any]) -> bool:
    return any(
        key in scoring
        for key in (
            "expected_source_filename",
            "expected_citation_filenames",
            "expected_citation_chunk_prefix",
            "expected_citation_terms",
        )
    )


def get_expected_citation_filenames(scoring: dict[str, Any]) -> list[str]:
    filenames: list[str] = []
    if "expected_source_filename" in scoring:
        filenames.extend(normalize_expected_terms(scoring["expected_source_filename"]))

    if "expected_citation_filenames" in scoring:
        filenames.extend(normalize_expected_terms(scoring["expected_citation_filenames"]))

    return list(dict.fromkeys(filenames))


def extract_answer_text(response_body: Any) -> str:
    if not isinstance(response_body, dict):
        return ""

    answer = response_body.get("answer", "")
    return answer if isinstance(answer, str) else str(answer)


def extract_reference_text(
    case: dict[str, Any],
    scoring: dict[str, Any],
) -> str:
    if "reference_text" in scoring:
        return str(scoring["reference_text"])

    setup = case.get("setup", {})
    if not isinstance(setup, dict):
        return ""

    upload_document = setup.get("upload_document", {})
    if isinstance(upload_document, dict):
        return str(upload_document.get("content", ""))

    return ""


def normalize_text(value: str) -> str:
    return " ".join(value.lower().split())


def extract_usage_metadata(response_body: Any) -> dict[str, Any]:
    usage = {
        "available": False,
        "input_tokens": None,
        "output_tokens": None,
        "total_tokens": None,
        "estimated_cost_usd": None,
    }
    if not isinstance(response_body, dict):
        return usage

    usage_source = first_dict_value(response_body, ["usage", "token_usage"])
    if usage_source is None:
        usage_source = response_body

    input_tokens = coerce_int(
        first_present_value(
            usage_source,
            ["input_tokens", "prompt_tokens", "prompt_token_count"],
        )
    )
    output_tokens = coerce_int(
        first_present_value(
            usage_source,
            ["output_tokens", "completion_tokens", "completion_token_count"],
        )
    )
    total_tokens = coerce_int(first_present_value(usage_source, ["total_tokens"]))
    if total_tokens is None and input_tokens is not None and output_tokens is not None:
        total_tokens = input_tokens + output_tokens

    estimated_cost = coerce_float(
        first_present_value(
            usage_source,
            ["estimated_cost_usd", "cost_usd", "total_cost_usd"],
        )
    )

    usage.update(
        {
            "available": any(
                value is not None
                for value in (input_tokens, output_tokens, total_tokens, estimated_cost)
            ),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "estimated_cost_usd": estimated_cost,
        }
    )
    return usage


def first_dict_value(
    source: dict[str, Any],
    keys: list[str],
) -> dict[str, Any] | None:
    for key in keys:
        value = source.get(key)
        if isinstance(value, dict):
            return value

    return None


def first_present_value(source: dict[str, Any], keys: list[str]) -> Any:
    for key in keys:
        if key in source:
            return source[key]

    return None


def coerce_int(value: Any) -> int | None:
    if value is None or isinstance(value, bool):
        return None

    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def coerce_float(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def build_failure_categories(scores: dict[str, dict[str, Any]]) -> list[str]:
    return [
        score_name
        for score_name, score_result in scores.items()
        if not score_result["passed"]
    ]


def build_summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(results)
    passed = sum(1 for result in results if result["passed"])
    failure_categories: dict[str, int] = {}
    for result in results:
        for category in result.get("failure_categories", []):
            failure_categories[category] = failure_categories.get(category, 0) + 1

    return {
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "pass_rate": round(passed / total, 4) if total else 0.0,
        "failure_categories": failure_categories,
        "usage": build_usage_summary(results),
    }


def build_usage_summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    usage_items = [
        result.get("usage", {})
        for result in results
        if result.get("usage", {}).get("available") is True
    ]

    return {
        "available_cases": len(usage_items),
        "unavailable_cases": len(results) - len(usage_items),
        "input_tokens": sum_optional_usage_field(usage_items, "input_tokens"),
        "output_tokens": sum_optional_usage_field(usage_items, "output_tokens"),
        "total_tokens": sum_optional_usage_field(usage_items, "total_tokens"),
        "estimated_cost_usd": sum_optional_cost(usage_items),
    }


def sum_optional_usage_field(
    usage_items: list[dict[str, Any]],
    field_name: str,
) -> int | None:
    values = [
        usage[field_name]
        for usage in usage_items
        if usage.get(field_name) is not None
    ]
    if not values:
        return None

    return int(sum(values))


def sum_optional_cost(usage_items: list[dict[str, Any]]) -> float | None:
    values = [
        usage["estimated_cost_usd"]
        for usage in usage_items
        if usage.get("estimated_cost_usd") is not None
    ]
    if not values:
        return None

    return round(float(sum(values)), 6)


def load_previous_results(previous_results_path: Path) -> dict[str, Any]:
    if not previous_results_path.exists():
        raise EvalRunnerError(f"Previous results not found: {previous_results_path}")

    try:
        return json.loads(previous_results_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise EvalRunnerError("Previous results file is not valid JSON.") from exc


def compare_eval_results(
    current_results: list[dict[str, Any]],
    previous_output: dict[str, Any],
) -> dict[str, Any]:
    previous_results = previous_output.get("results", [])
    previous_summary = previous_output.get("summary", {})
    current_summary = build_summary(current_results)

    previous_by_id = {
        str(result["id"]): result
        for result in previous_results
        if isinstance(result, dict) and "id" in result
    }
    current_by_id = {str(result["id"]): result for result in current_results}

    new_failures = [
        case_id
        for case_id, current_result in current_by_id.items()
        if previous_by_id.get(case_id, {}).get("passed") is True
        and current_result["passed"] is False
    ]
    new_passes = [
        case_id
        for case_id, current_result in current_by_id.items()
        if previous_by_id.get(case_id, {}).get("passed") is False
        and current_result["passed"] is True
    ]

    previous_pass_rate = float(previous_summary.get("pass_rate", 0.0))
    current_pass_rate = float(current_summary["pass_rate"])

    return {
        "previous_pass_rate": previous_pass_rate,
        "current_pass_rate": current_pass_rate,
        "pass_rate_delta": round(current_pass_rate - previous_pass_rate, 4),
        "new_failures": sorted(new_failures),
        "new_passes": sorted(new_passes),
        "added_cases": sorted(set(current_by_id) - set(previous_by_id)),
        "removed_cases": sorted(set(previous_by_id) - set(current_by_id)),
    }


def save_results(
    results: list[dict[str, Any]],
    results_path: Path,
    comparison: dict[str, Any] | None = None,
) -> None:
    results_path.parent.mkdir(parents=True, exist_ok=True)
    output = {
        "summary": build_summary(results),
        "results": results,
    }
    if comparison is not None:
        output["comparison"] = comparison

    results_path.write_text(json.dumps(output, indent=2), encoding="utf-8")


def build_eval_request_id(case_id: str, step: str) -> str:
    return f"eval_{sanitize_request_id_part(case_id)}_{sanitize_request_id_part(step)}"


def sanitize_request_id_part(value: str) -> str:
    sanitized = "".join(
        character.lower() if character.isalnum() else "_"
        for character in value.strip()
    ).strip("_")
    return sanitized or "unknown"


def build_headers(api_key: str, request_id: str | None = None) -> dict[str, str]:
    headers = {"x-api-key": api_key}
    if request_id is not None:
        headers[REQUEST_ID_HEADER] = request_id
    return headers


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run InsightAgent evaluation cases.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--api-key", required=True)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET_PATH)
    parser.add_argument("--results", type=Path, default=DEFAULT_RESULTS_PATH)
    parser.add_argument("--compare-to", type=Path, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cases = load_eval_cases(args.dataset)
    results = run_eval_cases(cases, base_url=args.base_url, api_key=args.api_key)
    comparison = None
    if args.compare_to is not None:
        previous_output = load_previous_results(args.compare_to)
        comparison = compare_eval_results(results, previous_output)

    save_results(results, args.results, comparison=comparison)
    summary = build_summary(results)
    print(
        f"Evaluated {summary['total']} cases: "
        f"{summary['passed']} passed, {summary['failed']} failed."
    )
    if comparison is not None:
        print(
            "Pass-rate delta vs previous: "
            f"{comparison['pass_rate_delta']:+.4f}"
        )


if __name__ == "__main__":
    main()
