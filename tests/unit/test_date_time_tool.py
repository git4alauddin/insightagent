import pytest

from app.tools.date_time import DateTimeToolError, date_time_tool


def test_date_time_tool_returns_iso_datetime_for_valid_timezone() -> None:
    result = date_time_tool({"timezone": "UTC"})

    assert "T" in result
    assert len(result) >= 19


def test_date_time_tool_uses_default_timezone() -> None:
    result = date_time_tool({})

    assert "T" in result


def test_date_time_tool_rejects_non_string_timezone() -> None:
    with pytest.raises(DateTimeToolError, match="Invalid date_time tool input"):
        date_time_tool({"timezone": 123})


def test_date_time_tool_rejects_blank_timezone() -> None:
    with pytest.raises(DateTimeToolError, match="Invalid date_time tool input"):
        date_time_tool({"timezone": "   "})


def test_date_time_tool_rejects_invalid_timezone() -> None:
    with pytest.raises(DateTimeToolError, match="Invalid timezone"):
        date_time_tool({"timezone": "Invalid/Timezone"})
