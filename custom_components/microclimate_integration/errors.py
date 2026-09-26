"""Safe error categories shared by read/setup, jobs and WebSocket replies."""
from homeassistant.helpers.update_coordinator import UpdateFailed
from .const import DOMAIN

MESSAGES = {
    'unavailable': 'Controller service unavailable. Check connectivity and try again later.',
    'invalid_payload': 'The service returned unusable data. Refresh later; if it persists, report sanitized diagnostics.',
    'rate_limited': 'The service is throttling requests. Wait before trying again; check observed settings before repeating a write.',
    'invalid_auth': 'The token was rejected. Reauthenticate this integration.',
    'operation_timeout': 'The operation deadline expired. Review confirmed changes and controller state before trying again.',
    'job_limit': 'Too many controller operations are active. Wait for an existing operation to finish.',
    'subscription_limit': 'Too many live card subscriptions. Close unused dashboards and reconnect.',
    'busy': 'This controller is applying a change. Wait for it to finish.',
    'conflict': 'Controller settings changed. Refresh the card and review your draft before saving.',
    'control_denied': 'Control permission was revoked or is unavailable. Restore permission before saving.',
    'operation_unavailable': 'This operation expired or the integration reloaded. Refresh the observed controller state; do not replay automatically.',
    'writes_unavailable': 'Writes or current observations are unavailable. Check integration options and connectivity.',
}


def error_message(code: str) -> str:
    return MESSAGES.get(code, code.replace('_', ' ') + '. Refresh observed settings before trying again.')


class ReadUpdateFailed(UpdateFailed):
    """Retain a whitelisted category without carrying transport exception details."""
    def __init__(self, code: str):
        self.code = code if code in ('unavailable', 'invalid_payload', 'rate_limited') else 'unavailable'
        super().__init__(error_message(self.code), translation_domain=DOMAIN, translation_key=self.code)
