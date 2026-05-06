from typing import Literal

from pydantic import BaseModel

from app.services.dataset_intent_service import detect_columns_from_question, detect_intent


ROUTABLE_INTENT = Literal[
    "dataset_summary",
    "missing_value_analysis",
    "column_stats",
    "value_counts",
    "groupby_aggregation",
    "unsupported",
    "ambiguous",
]

TOOL_NAME = Literal[
    "dataset_summary_tool",
    "missing_value_tool",
    "column_stats_tool",
    "value_counts_tool",
    "groupby_aggregation_tool",
    "none",
]

OPERATION_NAME = Literal[
    "dataset_overview",
    "count_nulls",
    "column_statistics",
    "value_frequencies",
    "groupby_aggregate",
    "not_applicable",
]


class DatasetRouteDecision(BaseModel):
    intent: ROUTABLE_INTENT
    tool_name: TOOL_NAME
    columns_used: list[str]
    operation: OPERATION_NAME
    confidence: Literal["low", "medium", "high"]


_TOOL_BY_INTENT: dict[str, TOOL_NAME] = {
    "dataset_summary": "dataset_summary_tool",
    "missing_value_analysis": "missing_value_tool",
    "column_stats": "column_stats_tool",
    "value_counts": "value_counts_tool",
    "groupby_aggregation": "groupby_aggregation_tool",
    "unsupported": "none",
    "ambiguous": "none",
}

_OPERATION_BY_INTENT: dict[str, OPERATION_NAME] = {
    "dataset_summary": "dataset_overview",
    "missing_value_analysis": "count_nulls",
    "column_stats": "column_statistics",
    "value_counts": "value_frequencies",
    "groupby_aggregation": "groupby_aggregate",
    "unsupported": "not_applicable",
    "ambiguous": "not_applicable",
}


def _compute_confidence(intent: str, columns_used: list[str]) -> Literal["low", "medium", "high"]:
    if intent in {"unsupported", "ambiguous"}:
        return "low"

    if intent == "groupby_aggregation":
        if len(columns_used) >= 2:
            return "high"
        return "medium"

    if intent in {"column_stats", "value_counts"}:
        if columns_used:
            return "high"
        return "medium"

    return "high"


def build_route_decision(question: str, df_columns: list[str]) -> DatasetRouteDecision:
    intent = detect_intent(question)
    columns_used = detect_columns_from_question(question, df_columns)
    tool_name = _TOOL_BY_INTENT[intent]
    operation = _OPERATION_BY_INTENT[intent]
    confidence = _compute_confidence(intent, columns_used)

    return DatasetRouteDecision(
        intent=intent,
        tool_name=tool_name,
        columns_used=columns_used,
        operation=operation,
        confidence=confidence,
    )
