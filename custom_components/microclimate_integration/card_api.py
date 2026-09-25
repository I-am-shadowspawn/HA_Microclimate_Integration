"""Authenticated card API and bounded, non-atomic sequential save jobs."""
import asyncio
from collections import OrderedDict
import hashlib
import json
from pathlib import Path
from time import monotonic
from uuid import uuid4, UUID
import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.components.http import StaticPathConfig
from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError, ConfigEntryAuthFailed
from homeassistant.helpers import device_registry as dr
from . import coordinator as coordinator_module
from .card_model import (SCHEMA_VERSION, resolve, snapshot, revision, generation, authorize, field_access)
from .edit_plan import build_plan
from .write_contract import matches, WriteValidationError

KEY = 'microclimate_card_api'
PREFIX = 'microclimate_integration/card/'
TERMINAL = {'succeeded', 'failed', 'partial', 'uncertain', 'stopped'}


class CardAPI:
    def __init__(self, hass):
        self.hass = hass
        self.jobs = OrderedDict()
        self.listeners = set()

    def emit(self, job):
        job['sequence'] += 1
        for listener in tuple(self.listeners):
            listener(job['operation_id'])

    def public_job(self, job):
        return {k: job[k] for k in ('operation_id', 'sequence', 'status', 'phase', 'confirmed', 'total', 'fields', 'reason')}

    def prune(self):
        counts = {}
        for key, job in reversed(tuple(self.jobs.items())):
            if job['status'] not in TERMINAL:
                continue
            entry_id = job['entry_id']
            counts[entry_id] = counts.get(entry_id, 0)+1
            if counts[entry_id] > 20 or monotonic()-job['finished'] > 3600:
                del self.jobs[key]

    def find_job(self, msg, user):
        self.prune()
        job = self.jobs.get(msg['operation_id'])
        if job is None or job['user_id'] != user.id:
            raise WriteValidationError('operation_unavailable')
        c = self.hass.data.get('microclimate_integration', {}).get(job['entry_id'], job['coordinator'])
        if generation(c) != job['generation']:
            raise WriteValidationError('operation_unavailable')
        # Recheck read/control scope; a revoked permission cannot expose results.
        for field in job['plan'].fields:
            if not field_access(self.hass, c, field, user, control=True):
                raise WriteValidationError('control_denied')
        return job

    async def save(self, msg, user):
        self.prune()
        c, channel, device = resolve(self.hass, msg['device_id'])
        if msg['schema_version'] != SCHEMA_VERSION or msg['runtime_generation'] != generation(c):
            raise WriteValidationError('version_changed')
        try:
            UUID(msg['request_id'])
            encoded = json.dumps(msg['patch'], sort_keys=True, allow_nan=False)
            if len(encoded) > 16000:
                raise ValueError
        except (ValueError, TypeError):
            raise WriteValidationError('invalid_patch') from None
        digest = hashlib.sha256(encoded.encode()).hexdigest()
        for job in self.jobs.values():
            if (job['user_id'], job['entry_id'], job['request_id']) == (user.id, c.entry.entry_id, msg['request_id']):
                if (job['digest'], job['device_id'], job['generation']) != (digest, device.id, generation(c)):
                    raise WriteValidationError('request_id_reused')
                authorize(self.hass, c, user, job['plan'].fields)
                return {'operation_id': job['operation_id']}
        if getattr(c, '_card_active', None) is not None or c._write_lock.locked():
            raise WriteValidationError('busy')
        if revision(c, channel) != msg['base_revision']:
            raise WriteValidationError('conflict')
        plan = build_plan(c.entry.data['model'], channel, c.data, msg['patch'])
        authorize(self.hass, c, user, plan.fields)
        operation_id = uuid4().hex
        job = {'operation_id': operation_id, 'device_id': device.id, 'entry_id': c.entry.entry_id,
               'user_id': user.id, 'request_id': msg['request_id'], 'digest': digest,
               'generation': generation(c), 'coordinator': c, 'plan': plan, 'sequence': 0, 'status': 'pending',
               'phase': 'Preflight', 'confirmed': 0, 'total': len(plan.steps), 'reason': None,
               'completion': asyncio.get_running_loop().create_future(),
               'fields': [{'key': s.field.key, 'label': s.field.name if s.field.index is None else
                           f'Point {s.field.index} {"start" if s.field.kind == "time" else "target"}',
                           'status': 'not-sent'} for s in plan.steps], 'stop': False}
        self.jobs[operation_id] = job
        c._card_active = operation_id
        task = self.hass.async_create_background_task(self.run(c, channel, user, msg, job), 'Microclimate card save')
        c._write_tasks.add(task)
        task.add_done_callback(c._write_tasks.discard)
        c.async_update_listeners()
        return {'operation_id': operation_id}

    async def run(self, c, channel, user, msg, job):
        in_flight = False
        try:
            async with asyncio.timeout(600), c._write_lock, c._io_lock:
                authorize(self.hass, c, user, job['plan'].fields)
                data = await coordinator_module.async_update_data(self.hass, c.entry)
                c._publish(data)
                if generation(c) != job['generation'] or revision(c, channel) != msg['base_revision']:
                    raise WriteValidationError('conflict')
                plan = build_plan(c.entry.data['model'], channel, data, msg['patch'])
                job['status'] = 'running'
                job['phase'] = 'Applying changes'
                self.emit(job)
                expected_revision = revision(c, channel)
                for index, step in enumerate(plan.steps):
                    if job['stop']:
                        job['status'] = 'stopped'
                        break
                    authorize(self.hass, c, user, plan.fields)
                    if generation(c) != job['generation']:
                        raise WriteValidationError('conflict')
                    fresh = await coordinator_module.async_update_data(self.hass, c.entry)
                    c._publish(fresh)
                    if revision(c, channel) != expected_revision:
                        raise WriteValidationError('conflict')
                    expected = dict(fresh)
                    expected[step.field.pin] = step.wire
                    # Primitive does a further fresh read; guard its publication too.
                    c._card_expected_revision = (channel, expected_revision)
                    in_flight = True
                    job['fields'][index]['status'] = 'pending'
                    self.emit(job)
                    await c._async_write_locked(step.field.key, step.value,
                                                authorize_write=lambda: authorize(self.hass, c, user, plan.fields))
                    in_flight = False
                    job['fields'][index]['status'] = 'confirmed'
                    job['confirmed'] += 1
                    # Wire numeric/string equivalence is normalized for revision comparison.
                    if revision(c, channel) != revision(c, channel, expected):
                        raise WriteValidationError('conflict')
                    expected_revision = revision(c, channel)
                    self.emit(job)
                else:
                    final = await coordinator_module.async_update_data(self.hass, c.entry)
                    c._publish(final)
                    if (generation(c) != job['generation'] or revision(c, channel) != expected_revision
                            or any(not matches(f, str(plan.expected[f.pin]), final) for f in plan.fields)):
                        raise WriteValidationError('final_mismatch')
                    job['status'] = 'succeeded'
                job['phase'] = 'Finished'
        except asyncio.CancelledError:
            job['status'] = 'uncertain' if in_flight else 'stopped'
            job['reason'] = 'Integration unloaded; no automatic replay'
        except ConfigEntryAuthFailed:
            c.async_set_update_error(ConfigEntryAuthFailed('Microclimate authentication failed'))
            c.entry.async_start_reauth(self.hass)
            job['status'] = 'uncertain' if in_flight else 'partial' if job['confirmed'] else 'failed'
            job['reason'] = 'invalid_auth'
        except (WriteValidationError, HomeAssistantError, TimeoutError) as err:
            reason = err.code if isinstance(err, WriteValidationError) else getattr(err, 'translation_key', None) or 'read_failed'
            uncertain = in_flight and (reason in ('uncertain', 'stale_context', 'read_failed'))
            job['status'] = 'uncertain' if uncertain else 'partial' if job['confirmed'] else 'failed'
            job['reason'] = reason
        except Exception:
            # Sanitized unexpected failures never expose vendor URLs or credentials.
            job['status'] = 'uncertain' if in_flight else 'partial' if job['confirmed'] else 'failed'
            job['reason'] = 'operation_failed'
        finally:
            for field in job['fields']:
                if field['status'] == 'pending':
                    field['status'] = 'uncertain' if job['status'] == 'uncertain' else 'failed'
            job['finished'] = monotonic()
            job['phase'] = 'Finished'
            c._card_active = None
            c._card_expected_revision = None
            self.emit(job)
            self.prune()
            if not c.closed:
                c.async_update_listeners()
            if not job['completion'].done():
                job['completion'].set_result(self.public_job(job))

    async def handle(self, connection, msg, verb):
        user = connection.user
        try:
            if user is None:
                raise WriteValidationError('unauthorized')
            if verb == 'list':
                devices = []
                for device in dr.async_get(self.hass).devices.values():
                    try:
                        c, channel, resolved = resolve(self.hass, device.id)
                        view = snapshot(self.hass, c, channel, resolved, user)
                    except WriteValidationError:
                        continue
                    devices.append({k: view[k] for k in ('device_id', 'kind', 'name', 'channel', 'model')})
                connection.send_result(msg['id'], devices)
            elif verb == 'subscribe':
                c, channel, device = resolve(self.hass, msg['device_id'])
                snapshot(self.hass, c, channel, device, user)
                attached = None
                remove_coordinator = None
                @callback
                def send(*_):
                    nonlocal attached, remove_coordinator
                    try:
                        current, current_channel, current_device = resolve(self.hass, msg['device_id'])
                        if current is not attached:
                            if remove_coordinator:
                                remove_coordinator()
                            attached = current
                            remove_coordinator = current.async_add_listener(send)
                        value = snapshot(self.hass, current, current_channel, current_device, user)
                    except WriteValidationError as err:
                        value = {'error': err.code}
                    connection.send_event(msg['id'], value)
                remove_entry = self.hass.bus.async_listen('microclimate_card_entry_changed', send)
                remove_entity = self.hass.bus.async_listen('entity_registry_updated', send)
                remove_device = self.hass.bus.async_listen('device_registry_updated', send)
                @callback
                def unsubscribe():
                    if remove_coordinator:
                        remove_coordinator()
                    remove_entry()
                    remove_entity()
                    remove_device()
                connection.subscriptions[msg['id']] = unsubscribe
                connection.send_result(msg['id'])
                send()
            elif verb == 'request':
                c, channel, device = resolve(self.hass, msg['device_id'])
                snapshot(self.hass, c, channel, device, user)
                self.prune()
                found = next((job for job in self.jobs.values()
                              if job['device_id'] == device.id and job['user_id'] == user.id
                              and job['request_id'] == msg['request_id']
                              and job['generation'] == generation(c)), None)
                if found:
                    self.find_job({'operation_id': found['operation_id']}, user)
                connection.send_result(msg['id'], {'operation_id': found['operation_id']} if found else None)
            elif verb == 'save':
                connection.send_result(msg['id'], await self.save(msg, user))
            else:
                job = self.find_job(msg, user)
                if verb == 'stop':
                    job['stop'] = True
                    connection.send_result(msg['id'])
                else:
                    @callback
                    def send_job(operation_id):
                        if operation_id != job['operation_id']:
                            return
                        try:
                            checked = self.find_job(msg, user)
                            value = self.public_job(checked)
                        except WriteValidationError as err:
                            value = {'error': err.code}
                        connection.send_event(msg['id'], value)
                    self.listeners.add(send_job)
                    connection.subscriptions[msg['id']] = lambda: self.listeners.discard(send_job)
                    connection.send_result(msg['id'])
                    send_job(job['operation_id'])
        except WriteValidationError as err:
            connection.send_error(msg['id'], err.code, err.code.replace('_', ' '))


async def async_setup_card_api(hass):
    if KEY in hass.data:
        return
    api = CardAPI(hass)
    short_string = vol.All(str, vol.Length(min=1, max=128))
    for verb in ('list', 'subscribe', 'save', 'operation', 'stop', 'request'):
        schema = {vol.Required('type'): PREFIX+verb}
        if verb in ('subscribe', 'save', 'request'):
            schema[vol.Required('device_id')] = short_string
        if verb in ('operation', 'stop'):
            schema[vol.Required('operation_id')] = short_string
        if verb == 'request':
            schema[vol.Required('request_id')] = short_string
        if verb == 'save':
            schema.update({vol.Required('schema_version'): int, vol.Required('patch'): dict,
                           vol.Required('runtime_generation'): short_string,
                           vol.Required('base_revision'): short_string,
                           vol.Required('request_id'): short_string})
        async def handler(hass, connection, msg, action=verb):
            await api.handle(connection, msg, action)
        decorated = websocket_api.websocket_command(schema)(websocket_api.async_response(handler))
        websocket_api.async_register_command(hass, decorated)
    await hass.http.async_register_static_paths([StaticPathConfig(
        '/microclimate_integration/microclimate-cards.js',
        str(Path(__file__).parent / 'frontend' / 'microclimate-cards.js'), False)])
    hass.data[KEY] = api
