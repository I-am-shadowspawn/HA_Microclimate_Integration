"""Temperature parsing preserves the reported numeric value and response unit."""

import pytest

from custom_components.microclimate_integration.transformation import convert_temperature
from custom_components.microclimate_integration.validation import (
    reported_temperature_unit,
    safe_temperature,
)


@pytest.mark.parametrize(
    "raw,flag,expected",
    [
        ("25°C", "C", 25.0),
        ("77°F", "F", 77.0),
        ("32°F", "F", 32.0),
        ("20", None, 20.0),
    ],
)
def test_reported_value_is_not_converted_twice(raw, flag, expected):
    assert convert_temperature(raw, {"v25": flag}) == expected
    assert safe_temperature(raw) == expected
    assert reported_temperature_unit({"v25": flag}) == (f"°{flag}" if flag else None)


@pytest.mark.parametrize("raw", ["invalid", "nan°F", "inf", "1e999F", None, True, {}])
def test_invalid_temperature_is_unknown_at_entity_boundary(raw):
    with pytest.raises(ValueError):
        convert_temperature(raw)
    assert safe_temperature(raw) is None
