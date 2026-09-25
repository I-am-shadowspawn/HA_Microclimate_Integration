"""Onboarding and credential recovery for Microclimate."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from . import api_client
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import MODEL_OPTIONS, DEFAULT_MODEL
from .const import DOMAIN, CONF_LOG_RAW_RESPONSE, CONF_ENABLE_WRITES, DEFAULT_ENABLE_WRITES
from .identity import token_identity


class MicroclimateConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Validate credentials before creating or updating an entry."""

    VERSION = 1
    DOMAIN = DOMAIN

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return MicroclimateOptionsFlow()

    def _duplicate(self, token, entry=None):
        identity = token_identity(token)
        return any(
            (entry is None or other.entry_id != entry.entry_id)
            and (other.data.get("token") == token or other.unique_id == identity)
            for other in self._async_current_entries()
        )

    async def _validate_token(self, token):
        try:
            await api_client.fetch_data(token, session=async_get_clientsession(self.hass))
        except api_client.UnauthenticatedError:
            return "invalid_auth"
        except (api_client.EvoDeviceDataError, TimeoutError):
            return "cannot_connect"
        except Exception:
            # Never surface transport exception URLs or response bodies in UI/logs.
            return "cannot_connect"
        return None

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            data = {**user_input}
            data.setdefault("model", DEFAULT_MODEL)
            if not all(isinstance(data.get(key), str) and data[key].strip()
                       for key in ("evo_device", "token", "model")):
                errors["base"] = "required"
            elif data["model"] not in MODEL_OPTIONS:
                errors["model"] = "invalid_model"
            elif self._duplicate(data["token"]):
                return self.async_abort(reason="already_configured")
            elif error := await self._validate_token(data["token"]):
                errors["base"] = error
            else:
                # Recheck after I/O so concurrent onboarding cannot create duplicates.
                if self._duplicate(data["token"]):
                    return self.async_abort(reason="already_configured")
                await self.async_set_unique_id(token_identity(data["token"]))
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"Microclimate Evo Device: {data['evo_device']}",
                    data={key: data[key] for key in ("evo_device", "token", "model")},
                )
        return self.async_show_form(step_id="user", data_schema=self._get_data_schema(), errors=errors)

    async def async_step_reauth(self, entry_data):
        """HA initiates this after a coordinator authentication failure."""
        self._get_reauth_entry()  # Bind recovery to the entry in the HA context.
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input=None):
        return await self._credential_step("reauth_confirm", self._get_reauth_entry(), user_input)

    async def async_step_reconfigure(self, user_input=None):
        return await self._credential_step("reconfigure", self._get_reconfigure_entry(), user_input)

    async def _credential_step(self, step, entry, user_input):
        errors = {}
        if user_input is not None:
            token = user_input.get("token", "")
            name = user_input.get("evo_device", entry.data["evo_device"])
            if not isinstance(token, str) or not token.strip() or not isinstance(name, str) or not name.strip():
                errors["base"] = "required"
            elif self._duplicate(token, entry):
                errors["base"] = "already_configured"
            elif error := await self._validate_token(token):
                errors["base"] = error
            elif self._duplicate(token, entry):
                errors["base"] = "already_configured"
            else:
                # No entry/registry mutation until validation has succeeded.
                await self.async_set_unique_id(token_identity(token))
                return self.async_update_reload_and_abort(
                    entry, unique_id=token_identity(token),
                    title=f"Microclimate Evo Device: {name}",
                    data_updates={"evo_device": name, "token": token},
                )
        fields = {vol.Required("token"): str}
        if step == "reconfigure":
            fields = {vol.Required("evo_device", default=entry.data["evo_device"]): str, **fields}
        return self.async_show_form(step_id=step, errors=errors, data_schema=vol.Schema(fields))

    def _get_data_schema(self):
        if not MODEL_OPTIONS:
            raise vol.Invalid("No valid models available.")
        return vol.Schema({
            vol.Required("evo_device"): str,
            vol.Required("token"): str,
            vol.Required("model", default=DEFAULT_MODEL): vol.In(MODEL_OPTIONS),
        })


class MicroclimateOptionsFlow(config_entries.OptionsFlow):
    """Per-entry diagnostic logging; read at the next polling request."""

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data={**self.config_entry.options,
                CONF_LOG_RAW_RESPONSE: user_input.get(CONF_LOG_RAW_RESPONSE, self.config_entry.options.get(CONF_LOG_RAW_RESPONSE, False)),
                CONF_ENABLE_WRITES: user_input.get(CONF_ENABLE_WRITES, self.config_entry.options.get(CONF_ENABLE_WRITES, DEFAULT_ENABLE_WRITES))})
        return self.async_show_form(step_id="init", data_schema=vol.Schema({
            vol.Required(CONF_ENABLE_WRITES,
                         default=self.config_entry.options.get(CONF_ENABLE_WRITES, DEFAULT_ENABLE_WRITES)): bool,
            vol.Required(CONF_LOG_RAW_RESPONSE,
                         default=self.config_entry.options.get(CONF_LOG_RAW_RESPONSE, False)): bool,
        }))
