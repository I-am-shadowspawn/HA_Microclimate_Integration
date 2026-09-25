import pytest
import logging
from unittest.mock import AsyncMock, patch
from custom_components.microclimate_integration.helpers import (
    async_update_data,
    MicroclimateBaseEntity)

from homeassistant.core import HomeAssistant
import tempfile
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator


@pytest.mark.asyncio
async def test_async_update_data():
    """Test fetching data from the API."""

    with tempfile.TemporaryDirectory() as temp_config_dir:
        hass = HomeAssistant(temp_config_dir)  # ✅ Manually create HomeAssistant

        mock_data = {"temperature": 22.5, "humidity": 50}

        with patch("custom_components.microclimate_integration.helpers.get_evo_device_data", new=AsyncMock(return_value=mock_data)) as mock_api:
            data = await async_update_data(hass, "Device_123")

        mock_api.assert_awaited_once_with(hass, "Device_123")
        assert data == mock_data


@pytest.mark.asyncio
async def test_async_update_data2(hass:HomeAssistant):
    """Test fetching data from the API."""

    mock_data = {"temperature": 22.5, "humidity": 50}

    with patch("custom_components.microclimate_integration.helpers.get_evo_device_data", new=AsyncMock(return_value=mock_data)) as mock_api:
        data = await async_update_data(hass, "Device_123")

    mock_api.assert_awaited_once_with(hass, "Device_123")
    assert data == mock_data






@pytest.mark.asyncio
async def test_microclimate_base_entity_new():
    """Test MicroclimateBaseEntity initialization and async_update."""
    mock_coordinator = AsyncMock()
    evo_device = "device_123"
    model = "Evo Connect"
    channel = "Yellow"
    logger = logging.getLogger("test_logger")

    with tempfile.TemporaryDirectory() as temp_config_dir:
        hass_instance = HomeAssistant(temp_config_dir)

        # Create a real DataUpdateCoordinator with hass
        coordinator = DataUpdateCoordinator(
            hass_instance,
            logger=logger,
            name="test_coordinator",
            config_entry=None,  # Standalone test coordinator has no config entry.
            update_method=AsyncMock(),
            update_interval=None,  # No auto updates in test
        )
        # Patch out async_config_entry_first_refresh to avoid MissingIntegrationFrame error.
        coordinator.async_config_entry_first_refresh = AsyncMock(return_value=None)
        await coordinator.async_config_entry_first_refresh()

        entity = MicroclimateBaseEntity(coordinator, evo_device, model, channel)
        # Manually set hass on the entity to mimic HA's behavior.
        entity.hass = hass_instance

        # Override async_write_ha_state to bypass the missing entity ID error.
        entity.async_write_ha_state = lambda: None

    # Verify attributes
    assert entity.hass is not None  # This should now pass
    assert entity._evo_device == evo_device
    assert entity._model == model
    assert entity._channel == channel
    assert "identifiers" in entity._attr_device_info
    assert entity._attr_device_info["identifiers"] == {("microclimate_integration", evo_device)}

    # Mock async_request_refresh on the coordinator
    coordinator.async_request_refresh = AsyncMock()

    # Test async_update
    await entity.async_update()
    coordinator.async_request_refresh.assert_called_once()
