"""Bounded alarm thresholds and supported ramp durations."""
from homeassistant.components.number import NumberEntity, NumberMode, NumberDeviceClass
from homeassistant.const import UnitOfTemperature, UnitOfTime, PERCENTAGE
from .write_contract import observed_numeric, WriteValidationError
from .constraints import numeric_maximum
from .write_entity import WriteEntity, setup_controls


async def async_setup_entry(hass, entry, async_add_entities):
    setup_controls(hass, entry, async_add_entities, 'number', MicroclimateNumber)


class MicroclimateNumber(WriteEntity, NumberEntity):
    _attr_native_min_value = 0
    _attr_mode = NumberMode.BOX

    @property
    def native_max_value(self):
        return numeric_maximum(self.field.kind)

    @property
    def native_step(self):
        return 1 if self.field.kind == 'ramp' else 0.1

    @property
    def native_value(self):
        try:
            return float(observed_numeric(self.field,self.data))
        except WriteValidationError:
            return None

    @property
    def native_unit_of_measurement(self):
        if self.field.kind == 'ramp':
            return UnitOfTime.MINUTES
        return UnitOfTemperature.CELSIUS if self.thermal else PERCENTAGE

    @property
    def device_class(self):
        if self.field.kind == 'ramp':
            return NumberDeviceClass.DURATION
        return NumberDeviceClass.TEMPERATURE if self.thermal else None

    async def async_set_native_value(self, value):
        await self._write(value)
