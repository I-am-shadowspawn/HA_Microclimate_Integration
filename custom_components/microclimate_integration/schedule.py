"""Lossless, bounded schedule observations; never an execution engine.

Schedules use manually configured clock times. Unexpected tokens remain raw. Remaining
NUL-separated fields are retained, not assigned undocumented meanings. A
candidate timezone in field 3 is reported without converting to HA local time.
"""
import math
import re
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .readings import cached, read_pin, read_enum
from .const import CHANNEL_PINS, CHANNELS, CHANNEL_CAPABILITIES, DEVICE_METADATA_PINS, timing_type_mapping
from .validation import control_mode, safe_temperature, percentage, nonnegative_number


def reported_value(value):
    """Keep bounded scalar data, including encoded NUL separators, JSON-safe."""
    if type(value) in (int, float):
        try:
            return value if math.isfinite(value) else None
        except OverflowError:
            return None
    if isinstance(value, str) and value and len(value) <= 1024:
        if all(ord(c) >= 32 and ord(c) != 127 or c == '\x00' for c in value):
            return value
    return None


def observe_time(value):
    """Preserve all fields; optionally decode the leading time token."""
    raw = reported_value(value)
    if raw is None:
        return {"raw": None, "interpretation": "missing_or_invalid", "status": "invalid"}
    fields = str(raw).split('\x00')
    result = {"raw": raw, "fields": fields, "interpretation": "reported_unparsed", "status": "unsupported",
              "opaque_fields": [{"index": index, "value": field} for index, field in enumerate(fields)
                                if index not in (0, 2)]}
    first = fields[0]
    if first in ('sr', 'ss'):
        result['unsupported_token'] = first  # No automated solar scheduling on these controllers.
    elif re.fullmatch(r'[0-9]+(?:\.0+)?', first):
        seconds = float(first)
        if math.isfinite(seconds) and 0 <= seconds < 86400:
            seconds = int(seconds)
            result.update(kind='clock', seconds=seconds,
                          time=f'{seconds//3600:02}:{seconds//60%60:02}:{seconds%60:02}',
                          interpretation='time_token', status='valid')
    if result['status'] != 'valid':
        try:
            float(first)
        except ValueError:
            pass  # Unknown text is retained, without inventing its grammar.
        else:
            result['status'] = 'invalid'  # Out-of-range/fractional/non-finite numeric time.
    if len(fields) > 2:
        result['reported_timezone'] = fields[2]
        try:
            ZoneInfo(fields[2])
            result['timezone_recognized'] = True
            result['timezone_status'] = 'recognized'
        except (ZoneInfoNotFoundError, ValueError):
            result['timezone_recognized'] = False
            result['timezone_status'] = 'unrecognized'
    return result


def observe_field(data, pin, observer):
    """Attach field presence without conflating absent pins with invalid values."""
    data = data if isinstance(data, dict) else {}
    def build():
        observation = dict(observer(data.get(pin)))
        if pin not in data:
            observation['status'] = 'absent'
        elif 'status' not in observation:
            interpretation = observation.get('interpretation')
            observation['status'] = (
                'valid' if interpretation == 'calendar_fields' else
                'sentinel' if interpretation == 'zero_date' else
                'invalid' if interpretation in ('missing_or_invalid', 'invalid_date') else 'unsupported')
        return {'source_pin': pin, **observation}
    return cached(data, ('field', pin, observer), build)


def _typed_status(data, pin, value, supported=True):
    if pin not in data:
        return 'absent'
    if reported_value(data.get(pin)) is None:
        return 'invalid'
    if not supported:
        return 'unsupported'
    return 'valid' if value is not None else 'invalid'


def _schedule_observation(data, channel):
    """Report every mapped period, without claiming it is enabled or active."""
    data = data if isinstance(data, dict) else {}
    schema = CHANNEL_PINS[channel]['schedule']
    mode = read_pin(data, CHANNELS[channel]['control_pin'], control_mode)
    result = {
        'interpretation': 'reported_configuration_not_active_schedule',
        'timing_type': read_enum(data, schema['timing_type_pin'], timing_type_mapping(channel)),
        'control_mode': mode,
        'periods': {},
        'reported_period_count': 0,
    }
    timing_pin = schema['timing_type_pin']
    control_pin = CHANNELS[channel]['control_pin']
    result['timing'] = {'source_pin': timing_pin, 'raw': reported_value(data.get(timing_pin)),
                        'status': _typed_status(data, timing_pin, result['timing_type'], result['timing_type'] is not None)}
    result['control'] = {'source_pin': control_pin, 'raw': reported_value(data.get(control_pin)),
                         'status': _typed_status(data, control_pin, mode, mode is not None)}
    result['activation'] = 'unverified'  # No confirmed per-slot enable/disable encoding.
    for key, pins in schema.items():
        if not isinstance(pins, dict):
            if key == "ramp_time_pin" and not CHANNEL_CAPABILITIES[channel]["ramp"]:
                continue
            if key.startswith("periodic_") and (not CHANNEL_CAPABILITIES[channel]["periodic"] or result["timing_type"] != "Periodic"):
                continue
            if key != 'timing_type_pin':
                result[key.removesuffix('_pin')] = {
                    'source_pin': pins, 'raw': reported_value(data.get(pins)),
                    'interpretation': 'reported_unparsed',
                    'status': _typed_status(data, pins, None, supported=False),
                }
                if key == 'ramp_time_pin':
                    result['ramp_time'].update(minutes=nonnegative_number(data.get(pins)), unit='min',
                                               interpretation='duration_minutes',
                                               status=_typed_status(data, pins, nonnegative_number(data.get(pins))))
            continue
        start_pin, setpoint_pin = pins['schedule_start_time_pin'], pins['schedule_set_point_pin']
        raw = reported_value(data.get(setpoint_pin))
        period = {
            'start_pin': start_pin, 'setpoint_pin': setpoint_pin,
            'start': observe_field(data, start_pin, observe_time),
            'setpoint_raw': raw,
            'setpoint_interpretation': 'reported_unparsed',
        }
        if mode in ('heating', 'cooling'):
            temperature = read_pin(data, setpoint_pin, safe_temperature)
            if temperature is not None:
                period.update(setpoint_celsius=temperature, setpoint_interpretation='temperature')
        elif mode == 'fixed':
            output = read_pin(data, setpoint_pin, percentage)
            if output is not None:
                period.update(setpoint_percentage=output, setpoint_interpretation='percentage')
        converted = period.get('setpoint_celsius', period.get('setpoint_percentage'))
        period['setpoint_status'] = _typed_status(data, setpoint_pin, converted, mode in ('heating', 'cooling', 'fixed'))
        period['activation'] = 'unverified'
        if (result['timing_type'] == 'Multi' and period['start'].get('kind') == 'clock'
                and period['start'].get('seconds') == 0 and converted == 0):
            period['activation'] = 'likely_unused'
            period['activation_reason'] = 'midnight_zero_default_pair'
            period['activation_evidence'] = 'maintainer_inference_not_explicit_enable_flag'
            # Keep the observation label stable; card editing has a stronger,
            # maintainer-confirmed storage contract, not a physical enable bit.
            period['card_storage_role'] = 'cleared_slot'
            period['card_storage_evidence'] = 'maintainer_confirmed_contiguous_prefix_and_zero_tail'  
        result['periods'][key] = period
        if period['start']['raw'] is not None or raw is not None:
            result['reported_period_count'] += 1
    if result['timing_type'] == 'Day Night':
        result['day_night'] = {'day': result['periods']['period_1'],
                               'night': result['periods']['period_2']}
    elif result['timing_type'] == 'Multi':
        result['daily_points'] = dict(result['periods'])
        # Report structural anomalies without choosing duplicate precedence,
        # sorting controller slots, or projecting an active setpoint.
        clock_slots = {}
        for name, period in result['periods'].items():
            start = period['start']
            if start.get('kind') == 'clock':
                clock_slots.setdefault(start['time'], []).append(name)
        result['duplicate_clock_times'] = {time: slots for time, slots in clock_slots.items() if len(slots) > 1}
    elif result['timing_type'] == 'Seasonal':
        result['seasons'] = {}
        for season in range(1, 5):
            date_pin = DEVICE_METADATA_PINS[f'season_{season}_start_pin']['pin']
            result['seasons'][f'season_{season}'] = {
                'start_date': observe_field(data, date_pin, observe_date),
                'day': result['periods'][f'period_{2 * season - 1}'],
                'night': result['periods'][f'period_{2 * season}'],
            }
    result['summary'] = _summary(result)
    return result


def _summary(observation):
    """Compact reported settings for HA; never an active-period prediction."""
    def point(period):
        if period.get('activation') == 'likely_unused':
            return 'likely unused'
        start = period['start']
        time = start.get('time', start.get('status', 'unknown'))
        if 'setpoint_celsius' in period:
            value = f"{period['setpoint_celsius']:g} C"
        elif 'setpoint_percentage' in period:
            value = f"{period['setpoint_percentage']:g}%"
        else:
            value = period['setpoint_status']
        return f'{time} = {value}'

    mode = observation['timing_type']
    if mode == 'Day Night':
        pairs = observation['day_night']
        text = 'Day & Night: day ' + point(pairs['day']) + '; night ' + point(pairs['night'])
    elif mode == 'Multi':
        text = 'Multi: ' + '; '.join(f'{i} {point(p)}' for i, p in enumerate(observation['daily_points'].values(), 1))
    elif mode == 'Seasonal':
        text = 'Seasonal: ' + '; '.join(
            f"S{i} [{group['start_date'].get('raw') or 'unknown date'}] D {point(group['day'])}, N {point(group['night'])}"
            for i, group in enumerate(observation['seasons'].values(), 1))
    elif mode == 'Periodic':
        text = 'Periodic: interval/duration reported; units unverified'
    elif mode == 'Constant':
        text = 'Constant: no timed transitions'
    else:
        text = 'Unknown timing mode'
    return text if len(text) <= 255 else text[:252] + '...'


def observe_date(value):
    """Parse observed DD/MM[/YY], preserving the two-digit year without a pivot."""
    from datetime import date
    raw = reported_value(value)
    result = {'raw': raw, 'interpretation': 'reported_unparsed' if raw is not None else 'missing_or_invalid'}
    if not isinstance(raw, str):
        return result
    match = re.fullmatch(r'(\d{2})/(\d{2})(?:/(\d{2}|\d{4}))?', raw)
    if not match:
        return result
    day, month = int(match[1]), int(match[2])
    if day == month == 0 and match[3] is None:
        return {**result, 'interpretation': 'zero_date'}
    # A yearless recurring date may include February 29. A nonzero short
    # year establishes divisibility by four without a century assumption.
    # Short year 00 cannot establish the Gregorian century exception.
    if match[3] == "00" and (month, day) == (2, 29):
        return {**result, "day": day, "month": month, "year_two_digits": 0,
                "interpretation": "reported_unparsed", "reason": "century_required"}
    year = 2000 if match[3] is None else int(match[3])
    if match[3] is not None and len(match[3]) == 2:
        year += 2000  # Validation reference only; never exposed as the actual year.
    try:
        date(year, month, day)
    except ValueError:
        return {**result, 'interpretation': 'invalid_date'}
    result.update(day=day, month=month, interpretation='calendar_fields')
    if match[3] is not None:
        result['year' if len(match[3]) == 4 else 'year_two_digits'] = int(match[3])
    return result


def schedule_observation(data, channel):
    return cached(data, ("schedule", channel), lambda: _schedule_observation(data, channel))
