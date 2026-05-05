import pytest

from app.tools.calculator import CalculatorToolError, calculate_expression, calculator_tool


def test_calculate_expression_handles_basic_math() -> None:
    assert calculate_expression("25 * 18") == "450"
    assert calculate_expression("10 / 4") == "2.5"


def test_calculate_expression_rejects_invalid_syntax() -> None:
    with pytest.raises(CalculatorToolError, match="Invalid math expression syntax"):
        calculate_expression("2 +")


def test_calculate_expression_rejects_division_by_zero() -> None:
    with pytest.raises(CalculatorToolError, match="Division by zero"):
        calculate_expression("10 / 0")


def test_calculator_tool_requires_expression_string() -> None:
    with pytest.raises(CalculatorToolError, match="expression"):
        calculator_tool({})


def test_calculator_tool_rejects_blank_expression() -> None:
    with pytest.raises(CalculatorToolError, match="must not be empty"):
        calculator_tool({"expression": "   "})

