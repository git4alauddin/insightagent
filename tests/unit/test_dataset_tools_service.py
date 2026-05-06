import pandas as pd
import pytest

from app.services.dataset_tools_service import (
    DatasetToolError,
    run_column_stats,
    run_groupby_aggregation,
    run_missing_value_analysis,
    run_value_counts,
)


@pytest.fixture
def sample_dataframe():
    return pd.DataFrame(
        {
            "city": ["A", "B", "A", "C"],
            "fare": [10.0, 20.0, None, 40.0],
            "age": [22, 35, 28, 40],
        }
    )


def test_missing_value_analysis_all_columns(sample_dataframe) -> None:
    result = run_missing_value_analysis(sample_dataframe)
    top_item = result["results"][0]

    assert top_item["column"] == "fare"
    assert top_item["missing_count"] == 1


def test_column_stats_numeric_only(sample_dataframe) -> None:
    result = run_column_stats(sample_dataframe, ["age"])
    stats = result["stats"]["age"]

    assert stats["count"] == 4
    assert stats["min"] == 22.0
    assert stats["max"] == 40.0


def test_value_counts_top_k(sample_dataframe) -> None:
    result = run_value_counts(sample_dataframe, "city", top_k=2)

    assert result["column"] == "city"
    assert result["top_k"] == 2
    assert set(result["value_counts"].keys()) == {"A", "B"}


def test_groupby_aggregation_mean(sample_dataframe) -> None:
    result = run_groupby_aggregation(
        sample_dataframe,
        group_by_column="city",
        target_column="fare",
        aggregation="mean",
    )

    assert result["aggregation"] == "mean"
    assert result["values"]["A"] == 10.0
    assert result["values"]["B"] == 20.0


def test_invalid_column_raises_controlled_error(sample_dataframe) -> None:
    with pytest.raises(DatasetToolError, match="Column not found"):
        run_column_stats(sample_dataframe, ["salary"])


def test_invalid_aggregation_raises_controlled_error(sample_dataframe) -> None:
    with pytest.raises(DatasetToolError, match="Unsupported aggregation"):
        run_groupby_aggregation(
            sample_dataframe,
            group_by_column="city",
            target_column="fare",
            aggregation="median",  # type: ignore[arg-type]
        )
