"""Entry-bound HA identity for fresh installations."""
import hashlib
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers import device_registry as dr
from .const import DOMAIN


def token_identity(token):
    """Full digest for duplicate detection; never put credentials in IDs."""
    return hashlib.sha256(token.encode()).hexdigest()


def channel_identity(entry, channel):
    """Stable across updates to entry name and token."""
    return f"{entry.entry_id}_{channel}"


def controller_device_info(entry):
    return DeviceInfo(identifiers={(DOMAIN, entry.entry_id)},
                      name=f"Microclimate {entry.data['evo_device']}",
                      manufacturer="Microclimate", model=entry.data.get("model"))


def channel_device_info(entry, channel, hass=None):
    info = DeviceInfo(identifiers={(DOMAIN, channel_identity(entry, channel))},
                      name=f"Microclimate {entry.data['evo_device']} {channel}",
                      manufacturer="Microclimate", model=entry.data.get("model"))
    if hass is not None:
        parent = dr.async_get(hass).async_get_device_by_identifier((DOMAIN, entry.entry_id), entry.entry_id)
        if parent is not None:
            info["via_device_id"] = parent.id
    return info

