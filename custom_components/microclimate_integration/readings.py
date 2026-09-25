"""Per-response derived readings shared by every entity on an entry.

Equality uses raw normalized pins only. The private memo is discarded with the
snapshot and never changes coordinator equality or another entry's readings.
"""
from .const_helpers import enum_value


class DataSnapshot(dict):
    def __init__(self, values):
        super().__init__(values)
        self._readings = {}


def cached(data, key, factory):
    if not isinstance(data, DataSnapshot):
        return factory()
    if key not in data._readings:
        data._readings[key] = factory()
    return data._readings[key]


def read_pin(data, pin, transform):
    return cached(data, (pin, transform),
                  lambda: transform(data.get(pin) if isinstance(data, dict) else None))


def read_enum(data, pin, mapping):
    from .const import CONTROL_TYPE_MAPPING
    from .validation import control_mode
    if mapping == CONTROL_TYPE_MAPPING:
        return read_pin(data, pin, control_mode)
    return cached(data, (pin, tuple(mapping.items())),
                  lambda: enum_value(data.get(pin), mapping) if isinstance(data, dict) else None)
