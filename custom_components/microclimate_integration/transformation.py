from .const import CHANNEL_CAPABILITIES, timing_type_mapping
import logging
import math
import re
from typing import Optional, Dict, Union, Any
from custom_components.microclimate_integration.const_helpers import  get_control_pin, map_value
from custom_components.microclimate_integration.const import CONTROL_TYPE_MAPPING, OUTPUT_TYPE_MAPPING

_LOGGER = logging.getLogger(__name__)


def convert_temperature(value:str, data:Optional[Dict])->float:
    """Read Celsius, preserving upstream Celsius numbers mislabeled F."""
    # Scope: Microclimate getAll responses; this is not a general C/F converter.
    # A suffix or v25 unit flag never changes the upstream numeric Celsius value.
    if type(value) not in (str, int, float):
        raise ValueError(f"Error Converting temperature from input: {value}")
    text = str(value).strip()
    match = re.fullmatch(r"([+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?)\s*(?:°?[CF])?", text, re.IGNORECASE)
    if not match:
        raise ValueError(f"Error Converting temperature from input: {value}")
    numeric_value = float(match[1])
    if not math.isfinite(numeric_value):
        raise ValueError("Non-finite temperature")
    return round(numeric_value, 1)


def convert_time(value:Optional[str])->str:
    """Extracts time from encoded string and converts seconds to HH:MM format."""
    if value is None:
        raise ValueError("Input value cannot be None")

    try:
        first_part = value.split("\u0000")[0]  # Extract first split element

        if first_part in ("sr", "ss"):
            raise ValueError("Automated solar scheduling is unsupported")

        seconds = int(first_part)  # Try to convert to int
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours:02}:{minutes:02}"  # Format as HH:MM

    except (ValueError, AttributeError) as e:
        raise ValueError(f"Error converting time from input: {value}") from e


def convert_control_type(value: str) -> str:
    """Maps control type values to meaningful terms.

    Raises:
        ValueError: If the provided control type is not recognized.
    """
    result = map_value(value, CONTROL_TYPE_MAPPING)
    if result == str(value):
        raise ValueError(f"Invalid control type: {value}")
    return result

def convert_timing_type(value: str, channel=None) -> str:
    """Maps timing type values to meaningful terms."""
    mapping = timing_type_mapping(channel) if channel is not None else {"0": "Constant", "1": "Day Night", "2": "Multi"}
    result = map_value(value, mapping)
    if result == str(value):
        raise ValueError (f"Invalid timing type: {value}")
    return result


def convert_output_type(value:str)->str:
    """Maps output type values to meaningful terms."""
    result = map_value( value, OUTPUT_TYPE_MAPPING)

    if result == str(value) :
        raise ValueError (f"Invalid output type: {value}")
    return  result

def convert_setpoint(value, data, channel):
    """Fixed output has no temperature setpoint, regardless of input type."""
    from .validation import control_mode
    mode = control_mode(data.get(get_control_pin(channel)))
    if mode not in ("heating", "cooling"):
        return None
    return convert_temperature(value, data)


def format_sensor_value(pin, value, transformation, data, channel):
    """Applies the appropriate transformation based on type."""
    try:
        if transformation == "timing_type":
            return convert_timing_type(value, channel)
        if transformation == "output_type" and channel == "Blue":
            return "on_off"
        if transformation == "duration_minutes" and channel == "Blue":
            return None
        if transformation == "setpoint":
            return convert_setpoint(value, data, channel)
        if transformation == "temperature":
            return convert_temperature(value, data)
        transform_function = TRANSFORMATION_FUNCTIONS.get(transformation)
        return transform_function(value) if transform_function else value
    except ValueError:
        return value  # Return as-is if conversion fails


def convert_duration_minutes(value):
    """Already in minutes; do not treat a ramp duration as seconds of day."""
    from .validation import nonnegative_number
    result = nonnegative_number(value)
    if result is None:
        raise ValueError("Invalid ramp duration")
    return result


# Mapping of transformation types to their respective functions
TRANSFORMATION_FUNCTIONS = {
    "temperature": convert_temperature,
    "time": convert_time,
    "duration_minutes": convert_duration_minutes,
    "control_type": convert_control_type,
    "timing_type": convert_timing_type,
    "output_type": convert_output_type,
    "setpoint": convert_setpoint,
}
