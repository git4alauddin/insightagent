from collections.abc import Callable
from typing import Any

from app.schemas.agent import ToolName
from app.tools.calculator import calculator_tool


ToolFunction = Callable[[dict[str, Any]], str]


class ToolRegistryError(Exception):
    pass


TOOL_REGISTRY: dict[ToolName, ToolFunction] = {}


def register_tool(tool_name: ToolName, tool_fn: ToolFunction) -> None:
    TOOL_REGISTRY[tool_name] = tool_fn


def get_tool(tool_name: ToolName) -> ToolFunction:
    tool_fn = TOOL_REGISTRY.get(tool_name)
    if tool_fn is None:
        raise ToolRegistryError(f"Tool '{tool_name}' is not registered.")
    return tool_fn


def list_registered_tools() -> list[str]:
    return sorted(TOOL_REGISTRY.keys())


def initialize_tool_registry() -> None:
    TOOL_REGISTRY.clear()
    register_tool("calculator", calculator_tool)
