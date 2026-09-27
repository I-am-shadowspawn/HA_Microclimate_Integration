"""Static artwork used for channel entity pictures."""

from pathlib import Path

from homeassistant.components.http import StaticPathConfig

_URL_PREFIX = "/microclimate_integration/channel"
_CHANNEL_FILES = {
    "Red": "channel_red.png",
    "Yellow": "channel_yellow.png",
    "Blue": "channel_blue.png",
}


def channel_picture(channel: str) -> str | None:
    """Return a local entity-picture URL for a known channel."""
    filename = _CHANNEL_FILES.get(channel)
    return f"{_URL_PREFIX}/{filename}" if filename else None


async def async_register_channel_artwork(hass) -> None:
    """Expose only the three packaged channel pictures."""
    static_dir = Path(__file__).parent / "static"
    await hass.http.async_register_static_paths(
        [
            StaticPathConfig(f"{_URL_PREFIX}/{filename}", str(static_dir / filename), True)
            for filename in _CHANNEL_FILES.values()
        ]
    )
