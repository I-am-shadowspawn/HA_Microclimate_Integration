"""Versioned, permission-filtered card projections; no additional polling."""
from datetime import time
import hashlib
import json
from uuid import uuid4

from homeassistant.auth.permissions.const import POLICY_READ, POLICY_CONTROL
from homeassistant.helpers import device_registry as dr, entity_registry as er
from .const import DOMAIN, MODEL_CHANNEL_OPTIONS
from .const_helpers import enum_value
from .write_contract import (write_definitions, observed_numeric, applicable,
                             control_mode, timing_mode, date_string, WriteValidationError)

SCHEMA_VERSION = 1


def generation(coordinator):
    context = (coordinator.entry.data.get('token'), coordinator.entry.data.get('model'))
    if getattr(coordinator, '_card_context', None) != context:
        coordinator._card_context = context
        coordinator._card_generation = uuid4().hex
    return coordinator._card_generation


def resolve(hass, device_id):
    device = dr.async_get(hass).async_get(device_id)
    if device is not None and device.disabled_by is None:
        for entry_id, coordinator in hass.data.get(DOMAIN, {}).items():
            if entry_id not in device.config_entries or coordinator.closed:
                continue
            for channel in (None, *MODEL_CHANNEL_OPTIONS.get(coordinator.entry.data.get('model'), {})):
                identity = entry_id if channel is None else f'{entry_id}_{channel}'
                if (DOMAIN, identity) in device.identifiers:
                    return coordinator, channel, device
    raise WriteValidationError('device_unavailable')


def scoped_fields(coordinator, channel):
    return tuple(f for f in write_definitions(coordinator.entry.data['model'])
                 if f.channel == channel or f.channel is None)


def revision(coordinator, channel, data=None):
    data = coordinator.data if data is None else data
    # All editable values, including preserved time suffixes, but no measurements.
    values = {f.key: (data.get(f.pin) if f.kind == 'time' else value_of(f, data))
              for f in scoped_fields(coordinator, channel)}
    payload = json.dumps([generation(coordinator), values], sort_keys=True, separators=(',', ':'), allow_nan=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def binding(hass, coordinator, field):
    """Resolve the server-owned permission anchor, never a client entity ID."""
    registry = er.async_get(hass)
    entry_id = coordinator.entry.entry_id
    platform = 'sensor' if field.index is not None else field.platform
    unique_id = (f'{entry_id}_{field.channel}_schedule' if field.index is not None
                 else f'{entry_id}_write_{field.key}')
    eid = registry.async_get_entity_id(platform, DOMAIN, unique_id)
    entity = registry.async_get(eid) if eid else None
    device = dr.async_get(hass).async_get(entity.device_id) if entity and entity.device_id else None
    identity = f'{entry_id}_{field.channel}' if field.channel else entry_id
    if (entity is None or entity.config_entry_id != entry_id or device is None
            or entry_id not in device.config_entries or (DOMAIN, identity) not in device.identifiers
            or device.disabled_by is not None):
        return None
    return entity


def field_access(hass, coordinator, field, user, *, control=False):
    entity = binding(hass, coordinator, field)
    return bool(entity and entity.disabled_by is None
                and allowed(user, entity.entity_id, POLICY_READ)
                and (not control or allowed(user, entity.entity_id, POLICY_CONTROL)))


def allowed(user, entity_id, policy):
    return user is not None and user.permissions.check_entity(entity_id, policy)


def authorize(hass, coordinator, user, fields):
    if not coordinator.writes_enabled or not coordinator.last_update_success:
        raise WriteValidationError('writes_unavailable')
    for field in fields:
        if (not field_access(hass, coordinator, field, user, control=True)
                or not applicable(field, coordinator.data)):
            raise WriteValidationError('control_denied')


def value_of(field, data):
    try:
        if field.kind == 'enum':
            return enum_value(data.get(field.pin), dict(field.options))
        if field.kind == 'date':
            return date_string(data.get(field.pin))
        if field.kind == 'time':
            raw = data.get(field.pin)
            number = float(str(raw).split('\0')[0])
            return int(number) if number.is_integer() and 0 <= number < 86400 else None
        return float(observed_numeric(field, data))
    except (ValueError, TypeError, OverflowError, WriteValidationError):
        return None


def input_value(field, value):
    if field.kind == 'time':
        if type(value) is not int or not 0 <= value < 86400:
            raise WriteValidationError('invalid_time')
        return time(value // 3600, value // 60 % 60, value % 60)
    return value


def snapshot(hass, coordinator, channel, device, user):
    data = coordinator.data or {}
    fields = []
    for field in scoped_fields(coordinator, channel):
        entity = binding(hass, coordinator, field)
        if not field_access(hass, coordinator, field, user):
            continue
        writable = (field.channel == channel and coordinator.writes_enabled
                    and coordinator.last_update_success and entity.disabled_by is None
                    and allowed(user, entity.entity_id, POLICY_CONTROL) and applicable(field, data))
        thermal = field.kind == 'number' or field.kind == 'setpoint' and control_mode(field, data) in ('heating', 'cooling')
        name = field.name
        if field.index:
            mode = timing_mode(field, data)
            label = (('Day' if field.index == 1 else 'Night') if mode == 'Day Night'
                     else f'Season {(field.index+1)//2} {"day" if field.index%2 else "night"}' if mode == 'Seasonal'
                     else f'Point {field.index}')
            name = f'{label} {"start" if field.kind == "time" else "target"}'
        fields.append({'key': field.key, 'kind': field.kind, 'label': name,
                       'index': field.index, 'shared': field.channel is None,
                       'value': value_of(field, data), 'validity': ('unset' if field.kind == 'date' and data.get(field.pin) == '00/00'
                           else 'valid' if value_of(field, data) is not None else 'missing' if field.pin not in data else 'invalid'), 'entity_id': entity.entity_id,
                       'authorization_scope': 'channel_schedule' if field.index is not None else 'entity',
                       'writable': bool(writable), 'reason': None if writable else 'Read only, unavailable or disabled',
                       'options': [label for _, label in field.options],
                       'unit': '°C' if thermal else '%' if field.kind == 'setpoint' else 'min' if field.kind == 'ramp' else None,
                       'minimum': 0, 'maximum': 240 if field.kind == 'ramp' else 100,
                       'step': 1 if field.kind == 'ramp' else 'any'})
    if not fields:
        raise WriteValidationError('read_denied')
    observations = []
    observation_ids = {f'{coordinator.entry.entry_id}_{channel}_measurement_{key}'
                       for key in ('temperature', 'setpoint', 'output')} if channel else set()
    for entity in er.async_entries_for_device(er.async_get(hass), device.id):
        if (entity.platform != DOMAIN or entity.domain not in ('sensor', 'climate')
                or entity.disabled_by is not None or not allowed(user, entity.entity_id, POLICY_READ)):
            continue
        state = hass.states.get(entity.entity_id)
        if state and entity.unique_id in observation_ids:
            observations.append({'name': entity.name or entity.original_name or state.name, 'value': state.state,
                                 'unit': state.attributes.get('unit_of_measurement')})
    return {'schema_version': SCHEMA_VERSION, 'runtime_generation': generation(coordinator),
            'revision': revision(coordinator, channel), 'device_id': device.id,
            'name': device.name_by_user or device.name, 'model': coordinator.entry.data['model'],
            'channel': channel, 'kind': 'channel' if channel else 'controller', 'fields': fields,
            'observations': observations, 'online': coordinator.last_update_success and not coordinator.closed,
            'writes_enabled': coordinator.writes_enabled, 'busy': coordinator._write_lock.locked()
                or getattr(coordinator, '_card_active', None) is not None}
