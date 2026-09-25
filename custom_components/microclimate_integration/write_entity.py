"""Shared entry/channel identity and observed-state configuration controls."""
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
from .identity import channel_device_info, controller_device_info
from .write_contract import write_definitions, applicable, control_mode


def setup_controls(hass, entry, async_add_entities, platform, entity_class):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(entity_class(coordinator, entry, field)
                       for field in write_definitions(entry.data['model']) if field.platform == platform and field.index is None)


class WriteEntity(CoordinatorEntity):
    _attr_has_entity_name = True
    _attr_entity_registry_enabled_default = True

    def __init__(self, coordinator, entry, field):
        super().__init__(coordinator)
        self.field = field
        self._attr_unique_id = f'{entry.entry_id}_write_{field.key}'
        self._attr_device_info = (channel_device_info(entry, field.channel, coordinator.hass)
                                  if field.channel else controller_device_info(entry))
        self._attr_extra_state_attributes = {'source_pin': field.pin, 'confirmation': 'API readback'}

    @property
    def data(self):
        return self.coordinator.data if isinstance(self.coordinator.data, dict) else {}

    @property
    def available(self):
        return super().available and self.coordinator.writes_enabled and applicable(self.field, self.data)

    @property
    def name(self):
        return self.field.name

    @property
    def thermal(self):
        return self.field.kind == 'number' or control_mode(self.field, self.data) in ('heating', 'cooling')

    async def _write(self, value):
        await self.coordinator.async_write(self.field.key, value)
