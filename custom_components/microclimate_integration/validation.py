"""Safe typed readings for entity properties."""
import math
from .transformation import convert_temperature
from .const import CONTROL_TYPE_MAPPING
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
