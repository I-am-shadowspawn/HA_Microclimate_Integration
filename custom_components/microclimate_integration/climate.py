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
from .identity import channel_identity

_LOGGER = logging.getLogger(__name__)
_READ_ONLY_MESSAGE = (
    "This climate entity is read-only; use the Microclimate configuration controls"
)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up devices and entities."""
    model = entry.data.get("model", "Unknown")
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []

    for channel, channel_config in MODEL_CHANNEL_OPTIONS.get(model, {}).items():
        pins = CHANNELS.get(channel, {})

        # Only create a climate entity if the channel has a temperature probe
        if channel_config.get("hasTemperatureProbe", False):
            entities.append(MicroclimateClimate(coordinator, channel, pins))

    async_add_entities(entities)
    _LOGGER.debug("Created %s climate entities", len(entities))


class MicroclimateClimate(MicroclimateBaseEntity, ClimateEntity):
    """Read-only climate observation of a channel with separate configuration controls."""
    _attr_hvac_modes = []
    _attr_supported_features = ClimateEntityFeature(0)
    _attr_temperature_unit = UnitOfTemperature.CELSIUS


    def __init__(self, coordinator, channel, pins):
        super().__init__(coordinator, channel)
        self._attr_unique_id = channel_identity(coordinator.config_entry, channel)
        self._pins = pins or {}

    @property
    def name(self):
        """Follow entry renames and reported channel names without changing entity IDs."""
        channel_name = self._pins.get("channel_name")
        return f"{self._entry.data['evo_device']}: {self.data.get(channel_name, 'Unknown')}"


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
        raise HomeAssistantError(_READ_ONLY_MESSAGE)

    async def async_set_hvac_mode(self, hvac_mode):
        raise HomeAssistantError(_READ_ONLY_MESSAGE)

    async def async_turn_on(self):
        raise HomeAssistantError(_READ_ONLY_MESSAGE)

    async def async_turn_off(self):
        raise HomeAssistantError(_READ_ONLY_MESSAGE)
