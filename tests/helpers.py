"""Shared data builders and projections for integration tests."""

import asyncio
from typing import Any
from uuid import uuid4

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from custom_components.microclimate_integration.card_model import snapshot
from custom_components.microclimate_integration.const import CHANNELS, DOMAIN, MODEL_CHANNEL_OPTIONS
from custom_components.microclimate_integration.write_contract import (
    definition_for,
    write_definitions,
)
from tests.http_mocks import json_stream


def payload(model: str = "Evo Connect 3") -> dict[str, Any]:
    """Create a complete deterministic pin payload for a controller model."""
    data: dict[str, Any] = {
        "v20": "01/01",
        "v21": "00/00",
        "v22": "00/00",
        "v23": "00/00",
        "v25": "C",
    }
    for field in write_definitions(model):
        if field.kind == "time":
            separator = chr(0)
            data[field.pin] = separator.join(("0", "0", "Europe/London", "0"))
        elif field.kind in ("number", "setpoint", "ramp"):
            data[field.pin] = 20
        elif field.kind == "enum":
            data[field.pin] = 0
    for channel, features in MODEL_CHANNEL_OPTIONS[model].items():
        data[CHANNELS[channel]["control_pin"]] = 1 if features["hasTemperatureProbe"] else 0
        data[CHANNELS[channel]["timing_type"]] = 2
    return data


def populate(data: dict[str, Any], count: int = 8, channel: str = "Yellow") -> None:
    """Populate the first count schedule points with deterministic values."""
    for index in range(1, 9):
        time_field = definition_for("Evo Connect 3", f"{channel}_period_{index}_time")
        target_field = definition_for("Evo Connect 3", f"{channel}_period_{index}_setpoint")
        seconds = index * 3600 if index <= count else 0
        separator = chr(0)
        data[time_field.pin] = separator.join((str(seconds), str(seconds), "Europe/London", "0"))
        data[target_field.pin] = 20 + index if index <= count else 0


def points(count: int) -> list[dict[str, int]]:
    """Return count ordered points suitable for a Multi schedule."""
    return [{"seconds": index * 3600, "target_native": 20 + index} for index in range(1, count + 1)]


def patch(schedule_points: list[dict[str, int]]) -> dict[str, Any]:
    """Build the channel Multi patch used by schedule planner tests."""
    return {
        "kind": "channel",
        "fields": {},
        "schedule": {"mode": "Multi", "points": schedule_points},
    }


async def card_context(hass: HomeAssistant, runtime: tuple[Any, ...], user: Any) -> tuple[Any, ...]:
    """Build an authorized channel snapshot and matching save request."""
    entry, coordinator, data, reader, writer = runtime
    populate(data, 4)
    coordinator._publish(dict(data))
    device = dr.async_get(hass).async_get_device_by_identifier(
        (DOMAIN, f"{entry.entry_id}_Yellow"), entry.entry_id
    )
    view = snapshot(hass, coordinator, "Yellow", device, user)
    message = {
        "device_id": device.id,
        "schema_version": 1,
        "base_revision": view["revision"],
        "runtime_generation": view["runtime_generation"],
        "request_id": str(uuid4()),
        "patch": patch(points(3)),
    }
    return coordinator, data, writer, device, view, message


async def wait_job(hass: HomeAssistant, api: Any, result: dict[str, str]) -> Any:
    """Wait for a card operation to reach a terminal state."""
    for _ in range(500):
        await asyncio.sleep(0)
        job = api.manager.jobs[result["operation_id"]]
        if job["status"] in ("succeeded", "failed", "partial", "uncertain", "stopped"):
            return job
    pytest.fail("job did not finish")


def http_response(status: int, response_payload: Any) -> Any:
    """Create the async HTTP response context used at the auth boundary."""
    from unittest.mock import AsyncMock

    response = AsyncMock(status=status)
    response.json.return_value = response_payload
    context = AsyncMock()
    context.__aenter__.return_value = json_stream(response)
    return context


def entity_id(hass: HomeAssistant, entry: Any, platform: str, key: str) -> str | None:
    """Resolve the registry entity belonging to a write definition."""
    from homeassistant.helpers import entity_registry as er

    return er.async_get(hass).async_get_entity_id(platform, DOMAIN, f"{entry.entry_id}_write_{key}")
