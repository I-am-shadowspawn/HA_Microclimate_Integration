import pytest

from custom_components.microclimate_integration.const_helpers import get_device_channels, get_pin_categories, map_value
from custom_components.microclimate_integration.const_helpers import get_pin_data, process_pins, get_control_pin
from custom_components.microclimate_integration.const import CHANNEL_PINS
@pytest.fixture
def mock_model_channel_options(mocker):
    #mocking model_channel_options to return custom mock value
    mock_model_channel_options ={
    "Evo Connect": {
        "Yellow": {"modes": ["Heating", "Cooling", "Lighting"], "hasTemperatureProbe": True},
        "Blue": {"modes": ["Lighting"], "hasTemperatureProbe": False}
    },
    "Evo Connect 2": {
        "Yellow": {"modes": ["Heating", "Cooling", "Lighting"], "hasTemperatureProbe": True},
        "Blue": {"modes": ["Heating", "Cooling", "Lighting"], "hasTemperatureProbe": True}
    },
    "Evo Connect 3": {
        "Yellow": {"modes": ["Heating", "Cooling", "Lighting"], "hasTemperatureProbe": True},
        "Red": {"modes": ["Heating", "Cooling", "Lighting"], "hasTemperatureProbe": True},
        "Blue": {"modes": ["Lighting"], "hasTemperatureProbe": True}
    }
    }
    #mocker.patch("custom_components.microclimate_integration.const.MODEL_CHANNEL_OPTIONS", mock_model_channel_options)
    mocker.patch ("custom_components.microclimate_integration.const_helpers.MODEL_CHANNEL_OPTIONS", mock_model_channel_options)
    return mock_model_channel_options

@pytest.fixture
def mock_common_attributes (mocker):
    #mocking COMMON_ATTRIBUTES to return custom mock value
    mock_common_attributes ={

        "temp_pin": {"description": "Current Temp", "transformation": "temperature"},
        "setpoint_pin": {"description": "Current Set Point", "transformation": "temperature"},
        "control_pin": {"description": "Control Type", "transformation": "control_type"},
        "ramp_time_pin": {"description": "Ramp Time", "transformation": "time"},
        "lower_alarm_pin ": {"description": "Lower Alarm Point", "transformation": "temperature"},
    }
    #mocker.patch("custom_components.microclimate_integration.const.COMMON_ATTRIBUTES", mock_common_attributes)
    mocker.patch ("custom_components.microclimate_integration.const_helpers.COMMON_ATTRIBUTES",mock_common_attributes)
    return mock_common_attributes

@pytest.fixture
def mock_channel_pins(mocker):
     mock_channel_pins = {
         "Yellow": {
            "temperature": {"temp_pin": "v0", "setpoint_pin": "v8"},
            "alarm": {"lower_alarm_pin": "v49"},
            "metadata": {"control_pin": "v52"},
            "schedule": {
                "ramp_time_pin": "v48",
                "timing_type_pin": "v53",
                "period_1": {"schedule_start_time_pin": "v32", "schedule_set_point_pin": "v33"}
            }
        }
     }
     #mocker.patch("custom_components.microclimate_integration.const.CHANNEL_PINS", mock_channel_pins)
     mocker.patch ("custom_components.microclimate_integration.const_helpers.CHANNEL_PINS",mock_channel_pins)
     return mock_channel_pins

# Patch the mock data for testing
@pytest.fixture
def mock_data(mocker):
    mocker.patch('custom_components.microclimate_integration.const_helpers.COMMON_ATTRIBUTES', mock_common_attributes)
    mocker.patch('custom_components.microclimate_integration.const_helpers.CHANNEL_PINS', mock_channel_pins)
    mocker.patch('custom_components.microclimate_integration.const_helpers.MODEL_CHANNEL_OPTIONS', mock_model_channel_options)


@pytest.mark.parametrize("model, expected_channels", [
    ("Evo Connect", ["Yellow","Blue" ]),
    ("Evo Connect 2", ["Yellow", "Blue"]),
    ("Evo Connect 3", ["Yellow", "Red", "Blue"]),
])
def test_get_device_channels_structure(mock_model_channel_options, mock_common_attributes, mock_channel_pins, model, expected_channels):
    """Test that the generated dictionary has the expected channel structure."""
    result = get_device_channels(model)

    # Ensure all expected channels exist in the result
    assert set(result.keys()) == set(expected_channels), f"Missing channels in {model}: {result.keys()}"

    # Check that each channel contains 'features' and 'pins'
    for channel in expected_channels:
        assert "features" in result[channel], f"Missing 'features' key in {channel}"
        assert "pins" in result[channel], f"Missing 'pins' key in {channel}"

        # Ensure 'features' contains required properties
        assert "modes" in result[channel]["features"], f"Missing 'modes' in {channel} features"
        assert "hasTemperatureProbe" in result[channel]["features"], f"Missing 'hasTemperatureProbe' in {channel} features"

        # Ensure 'pins' has expected nested dictionaries
        assert isinstance(result[channel]["pins"], dict), f"'pins' should be a dictionary in {channel}"

        # Verify that each expected pin category exists
        expected_pin_categories = ["temperature", "alarm", "metadata", "schedule"]
        for category in expected_pin_categories:
            if category in result[channel]["pins"]:
                assert isinstance(result[channel]["pins"][category], dict), f"'{category}' should be a dictionary in {channel} pins"

        # Check if 'control_pin' exists in 'pins' and validate its description
        for category, pin_data in result[channel]["pins"].items():
            if "control_pin" in pin_data:
                assert pin_data["control_pin"]["description"] == "Control Type", f"Unexpected description for control_pin in {channel}: {pin_data['control_pin']['description']}"

# Test the process_pins logic directly for the 'pin_dict' return value
@pytest.mark.parametrize("pin_dict, expected", [
    # Test simple pin dictionary
    (
        {'temp_pin': 'v0', 'setpoint_pin': 'v8'},
        {
            'temp_pin': {
                'pin': 'v0',
                'description': 'Current Temp',
                'transformation': 'temperature'
            },
            'setpoint_pin': {
                'pin': 'v8',
                'description': 'Current Set Point',
                'transformation': 'setpoint'
            }
        }
    ),
    # Test pin dictionary where COMMON_ATTRIBUTES doesn't have the key
    (
        {'unknown_pin': 'v99'},
        {
            'unknown_pin': {
                'pin': 'v99',
                'description': 'Unknown',
                'transformation': 'none'
            }
        }
    )
])
def test_process_pins(pin_dict, expected):
    from custom_components.microclimate_integration.const_helpers import process_pins
    result = process_pins(pin_dict)
    assert result == expected


# Test case for an empty input to process_pins
def test_process_pins_empty():
    from custom_components.microclimate_integration.const_helpers import process_pins
    result = process_pins({})
    assert result == {}


# Test case for handling a missing model in the configuration
def test_get_device_channels_invalid_model():
    result = get_device_channels("Invalid Model")
    assert result == None


@pytest.fixture
def mock_device_channels():
    return {
        "Yellow": {
            "features": {
                "modes": ["Heating", "Cooling", "Lighting"],
                "hasTemperatureProbe": True
            },
            "pins": {
                "temperature": {
                    "temp_pin": {
                        "pin": "v0",
                        "description": "Current Temp",
                        "transformation": "temperature"
                    },
                    "setpoint_pin": {
                        "pin": "v8",
                        "description": "Current Set Point",
                        "transformation": "temperature"
                    }
                },
                "alarm": {
                    "lower_alarm_pin": {
                        "pin": "v49",
                        "description": "Lower Alarm Point",
                        "transformation": "temperature"
                    }
                }
            }
        },
        "Blue": {
            "features": {
                "modes": ["Lighting"],
                "hasTemperatureProbe": False
            },
            "pins": {
                "metadata": {
                    "channel_name_pin": {
                        "pin": "v18",
                        "description": "Blue Channel Name",
                        "transformation": "none"
                    }
                }
            }
        }
    }

def test_get_single_category(mock_device_channels):
    result = get_pin_categories(mock_device_channels, "Yellow", "temperature")
    assert "temperature" in result
    assert result["temperature"]["temp_pin"]["pin"] == "v0"
    assert result["temperature"]["setpoint_pin"]["description"] == "Current Set Point"

def test_get_multiple_categories(mock_device_channels):
    result = get_pin_categories(mock_device_channels, "Yellow", ["temperature", "alarm"])
    assert "temperature" in result
    assert "alarm" in result
    assert result["alarm"]["lower_alarm_pin"]["pin"] == "v49"

def test_category_not_found(mock_device_channels):
    result = get_pin_categories(mock_device_channels, "Yellow", "nonexistent_category")
    assert result == {}

def test_channel_not_found(mock_device_channels):
    result = get_pin_categories(mock_device_channels, "Nonexistent", "temperature")
    assert result == {}

def test_get_category_for_blue_channel(mock_device_channels):
    result = get_pin_categories(mock_device_channels, "Blue", "metadata")
    assert "metadata" in result
    assert result["metadata"]["channel_name_pin"]["pin"] == "v18"


def test_get_existing_pin(mock_device_channels):
    result = get_pin_data(mock_device_channels, "Yellow",  "temp_pin")
    assert result == {
        "pin": "v0",
        "description": "Current Temp",
        "transformation": "temperature"
    }

def test_get_nonexistent_pin(mock_device_channels):
    result = get_pin_data(mock_device_channels, "Yellow",  "nonexistent_pin")
    assert result is None  # Expected to return None for a missing pin

def test_get_existing_pin_in_alarm_category(mock_device_channels):
    result = get_pin_data(mock_device_channels, "Yellow",  "lower_alarm_pin")
    assert result == {
        "pin": "v49",
        "description": "Lower Alarm Point",
        "transformation": "temperature"
    }

def test_get_pin_for_blue_channel(mock_device_channels):
    result = get_pin_data(mock_device_channels, "Blue",  "channel_name_pin")
    assert result == {
        "pin": "v18",
        "description": "Blue Channel Name",
        "transformation": "none"
    }

def test_get_pin_from_nonexistent_channel(mock_device_channels):
    result = get_pin_data(mock_device_channels, "Nonexistent",  "temp_pin")
    assert result is None  # Expected to return None if the channel doesn't exist


#test get_control_pin
@pytest.mark.parametrize("channel,expected", [
    ("Yellow", "v52"),
    ("Red", "v82"),
    ("Blue", "v112")
])
def test_get_control_pin(monkeypatch, channel, expected):
    # Ensure the expected control pin value is set in the CHANNEL_PINS dict.
    # This overrides any existing value for testing purposes.
    monkeypatch.setitem(CHANNEL_PINS[channel]["metadata"], "control_pin", expected)

    # Now, get_control_pin should return the expected value.
    assert get_control_pin(channel) == expected



def test_get_control_pin_invalid_channel():
    # For a channel that does not exist, we expect a ValueError.
    with pytest.raises(ValueError, match="Control pin for channel 'Green' not found."):
        get_control_pin("Green")


def test_get_control_pin_missing_metadata(monkeypatch):
    # Simulate missing "control_pin" in the metadata of the "Yellow" channel.
    # We first store the original metadata.
    original_metadata = CHANNEL_PINS["Yellow"]["metadata"].copy()
    # Remove the "control_pin" key
    monkeypatch.delitem(CHANNEL_PINS["Yellow"]["metadata"], "control_pin")

    with pytest.raises(ValueError, match="Control pin for channel 'Yellow' not found."):
        get_control_pin("Yellow")

    # Restore the original metadata for other tests.
    CHANNEL_PINS["Yellow"]["metadata"] = original_metadata


