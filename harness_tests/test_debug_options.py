from tests.http_mocks import json_stream
"""Opt-in complete response logging, credential redaction and live options."""
import json
import logging
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.translation import async_get_translations
from pytest_homeassistant_custom_component.common import MockConfigEntry
from custom_components.microclimate_integration.api_client import fetch_data, get_evo_device_data
from custom_components.microclimate_integration.const import DOMAIN, CONF_LOG_RAW_RESPONSE

LOGGER='custom_components.microclimate_integration.api_client'
TOKEN='a"secret-token'
PAYLOAD={'v0':25,'v29':'Capture controller','v32':'3600\x003600\x00Europe/London\x000',
         'v999':'last pin','token':'OTHER_SECRET','nested':{'Authorization':'Bearer PRIVATE','message':TOKEN},
         'list':[TOKEN,{'api_key':'KEY_SECRET'}]}


def response(payload):
    context=AsyncMock();context.__aenter__.return_value=json_stream(AsyncMock(status=200,json=AsyncMock(return_value=payload)))
    return context


@pytest.mark.parametrize('enabled,level,expected',[(False,logging.DEBUG,False),(True,logging.INFO,False),(True,logging.DEBUG,True)])
async def test_payload_logging_gated_and_redacted(hass,caplog,enabled,level,expected):
    caplog.set_level(level,logger=LOGGER)
    with patch.object(async_get_clientsession(hass),'get',return_value=response(PAYLOAD)):
        result=await fetch_data(TOKEN,session=async_get_clientsession(hass),log_raw_response=enabled)
    records=[r for r in caplog.records if r.name==LOGGER and 'API response' in r.getMessage()]
    assert bool(records)==expected
    assert result['v999']=='last pin'
    if expected:
        logged=json.loads(records[0].getMessage().split(': ',1)[1])
        assert logged['v32']==PAYLOAD['v32'] and logged['v999']=='last pin'
        assert logged['nested']['message']=='[REDACTED]'
        assert logged['token']=='[REDACTED]'
        assert logged['nested']['Authorization']=='[REDACTED]'
        assert logged['list']==['[REDACTED]',{'api_key':'[REDACTED]'}]
        for secret in (TOKEN,'OTHER_SECRET','PRIVATE','KEY_SECRET'):
            assert secret not in records[0].getMessage()
    assert PAYLOAD['token']=='OTHER_SECRET'  # Redaction must not mutate the response.


async def test_options_change_next_request_and_preserve_other_options(hass,caplog):
    entry=MockConfigEntry(domain=DOMAIN,data={'evo_device':'test','token':TOKEN,'model':'Evo Connect'},options={'future_option':42})
    entry.add_to_hass(hass);caplog.set_level(logging.DEBUG,logger=LOGGER)
    with patch.object(async_get_clientsession(hass),'get',return_value=response(PAYLOAD)):
        await get_evo_device_data(hass,entry)
        assert not [r for r in caplog.records if r.name==LOGGER]
        form=await hass.config_entries.options.async_init(entry.entry_id)
        assert form['type']=='form'
        assert form['data_schema']({})=={CONF_LOG_RAW_RESPONSE:False, 'enable_writes':True}
        result=await hass.config_entries.options.async_configure(form['flow_id'],user_input={CONF_LOG_RAW_RESPONSE:True})
        assert result['type']=='create_entry'
        assert entry.options=={'future_option':42,CONF_LOG_RAW_RESPONSE:True,'enable_writes':True}
        await get_evo_device_data(hass,entry)
        assert len([r for r in caplog.records if r.name==LOGGER])==1
        form=await hass.config_entries.options.async_init(entry.entry_id)
        await hass.config_entries.options.async_configure(form['flow_id'],user_input={CONF_LOG_RAW_RESPONSE:False})
        caplog.clear()
        await get_evo_device_data(hass,entry)
        assert not [r for r in caplog.records if r.name==LOGGER]
    translations=await async_get_translations(hass,'en','options',{DOMAIN})
    assert translations[f'component.{DOMAIN}.options.step.init.data.{CONF_LOG_RAW_RESPONSE}']=='Log full API responses'


@pytest.mark.parametrize('status',[401,429,500])
async def test_error_response_logging_preserves_http_classification(hass,caplog,status):
    from custom_components.microclimate_integration.api_client import UnauthenticatedError, EvoDeviceDataError
    context=response(PAYLOAD);context.__aenter__.return_value.status=status
    caplog.set_level(logging.DEBUG,logger=LOGGER)
    with patch.object(async_get_clientsession(hass),'get',return_value=context):
        with pytest.raises(UnauthenticatedError if status==401 else EvoDeviceDataError):
            await fetch_data(TOKEN,session=async_get_clientsession(hass),log_raw_response=True)
    records=[r.getMessage() for r in caplog.records if r.name==LOGGER]
    assert len(records)==1 and 'last pin' in records[0]
    assert 'OTHER_SECRET' not in records[0]
    context.__aenter__.return_value.json.assert_awaited_once()


@pytest.mark.parametrize('status',[200,401])
async def test_invalid_json_logging_is_safe(hass,caplog,status):
    from custom_components.microclimate_integration.api_client import UnauthenticatedError, EvoDeviceDataError
    context=response(None);context.__aenter__.return_value.status=status
    context.__aenter__.return_value.json.side_effect=ValueError(TOKEN)
    caplog.set_level(logging.DEBUG,logger=LOGGER)
    with patch.object(async_get_clientsession(hass),'get',return_value=context):
        with pytest.raises(UnauthenticatedError if status==401 else EvoDeviceDataError):
            await fetch_data(TOKEN,session=async_get_clientsession(hass),log_raw_response=True)
    assert TOKEN not in caplog.text
    assert 'JSON body unavailable' in caplog.text
    context.__aenter__.return_value.json.assert_awaited_once()
