# Compact schedule cards — 1.3.2

> **Unofficial, independent project.** This integration and its custom cards are not affiliated with, endorsed by, or supported by Microclimate. Their only connection to Microclimate is that they work with its products. Product names are used solely to identify compatibility. For integration support, use this project’s [GitHub Issues](https://github.com/I-am-shadowspawn/HA_Microclimate_Integration/issues).

The compact series adds channel schedule cards and a root-controller season-date card with explicit Save/Cancel. See [installation and card usage](docs/CARD-USAGE.md) and [card API](docs/CARD-API.md). A clean reinstall was required for the 1.3.0 transition from the disposable prototype; upgrading an existing compact 1.3.0 entry to 1.3.1 preserves its identity. Individual schedule time/setpoint entities were removed; the cards use the aggregate schedule sensor as their permission scope. See [clean reinstall](docs/CLEAN-INSTALL-1.3.0.md) if still on the prototype.

# Microclimate Integration for Home Assistant

Version **1.3.2**. This custom integration reads Microclimate Evo Connect controller data and adds readback-confirmed configuration controls. Configuration writes remain enabled by default and can be disabled in entry options. Raw-pin diagnostic entities are disabled by default; the Reported schedule periods sensor remains enabled because the card uses it for permissions. Existing climate/sensor observations stay read-only. The channel card can import/export schedule preset files, and HA actions can export, apply or copy compatible schedules; see [schedule presets](docs/SCHEDULE-PRESETS.md) and [write controls](docs/WRITE-CONTROLS.md).

## Supported Home Assistant baseline

Initial public minimum: **Home Assistant Core 2026.9.3**. See [the maintainer-confirmed test platform](docs/TESTED-PLATFORM.md) for Supervisor, OS and Frontend versions. These describe the tested environment, not additional runtime dependencies.

## Supported profiles and devices

| Profile | Channel devices | Climate entities |
|---|---|---|
| Evo Connect | Yellow, Blue | Yellow |
| Evo Connect 2 | Yellow, Blue | Yellow, Blue |
| Evo Connect 3 | Yellow, Red, Blue | Yellow, Red, Blue |

Each entry creates one root controller device and its channel devices. Supplied captures cover all three profiles, including all Evo Connect 2 timing modes on firmware 0.2.4. Capability families and schedule pin groups are maintainer-confirmed. Physical transitions, periodic duration units, zero-date behaviour and complete hardware/firmware verification remain outstanding.

## Readings

- Temperature, observed setpoint and lower/upper alarm **thresholds**, where the profile has a probe. No active-alarm status is inferred.
- Output percentage, control mode and timing type. Yellow and Red expose pulse/dimming output readings and ramp duration in minutes; Blue reports its fixed on/off output capability and has no ramp measurement or attributes.
- Reported schedule periods, with all eight slots retained in attributes. The count means reported slots, not active slots. Thermal setpoints are Celsius; fixed-output setpoints are percentages. Unexpected tokens, reported timezone and unrecognized fields are preserved without calculating the active schedule.
- Mode-specific schedule attributes: Day Night exposes `day_night.day` and `.night` from the first two pairs; Multi exposes `daily_points` (eight time/setpoint entries); Seasonal exposes `seasons` (four day/night pairs plus root start dates). Original `periods` remain available in every mode. These are reported settings, not an active-schedule calculation. Blue Periodic retains unparsed interval/duration fields; no periodic meaning is assigned to Yellow/Red fields.
- Root metadata: four season starts, previous-24-hour power, temperature-unit code, system date/time and system name, plus reported pin count. The 24-hour power unit remains unverified and unset. Dates retain the reported year format; no century or timestamp is invented.
- Optional raw-pin diagnostics, disabled by default. Individual registry enable/disable choices survive reload.

Missing/invalid readings are unknown; failed refreshes make entities unavailable. Native temperatures are Celsius even when the upstream text is mislabeled F. Home Assistant may convert those native values for display. The reported unit flag does not trigger an extra conversion.

All entities use one polling coordinator per entry, normally refreshing once per minute. Entries share Home Assistant's HTTP session with explicit request timeouts. One normalization pass and a per-response reading cache avoid duplicate work; unchanged responses suppress entity notifications while failure/recovery transitions remain visible.

## Timing and schedule mapping

| Code | Yellow (all models), Red (Evo III) | Blue (all models) |
|---|---|---|
| 0 | Constant | Constant |
| 1 | Day Night | Day Night |
| 2 | Multi | Multi |
| 3 | Seasonal | Periodic |
| 4 | Unknown/unsupported | Seasonal |

Yellow pairs run v32/v33 through v46/v47; Red v62/v63 through v76/v77; Blue v92/v93 through v106/v107. In Seasonal mode pairs 1/2 are Season 1 day/night, 3/4 Season 2, 5/6 Season 3 and 7/8 Season 4. Root v20–v23 are the corresponding start dates. In Multi the same pairs are eight daily setpoint-change times. Yellow ramp is v48, Red ramp v78, both minutes. Blue has no ramp; returned v108/v114 values remain raw diagnostics without implying ramp or pulse/dimming capability.

00:00 is retained as a time and 00/00 as a zero-date sentinel; neither is automatically treated as a disabled slot/season. Do not infer an active season from missing dates.

## Installation and configuration

1. Back up the current integration directory and Home Assistant configuration.
2. Extract the install archive and replace `config/custom_components/microclimate_integration` with the bundled directory. Replace rather than merge: obsolete alternative modules were removed.
3. Restart Home Assistant. Add **Microclimate Integration (Unofficial)** through Devices & services and provide the controller name, API token and model.

This release requires recreating the single testing installation; no migration or legacy exposure mode is provided. Device/entity IDs may change during recreation. Entries created with this candidate keep their identity across subsequent rename and credential changes. Use Reconfigure to change the name or token; authentication failures offer reauthentication. The token is the only remote identity available, so different tokens cannot automatically be correlated to the same physical controller. Duplicate tokens are rejected. Never publish a token or credential-bearing request URL.

The install archive is a manual custom-component bundle, not an HA add-on or a published HACS release. This candidate has not been installed into your live HA instance by the review process.

## Maintainer guidance

`const.py` owns channel pins, metadata pins, shared field semantics, enum tables and probe profiles. `CHANNELS` is a generated view used by runtime consumers. The unused `const2.py` shim and compatibility mappings have been removed. Edit the canonical definitions and restart HA to load changed Python code. Climate/sensor observations and select/number/text controls and card schedule writes share one coordinator; `schedule.py` is a parser, not another platform or poller.

Normal operation adds only concise setup/unload debug messages. HA's coordinator reports failures and recovery. Full responses are logged only with the explicit diagnostic option below; credentials are redacted. Unknown vendor behavior is documented in TODO.md rather than hidden behind inferred values.

See README-TESTING.md for the pinned test matrix and build commands; CHANGELOG.md records the local candidate changes. Runtime HTTP uses aiohttp supplied by Home Assistant; the manifest requires no separately installed libraries. Test dependencies are pinned separately for each tested HA version.

## Capture full API responses for troubleshooting

Open this integration entry's options under Devices & services and enable **Log full API responses**. Also enable DEBUG logging for `custom_components.microclimate_integration` (or specifically `custom_components.microclimate_integration.api_client`). For YAML logging configuration:

```yaml
logger:
  logs:
    custom_components.microclimate_integration: debug
```

Merge this into an existing logger configuration rather than adding a second logger key. The per-entry option applies on the next poll; changing YAML requires the usual HA configuration reload/restart. Disable the option when capture is finished.

The log contains complete decoded JSON, including all pins and encoded schedule fields, without field truncation for accepted responses (read bodies over 1 MiB are rejected). NUL separators are JSON-escaped. This is a semantic JSON capture, not byte-for-byte HTTP traffic. It captures JSON error responses too; unreadable/non-JSON bodies produce a safe diagnostic message instead. Validation during onboarding does not enable response capture.

The configured API token, occurrences of it in response text, and credential fields such as token, password, authorization and API key are replaced with `[REDACTED]`. Other controller names and readings remain visible; review captured logs before sharing. Logging does not mutate the data supplied to entities. Both the option (default off) and DEBUG level are required.

## Schedule observation quality

Schedule fields expose `status`/`setpoint_status` to distinguish absent, invalid, unsupported and valid values. Unknown NUL fields retain their indexes and original values; solar offsets and day masks are not guessed. Seasonal zero dates use `status=sentinel`. API normalization already replaces non-finite numbers and unsupported containers with null; rejected inputs cannot be reconstructed from these typed views.

Multi preserves all eight slots in controller order. A midnight/zero-setpoint pair has `activation=likely_unused`, explicitly a maintainer inference, and is not removed. `duplicate_clock_times` reports repeated starts without deciding precedence. No active-period calculation is performed. The reported slot count is not an enabled-slot count.

See `docs/SCHEDULE-CONTRACT.md` for the complete evidence matrix, confirmed Day/Night and Multi layout, and the outstanding physical tests. R-01 full capture coverage and R-03 physical duplicate/midnight semantics remain pending; the read-only software views are implemented.

## Manual schedule presentation and history

Schedules are manually configured clock times. Automatic sunrise/sunset selection, solar offsets and astronomical calculations are not supported. Unexpected `sr`/`ss` tokens are retained as unsupported raw input rather than presented as a supported scheduling option.

The existing Reported schedule periods entity includes a readable `summary` attribute (maximum 255 characters) alongside the timing mode and reported slot count. Full `day_night`, `daily_points`, `seasons` and raw `periods` details remain available in the live entity attributes. IDs and polling are unchanged.

Large structured schedule attributes are excluded from recorder history using HA's entity metadata; the compact summary, mode and count remain recordable. Consequently history cannot reconstruct every old raw schedule field. HA's downloadable diagnostics provide a bounded structural summary without raw values; opt-in DEBUG capture is available when a full snapshot is needed. No active-calendar projection is calculated. Live dashboard acceptance and long-running recorder growth remain separate deployment checks.

## Aggregate schedule entity

Each channel has one enabled Reported schedule periods sensor with a summary and structured attributes. Its registry entity is the card's schedule permission anchor. Keep it enabled and grant READ access to view the schedule and CONTROL access to edit it.

Day & Night uses two pairs; Multi and Seasonal use up to eight. Constant and Periodic do not expose editable manual pairs. The card shows thermal setpoints in Celsius (or HA's configured temperature unit) and fixed output as percentages. The sensor remains read-only; validated writes use the card API.

Raw-pin entities remain registered for optional troubleshooting but are disabled by default. Other diagnostics, including root metadata and Last configuration write, retain their own defaults.

Root season starts remain separate metadata sensors. A raw 00/00 value reports unknown; a valid 09/02 reports 09/02. If a valid raw date nevertheless displays unknown, supply that entity's attributes for investigation.


## Ramp and season-order controls (1.1.1)

Yellow and Evo III Red now expose editable ramp duration (v48/v78), 0–240 whole minutes. Blue remains excluded. Root season date edits must form a distinct ordered annual cycle, with one December/January crossing allowed. Validation uses a fresh baseline and checks the observed cycle before confirmation; explicit 00/00 siblings permit initial population, while missing/invalid dates block unsafe ordering assumptions. See the write guide for examples and recovery.

The maintainer confirmed all previously enabled write attributes on Evo II/III. The new ramp/order additions, Evo I write validation and persistence/soak remain separate follow-ups. Hour/minute editor submissions remain separate confirmed operations; use one complete time action or an explicit Apply flow to avoid transient intermediate times.

## Project support and ownership

See [support and reporting](SUPPORT.md), [private security reporting](SECURITY.md), [contributing](CONTRIBUTING.md), [licensing](docs/LICENSING.md) and [independent branding](docs/BRANDING.md). Maintained by Simon Burke (`@I-am-shadowspawn`); project code is MIT licensed.
