"""Root season starts use yearless DD/MM text, never a fabricated calendar year."""
from homeassistant.components.text import TextEntity, TextMode
from .write_contract import date_string, WriteValidationError
from .write_entity import WriteEntity, setup_controls


async def async_setup_entry(hass, entry, async_add_entities):
    setup_controls(hass, entry, async_add_entities, 'text', MicroclimateText)


class MicroclimateText(WriteEntity, TextEntity):
    _attr_native_min = 5
    _attr_native_max = 5
    _attr_pattern = r'[0-9]{2}/[0-9]{2}'
    _attr_mode = TextMode.TEXT

    @property
    def native_value(self):
        try:
            return date_string(self.data.get(self.field.pin))
        except WriteValidationError:
            return None

    async def async_set_value(self, value):
        await self._write(value)
