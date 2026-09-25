from tests.http_mocks import json_stream
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import aiohttp
import pytest
from unittest.mock import AsyncMock, patch
from custom_components.microclimate_integration.api_client import (
    get_evo_device_data,
    fetch_data,
    UnauthenticatedError,
    EvoDeviceDataError,
    DOMAIN)

from homeassistant.exceptions import ConfigEntryAuthFailed

@pytest.mark.asyncio
async def test_fetch_data_success(hass):
    token = "valid_token"

    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={"key": "value"})

    # Create a fake async context manager for the get() method
    fake_context_manager = AsyncMock()
    fake_context_manager.__aenter__.return_value = json_stream(mock_response)

    with patch("aiohttp.ClientSession.get", return_value=fake_context_manager):
        result = await fetch_data(token, session=async_get_clientsession(hass))

    assert result == {"key": "value"}


@pytest.mark.asyncio
async def test_fetch_data_invalid_token(hass, mocker):
    token = "invalid_token"

    mock_response = AsyncMock()
    mock_response.status = 401
    mock_response.json = AsyncMock(return_value={"key": "value"})

    # Create a fake async context manager for the get() method
    fake_context_manager = AsyncMock()
    fake_context_manager.__aenter__.return_value = json_stream(mock_response)

    with patch("aiohttp.ClientSession.get", return_value=fake_context_manager):
    #     result = await fetch_data(token, session=async_get_clientsession(hass))
    #
    # assert result is None


        with pytest.raises(UnauthenticatedError) as excinfo:
            await fetch_data(token, session=async_get_clientsession(hass))
        assert "Authentication failed" in str(excinfo.value)



@pytest.mark.asyncio
async def test_fetch_data_server_error(hass, mocker):
    token = "valid_token"

    mock_response = AsyncMock()
    mock_response.status = 500
    mock_response.json = AsyncMock(return_value={"key": "value"})

    # Create a fake async context manager for the get() method
    fake_context_manager = AsyncMock()
    fake_context_manager.__aenter__.return_value = json_stream(mock_response)

    with patch("aiohttp.ClientSession.get", return_value=fake_context_manager):
        with pytest.raises(Exception) as excinfo:
            await fetch_data(token, session=async_get_clientsession(hass))
        assert "Unexpected response status" in str(excinfo.value)


@pytest.mark.asyncio
async def test_fetch_data_network_error(hass):
    token = "valid_token"

    # Create a fake async context manager for the get() method
    fake_context_manager = AsyncMock()
    # Simulate a network error by raising an exception when entering the context
    fake_context_manager.__aenter__.side_effect = aiohttp.ClientError("Network error")

    with patch("aiohttp.ClientSession.get", return_value=fake_context_manager):
        with pytest.raises(EvoDeviceDataError):
            await fetch_data(token, session=async_get_clientsession(hass))




# Create a simple fake config entry class to simulate Home Assistant's config entries.
class FakeConfigEntry:
    def __init__(self, data):
        self.data = data

# Create a fake config entries container with an async_entries method.
class FakeConfigEntries:
    def __init__(self, entries):
        self._entries = entries

    def async_entries(self, domain):
        # Here we assume all entries belong to the same domain.
        return self._entries

# Create a fake hass object with a config_entries attribute.
class FakeHass:
    def __init__(self, entries):
        self.config_entries = FakeConfigEntries(entries)

@pytest.mark.asyncio
async def test_get_evo_device_data_entry_not_found(hass):
    # No configuration entries are provided.
    fake_hass = FakeHass(entries=[])
    evo_device = "device123"

    # Expect a ValueError when the config entry for the evo_device is not found.
    with pytest.raises(ValueError, match="Configuration entry is required"):
        await get_evo_device_data(fake_hass, None)

@pytest.mark.asyncio
async def test_get_evo_device_data_success(hass):
    evo_device = "device123"
    token = "valid_token"
    expected_data = {"key": "value"}

    # Create a fake configuration entry with the correct evo_device and token.
    config_entry = FakeConfigEntry(data={"evo_device": evo_device, "token": token})
    fake_hass = hass

    # Patch fetch_data so that it returns the expected_data when called.
    with patch("custom_components.microclimate_integration.api_client.fetch_data", new=AsyncMock(return_value=expected_data)):
        result = await get_evo_device_data(fake_hass, config_entry)

    # Verify that get_evo_device_data returns the value from fetch_data.
    assert result == expected_data

@pytest.mark.asyncio
async def test_get_evo_device_data_auth_error(hass):
    evo_device = "device123"
    token = "invalid_token"
    # Create a fake configuration entry with the given evo_device and token.
    config_entry = FakeConfigEntry(data={"evo_device": evo_device, "token": token})
    fake_hass = hass

    # Patch fetch_data to simulate an authentication error by raising UnauthenticatedError.
    with patch(
            "custom_components.microclimate_integration.api_client.fetch_data",
            new=AsyncMock(side_effect=UnauthenticatedError("Authentication failed: invalid token"))
    ):
        with pytest.raises(ConfigEntryAuthFailed) as excinfo:
            await get_evo_device_data(fake_hass, config_entry)

    # Optionally, assert that the exception message contains relevant authentication information.
    assert "Authentication error" in str(excinfo.value)