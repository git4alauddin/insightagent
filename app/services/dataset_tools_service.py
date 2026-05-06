from collections.abc import Sequence
from statistics import median
from typing import Any, Literal

from pandas import DataFrame


ALLOWED_AGGREGATIONS = ("mean", "sum", "count", "min", "max")


class DatasetToolError(Exception):
    pass


def _ensure_columns_exist(dataframe: DataFrame, columns: Sequence[str]) -> None:
    missing_columns = [column for column in columns if column not in dataframe.columns]
    if missing_columns:
        raise DatasetToolError(
            f"Column not found: {', '.join(missing_columns)}"
        )


def _ensure_numeric_columns(dataframe: DataFrame, columns: Sequence[str]) -> None:
    non_numeric = [
        column for column in columns if not str(dataframe[column].dtype).startswith(("int", "float"))
    ]
    if non_numeric:
        raise DatasetToolError(
            f"Numeric column required: {', '.join(non_numeric)}"
        )


def run_dataset_summary(dataframe: DataFrame) -> dict[str, Any]:
    missing_values = {
        str(column): int(count)
        for column, count in dataframe.isna().sum().to_dict().items()
    }
    numeric_columns = [
        str(column)
        for column in dataframe.select_dtypes(include=["number"]).columns
    ]
    categorical_columns = [
        str(column)
        for column in dataframe.select_dtypes(exclude=["number"]).columns
    ]

    return {
        "rows": int(dataframe.shape[0]),
        "columns": int(dataframe.shape[1]),
        "column_names": [str(column) for column in dataframe.columns],
        "missing_values": missing_values,
        "numeric_columns": numeric_columns,
        "categorical_columns": categorical_columns,
    }


def run_missing_value_analysis(
    dataframe: DataFrame,
    columns: list[str] | None = None,
) -> dict[str, Any]:
    target_columns = columns or [str(column) for column in dataframe.columns]
    _ensure_columns_exist(dataframe, target_columns)

    total_rows = max(int(dataframe.shape[0]), 1)
    result_items: list[dict[str, Any]] = []
    for column in target_columns:
        missing_count = int(dataframe[column].isna().sum())
        missing_percentage = round((missing_count / total_rows) * 100, 2)
        result_items.append(
            {
                "column": column,
                "missing_count": missing_count,
                "missing_percentage": missing_percentage,
            }
        )

    result_items.sort(key=lambda item: int(item["missing_count"]), reverse=True)

    return {"results": result_items}


def run_column_stats(dataframe: DataFrame, columns: list[str]) -> dict[str, Any]:
    if not columns:
        raise DatasetToolError("At least one column is required for column statistics.")

    _ensure_columns_exist(dataframe, columns)
    _ensure_numeric_columns(dataframe, columns)

    stats_by_column: dict[str, dict[str, Any]] = {}
    for column in columns:
        clean_series = dataframe[column].dropna()
        if clean_series.empty:
            raise DatasetToolError(f"Column has no numeric values: {column}")

        values = [float(value) for value in clean_series.tolist()]
        stats_by_column[column] = {
            "count": int(len(values)),
            "mean": round(float(sum(values) / len(values)), 4),
            "median": round(float(median(values)), 4),
            "min": round(float(min(values)), 4),
            "max": round(float(max(values)), 4),
            "std": round(float(clean_series.std(ddof=0)), 4),
        }

    return {"stats": stats_by_column}


def run_value_counts(
    dataframe: DataFrame,
    column: str,
    top_k: int = 10,
) -> dict[str, Any]:
    _ensure_columns_exist(dataframe, [column])
    if top_k <= 0:
        raise DatasetToolError("top_k must be greater than 0.")

    counts = dataframe[column].value_counts(dropna=False).head(top_k)
    result = {str(index): int(value) for index, value in counts.to_dict().items()}
    return {"column": column, "top_k": top_k, "value_counts": result}


def run_groupby_aggregation(
    dataframe: DataFrame,
    group_by_column: str,
    target_column: str,
    aggregation: Literal["mean", "sum", "count", "min", "max"],
) -> dict[str, Any]:
    _ensure_columns_exist(dataframe, [group_by_column, target_column])
    if aggregation not in ALLOWED_AGGREGATIONS:
        raise DatasetToolError(
            f"Unsupported aggregation: {aggregation}. Allowed: {', '.join(ALLOWED_AGGREGATIONS)}"
        )

    if aggregation in {"mean", "sum", "min", "max"}:
        _ensure_numeric_columns(dataframe, [target_column])

    grouped = dataframe.groupby(group_by_column, dropna=False)[target_column]

    if aggregation == "mean":
        series = grouped.mean()
    elif aggregation == "sum":
        series = grouped.sum()
    elif aggregation == "count":
        series = grouped.count()
    elif aggregation == "min":
        series = grouped.min()
    else:
        series = grouped.max()

    values = {str(index): round(float(value), 4) for index, value in series.to_dict().items()}

    return {
        "group_by_column": group_by_column,
        "target_column": target_column,
        "aggregation": aggregation,
        "values": values,
    }
