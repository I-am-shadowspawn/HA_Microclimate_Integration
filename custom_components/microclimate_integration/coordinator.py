"""A single polling/normalization owner and serialized, observed configuration writes."""
import asyncio
from contextlib import asynccontextmanager
from datetime import timedelta, datetime, timezone
import logging

from homeassistant.exceptions import ConfigEntryAuthFailed, HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from . import write_transport
from .const import DOMAIN, CONF_ENABLE_WRITES, DEFAULT_ENABLE_WRITES
from .helpers import async_update_data
from .write_contract import (WriteValidationError, applicable, context, definition_for,
                             serialize, matches, validate_input, validate_season_sequence)

_LOGGER = logging.getLogger(__name__)
OPERATION_TIMEOUT = 60
READBACK_DELAYS = (0, 2, 5, 10)


class MicroclimateCoordinator(DataUpdateCoordinator):
    """The I/O lock includes publication, preventing an older poll overwriting a write."""

    def __init__(self, hass, entry):
        self.entry = entry
        self.closed = False
        self._io_lock = asyncio.Lock()
        self._write_lock = asyncio.Lock()
        self._write_tasks = set()
        self._refresh_tasks = set()
        self.last_write = None
        super().__init__(hass, _LOGGER, name=f'microclimate_integration_{entry.data["evo_device"]}',
                         config_entry=entry, always_update=False,
                         update_method=lambda: async_update_data(hass, entry),
                         update_interval=timedelta(minutes=1))

    @property
    def writes_enabled(self):
        return not self.closed and self.entry.options.get(CONF_ENABLE_WRITES, DEFAULT_ENABLE_WRITES) is True

    async def _async_refresh(self, *args, **kwargs):
        if self.closed:
            return
        task = asyncio.current_task()
        self._refresh_tasks.add(task)
        try:
            async with self._io_lock:
                if not self.closed:
                    await super()._async_refresh(*args, **kwargs)
        finally:
            self._refresh_tasks.discard(task)

    def _check(self, model):
        if not self.writes_enabled:
            raise WriteValidationError('writes_disabled')
        if self.entry.data.get('model') != model:
            raise WriteValidationError('stale_context')

    def _publish(self, data):
        if not self.closed and (not self.last_update_success or data != self.data):
            self.async_set_updated_data(data)

    def _record(self, key, status):
        self.last_write = {'field': key, 'status': status,
                           'time': datetime.now(timezone.utc).isoformat()}
        if not self.closed:
            self.async_update_listeners()

    @asynccontextmanager
    async def _locks(self, acquire):
        if acquire:
            async with self._write_lock, self._io_lock:
                yield
        else:
            yield

    async def async_write(self, key, value):
        return await self._execute_write(key, value, acquire=True)

    async def _async_write_locked(self, key, value, *, authorize_write=None):
        """Batch owner must hold both locks; all per-pin checks still apply."""
        return await self._execute_write(key, value, acquire=False, authorize_write=authorize_write)

    async def _execute_write(self, key, value, *, acquire, authorize_write=None):
        """Validate before I/O, update once, then confirm against fresh API observations."""
        dispatched = False
        task = asyncio.current_task()
        if acquire:
            self._write_tasks.add(task)
        try:
            model = self.entry.data.get('model')
            self._check(model)
            field = definition_for(model, key)
            validate_input(field, value)
            if not applicable(field, self.data):
                raise WriteValidationError('unsupported_capability')
            initial_context = context(field, self.data)
            # Validate the wire template before waiting; rederive it from fresh data below.
            initial_wire = serialize(field, value, self.data)
            async with asyncio.timeout(OPERATION_TIMEOUT):
                async with self._locks(acquire):
                    self._check(model)
                    token = self.entry.data['token']
                    baseline = await async_update_data(self.hass, self.entry)
                    self._check(model)
                    if token != self.entry.data['token']:
                        raise WriteValidationError('stale_context')
                    self._publish(baseline)
                    guard = getattr(self, '_card_expected_revision', None)
                    if not acquire and guard is not None:
                        from .card_model import revision
                        if revision(self, guard[0]) != guard[1]:
                            raise WriteValidationError('stale_context')
                    if initial_context != context(field, baseline):
                        raise WriteValidationError('stale_context')
                    if not applicable(field, baseline):
                        raise WriteValidationError('unsupported_capability')
                    wire = serialize(field, value, baseline)
                    if field.kind == 'time' and wire != initial_wire:
                        raise WriteValidationError('stale_context')
                    # Recheck card scope after awaited reads, before any dispatch.
                    if authorize_write is not None:
                        authorize_write()
                    if matches(field, wire, baseline):
                        self._record(key, 'confirmed_no_change')
                        return
                    # No await between final option/credential checks and dispatch.
                    self._check(model)
                    dispatched = True
                    result = await write_transport.update_pin(token, field.pin, wire,
                                                              session=async_get_clientsession(self.hass))
                    if result.outcome == 'invalid_auth':
                        raise ConfigEntryAuthFailed('Microclimate authentication failed')
                    if result.outcome == 'rejected':
                        raise WriteValidationError('rejected')
                    if result.retry_after:
                        await asyncio.sleep(result.retry_after)
                    started = asyncio.get_running_loop().time()
                    observed = False
                    for delay in READBACK_DELAYS:
                        await asyncio.sleep(max(0, started + delay - asyncio.get_running_loop().time()))
                        if self.closed or self.entry.data['token'] != token:
                            raise WriteValidationError('uncertain')
                        try:
                            data = await async_update_data(self.hass, self.entry)
                        except UpdateFailed:
                            continue
                        if self.closed or self.entry.data['token'] != token or self.entry.data.get('model') != model:
                            raise WriteValidationError('uncertain')
                        self._publish(data)
                        observed = True
                        # Context cannot be reinterpreted after a write either.
                        if (field.index is not None and context(field, data)[:2] != initial_context[:2]):
                            raise WriteValidationError('stale_context')
                        if matches(field, wire, data):
                            if field.kind == 'date':
                                validate_season_sequence(field, wire, data)
                            self._record(key, 'confirmed')
                            return
                    raise WriteValidationError('rate_limited' if result.outcome == 'rate_limited'
                                               else 'mismatch' if observed else 'uncertain')
        except asyncio.CancelledError:
            if dispatched or not self.closed:
                self._record(key, 'uncertain' if dispatched else 'cancelled_before_dispatch')
            raise
        except ConfigEntryAuthFailed:
            self.async_set_update_error(ConfigEntryAuthFailed('Microclimate authentication failed'))
            self.entry.async_start_reauth(self.hass)
            self._record(key, 'invalid_auth')
            raise HomeAssistantError(translation_domain=DOMAIN, translation_key='invalid_auth') from None
        except (WriteValidationError, UpdateFailed, TimeoutError) as err:
            code = err.code if isinstance(err, WriteValidationError) else ('uncertain' if dispatched else 'read_failed')
            self._record(key, code)
            raise HomeAssistantError(translation_domain=DOMAIN, translation_key=code) from None
        finally:
            if acquire:
                self._write_tasks.discard(task)

    async def async_stop_writes(self):
        """Cancel unsent/active operations; never replay a possibly dispatched command."""
        self.closed = True
        tasks = [task for task in self._write_tasks | self._refresh_tasks if task is not asyncio.current_task()]
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def async_close(self):
        await self.async_stop_writes()
        await self.async_shutdown()
