import pytest

from app.tools.calculator import calculator_tool
from app.tools.date_time import date_time_tool
from app.tools.text_summarizer import text_summarizer_tool
from app.tools.registry import (
    TOOL_REGISTRY,
    ToolRegistryError,
    get_tool,
    initialize_tool_registry,
    list_registered_tools,
    register_tool,
)


def test_initialize_tool_registry_registers_tools() -> None:
    initialize_tool_registry()

    assert "calculator" in TOOL_REGISTRY
    assert "date_time" in TOOL_REGISTRY
    assert "text_summarizer" in TOOL_REGISTRY
    assert get_tool("calculator") is calculator_tool
    assert get_tool("date_time") is date_time_tool
    assert get_tool("text_summarizer") is text_summarizer_tool


def test_get_tool_raises_for_unknown_tool() -> None:
    initialize_tool_registry()
    with pytest.raises(ToolRegistryError, match="not registered"):
        get_tool("none")


def test_register_tool_adds_new_tool() -> None:
    initialize_tool_registry()

    def fake_tool(_tool_input: dict[str, object]) -> str:
        return "ok"

    register_tool("none", fake_tool)

    assert "none" in list_registered_tools()
    assert get_tool("none")({"x": 1}) == "ok"
