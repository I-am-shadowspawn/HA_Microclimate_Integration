"""Microclimate Integration for Home Assistant."""
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .coordinator import MicroclimateCoordinator
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity import EntityCategory
from .identity import controller_device_info
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN, DEFAULT_ENABLE_DIAGNOSTICS
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

PLATFORMS = ["climate", "sensor", "select", "number", "text"]

_LOGGER = logging.getLogger(__name__)


# noinspection SpellCheckingInspection
async def async_setup(hass: HomeAssistant, _config: dict):
    """Set up the Microclimate Integration."""
    hass.data.setdefault(DOMAIN, {})
    from .card_api import async_setup_card_api
    await async_setup_card_api(hass)
    return True


async def async_setup_entry(hass, entry):
    coordinator = MicroclimateCoordinator(hass, entry)
    forwarding = False
    try:
        await coordinator.async_config_entry_first_refresh()
        hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
        dr.async_get(hass).async_get_or_create(config_entry_id=entry.entry_id, **controller_device_info(entry))
        if DEFAULT_ENABLE_DIAGNOSTICS:
            registry = er.async_get(hass)
            for registered in er.async_entries_for_config_entry(registry, entry.entry_id):
                if (registered.platform == DOMAIN and registered.entity_category == EntityCategory.DIAGNOSTIC
                        and registered.disabled_by == er.RegistryEntryDisabler.INTEGRATION):
                    registry.async_update_entity(registered.entity_id, disabled_by=None)
        forwarding = True
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
        entry.async_on_unload(entry.add_update_listener(_options_updated))
        hass.bus.async_fire("microclimate_card_entry_changed", {"entry_id": entry.entry_id})
    except BaseException:
        await coordinator.async_close()
        if forwarding:
            try:
                await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
            except Exception:
                _LOGGER.error('Unable to unload partially initialized Microclimate platforms')
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
        raise

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    _LOGGER.debug("Unloading Microclimate entry")

    coordinator = hass.data[DOMAIN][entry.entry_id]
    await coordinator.async_stop_writes()
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        await coordinator.async_shutdown()
        hass.data[DOMAIN].pop(entry.entry_id, None)

    else:
        coordinator.closed = False
        await coordinator.async_refresh()
    hass.bus.async_fire("microclimate_card_entry_changed", {"entry_id": entry.entry_id})
    return unload_ok


async def _options_updated(hass, entry):
    coordinator = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    if coordinator is not None:
        coordinator.async_update_listeners()
