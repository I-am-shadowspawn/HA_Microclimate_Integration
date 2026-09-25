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
async def test_microclimate_base_entity_uses_entry_identity_and_coordinator_refresh(hass):
    """A renamed controller keeps its device identity and one refresh path."""
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    entry = MockConfigEntry(
        domain="microclimate_integration",
        data={"evo_device": "device_123", "model": "Evo Connect", "token": "fake"},
    )
    coordinator = DataUpdateCoordinator(
        hass, logger=logging.getLogger(__name__), name="test_coordinator",
        config_entry=entry, update_method=AsyncMock(),
    )
    entity = MicroclimateBaseEntity(coordinator, "Yellow")
    assert entity.device_info["identifiers"] == {
        ("microclimate_integration", f"{entry.entry_id}_Yellow")
    }
    assert entity.data == {}

    coordinator.async_request_refresh = AsyncMock()
    with patch.object(entity, "async_write_ha_state") as publish:
        await entity.async_update()
    coordinator.async_request_refresh.assert_awaited_once()
    publish.assert_not_called()
