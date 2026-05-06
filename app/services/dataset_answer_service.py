from typing import Any

from app.schemas.dataset import DatasetAnalysisTrace, DatasetAskResponse
from app.services.dataset_analysis_router import DatasetRouteDecision


def _build_answer_text(
    question: str,
    decision: DatasetRouteDecision,
    tool_output: dict[str, Any],
    tool_output_summary: str,
) -> str:
    del question

    if decision.intent == "missing_value_analysis":
        results = tool_output.get("results", [])
        if results:
            top_item = results[0]
            return (
                f"The column with the most missing values is {top_item['column']} "
                f"with {top_item['missing_count']} missing entries."
            )
        return "No missing values were detected in the dataset."

    if decision.intent == "groupby_aggregation":
        values = tool_output.get("values", {})
        preview = ", ".join(f"{key}: {value}" for key, value in list(values.items())[:3])
        if preview:
            return f"Group-by aggregation completed. Sample results -> {preview}."
        return tool_output_summary

    if decision.intent == "column_stats":
        columns = list(tool_output.get("stats", {}).keys())
        if columns:
            return f"Column statistics were computed for: {', '.join(columns)}."
        return tool_output_summary

    if decision.intent == "value_counts":
        column = str(tool_output.get("column", "requested column"))
        return f"Value counts were computed for {column}."

    if decision.intent == "dataset_summary":
        rows = tool_output.get("rows")
        columns = tool_output.get("columns")
        return f"Dataset summary generated with {rows} rows and {columns} columns."

    return tool_output_summary


def build_dataset_ask_response(
    question: str,
    decision: DatasetRouteDecision,
    execution_result: dict[str, Any],
    dataset_id: str,
) -> DatasetAskResponse:
    tool_output = execution_result["tool_output"]
    tool_output_summary = str(execution_result["tool_output_summary"])
    answer = _build_answer_text(
        question=question,
        decision=decision,
        tool_output=tool_output,
        tool_output_summary=tool_output_summary,
    )

    trace_dict = execution_result["analysis_trace"]
    analysis_trace = DatasetAnalysisTrace(
        intent=str(trace_dict["intent"]),
        tool_used=str(trace_dict["tool_used"]),
        columns_used=[str(column) for column in trace_dict["columns_used"]],
        operation=str(trace_dict["operation"]),
    )

    return DatasetAskResponse(
        answer=answer,
        confidence=decision.confidence,
        dataset_id=dataset_id,
        tool_used=str(execution_result["tool_used"]),
        tool_output_summary=tool_output_summary,
        analysis_trace=analysis_trace,
        status="success",
    )
