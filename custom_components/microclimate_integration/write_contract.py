"""Allowlisted configuration writes derived from the canonical pin schema."""
from dataclasses import dataclass
from datetime import date, time
from decimal import Decimal, InvalidOperation
from functools import lru_cache
import re
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .const import (CHANNEL_CAPABILITIES, CHANNEL_PINS, CHANNELS, CONTROL_TYPE_MAPPING,
                    DEVICE_METADATA_PINS, MODEL_CHANNEL_OPTIONS, OUTPUT_TYPE_MAPPING,
                    timing_type_mapping)
from .const_helpers import enum_value


class WriteValidationError(ValueError):
    """Only fixed public reason codes: never include request data/credentials."""
    def __init__(self, code):
        super().__init__(code)
        self.code = code


@dataclass(frozen=True)
class WriteDefinition:
    key: str
    pin: str
    kind: str
    name: str
    channel: str | None = None
    index: int | None = None
    options: tuple[tuple[str, str], ...] = ()
    temperature_capable: bool = True

    @property
    def platform(self):
        return {'enum': 'select', 'number': 'number', 'setpoint': 'number',
                'time': 'time', 'date': 'text', 'ramp': 'number'}[self.kind]


@lru_cache(maxsize=3)
def write_definitions(model):
    definitions = []
    profile = MODEL_CHANNEL_OPTIONS.get(model)
    if not profile:
        return ()
    for key, metadata in DEVICE_METADATA_PINS.items():
        if key.startswith('season_'):
            definitions.append(WriteDefinition(key, metadata['pin'], 'date', 'Set ' + metadata['description'].lower()))
    for channel, features in profile.items():
        pins = CHANNELS[channel]
        for key, name, mapping in (
            ('control_pin', 'Configure control mode', CONTROL_TYPE_MAPPING if features['hasTemperatureProbe'] else {'0':'fixed'}),
            ('timing_type', 'Configure timing mode', timing_type_mapping(channel)),
            ('output_type', 'Configure output type', OUTPUT_TYPE_MAPPING),
        ):
            if key == 'output_type' and not CHANNEL_CAPABILITIES[channel]['variable_output']:
                continue
            definitions.append(WriteDefinition(f'{channel}_{key}', pins[key], 'enum', name, channel,
                                               options=tuple(mapping.items())))
        if CHANNEL_CAPABILITIES[channel]['ramp']:
            definitions.append(WriteDefinition(f'{channel}_ramp_time',pins['ramp_time'],'ramp',
                                               'Set ramp time',channel))
        if features['hasTemperatureProbe']:
            for key in ('lower_alarm', 'upper_alarm'):
                definitions.append(WriteDefinition(f'{channel}_{key}', pins[key], 'number',
                                                   'Set ' + key.replace('_', ' ') + ' threshold', channel))
        for index in range(1, 9):
            pair = CHANNEL_PINS[channel]['schedule'][f'period_{index}']
            for kind, role in (('time','schedule_start_time_pin'),('setpoint','schedule_set_point_pin')):
                definitions.append(WriteDefinition(f'{channel}_period_{index}_{kind}',pair[role],kind,
                                                   'Set schedule ' + kind,channel,index,
                                                   temperature_capable=features['hasTemperatureProbe']))
    return tuple(definitions)


def definition_for(model, key):
    for definition in write_definitions(model):
        if definition.key == key:
            return definition
    raise WriteValidationError('unsupported_capability')


def control_mode(field, data):
    mode = enum_value(data.get(CHANNELS[field.channel]['control_pin']), CONTROL_TYPE_MAPPING) if field.channel else None
    return mode if field.temperature_capable or mode == 'fixed' else None


def timing_mode(field, data):
    return enum_value(data.get(CHANNELS[field.channel]['timing_type']), timing_type_mapping(field.channel)) if field.channel else None


def applicable(field, data):
    if not isinstance(data, dict) or field.pin not in data:
        return False
    if field.index is None:
        return True
    mode = timing_mode(field, data)
    return (mode in ('Multi','Seasonal') or mode == 'Day Night' and field.index <= 2) and control_mode(field,data) is not None


def context(field, data):
    """Only semantic context; unrelated measurements do not invalidate commands."""
    if field.index is not None:
        suffix = None
        if field.kind == 'time':
            raw = data.get(field.pin)
            suffix = tuple(raw.split('\0')[2:]) if isinstance(raw,str) and '\0' in raw else ()
        return (timing_mode(field,data), control_mode(field,data), suffix)
    if field.kind == 'enum':
        return enum_value(data.get(field.pin), dict(field.options))
    return None


def numeric(value, *, maximum=100):
    if type(value) not in (str, int, float, Decimal):
        raise WriteValidationError('invalid_number')
    try:
        number = Decimal(str(value))
    except InvalidOperation:
        raise WriteValidationError('invalid_number') from None
    if not number.is_finite() or not 0 <= number <= maximum:
        raise WriteValidationError('invalid_number')
    return number


def date_string(value):
    if not isinstance(value,str) or not re.fullmatch(r'[0-9]{2}/[0-9]{2}',value):
        raise WriteValidationError('invalid_date')
    try:
        day,month=map(int,value.split('/'))
        date(2001,month,day)  # Validation only: leap day deliberately prohibited.
    except ValueError:
        raise WriteValidationError('invalid_date') from None
    return value


def time_seconds(value):
    if not isinstance(value,time) or value.tzinfo is not None or value.microsecond:
        raise WriteValidationError('invalid_time')
    return value.hour*3600+value.minute*60+value.second


def validate_input(field,value):
    if field.kind == 'enum':
        if not isinstance(value,str) or value not in dict(field.options).values():
            raise WriteValidationError('invalid_option')
    elif field.kind in ('number','setpoint'):
        numeric(value)
    elif field.kind == 'ramp':
        ramp_minutes(value)
    elif field.kind == 'date':
        date_string(value)
    else:
        time_seconds(value)


def _clock(value):
    if not re.fullmatch(r'[0-9]+(?:\.0+)?',value):
        raise WriteValidationError('unsupported_encoding')
    seconds=Decimal(value)
    if not 0 <= seconds < 86400:
        raise WriteValidationError('unsupported_encoding')
    return seconds


def _zone(value):
    try:
        ZoneInfo(value)
    except (ValueError,ZoneInfoNotFoundError):
        raise WriteValidationError('unsupported_encoding') from None
    return value


def _parts(raw):
    if not isinstance(raw,str) or len(raw)>1024 or any(ord(c)<32 and c!='\0' or ord(c)==127 for c in raw):
        raise WriteValidationError('unsupported_encoding')
    parts=raw.split('\0')
    if len(parts)<4 or _clock(parts[0])!=_clock(parts[1]):
        raise WriteValidationError('unsupported_encoding')
    _zone(parts[2])
    return parts


def encode_time(field,value,data):
    seconds=str(time_seconds(value))
    raw=data.get(field.pin)
    if isinstance(raw,str) and '\0' in raw:
        parts=_parts(raw)
        return '\0'.join([seconds,seconds,*parts[2:]])
    if type(raw) not in (str,int,float):
        raise WriteValidationError('unsupported_encoding')
    _clock(str(raw))
    zones=set()
    for group in CHANNEL_PINS[field.channel]['schedule'].values():
        if not isinstance(group,dict):
            continue
        candidate=data.get(group.get('schedule_start_time_pin'))
        if not isinstance(candidate,str) or '\0' not in candidate:
            continue
        try:
            parts=_parts(candidate)
        except WriteValidationError:
            continue
        if len(parts)==4 and parts[3]=='0':
            zones.add(parts[2])
    if len(zones)!=1:
        raise WriteValidationError('unsupported_encoding')
    zone=zones.pop()
    clock=data.get('v27')
    if isinstance(clock,str) and '\0' in clock:
        if _parts(clock)[2]!=zone:
            raise WriteValidationError('unsupported_encoding')
    return '\0'.join([seconds,seconds,zone,'0'])


def serialize(field,value,data):
    validate_input(field,value)
    if field.kind=='enum':
        return next(code for code,label in field.options if label==value)
    if field.kind in ('number','setpoint'):
        number=numeric(value)
        text=format(number,'f') if number.adjusted() >= -20 else str(number)
        return text.rstrip('0').rstrip('.') if '.' in text and 'E' not in text else text
    if field.kind=='ramp':
        return str(int(ramp_minutes(value)))
    if field.kind=='date':
        validate_season_sequence(field,value,data)
        return date_string(value)
    return encode_time(field,value,data)


def matches(field,expected,data):
    actual=data.get(field.pin)
    if field.kind in ('date','time'):
        return type(actual) is str and actual==expected
    if field.kind=='enum':
        return expected in dict(field.options) and enum_value(actual,dict(field.options))==dict(field.options)[expected]
    try:
        return observed_numeric(field,data)==Decimal(expected)
    except (WriteValidationError,InvalidOperation):
        return False


def observed_numeric(field,data):
    """Unrounded native value; F suffixes are the known upstream Celsius nuance."""
    actual=data.get(field.pin)
    if field.kind=='ramp':
        return ramp_minutes(actual)
    if isinstance(actual,str):
        thermal = field.kind=='number' or control_mode(field,data) in ('heating','cooling')
        if thermal:
            actual=re.sub(r'\s*°?[CF]\s*$','',actual,flags=re.I)
    return numeric(actual)


SEASON_PINS = tuple(DEVICE_METADATA_PINS[f'season_{index}_start_pin']['pin'] for index in range(1,5))


def validate_season_sequence(field, value, data):
    """Require a strictly ordered annual cycle, allowing one December/January wrap.

    Explicit 00/00 siblings are unset and omitted, permitting initial population.
    Missing/malformed siblings cannot establish a safe order. No date is rewritten.
    """
    dates=[]
    for pin in SEASON_PINS:
        raw=value if pin==field.pin else data.get(pin)
        if raw=='00/00' and pin!=field.pin:
            continue
        try:
            day,month=map(int,date_string(raw).split('/'))
        except WriteValidationError:
            raise WriteValidationError('season_dates_unavailable') from None
        dates.append(date(2001,month,day).timetuple().tm_yday)
    if len(set(dates)) != len(dates):
        raise WriteValidationError('invalid_season_order')
    if len(dates)>1:
        forward_span=sum((following-current)%365 for current,following in zip(dates,dates[1:]+dates[:1]))
        if forward_span!=365:
            raise WriteValidationError('invalid_season_order')


MAX_RAMP_MINUTES = 240


def ramp_minutes(value):
    """Maintainer-confirmed controller range: 0–240, whole minutes."""
    try:
        number=numeric(value,maximum=MAX_RAMP_MINUTES)
    except WriteValidationError:
        raise WriteValidationError('invalid_ramp') from None
    if number!=number.to_integral_value():
        raise WriteValidationError('invalid_ramp')
    return number
