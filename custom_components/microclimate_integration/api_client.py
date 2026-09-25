from typing import Any, Dict
import json
import logging
import math
import re
from urllib.parse import quote, quote_plus

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .readings import DataSnapshot
from .http_response import read_body
from homeassistant.exceptions import ConfigEntryAuthFailed
from .const import CONF_LOG_RAW_RESPONSE
from custom_components.microclimate_integration.const import DOMAIN


class UnauthenticatedError(Exception):
    """Raised when the request is unauthenticated."""
    pass
class EvoDeviceDataError(Exception):
    """Custom exception for errors fetching Evo Device data."""
    pass


_LOGGER = logging.getLogger(__name__)


READ_URL = "https://microclimate.blynk.cc/external/api/getAll"
REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=20, connect=10, sock_read=15)


async def fetch_data(token: str, *, session: aiohttp.ClientSession, log_raw_response: bool = False)->Dict[str,Any]:
    url = READ_URL
    params = {"token": token}

    try:
        async with session.get(url, params=params, timeout=REQUEST_TIMEOUT, allow_redirects=False) as response:
            payload_read = False
            payload_error = None
            if log_raw_response and _LOGGER.isEnabledFor(logging.DEBUG):
                try:
                    data = json.loads(await read_body(response, 1024 * 1024))
                    payload_read = True
                except Exception as err:
                    payload_error = err
                    _LOGGER.debug("Microclimate API response (HTTP %s): JSON body unavailable", response.status)
                else:
                    _LOGGER.debug("Microclimate API response (HTTP %s): %s", response.status,
                                  json.dumps(redact_response(data, token), ensure_ascii=True))
            if response.status == 401:
                raise UnauthenticatedError("Authentication failed: invalid token")
            if response.status not in (200, 400):
                raise EvoDeviceDataError(f"Unexpected response status: {response.status}")
            if payload_error is not None:
                raise payload_error
            if not payload_read:
                data = json.loads(await read_body(response, 1024 * 1024))
            # Blynk documents this exact envelope for an invalid device token.
            # Do not classify all HTTP 400s (e.g. wrong pin) as credential errors.
            if isinstance(data, dict) and data.get("error") == {"message": "Invalid token."}:
                raise UnauthenticatedError("Authentication failed: invalid token")
            if response.status != 200:
                raise EvoDeviceDataError("Unexpected response status: 400")
            return normalize_response(data)
    except (UnauthenticatedError, EvoDeviceDataError):
        raise
    except TimeoutError:
        raise EvoDeviceDataError("Microclimate request timed out") from None
    except aiohttp.ClientError:
        raise EvoDeviceDataError("Microclimate transport or response error") from None
    except ValueError:
        raise EvoDeviceDataError("Invalid Microclimate JSON response") from None
    except Exception:
        # Transport/JSON exceptions can embed the full credential-bearing URL.
        raise EvoDeviceDataError("Unable to fetch Microclimate data") from None


def normalize_response(data):
    """Require an object; unsupported pin values become unknown.

    Preserve strings (including encoded schedules and mislabeled temperatures).
    Typed interpretation belongs to the consuming property.
    """
    if not isinstance(data, dict):
        raise EvoDeviceDataError("Expected a Microclimate JSON object")
    if "error" in data:
        raise EvoDeviceDataError("Microclimate API returned an error")
    return DataSnapshot({
        key: value if (type(value) in (str, int) or type(value) is float and math.isfinite(value)) else None
        for key, value in data.items() if isinstance(key, str)
    })




async def get_evo_device_data(hass: HomeAssistant, config_entry) -> Dict[str, Any]:
    """Fetch using this entry's current credential, never a name lookup."""
    if config_entry is None:
        raise ValueError("Configuration entry is required")
    token = config_entry.data["token"]
    try:
        data = await fetch_data(token, session=async_get_clientsession(hass),
                                log_raw_response=getattr(config_entry, "options", {}).get(CONF_LOG_RAW_RESPONSE) is True)
        return data
    except UnauthenticatedError:
        raise ConfigEntryAuthFailed("Authentication error for Microclimate") from None
    except Exception:
        raise EvoDeviceDataError("Failed to fetch Microclimate data") from None

def redact_response(value, token):
    """Retain complete JSON structure while removing credential fields and this token."""
    def redact_text(text):
        if token:
            variants = {token, quote(token, safe=""), quote_plus(token, safe="")}
            for variant in sorted(variants, key=len, reverse=True):
                pattern = re.sub(r"%[0-9A-Fa-f]{2}", lambda match: f"(?i:{match.group()})", re.escape(variant))
                text = re.sub(pattern, "[REDACTED]", text)
        return text

    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            normalized = str(key).lower().replace("-", "_")
            sensitive = normalized in {"token", "api_token", "access_token", "refresh_token",
                                       "api_key", "apikey", "authorization", "password", "secret"}
            sensitive = sensitive or normalized.endswith(("_token", "_secret", "_password"))
            result[redact_text(str(key))] = "[REDACTED]" if sensitive else redact_response(item, token)
        return result
    if isinstance(value, list):
        return [redact_response(item, token) for item in value]
    return redact_text(value) if isinstance(value, str) else value
