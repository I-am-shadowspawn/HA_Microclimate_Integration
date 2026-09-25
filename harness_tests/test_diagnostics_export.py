"""HA downloadable diagnostics expose useful structure without raw values."""

import json
from urllib.parse import quote
from unittest.mock import patch

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.microclimate_integration.api_client import redact_response
from custom_components.microclimate_integration.const import DOMAIN
from custom_components.microclimate_integration.diagnostics import (
    MAX_EXPORT_BYTES,
    MAX_SAMPLED_FIELDS,
    async_get_config_entry_diagnostics,
)


async def test_download_redacts_and_bounds_nested_response(hass):
    token = "private+/token"
    secret = "private controller name"
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={"model": "Evo Connect 2", "evo_device": secret, "token": token},
        options={"enable_writes": True, "future_option": {"api_key": "another secret"}},
    )
    entry.add_to_hass(hass)
    data = {f"v{index}": index for index in range(1000)}
    data.update({"nested": {"token": "another secret", "url": quote(token, safe="")},
                 "opaque": [secret, token, float("nan")]})
    with patch("custom_components.microclimate_integration.api_client.fetch_data", return_value=data):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        report = await async_get_config_entry_diagnostics(hass, entry)
    encoded = json.dumps(report)
    assert len(encoded.encode()) <= MAX_EXPORT_BYTES
    for sensitive in (token, quote(token, safe=""), secret, "another secret", entry.entry_id):
        assert sensitive not in encoded
    assert report["entry"]["token"] == "[REDACTED]"
    assert report["entry"]["options"] == {"enable_writes": True, "log_raw_response": False}
    assert report["entry"]["other_option_count"] == 1
    assert report["integration"]["model"] == "Evo Connect 2"
    assert report["integration"]["version"] == "1.3.1"
    shape = report["response_shape"]
    assert shape["field_count"] == len(data)
    assert shape["sampled_fields"] == MAX_SAMPLED_FIELDS
    assert shape["sample_truncated"] is True
    assert shape["sampled_virtual_pins"] == MAX_SAMPLED_FIELDS
    assert report["coordinator"]["last_update_success"] is True


async def test_download_handles_unloaded_and_malformed_state(hass):
    token = "token with spaces"
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={"model": [token], "evo_device": "name", "token": token},
        options={"enable_writes": False, "unknown": [token, {"authorization": "secret"}]},
    )
    entry.add_to_hass(hass)
    unloaded = await async_get_config_entry_diagnostics(hass, entry)
    assert unloaded["integration"]["model"] == "unknown"
    assert unloaded["coordinator"]["loaded"] is False
    assert unloaded["response_shape"]["kind"] == "unavailable"
    assert token not in json.dumps(unloaded)

    class FailedCoordinator:
        data = [token, {"api_key": "secret"}]
        last_update_success = "malformed"
        last_exception = ValueError(f"https://host/?token={quote(token, safe='')}")
        last_write = {"status": {"nested": token}}

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = FailedCoordinator()
    malformed = await async_get_config_entry_diagnostics(hass, entry)
    assert malformed["response_shape"]["kind"] == "unexpected_type"
    assert malformed["coordinator"] == {
        "loaded": True, "last_update_success": None,
        "failure_type": "ValueError", "last_write_status": "other",
    }
    assert token not in json.dumps(malformed)


def test_shared_redactor_handles_nested_encoded_credentials():
    token = "secret+/ token"
    value = {"connection": {"url": f"https://host/?token={quote(token, safe='')}",
                            "API-TOKEN": "different secret"},
             "items": [token, {"authorization": "Bearer different secret"}]}
    redacted = redact_response(value, token)
    encoded = json.dumps(redacted)
    for secret in (token, quote(token, safe=""), "different secret"):
        assert secret not in encoded
    assert redacted["connection"]["API-TOKEN"] == "[REDACTED]"
    assert redacted["items"][0] == "[REDACTED]"
