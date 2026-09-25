"""Upstream F-labelled Celsius observations share one live parser."""

import pytest

from custom_components.microclimate_integration.transformation import convert_temperature
from custom_components.microclimate_integration.validation import safe_temperature


@pytest.mark.parametrize("raw,flag,expected", [
    ("25°C", "C", 25.0), ("32°F", "F", 32.0),
    ("0.1°C", "F", 0.1), ("20", None, 20.0),
])
def test_upstream_label_never_causes_an_extra_conversion(raw, flag, expected):
    assert convert_temperature(raw, {"v25": flag}) == expected
    assert safe_temperature(raw) == expected


@pytest.mark.parametrize("raw", ["invalid", "nan°F", "inf", "1e999F", None, True, {}])
def test_invalid_temperature_is_unknown_at_entity_boundary(raw):
    with pytest.raises(ValueError):
        convert_temperature(raw)
    assert safe_temperature(raw) is None
