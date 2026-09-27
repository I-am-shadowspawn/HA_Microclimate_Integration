"""Registry and card identity retained from the v1.4.5-delta2 public baseline."""

from unittest.mock import AsyncMock, patch

from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.microclimate_integration.card_model import resolve, snapshot
from custom_components.microclimate_integration.config_flow import MicroclimateConfigFlow
from custom_components.microclimate_integration.const import DOMAIN
from custom_components.microclimate_integration.identity import token_identity
from tests.helpers import payload

ENTRY_ID = "v2_public_baseline"


def registry_view(hass, entry):
    """Capture durable IDs and user registry choices, excluding runtime revisions."""
    registry = er.async_get(hass)
    devices = dr.async_get(hass)
    entities = {
        row.unique_id: (row.entity_id, row.device_id, row.name, row.disabled_by)
        for row in er.async_entries_for_config_entry(registry, entry.entry_id)
    }
    registered_devices = {
        next(identifier for identifier in device.identifiers if identifier[0] == DOMAIN): (
            device.id,
            device.name_by_user,
        )
        for device in dr.async_entries_for_config_entry(devices, entry.entry_id)
    }
    return entities, registered_devices


async def test_public_candidate_identity_survives_upgrade_reauth_and_reload(hass, hass_admin_user):
    """A saved card device ID and customized registry rows survive normal release reloads."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        entry_id=ENTRY_ID,
        unique_id=token_identity("candidate-one"),
        data={
            "evo_device": "candidate controller",
            "model": "Evo Connect 2",
            "token": "candidate-one",
        },
    )
    entry.add_to_hass(hass)
    read = AsyncMock(return_value=payload("Evo Connect 2"))
    with patch("custom_components.microclimate_integration.api_client.fetch_data", read):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        assert entry.version == MicroclimateConfigFlow.VERSION == 1

        registry = er.async_get(hass)
        devices = dr.async_get(hass)
        # These unique IDs and device identifiers existed in the tagged candidate.
        assert registry.async_get_entity_id("climate", DOMAIN, f"{ENTRY_ID}_Yellow")
        assert registry.async_get_entity_id("sensor", DOMAIN, f"{ENTRY_ID}_Yellow_schedule")
        assert registry.async_get_entity_id(
            "select", DOMAIN, f"{ENTRY_ID}_write_Yellow_control_pin"
        )
        assert registry.async_get_entity_id("text", DOMAIN, f"{ENTRY_ID}_write_season_1_start_pin")
        root = devices.async_get_device_by_identifier((DOMAIN, ENTRY_ID), ENTRY_ID)
        channel = devices.async_get_device_by_identifier((DOMAIN, f"{ENTRY_ID}_Yellow"), ENTRY_ID)
        assert root and channel
        card_configuration = {"type": "custom:microclimate-channel-card", "device_id": channel.id}
        root_card = {"type": "custom:microclimate-controller-card", "device_id": root.id}

        climate_id = registry.async_get_entity_id("climate", DOMAIN, f"{ENTRY_ID}_Yellow")
        registry.async_update_entity(climate_id, name="User thermostat")
        devices.async_update_device(channel.id, name_by_user="User channel")
        original = registry_view(hass, entry)

        async def assert_cards_and_registry():
            assert registry_view(hass, entry) == original
            coordinator, selected, selected_device = resolve(hass, card_configuration["device_id"])
            assert selected == "Yellow" and selected_device.id == channel.id
            view = snapshot(hass, coordinator, selected, selected_device, hass_admin_user)
            assert view["device_id"] == card_configuration["device_id"]
            assert view["schema_version"] == 1
            assert any(
                field["authorization_scope"] == "channel_schedule" for field in view["fields"]
            )
            root_coordinator, root_selected, root_device = resolve(hass, root_card["device_id"])
            assert root_selected is None
            root_view = snapshot(
                hass, root_coordinator, root_selected, root_device, hass_admin_user
            )
            assert root_view["device_id"] == root_card["device_id"]
            assert any(field["key"] == "season_1_start_pin" for field in root_view["fields"])

        await assert_cards_and_registry()
        # A normal release replaces code while retaining the HA entry and registries.
        # Reload exercises that retained-state path without swapping packages.
        assert await hass.config_entries.async_reload(entry.entry_id)
        await hass.async_block_till_done()
        await assert_cards_and_registry()

        flow = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": "reconfigure", "entry_id": entry.entry_id}
        )
        result = await hass.config_entries.flow.async_configure(
            flow["flow_id"], {"evo_device": "renamed controller", "token": "candidate-two"}
        )
        assert result["reason"] == "reconfigure_successful"
        await hass.async_block_till_done()
        assert entry.entry_id == ENTRY_ID and entry.unique_id == token_identity("candidate-two")
        await assert_cards_and_registry()

        flow = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": "reauth", "entry_id": entry.entry_id},
            data=entry.data,
        )
        result = await hass.config_entries.flow.async_configure(
            flow["flow_id"], {"token": "candidate-three"}
        )
        assert result["reason"] == "reauth_successful"
        await hass.async_block_till_done()
        assert entry.entry_id == ENTRY_ID and entry.unique_id == token_identity("candidate-three")
        await assert_cards_and_registry()

        # Repeat after credential changes; physical package rollback is a separate check.
        assert await hass.config_entries.async_reload(entry.entry_id)
        await hass.async_block_till_done()
        await assert_cards_and_registry()
        assert await hass.config_entries.async_unload(entry.entry_id)
