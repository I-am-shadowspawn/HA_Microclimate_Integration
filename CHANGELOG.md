# 1.3.1 — support diagnostics and public defaults

- Disable raw-pin diagnostic entities by default without changing registry choices on reload. Keep schedule sensors enabled as ordinary entities for card permissions; writes retain their enabled default.
- Add bounded, redacted Home Assistant downloadable diagnostics with model/version, safe options, polling/write status and response shape. Raw values require the existing explicit DEBUG capture option.
- Remove a workstation path from the development documentation and audit packaged public assets for credentials and personal paths.

# Unreleased — distribution tooling

> **Unofficial, independent project.** This integration and its custom cards are not affiliated with, endorsed by, or supported by Microclimate. Their only connection to Microclimate is that they work with its products. Product names are used solely to identify compatibility. For integration support, use this project’s [GitHub Issues](https://github.com/I-am-shadowspawn/HA_Microclimate_Integration/issues).

- Select reviewed public fixtures and required runtime assets explicitly in reproducible release archives; check clean extraction and version agreement.
- Run Core 2026.9.3, frontend type/lint/unit/browser checks, bundle reproducibility, HACS and hassfest in GitHub CI. Gate future tagged releases on those results.
- Document portable Python/Node/uv commands. This is packaging and CI work; integration behaviour is unchanged.

# 1.3.0 — clean reinstall required

- Remove 32 individual schedule entities per channel; preserve aggregate observations, independent controls and card editing.
- Authorize channel schedule operations through the enabled, registry-bound aggregate sensor, including job recovery and per-step checks.
- Remove obsolete time platform, const2 shim, unused compatibility mappings and dead response decoder. Preserve validated pin schema and active derived views.
- No migration or legacy exposure mode. Reselect devices in existing cards after reinstall.

# 1.2.2

- Move target sliders directly below each timeline; collapse slot tables by default.
- Use configurable Celsius temperature bands with amber/orange/red defaults and a visual configuration editor.
- Match both colour and hatching across midnight-spanning slots.
- Preserve local drafts, explicit Save/Cancel, and all integration write behavior.

# 1.2.1 — card input and HTTP compatibility fixes

- Preserve partial date, numeric and schedule-time edits on input, before blur, across HA rerenders. No input event sends a vendor update.
- Replace secure-context-only randomUUID calls with UUID v4 identifiers from getRandomValues, supporting ordinary HTTP dashboard origins for rendering, Add and Save.
- Commit Multi time ordering after the input is committed, preserving focus while typing across another boundary.
- Keep annual season-cycle validation unchanged; invalid dates/order still block Save.

# 1.2.0 — Microclimate schedule cards

- Separate channel and controller cards, daily/seasonal timelines and 2–8-point Multi editing.
- Draft-only edits, changed-field review, sequential confirmed Save, conflict detection, progress/stop and partial outcomes.
- Registry/permission-bound WebSocket projection and jobs using existing shared write/I/O locks.
- Local bundled frontend, visual configuration editor, responsive theme support, keyboard/numeric input and manual resource installation.
- Device write protocol and ordinary entity identities preserved; no live controller calls during implementation.

# Changelog

## 1.1.1 — ramp controls and annual season order

645 tests pass per pinned HA version in both modes; 97% line coverage.

- Add enabled Yellow/Red ramp controls on v48/v78, constrained to 0–240 whole minutes; no Blue ramp.
- Validate root dates as a distinct annual cycle, allowing one year crossing, against fresh baseline and readback. Retain calendar bounds and support initial population around explicit 00/00 sentinels.
- Record maintainer-confirmed functional testing of all 1.1.0 enabled attributes on Evo II/III.
- Document why separate hour/minute submissions cause separate complete writes and why automatic debounce is not silently enabled.

## 1.1.0 — readback-confirmed configuration controls

601 tests pass on each pinned HA version in both regression and release-gate modes; 97% line coverage.

- Add selectors, numbers, manual times and root DD/MM text controls derived from the canonical schema; retain all observation IDs.
- Default writes and diagnostics on temporarily, preserve explicit user disables and keep raw DEBUG logging separately off.
- Serialize one-shot updates with fresh baseline/context checks, bounded readback/deadline and safe cancellation/reauthentication. Poll publication shares the same lock.
- Enforce numeric/date/time constraints; preserve NUL encoding and opaque suffixes; no inferred Constant targets, Blue output modes or arbitrary pin service.
- Bound response bodies, refuse redirects and redact encoded tokens. No live controller write or deployment was performed.
- See docs/WRITE-CONTROLS.md for usage and remaining model/firmware physical validation.

## 1.0.9 — individual schedule field sensors

467 tests pass per pinned HA version; 97% integration coverage.

- Correct the presentation gap: times and setpoints now have separate enabled sensors, rather than only nested attributes.
- Register 16 slot-stable sensors per channel with mode-aware names, applicability and temperature/percentage units.
- Preserve existing aggregate schedule entities, root date handling and shared polling.


## 1.0.8 — manual schedule presentation

464 tests pass per pinned HA version; 97% integration coverage.

- Close unsupported solar scheduling scope: unexpected sr/ss tokens stay raw/unsupported; clock schedules remain manual.
- Add bounded readable summaries to existing schedule entities without changing IDs or adding pollers.
- Keep full structured schedules live while excluding bulky duplicate detail from recorder history.


## 1.0.7 — schedule observation candidate

458 tests pass on each pinned HA version in regression and release-gate modes (97% coverage).

- Add explicit Day/Night groups using the first two time/setpoint pairs on every channel.
- Distinguish absent, invalid, unsupported and valid schedule fields; preserve opaque NUL fields with indexes and report timezone recognition separately.
- Annotate Multi midnight/zero default pairs as likely unused without discarding them; report duplicate times without inventing precedence.
- Add a model/channel/mode evidence ledger and controlled-test plan; retain explicit gaps for solar field meanings and physical schedule execution.


## 1.0.6 — validated mapping candidate, 23 September 2026

- Decode Constant and channel-specific Seasonal/Periodic codes consistently; Yellow/all models and Red/III share one timing table, Blue another.
- Present eight daily Multi points or four Seasonal day/night groups with root start dates, retaining all original slot values and pins.
- Describe Blue output as on/off; omit unsupported Blue ramp sensors/attributes and misleading pulse/dimming interpretations.
- Keep periodic interval/duration observational and only expose the typed periodic view for Blue in Periodic mode.
- Replay 48 sanitized responses from 12 hardware runs and add channel/capability acceptance regressions. Physical transitions, zero-date semantics and writes remain unverified.


## 1.0.5 — local candidate, 23 September 2026

- Share 0–100% output and nonnegative ramp validation across climate, sensors and schedule views.
- Reject impossible two-digit-year dates; preserve ambiguous century leap dates as unparsed and support yearless recurring leap days.
- Normalize non-finite numeric API values once so unchanged malformed responses compare equal.
- Remove legacy ID migration, collision paths and hashed-name fallbacks; verify fresh-entry rename, token replacement and reauthentication preserve current IDs and customizations.
- 398 tests pass per supported test-matrix version in regression and release modes. Evo Connect II hardware confirmation and live validation remain pending.

## 1.0.4 — local candidate, 23 September 2026

This candidate consolidates the workspace review changes since the original 1.0.3 code; it is not a published release.

- Correct Red and Blue pin assignments; consolidate definitions in const.py.
- Validate configuration and responses; sanitize credential-bearing errors; support reauthentication and token replacement.
- Preserve entity identities and root/channel grouping with tested legacy migration.
- Advertise observational capabilities only; retain the upstream Celsius/mislabeled-F workaround.
- Add typed measurements, raw diagnostics, root metadata and bounded schedule reporting.
- Reuse HA's HTTP session, explicit timeouts and one polling coordinator per entry; cache derived readings and suppress unchanged updates.
- Remove unused alternative platforms and broken factories.
- Replace stale feature claims with accurate documentation; remove placeholder code ownership and the redundant unpinned aiohttp manifest requirement.
- Add opt-in per-entry full JSON response logging with credential redaction and live option changes.
- Add pinned two-version HA tests, sanitized controller captures and deterministic install/development package generation.

## 1.0.3 — original project baseline

The unchanged original repository used this version. Earlier version numbers are not invented here.
