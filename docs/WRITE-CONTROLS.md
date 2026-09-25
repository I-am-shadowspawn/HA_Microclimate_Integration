# Configuration writes — 1.3.2

> **Unofficial, independent project.** This integration and its custom cards are not affiliated with, endorsed by, or supported by Microclimate. Their only connection to Microclimate is that they work with its products. Product names are used solely to identify compatibility. For integration support, use this project’s [GitHub Issues](https://github.com/I-am-shadowspawn/HA_Microclimate_Integration/issues).

This iteration adds editable controls alongside the existing observations. Writes remain enabled by default; raw-pin diagnostics default to disabled. Full raw-response DEBUG logging remains off. The automated validation uses mocked controller traffic and does not dispatch live writes.

## Where to find the controls

Open Settings → Devices & services → Microclimate and select a channel device. Selectors named Configure control mode, Configure output type and Configure timing mode edit the confirmed enums. Number controls edit lower/upper alarm thresholds and Yellow/Red ramp time. The channel card edits schedule setpoints and start times with explicit Save/Cancel; individual schedule number/time entities have been removed. The root controller has four Set season start text controls and a Last configuration write diagnostic.

After the required clean reinstall, existing ID continuity is not guaranteed. New controls have distinct stable unique IDs `<entry_id>_write_<field_key>`. HA assigns their visible entity IDs from the device/control names; use the entity picker rather than constructing IDs. Internal slot field keys remain stable across timing modes. Controls track observed values, including subsequent official-app edits.

| Setting | Yellow | Red, Evo III only | Blue |
|---|---|---|---|
| Control mode | v52 | v82 | v112 |
| Output type | v54 | v84 | Not supported: hardware on/off |
| Timing mode | v53 | v83 | v113 |
| Lower / upper alarms | v49 / v50 | v79 / v80 | v109 / v110, probe profiles only |
| Eight time / setpoint pairs | v32/v33 … v46/v47 | v62/v63 … v76/v77 | v92/v93 … v106/v107 |
| Ramp time (whole minutes) | v48 | v78 | Not supported |
| Root season start dates | v20–v23, shared across channels | Shared | Shared |

Control codes are 0=fixed, 1=heating, 2=cooling. Evo Connect I Blue exposes only fixed. Output codes are 0=pulse, 1=dimming. Timing codes are 0=Constant, 1=Day Night, 2=Multi; Yellow/Red 3=Seasonal, while Blue 3=Periodic and 4=Seasonal.

Day Night makes the first two pairs editable. Multi and Seasonal make all eight pairs editable. Seasonal names identify Season 1–4 day/night; Multi names identify Schedule point 1–8. Constant and Periodic make these pairs unavailable. There is no verified separate Constant target, and v8/v9/v10 Observed Setpoint remain read-only. Periodic interval/duration, device names/clock/unit flags, arbitrary pins and climate setters are outside this release.

## Input rules

- Temperature settings and alarm thresholds: 0–100 °C inclusive, finite numbers. Fixed-control schedule setpoints: 0–100 %. Retained number controls use a 0.1 UI step; card sliders use 0.5 displayed units and exact numeric fields accept decimals; other in-range decimal values are accepted without rounding the request. Native values remain Celsius despite upstream F suffixes; HA may convert displayed temperatures normally. Reversed alarm thresholds are retained and may be edited independently; no undocumented ordering constraint is invented.
- Ramp time: 0–240 whole minutes, inclusive. Yellow on every model and Red on Evo III use enabled Number controls; Blue has no ramp control. Fractions, negatives, non-finite values and values over 240 are rejected.
- Times: manual local clock values 00:00:00–23:59:59, whole seconds, without a supplied timezone. No sunrise/sunset modes. An encoded time preserves the controller's timezone and every trailing opaque field. A plain-seconds value needs agreeing same-channel four-field templates, checked against any reported root timezone; an absent/conflicting/unsupported template blocks that edit.
- Season dates: exactly DD/MM. Calendar validity uses a non-leap year solely for validation; no year is sent. 29/02, 31/04, 00/00 and malformed values are rejected. Season starts must also follow one strictly ordered annual cycle, including season 4 back to next season 1. Distinct dates may cross December/January once, so `09/10, 01/01, 01/06, 01/07` and `01/05, 01/09, 01/01, 01/03` are valid. `01/01, 02/12, 01/04, 01/11` and `20/02, 01/02, 30/06, 20/06` are rejected. `01/13` is invalid; the maintainer corrected that example to `01/03`. Existing unset/invalid observations can remain unknown; writing an unset sentinel is intentionally not offered.

For retained independent controls, automations can use HA's `select.select_option`, `number.set_value` or `text.set_value`. Schedule edits use the card's authenticated batch API or the `apply_schedule`/`copy_schedule` actions, which share the same planner and readback-confirmed job. The read-only `export_schedule` action returns a portable template. See [schedule presets](SCHEDULE-PRESETS.md) and [card API](CARD-API.md). No `time.set_value`, per-point number entities or arbitrary-pin service are exposed.

## Completion, conflicts and recovery

Each operation validates locally, waits for this entry's write lock, fetches a fresh baseline and checks the setting's mode/units/encoding context. If already matching, the result is `confirmed_no_change` with no update. Otherwise it sends exactly one update and confirms using getAll immediately and, if necessary, around 2, 5 and 10 seconds later. The whole operation, including queueing, is bounded by 60 seconds. Requests have explicit connect/read/total timeouts and the outer deadline cancels any remaining work.

An empty HTTP 200 is only an acknowledgement. Confirmation requires the requested pin's value in readback: numeric equivalence for numbers/enums, exact DD/MM for dates and the complete encoded string for times. A clamp or changed encoding is a mismatch. The displayed value always comes from observed data. A timeout may have happened after the server applied the write, so the integration reads back where possible and **never automatically repeats an update**. Rate limits honour bounded Retry-After; updates still are not repeated.

Last configuration write reports the field, outcome and time without credentials. Service errors are translated: rejected, rate limited, mismatch, uncertain, stale context, read failed, unsupported encoding/capability or invalid input. Authentication failures initiate HA reauthentication. If an outcome is uncertain, inspect the latest observed value and the controller before choosing whether to repeat the edit. Unload cancels pending operations; an already dispatched operation may still have applied remotely. No queued operation is replayed on restart.

Polling and writes share one coordinator/session per entry. The I/O lock includes publication, preventing an older poll from overwriting newer readback. Entries have independent locks. There is no atomic compare-and-set in the cloud API: another app can write between baseline, update and readback. Confirmation proves an API observation, not physical execution, persistence after reboot, or exclusivity against other clients.

## Options and diagnostics

Disable **Enable configuration writes** in this entry's options to block new and queued updates; already dispatched requests cannot be recalled. Observations remain available. Missing option values default to enabled. Raw-pin diagnostic entities are registered but disabled by default; enable only the pins needed for troubleshooting. User and integration registry choices remain unchanged on reload. The Reported schedule periods sensor stays enabled and is required for card schedule access. Other diagnostics retain their defaults. Enabling many raw pins can increase recorder/history volume.

Home Assistant's **Download diagnostics** action on the integration entry produces a bounded summary of model/version, safe option flags, polling and write status, and response shape. It omits raw pin names/values, controller name, token, entry ID, URLs and exception messages. Review the file before posting it. For a full raw response, explicitly enable **Log full API responses** and DEBUG logging; those logs may contain controller names and readings and must be reviewed before sharing.

Full response logging requires both the per-entry option and HA DEBUG logging. It covers read/baseline/readback JSON, not credential URLs. Tokens and credential fields are redacted, including URL-encoded occurrences; other names/readings remain visible. Accepted read bodies are bounded to 1 MiB, update acknowledgements to 64 KiB. Oversized responses are rejected, not partially normalized or logged. Both endpoints refuse redirects and use HA's normal TLS session.

## Endpoint contract and evidence limits

Read: `GET https://microclimate.blynk.cc/external/api/getAll?token=…`

Update: `GET https://microclimate.blynk.cc/external/api/update?token=…&vN=value`

The application passes one pin/value and token to aiohttp's query encoder. Time separators are actual NUL characters in memory, encoded once as `%00`; there is no `/data/` insertion or alternative-host fallback.

`fixtures/write_captures.json` contains sanitized, provenance-hashed evidence for v20=`09/02` and v32's plain-seconds → duplicate-seconds/NUL/Europe-London encoding. These prove those captured round trips only. Model/firmware were not recorded in those write logs, so they are not attributed to every model. Mappings and constraints come from the maintainer-confirmed contract; all enabled field families have mocked dispatch/readback acceptance tests. On 24 September 2026 the maintainer confirmed testing of every already-enabled 1.1.0 attribute on Evo II and Evo III. This is recorded as maintainer-confirmed functional evidence, without a supplied new capture or firmware attribution. New ramp controls and season-order rules require their own live acceptance; Evo I writes, persistence, scheduled transitions and soak remain follow-ups in TODO.md.


## Season-order checks and partial configurations

Each season edit substitutes just the requested date into the four root dates and validates the resulting annual cycle. Validation runs before I/O, again against the fresh baseline while holding the write lock, and on a matching readback before reporting confirmation. Equal start dates are rejected because their precedence is undefined. This rule restricts the order to one yearly cycle; permitting one backward step among the first three pairs alone would incorrectly accept some two-year sequences.

Explicit sibling `00/00` values are omitted from order validation so an initial configuration can be populated one date at a time. This does not claim that an unset season is disabled on the hardware. Missing, malformed or otherwise invalid sibling dates block a season edit because a valid order cannot be established. Correct those values on the controller and refresh first; no neighbouring dates are silently repaired. Existing out-of-order valid dates may be repaired by any single edit that produces a valid cycle. Each intermediate configuration must satisfy the rule; whole-calendar atomic replacement is not supported.

Other apps can still change dates after the fresh baseline. If readback reveals an invalid cycle, the action reports a season-order error while retaining all observed values, including any edit already applied remotely. There is no blind rollback. This is a client-side consistency check, not a remote transaction guarantee.

## Editing hours and minutes

The card keeps edits local until Save. Changing hours and minutes several times produces the final desired time in one planned edit, rather than separate writes per UI interaction. Writes still apply sequentially; a time/setpoint pair is not atomic. No debounce or automatic replay is introduced. The old standalone schedule time entities and their `time.set_value` workflow are removed in 1.3.0.
