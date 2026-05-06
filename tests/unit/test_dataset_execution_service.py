import pandas as pd
import pytest

from app.services.dataset_analysis_router import DatasetRouteDecision
from app.services.dataset_execution_service import DatasetExecutionError, execute_analysis_tool


@pytest.fixture
def sample_dataframe():
    return pd.DataFrame(
        {
            "city": ["A", "B", "A", "C"],
            "fare": [10.0, 20.0, 15.0, 40.0],
            "age": [22, 35, 28, 40],
        }
    )


def test_execution_routes_to_correct_tool(sample_dataframe) -> None:
    decision = DatasetRouteDecision(
        intent="missing_value_analysis",
        tool_name="missing_value_tool",
        columns_used=["fare"],
        operation="count_nulls",
        confidence="high",
    )

    result = execute_analysis_tool(sample_dataframe, decision)
    assert result["tool_used"] == "missing_value_tool"
    assert result["analysis_trace"]["operation"] == "count_nulls"


def test_execution_rejects_unknown_tool(sample_dataframe) -> None:
    decision = DatasetRouteDecision(
        intent="unsupported",
        tool_name="none",
        columns_used=[],
        operation="not_applicable",
        confidence="low",
    )

    with pytest.raises(DatasetExecutionError, match="Unsupported or ambiguous"):
        execute_analysis_tool(sample_dataframe, decision)


def test_execution_returns_trace_and_summary(sample_dataframe) -> None:
    decision = DatasetRouteDecision(
        intent="dataset_summary",
        tool_name="dataset_summary_tool",
        columns_used=[],
        operation="dataset_overview",
        confidence="high",
    )

    result = execute_analysis_tool(sample_dataframe, decision)
    assert "Dataset has 4 rows and 3 columns." == result["tool_output_summary"]
    assert result["analysis_trace"]["intent"] == "dataset_summary"


def test_execution_handles_tool_failure_cleanly(sample_dataframe) -> None:
    decision = DatasetRouteDecision(
        intent="column_stats",
        tool_name="column_stats_tool",
        columns_used=["city"],
        operation="column_statistics",
        confidence="medium",
    )

    with pytest.raises(DatasetExecutionError, match="Numeric column required"):
        execute_analysis_tool(sample_dataframe, decision)
