# Schedule presets and automation actions — 1.4.0

> **Unofficial, independent project.** This integration and its custom cards are not affiliated with, endorsed by, or supported by Microclimate. Their only connection to Microclimate is that they work with its products. For support, use [GitHub Issues](https://github.com/I-am-shadowspawn/HA_Microclimate_Integration/issues).

The channel card can **Download preset** from a complete Day Night, Multi or Seasonal schedule. In Edit mode, **Import preset** loads a JSON file into the local draft. Review the changed fields and press Save; import alone sends no controller update. To copy between cards, download from one channel and import on another. Preset files can be kept as named templates outside Home Assistant. The integration does not store a preset library or create extra entities.

The file contains only `format`, `mode`, `unit` and `points`. Time is whole seconds from local midnight (0–86399); `target_native` is 0–100 Celsius or percent according to `unit`. It contains no device ID, token, pin, controller name, timezone or root season dates. Never change `unit` to force an incompatible import: a 25% fixed-output target is not 25°C. HA Fahrenheit display does not change the file's native Celsius values.

```json
{"format":"microclimate.schedule.v1","mode":"Multi","unit":"celsius","points":[{"seconds":25200,"target_native":27},{"seconds":68400,"target_native":22}]}
```

The destination must already report the same timing mode and native unit. Day Night requires two points, Seasonal eight, and Multi 2–8 consecutive chronological points. Shared root season dates, control mode, output type, ramp time and alarm thresholds are never copied. Source and destination may be different confirmed model/channel profiles when their current modes and units agree. The destination's own time encoding is preserved by the existing planner; missing or incompatible encoding blocks the action. Constant and Periodic remain unsupported for schedule export/import.

Home Assistant also registers three actions under `microclimate_integration`:

| Action | Data | Result |
|---|---|---|
| `export_schedule` | `device_id` (source channel) | Read-only `template` JSON response; requires `response_variable` or `return_response=True` |
| `apply_schedule` | `device_id` (target channel), `template` JSON string | Apply a saved preset |
| `copy_schedule` | `source_device_id`, `target_device_id` | Export source and apply to target in one action |

Example automation action:

```yaml
- action: microclimate_integration.copy_schedule
  data:
    source_device_id: SOURCE_CHANNEL_DEVICE_ID
    target_device_id: TARGET_CHANNEL_DEVICE_ID
  response_variable: schedule_result
```

For `apply_schedule`, provide the exact exported JSON string as `template`. When a response is requested, apply/copy return `operation_id`, `status`, `confirmed`, `total` and `reason`. Inspect `status == "succeeded"` before treating the automation as complete. Without a response variable, partial/failed/uncertain outcomes raise an HA action error with the operation ID and confirmed count. HA automations without a named user run in HA's trusted system context; named users retain entity-level permissions. Export/copy require READ access to the complete source schedule; apply/copy require READ and CONTROL access to the destination's enabled Reported schedule periods sensor. The entry's **Enable configuration writes** option must be on.

All writes use the existing single-entry lock, fresh baseline, sequential pin plan, per-pin readback and final confirmation. A multi-pin update is not atomic. If one step fails, later steps are not sent; earlier confirmed changes remain. There is no automatic retry, rollback or persistence/reboot guarantee. Check the returned status and current controller settings before any new action. Export reads the current HA observation; it does not fetch a fresh source snapshot, so wait for a normal refresh when an external app just changed the source.
