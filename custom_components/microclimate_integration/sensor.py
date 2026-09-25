from .const import CHANNEL_CAPABILITIES, timing_type_mapping, DEFAULT_ENABLE_DIAGNOSTICS
from homeassistant.const import UnitOfTemperature, PERCENTAGE
import re
from .readings import cached, read_pin, read_enum
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import SensorEntity
from .identity import channel_identity, controller_device_info, channel_device_info
from .sensor_contract import VERIFIED_MEASUREMENTS
from .validation import finite_number, safe_temperature, control_mode, safe_scalar, nonnegative_number, percentage
from custom_components.microclimate_integration.const import MODEL_CHANNEL_OPTIONS, CHANNELS, DEVICE_METADATA_PINS, CONTROL_TYPE_MAPPING, OUTPUT_TYPE_MAPPING
from .const_helpers import enum_value
from .schedule import schedule_observation, reported_value, observe_time, observe_date, observe_field
from custom_components.microclimate_integration.const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    """Use the entry coordinator; raw candidates make no vendor claims."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [MicroclimatePinCount(coordinator, entry), MicroclimateWriteStatus(coordinator, entry)]
    entities.extend(MicroclimateDeviceMetadata(coordinator, entry, key, definition)
                    for key, definition in DEVICE_METADATA_PINS.items())
    for channel in MODEL_CHANNEL_OPTIONS.get(entry.data.get("model"), {}):
        entities.append(MicroclimateSchedule(coordinator, entry, channel))
        entities.extend(MicroclimateChannelMode(coordinator, entry, channel, key, name, mapping)
                        for key, name, mapping in (
                            ("control_pin", "Control mode", CONTROL_TYPE_MAPPING),
                            ("timing_type", "Timing type", timing_type_mapping(channel)),
                            ("output_type", "Output type", OUTPUT_TYPE_MAPPING),
                        ))
        # Only existing pin mappings: no inferred or dynamically exposed fields.
        pins = sorted({pin for pin in CHANNELS.get(channel, {}).values()
                       if isinstance(pin, str) and re.fullmatch(r"v[0-9]+", pin)})
        entities.extend(MicroclimateRawPin(coordinator, entry, channel, pin) for pin in pins)
    entities.extend(MicroclimateMeasurement(coordinator, entry, definition)
                    for definition in VERIFIED_MEASUREMENTS.get(entry.data.get("model"), ()))
    async_add_entities(entities)


class MicroclimatePinCount(CoordinatorEntity, SensorEntity):
    """A structural response diagnostic, independent of hardware semantics."""
    _attr_has_entity_name = True
    _attr_name = "Reported pin count"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_reported_pin_count"
        self._attr_device_info = controller_device_info(entry)

    @property
    def native_value(self):
        data = self.coordinator.data
        if not isinstance(data, dict):
            return None
        return cached(data, "pin_count", lambda: sum(isinstance(key, str) and bool(re.fullmatch(r"v[0-9]+", key)) for key in data))


class MicroclimateRawPin(CoordinatorEntity, SensorEntity):
    """Raw observation, temporarily enabled by default; mapping and physical meaning are unverified."""
    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_entity_registry_enabled_default = DEFAULT_ENABLE_DIAGNOSTICS

    def __init__(self, coordinator, entry, channel, pin):
        super().__init__(coordinator)
        self._pin = pin
        self._attr_name = f"Raw {pin}"
        self._attr_unique_id = f"{channel_identity(entry, channel)}_raw_{pin}"
        self._attr_device_info = channel_device_info(entry, channel, coordinator.hass)
        self._attr_extra_state_attributes = {"source_pin": pin, "interpretation": "raw"}

    @property
    def native_value(self):
        data = self.coordinator.data
        return read_pin(data, self._pin, safe_scalar)


class MicroclimateMeasurement(CoordinatorEntity, SensorEntity):
    """A typed reading explicitly described by a documented pin contract."""
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry, definition):
        super().__init__(coordinator)
        self.definition = definition
        self._attr_unique_id = f"{channel_identity(entry, definition.channel)}_measurement_{definition.key}"
        self._attr_name = definition.name
        self._attr_device_info = channel_device_info(entry, definition.channel, coordinator.hass)
        self._attr_native_unit_of_measurement = definition.unit
        self._attr_device_class = definition.device_class
        self._attr_state_class = definition.state_class
        self._attr_options = list(definition.alarm_codes.values()) if definition.alarm_codes else None
        self._attr_extra_state_attributes = {"source_pin": definition.pin, "evidence": definition.evidence}

    @property
    def native_value(self):
        data = self.coordinator.data
        if self.definition.kind == "setpoint":
            if read_pin(data, CHANNELS[self.definition.channel].get("control_pin"), control_mode) not in ("heating", "cooling"):
                return None
            return read_pin(data, self.definition.pin, safe_temperature)
        if self.definition.kind == "temperature":
            return read_pin(data, self.definition.pin, safe_temperature)
        if self.definition.kind == "percentage":
            return read_pin(data, self.definition.pin, percentage)
        if self.definition.kind == "duration":
            return read_pin(data, self.definition.pin, nonnegative_number)
        if self.definition.kind == "number":
            return read_pin(data, self.definition.pin, finite_number)
        number = read_pin(data, self.definition.pin, finite_number)
        if number is None or not number.is_integer():
            return None
        return self.definition.alarm_codes.get(int(number))


class MicroclimateDeviceMetadata(CoordinatorEntity, SensorEntity):
    """Controller-owned metadata; reported text until its encoding is verified."""
    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator, entry, key, definition):
        super().__init__(coordinator)
        self._pin = definition["pin"]
        self._transformation = definition["transformation"]
        self._attr_unique_id = f"{entry.entry_id}_metadata_{key.removesuffix('_pin')}"
        self._attr_name = definition["description"]
        self._attr_device_info = controller_device_info(entry)
        self._attr_extra_state_attributes = {"source_pin": self._pin, "interpretation": "reported"}

    def _observation(self):
        data = self.coordinator.data
        if self._transformation == "time":
            return observe_field(data, self._pin, observe_time)
        if self._transformation == "date":
            return observe_field(data, self._pin, observe_date)
        return {"raw": read_pin(data, self._pin, reported_value), "interpretation": "reported_unparsed"}

    @property
    def native_value(self):
        observation = self._observation()
        if observation.get("kind") == "clock":
            return observation["time"]
        if observation["interpretation"] in ("zero_date", "invalid_date", "missing_or_invalid"):
            return None
        scalar = safe_scalar(observation["raw"])
        if scalar is not None:
            return scalar
        return "reported_unparsed" if observation["raw"] is not None else None

    @property
    def extra_state_attributes(self):
        return {"source_pin": self._pin, **self._observation()}


class MicroclimateChannelMode(CoordinatorEntity, SensorEntity):
    """Read-only controller configuration using the shared enum definitions."""
    _attr_has_entity_name = True
    _attr_device_class = "enum"

    def __init__(self, coordinator, entry, channel, key, name, mapping):
        super().__init__(coordinator)
        self._pin = CHANNELS[channel][key]
        self._mapping = mapping
        self._fixed_output = key == "output_type" and not CHANNEL_CAPABILITIES[channel]["variable_output"]
        self._attr_unique_id = f"{channel_identity(entry, channel)}_configuration_{key}"
        self._attr_name = name
        self._attr_options = ["on_off"] if self._fixed_output else list(mapping.values())
        self._attr_device_info = channel_device_info(entry, channel, coordinator.hass)
        self._attr_extra_state_attributes = ({"interpretation": "hardware_capability"} if self._fixed_output
                                             else {"source_pin": self._pin})

    @property
    def native_value(self):
        if self._fixed_output:
            return "on_off"
        data = self.coordinator.data
        return read_enum(data, self._pin, self._mapping)


class MicroclimateSchedule(CoordinatorEntity, SensorEntity):
    """Count reported periods and expose their data; no active-period inference."""
    _attr_has_entity_name = True
    _attr_name = "Reported schedule periods"
    # Full detail remains live; history retains the compact summary and mode/count.
    _unrecorded_attributes = frozenset({
        'periods', 'daily_points', 'day_night', 'seasons', 'duplicate_clock_times',
        'timing', 'control', 'ramp_time', 'periodic_interval', 'periodic_duration',
    })
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator, entry, channel):
        super().__init__(coordinator)
        self._channel = channel
        self._attr_unique_id = f"{channel_identity(entry, channel)}_schedule"
        self._attr_device_info = channel_device_info(entry, channel, coordinator.hass)

    @property
    def native_value(self):
        count = schedule_observation(self.coordinator.data, self._channel)["reported_period_count"]
        return count if count else None

    @property
    def extra_state_attributes(self):
        return schedule_observation(self.coordinator.data, self._channel)


class MicroclimateWriteStatus(CoordinatorEntity, SensorEntity):
    """Compact last operation result, without credentials or response bodies."""
    _attr_has_entity_name = True
    _attr_name = 'Last configuration write'
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_entity_registry_enabled_default = DEFAULT_ENABLE_DIAGNOSTICS

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_unique_id = f'{entry.entry_id}_last_write'
        self._attr_device_info = controller_device_info(entry)

    @property
    def native_value(self):
        return (self.coordinator.last_write or {}).get('status', 'idle')

    @property
    def extra_state_attributes(self):
        return self.coordinator.last_write or {}
