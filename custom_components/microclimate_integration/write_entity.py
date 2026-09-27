"""Shared entry/channel identity and observed-state configuration controls."""

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .channel_artwork import channel_picture
from .identity import channel_device_info, controller_device_info
from .validation import reported_temperature_unit
from .write_contract import applicable, control_mode, write_definitions


def setup_controls(hass, entry, async_add_entities, platform, entity_class):
    coordinator = entry.runtime_data
    async_add_entities(
        entity_class(coordinator, entry, field)
        for field in write_definitions(entry.data["model"])
        if field.platform == platform and field.index is None
    )


class WriteEntity(CoordinatorEntity):
    _attr_has_entity_name = True
    _attr_entity_registry_enabled_default = True

    def __init__(self, coordinator, entry, field):
        super().__init__(coordinator)
        self.field = field
        self._attr_entity_picture = channel_picture(field.channel) if field.channel else None
        self._attr_unique_id = f"{entry.entry_id}_write_{field.key}"
        self._attr_device_info = (
            channel_device_info(entry, field.channel, coordinator.hass)
            if field.channel
            else controller_device_info(entry)
        )
        self._attr_extra_state_attributes = {
            "source_pin": field.pin,
            "confirmation": "API readback",
        }

    @property
    def data(self):
        return self.coordinator.data if isinstance(self.coordinator.data, dict) else {}

    @property
    def available(self):
        return (
            super().available
            and self.coordinator.writes_enabled
            and applicable(self.field, self.data)
            and (not self.thermal or reported_temperature_unit(self.data) is not None)
        )

    @property
    def name(self):
        return self.field.name

    @property
    def thermal(self):
        return self.field.kind == "number" or (
            self.field.kind == "setpoint"
            and control_mode(self.field, self.data) in ("heating", "cooling")
        )

    async def _write(self, value):
        await self.coordinator.async_write(self.field.key, value)
