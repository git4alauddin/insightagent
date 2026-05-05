import pytest
from pydantic import ValidationError

from app.schemas.tools import DateTimeInput


def test_date_time_input_uses_default_timezone() -> None:
    model = DateTimeInput()
    assert model.timezone == "UTC"


def test_date_time_input_trims_timezone() -> None:
    model = DateTimeInput(timezone="  UTC  ")
    assert model.timezone == "UTC"


def test_date_time_input_rejects_blank_timezone() -> None:
    with pytest.raises(ValidationError):
        DateTimeInput(timezone="   ")


def test_date_time_input_rejects_non_string_timezone() -> None:
    with pytest.raises(ValidationError):
        DateTimeInput(timezone=123)

