"""F06/F07 activity, isolation, onboarding, and current-entry identity."""
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant import config_entries
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er, device_registry as dr
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.microclimate_integration.climate import MicroclimateClimate
from custom_components.microclimate_integration.const import CHANNELS, DOMAIN
from custom_components.microclimate_integration.identity import channel_identity, token_identity


@pytest.mark.parametrize('control,mode,active', [(1,'heat','heating'),('1','heat','heating'),(2,'cool','cooling'),('2','cool','cooling')])
@pytest.mark.parametrize('power,activity', [(0,'idle'),('0','idle'),(50,'active'),('50','active'),(None,None),('bad',None),(-1,None)])
def test_mode_independent_of_activity(control, mode, active, power, activity):
    entity = MicroclimateClimate(SimpleNamespace(config_entry=SimpleNamespace(entry_id="test-entry", data={"evo_device":"test","model":"Evo Connect"}), hass=None, data={'v52':control,'v4':power}), 'Yellow',CHANNELS['Yellow'])
    assert entity.hvac_mode == mode
    assert entity.hvac_action == (active if activity == 'active' else activity)
    assert entity.hvac_modes == []  # Observational, including cooling.
    assert entity.supported_features == 0


@pytest.mark.parametrize('control', [0,'0',None,'bad',True])
def test_fixed_or_invalid_not_temperature(control):
    entity = MicroclimateClimate(SimpleNamespace(config_entry=SimpleNamespace(entry_id="test-entry", data={"evo_device":"test","model":"Evo Connect"}), hass=None, data={'v52':control,'v8':1,'v4':50}), 'Yellow',CHANNELS['Yellow'])
    assert entity.hvac_mode is None
    assert entity.hvac_action is None
    assert entity.target_temperature is None


async def test_climate_name_tracks_entry_and_channel_without_changing_identity():
    entry = SimpleNamespace(entry_id="test-entry", data={"evo_device": "before", "model": "Evo Connect"})
    coordinator = SimpleNamespace(config_entry=entry, hass=None, data={"v16": "Yellow"})
    entity = MicroclimateClimate(coordinator, "Yellow", CHANNELS["Yellow"])
    assert entity.name == "before: Yellow"
    unique_id = entity.unique_id
    device_info = entity.device_info
    entry.data["evo_device"] = "after"
    coordinator.data = {"v16": "Warm side"}
    assert entity.name == "after: Warm side"
    assert entity.unique_id == unique_id
    assert entity.device_info["identifiers"] == device_info["identifiers"]

    for method, args in (
        (entity.async_set_temperature, {"temperature": 25}),
        (entity.async_set_hvac_mode, {"hvac_mode": "heat"}),
        (entity.async_turn_on, {}),
        (entity.async_turn_off, {}),
    ):
        with pytest.raises(HomeAssistantError, match="climate entity is read-only"):
            await method(**args)


def entry(token='token-a', name='same'):
    return MockConfigEntry(domain=DOMAIN, data={'evo_device':name, 'token':token,'model':'Evo Connect'})


async def test_same_name_entries_are_isolated(hass):
    first, second = entry(), entry('token-b')
    first.add_to_hass(hass)
    second.add_to_hass(hass)
    async def fetch(token, *, session, log_raw_response=False):
        return {'v0': 21 if token == 'token-a' else 28,'v52':1,'v4':0}
    with patch('custom_components.microclimate_integration.api_client.fetch_data',side_effect=fetch) as api:
        assert await hass.config_entries.async_setup(first.entry_id)
        await hass.async_block_till_done()
        assert first.state == second.state == config_entries.ConfigEntryState.LOADED
        registry = er.async_get(hass)
        ids = [registry.async_get_entity_id('climate', DOMAIN, channel_identity(item,'Yellow')) for item in (first,second)]
        assert ids[0] != ids[1]
        assert [hass.states.get(e).attributes['current_temperature'] for e in ids] == [21,28]
        assert [hass.states.get(e).attributes['hvac_action'] for e in ids] == ['idle','idle']
        assert {call.args[0] for call in api.await_args_list} == {'token-a','token-b'}
        for item in (first,second):
            assert await hass.config_entries.async_unload(item.entry_id)
        await hass.async_block_till_done()


async def test_duplicate_token_in_existing_entry_rejected(hass):
    existing = entry()
    existing.add_to_hass(hass)
    result = await hass.config_entries.flow.async_init(DOMAIN,context={'source':'user'},data={'evo_device':'different name','token':'token-a','model':'Evo Connect'})
    assert result['type'] == 'abort'
    assert result['reason'] == 'already_configured'


async def test_new_flow_uses_token_digest(hass):
    with patch('custom_components.microclimate_integration.async_setup_entry', return_value=True), patch('custom_components.microclimate_integration.api_client.fetch_data', new=AsyncMock(return_value={})):
        result = await hass.config_entries.flow.async_init(DOMAIN,context={'source':'user'},data={'evo_device':'same','token':'new-token','model':'Evo Connect'})
        await hass.async_block_till_done()
    assert result['type'] == 'create_entry'
    assert result['result'].unique_id == token_identity('new-token')
    assert 'new-token' not in result['result'].unique_id






async def test_reconfigure_duplicate_rejected(hass):
    first, second = entry(),entry('token-b')
    first.add_to_hass(hass)
    second.add_to_hass(hass)
    flow = await hass.config_entries.flow.async_init(DOMAIN,context={'source':'reconfigure','entry_id':first.entry_id})
    result = await hass.config_entries.flow.async_configure(flow['flow_id'],{'evo_device':'renamed','token':'token-b'})
    assert result['errors'] == {'base':'already_configured'}
    assert first.data['token'] == 'token-a'


