from unittest.mock import AsyncMock, patch
from homeassistant.util.unit_system import METRIC_SYSTEM
from pytest_homeassistant_custom_component.common import MockConfigEntry

async def test_evo_connect_setup(hass):
    hass.config.units = METRIC_SYSTEM
    entry = MockConfigEntry(
        domain='microclimate_integration',
        version=1,
        title='Review controller',
        data={
            'evo_device': 'review_controller',
            'token': 'dummy_token_not_a_secret',
            'model': 'Evo Connect',
        },
    )
    entry.add_to_hass(hass)
    # Synthetic wiring fixture, not evidence of vendor pin correctness.
    payload = {'v0': '25°F', 'v8': '27°F', 'v16': 'Yellow',
               'v52': '1', 'v4': 50}
    with patch(
        'custom_components.microclimate_integration.api_client.fetch_data',
        new=AsyncMock(return_value=payload),
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        states = hass.states.async_all('climate')
        assert len(states) == 1
        assert states[0].attributes['current_temperature'] == 25.0
        assert states[0].attributes['observed_target_temperature'] == 27.0
        # Climate state values use HA's configured display units.
        assert hass.config.units.temperature_unit == '°C'
        assert await hass.config_entries.async_unload(entry.entry_id)
        await hass.async_block_till_done()
