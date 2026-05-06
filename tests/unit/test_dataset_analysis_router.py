from app.services.dataset_analysis_router import build_route_decision


def test_router_maps_groupby_intent_to_expected_tool() -> None:
    decision = build_route_decision(
        question="What is the average fare by passenger class?",
        df_columns=["fare", "passenger_class", "age"],
    )

    assert decision.intent == "groupby_aggregation"
    assert decision.tool_name == "groupby_aggregation_tool"
    assert decision.operation == "groupby_aggregate"


def test_router_sets_low_confidence_for_unsupported_question() -> None:
    decision = build_route_decision(
        question="Tell me a joke",
        df_columns=["age", "fare"],
    )

    assert decision.intent == "unsupported"
    assert decision.tool_name == "none"
    assert decision.confidence == "low"
    assert decision.operation == "not_applicable"


def test_router_collects_columns_and_operation_for_stats() -> None:
    decision = build_route_decision(
        question="Show stats for age and fare",
        df_columns=["age", "fare", "city"],
    )

    assert decision.intent == "column_stats"
    assert decision.tool_name == "column_stats_tool"
    assert decision.operation == "column_statistics"
    assert decision.columns_used == ["age", "fare"]
    assert decision.confidence == "high"
