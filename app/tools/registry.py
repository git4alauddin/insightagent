from collections.abc import Callable
from typing import Any

from app.schemas.agent import ToolName
from app.tools.calculator import calculator_tool
from app.tools.date_time import date_time_tool
from app.tools.text_summarizer import text_summarizer_tool


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
    register_tool("date_time", date_time_tool)
    register_tool("text_summarizer", text_summarizer_tool)
