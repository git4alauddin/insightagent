import ast
import operator
from typing import Any


class CalculatorToolError(Exception):
    pass


_ALLOWED_BINARY_OPERATORS: dict[type[ast.operator], Any] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

_ALLOWED_UNARY_OPERATORS: dict[type[ast.unaryop], Any] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def _evaluate_node(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)

    if isinstance(node, ast.BinOp):
        left_value = _evaluate_node(node.left)
        right_value = _evaluate_node(node.right)
        operation = _ALLOWED_BINARY_OPERATORS.get(type(node.op))

        if operation is None:
            raise CalculatorToolError("Unsupported operator in expression.")

        try:
            return float(operation(left_value, right_value))
        except ZeroDivisionError as exc:
            raise CalculatorToolError("Division by zero is not allowed.") from exc

    if isinstance(node, ast.UnaryOp):
        operand_value = _evaluate_node(node.operand)
        operation = _ALLOWED_UNARY_OPERATORS.get(type(node.op))

        if operation is None:
            raise CalculatorToolError("Unsupported unary operator in expression.")

        return float(operation(operand_value))

    raise CalculatorToolError("Unsupported expression format.")


def calculate_expression(expression: str) -> str:
    try:
        parsed = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise CalculatorToolError("Invalid math expression syntax.") from exc

    result = _evaluate_node(parsed.body)
    # Keep clean integer display when possible
    if result.is_integer():
        return str(int(result))
    return str(result)


def calculator_tool(tool_input: dict[str, Any]) -> str:
    expression_value = tool_input.get("expression")

    if not isinstance(expression_value, str):
        raise CalculatorToolError("Tool input must include an 'expression' string.")

    cleaned_expression = expression_value.strip()
    if not cleaned_expression:
        raise CalculatorToolError("Expression must not be empty.")

    return calculate_expression(cleaned_expression)
