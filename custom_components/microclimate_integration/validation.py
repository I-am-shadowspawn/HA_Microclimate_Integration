"""Safe typed readings for entity properties."""
import math
from homeassistant.const import UnitOfTemperature
from .transformation import convert_temperature
from .const import CONTROL_TYPE_MAPPING, DEVICE_METADATA_PINS
from .const_helpers import enum_value


def finite_number(value):
    """Normalize numeric strings and numbers; reject booleans and containers."""
    if type(value) not in (str, int, float):
        return None
    try:
        number = float(value)
        return number if math.isfinite(number) else None
    except (ValueError, OverflowError):
        return None


def control_mode(value):
    return enum_value(value, CONTROL_TYPE_MAPPING)


def safe_temperature(value):
    if type(value) not in (str, int, float):
        return None
    try:
        return convert_temperature(value, {})
    except (ValueError, TypeError, OverflowError):
        return None


def reported_temperature_unit(data):
    """The controller's unit belongs to this response, never a previous poll."""
    raw = data.get(DEVICE_METADATA_PINS['temperature_units_pin']['pin']) if isinstance(data, dict) else None
    if type(raw) in (int, float) and math.isfinite(raw) and raw == 0:
        return UnitOfTemperature.CELSIUS
    if not isinstance(raw, str):
        return None
    return {'C': UnitOfTemperature.CELSIUS, 'F': UnitOfTemperature.FAHRENHEIT,
            '0': UnitOfTemperature.CELSIUS}.get(raw.strip().upper())


def safe_scalar(value):
    """HA-safe reported metadata, without inventing units or date formats."""
    if type(value) in (int, float):
        return finite_number(value)
    if isinstance(value, str) and value.strip() and len(value) <= 255 and not any(ord(c) < 32 or ord(c) == 127 for c in value):
        return value
    return None


def nonnegative_number(value):
    number = finite_number(value)
    return number if number is not None and number >= 0 else None


def percentage(value):
    number = finite_number(value)
    return number if number is not None and 0 <= number <= 100 else None
