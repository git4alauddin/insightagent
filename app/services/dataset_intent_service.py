import re


SUPPORTED_INTENTS = (
    "dataset_summary",
    "missing_value_analysis",
    "column_stats",
    "value_counts",
    "groupby_aggregation",
    "unsupported",
    "ambiguous",
)


def _normalize_text(value: str) -> str:
    lowered = value.strip().lower()
    return re.sub(r"[^a-z0-9\s]+", " ", lowered)


def detect_intent(question: str) -> str:
    normalized_question = _normalize_text(question)

    if not normalized_question:
        return "ambiguous"

    if any(
        keyword in normalized_question
        for keyword in ("analyze this", "insight please", "what do you think", "help me")
    ):
        return "ambiguous"

    aggregation_keywords = ("average", "mean", "sum", "count", "min", "max")
    if (
        " by " in f" {normalized_question} "
        and any(keyword in normalized_question for keyword in aggregation_keywords)
    ):
        return "groupby_aggregation"

    if any(keyword in normalized_question for keyword in ("missing", "null", "na values")):
        return "missing_value_analysis"

    if any(keyword in normalized_question for keyword in ("value counts", "frequency")):
        return "value_counts"

    if any(
        keyword in normalized_question
        for keyword in ("statistics", "stats", "distribution", "describe", "std dev")
    ) or (
        any(keyword in normalized_question for keyword in aggregation_keywords)
        and " by " not in f" {normalized_question} "
    ):
        return "column_stats"

    if any(
        keyword in normalized_question
        for keyword in ("summary", "overview", "shape", "column names", "dataset info")
    ):
        return "dataset_summary"

    return "unsupported"


def detect_columns_from_question(question: str, df_columns: list[str]) -> list[str]:
    normalized_question = _normalize_text(question)
    detected_columns: list[str] = []

    normalized_column_map = {
        column: _normalize_text(column).replace("_", " ").strip() for column in df_columns
    }

    for original_column, normalized_column in normalized_column_map.items():
        if not normalized_column:
            continue
        if f" {normalized_column} " in f" {normalized_question} ":
            detected_columns.append(original_column)

    return detected_columns
