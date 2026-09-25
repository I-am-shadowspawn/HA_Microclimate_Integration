from tests.http_mocks import json_stream
"""HTTP ownership, one normalization pass, derived-reading cache and polling."""
import asyncio
from datetime import timedelta
from unittest.mock import AsyncMock, Mock, patch
import traceback

import aiohttp
import pytest
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_fire_time_changed

from custom_components.microclimate_integration import api_client
from custom_components.microclimate_integration.const import DOMAIN, CHANNELS
from custom_components.microclimate_integration.config_flow import MicroclimateConfigFlow
from custom_components.microclimate_integration.readings import read_pin, DataSnapshot
from custom_components.microclimate_integration.validation import safe_temperature
from custom_components.microclimate_integration.climate import MicroclimateClimate
from custom_components.microclimate_integration.sensor import MicroclimateMeasurement, MicroclimateSchedule
from custom_components.microclimate_integration.sensor_contract import VERIFIED_MEASUREMENTS
from custom_components.microclimate_integration.schedule import _schedule_observation

PAYLOAD={'v0':'25°F','v8':27,'v52':1,'v4':0,'v32':'3600\x003600\x00Europe/London\x000','v33':20}


def response(payload=PAYLOAD,status=200):
    context=AsyncMock()
    context.__aenter__.return_value=json_stream(AsyncMock(status=status,json=AsyncMock(return_value=payload)))
    return context


@pytest.mark.parametrize('error,message',[
    (TimeoutError('SECRET_TOKEN'),'timed out'),
    (aiohttp.ClientConnectionError('SECRET_TOKEN'),'transport'),
    (ValueError('SECRET_TOKEN'),'JSON'),
    (RuntimeError('SECRET_TOKEN'),'Unable to fetch'),
])
async def test_classification_timeout_and_redaction(hass,error,message):
    session=async_get_clientsession(hass)
    token='SECRET_TOKEN'
    context=response();context.__aenter__.return_value.json.side_effect=error
    with patch.object(session,'get',return_value=context) as get:
        with pytest.raises(api_client.EvoDeviceDataError,match=message) as caught:
            await api_client.fetch_data(token,session=session)
    assert 'SECRET_TOKEN' not in ''.join(traceback.format_exception(caught.value))
    assert get.call_args.kwargs['timeout'] is api_client.REQUEST_TIMEOUT
    assert (api_client.REQUEST_TIMEOUT.total,api_client.REQUEST_TIMEOUT.connect,api_client.REQUEST_TIMEOUT.sock_read)==(20,10,15)
    assert not session.closed
    context.__aexit__.assert_awaited_once()


async def test_cancellation_propagates_without_closing_shared_session(hass):
    session=async_get_clientsession(hass)
    context=response();context.__aenter__.side_effect=asyncio.CancelledError()
    with patch.object(session,'get',return_value=context):
        with pytest.raises(asyncio.CancelledError):
            await api_client.fetch_data('fake',session=session)
    assert not session.closed


async def test_flow_normalizes_exactly_once(hass):
    session=async_get_clientsession(hass)
    flow=MicroclimateConfigFlow();flow.hass=hass
    with patch.object(session,'get',return_value=response()) as get, patch.object(api_client,'normalize_response',wraps=api_client.normalize_response) as normalize:
        assert await flow._validate_token('fake') is None
        assert get.call_count==normalize.call_count==1
    assert not session.closed


async def test_two_entries_share_session_not_state_and_poll_once(hass,freezer):
    session=async_get_clientsession(hass)
    entries=[MockConfigEntry(domain=DOMAIN,data={'evo_device':'same','model':model,'token':token})
             for model,token in [('Evo Connect','first'),('Evo Connect 3','second')]]
    for entry in entries:entry.add_to_hass(hass)
    def request(url,**kwargs):
        return response({**PAYLOAD,'v0':21 if kwargs['params']['token']=='first' else 28})
    with patch.object(session,'get',side_effect=request) as get, patch.object(api_client,'normalize_response',wraps=api_client.normalize_response) as normalize:
        assert await hass.config_entries.async_setup(entries[0].entry_id)
        await hass.async_block_till_done()
        coordinators=[hass.data[DOMAIN][entry.entry_id] for entry in entries]
        assert get.call_count==normalize.call_count==2
        assert coordinators[0] is not coordinators[1]
        assert [c.data['v0'] for c in coordinators]==[21,28]
        assert all(isinstance(c.data,DataSnapshot) for c in coordinators)
        freezer.tick(timedelta(seconds=61))
        async_fire_time_changed(hass,dt_util.utcnow())
        await hass.async_block_till_done()
        assert get.call_count==normalize.call_count==4  # One scheduled request per entry.
        assert await hass.config_entries.async_unload(entries[0].entry_id)
        await hass.async_block_till_done()
        assert not session.closed
        freezer.tick(timedelta(seconds=61))
        async_fire_time_changed(hass,dt_util.utcnow())
        await hass.async_block_till_done()
        assert get.call_count==normalize.call_count==5
        assert await hass.config_entries.async_unload(entries[1].entry_id)
        await hass.async_block_till_done()
        assert all(not c._listeners and c._unsub_refresh is None for c in coordinators)
        assert not session.closed


async def test_equal_data_suppressed_but_failure_recovery_not_suppressed(hass):
    entry=MockConfigEntry(domain=DOMAIN,data={'evo_device':'test','model':'Evo Connect','token':'fake'})
    entry.add_to_hass(hass);session=async_get_clientsession(hass)
    with patch.object(session,'get',return_value=response()) as get:
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        coordinator=hass.data[DOMAIN][entry.entry_id]
        listener=Mock();remove=coordinator.async_add_listener(listener)
        old=coordinator.data
        read_pin(old,'v0',safe_temperature)
        await coordinator.async_refresh();await hass.async_block_till_done()
        assert coordinator.data==old
        listener.assert_not_called()
        get.return_value=response({**PAYLOAD,'v0':26})
        await coordinator.async_refresh();await hass.async_block_till_done()
        assert listener.call_count==1
        assert read_pin(coordinator.data,'v0',safe_temperature)==26
        get.side_effect=TimeoutError('secret')
        await coordinator.async_refresh();await hass.async_block_till_done()
        assert listener.call_count==2 and not coordinator.last_update_success
        get.side_effect=None  # Return same 26-degree data as before failure.
        await coordinator.async_refresh();await hass.async_block_till_done()
        assert listener.call_count==3 and coordinator.last_update_success
        remove()
        assert await hass.config_entries.async_unload(entry.entry_id)
        await hass.async_block_till_done()


async def test_entities_share_transforms_and_schedule_cache(hass):
    entry=MockConfigEntry(domain=DOMAIN,data={'evo_device':'test','model':'Evo Connect','token':'fake'})
    entry.add_to_hass(hass)
    with patch.object(async_get_clientsession(hass),'get',return_value=response()):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        coordinator=hass.data[DOMAIN][entry.entry_id]
        coordinator.data=api_client.normalize_response(PAYLOAD)  # Fresh unread snapshot.
        climate=MicroclimateClimate(coordinator,'Yellow',CHANNELS['Yellow'])
        definition=next(d for d in VERIFIED_MEASUREMENTS['Evo Connect'] if d.key=='temperature' and d.channel=='Yellow')
        sensor=MicroclimateMeasurement(coordinator,entry,definition)
        schedule=MicroclimateSchedule(coordinator,entry,'Yellow')
        with patch('custom_components.microclimate_integration.validation.convert_temperature',wraps=__import__('custom_components.microclimate_integration.validation',fromlist=['convert_temperature']).convert_temperature) as convert:
            assert climate.current_temperature==sensor.native_value==climate.current_temperature==25
            assert convert.call_count==1
        with patch('custom_components.microclimate_integration.schedule._schedule_observation',wraps=_schedule_observation) as parse:
            assert schedule.native_value==1
            assert schedule.extra_state_attributes['reported_period_count']==1
            assert schedule.native_value==1
            assert parse.call_count==1
        another=api_client.normalize_response({**PAYLOAD,'v0':30})
        assert read_pin(another,'v0',safe_temperature)==30
        assert climate.current_temperature==25
        assert await hass.config_entries.async_unload(entry.entry_id)
        await hass.async_block_till_done()
