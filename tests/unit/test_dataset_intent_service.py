from app.services.dataset_intent_service import (
    detect_columns_from_question,
    detect_intent,
)


def test_detect_missing_value_intent() -> None:
    intent = detect_intent("Which column has the most missing values?")
    assert intent == "missing_value_analysis"


def test_detect_column_stats_intent() -> None:
    intent = detect_intent("Show statistics for age column.")
    assert intent == "column_stats"


def test_detect_value_counts_intent() -> None:
    intent = detect_intent("Give me value counts for city.")
    assert intent == "value_counts"


def test_detect_groupby_aggregation_intent() -> None:
    intent = detect_intent("What is the average fare by passenger_class?")
    assert intent == "groupby_aggregation"


def test_detect_unsupported_intent() -> None:
    intent = detect_intent("Who won the match yesterday?")
    assert intent == "unsupported"


def test_detect_column_mentions_case_insensitive() -> None:
    columns = ["Age", "Fare", "Passenger_Class"]
    detected = detect_columns_from_question(
        "Please show average FARE by passenger class",
        columns,
    )
    assert detected == ["Fare", "Passenger_Class"]
