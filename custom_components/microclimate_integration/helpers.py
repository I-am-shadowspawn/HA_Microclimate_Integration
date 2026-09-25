import logging

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import CoordinatorEntity, UpdateFailed

from .api_client import get_evo_device_data
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_update_data(hass, config_entry):
    """Fetch data from the API."""
    try:
        return await get_evo_device_data(hass, config_entry)
    except ConfigEntryAuthFailed:
        raise ConfigEntryAuthFailed("Authentication failed for Microclimate integration") from None
    except Exception:
        # Do not log or chain transport exceptions containing request URLs.
        raise UpdateFailed("Unable to update Microclimate data") from None


class MicroclimateBaseEntity(CoordinatorEntity):
    """Base class for Microclimate entities."""

    def __init__(self, coordinator, evo_device, model, channel=None, pin=None):
        super().__init__(coordinator)
        self._evo_device = evo_device
        self._model = model
        self._channel = channel
        self._pin = pin
        self._name = "default_name"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, evo_device)},
            "name": f"Microclimate {evo_device} {channel if channel else 'System'}",
            "manufacturer": "Microclimate",
            "model": model,
        }

    @property
    def data(self):
        """Return a safe mapping when no usable coordinator data exists."""
        data = self.coordinator.data
        return data if isinstance(data, dict) else {}

    async def async_update(self):
        """Ensure updates are requested."""
        await self.coordinator.async_request_refresh()
        self.async_write_ha_state()

