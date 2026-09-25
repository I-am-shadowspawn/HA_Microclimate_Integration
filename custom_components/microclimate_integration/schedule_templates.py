"""Portable schedule-only templates; no controller identity or raw pin data."""

import json

from .constraints import valid_seconds, valid_point_count

from .card_model import value_of
from .edit_plan import build_plan
from .write_contract import control_mode, definition_for, timing_mode, WriteValidationError

FORMAT = "microclimate.schedule.v1"
MAX_TEMPLATE_BYTES = 4096
MODES = {"Day Night": 2, "Seasonal": 8, "Multi": None}


def _context(model, channel, data):
    if channel is None:
        raise WriteValidationError("unsupported_capability")
    first = definition_for(model, f"{channel}_period_1_setpoint")
    mode = timing_mode(first, data)
    control = control_mode(first, data)
    if mode not in MODES or control not in ("fixed", "heating", "cooling"):
        raise WriteValidationError("unsupported_capability")
    return mode, "percent" if control == "fixed" else "celsius"


def validate_template(template, mode, unit):
    """Validate a foreign preset before passing its points to the existing planner."""
    if type(template) is not dict or set(template) != {"format", "mode", "unit", "points"}:
        raise WriteValidationError("invalid_patch")
    if template["format"] != FORMAT:
        raise WriteValidationError("version_changed")
    if template["mode"] != mode or template["unit"] != unit:
        raise WriteValidationError("stale_context")
    points = template["points"]
    if type(points) is not list or not valid_point_count(mode, len(points)):
        raise WriteValidationError("invalid_patch")
    clean = []
    for point in points:
        if type(point) is not dict or set(point) != {"seconds", "target_native"}:
            raise WriteValidationError("invalid_patch")
        seconds, target = point["seconds"], point["target_native"]
        if not valid_seconds(seconds) or type(target) not in (int, float):
            raise WriteValidationError("invalid_patch")
        # build_plan performs the full numeric, ordering and reserved-slot checks.
        clean.append({"seconds": seconds, "target_native": target})
    return clean


def import_patch(model, channel, data, template):
    """Return a validated patch for the current destination context."""
    mode, unit = _context(model, channel, data)
    points = validate_template(template, mode, unit)
    patch = {"kind": "channel", "fields": {}, "schedule": {"mode": mode, "points": points}}
    build_plan(model, channel, data, patch)
    return patch


def export_template(model, channel, data):
    """Export only complete, supported schedule points in controller-native units."""
    mode, unit = _context(model, channel, data)
    points = []
    for index in range(1, (MODES[mode] or 8) + 1):
        time_field = definition_for(model, f"{channel}_period_{index}_time")
        target_field = definition_for(model, f"{channel}_period_{index}_setpoint")
        points.append({"seconds": value_of(time_field, data),
                       "target_native": value_of(target_field, data)})
    if mode == "Multi":
        while points and points[-1] == {"seconds": 0, "target_native": 0.0}:
            points.pop()
    template = {"format": FORMAT, "mode": mode, "unit": unit, "points": points}
    import_patch(model, channel, data, template)
    return template


def parse_template(value):
    """Accept a bounded JSON service argument; never echo invalid input."""
    if type(value) is not str:
        raise WriteValidationError("invalid_patch")
    try:
        if len(value.encode("utf-8")) > MAX_TEMPLATE_BYTES:
            raise WriteValidationError("invalid_patch")
        return json.loads(value)
    except (ValueError, TypeError, UnicodeError):
        raise WriteValidationError("invalid_patch") from None
