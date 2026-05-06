from typing import Any

from pandas import DataFrame

from app.services.dataset_analysis_router import DatasetRouteDecision
from app.services.dataset_tools_service import (
    DatasetToolError,
    run_column_stats,
    run_dataset_summary,
    run_groupby_aggregation,
    run_missing_value_analysis,
    run_value_counts,
)


class DatasetExecutionError(Exception):
    pass


def _build_summary(tool_output: dict[str, Any], tool_name: str) -> str:
    if tool_name == "dataset_summary_tool":
        return (
            f"Dataset has {tool_output['rows']} rows and {tool_output['columns']} columns."
        )

    if tool_name == "missing_value_tool":
        results = tool_output["results"]
        if not results:
            return "No missing value details found."
        top_item = results[0]
        return (
            f"{top_item['column']} has {top_item['missing_count']} missing values."
        )

    if tool_name == "column_stats_tool":
        columns = list(tool_output["stats"].keys())
        return f"Computed statistics for columns: {', '.join(columns)}."

    if tool_name == "value_counts_tool":
        return (
            f"Computed value counts for {tool_output['column']} (top {tool_output['top_k']})."
        )

    if tool_name == "groupby_aggregation_tool":
        return (
            f"Computed {tool_output['aggregation']} of {tool_output['target_column']} by "
            f"{tool_output['group_by_column']}."
        )

    return "Tool execution completed."


def execute_analysis_tool(
    dataframe: DataFrame,
    decision: DatasetRouteDecision,
) -> dict[str, Any]:
    tool_name = decision.tool_name

    if tool_name == "none":
        raise DatasetExecutionError("Unsupported or ambiguous analysis query.")

    try:
        if tool_name == "dataset_summary_tool":
            tool_output = run_dataset_summary(dataframe)
        elif tool_name == "missing_value_tool":
            tool_output = run_missing_value_analysis(
                dataframe,
                columns=decision.columns_used or None,
            )
        elif tool_name == "column_stats_tool":
            if not decision.columns_used:
                raise DatasetExecutionError("Column statistics requires at least one column.")
            tool_output = run_column_stats(dataframe, decision.columns_used)
        elif tool_name == "value_counts_tool":
            if not decision.columns_used:
                raise DatasetExecutionError("Value counts requires one column.")
            tool_output = run_value_counts(dataframe, decision.columns_used[0])
        elif tool_name == "groupby_aggregation_tool":
            if len(decision.columns_used) < 2:
                raise DatasetExecutionError(
                    "Groupby aggregation requires group and target columns."
                )
            tool_output = run_groupby_aggregation(
                dataframe,
                group_by_column=decision.columns_used[0],
                target_column=decision.columns_used[1],
                aggregation="mean",
            )
        else:
            raise DatasetExecutionError(f"Tool not supported: {tool_name}")
    except DatasetToolError as exc:
        raise DatasetExecutionError(str(exc)) from exc

    return {
        "tool_used": tool_name,
        "tool_output": tool_output,
        "tool_output_summary": _build_summary(tool_output, tool_name),
        "analysis_trace": {
            "intent": decision.intent,
            "tool_used": tool_name,
            "columns_used": decision.columns_used,
            "operation": decision.operation,
        },
    }
