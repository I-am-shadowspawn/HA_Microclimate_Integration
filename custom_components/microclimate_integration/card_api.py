"""Authenticated WebSocket routing, subscriptions and static card registration."""

from pathlib import Path
from typing import Any

import voluptuous as vol
from homeassistant.components import websocket_api
from homeassistant.components.http import StaticPathConfig
from homeassistant.core import callback
from homeassistant.helpers import device_registry as dr

from .card_model import SCHEMA_VERSION, generation, resolve, snapshot
from .write_contract import WriteValidationError

KEY = "microclimate_card_api"
PREFIX = "microclimate_integration/card/"
from .card_jobs import CardJobs
from .errors import error_message

MAX_SUBSCRIPTIONS = 256
MAX_CONNECTION_SUBSCRIPTIONS = 32


class CardAPI:
    def __init__(self, hass):
        self.hass = hass
        self.manager = CardJobs(hass)
        self.subscriptions: dict[object, Any] = {}

    def subscribe(self, connection, message_id, remove):
        token = object()
        self.subscriptions[token] = connection

        @callback
        def unsubscribe():
            self.subscriptions.pop(token, None)
            remove()

        connection.subscriptions[message_id] = unsubscribe

    async def handle(self, connection, msg, verb):
        user = connection.user
        try:
            if user is None:
                raise WriteValidationError("unauthorized")
            if verb in ("subscribe", "operation") and (
                len(self.subscriptions) >= MAX_SUBSCRIPTIONS
                or sum(c is connection for c in self.subscriptions.values())
                >= MAX_CONNECTION_SUBSCRIPTIONS
            ):
                raise WriteValidationError("subscription_limit")
            if verb == "list":
                devices = []
                for device in dr.async_get(self.hass).devices.values():
                    try:
                        c, channel, resolved = resolve(self.hass, device.id)
                        view = snapshot(self.hass, c, channel, resolved, user)
                    except WriteValidationError:
                        continue
                    devices.append(
                        {k: view[k] for k in ("device_id", "kind", "name", "channel", "model")}
                    )
                connection.send_result(msg["id"], devices)
            elif verb == "subscribe":
                c, channel, device = resolve(self.hass, msg["device_id"])
                snapshot(self.hass, c, channel, device, user)
                attached = None
                remove_coordinator = None

                @callback
                def send(*_):
                    nonlocal attached, remove_coordinator
                    try:
                        current, current_channel, current_device = resolve(
                            self.hass, msg["device_id"]
                        )
                        if current is not attached:
                            if remove_coordinator:
                                remove_coordinator()
                            attached = current
                            remove_coordinator = current.async_add_listener(send)
                        value = snapshot(self.hass, current, current_channel, current_device, user)
                    except WriteValidationError as err:
                        if remove_coordinator:
                            remove_coordinator()
                            remove_coordinator = None
                            attached = None
                        value = {"error": err.code}
                    connection.send_event(msg["id"], value)

                remove_entry = self.hass.bus.async_listen("microclimate_card_entry_changed", send)
                remove_entity = self.hass.bus.async_listen("entity_registry_updated", send)
                remove_device = self.hass.bus.async_listen("device_registry_updated", send)

                @callback
                def unsubscribe():
                    if remove_coordinator:
                        remove_coordinator()
                    remove_entry()
                    remove_entity()
                    remove_device()

                self.subscribe(connection, msg["id"], unsubscribe)
                connection.send_result(msg["id"])
                send()
            elif verb == "request":
                c, channel, device = resolve(self.hass, msg["device_id"])
                snapshot(self.hass, c, channel, device, user)
                self.manager.prune()
                found = next(
                    (
                        job
                        for job in self.manager.jobs.values()
                        if job["device_id"] == device.id
                        and job["user_id"] == user.id
                        and job["request_id"] == msg["request_id"]
                        and job["generation"] == generation(c)
                    ),
                    None,
                )
                if found:
                    self.manager.find_job({"operation_id": found["operation_id"]}, user)
                connection.send_result(
                    msg["id"], {"operation_id": found["operation_id"]} if found else None
                )
            elif verb == "save":
                connection.send_result(msg["id"], await self.manager.save(msg, user))
            else:
                job = self.manager.find_job(msg, user)
                if verb == "stop":
                    job["stop"] = True
                    connection.send_result(msg["id"])
                else:
                    operation = job["operation_id"]

                    @callback
                    def send_job(operation_id):
                        if operation_id != operation:
                            return
                        try:
                            checked = self.manager.find_job(msg, user)
                            value = self.manager.public_job(checked)
                        except WriteValidationError as err:
                            value = {"error": err.code}
                        connection.send_event(msg["id"], value)

                    self.manager.listeners.add(send_job)
                    self.subscribe(
                        connection, msg["id"], lambda: self.manager.listeners.discard(send_job)
                    )
                    connection.send_result(msg["id"])
                    send_job(job["operation_id"])
        except WriteValidationError as err:
            connection.send_error(msg["id"], err.code, error_message(err.code))


async def async_setup_card_api(hass):
    if KEY in hass.data:
        return
    api = CardAPI(hass)
    short_string = vol.All(str, vol.Length(min=1, max=128))
    for verb in ("list", "subscribe", "save", "operation", "stop", "request"):
        schema = {vol.Required("type"): PREFIX + verb}
        if verb in ("subscribe", "save", "request"):
            schema[vol.Required("device_id")] = short_string
        if verb in ("operation", "stop"):
            schema[vol.Required("operation_id")] = short_string
        if verb == "request":
            schema[vol.Required("request_id")] = short_string
        if verb == "save":
            schema.update(
                {
                    vol.Required("schema_version"): int,
                    vol.Required("patch"): dict,
                    vol.Required("runtime_generation"): short_string,
                    vol.Required("base_revision"): short_string,
                    vol.Required("request_id"): short_string,
                }
            )

        async def handler(hass, connection, msg, action=verb):
            await api.handle(connection, msg, action)

        decorated = websocket_api.websocket_command(schema)(websocket_api.async_response(handler))
        websocket_api.async_register_command(hass, decorated)
    await hass.http.async_register_static_paths(
        [
            StaticPathConfig(
                "/microclimate_integration/microclimate-cards.js",
                str(Path(__file__).parent / "frontend" / "microclimate-cards.js"),
                False,
            )
        ]
    )
    hass.data[KEY] = api
