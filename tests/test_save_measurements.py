"""Deterministic V2-19 traffic/event measurements; no live controller calls."""

import json
from collections import Counter
from unittest.mock import Mock
from uuid import uuid4

import pytest
from homeassistant.core import callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er

from custom_components.microclimate_integration.card_api import CardAPI
from custom_components.microclimate_integration.card_model import snapshot
from custom_components.microclimate_integration.const import DOMAIN
from tests.helpers import points, populate, wait_job


@pytest.mark.parametrize("count,mode", [(2, "Day Night"), (2, "Multi"), (8, "Multi")])
@pytest.mark.parametrize("change_times", [False, True], ids=["targets", "times-and-targets"])
async def test_save_counts(hass, runtime, hass_admin_user, count, mode, change_times):
    entry, c, data, reader, writer = runtime
    populate(data, count)
    data["v53"] = 1 if mode == "Day Night" else 2
    await c.async_refresh()
    await hass.async_block_till_done()
    device = dr.async_get(hass).async_get_device_by_identifier(
        (DOMAIN, f"{entry.entry_id}_Yellow"), entry.entry_id
    )
    view = snapshot(hass, c, "Yellow", device, hass_admin_user)
    desired = points(count)
    for point in desired:
        point["target_native"] += 1
        if change_times:
            point["seconds"] += 600
    msg = {
        "device_id": device.id,
        "schema_version": 1,
        "base_revision": view["revision"],
        "runtime_generation": view["runtime_generation"],
        "request_id": str(uuid4()),
        "patch": {"kind": "channel", "fields": {}, "schedule": {"mode": mode, "points": desired}},
    }
    api = CardAPI(hass)
    connection = Mock(user=hass_admin_user, subscriptions={})
    await api.handle(connection, {"id": 1, "device_id": device.id}, "subscribe")
    connection.send_event.reset_mock()
    counts = Counter()
    entity_ids = {
        entity.entity_id
        for entity in er.async_entries_for_config_entry(er.async_get(hass), entry.entry_id)
    }

    @callback
    def state_changed(event):
        if event.data["entity_id"] in entity_ids:
            counts["ha_state_events"] += 1

    remove_state = hass.bus.async_listen("state_changed", state_changed)
    remove_listener = c.async_add_listener(lambda: counts.update(["coordinator_notifications"]))
    api.manager.listeners.add(lambda _: counts.update(["job_notifications"]))
    reader.reset_mock()
    writer.reset_mock()
    try:
        job = await wait_job(hass, api, await api.manager.save(msg, hass_admin_user))
        await hass.async_block_till_done()
        assert job["status"] == "succeeded", job
        steps = count * (2 if change_times else 1)
        counts.update(
            reads=reader.await_count,
            writes=writer.await_count,
            card_snapshots=connection.send_event.call_count,
        )
        assert counts["writes"] == steps
        assert counts["reads"] == 2 * steps + 2
        assert counts["coordinator_notifications"] == 2 * steps + 2
        assert counts["card_snapshots"] == 2 * steps + 2
        assert counts["job_notifications"] == 2 * steps + 2
        assert counts["ha_state_events"] == 2 * steps
        print(
            json.dumps(
                {"mode": mode, "points": count, "times_changed": change_times, **counts},
                sort_keys=True,
            )
        )
    finally:
        connection.subscriptions[1]()
        remove_listener()
        remove_state()


@pytest.mark.parametrize("changing", [False, True], ids=["unchanged", "telemetry-changes"])
async def test_idle_poll_counts(hass, runtime, hass_admin_user, changing):
    entry, c, data, reader, writer = runtime
    counts = Counter()
    device = dr.async_get(hass).async_get_device_by_identifier(
        (DOMAIN, f"{entry.entry_id}_Yellow"), entry.entry_id
    )
    api = CardAPI(hass)
    connection = Mock(user=hass_admin_user, subscriptions={})
    await api.handle(connection, {"id": 1, "device_id": device.id}, "subscribe")
    connection.send_event.reset_mock()
    entity_ids = {
        entity.entity_id
        for entity in er.async_entries_for_config_entry(er.async_get(hass), entry.entry_id)
    }

    @callback
    def state_changed(event):
        if event.data["entity_id"] in entity_ids:
            counts["ha_state_events"] += 1

    remove_state = hass.bus.async_listen("state_changed", state_changed)
    remove_listener = c.async_add_listener(lambda: counts.update(["coordinator_notifications"]))
    reader.reset_mock()
    writer.reset_mock()
    try:
        for value in range(3):
            if changing:
                data["v0"] = 24 + value
            await c.async_refresh()
        await hass.async_block_till_done()
        assert reader.await_count == 3 and writer.await_count == 0
        assert counts["coordinator_notifications"] == (3 if changing else 0)
        counts["card_snapshots"] = connection.send_event.call_count
        counts["job_notifications"] = 0
        assert counts["card_snapshots"] == (3 if changing else 0)
        if not changing:
            assert counts["ha_state_events"] == 0
        print(
            json.dumps(
                {
                    "idle_polls": 3,
                    "changing": changing,
                    "reads": reader.await_count,
                    "writes": writer.await_count,
                    **counts,
                }
            )
        )
    finally:
        connection.subscriptions[1]()
        remove_state()
        remove_listener()
