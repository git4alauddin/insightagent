from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from pydantic import ValidationError

from app.schemas.tools import DateTimeInput


class DateTimeToolError(Exception):
    pass


def date_time_tool(tool_input: dict[str, object]) -> str:
    try:
        validated_input = DateTimeInput.model_validate(tool_input)
    except ValidationError as exc:
        raise DateTimeToolError("Invalid date_time tool input.") from exc

    try:
        if validated_input.timezone.upper() == "UTC":
            now = datetime.now(timezone.utc)
        else:
            now = datetime.now(ZoneInfo(validated_input.timezone))
    except Exception as exc:
        raise DateTimeToolError("Invalid timezone provided.") from exc

    return now.isoformat()
