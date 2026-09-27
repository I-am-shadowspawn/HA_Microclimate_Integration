from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.components.frontend import DATA_EXTRA_MODULE_URL, UrlManager
from homeassistant.const import EVENT_COMPONENT_LOADED
from homeassistant.loader import async_get_integration
from homeassistant.util.unit_system import METRIC_SYSTEM
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.microclimate_integration.const import DOMAIN


@pytest.mark.parametrize("frontend_loaded", [False, True])
async def test_evo_connect_setup(hass, frontend_loaded):
    hass.config.units = METRIC_SYSTEM
    # Simulate both orders without installing the full frontend distribution.
    hass.data[DATA_EXTRA_MODULE_URL] = UrlManager(lambda _kind, _url: None, [])
    if frontend_loaded:
        hass.config.components.add("frontend")
    entry = MockConfigEntry(
        domain="microclimate_integration",
        version=1,
        title="Review controller",
        data={
            "evo_device": "review_controller",
            "token": "dummy_token_not_a_secret",
            "model": "Evo Connect",
        },
    )
    entry.add_to_hass(hass)
    # Synthetic wiring fixture, not evidence of vendor pin correctness.
    payload = {"v25": "C", "v0": "25°C", "v8": "27°C", "v16": "Yellow", "v52": "1", "v4": 50}
    with patch(
        "custom_components.microclimate_integration.api_client.fetch_data",
        new=AsyncMock(return_value=payload),
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        states = hass.states.async_all("climate")
        assert len(states) == 1
        assert states[0].attributes["current_temperature"] == 25.0
        assert states[0].attributes["observed_target_temperature"] == 27.0
        # Climate state values use HA's configured display units.
        assert hass.config.units.temperature_unit == "°C"
        if not frontend_loaded:
            hass.bus.async_fire(EVENT_COMPONENT_LOADED, {"component": "frontend"})
            await hass.async_block_till_done()
        modules = hass.data[DATA_EXTRA_MODULE_URL].urls
        version = (await async_get_integration(hass, DOMAIN)).version
        expected = f"/microclimate_integration/microclimate-cards.js?v={version}"
        assert expected in modules
        assert (
            len([url for url in modules if url.startswith(f"/{DOMAIN}/microclimate-cards.js")]) == 1
        )
        assert await hass.config_entries.async_unload(entry.entry_id)
        await hass.async_block_till_done()
        # The module belongs to the integration runtime, not this one controller entry.
        assert expected in hass.data[DATA_EXTRA_MODULE_URL].urls
