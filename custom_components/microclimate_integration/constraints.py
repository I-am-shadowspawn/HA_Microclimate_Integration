"""Edit limits shared by backend validation and control metadata.

Observation parsers deliberately retain their own permissive semantics.
Cross-language examples live in fixtures/validation_contract.json.
"""

MIN_VALUE = 0
MAX_TARGET = 100
MAX_RAMP_MINUTES = 240
SECONDS_PER_DAY = 86400
MAX_POINTS = 8
MIN_POINTS = 2


def numeric_maximum(kind):
    return MAX_RAMP_MINUTES if kind == "ramp" else MAX_TARGET


def valid_seconds(value):
    """Card edits supply whole seconds, never booleans or numeric strings."""
    return type(value) is int and 0 <= value < SECONDS_PER_DAY


def valid_point_count(mode, count):
    return (MIN_POINTS <= count <= MAX_POINTS if mode == "Multi"
            else count == 2 if mode == "Day Night"
            else count == 8 if mode == "Seasonal" else False)
