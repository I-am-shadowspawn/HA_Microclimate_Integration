"""Numeric enum normalization shared by live readers and write contracts."""

import math


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
