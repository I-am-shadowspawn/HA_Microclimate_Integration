from tests.http_mocks import json_stream
from homeassistant.helpers.aiohttp_client import async_get_clientsession
"""F09 tests at the HTTP boundary and through real HA config flows."""
import logging
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.microclimate_integration.api_client import fetch_data, UnauthenticatedError, EvoDeviceDataError
from custom_components.microclimate_integration.const import DOMAIN
from custom_components.microclimate_integration.identity import token_identity

PAYLOAD = {'v0':'25°F','v8':'27°F','v52':1,'v4':0}


def http_response(status, payload):
    response = AsyncMock(status=status)
    response.json.return_value = payload
    context = AsyncMock()
    context.__aenter__.return_value = json_stream(response)
    return context


@pytest.mark.parametrize('status,payload,error', [
    (401,None,UnauthenticatedError),
    (400,{'error':{'message':'Invalid token.'}},UnauthenticatedError),
    (200,{'error':{'message':'Invalid token.'}},UnauthenticatedError),
    (400,{'error':{'message':'Wrong pin format.'}},EvoDeviceDataError),
    (403,{'error':{'message':'Invalid token.'}},EvoDeviceDataError),
    (429,{},EvoDeviceDataError),
    (500,{'error':{'message':'Invalid token.'}},EvoDeviceDataError),
    (200,{'error':{'message':'Unexpected service error'}},EvoDeviceDataError),
    (200,[],EvoDeviceDataError),
])
async def test_http_auth_classification(hass, status,payload,error,caplog,capsys):
    caplog.set_level(logging.DEBUG)
    with patch('aiohttp.ClientSession.get',return_value=http_response(status,payload)):
        with pytest.raises(error):
            await fetch_data('FAKE_F09_PRIVATE_TOKEN', session=async_get_clientsession(hass))
    captured = capsys.readouterr()
    assert 'FAKE_F09_PRIVATE_TOKEN' not in caplog.text + captured.out + captured.err


@pytest.mark.parametrize('status,payload,expected', [
    (400,{'error':{'message':'Invalid token.'}},'invalid_auth'),
    (401,None,'invalid_auth'),
    (500,{},'cannot_connect'),
    (200,[],'cannot_connect'),
    (200,{'error':'unknown failure'},'cannot_connect'),
])
async def test_onboarding_validates_and_allows_retry(hass,status,payload,expected):
    with patch('aiohttp.ClientSession.get',return_value=http_response(status,payload)) as http:
        result = await hass.config_entries.flow.async_init(DOMAIN,context={'source':'user'},data={'evo_device':'test','token':'bad','model':'Evo Connect'})
        assert result['type'] == 'form'
        assert result['errors'] == {'base':expected}
        assert not hass.config_entries.async_entries(DOMAIN)
        http.return_value = http_response(200,PAYLOAD)
        result = await hass.config_entries.flow.async_configure(result['flow_id'],{'evo_device':'test','token':'good','model':'Evo Connect'})
        await hass.async_block_till_done()
        assert result['type'] == 'create_entry'
        entry = result['result']
        assert entry.unique_id == token_identity('good')
        assert entry.state == ConfigEntryState.LOADED
        assert await hass.config_entries.async_unload(entry.entry_id)
        await hass.async_block_till_done()


async def test_transport_timeout_keeps_onboarding_form(hass):
    context = AsyncMock()
    context.__aenter__.side_effect = TimeoutError('https://example.test/?token=FAKE_SECRET')
    with patch('aiohttp.ClientSession.get',return_value=context):
        result = await hass.config_entries.flow.async_init(DOMAIN,context={'source':'user'},data={'evo_device':'test','token':'FAKE_SECRET','model':'Evo Connect'})
    assert result['errors'] == {'base':'cannot_connect'}
    assert not hass.config_entries.async_entries(DOMAIN)


@pytest.mark.parametrize('initial_failure',[False,True])
async def test_reauth_validates_then_reloads_same_entry(hass,initial_failure,caplog):
    entry = MockConfigEntry(domain=DOMAIN,unique_id=token_identity('old'),data={'evo_device':'controller','token':'old','model':'Evo Connect'})
    entry.add_to_hass(hass)
    with patch('aiohttp.ClientSession.get',return_value=http_response(200,PAYLOAD)) as http:
        if initial_failure:
            http.return_value = http_response(401,{})
            assert not await hass.config_entries.async_setup(entry.entry_id)
        else:
            assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        registry = er.async_get(hass)
        existing = er.async_entries_for_config_entry(registry,entry.entry_id)
        before = {e.entity_id:(e.unique_id,e.device_id,e.disabled_by) for e in existing}
        if existing:
            registry.async_update_entity(existing[0].entity_id,name='Keep my custom name')
            http.return_value = http_response(400,{'error':{'message':'Invalid token.'}})
            await hass.data[DOMAIN][entry.entry_id].async_refresh()
            await hass.async_block_till_done()
            assert all(state.state == 'unavailable' for state in hass.states.async_all() if state.entity_id in before)
        progress = [flow for flow in hass.config_entries.flow.async_progress() if flow['context']['source']=='reauth']
        assert len(progress) == 1
        flow_id = progress[0]['flow_id']
        original = dict(entry.data)
        for response,expected in [(http_response(401,{}),'invalid_auth'),(http_response(500,{}),'cannot_connect')]:
            http.return_value = response
            result = await hass.config_entries.flow.async_configure(flow_id,{'token':'FAKE_REJECTED_CREDENTIAL'})
            assert result['type'] == 'form'
            assert result['errors'] == {'base':expected}
            assert dict(entry.data) == original
            assert entry.unique_id == token_identity('old')
        http.return_value = http_response(200,PAYLOAD)
        result = await hass.config_entries.flow.async_configure(flow_id,{'token':'new'})
        assert result['reason'] == 'reauth_successful'
        await hass.async_block_till_done()
        assert entry.state == ConfigEntryState.LOADED
        assert entry.unique_id == token_identity('new')
        assert entry.data['token'] == 'new'
        assert len(hass.config_entries.async_entries(DOMAIN)) == 1
        assert http.call_args.kwargs['params'] == {'token':'new'}
        after = {e.entity_id:(e.unique_id,e.device_id,e.disabled_by) for e in er.async_entries_for_config_entry(registry,entry.entry_id)}
        if before:
            assert after == before
            assert registry.async_get(existing[0].entity_id).name == 'Keep my custom name'
        assert not [flow for flow in hass.config_entries.flow.async_progress() if flow['context']['source']=='reauth']
        assert 'FAKE_REJECTED_CREDENTIAL' not in caplog.text
        assert await hass.config_entries.async_unload(entry.entry_id)
        await hass.async_block_till_done()


async def test_reauth_rejects_another_entries_token(hass):
    first=MockConfigEntry(domain=DOMAIN,data={'evo_device':'same','token':'first','model':'Evo Connect'})
    second=MockConfigEntry(domain=DOMAIN,data={'evo_device':'same','token':'second','model':'Evo Connect'})
    first.add_to_hass(hass);second.add_to_hass(hass)
    result=await hass.config_entries.flow.async_init(DOMAIN,context={'source':'reauth','entry_id':first.entry_id},data=first.data)
    with patch('aiohttp.ClientSession.get') as http:
        result=await hass.config_entries.flow.async_configure(result['flow_id'],{'token':'second'})
        http.assert_not_called()
    assert result['errors']=={'base':'already_configured'}
    assert first.data['token']=='first'


async def test_reconfigure_does_not_save_unvalidated_name_or_token(hass):
    entry = MockConfigEntry(domain=DOMAIN,unique_id=token_identity('old'),data={'evo_device':'original','token':'old','model':'Evo Connect'})
    entry.add_to_hass(hass)
    result = await hass.config_entries.flow.async_init(DOMAIN,context={'source':'reconfigure','entry_id':entry.entry_id})
    with patch('aiohttp.ClientSession.get',return_value=http_response(401,{})):
        result = await hass.config_entries.flow.async_configure(result['flow_id'],{'evo_device':'changed','token':'invalid'})
    assert result['errors'] == {'base':'invalid_auth'}
    assert entry.data == {'evo_device':'original','token':'old','model':'Evo Connect'}
    assert entry.unique_id == token_identity('old')


async def test_server_outage_does_not_start_reauth(hass):
    entry=MockConfigEntry(domain=DOMAIN,data={'evo_device':'test','token':'valid','model':'Evo Connect'})
    entry.add_to_hass(hass)
    with patch('aiohttp.ClientSession.get',return_value=http_response(200,PAYLOAD)) as http:
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        coordinator=hass.data[DOMAIN][entry.entry_id]
        http.return_value=http_response(503,{})
        await coordinator.async_refresh()
        await hass.async_block_till_done()
        assert not coordinator.last_update_success
        assert not hass.config_entries.flow.async_progress()
        assert entry.data['token']=='valid'
        http.return_value=http_response(200,PAYLOAD)
        await coordinator.async_refresh()
        await hass.async_block_till_done()
        assert coordinator.last_update_success
        assert await hass.config_entries.async_unload(entry.entry_id)
        await hass.async_block_till_done()
