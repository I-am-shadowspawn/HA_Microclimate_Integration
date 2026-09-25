"""Upstream temperature parsing shared by typed observations."""

import math
import re


def convert_temperature(value, data=None) -> float:
    """Read Celsius, preserving upstream Celsius numbers mislabeled F.

    The optional data argument retains the live parser's call contract; the
    reported unit flag never changes the upstream numeric Celsius value.
    """
    if type(value) not in (str, int, float):
        raise ValueError(f"Error Converting temperature from input: {value}")
    text = str(value).strip()
    match = re.fullmatch(
        r"([+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?)\s*(?:°?[CF])?",
        text,
        re.IGNORECASE,
    )
    if not match:
        raise ValueError(f"Error Converting temperature from input: {value}")
    numeric_value = float(match[1])
    if not math.isfinite(numeric_value):
        raise ValueError("Non-finite temperature")
    return round(numeric_value, 1)
