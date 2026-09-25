import logging

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import CoordinatorEntity, UpdateFailed

from .api_client import get_evo_device_data
from .identity import channel_device_info, controller_device_info

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
    """Coordinator-backed entity bound to the config entry's device identity."""

    def __init__(self, coordinator, channel=None):
        super().__init__(coordinator)
        self._entry = coordinator.config_entry
        self._channel = channel
        self._attr_device_info = (
            channel_device_info(self._entry, channel, coordinator.hass)
            if channel else controller_device_info(self._entry)
        )

    @property
    def data(self):
        """Return a safe mapping when no usable coordinator data exists."""
        data = self.coordinator.data
        return data if isinstance(data, dict) else {}
