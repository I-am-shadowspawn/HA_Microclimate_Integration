"""Shared Home Assistant runtime fixture for integration tests."""

from collections.abc import AsyncIterator
from typing import Any
from unittest.mock import patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.microclimate_integration import coordinator as coordinator_module
from custom_components.microclimate_integration.const import DOMAIN
from custom_components.microclimate_integration.write_transport import UpdateResult
from tests.helpers import payload


@pytest.fixture
async def runtime(hass: Any) -> AsyncIterator[tuple[Any, Any, dict[str, Any], Any, Any]]:
    """Load a controller entry with in-memory mocked API reads and writes."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={"evo_device": "writes", "model": "Evo Connect 3", "token": "fake"},
    )
    entry.add_to_hass(hass)
    data = payload()

    async def read(*args: Any, **kwargs: Any) -> dict[str, Any]:
        return dict(data)

    async def update(token: str, pin: str, value: Any, **kwargs: Any) -> UpdateResult:
        data[pin] = value
        return UpdateResult("acknowledged")

    with (
        patch(
            "custom_components.microclimate_integration.api_client.fetch_data", side_effect=read
        ) as reader,
        patch(
            "custom_components.microclimate_integration.write_transport.update_pin",
            side_effect=update,
        ) as writer,
        patch.object(coordinator_module, "READBACK_DELAYS", (0, 0, 0, 0)),
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        yield entry, hass.data[DOMAIN][entry.entry_id], data, reader, writer
        if entry.entry_id in hass.data[DOMAIN]:
            await hass.config_entries.async_unload(entry.entry_id)
            await hass.async_block_till_done()
