"""Channel pictures belong to entities, not to root-device metadata."""

from unittest.mock import AsyncMock, patch

from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.microclimate_integration.channel_artwork import channel_picture
from custom_components.microclimate_integration.const import DOMAIN


async def test_channel_entity_pictures_and_served_assets(hass, hass_client):
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Artwork controller",
        data={
            "evo_device": "artwork_controller",
            "token": "dummy_token_not_a_secret",
            "model": "Evo Connect 3",
        },
    )
    entry.add_to_hass(hass)
    with patch(
        "custom_components.microclimate_integration.api_client.fetch_data",
        new=AsyncMock(return_value={"v25": "C"}),
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    devices = dr.async_get(hass)
    entities = er.async_get(hass)
    client = await hass_client()
    for channel in ("Red", "Yellow", "Blue"):
        device = devices.async_get_device_by_identifier(
            (DOMAIN, f"{entry.entry_id}_{channel}"), entry.entry_id
        )
        assert device is not None
        states = [
            hass.states.get(entity.entity_id)
            for entity in entities.entities.values()
            if entity.device_id == device.id
        ]
        visible_states = [state for state in states if state is not None]
        assert visible_states
        assert {"climate", "sensor", "select", "number"} <= {
            state.domain for state in visible_states
        }
        picture = channel_picture(channel)
        assert all(state.attributes.get("entity_picture") == picture for state in visible_states)
        response = await client.get(picture)
        assert response.status == 200
        assert response.content_type == "image/png"
        assert (await response.read()).startswith(b"\x89PNG\r\n\x1a\n")

    root = devices.async_get_device_by_identifier((DOMAIN, entry.entry_id), entry.entry_id)
    assert root is not None
    root_states = [
        hass.states.get(entity.entity_id)
        for entity in entities.entities.values()
        if entity.device_id == root.id
    ]
    assert root_states
    assert all(
        "entity_picture" not in state.attributes for state in root_states if state is not None
    )
    assert channel_picture("unknown") is None
