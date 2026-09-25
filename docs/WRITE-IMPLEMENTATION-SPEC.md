# Microclimate HA writes — finalized unattended implementation plan

> **Unofficial, independent project.** This integration and its custom cards are not affiliated with, endorsed by, or supported by Microclimate. Their only connection to Microclimate is that they work with its products. Product names are used solely to identify compatibility. For integration support, use this project’s [GitHub Issues](https://github.com/I-am-shadowspawn/HA_Microclimate_Integration/issues).

**Release specification for candidate 1.1.0.** Final execution status is maintained in outputs/microclimate_write_implementation_plan.md.

## 1. Objective and execution scope

Implement read/write HA controls for Control Mode, Output Type, Timing Type, configured schedule setpoints, scheduled start times, alarm thresholds and root season starts. Controls are **editable by default for this iteration**. Diagnostic entities are **enabled by default temporarily**. Retain all existing read-only entities, IDs, channel/root grouping and the shared polling/session architecture.

Work in `work/microclimate-test` under the current Codex workspace. Keep the original repository untouched. An instruction to implement this plan authorizes local code, tests, documentation and packages; it does not authorize deployment to live HA or unattended physical controller experiments. Offline tests must not read device-token files or call the live update endpoint.

Proposed release: **1.1.0**, the first write-enabled development candidate. Preserve all 1.0.x archives.

## 2. Resolved contract and implementation decisions

| Area | Final rule |
|---|---|
| Read endpoint | `https://microclimate.blynk.cc/external/api/getAll` |
| Write endpoint | `https://microclimate.blynk.cc/external/api/update` |
| Method/auth | GET; query parameters `token`, plus exactly one whitelisted `vN=value` for updates. No `/data/` insertion and no blynk.cloud fallback. |
| Numeric settings | Temperature setpoints, alarm thresholds and fixed-output percentage setpoints: finite values **0–100 inclusive**. Use **0.1 as the HA UI step** (implementation choice, not a claimed vendor constraint); accept finite decimal values within the range without silently rounding/clamping. |
| Scheduled start | Manual local wall-clock **00:00:00–23:59:59**, whole seconds. No solar modes or timezone conversion. |
| Season starts | Exact **DD/MM**, valid in a non-leap calendar. Validate using a fixed non-leap reference year solely for validation. Reject `29/02`, `31/04`, `00/00`, zero components, year-bearing dates and malformed strings before any update. |
| Setpoint scope | All confirmed schedule setpoint pins. **v8/v9/v10 remain read-only Observed Setpoint.** No separate Constant target pin is known, so do not invent one or repurpose slot 1. |
| Write default | `enable_writes=True` when no stored preference exists. Allow the user to turn writes off; honour an explicit stored false value. No additional opt-in step for this iteration. |
| Diagnostic default | Register diagnostic/raw entities enabled by default. Re-enable only this integration's previously integration-disabled diagnostic entries; preserve entities explicitly disabled by the user. No token/secret fields are exposed. |
| Full response logging | Remains a separate existing option and is not automatically turned on by enabling diagnostic entities. |
| UI | Select controls for modes; Number controls for targets/thresholds; Time controls for schedule clocks; Text controls for recurring DD/MM season dates (HA Date controls require a year). |
| Exclusions | Ramp edits, periodic interval/duration edits, names, unit flags, controller clock, arbitrary pin services, batch schedule editing and writable climate/observed-target entities are outside this request. |

The UI step is deliberately separate from server validation: do not claim the controller accepts only tenths or compare rounded display values to establish write success. Readback comparison uses the original numeric response, including suffix handling where necessary.

## 3. Evidence and remaining uncertainty

### Confirmed date write

Capture `20260923T163151Z-3x_viumy` reports v20 changing from `00/00` to `09/02`, HTTP 200 acknowledgement and three matching getAll samples. Both operations use microclimate.blynk.cc. Model/firmware were labelled unknown.

### Confirmed scheduled write

Inspected the local folder:

`/home/simon/Documents/Codex/2026-09-22/in-app-browser-context-source-ambient/work/20260923T222243Z-n2x2lwed`

- Target: v32; baseline value: plain string `7200`.
- Sent value: `7200\u00007200\u0000Europe/London\u00000` in JSON notation.
- The decoded value contains **three actual NUL characters** and has length 25. It contains no literal backslash-x00 or backslash-u0000 sequences.
- Update returns HTTP 200 with no JSON payload; all **five** subsequent readbacks match the complete requested string exactly.
- Baseline v34 already has the same four-field clock structure and timezone; root v27 also reports Europe/London.
- Model/firmware were labelled unknown. This proves the observed transport/string round trip; it is not independent evidence of every pin, model, physical transition or reboot persistence.

The attached `evo_probe2.py` also establishes URL encoding, redirect blocking, baseline/readback capture and no automatic update retry. Adapt those principles to asynchronous HA code rather than embedding its urllib/certifi implementation.

Blynk's documented endpoint accepts a string value and applies datastream type/bounds; a successful acknowledgement still needs readback to detect rejection, clamping or a different stored value. Reference: [Blynk Update Datastream Value](https://docs.blynk.io/en/blynk.cloud/device-https-api/update-datastream-value).

The other requested fields are covered by the maintainer-confirmed pin/capability contract and the common update API. Implement them for this iteration without claiming each is hardware-write-tested. Record that distinction in the release evidence. No new physical tests are prerequisites for completing the offline implementation.

## 4. Writable field matrix

Derive pin addresses from the canonical schema; platform modules must not maintain independent pin tables.

| Setting | Yellow | Red — Evo III only | Blue | Control and applicability |
|---|---|---|---|---|
| Control Mode | v52 | v82 | v112 | Select: 0 fixed, 1 heating, 2 cooling; thermal options only on probe-capable profiles. Evo I Blue is fixed-only: do not offer unsupported thermal choices. |
| Output Type | v54 | v84 | None | Select: 0 pulse, 1 dimming. Blue is on/off; v114 must not become writable pulse/dimming. |
| Timing Type | v53 | v83 | v113 | Yellow/Red: 0 Constant, 1 Day Night, 2 Multi, 3 Seasonal. Blue: 0 Constant, 1 Day Night, 2 Multi, 3 Periodic, 4 Seasonal. |
| Schedule setpoints | v33/35/37/39/41/43/45/47 | v63/65/67/69/71/73/75/77 | v93/95/97/99/101/103/105/107 | Number, 0–100. Native °C in heating/cooling; % in fixed-output mode. |
| Schedule starts | v32/34/36/38/40/42/44/46 | v62/64/66/68/70/72/74/76 | v92/94/96/98/100/102/104/106 | Time, second precision, encoded using the rules below. |
| Lower/upper alarm | v49/v50 | v79/v80 | v109/v110 for probe-capable profiles | Number, 0–100°C. Do not enforce lower < upper: 100/45 is a maintainer-confirmed displayed configuration. |
| Season starts | Root v20/v21/v22/v23 | Same root set | Same root set | Four root-owned DD/MM Text controls; not duplicated on channels. |

Day Night permits schedule slots 1–2. Multi and Seasonal permit all eight. Constant and Periodic do not expose these clock/setpoint edits. Likely-unused midnight/zero Multi pairs remain editable so users can populate them. No enable/disable toggle is invented.

Keep the existing read-only sensors. Add write controls with new, stable, physical-slot/field IDs in their appropriate HA domains; do not migrate sensor entities into number/time/select/text entities. Use clear names such as “Set season 1 day temperature” or “Configure timing mode”. Mode changes may update friendly names and applicability, but never identity.

## 5. Exact serializers and comparators

### Schedule time

1. Obtain a fresh baseline while holding the write operation's serialization lock. The target pin must exist.
2. Convert the requested naive local time to integer seconds `s` in 0–86399. Reject timezone-bearing times, fractional seconds and unsupported tokens.
3. For an existing encoded value with duplicated numeric clock fields, replace fields 0 and 1 with decimal `s`. Preserve field 2 (reported timezone) and every remaining field, including empty/trailing fields, exactly. Do not interpret opaque suffixes or copy another slot's arbitrary flags.
4. For a **plain seconds** baseline, support the exact expansion demonstrated by v32: `s + NUL + s + NUL + timezone + NUL + "0"`. Derive the timezone only from agreeing valid same-channel four-field clock samples with suffix `0`; cross-check root v27's reported timezone when present. Require a recognized, unambiguous timezone. Do not silently use HA's timezone or hard-code Europe/London for every installation.
5. If no safe template exists, time writing for that operation fails with a clear encoding/context error; other write categories continue to function. Preserve the original snapshot. Unknown/malformed encodings must not be guessed into the four-field format.
6. Join using actual `\x00` characters in memory and let aiohttp encode query parameters once (`%00` on the wire). A literal string containing `\\x00` is not the same value.
7. Readback must match the full expected encoded string. Check both leading fields and preserved suffix, not just the displayed HH:MM value.

This decision supports the supplied plain→encoded successful example without inventing a default timezone or discarding undocumented suffixes. A future response with unequal leading fields or a different unsupported format must be rejected for editing, not silently overwritten.

### Other values

- Enums: exact integral wire codes from the channel table; reject booleans/unknown options.
- Numeric settings: finite 0–100 inclusive, minimal decimal wire string, no suffix added. Compare raw readback numerically (using Decimal or equivalent), stripping only the established Microclimate C/F label while retaining the upstream Celsius number. Never compare a display-rounded temperature to claim exact application.
- Dates: zero-padded exact DD/MM, validated against a non-leap reference calendar. Send and compare the exact string. Existing observed `00/00` or `29/02` data may remain visible/read-only; the new write validation must not erase or rewrite it automatically.
- No automatic writes to neighbouring fields, no implicit mode change, no date reordering, no client clamping and no rollback/batch-atomicity claim.

## 6. Runtime architecture

### Authoritative write contracts

Add `WriteDefinition` metadata describing category, model/channel capability, source pin role, permitted mode/control context, validators, encoder and comparator. Use a single allowlist shared by UI availability and the service-side write manager. Block observed v8/v9/v10, unsupported Blue capabilities and arbitrary caller-supplied pins at the manager boundary.

### Shared transport and coordination

Reuse HA's aiohttp session, verified TLS and explicit timeout policy. Do not import the standalone script's blocking urllib/time.sleep or add its certifi workaround to HA. Keep separate read/write endpoint constants even though both use the same confirmed server. Set `allow_redirects=False` for credential-bearing calls; never forward tokens to another host or automatically try another endpoint.

Maintain one polling coordinator per entry, with normalized DataSnapshot values and `always_update=False`. Add a per-entry write queue/operation lock plus a documented I/O lock used by polling. Lock order: write-operation lock → I/O lock; coordinator reads acquire only I/O lock. Never request a coordinator refresh while holding a lock it needs. Use request generations/sequence checks so a slow old poll cannot overwrite a newer readback. Independent entries remain concurrent.

Read current token, options and model at dispatch. A queued command must recheck write-disabled state, capability and fresh mode/control context. Do not reuse stale credentials after reauth. Unload cancels queued/unsent work; already-dispatched updates may have applied and must be reported uncertain if interrupted. Do not replay pending commands after restart.

### Single-pin operation lifecycle

1. Resolve the whitelisted field; validate input and current edit permission.
2. Capture the invocation's semantic context (mode/control/unit/slot meaning), then serialize through the per-entry operation lock.
3. Fetch a fresh baseline. On read/auth failure, do not write.
4. Compare relevant context with the invocation. If an official-app or preceding command changed units/mode/applicability, reject the stale command rather than reinterpret it. Preserve unrelated naturally changing temperatures/clock/output.
5. Serialize from the fresh snapshot. If already matching, return confirmed-no-change without an update request.
6. Issue **one** update GET. Success can be HTTP 200 with an empty body. A JSON error envelope is a rejection even on 200. Auth failure triggers normal HA reauthentication; other 400 responses, 429, 5xx and transport errors are distinguished without exposing credential URLs.
7. Read back immediately; if necessary perform bounded follow-up reads around 2, 5 and 10 seconds after acknowledgement. Initial total operation deadline: 60 seconds; clamp every request/wait to the remaining deadline. Readback attempts may be retried; **the update is never automatically retried**.
8. Also read back after an uncertain transport outcome where feasible, since the update may have applied. Honour a bounded Retry-After before subsequent requests after rate limiting; never sleep beyond the operation deadline or resend the update.
9. Publish valid snapshots through the existing coordinator. Confirm only matching values. Server clamping/reformatting that violates the field comparator becomes mismatch, with actual observed state shown. Unresolved transport/readback becomes uncertain. No optimistic state overwrite.
10. Service calls complete with a translated, concise result/error. A compact root diagnostic may record last field, status, time and error category; never tokens, full URLs or full response bodies by default.

External application writes cannot be made atomic with this API. Document that limitation; fresh reads/context checks and readback reduce it but do not eliminate it.

## 7. HA platforms and temporary defaults

Add `select.py`, `number.py`, `time.py`, `text.py` plus shared entity/runtime helpers; extend setup/unload PLATFORMS. Use the installed pinned HA APIs. No per-entity HTTP or polling.

- Controls are registered enabled and editable immediately when applicable, data is usable and `enable_writes` has not explicitly been set false.
- The write switch is an optional user disable mechanism, not a new opt-in gate. Existing entries with no stored flag use true for this iteration.
- Existing read-only entities remain available regardless of that preference. Updating options preserves existing raw-response logging choices.
- Diagnostic and raw entities default enabled. On this version's initial setup, clear only `RegistryEntryDisabler.INTEGRATION` for this integration's diagnostic entries; never clear USER-disabled entries or touch another integration. This is an enable-default adjustment, not an ID migration.
- Implement defaults as named constants so a later release can reverse the temporary policy explicitly. Document increased diagnostic entity/history volume.
- Controls retain observed values, not requested optimistic values. Time/number values and units must track confirmed control mode. Do not support a temperature request using percentage context or vice versa.
- Root DD/MM text controls reject invalid calendar dates locally; no native Date entity with a fake year.
- Add clear translations for disabled-by-option, unsupported capability, stale context, invalid range/date/time, rejected, rate-limited, mismatch and uncertain outcomes.

## 8. Ordered unattended work plan

| Phase | Implement | Required result |
|---|---|---|
| P0 — baseline/evidence | Record 1.0.9 baseline; sanitize the v20 and v32 successful captures into fixtures with provenance/hashes. Do not copy tokens/URLs with query credentials. | Working reference fixtures distinguish transport confirmation from physical/model coverage. |
| P1 — contracts | Add capability allowlist, numeric/date/time validators, serializers and field-aware readback comparators, derived from const.py. | Table-driven tests cover every requested field and rejected capability. No guessed Constant target. |
| P2 — transport | Add one-shot asynchronous update transport using the confirmed server; bounded bodies, no redirects, categorized errors and credential redaction. | Empty-200 update fixture succeeds; rejection/uncertain cases are represented correctly. |
| P3 — write manager | Add queue/locks, fresh baseline/context checks, readback confirmation/deadline, coordinator publication and lifecycle cleanup. | No deadlock, double submission, stale overwrite or orphan task in concurrency/cancellation tests. |
| P4 — entities/defaults | Add controls and diagnostics, preserve existing sensors/IDs, default writes/diagnostics on, respect explicit user disable choices. | Real HA setup tests show correct controls and devices for all three profiles; state comes from readback. |
| P5 — regression | Run targeted tests, then both pinned full matrix modes, network blocked. Fix new failures and rerun affected checks. | Passing original read-only behaviours plus write acceptance tests; no skipped/xfail workaround for incomplete requested functionality. |
| P6 — delivery | Update manifest to 1.1.0, README, changelog, TODO and scope/limitations. Build deterministic install/development ZIPs, hashes, patch and test report. | Reviewable artifacts; prior archives preserved; no live deployment or physical write performed. |

Commands: `outputs/microclimate-test-matrix.sh` and `outputs/microclimate-test-matrix.sh --release-gate`; then `python3 work/microclimate-test/scripts/build_release.py --output outputs`. Test matrix remains HA 2026.9.2/2026.9.3 and Python 3.14.7 unless a genuine dependency blocker is reported.

## 9. Acceptance tests

1. **Defaults:** existing entries without a write preference can use applicable controls; explicit false blocks direct service calls and queued writes. Diagnostic defaults are on; only integration-disabled diagnostic entries are re-enabled, while user-disabled entries remain disabled.
2. **Scope:** no Red on Evo I/II; no Blue output-type/ramp writes; no thermal settings on no-probe profiles; v8/v9/v10 always rejected. The seven requested categories route through one allowlist.
3. **Exact targeting:** test every enum table, all slot pins and v20–v23; no adjacent pin updates or extra mode writes.
4. **Numbers:** accept 0/100 and finite in-range decimals, reject negative/>100/NaN/infinity/boolean/null. Preserve reversed alarm thresholds. Compare suffix-bearing raw thermal readback without display rounding or F conversion.
5. **Dates:** accept 01/01, 28/02, 30/04, 31/12; reject 29/02 in every yearless request, 31/04, 00/00, zero components, malformed/year-bearing strings. Invalid requests make zero HTTP update calls.
6. **Times:** accept 00:00:00 and 23:59:59; reject 24:00:00, fractional/timezone-aware/solar inputs. Assert actual NULs and exactly-once URL encoding. Replay v32 plain→four-field encoding using the confirmed same-channel template. Preserve opaque suffixes on supported encoded targets; reject conflicting/missing templates without guessing timezone.
7. **Acknowledgement vs application:** empty 200, JSON error, delayed readback, numeric equivalence, clamping/mismatch, missing pin, oversized/malformed response, 429, auth expiry and timeout. Assert no automatic update retry.
8. **Concurrency:** queued edits serialize; separate entries remain independent; polling/readback lock order cannot deadlock; slow reads cannot overwrite newer data; external mode changes invalidate stale-context operations.
9. **Lifecycle:** token/options changed while queued, cancellation after dispatch, unload/reload during an update, and startup failures. No post-unload writes or replay after restart.
10. **HA UI:** correct root/channel grouping, typed controls and observed-value updates; existing sensor IDs/customizations preserved; new IDs remain stable across modes. Read-only sensors remain usable with writes disabled.
11. **Security/data handling:** no token or encoded token in logs/errors/fixtures, no redirect forwarding, no arbitrary URL/pin service; use the shared HA TLS session.
12. **Packaging:** both matrix modes pass on both versions; manifests/imports/archive contents/hashes validate; release notes explicitly state temporary editable/diagnostic defaults and field-level hardware-evidence limits.

## 10. Rules for finishing without further prompts

The product decisions above are sufficient to implement the requested iteration. Use the recorded defaults rather than reopening resolved questions. Continue independent phases if a runtime edge case exposes malformed data; reject only the affected operation with a clear error. Do not invent a new pin, endpoint, timezone or protocol meaning to make a test pass.

If evidence contradicts a requested capability, record the exact blocker and finish unaffected work; do not silently mark the whole request complete with a missing field family. Otherwise proceed through packaging without asking for repeated coding permission. No automatic live-controller verification is included: release notes must distinguish mocked write acceptance from the two hardware-confirmed pin examples.

