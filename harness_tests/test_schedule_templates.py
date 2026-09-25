"""Portable schedule files and HA automation actions use one guarded save engine."""

import json
from unittest.mock import Mock

import pytest
from homeassistant.core import Context
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import device_registry as dr, entity_registry as er

from custom_components.microclimate_integration.const import DOMAIN
from custom_components.microclimate_integration.schedule_templates import (
    FORMAT,
    export_template,
    import_patch,
    parse_template,
)
from custom_components.microclimate_integration.write_contract import WriteValidationError
from test_card_contract import populate
from test_write_runtime import runtime


def device_id(hass, entry, channel):
    return dr.async_get(hass).async_get_device_by_identifier((DOMAIN, f"{entry.entry_id}_{channel}"), entry.entry_id).id


def test_portable_template_has_no_pin_or_device_identity():
    from test_write_runtime import payload

    source = payload()
    populate(source, 3, "Yellow")
    template = export_template("Evo Connect 3", "Yellow", source)
    assert template == {
        "format": FORMAT, "mode": "Multi", "unit": "celsius",
        "points": [
            {"seconds": 3600, "target_native": 21.0},
            {"seconds": 7200, "target_native": 22.0},
            {"seconds": 10800, "target_native": 23.0},
        ],
    }
    encoded = json.dumps(template)
    assert "v32" not in encoded and "token" not in encoded and "device_id" not in encoded
    target = payload()
    populate(target, 2, "Red")
    patch = import_patch("Evo Connect 3", "Red", target, template)
    assert patch["schedule"]["points"] == template["points"]
    assert patch["kind"] == "channel" and patch["fields"] == {}


@pytest.mark.parametrize("mode,code,count", [("Day Night", 1, 2), ("Seasonal", 3, 8)])
def test_export_preserves_mode_specific_point_count_without_root_dates(mode, code, count):
    from test_write_runtime import payload

    data = payload()
    populate(data, count, "Yellow")
    data["v53"] = code
    data.update(v20="09/02", v21="01/05", v22="01/08", v23="01/11")
    template = export_template("Evo Connect 3", "Yellow", data)
    assert template["mode"] == mode and len(template["points"]) == count
    assert "v20" not in json.dumps(template) and "09/02" not in json.dumps(template)


@pytest.mark.parametrize("mutate", [
    lambda t: {**t, "unit": "percent"},
    lambda t: {**t, "mode": "Seasonal"},
    lambda t: {**t, "points": t["points"][:1]},
    lambda t: {**t, "points": list(reversed(t["points"]))},
    lambda t: {**t, "points": [{"seconds": 0, "target_native": 0}, *t["points"][1:]]},
    lambda t: {**t, "device_id": "foreign"},
])
def test_import_rejects_incompatible_or_invalid_templates(mutate):
    from test_write_runtime import payload

    data = payload()
    populate(data, 3)
    source = export_template("Evo Connect 3", "Yellow", data)
    with pytest.raises(WriteValidationError):
        import_patch("Evo Connect 3", "Yellow", data, mutate(source))


def test_import_rejects_oversized_or_malformed_json():
    for value in ("{", "x" * 4097, "\ud800"):
        with pytest.raises(WriteValidationError, match="invalid_patch"):
            parse_template(value)


def test_fixed_output_percent_cannot_be_imported_as_temperature():
    from test_write_runtime import payload

    fixed = payload("Evo Connect")
    populate(fixed, 2, "Blue")
    preset = export_template("Evo Connect", "Blue", fixed)
    assert preset["unit"] == "percent"
    thermal = payload("Evo Connect 3")
    populate(thermal, 2, "Blue")
    with pytest.raises(WriteValidationError, match="stale_context"):
        import_patch("Evo Connect 3", "Blue", thermal, preset)


async def test_copy_schedule_service_uses_existing_job_and_preserves_source(hass, runtime):
    entry, coordinator, data, reader, writer = runtime
    populate(data, 3, "Yellow")
    populate(data, 2, "Red")
    coordinator._publish(dict(data))
    source_before = {pin: value for pin, value in data.items() if pin.startswith("v3") or pin.startswith("v4")}
    result = await hass.services.async_call(
        DOMAIN, "copy_schedule", {"source_device_id": device_id(hass, entry, "Yellow"),
                                  "target_device_id": device_id(hass, entry, "Red")},
        blocking=True, return_response=True,
    )
    assert result["status"] == "succeeded" and result["confirmed"] > 0
    assert writer.await_count == result["confirmed"]
    assert [float(data[pin]) for pin in ("v63", "v65", "v67")] == [21, 22, 23]
    assert all(data[pin] == value for pin, value in source_before.items())
    assert reader.await_count > 1


async def test_export_and_apply_service_copy_without_arbitrary_pins(hass, runtime):
    entry, coordinator, data, _reader, writer = runtime
    populate(data, 3, "Yellow")
    populate(data, 2, "Red")
    coordinator._publish(dict(data))
    exported = await hass.services.async_call(
        DOMAIN, "export_schedule", {"device_id": device_id(hass, entry, "Yellow")},
        blocking=True, return_response=True,
    )
    template = json.loads(exported["template"])
    assert template["format"] == FORMAT and "token" not in exported["template"]
    result = await hass.services.async_call(
        DOMAIN, "apply_schedule", {"device_id": device_id(hass, entry, "Red"),
                                   "template": exported["template"]},
        blocking=True, return_response=True,
    )
    assert result["status"] == "succeeded" and writer.await_count == result["confirmed"]


async def test_named_user_source_permission_is_checked(hass, runtime, monkeypatch):
    entry, coordinator, data, _reader, writer = runtime
    populate(data, 2, "Yellow")
    coordinator._publish(dict(data))
    user = Mock(id="limited-user")
    user.permissions.check_entity.return_value = False
    async def get_user(_uid):
        return user
    monkeypatch.setattr(hass.auth, "async_get_user", get_user)
    with pytest.raises(HomeAssistantError, match="read_denied"):
        await hass.services.async_call(
            DOMAIN, "export_schedule", {"device_id": device_id(hass, entry, "Yellow")},
            blocking=True, return_response=True, context=Context(user_id="limited-user"),
        )
    assert writer.await_count == 0


async def test_apply_service_partial_failure_reports_without_retry(hass, runtime):
    from custom_components.microclimate_integration.write_transport import UpdateResult

    entry, coordinator, data, _reader, writer = runtime
    populate(data, 3, "Yellow")
    coordinator._publish(dict(data))
    template = export_template("Evo Connect 3", "Yellow", data)
    template["points"][0]["target_native"] = 25
    template["points"][1]["target_native"] = 26
    original = writer.side_effect

    async def reject_second(*args, **kwargs):
        if writer.await_count == 2:
            return UpdateResult("rejected")
        return await original(*args, **kwargs)

    writer.side_effect = reject_second
    result = await hass.services.async_call(
        DOMAIN, "apply_schedule", {"device_id": device_id(hass, entry, "Yellow"),
                                   "template": json.dumps(template)},
        blocking=True, return_response=True,
    )
    assert result["status"] == "partial" and result["confirmed"] == 1
    assert writer.await_count == 2


async def test_disabled_schedule_anchor_blocks_automation(hass, runtime):
    entry, coordinator, data, _reader, writer = runtime
    populate(data, 2, "Yellow")
    coordinator._publish(dict(data))
    template = export_template("Evo Connect 3", "Yellow", data)
    template["points"][0]["target_native"] = 30
    registry = er.async_get(hass)
    anchor = registry.async_get_entity_id("sensor", DOMAIN, f"{entry.entry_id}_Yellow_schedule")
    registry.async_update_entity(anchor, disabled_by=er.RegistryEntryDisabler.USER)
    with pytest.raises(HomeAssistantError, match="control_denied"):
        await hass.services.async_call(
            DOMAIN, "apply_schedule", {"device_id": device_id(hass, entry, "Yellow"),
                                       "template": json.dumps(template)},
            blocking=True, return_response=True,
        )
    assert writer.await_count == 0
