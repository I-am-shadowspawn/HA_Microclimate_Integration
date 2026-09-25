"""Live enum normalization and canonical model/channel pin equality."""

import pytest

from custom_components.microclimate_integration.const import (
    CHANNELS,
    CHANNEL_FIELD_PATHS,
    CHANNEL_PINS,
    CONTROL_TYPE_MAPPING,
    MODEL_CHANNEL_OPTIONS,
    timing_type_mapping,
)
from custom_components.microclimate_integration.const_helpers import enum_value


@pytest.mark.parametrize(
    "raw,expected",
    [
        (0, "fixed"), ("1.0", "heating"), (2.0, "cooling"),
        ("2.5", None), (True, None), ("nan", None), ("inf", None),
        (None, None), ({}, None), (9, None),
    ],
)
def test_enum_normalization(raw, expected):
    assert enum_value(raw, CONTROL_TYPE_MAPPING) == expected


def test_flat_runtime_view_matches_canonical_schema():
    assert set(MODEL_CHANNEL_OPTIONS) == {"Evo Connect", "Evo Connect 2", "Evo Connect 3"}
    for channel, grouped in CHANNEL_PINS.items():
        for key, (group, role) in CHANNEL_FIELD_PATHS.items():
            assert CHANNELS[channel][key] == grouped[group][role]
        assert len({grouped["schedule"][f"period_{i}"]["schedule_start_time_pin"] for i in range(1, 9)}) == 8
    assert CHANNELS["Red"]["control_pin"] == "v82"
    assert CHANNELS["Red"]["setpoint_pin"] == "v9"
    assert CHANNELS["Blue"]["ramp_time"] == "v108"  # Reported pin, not a supported ramp control.


@pytest.mark.parametrize("channel,code,expected", [
    ("Yellow", "3.0", "Seasonal"), ("Red", 3, "Seasonal"),
    ("Blue", 3.0, "Periodic"), ("Blue", "4", "Seasonal"),
])
def test_channel_specific_timing_codes(channel, code, expected):
    assert enum_value(code, timing_type_mapping(channel)) == expected
