"""Bounded job lifecycle shared by card WebSockets and HA schedule actions."""
import asyncio
from collections import OrderedDict
from typing import Any, Callable, TypedDict
from .coordinator import MicroclimateCoordinator, OPERATION_TIMEOUT
from .api_client import REQUEST_TIMEOUT
from .errors import ReadUpdateFailed, error_message
import hashlib
import json
from time import monotonic
from uuid import uuid4, UUID

from homeassistant.exceptions import HomeAssistantError, ConfigEntryAuthFailed
from .card_model import (SCHEMA_VERSION, resolve, revision, generation, authorize, field_access)
from .edit_plan import build_plan, EditPlan
from .write_contract import matches, WriteValidationError

TERMINAL = {'succeeded', 'failed', 'partial', 'uncertain', 'stopped'}


MAX_HISTORY = 200
MAX_HISTORY_PER_ENTRY = 20
HISTORY_SECONDS = 3600
MAX_ACTIVE_JOBS = 32


class Job(TypedDict):
    operation_id: str
    device_id: str
    entry_id: str
    user_id: str
    request_id: str
    digest: str
    generation: str
    coordinator: MicroclimateCoordinator
    plan: EditPlan
    sequence: int
    status: str
    phase: str
    confirmed: int
    total: int
    reason: str | None
    completion: asyncio.Future[dict[str, Any]]
    fields: list[dict[str, Any]]
    stop: bool
    finished: float


def job_timeout(step_count: int) -> float:
    # Retain the conservative existing deadline, including the former separate
    # guarded-read allowance. Sharing the baseline need not shorten deadlines.
    return 2 * REQUEST_TIMEOUT.total + step_count * (REQUEST_TIMEOUT.total + OPERATION_TIMEOUT) + 5


class CardJobs:
    def __init__(self, hass):
        self.hass = hass
        self.jobs: OrderedDict[str, Job] = OrderedDict()
        self.listeners: set[Callable[[str], None]] = set()

    def emit(self, job):
        job['sequence'] += 1
        for listener in tuple(self.listeners):
            listener(job['operation_id'])

    def public_job(self, job):
        return {**{k: job[k] for k in ('operation_id', 'sequence', 'status', 'phase', 'confirmed', 'total', 'fields', 'reason')},
                'reason_message': error_message(job['reason']) if job['reason'] else None}

    def prune(self):
        counts = {}
        retained = 0
        for key, job in reversed(tuple(self.jobs.items())):
            if job['status'] not in TERMINAL:
                continue
            entry_id = job['entry_id']
            counts[entry_id] = counts.get(entry_id, 0)+1
            retained += 1
            if counts[entry_id] > MAX_HISTORY_PER_ENTRY or monotonic()-job['finished'] > HISTORY_SECONDS or retained > MAX_HISTORY:
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
        if c.busy:
            raise WriteValidationError('busy')
        if sum(j['status'] not in TERMINAL for j in self.jobs.values()) >= MAX_ACTIVE_JOBS:
            raise WriteValidationError('job_limit')
        if revision(c, channel) != msg['base_revision']:
            raise WriteValidationError('conflict')
        plan = build_plan(c.entry.data['model'], channel, c.data, msg['patch'])
        authorize(self.hass, c, user, plan.fields)
        operation_id = uuid4().hex
        job: Job = {'operation_id': operation_id, 'device_id': device.id, 'entry_id': c.entry.entry_id,
               'user_id': user.id, 'request_id': msg['request_id'], 'digest': digest,
               'generation': generation(c), 'coordinator': c, 'plan': plan, 'sequence': 0, 'status': 'pending',
               'phase': 'Preflight', 'confirmed': 0, 'total': len(plan.steps), 'reason': None,
               'completion': asyncio.get_running_loop().create_future(),
               'finished': 0.0,
               'fields': [{'key': s.field.key, 'label': s.field.name if s.field.index is None else
                           f'Point {s.field.index} {"start" if s.field.kind == "time" else "target"}',
                           'status': 'not-sent'} for s in plan.steps], 'stop': False}
        self.jobs[operation_id] = job
        c.active_job = operation_id
        task = self.hass.async_create_background_task(self.run(c, channel, user, msg, job), 'Microclimate card save')
        c.track_write_task(task)
        # A task cancelled before its first instruction never enters run/finally.
        task.add_done_callback(lambda _: self.finish(c, job))
        c.async_update_listeners()
        return {'operation_id': operation_id}

    async def run(self, c, channel, user, msg, job):
        in_flight = False
        try:
            async with asyncio.timeout(job_timeout(len(job['plan'].steps))), c.async_batch():
                authorize(self.hass, c, user, job['plan'].fields)
                data = await c.async_read_locked()
                authorize(self.hass, c, user, job['plan'].fields)
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
                    # The primitive owns the fresh pre-dispatch read and its guard.
                    # Reuse that exact baseline only for post-write comparison.
                    in_flight = True
                    job['fields'][index]['status'] = 'pending'
                    self.emit(job)
                    baseline = await c.async_write_locked(step.field.key, step.value,
                                                expected_revision=(channel, expected_revision),
                                                authorize_write=lambda: authorize(self.hass, c, user, plan.fields))
                    in_flight = False
                    job['fields'][index]['status'] = 'confirmed'
                    job['confirmed'] += 1
                    expected = dict(baseline)
                    expected[step.field.pin] = step.wire
                    # Wire numeric/string equivalence is normalized for revision comparison.
                    if revision(c, channel) != revision(c, channel, expected):
                        raise WriteValidationError('conflict')
                    expected_revision = revision(c, channel)
                    self.emit(job)
                else:
                    final = await c.async_read_locked()
                    authorize(self.hass, c, user, plan.fields)
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
            reason = err.code if isinstance(err, (WriteValidationError, ReadUpdateFailed)) else 'operation_timeout' if isinstance(err, TimeoutError) else getattr(err, 'translation_key', None) or 'read_failed'
            uncertain = in_flight and (reason in ('uncertain', 'stale_context', 'read_failed', 'operation_timeout'))
            job['status'] = 'uncertain' if uncertain else 'partial' if job['confirmed'] else 'failed'
            job['reason'] = reason
        except Exception:
            # Sanitized unexpected failures never expose vendor URLs or credentials.
            job['status'] = 'uncertain' if in_flight else 'partial' if job['confirmed'] else 'failed'
            job['reason'] = 'operation_failed'
        finally:
            self.finish(c, job)

    def finish(self, c: MicroclimateCoordinator, job: Job) -> None:
        """Idempotent completion, including cancellation before the coroutine starts."""
        if job['completion'].done():
            return
        if job['status'] not in TERMINAL:
            job['status'] = 'stopped'
            job['reason'] = 'Integration unloaded; no automatic replay'
        for field in job['fields']:
            if field['status'] == 'pending':
                field['status'] = 'uncertain' if job['status'] == 'uncertain' else 'failed'
        job['finished'] = monotonic()
        job['phase'] = 'Finished'
        if c.active_job == job['operation_id']:
            c.active_job = None
        self.emit(job)
        self.prune()
        if not c.closed:
            c.async_update_listeners()
        job['completion'].set_result(self.public_job(job))
