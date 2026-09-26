"""Ownership, bounded resources and safe classified failures; no live I/O."""

import asyncio
from time import monotonic
from unittest.mock import Mock
from unittest.mock import patch as mock_patch

import pytest
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from custom_components.microclimate_integration import card_api, card_jobs
from custom_components.microclimate_integration.api_client import EvoDeviceDataError, fetch_data
from custom_components.microclimate_integration.card_api import CardAPI
from custom_components.microclimate_integration.card_model import generation
from custom_components.microclimate_integration.config_flow import MicroclimateConfigFlow
from custom_components.microclimate_integration.coordinator import OPERATION_TIMEOUT
from custom_components.microclimate_integration.errors import ReadUpdateFailed
from custom_components.microclimate_integration.helpers import async_update_data
from tests.helpers import card_context as context
from tests.helpers import http_response, patch, points, populate, wait_job


@pytest.mark.parametrize(
    ("status", "body", "code"),
    [(429, {}, "rate_limited"), (503, {}, "unavailable"), (200, [], "invalid_payload")],
)
async def test_read_categories_survive_all_layers(hass, runtime, status, body, code):
    entry, c, data, reader, writer = runtime
    # Bypass the fixture fetch mock to exercise the real HTTP adapter, then the
    # entry/setup adapter, coordinator errors and config-flow classification.
    from custom_components.microclimate_integration import api_client

    with (
        mock_patch.object(api_client, "fetch_data", fetch_data),
        mock_patch("aiohttp.ClientSession.get", return_value=http_response(status, body)),
    ):
        with pytest.raises(EvoDeviceDataError) as error:
            await fetch_data("secret", session=async_get_clientsession(hass))
        assert error.value.code == code
        with pytest.raises(ReadUpdateFailed) as error:
            await async_update_data(hass, entry)
        assert error.value.code == code
        assert "secret" not in str(error.value) and "http" not in str(error.value)
        flow = MicroclimateConfigFlow()
        flow.hass = hass
        assert await flow._validate_token("secret") == (
            "cannot_connect" if code == "unavailable" else code
        )
        with pytest.raises(HomeAssistantError) as error:
            await c.async_write("Yellow_lower_alarm", 30)
        assert error.value.translation_key == code and writer.call_count == 0


async def test_cancel_before_job_body_completes_future(hass, runtime, hass_admin_user):
    c, data, writer, device, view, msg = await context(hass, runtime, hass_admin_user)
    api = CardAPI(hass)

    # HA may start background tasks eagerly; force cancellation before first step.
    def never_start(coro, name):
        task = asyncio.create_task(coro)
        task.cancel()
        return task

    with mock_patch.object(hass, "async_create_background_task", side_effect=never_start):
        result = await api.manager.save(msg, hass_admin_user)
    job = await wait_job(hass, api, result)
    assert job["status"] == "stopped"
    assert job["completion"].done() and not job["completion"].cancelled()
    assert c.active_job is None and not c.busy and writer.call_count == 0
    assert c.entry.runtime_data is c


async def test_full_eight_slot_job_budget_and_slow_readback(hass, runtime, hass_admin_user):
    c, data, writer, device, view, msg = await context(hass, runtime, hass_admin_user)
    populate(data, 8)
    c._publish(dict(data))
    from custom_components.microclimate_integration.card_model import revision

    msg["base_revision"] = revision(c, "Yellow")
    msg["patch"] = patch(
        [{"seconds": p["seconds"] + 60, "target_native": p["target_native"] + 1} for p in points(8)]
    )
    reader = runtime[3]

    async def slow_read(*args, **kwargs):
        await asyncio.sleep(0.001)
        return dict(data)

    reader.side_effect = slow_read
    api = CardAPI(hass)
    result = await api.manager.save(msg, hass_admin_user)
    await asyncio.wait_for(
        asyncio.shield(api.manager.jobs[result["operation_id"]]["completion"]), 5
    )
    job = api.manager.jobs[result["operation_id"]]
    assert job["total"] == job["confirmed"] == 16 and writer.call_count == 16
    assert job["status"] == "succeeded"
    assert card_jobs.job_timeout(16) >= 16 * (OPERATION_TIMEOUT + 20) + 40


def test_global_history_across_many_entries(hass):
    jobs = card_jobs.CardJobs(hass)
    for index in range(300):
        jobs.jobs[str(index)] = {
            "entry_id": str(index),
            "status": "succeeded",
            "finished": monotonic(),
        }
    jobs.prune()
    assert len(jobs.jobs) == card_jobs.MAX_HISTORY
    assert "0" not in jobs.jobs and "299" in jobs.jobs
    for job in jobs.jobs.values():
        job["finished"] -= 3601
    jobs.prune()
    assert not jobs.jobs


async def test_active_capacity_rejects_before_io(hass, runtime, hass_admin_user, monkeypatch):
    c, data, writer, device, view, msg = await context(hass, runtime, hass_admin_user)
    api = CardAPI(hass)
    monkeypatch.setattr(card_jobs, "MAX_ACTIVE_JOBS", 0)
    from custom_components.microclimate_integration.write_contract import WriteValidationError

    with pytest.raises(WriteValidationError, match="job_limit"):
        await api.manager.save(msg, hass_admin_user)
    assert not api.manager.jobs and not c.busy and writer.call_count == 0


async def test_subscription_limits_and_disconnect_cleanup(
    hass, runtime, hass_admin_user, monkeypatch
):
    c, data, writer, device, view, msg = await context(hass, runtime, hass_admin_user)
    api = CardAPI(hass)
    connection = Mock(user=hass_admin_user, subscriptions={})
    monkeypatch.setattr(card_api, "MAX_CONNECTION_SUBSCRIPTIONS", 1)
    await api.handle(connection, {"id": 1, "device_id": device.id}, "subscribe")
    await api.handle(connection, {"id": 2, "device_id": device.id}, "subscribe")
    assert connection.send_error.call_args.args[1] == "subscription_limit"
    assert len(api.subscriptions) == 1
    connection.subscriptions.pop(1)()
    assert not api.subscriptions
    monkeypatch.setattr(card_api, "MAX_SUBSCRIPTIONS", 0)
    await api.handle(connection, {"id": 3, "device_id": device.id}, "subscribe")
    assert connection.send_error.call_args.args[1] == "subscription_limit"


async def test_batch_preflight_category_reaches_public_job(hass, runtime, hass_admin_user):
    c, data, writer, device, view, msg = await context(hass, runtime, hass_admin_user)
    runtime[3].side_effect = EvoDeviceDataError("sanitized", code="rate_limited")
    api = CardAPI(hass)
    job = await wait_job(hass, api, await api.manager.save(msg, hass_admin_user))
    public = api.manager.public_job(job)
    assert public["reason"] == "rate_limited" and "Wait" in public["reason_message"]
    assert job["status"] == "failed" and writer.call_count == 0


async def test_reload_replaces_runtime_and_generation(hass, runtime, hass_admin_user):
    c, data, writer, device, view, msg = await context(hass, runtime, hass_admin_user)
    old = generation(c)
    assert await hass.config_entries.async_reload(c.entry.entry_id)
    replacement = c.entry.runtime_data
    assert replacement is not c and c.closed
    assert generation(replacement) != old and not replacement.busy
    assert not c._write_tasks and not c._refresh_tasks


async def test_entries_keep_independent_jobs_and_locks(hass, runtime, hass_admin_user):
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    from custom_components.microclimate_integration.const import DOMAIN

    c, data, writer, device, view, msg = await context(hass, runtime, hass_admin_user)
    second = MockConfigEntry(
        domain=DOMAIN, data={**c.entry.data, "token": "other-device", "evo_device": "second"}
    )
    second.add_to_hass(hass)
    assert await hass.config_entries.async_setup(second.entry_id)
    other = second.runtime_data
    _, _, _, _, _, other_msg = await context(
        hass, (second, other, data, runtime[3], writer), hass_admin_user
    )
    api = CardAPI(hass)
    # The first owner is blocked; the second must finish without acquiring its locks.
    await c._io_lock.acquire()
    try:
        first_result = await api.manager.save(msg, hass_admin_user)
        other_job = await wait_job(hass, api, await api.manager.save(other_msg, hass_admin_user))
        assert other_job["status"] == "succeeded"
        assert not api.manager.jobs[first_result["operation_id"]]["completion"].done()
        await c.async_stop_writes()
        assert api.manager.jobs[first_result["operation_id"]]["status"] == "stopped"
        assert not other.closed and not other.busy
    finally:
        c._io_lock.release()
        await hass.config_entries.async_unload(second.entry_id)


async def test_noop_rechecks_permission_after_await(hass, runtime, hass_admin_user):
    c, data, writer, device, view, msg = await context(hass, runtime, hass_admin_user)
    msg["patch"] = patch(points(4))
    user = Mock(id="revoked")
    user.permissions.check_entity.return_value = True

    async def revoke():
        user.permissions.check_entity.return_value = False
        return dict(data)

    api = CardAPI(hass)
    with mock_patch.object(c, "async_read_locked", side_effect=revoke):
        job = await wait_job(hass, api, await api.manager.save(msg, user))
    assert job["status"] == "failed" and job["reason"] == "control_denied"
    assert not writer.called


async def test_batch_deadline_stops_without_replay(hass, runtime, hass_admin_user, monkeypatch):
    c, data, writer, device, view, msg = await context(hass, runtime, hass_admin_user)

    async def blocked_read():
        await asyncio.Future()

    monkeypatch.setattr(card_jobs, "job_timeout", lambda _: 0.01)
    api = CardAPI(hass)
    with mock_patch.object(c, "async_read_locked", side_effect=blocked_read):
        result = await api.manager.save(msg, hass_admin_user)
        outcome = await asyncio.wait_for(api.manager.jobs[result["operation_id"]]["completion"], 1)
    assert outcome["status"] == "failed" and outcome["reason"] == "operation_timeout"
    assert not c.busy and not writer.called
