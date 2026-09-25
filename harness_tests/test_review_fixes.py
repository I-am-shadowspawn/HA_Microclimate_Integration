from tests.http_mocks import json_stream
from homeassistant.helpers.aiohttp_client import async_get_clientsession
"""Regression coverage for F01, F03 and F05 with no live device traffic."""
import logging
import traceback
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import aiohttp
import pytest
from homeassistant.exceptions import HomeAssistantError
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.microclimate_integration.api_client import fetch_data, EvoDeviceDataError
from custom_components.microclimate_integration.climate import MicroclimateClimate
from custom_components.microclimate_integration.const import CHANNELS

TOKEN = 'FAKE_PRIVATE_TOKEN_9381'


def response_context(payload, status=200):
    response = AsyncMock(status=status)
    response.json.return_value = payload
    context = AsyncMock()
    context.__aenter__.return_value = json_stream(response)
    return context


@pytest.mark.parametrize('payload', [None, [], 'oops', 42, True])
async def test_reject_response_shape(hass, payload):
    with patch('aiohttp.ClientSession.get', return_value=response_context(payload)):
        with pytest.raises(EvoDeviceDataError, match='JSON object'):
            await fetch_data(TOKEN, session=async_get_clientsession(hass))


async def test_normalize_structured_and_boolean_pins(hass):
    payload = {'v0': {}, 'v8': [], 'v52': True, 'v4': '50', 'v16': 'Yellow'}
    with patch('aiohttp.ClientSession.get', return_value=response_context(payload)):
        assert await fetch_data(TOKEN, session=async_get_clientsession(hass)) == {**payload, 'v0': None, 'v8': None, 'v52': None}


@pytest.mark.parametrize('status', [401, 500])
async def test_http_error_does_not_log_token(hass, status, caplog, capsys):
    from custom_components.microclimate_integration.api_client import UnauthenticatedError
    caplog.set_level(logging.DEBUG)
    with patch('aiohttp.ClientSession.get', return_value=response_context({'token': TOKEN}, status)):
        with pytest.raises((EvoDeviceDataError, UnauthenticatedError)) as caught:
            await fetch_data(TOKEN, session=async_get_clientsession(hass))
    captured = capsys.readouterr()
    assert TOKEN not in ''.join(traceback.format_exception(caught.value)) + caplog.text + captured.out + captured.err
