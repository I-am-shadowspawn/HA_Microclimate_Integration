"""Bounded, credential-free support diagnostics for a config entry."""

from collections.abc import Mapping
from itertools import islice
import json
import math
import re
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.loader import async_get_integration

from .api_client import redact_response
from .const import CONF_ENABLE_WRITES, CONF_LOG_RAW_RESPONSE, DEFAULT_ENABLE_WRITES, DOMAIN, MODEL_CHANNEL_OPTIONS

MAX_SAMPLED_FIELDS = 256
MAX_EXPORT_BYTES = 4096
_PIN = re.compile(r"v[0-9]+\Z")
_SAFE_NAME = re.compile(r"[A-Za-z][A-Za-z0-9_]{0,63}\Z")
_WRITE_STATUSES = {
    "confirmed", "confirmed_no_change", "uncertain", "cancelled_before_dispatch",
    "invalid_auth", "rejected", "rate_limited", "mismatch", "stale_context",
    "read_failed", "unsupported_capability", "invalid_input",
}


def _response_shape(data: Any) -> dict[str, Any]:
    """Report only a bounded structural sample; never include keys or values."""
    if not isinstance(data, Mapping):
        return {"kind": "unavailable" if data is None else "unexpected_type"}

    kinds = {"number": 0, "text": 0, "unknown": 0, "other": 0}
    sampled_pins = 0
    for key, value in islice(data.items(), MAX_SAMPLED_FIELDS):
        if isinstance(key, str) and _PIN.fullmatch(key):
            sampled_pins += 1
        if value is None:
            kinds["unknown"] += 1
        elif type(value) in (int, float) and math.isfinite(value):
            kinds["number"] += 1
        elif isinstance(value, str):
            kinds["text"] += 1
        else:
            kinds["other"] += 1
    return {
        "kind": "object",
        "field_count": len(data),
        "sampled_fields": min(len(data), MAX_SAMPLED_FIELDS),
        "sample_truncated": len(data) > MAX_SAMPLED_FIELDS,
        "sampled_virtual_pins": sampled_pins,
        "sampled_value_types": kinds,
    }


async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry) -> dict[str, Any]:
    """Produce an HA download without a raw API response or identifying data."""
    coordinator = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    integration = await async_get_integration(hass, DOMAIN)
    model = entry.data.get("model")
    if not isinstance(model, str) or model not in MODEL_CHANNEL_OPTIONS:
        model = "unknown"
    options = entry.options if isinstance(entry.options, Mapping) else {}
    last_write = getattr(coordinator, "last_write", None)
    write_status = last_write.get("status") if isinstance(last_write, Mapping) else None
    if not isinstance(write_status, str) or write_status not in _WRITE_STATUSES:
        write_status = "other" if write_status is not None else None
    failure = getattr(coordinator, "last_exception", None)
    failure_type = type(failure).__name__ if failure is not None else None
    if failure_type is not None and not _SAFE_NAME.fullmatch(failure_type):
        failure_type = "OtherError"
    last_update_success = getattr(coordinator, "last_update_success", None)
    if type(last_update_success) is not bool:
        last_update_success = None

    result = {
        "integration": {"domain": DOMAIN, "version": str(integration.version), "model": model},
        "entry": {
            "token": "[REDACTED]",
            "unique_id": "[REDACTED]",
            "options": {
                CONF_ENABLE_WRITES: options.get(CONF_ENABLE_WRITES, DEFAULT_ENABLE_WRITES) is True,
                CONF_LOG_RAW_RESPONSE: options.get(CONF_LOG_RAW_RESPONSE, False) is True,
            },
            "other_option_count": max(0, len(options) - sum(
                key in options for key in (CONF_ENABLE_WRITES, CONF_LOG_RAW_RESPONSE)
            )),
        },
        "coordinator": {
            "loaded": coordinator is not None,
            "last_update_success": last_update_success,
            "failure_type": failure_type,
            "last_write_status": write_status,
        },
        "response_shape": _response_shape(getattr(coordinator, "data", None)),
    }
    # Reuse the credential redactor as a final guard, even on this allowlisted summary.
    result = redact_response(result, entry.data.get("token"))
    if len(json.dumps(result, ensure_ascii=True).encode("utf-8")) > MAX_EXPORT_BYTES:
        return {"integration": DOMAIN, "diagnostics_error": "summary_too_large"}
    return result
