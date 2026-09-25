# Card API schema 1

> **Unofficial, independent project.** This integration and its custom cards are not affiliated with, endorsed by, or supported by Microclimate. Their only connection to Microclimate is that they work with its products. Product names are used solely to identify compatibility. For integration support, use this project’s [GitHub Issues](https://github.com/I-am-shadowspawn/HA_Microclimate_Integration/issues).

Authenticated HA WebSocket commands under `microclimate_integration/card/`:

| Command | Parameters beyond HA id/type | Result |
|---|---|---|
| list | none | Authorized root/channel device descriptors |
| subscribe | device_id | Subscription ack then permission-filtered snapshots |
| save | schema_version=1, device_id, runtime_generation, base_revision, request_id (UUID), patch | operation_id, promptly; observe job separately |
| operation | operation_id | Subscription ack then monotonically sequenced job events |
| stop | operation_id | Ack; stop unsent steps, no rollback |
| request | device_id, request_id | Retained operation_id or null; read-only lost-ack recovery |

Unsubscribe through HA `unsubscribe_events`. Subscriptions rebind after integration reload. Snapshot events include safe typed fields, constraints, native values, validity, entity bindings, observations, online/write/busy status and opaque settings revision/generation. Snapshot publication uses the existing coordinator. Device identity is registry-bound; friendly names are not keys. Root dates are readonly in channel snapshots.

Save patch variants:

```json
{"kind":"mode","fields":{"Yellow_control_pin":"heating"}}
```

```json
{"kind":"channel","fields":{"Yellow_ramp_time":9},"schedule":{"mode":"Multi","points":[{"seconds":25200,"target_native":27},{"seconds":68400,"target_native":22}]}}
```

```json
{"kind":"season_dates","fields":{"season_1_start_pin":"09/10"}}
```

Canonical keys derive from Python write definitions. The browser cannot supply pins, URLs, tokens or write order. Schedule modes are exact `Day Night`, `Multi`, `Seasonal`; 2, 2–8, 8 points respectively. `draft_id`/`source_slot` are optional untrusted editing metadata; ordering optimization is verified by unchanged retained values against the fresh baseline. Wire numbers are native Celsius/%; seconds and ramp minutes are integral. Root and channel patches cannot be mixed; one enum per mode Save.

The pure planner validates the full desired state and preserved time templates before dispatch. Single insertions shift backwards, single deletions promote forwards, general changes use the complete frozen final map. Populated pairs use target-then-time; cleared pairs use midnight-then-zero. Final prefix checks do not incorrectly reject necessary transient intermediate duplicates. Date permutations are searched without scratch values.

Server READ/CONTROL permissions, disabled controls, entry write option, mode, generation and settings revisions are checked independently of the card. Read-only request IDs and job history are scoped to the initiating user. Jobs on one entry share the ordinary write lock and I/O lock; only one active card job is allowed. Calls are never parallelized into the vendor API. Current readings are excluded from draft revisions; editable values/time suffixes are included. Credential/model changes rotate an opaque generation.

Same retained user/entry/request UUID and patch digest returns the same operation; changed payload/device/generation rejects reuse. Completed history is bounded to 20 jobs/entry and one hour. Jobs are not persisted. Result statuses: pending/running/succeeded/failed/partial/uncertain/stopped. Per-field statuses: not-sent/pending/confirmed/failed/uncertain. No-op fields are omitted from dispatch/progress totals. No update retries/compensating writes are performed. API readback is confirmation of reported configuration, not evidence of physical execution or durable storage.

Frontend uses HA's `hass` connection/setConfig/custom-element interfaces for the pinned HA release. The module and dependencies are bundled locally. References: [custom card interface](https://developers.home-assistant.io/docs/frontend/custom-ui/custom-card/), [WebSocket extension](https://developers.home-assistant.io/docs/frontend/extending/websocket-api/).

## Compact schedule authorization (1.3.0)

Schema 1 is retained because field keys/types and patch contracts are unchanged. `fields[].entity_id` identifies an authorization anchor, not necessarily a distinct control entity. All indexed fields in one channel bind to that channel's enabled Reported schedule periods sensor, resolved from its registry unique ID and verified against entry/device identity. `authorization_scope` is `channel_schedule` for indexed fields and `entity` otherwise. The frontend uses field keys, not entity IDs, to identify inputs.

READ is required for projection; READ and CONTROL are required for writes, status and recovery. Disabled/missing/misbound anchors fail closed; hidden anchors remain usable. Permission checks run before each write step. Root dates and ordinary mode/ramp/alarm controls retain their individual authorization anchors. The channel schedule sensor is not directly writable and no generic pin service is added. No per-point entities or compatibility exposure mode are registered.
