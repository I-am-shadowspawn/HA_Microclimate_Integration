"""Entry-bound climate identity and coordinator publication regressions."""

from unittest.mock import AsyncMock, patch

from homeassistant.const import EVENT_STATE_CHANGED
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.microclimate_integration.api_client import EvoDeviceDataError
from custom_components.microclimate_integration.const import DOMAIN
from custom_components.microclimate_integration.identity import channel_identity


async def test_climate_refresh_failure_recovery_and_unload(hass):
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={"evo_device": "review_controller", "model": "Evo Connect", "token": "fake"},
    )
    entry.add_to_hass(hass)
    payload = {"v0": 25, "v8": 27, "v16": "Yellow", "v52": 1, "v4": 0}
    with patch(
        "custom_components.microclimate_integration.api_client.fetch_data",
        new=AsyncMock(return_value=payload),
    ) as fetch:
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        entity_id = er.async_get(hass).async_get_entity_id(
            "climate", DOMAIN, channel_identity(entry, "Yellow")
        )
        assert entity_id == "climate.microclimate_review_controller_yellow_review_controller_yellow"
        assert hass.states.get(entity_id).attributes["friendly_name"] == (
            "Microclimate review_controller Yellow review_controller: Yellow"
        )
        events = []
        unsubscribe = hass.bus.async_listen(
            EVENT_STATE_CHANGED,
            lambda event: events.append(event) if event.data["entity_id"] == entity_id else None,
        )
        coordinator = hass.data[DOMAIN][entry.entry_id]

        fetch.return_value = {**payload, "v0": 26}
        await coordinator.async_refresh()
        await hass.async_block_till_done()
        assert len(events) == 1
        assert hass.states.get(entity_id).attributes["current_temperature"] == 26

        fetch.side_effect = EvoDeviceDataError("offline")
        await coordinator.async_refresh()
        await hass.async_block_till_done()
        assert len(events) == 2
        assert hass.states.get(entity_id).state == "unavailable"

        fetch.side_effect = None
        await coordinator.async_refresh()
        await hass.async_block_till_done()
        assert len(events) == 3
        assert hass.states.get(entity_id).attributes["current_temperature"] == 26

        unsubscribe()
        assert await hass.config_entries.async_unload(entry.entry_id)
        await hass.async_block_till_done()
        assert hass.states.get(entity_id).state == "unavailable"
        assert er.async_get(hass).async_get(entity_id).unique_id == channel_identity(entry, "Yellow")
