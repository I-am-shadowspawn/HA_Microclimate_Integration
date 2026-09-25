import pytest
from unittest.mock import patch

from custom_components.microclimate_integration.transformation import (
convert_temperature,
convert_control_type,
convert_time,
convert_timing_type,
convert_output_type,
convert_setpoint,

)
from custom_components.microclimate_integration.const import CHANNEL_PINS

# Mocking the `CHANNELS` dict for testing

# Mock function to represent convert_temperature
def mock_convert_temperature(value, data):
    return 25.0  # Returning a mock converted value for testing


# ✅ Test Convert Temperature
@pytest.mark.parametrize("value, data, expected", [
    ("25°C", {"v25": "C"}, 25.0),
    ("30", {"v25": "C"}, 30.0),
    ("20°C", {}, 20.0),  # Fallback to Celsius
    ("32°F", {"v25": "F"}, 32.0),
    ("0.1°C", {"v25": "C"}, 0.1)
])
@patch('custom_components.microclimate_integration.transformation._LOGGER.debug')
def test_convert_temperature(mock_debug, value, data, expected):
    assert convert_temperature(value, data) == expected


@pytest.mark.parametrize("value, data", [
    ("invalid_value", {"v25": "C"})])

@patch('custom_components.microclimate_integration.transformation._LOGGER.debug')
def test_convert_temperature_invalid(mock_device_channels, value, data):
    with pytest.raises(ValueError, match= f"Error Converting temperature from input: {value}"):
        convert_temperature(value, data)


# ✅ Test Convert Control Type
@pytest.mark.parametrize("value, expected", [
    ("0", "fixed"), (0, "fixed"),
    ("1", "heating"), (1, "heating"),
    ("2", "cooling"), (2, "cooling")
])
def test_convert_control_type(value, expected):
    assert convert_control_type(value) == expected

# ✅ Test Convert Control Type
@pytest.mark.parametrize("value, expected", [
    ("3", "Invalid control type: 3"), (3, "Invalid control type: 3"),
    ("random", "Invalid control type: random"),
    ("", "Invalid control type:"),
    (None, "Invalid control type: None")])
def test_convert_control_type_invalid(value, expected):
    with pytest.raises(ValueError, match=expected):
        convert_control_type(value)


# ✅ Test Convert Time
@pytest.mark.parametrize("value, expected", [
    ("27000\x0027000\x00Europe/London\x000", "07:30"),
    ("3600", "01:00"),
    ("0\x000\x00Europe/London\x00\x000", "00:00"),
    ("86399\x000\x00Europe/London\x00\x000", "23:59"),
    ("90000\x000\x00Europe/London\x000", "25:00")  # More than 24 hours
])
def test_convert_time(value, expected):
    assert convert_time(value) == expected


# ✅ Test Convert Time
@pytest.mark.parametrize("value, expected", [
    ("", ""),
    ("invalid\x000\x00Europe/London\x00\x000", "invalid"),
    ("invalid_string", "invalid_string")])
def test_convert_time_invalid(value, expected):
    with pytest.raises(ValueError, match=f"Error converting time from input: {expected}"):
        convert_time(value)

def test_convert_time_none():
    with pytest.raises(ValueError, match="Input value cannot be None"):
        convert_time(None)



# Test Convert Timing Type
@pytest.mark.parametrize("value,expected",[
    ("1","Day Night"),    (1,"Day Night"),
    ("2", "Multi"),    (2, "Multi"),
    ("3", "Periodic"),    (3, "Periodic"),
    ("4", "Seasonal"),(4, "Seasonal")])

def test_convert_timing_type(value,expected):
    """Maps timing type values to meaningful terms."""
    assert convert_timing_type(value, "Blue") == expected


@pytest.mark.parametrize("value,expected",[
    ("rubbish","rubbish"), (888, 888),
    (None,None),
    ("","")
])
def test_convert_timing_type_invalid(value,expected):
    """Maps timing type values to meaningful terms."""
    with pytest.raises(ValueError, match=f"Invalid timing type: {expected}"):
        convert_timing_type(value, "Blue")



# Test Convert Output Type
@pytest.mark.parametrize("value,expected",[
    ("0", "pulse"),(0, "pulse"),
    ("1", "dimming"),(1, "dimming")
])

def test_convert_output_type(value,expected):
    assert convert_output_type(value) == expected


@pytest.mark.parametrize("value,expected",[

    ("anything","anything"),
    (999,999), ("999","999"),
    (None,None),
    ("","")
])

def test_convert_output_type_invalid(value,expected):

    with pytest.raises(ValueError, match=f"Invalid output type: {expected}"):
        convert_output_type(value)




# ✅ Test Convert Setpoint
@pytest.mark.parametrize("value, data, channel, expected", [
    # Test fixed control type (no temperature)
    ("10", {"V52": "0"}, "Yellow", None),  # Fixed output is not a temperature
    ("0", {"v112": "0"}, "Blue", None),  # Fixed output is not a temperature

    # Test when control type is 'heating' (should use convert_temperature)
    ("20°C", {"pin_1": "1"}, "Yellow", 25.0),  # Mocking convert_temperature result

    # Test when control type is 'cooling' (should also use convert_temperature)
    ("20°C", {"pin_2": "2"}, "Blue", 25.0),  # Mocking convert_temperature result
])
@patch('custom_components.microclimate_integration.transformation.convert_temperature', side_effect=mock_convert_temperature)
@patch('custom_components.microclimate_integration.transformation._LOGGER.debug')  # Mocking logger to suppress debug output

def test_convert_setpoint_monkeypatch(mock_debug, mock_convert_temperature,monkeypatch, value, data, channel, expected):
    #detemine the control pin key from the sample data
    control_pin_key = list(data.keys())[0]

    #useing monkeypatch to ensure that hte CHANNEL_PINS dictionary has the expected value
    monkeypatch.setitem(CHANNEL_PINS[channel]["metadata"],"control_pin",control_pin_key)

    # Run the test with mocked data
    result = convert_setpoint(value, data, channel)
    assert result == expected



