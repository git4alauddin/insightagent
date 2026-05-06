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


def _contains_any_phrase(text: str, phrases: tuple[str, ...]) -> bool:
    return any(phrase in text for phrase in phrases)


def _contains_any_token(tokens: set[str], candidates: tuple[str, ...]) -> bool:
    return any(candidate in tokens for candidate in candidates)


def detect_intent(question: str) -> str:
    normalized_question = _normalize_text(question)
    tokens = set(normalized_question.split())

    if not normalized_question:
        return "ambiguous"

    if _contains_any_phrase(
        normalized_question,
        ("analyze this", "insight please", "what do you think", "help me"),
    ):
        return "ambiguous"

    aggregation_keywords = ("average", "mean", "sum", "count", "min", "max")
    if (
        " by " in f" {normalized_question} "
        and _contains_any_token(tokens, aggregation_keywords)
    ):
        return "groupby_aggregation"

    if _contains_any_phrase(normalized_question, ("na values",)) or _contains_any_token(
        tokens,
        ("missing", "null"),
    ):
        return "missing_value_analysis"

    if _contains_any_phrase(normalized_question, ("value counts",)) or _contains_any_token(
        tokens,
        ("frequency", "frequencies"),
    ):
        return "value_counts"

    if _contains_any_phrase(normalized_question, ("std dev",)) or _contains_any_token(
        tokens,
        ("statistics", "stats", "distribution", "describe"),
    ) or (
        _contains_any_token(tokens, aggregation_keywords)
        and " by " not in f" {normalized_question} "
    ):
        return "column_stats"

    if _contains_any_phrase(normalized_question, ("column names", "dataset info")) or _contains_any_token(
        tokens,
        ("summary", "overview", "shape"),
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
