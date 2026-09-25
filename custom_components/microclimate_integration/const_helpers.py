"""Access to the canonical device schema and numeric enum codes."""
import math

from .const import COMMON_ATTRIBUTES, CHANNEL_PINS, MODEL_CHANNEL_OPTIONS


def process_pins(pin_dict):
    """Attach shared semantics while retaining groups and period boundaries."""
    return {
        key: process_pins(value) if isinstance(value, dict) else {
            "pin": value,
            **COMMON_ATTRIBUTES.get(key, {"description": "Unknown", "transformation": "none"}),
        }
        for key, value in pin_dict.items()
    }


def get_device_channels(model):
    channels = MODEL_CHANNEL_OPTIONS.get(model)
    if not channels:
        return None
    return {channel: {"features": features, "pins": process_pins(CHANNEL_PINS.get(channel, {}))}
            for channel, features in channels.items()}


def get_pin_data(device_channels, channel, pin_name):
    """Find a unique role, or a dotted path such as schedule.period_1.schedule_start_time_pin.

    Repeated period roles require a path; never silently choose the first period.
    """
    pins = (device_channels or {}).get(channel, {}).get("pins", {})
    if "." in pin_name:
        for part in pin_name.split("."):
            pins = pins.get(part, {})
        return pins if "pin" in pins else None
    matches = []

    def visit(group):
        for role, value in group.items():
            if isinstance(value, dict):
                if role == pin_name and "pin" in value:
                    matches.append(value)
                elif "pin" not in value:
                    visit(value)

    visit(pins)
    return matches[0] if len(matches) == 1 else None


def get_pin_categories(device_channels, channel, categories):
    pins = (device_channels or {}).get(channel, {}).get("pins", {})
    if isinstance(categories, str):
        categories = [categories]
    return {category: pins[category] for category in categories if category in pins}


def get_control_pin(channel):
    try:
        return CHANNEL_PINS[channel]["metadata"]["control_pin"]
    except KeyError as err:
        raise ValueError(f"Control pin for channel '{channel}' not found.") from err


def enum_value(value, mapping):
    """Accept integral numeric codes (including '1.0'); unknown codes stay unknown."""
    if type(value) not in (str, int, float):
        return None
    try:
        number = float(value)
        if math.isfinite(number) and number.is_integer():
            return mapping.get(str(int(number)))
    except (ValueError, OverflowError):
        pass
    return None


def map_value(value, mapping, default=None):
    result = enum_value(value, mapping)
    return result if result is not None else (str(value) if default is None else default)
