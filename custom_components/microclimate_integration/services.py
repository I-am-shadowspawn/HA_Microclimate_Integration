"""Trusted HA schedule actions using the card's existing validated save jobs."""

import json
from types import SimpleNamespace
from uuid import uuid4

import voluptuous as vol
from homeassistant.core import SupportsResponse
from homeassistant.exceptions import HomeAssistantError

from .card_api import KEY
from .card_model import SCHEMA_VERSION, field_access, generation, resolve, revision
from .const import DOMAIN
from .schedule_templates import export_template, import_patch, parse_template
from .write_contract import definition_for, WriteValidationError

_DEVICE_ID = vol.All(str, vol.Length(min=1, max=128))


async def _caller(hass, call):
    if call.context.user_id is None:
        # Automations run in HA's trusted system context; do not grant this to
        # a named user whose entity permissions can be checked explicitly.
        return SimpleNamespace(id="system", permissions=SimpleNamespace(check_entity=lambda *_: True))
    user = await hass.auth.async_get_user(call.context.user_id)
    if user is None:
        raise WriteValidationError("unauthorized")
    return user


def _source_template(hass, device_id, user):
    coordinator, channel, _device = resolve(hass, device_id)
    if channel is None or not coordinator.last_update_success:
        raise WriteValidationError("device_unavailable")
    template = export_template(coordinator.entry.data["model"], channel, coordinator.data)
    for index in range(1, len(template["points"]) + 1):
        for kind in ("time", "setpoint"):
            field = definition_for(coordinator.entry.data["model"], f"{channel}_period_{index}_{kind}")
            if not field_access(hass, coordinator, field, user):
                raise WriteValidationError("read_denied")
    return template


async def _apply(hass, device_id, template, user, *, return_response):
    coordinator, channel, device = resolve(hass, device_id)
    patch = import_patch(coordinator.entry.data["model"], channel, coordinator.data, template)
    msg = {"schema_version": SCHEMA_VERSION, "device_id": device.id,
           "runtime_generation": generation(coordinator), "base_revision": revision(coordinator, channel),
           "request_id": str(uuid4()), "patch": patch}
    api = hass.data[KEY]
    result = await api.save(msg, user)
    outcome = await api.jobs[result["operation_id"]]["completion"]
    if outcome["status"] != "succeeded" and not return_response:
        raise HomeAssistantError(
            f"Schedule {outcome['status']} ({outcome['confirmed']}/{outcome['total']} confirmed); "
            f"reason: {outcome['reason'] or 'unknown'}; operation: {outcome['operation_id']}. "
            "Review controller state before another action."
        )
    return {key: outcome[key] for key in ("operation_id", "status", "confirmed", "total", "reason")}


async def async_setup_services(hass):
    """Register once; ordinary entry unload does not remove integration actions."""
    if hass.services.has_service(DOMAIN, "apply_schedule"):
        return

    async def apply(call):
        try:
            return await _apply(hass, call.data["device_id"], parse_template(call.data["template"]),
                                await _caller(hass, call), return_response=call.return_response)
        except WriteValidationError as err:
            raise HomeAssistantError(f"Schedule action rejected: {err.code}") from None

    async def copy(call):
        try:
            user = await _caller(hass, call)
            template = _source_template(hass, call.data["source_device_id"], user)
            return await _apply(hass, call.data["target_device_id"], template, user,
                                return_response=call.return_response)
        except WriteValidationError as err:
            raise HomeAssistantError(f"Schedule action rejected: {err.code}") from None

    async def export(call):
        try:
            template = _source_template(hass, call.data["device_id"], await _caller(hass, call))
            return {"template": json.dumps(template, separators=(",", ":"), allow_nan=False)}
        except WriteValidationError as err:
            raise HomeAssistantError(f"Schedule export rejected: {err.code}") from None

    hass.services.async_register(
        DOMAIN, "apply_schedule", apply,
        schema=vol.Schema({vol.Required("device_id"): _DEVICE_ID,
                           vol.Required("template"): vol.All(str, vol.Length(min=1, max=4096))}),
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(
        DOMAIN, "copy_schedule", copy,
        schema=vol.Schema({vol.Required("source_device_id"): _DEVICE_ID,
                           vol.Required("target_device_id"): _DEVICE_ID}),
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(
        DOMAIN, "export_schedule", export,
        schema=vol.Schema({vol.Required("device_id"): _DEVICE_ID}),
        supports_response=SupportsResponse.ONLY,
    )
