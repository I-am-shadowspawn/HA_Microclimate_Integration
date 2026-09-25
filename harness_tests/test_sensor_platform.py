"""F02 real sensor registration with an explicitly unverified pin contract."""
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.microclimate_integration.const import DOMAIN
from custom_components.microclimate_integration.identity import channel_identity


@pytest.mark.parametrize('model,channels', [('Evo Connect',{'Yellow','Blue'}),('Evo Connect 2',{'Yellow','Blue'}),('Evo Connect 3',{'Yellow','Red','Blue'})])
async def test_raw_candidates_default_enabled_and_shared_fetch(hass,model,channels):
    entry = MockConfigEntry(domain=DOMAIN,data={'evo_device':'test','token':'fake','model':model})
    entry.add_to_hass(hass)
    payload = {'v0':'25°F','v8':'27°F','v52':1,'v4':0,'token':'not-a-pin'}
    with patch('custom_components.microclimate_integration.api_client.fetch_data',new=AsyncMock(return_value=payload)) as api:
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        registry = er.async_get(hass)
        sensors = [e for e in er.async_entries_for_config_entry(registry,entry.entry_id) if e.domain=='sensor']
        raw = [e for e in sensors if '_raw_' in e.unique_id]
        assert raw
        assert {e.unique_id.removeprefix(entry.entry_id+'_').split('_raw_')[0] for e in raw} == channels
        assert all(e.disabled_by is None for e in raw)
        assert all(hass.states.get(e.entity_id) is not None for e in raw)
        count_id = registry.async_get_entity_id('sensor',DOMAIN,f'{entry.entry_id}_reported_pin_count')
        assert hass.states.get(count_id).state == '4'
        assert api.await_count == 1
        selected = next(e for e in raw if e.unique_id == f'{channel_identity(entry,"Yellow")}_raw_v0')
        climate_id = registry.async_get_entity_id('climate',DOMAIN,channel_identity(entry,'Yellow'))
        assert selected.device_id == registry.async_get(climate_id).device_id
        registry.async_update_entity(selected.entity_id,disabled_by=None,name='My probe observation')
        assert await hass.config_entries.async_reload(entry.entry_id)
        await hass.async_block_till_done()
        assert api.await_count == 2
        state = hass.states.get(selected.entity_id)
        assert state.state == '25°F'  # Raw observation; climate still interprets this as Celsius.
        assert state.attributes['interpretation'] == 'raw'
        assert 'unit_of_measurement' not in state.attributes
        assert 'device_class' not in state.attributes
        coordinator = hass.data[DOMAIN][entry.entry_id]
        api.return_value = {**payload,'v0':'26°F'}
        await coordinator.async_refresh()
        await hass.async_block_till_done()
        assert api.await_count == 3
        assert hass.states.get(selected.entity_id).state == '26°F'
        assert hass.states.get(climate_id).attributes['current_temperature'] == 26
        api.side_effect = TimeoutError()
        await coordinator.async_refresh()
        await hass.async_block_till_done()
        assert hass.states.get(selected.entity_id).state == 'unavailable'
        assert hass.states.get(climate_id).state == 'unavailable'
        api.side_effect = None
        api.return_value = {}
        await coordinator.async_refresh()
        await hass.async_block_till_done()
        assert hass.states.get(selected.entity_id).state == 'unknown'
        assert hass.states.get(count_id).state == '0'
        hass.config_entries.async_update_entry(entry,data={**entry.data,'evo_device':'renamed','token':'replaced'})
        assert await hass.config_entries.async_reload(entry.entry_id)
        await hass.async_block_till_done()
        assert registry.async_get_entity_id('sensor',DOMAIN,selected.unique_id) == selected.entity_id
        assert registry.async_get(selected.entity_id).name == 'My probe observation'
        assert registry.async_get(selected.entity_id).disabled_by is None
        latest = hass.data[DOMAIN][entry.entry_id]
        assert await hass.config_entries.async_unload(entry.entry_id)
        await hass.async_block_till_done()
        assert not latest._listeners
        assert latest._unsub_refresh is None


@pytest.mark.parametrize('value', [None,True,{},[],float('nan'),float('inf'),'encoded\x00schedule','x'*256])
async def test_raw_sensor_invalid_values_unknown(hass,value):
    from custom_components.microclimate_integration.sensor import MicroclimateRawPin
    from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
    import logging
    entry = MockConfigEntry(domain=DOMAIN,data={'evo_device':'test','token':'fake','model':'Evo Connect'})
    coordinator = DataUpdateCoordinator(hass,logging.getLogger(__name__),name='test',config_entry=entry)
    coordinator.async_set_updated_data({'v0':value})
    sensor = MicroclimateRawPin(coordinator,entry,'Yellow','v0')
    assert sensor.native_value is None
