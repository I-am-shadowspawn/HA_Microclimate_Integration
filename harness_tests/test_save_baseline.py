"""Shared baseline safety at real batch/coordinator boundaries."""
import asyncio
from unittest.mock import Mock

import pytest

from custom_components.microclimate_integration.card_api import CardAPI
from custom_components.microclimate_integration.errors import ReadUpdateFailed
from test_card_contract import context, wait_job
from test_write_runtime import runtime


@pytest.mark.parametrize('read_number,writes,reason', [
    (2, 0, 'conflict'), (3, 1, 'conflict'), (6, 2, 'final_mismatch'),
])
async def test_edit_conflicts_at_baseline_readback_and_final(
        hass, runtime, hass_admin_user, read_number, writes, reason):
    c, data, writer, _, _, msg = await context(hass, runtime, hass_admin_user)
    reader = runtime[3]
    reader.reset_mock()

    async def read(*args, **kwargs):
        if reader.await_count == read_number:
            data['v49'] = 44  # External edit to another field in the same scope.
        return dict(data)

    reader.side_effect = read
    api = CardAPI(hass)
    job = await wait_job(hass, api, await api.manager.save(msg, hass_admin_user))
    assert job['reason'] == reason
    assert job['status'] == ('failed' if writes == 0 else 'partial')
    assert writer.await_count == job['confirmed'] == writes
    assert c.data['v49'] == 44


@pytest.mark.parametrize('change', ['unit', 'timing', 'token', 'model', 'writes', 'permission'])
async def test_context_and_permission_changes_during_shared_read_send_nothing(
        hass, runtime, hass_admin_user, change):
    c, data, writer, _, _, msg = await context(hass, runtime, hass_admin_user)
    reader = runtime[3]
    reader.reset_mock()
    user = Mock(id='baseline-user')
    user.permissions.check_entity.return_value = True

    async def read(*args, **kwargs):
        if reader.await_count == 2:
            await asyncio.sleep(0)  # Revocation/change while the HTTP read is awaited.
            if change == 'unit':
                data['v25'] = 'F'
            elif change == 'timing':
                data['v53'] = 1
            elif change in ('token', 'model'):
                hass.config_entries.async_update_entry(c.entry, data={
                    **c.entry.data, change: 'other-token' if change == 'token' else 'Evo Connect 2'})
            elif change == 'writes':
                hass.config_entries.async_update_entry(c.entry, options={'enable_writes': False})
            else:
                user.permissions.check_entity.return_value = False
        return dict(data)

    reader.side_effect = read
    api = CardAPI(hass)
    job = await wait_job(hass, api, await api.manager.save(msg, user))
    assert job['status'] != 'succeeded'
    assert job['reason'] == {
        'unit': 'conflict', 'timing': 'conflict', 'token': 'stale_context',
        'model': 'stale_context', 'writes': 'writes_disabled', 'permission': 'control_denied',
    }[change]
    assert writer.await_count == job['confirmed'] == 0


async def test_shared_baseline_read_failure_sends_nothing(hass, runtime, hass_admin_user):
    c, data, writer, _, _, msg = await context(hass, runtime, hass_admin_user)
    reader = runtime[3]
    reader.reset_mock()

    async def read(*args, **kwargs):
        if reader.await_count == 2:
            raise ReadUpdateFailed('unavailable')
        return dict(data)

    reader.side_effect = read
    api = CardAPI(hass)
    job = await wait_job(hass, api, await api.manager.save(msg, hass_admin_user))
    assert job['reason'] == 'unavailable'
    assert writer.await_count == 0


async def test_delayed_confirmation_only_retries_reads(hass, runtime, hass_admin_user):
    c, data, writer, _, _, msg = await context(hass, runtime, hass_admin_user)
    reader = runtime[3]
    reader.reset_mock()
    original_update = writer.side_effect
    previous = dict(data)
    stale_reads = 0

    async def update(*args, **kwargs):
        nonlocal previous, stale_reads
        previous = dict(data)
        stale_reads = 1
        return await original_update(*args, **kwargs)

    async def read(*args, **kwargs):
        nonlocal stale_reads
        if stale_reads:
            stale_reads -= 1
            return dict(previous)
        return dict(data)

    reader.side_effect = read
    writer.side_effect = update
    api = CardAPI(hass)
    job = await wait_job(hass, api, await api.manager.save(msg, hass_admin_user))
    assert job['status'] == 'succeeded'
    assert writer.await_count == job['confirmed'] == 2
    assert reader.await_count == 8  # Six normal reads plus two delayed confirmations.


async def test_poll_and_native_write_wait_for_batch(hass, runtime, hass_admin_user):
    c, data, writer, _, _, msg = await context(hass, runtime, hass_admin_user)
    reader = runtime[3]
    reader.reset_mock()
    entered, resume = asyncio.Event(), asyncio.Event()
    trace = []
    original_update = writer.side_effect

    async def read(*args, **kwargs):
        trace.append('read')
        if reader.await_count == 2:
            entered.set()
            await resume.wait()
        return dict(data)

    async def update(token, pin, value, **kwargs):
        trace.append(pin)
        return await original_update(token, pin, value, **kwargs)

    reader.side_effect = read
    writer.side_effect = update
    api = CardAPI(hass)
    result = await api.manager.save(msg, hass_admin_user)
    await asyncio.wait_for(entered.wait(), 2)
    poll = asyncio.create_task(c.async_refresh())
    native = asyncio.create_task(c.async_write('Yellow_lower_alarm', 30))
    try:
        await asyncio.sleep(0)
        assert not poll.done() and not native.done()
        assert reader.await_count == 2 and writer.await_count == 0
    finally:
        resume.set()
        await asyncio.gather(poll, native)
    job = await wait_job(hass, api, result)
    assert job['status'] == 'succeeded'
    assert trace[:8] == ['read', 'read', 'v38', 'read', 'read', 'v39', 'read', 'read']
    assert writer.await_count == 3 and c.data['v49'] == '30'
