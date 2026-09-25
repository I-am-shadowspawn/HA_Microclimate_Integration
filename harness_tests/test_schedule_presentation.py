"""Manual schedule presentation and recorder metadata, without extra polling."""
from unittest.mock import AsyncMock, patch
import json
import pytest
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry
from custom_components.microclimate_integration.const import DOMAIN
from custom_components.microclimate_integration.schedule import schedule_observation, observe_time
from custom_components.microclimate_integration.transformation import convert_time


@pytest.mark.parametrize('token',['sr','ss'])
def test_solar_tokens_are_unsupported_raw_input(token):
    raw=token+'\x000\x00Europe/London\x000'
    observed=observe_time(raw)
    assert observed['status']=='unsupported'
    assert observed['raw']==raw
    assert 'event' not in observed and 'time' not in observed
    with pytest.raises(ValueError):convert_time(raw)


@pytest.mark.parametrize('code,label',[(0,'Constant'),(1,'Day & Night'),(2,'Multi'),(3,'Seasonal'),(99,'Unknown')])
def test_readable_bounded_summary(code,label):
    data={'v53':code,'v52':1,'v20':'09/02','v21':'00/00'}
    for i in range(8):
        data[f'v{32+2*i}']=str(i*3600)
        data[f'v{33+2*i}']=20+i
    observed=schedule_observation(data,'Yellow')
    assert observed['summary'].startswith(label)
    assert len(observed['summary'])<=255
    if code==1:assert 'day 00:00:00 = 20 C; night 01:00:00 = 21 C' in observed['summary']


async def test_live_detail_recorder_exclusions_and_same_entity(hass):
    entry=MockConfigEntry(domain=DOMAIN,data={'evo_device':'presentation','model':'Evo Connect 2','token':'fake'})
    entry.add_to_hass(hass)
    payload={'v53':3,'v52':1,'v20':'09/02','v21':'00/00','v113':0,'v112':1}
    for i in range(8):
        payload[f'v{32+2*i}']=f'{i*3600}\x00{i*3600}\x00Europe/London\x000'
        payload[f'v{33+2*i}']=20+i
    registry=er.async_get(hass)
    with patch('custom_components.microclimate_integration.api_client.fetch_data',new=AsyncMock(return_value=payload)) as api:
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        entity_id=registry.async_get_entity_id('sensor',DOMAIN,entry.entry_id+'_Yellow_schedule')
        state=hass.states.get(entity_id)
        assert state.state=='8'
        assert 'seasons' in state.attributes and 'periods' in state.attributes
        assert state.attributes['summary'].startswith('Seasonal:')
        exclusions=state.state_info['unrecorded_attributes']
        assert {'seasons','periods','daily_points','day_night'}<=exclusions
        assert 'summary' not in exclusions and 'timing_type' not in exclusions
        recorded={k:v for k,v in state.attributes.items() if k not in exclusions}
        assert len(json.dumps(recorded)) < len(json.dumps(dict(state.attributes)))/2
        assert api.await_count==1
        api.return_value={**payload,'v53':1}
        await hass.data[DOMAIN][entry.entry_id].async_refresh()
        await hass.async_block_till_done()
        state=hass.states.get(entity_id)
        assert 'day_night' in state.attributes and 'seasons' not in state.attributes
        assert state.attributes['summary'].startswith('Day & Night:')
        assert api.await_count==2
        assert await hass.config_entries.async_unload(entry.entry_id)
        await hass.async_block_till_done()
