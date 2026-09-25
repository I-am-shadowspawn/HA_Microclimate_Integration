"""One-shot update transport. No credential-bearing exceptions escape here."""
from dataclasses import dataclass
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone
import json
import re

import aiohttp
from .http_response import read_body

UPDATE_URL = 'https://microclimate.blynk.cc/external/api/update'
MAX_BODY = 64 * 1024


@dataclass(frozen=True)
class UpdateResult:
    outcome: str
    retry_after: float = 0


def retry_after_seconds(value):
    try:
        seconds = float(value)
    except (TypeError, ValueError):
        try:
            seconds = (parsedate_to_datetime(value) - datetime.now(timezone.utc)).total_seconds()
        except (TypeError, ValueError, OverflowError):
            return 0
    return min(60, max(0, seconds)) if seconds == seconds else 0


async def update_pin(token, pin, value, *, session):
    """Caller must resolve the capability allowlist; this is not a public service."""
    if not re.fullmatch(r'v[0-9]+', pin) or not isinstance(value, str) or len(value) > 1024:
        return UpdateResult('rejected')
    try:
        async with session.get(UPDATE_URL, params={'token': token, pin: value},
                               timeout=aiohttp.ClientTimeout(total=20, connect=10, sock_read=15),
                               allow_redirects=False) as response:
            if response.status == 401:
                return UpdateResult('invalid_auth')
            if response.status == 429:
                return UpdateResult('rate_limited', retry_after_seconds(response.headers.get('Retry-After')))
            if response.status not in (200, 400):
                return UpdateResult('uncertain')
            body = await read_body(response, MAX_BODY)
            payload = None
            if body.strip():
                try:
                    payload = json.loads(body)
                except (ValueError, UnicodeError):
                    return UpdateResult('rejected' if response.status == 400 else 'uncertain')
            if isinstance(payload, dict) and payload.get('error') == {'message': 'Invalid token.'}:
                return UpdateResult('invalid_auth')
            if response.status == 400 or isinstance(payload, dict) and 'error' in payload:
                return UpdateResult('rejected')
            return UpdateResult('acknowledged' if response.status == 200 else 'uncertain')
    except (TimeoutError, aiohttp.ClientError, ValueError):
        return UpdateResult('uncertain')
    except Exception:
        return UpdateResult('uncertain')
