# custom_components/microclimate_integration/climate.py
import logging
from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    HVACMode, HVACAction
)
from homeassistant.components.climate.const import ClimateEntityFeature
from homeassistant.const import UnitOfTemperature

from .readings import read_pin
from .validation import percentage, nonnegative_number, control_mode, safe_temperature
from homeassistant.exceptions import HomeAssistantError
from .const import CHANNEL_CAPABILITIES, CHANNELS, HVAC_MODE_MAPPING, DOMAIN, MODEL_CHANNEL_OPTIONS
from .helpers import MicroclimateBaseEntity
from .identity import channel_identity, channel_device_info

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up devices and entities."""
    evo_device = entry.data["evo_device"]
    model = entry.data.get("model", "Unknown")
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []

    for channel, channel_config in MODEL_CHANNEL_OPTIONS.get(model, {}).items():
        pins = CHANNELS.get(channel, {})

        # Only create a climate entity if the channel has a temperature probe
        if channel_config.get("hasTemperatureProbe", False):
            entities.append(MicroclimateClimate(coordinator, evo_device, model, channel, pins))

    async_add_entities(entities)
    _LOGGER.debug("Created %s climate entities", len(entities))


class MicroclimateClimate(MicroclimateBaseEntity, ClimateEntity):
    """Observational climate entity; device writes are not supported."""
    _attr_hvac_modes = []
    _attr_supported_features = ClimateEntityFeature(0)
    _attr_temperature_unit = UnitOfTemperature.CELSIUS


    def __init__(self, coordinator, evo_device, model, channel, pins):
        super().__init__(coordinator, evo_device, model, channel)
        self._attr_unique_id = channel_identity(coordinator.config_entry, channel)
        self._pins = pins or {}
        # Concatenate evo_device and data.get outcome into a single string for _attr_name
        channel_name = self._pins.get("channel_name")
        self._attr_name = f"{evo_device}: {self.data.get(channel_name, 'Unknown')}"
        self._attr_device_info = channel_device_info(coordinator.config_entry, channel, coordinator.hass)


    @property
    def target_temperature(self):
        """Return a temperature only for a known thermal control mode."""
        if read_pin(self.data, self._pins.get("control_pin"), control_mode) not in ("heating", "cooling"):
            return None
        return read_pin(self.data, self._pins.get("setpoint_pin"), safe_temperature)

    @property
    def hvac_mode(self):
        """Configured thermal mode is independent of present output."""
        mode = read_pin(self.data, self._pins.get("control_pin"), control_mode)
        return HVAC_MODE_MAPPING.get(mode)

    @property
    def hvac_action(self):
        """Describe observed output only when mode and power are usable."""
        mode = self.hvac_mode
        power = read_pin(self.data, self._pins.get("current_power"), percentage)
        if mode not in (HVACMode.HEAT, HVACMode.COOL) or power is None or power < 0:
            return None
        if power == 0:
            return HVACAction.IDLE
        return HVACAction.HEATING if mode == HVACMode.HEAT else HVACAction.COOLING

    @property
    def extra_state_attributes(self):
        """Expose observations without advertising a writable target."""
        attributes = {
            "observed_target_temperature": self.target_temperature,
            "lower_alarm": read_pin(self.data, self._pins.get("lower_alarm"), safe_temperature),
            "upper_alarm": read_pin(self.data, self._pins.get("upper_alarm"), safe_temperature),
            "mode": read_pin(self.data, self._pins.get("control_pin"), control_mode),
            "current_power": read_pin(self.data, self._pins.get("current_power"), percentage),
        }

        if CHANNEL_CAPABILITIES[self._channel]["ramp"]:
            attributes["ramp_time"] = read_pin(self.data, self._pins.get("ramp_time"), nonnegative_number)
        return attributes

    @property
    def current_temperature(self):
        return read_pin(self.data, self._pins.get("temp_pin"), safe_temperature)

    async def async_set_temperature(self, **kwargs):
        raise HomeAssistantError("Microclimate is observational; device writes are unsupported")

    async def async_set_hvac_mode(self, hvac_mode):
        raise HomeAssistantError("Microclimate is observational; device writes are unsupported")

    async def async_turn_on(self):
        raise HomeAssistantError("Microclimate is observational; device writes are unsupported")

    async def async_turn_off(self):
        raise HomeAssistantError("Microclimate is observational; device writes are unsupported")

    def entity_name(self):
        """sets the entities user-friendly name value"""


        return self.data.get(self._pins.get("channel_name"))

    async def async_update(self):
        """Update data from the coordinator."""
        await self.coordinator.async_request_refresh()
        self._attr_target_temperature = self.target_temperature  # Force re-fetch
        self.async_write_ha_state()  # Force HA to recognize updates
