from tests.http_mocks import json_stream
"""RC-01 through RC-04: boundaries, dates, normalization and fresh identities."""
import logging
from unittest.mock import Mock, AsyncMock, patch

import pytest
from homeassistant.helpers import entity_registry as er, device_registry as dr
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.microclimate_integration.api_client import normalize_response
from custom_components.microclimate_integration.const import DOMAIN, CHANNELS
from custom_components.microclimate_integration.climate import MicroclimateClimate
from custom_components.microclimate_integration.sensor import MicroclimateMeasurement
from custom_components.microclimate_integration.sensor_contract import VERIFIED_MEASUREMENTS
from custom_components.microclimate_integration.schedule import schedule_observation, observe_date
from custom_components.microclimate_integration.identity import channel_identity, token_identity
PAYLOAD = {'v0':25, 'v8':27, 'v52':1, 'v4':0}


def response(payload):
    context = AsyncMock()
    context.__aenter__.return_value = json_stream(AsyncMock(status=200, json=AsyncMock(return_value=payload)))
    return context


@pytest.mark.parametrize('raw,expected',[(None,None),(-1,None),(0,0),(100,100),(101,None),('50.5',50.5),
    (float('nan'),None),(float('inf'),None),(-float('inf'),None),('nan',None),(True,None)])
@pytest.mark.parametrize('control,active',[(1,'heating'),(2,'cooling')])
async def test_consistent_output_boundaries(hass,raw,expected,control,active):
    entry=MockConfigEntry(domain=DOMAIN,data={'evo_device':'test','model':'Evo Connect','token':'fake'})
    coordinator=DataUpdateCoordinator(hass,logging.getLogger(__name__),name='test',config_entry=entry)
    coordinator.async_set_updated_data(normalize_response({'v52':control,'v4':raw}))
    climate=MicroclimateClimate(coordinator,'test','Evo Connect','Yellow',CHANNELS['Yellow'])
    definition=next(d for d in VERIFIED_MEASUREMENTS['Evo Connect'] if d.key=='output' and d.channel=='Yellow')
    sensor=MicroclimateMeasurement(coordinator,entry,definition)
    assert sensor.native_value==climate.extra_state_attributes['current_power']==expected
    assert climate.hvac_action==(None if expected is None else 'idle' if expected==0 else active)
    period=schedule_observation(normalize_response({'v52':0,'v33':raw}),'Yellow')['periods']['period_1']
    assert period.get('setpoint_percentage')==expected
    coordinator.async_set_updated_data({})
    assert climate.hvac_action is None and sensor.native_value is None


@pytest.mark.parametrize('raw,expected',[(None,None),(-1,None),(0,0),('120.5',120.5),(10000,10000),
    (float('nan'),None),(float('inf'),None),(-float('inf'),None),('inf',None),(True,None)])
async def test_consistent_ramp_boundaries(hass,raw,expected):
    entry=MockConfigEntry(domain=DOMAIN,data={'evo_device':'test','model':'Evo Connect','token':'fake'})
    coordinator=DataUpdateCoordinator(hass,logging.getLogger(__name__),name='test',config_entry=entry)
    coordinator.async_set_updated_data(normalize_response({'v48':raw}))
    climate=MicroclimateClimate(coordinator,'test','Evo Connect','Yellow',CHANNELS['Yellow'])
    definition=next(d for d in VERIFIED_MEASUREMENTS['Evo Connect'] if d.key=='ramp_time' and d.channel=='Yellow')
    sensor=MicroclimateMeasurement(coordinator,entry,definition)
    assert sensor.native_value==climate.extra_state_attributes['ramp_time']==expected
    assert schedule_observation(coordinator.data,'Yellow')['ramp_time']['minutes']==expected


@pytest.mark.parametrize('raw,status',[
    ('29/02/25','invalid_date'),('29/02/24','calendar_fields'),('29/02/00','reported_unparsed'),
    ('29/02','calendar_fields'),('29/02/1900','invalid_date'),('29/02/2000','calendar_fields'),
    ('28/02/00','calendar_fields'),('31/04/24','invalid_date'),('00/00','zero_date'),
    ('00/00/00','invalid_date'),('22/09/26','calendar_fields'),('29/02/0000','invalid_date')])
def test_short_year_and_recurring_dates(raw,status):
    result=observe_date(raw)
    assert result['interpretation']==status
    assert result['raw']==raw
    if len(raw.split('/')[-1])==2:
        assert 'year' not in result
    if raw=='29/02/00':assert result['reason']=='century_required'


@pytest.mark.parametrize('value',[float('nan'),float('inf'),-float('inf')])
def test_nonfinite_normalization(value):
    first=normalize_response({'v0':value,'v1':'nan','v2':'25°F','v3':0,'v4':True})
    second=normalize_response({'v0':float(str(value)),'v1':'nan','v2':'25°F','v3':0,'v4':True})
    assert first==second=={'v0':None,'v1':'nan','v2':'25°F','v3':0,'v4':None}


async def test_nonfinite_listener_suppression_and_recovery(hass):
    entry=MockConfigEntry(domain=DOMAIN,data={'evo_device':'test','token':'fake','model':'Evo Connect'})
    entry.add_to_hass(hass)
    with patch.object(async_get_clientsession(hass),'get',return_value=response({'v0':float('nan')})) as get:
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        coordinator=hass.data[DOMAIN][entry.entry_id]
        listener=Mock();remove=coordinator.async_add_listener(listener)
        get.return_value=response({'v0':float('nan')})
        await coordinator.async_refresh();await hass.async_block_till_done()
        listener.assert_not_called()
        get.side_effect=TimeoutError()
        await coordinator.async_refresh();await hass.async_block_till_done()
        assert listener.call_count==1 and not coordinator.last_update_success
        get.side_effect=None
        await coordinator.async_refresh();await hass.async_block_till_done()
        assert listener.call_count==2 and coordinator.last_update_success
        get.return_value=response({'v0':25})
        await coordinator.async_refresh();await hass.async_block_till_done()
        assert listener.call_count==3 and coordinator.data['v0']==25
        remove()
        assert await hass.config_entries.async_unload(entry.entry_id)
        await hass.async_block_till_done()


async def test_fresh_entry_rename_reconfigure_reauth_keep_identity(hass):
    registry=er.async_get(hass);devices=dr.async_get(hass)
    with patch.object(async_get_clientsession(hass),'get',return_value=response(PAYLOAD)) as get:
        created=await hass.config_entries.flow.async_init(DOMAIN,context={'source':'user'},
            data={'evo_device':'fresh','token':'first','model':'Evo Connect'})
        await hass.async_block_till_done()
        entry=created['result'];eid=entry.entry_id
        climate_id=registry.async_get_entity_id('climate',DOMAIN,channel_identity(entry,'Yellow'))
        record=registry.async_get(climate_id);device_id=record.device_id
        registry.async_update_entity(climate_id,name='Custom thermostat',icon='mdi:snake')
        devices.async_update_device(device_id,name_by_user='Vivarium')
        initial={e.unique_id:e.entity_id for e in er.async_entries_for_config_entry(registry,eid)}
        initial_devices={d.id for d in dr.async_entries_for_config_entry(devices,eid)}
        for source,values,token in [
            ('reconfigure',{'evo_device':'renamed','token':'first'},'first'),
            ('reconfigure',{'evo_device':'renamed','token':'replacement'},'replacement'),
            ('reauth',{'token':'reauthenticated'},'reauthenticated'),
        ]:
            flow=await hass.config_entries.flow.async_init(DOMAIN,context={'source':source,'entry_id':eid},
                data=entry.data if source=='reauth' else None)
            result=await hass.config_entries.flow.async_configure(flow['flow_id'],values)
            await hass.async_block_till_done()
            assert result['reason']==('reauth_successful' if source=='reauth' else 'reconfigure_successful')
            assert entry.entry_id==eid and entry.unique_id==token_identity(token)
            assert entry.data['evo_device']=='renamed'
            assert initial=={e.unique_id:e.entity_id for e in er.async_entries_for_config_entry(registry,eid)}
            assert initial_devices=={d.id for d in dr.async_entries_for_config_entry(devices,eid)}
            current=registry.async_get(climate_id)
            assert (current.device_id,current.name,current.icon)==(device_id,'Custom thermostat','mdi:snake')
            assert devices.async_get(device_id).name_by_user=='Vivarium'
            assert get.call_args.kwargs['params']['token']==token
        assert await hass.config_entries.async_unload(eid)
        await hass.async_block_till_done()
