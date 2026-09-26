# Microclimate 1.3.0 — compact schedule refactor

> **Unofficial, independent project.** This integration and its custom cards are not affiliated with, endorsed by, or supported by Microclimate. Their only connection to Microclimate is that they work with its products. Product names are used solely to identify compatibility. For integration support, use this project’s [GitHub Issues](https://github.com/I-am-shadowspawn/HA_Microclimate_Integration/issues).

## Delivered

The aggregate Reported schedule periods sensor is the channel schedule permission anchor. Cards still read normalized coordinator data and use the existing validated sequential write engine; sensor attributes are not a writable database. All 32 individual schedule entities per channel (16 read-only sensors plus 16 number/time controls) are removed. The obsolete time platform is removed. No new exposure toggle, migration or registry-restoration machinery is introduced.

Fresh-install default entity totals, verified with real HA setup:

| Model | 1.2.2 | 1.3.0 | Removed |
|---|---:|---:|---:|
| Evo Connect | 123 | 59 | 64 |
| Evo Connect 2 | 130 | 66 | 64 |
| Evo Connect 3 | 189 | 93 | 96 |

Independent modes, output type, ramps, alarm thresholds, root dates and current observations remain. Per-channel schedule sensors retain all eight stored slots and recorder exclusions. Day/Night uses the first two pairs; retained other values are not active-period evidence. No current-period inference or schedule library was added.

## Constants cleanup

Removed const2.py re-export shim; unused NEW_ATTRIBUTE_MAPPING and SCHEDULE_PIN_MAPPING; the unused api_client.decode_response / ATTRIBUTE_MAPPING / _attribute_rows chain, including its unconsumed v31 descriptive alias. The API still preserves unknown raw pins. Tests now import canonical const.py. The Blue timing table is named BLUE_TIMING_TYPE_MAPPING instead of the generic legacy name. CHANNELS remains because current runtime consumers use that generated view; COMMON_ATTRIBUTES, model/HVAC mappings and canonical pin definitions remain.

An executable equality audit against the preserved 1.2.2 ZIP verified all surviving channel pins, capabilities, metadata, derived maps, enum values and defaults unchanged. The results are included in the schema-audit JSON. No vendor pin values or behavior have been guessed or changed.

## Permissions and implementation decisions

Indexed fields resolve to a server-selected aggregate sensor verified against the entry/channel device. READ allows projection; READ plus CONTROL allows schedule writes and job access. Disabled, missing or misbound anchors fail closed; hidden anchors remain usable. Other fields retain independent permission anchors. Runtime generation/conflict checks, shared locks, sequential readback, Multi shifting, time suffixes and failure/recovery behavior remain in place.

Schema 1 is retained: frontend field identities use keys, not entity IDs. An additive authorization_scope field explains the binding. Browser fixtures now use one shared entity ID for indexed fields. No frontend runtime changes were needed.

Final review found a permission revocation window during awaited baseline reads. A callback now rechecks authorization after the final read and before dispatch, and a regression proves revocation there sends zero writes. Request recovery and completed job access also recheck scope. There is still no atomic remote transaction, write retry or automatic rollback.

## Validation

- 697 tests passed on each pinned HA 2026.9.2 / 2026.9.3 environment, release-gate mode (no expected-failure masking), zero failures/skips; 96% rounded Python coverage.
- Strict TypeScript, ESLint, 21 unit tests, 43 Chromium browser tests and production build passed. Browser tests include compact shared-anchor fixtures, prior typing/HTTP regressions, all schedule UI workflows and responsive previews.
- Desktop Multi edit and 320px dark seasonal screenshots visually inspected. Static resource and authenticated WebSocket behavior tested with HA.
- New coverage includes fresh counts/absence of old registry rows, all model/channel projections, supplied Evo II Day/Night values, read-only scope, renamed/hidden/missing/disabled/wrong-channel/wrong-entry anchors, independent root/alarm permissions, permission revocation between writes and during the final read, and job recovery restrictions.
- Existing lifecycle, identity, reauth, read/write, recorder, malformed-response, encoding, range and cancellation regressions remain passing. Tests for removed controls were ported to card projection/internal wire validation; Fahrenheit HA number-service conversion is retained through an alarm control.
- Dependency checks passed on both matrix environments. Build tooling compiles all packaged Python source and validates the manifest.

Evidence is in microclimate-1.3.0-validation and microclimate-1.3.0-test-results.json. Prior release artifacts remain the rollback baseline. No live device requests, HA deployment or edits to the original source repository were performed.

## Installation and remaining acceptance

Clean reinstall is required and accepted for the single testing instance. See CLEAN-INSTALL-1.3.0.md: preserve credentials and card configuration, remove old entries/devices, replace the component directory, restart, recreate entries, reselect devices in the cards and update the resource URL to `?v=1.3.0`. Do not overlay obsolete files or edit HA registry storage manually. Installing/removing the integration sends no controller-reset or schedule-clear command.

All local implementation work is complete subject to final artifact checks recorded alongside this report. Actual reinstall/dashboard acceptance remains with the user. Current-period calculation, reusable schedules, Constant target and Periodic writes are outside this refactor.
