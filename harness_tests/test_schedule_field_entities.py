"""Schedule fields remain in the card projection, without per-point entities."""
from unittest.mock import AsyncMock, patch
import pytest
from homeassistant.helpers import entity_registry as er, device_registry as dr
from pytest_homeassistant_custom_component.common import MockConfigEntry
from custom_components.microclimate_integration.const import DOMAIN
from custom_components.microclimate_integration.card_model import snapshot

@pytest.mark.parametrize('model,channels', [('Evo Connect',['Yellow','Blue']),('Evo Connect 2',['Yellow','Blue']),('Evo Connect 3',['Yellow','Red','Blue'])])
async def test_schedule_projection_modes_units_and_availability(hass,hass_admin_user,model,channels):
    entry=MockConfigEntry(domain=DOMAIN,data={'model':model,'evo_device':'fields','token':'fake'})
    entry.add_to_hass(hass);registry=er.async_get(hass)
    payload={'v20':'09/02','v21':'00/00'}
    maps={'Yellow':(32,'v53','v52',3),'Red':(62,'v83','v82',3),'Blue':(92,'v113','v112',4)}
    for channel in channels:
        first,timing,control,season=maps[channel]
        payload[timing]=season;payload[control]=0 if model=='Evo Connect' and channel=='Blue' else 1
        for i in range(8):
            payload[f'v{first+2*i}']=str(i*3600)
            payload[f'v{first+2*i+1}']=20+i
    def fields(channel):
        device=dr.async_get(hass).async_get_device_by_identifier((DOMAIN,f'{entry.entry_id}_{channel}'),entry.entry_id)
        return {f['key']:f for f in snapshot(hass,hass.data[DOMAIN][entry.entry_id],channel,device,hass_admin_user)['fields']}
    with patch('custom_components.microclimate_integration.api_client.fetch_data',new=AsyncMock(return_value=dict(payload))) as api:
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        for channel in channels:
            view=fields(channel)
            anchor=registry.async_get_entity_id('sensor',DOMAIN,f'{entry.entry_id}_{channel}_schedule')
            for index in range(1,9):
                start=view[f'{channel}_period_{index}_time'];target=view[f'{channel}_period_{index}_setpoint']
                assert start['value']==(index-1)*3600 and target['value']==19+index
                assert target['unit']==('%' if model=='Evo Connect' and channel=='Blue' else '°C')
                assert f"Season {(index+1)//2} {'day' if index%2 else 'night'}" in target['label']
                assert start['entity_id']==target['entity_id']==anchor and target['writable']
                assert registry.async_get_entity_id('number',DOMAIN,f'{entry.entry_id}_write_{channel}_period_{index}_setpoint') is None
        assert api.await_count==1
        season1=hass.states.get(registry.async_get_entity_id('sensor',DOMAIN,entry.entry_id+'_metadata_season_1_start'))
        season2=hass.states.get(registry.async_get_entity_id('sensor',DOMAIN,entry.entry_id+'_metadata_season_2_start'))
        assert season1.state=='09/02' and season2.state=='unknown'
        for channel in channels:
            first,timing,control,_=maps[channel]
            payload[timing]=2;payload[control]=0;payload[f'v{first+1}']=0
        api.return_value=dict(payload)
        await hass.data[DOMAIN][entry.entry_id].async_refresh();await hass.async_block_till_done()
        for channel in channels:
            target=fields(channel)[f'{channel}_period_1_setpoint']
            assert target['value']==0 and target['unit']=='%' and 'Point 1' in target['label']
        for channel in channels:payload[maps[channel][1]]=1
        api.return_value=dict(payload)
        await hass.data[DOMAIN][entry.entry_id].async_refresh();await hass.async_block_till_done()
        for channel in channels:
            view=fields(channel)
            assert view[f'{channel}_period_1_time']['label']=='Day start'
            assert view[f'{channel}_period_2_setpoint']['label']=='Night target'
            assert not view[f'{channel}_period_3_time']['writable']
        api.side_effect=TimeoutError()
        await hass.data[DOMAIN][entry.entry_id].async_refresh();await hass.async_block_till_done()
        assert not fields('Yellow')['Yellow_period_1_time']['writable']
        api.side_effect=None
        for channel in channels:payload[maps[channel][1]]=0
        api.return_value=dict(payload)
        await hass.data[DOMAIN][entry.entry_id].async_refresh();await hass.async_block_till_done()
        assert not fields('Yellow')['Yellow_period_1_time']['writable']
        assert await hass.config_entries.async_unload(entry.entry_id)
