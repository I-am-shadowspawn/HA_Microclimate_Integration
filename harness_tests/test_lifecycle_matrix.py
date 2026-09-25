"""Real HA lifecycle, exercising current models without assuming pin validity."""
import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.data_entry_flow import UnknownStep
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.microclimate_integration.api_client import UnauthenticatedError
from custom_components.microclimate_integration.const import DOMAIN


@pytest.fixture
def synthetic_payload():
    return json.loads((Path(__file__).parents[1] / 'fixtures/synthetic_get_all.json').read_text())['payload']


@pytest.fixture
def model_entry(hass, request):
    entry = MockConfigEntry(domain=DOMAIN, data={
        'evo_device': 'lifecycle', 'token': 'fake-lifecycle-token',
        'model': getattr(request, 'param', 'Evo Connect')})
    entry.add_to_hass(hass)
    return entry


@pytest.mark.parametrize('model_entry,expected', [('Evo Connect',1),('Evo Connect 2',2),('Evo Connect 3',3)], indirect=['model_entry'])
async def test_models_refresh_reload_and_unload(hass, model_entry, expected, synthetic_payload):
    with patch('custom_components.microclimate_integration.api_client.fetch_data',new=AsyncMock(return_value=synthetic_payload)) as api:
        assert await hass.config_entries.async_setup(model_entry.entry_id)
        await hass.async_block_till_done()
        states = hass.states.async_all('climate')
        assert len(states) == expected
        assert sorted(s.attributes['current_temperature'] for s in states) == sorted({1:[25],2:[25,23],3:[25,24,23]}[expected])
        assert api.await_count == 1  # Shared entry coordinator, regardless of entity count.
        registry = er.async_get(hass)
        original_ids = {e.entity_id for e in er.async_entries_for_config_entry(registry,model_entry.entry_id)}
        coordinator = hass.data[DOMAIN][model_entry.entry_id]
        api.return_value = {**synthetic_payload,'v0':'26°F'}
        await coordinator.async_refresh()
        await hass.async_block_till_done()
        assert api.await_count == 2
        assert 26 in [s.attributes['current_temperature'] for s in hass.states.async_all('climate')]
        assert await hass.config_entries.async_reload(model_entry.entry_id)
        await hass.async_block_till_done()
        assert api.await_count == 3
        assert {e.entity_id for e in er.async_entries_for_config_entry(registry,model_entry.entry_id)} == original_ids
        assert len(hass.states.async_all('climate')) == expected
        reloaded_coordinator = hass.data[DOMAIN][model_entry.entry_id]
        assert await hass.config_entries.async_unload(model_entry.entry_id)
        await hass.async_block_till_done()
        assert model_entry.entry_id not in hass.data[DOMAIN]
        assert all(hass.states.get(eid) is None or hass.states.get(eid).state == 'unavailable' for eid in original_ids)
        assert not coordinator._listeners
        assert coordinator._unsub_refresh is None
        assert not reloaded_coordinator._listeners
        assert reloaded_coordinator._unsub_refresh is None


async def test_transient_first_refresh_recovers_on_reload(hass,model_entry,synthetic_payload):
    with patch('custom_components.microclimate_integration.api_client.fetch_data',new=AsyncMock(side_effect=TimeoutError('simulated timeout'))) as api:
        assert not await hass.config_entries.async_setup(model_entry.entry_id)
        assert model_entry.state == ConfigEntryState.SETUP_RETRY
        assert model_entry.entry_id not in hass.data.get(DOMAIN,{})
        api.side_effect = None
        api.return_value = synthetic_payload
        assert await hass.config_entries.async_reload(model_entry.entry_id)
        await hass.async_block_till_done()
        assert model_entry.state == ConfigEntryState.LOADED
        assert await hass.config_entries.async_unload(model_entry.entry_id)
        await hass.async_block_till_done()


async def test_sensor_entities_registered_by_real_setup(hass,model_entry,synthetic_payload):
    with patch('custom_components.microclimate_integration.api_client.fetch_data',new=AsyncMock(return_value=synthetic_payload)):
        assert await hass.config_entries.async_setup(model_entry.entry_id)
        await hass.async_block_till_done()
        sensors = hass.states.async_all('sensor')
        assert await hass.config_entries.async_unload(model_entry.entry_id)
        await hass.async_block_till_done()
        assert len(sensors) == 26  # 20 registered raw-pin diagnostics are disabled.
        count_id = er.async_get(hass).async_get_entity_id('sensor',DOMAIN,f'{model_entry.entry_id}_reported_pin_count')
        assert next(s for s in sensors if s.entity_id==count_id).state == str(len(synthetic_payload))


async def test_sensor_platform_loads_through_ha(hass,model_entry,synthetic_payload,caplog):
    with patch('custom_components.microclimate_integration.api_client.fetch_data',new=AsyncMock(return_value=synthetic_payload)):
        assert await hass.config_entries.async_setup(model_entry.entry_id)
        assert await hass.config_entries.async_reload(model_entry.entry_id)
        await hass.async_block_till_done()
        sensors = hass.states.async_all('sensor')
        assert await hass.config_entries.async_unload(model_entry.entry_id)
        await hass.async_block_till_done()
        assert len(sensors) == 26  # Reload preserves the raw-pin default.
        count_id = er.async_get(hass).async_get_entity_id('sensor',DOMAIN,f'{model_entry.entry_id}_reported_pin_count')
        assert next(s for s in sensors if s.entity_id==count_id).state == str(len(synthetic_payload))


async def test_initial_auth_failure_requests_reauth(hass,model_entry):
    with patch('custom_components.microclimate_integration.api_client.fetch_data',new=AsyncMock(side_effect=UnauthenticatedError('invalid credential'))):
        assert not await hass.config_entries.async_setup(model_entry.entry_id)
        await hass.async_block_till_done()
        assert model_entry.state == ConfigEntryState.SETUP_ERROR
        assert any(flow['context']['source'] == 'reauth' for flow in hass.config_entries.flow.async_progress())


async def test_reauth_flow_can_start(hass,model_entry):
    result = await hass.config_entries.flow.async_init(DOMAIN,context={'source':'reauth','entry_id':model_entry.entry_id},data=model_entry.data)
    assert result['type'] == 'form'
