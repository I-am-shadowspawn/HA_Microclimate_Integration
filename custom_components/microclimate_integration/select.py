"""Allowlisted mode selectors, using confirmed numeric enum mappings."""
from homeassistant.components.select import SelectEntity
from .const_helpers import enum_value
from .write_entity import WriteEntity, setup_controls


async def async_setup_entry(hass, entry, async_add_entities):
    setup_controls(hass, entry, async_add_entities, 'select', MicroclimateSelect)


class MicroclimateSelect(WriteEntity, SelectEntity):
    @property
    def options(self):
        return list(dict(self.field.options).values())

    @property
    def current_option(self):
        return enum_value(self.data.get(self.field.pin), dict(self.field.options))

    async def async_select_option(self, option):
        await self._write(option)
