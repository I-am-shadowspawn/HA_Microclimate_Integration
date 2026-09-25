# Latest schedule work — candidate 1.0.7

> **Unofficial, independent project.** This integration and its custom cards are not affiliated with, endorsed by, or supported by Microclimate. Their only connection to Microclimate is that they work with its products. Product names are used solely to identify compatibility. For integration support, use this project’s [GitHub Issues](https://github.com/I-am-shadowspawn/HA_Microclimate_Integration/issues).

R-02 and the R-03 read-only implementation are delivered. R-01 evidence is consolidated; full R-01 and physical R-03 verification still need controller experiments. See the task entries below for exact scope. Earlier candidate status notes are historical.

# Current implementation status — candidate 1.0.6

RC-08/RC-09 are resolved. Multi daily points and Seasonal groups for Yellow/Red/Blue are implemented with root dates; unsupported Blue ramp and pulse/dimming interpretations are removed. The earlier evidence notes below remain as history; statements that implementation is unchanged are superseded by this status. Physical transitions, periodic units, zero-date semantics and writes remain open.

# Microclimate — clean forward TODO

Updated 23 September 2026 after review of local candidate 1.0.4. This replaces the old corrective checklist as the active work queue. RC-01 through RC-04 are resolved in candidate 1.0.5; remaining unchecked items are outstanding.

**Scope:** first a dependable read-only release, then complete schedule observation, then opt-in verified settings writes. No legacy ID migration is required: there are no live prior-version installations. Stable IDs for new installations remain required. **Full Evo Connect II mapping and behaviour confirmation is pending.**

## Candidate corrections and remaining release gates

- [x] **RC-01 — Align reading boundaries.** Reject output outside 0–100 consistently in climate activity, sensor state and attributes; reject negative ramp durations consistently. Add boundary regressions for missing, non-finite, negative and over-range values.
- [x] **RC-02 — Correct short-year date validation.** Do not classify `29/02/25` as a validated date. Validate what the year representation establishes, retain century uncertainty, and test yearless/leap/sentinel dates.
- [x] **RC-03 — Normalize non-finite API numbers.** Convert NaN/infinity numeric values to unknown once at the API boundary. Identical invalid responses must compare equal and suppress duplicate notifications; recovery must still notify.
- [x] **RC-04 — Remove legacy ID migration.** Remove registry migration calls, conflict/manual-migration paths, old hashed-name fallbacks and migration-only tests. Preserve entry/channel IDs and duplicate-token checks; directly test rename, reconfigure and reauth continuity from a fresh entry.
- [ ] **RC-05 — Freeze honest model support.** Label Evo II provisional or exclude it from verified support until V-01 passes. State firmware uncertainty and partial schedule interpretation explicitly.
- [ ] **RC-06 — Rebuild release evidence.** After changes, run both full matrix modes, validate the manifest, build deterministic install/development archives, check hashes and assign a distinct next candidate version. Do not overwrite the reviewed 1.0.4 release bytes.
- [ ] **RC-07 — Finish publication details.** Confirm actual owner, repository/documentation/issue links, intended distribution, licence terms and tested HA/Python range. Do not invent a minimum compatibility version from two passing test rows.

## Validation beyond the current fixtures

- [ ] **V-01 — Confirm Evo Connect II completely.** Capture each supported channel, mode and scheduling option; match pins, units, ranges, probe capabilities and actual behaviour to the display. Record firmware and repeated observations before promoting the profile.
- [ ] **V-02 — Complete Evo I/III evidence.** Record firmware; compare mode/ramp/alarm changes, output activity and missing/disconnected probes against the controller. Keep captures model/firmware-specific.
- [ ] **V-03 — Resolve unverified units/pins.** Confirm v24 units, v25 flag meaning, Blue periodic interval/duration units. Yellow and Evo III Red lack Periodic capability; preserve unexplained fields without assigning them periodic semantics. Update fixtures/schema only after evidence.
- [ ] **V-04 — Fresh-install and real UI checks.** Check root/channel grouping, entity names/IDs, metric/US display, observational climate actions, options, disabled diagnostics and readability of schedules. Restart HA and verify saved options and identity continuity.
- [ ] **V-05 — Lifecycle failure checks.** Inject failed platform setup after first refresh, in-flight reload/unload, entry removal and token expiry. Confirm no orphan listeners, pollers or registry artifacts; other entries keep working.
- [ ] **V-06 — Live read-only soak.** Run a documented 24–48-hour trial with network outage and controller restart; record cloud request rate/throttling, TLS/connectivity, recovery, memory and recorder/log growth.
- [ ] **V-07 — Validate debug capture operationally.** Confirm default-off, per-entry gating, next-poll enable/disable, complete JSON fields and redaction on actual responses. Measure log volume and verify rotation; inspect captures before sharing.

## Complete read-only schedule exposure

- [ ] **R-01 — Capture the full schedule contract (partial).** Existing evidence is indexed in `docs/SCHEDULE-CONTRACT.md` and `fixtures/schedule_contract.json`; all Evo II timing codes and confirmed slot layouts are recorded. Still requires independent complete Evo I/III mode sweeps, unassigned non-solar fields and physical edge-case observations. No full hardware contract is claimed.
- [x] **R-02 — Build typed, lossless observations (verified-format scope).** Candidate 1.0.7 distinguishes absent, invalid, unsupported and valid fields; retains supported raw values and indexed opaque fields; reports timezone recognition; preserves valid zero and zero-date sentinels. Unknown offsets/day masks stay opaque. Disabled is not fabricated: Multi midnight/zero is explicitly likely-unused inference. API-rejected/oversized inputs are not losslessly reconstructable.
- [ ] **R-03 — Complete Day Night and Multi (software complete, physical checks pending).** Candidate 1.0.7 exposes confirmed Day/Night pairs, eight Multi points, typed temperature/percentage setpoints, inferred-unused default pairs and duplicate-clock diagnostics; preserves order and midnight values. Still requires actual duplicate precedence, midnight carry-over, default-versus-intentional-zero distinction and mode-switch persistence tests.
- [ ] **R-04 — Complete Periodic.** Verify units, limits, resolution, interval/duration relationship, phase reference and interaction with control mode; restrict Periodic to Blue, as confirmed by the maintainer; raw fields on Yellow/Red do not establish capability.
- [ ] **R-05 — Complete Seasonal (configuration implementation complete; behaviour validation pending).** Confirmed timing codes, all channel season/day/night pairs, root date ordering and ramp capabilities are implemented in 1.0.7. Remaining S-01–S-04 checks: zero-date selection, actual boundary/shared-date behaviour, year rollover/date ordering and leap-day handling. See `microclimate_R05_completion.md`; no pin-mapping gap remains for the confirmed read-only view.
- [x] **R-06 — Solar scope closed as not applicable.** Maintainer confirms all schedules are manually timed: no sunrise/sunset automation. Candidate 1.0.8 treats unexpected sr/ss as unsupported raw input; no solar options, offsets or projections are offered.
- [x] **R-07 — HA read-only presentation complete.** Candidate 1.0.8 provides bounded mode-specific summary attributes, full live structured views, correct channel capabilities and unknown/unavailable behaviour, stable IDs and one coordinator. Large structured attributes are excluded from recorder history; offline HA tests verify metadata and reduced attribute size. Live dashboard acceptance/soak remain V-04/V-06, not claimed as performed.
- [ ] **R-08 — Gate the read-only scheduling release.** Add captured and boundary fixtures for every promoted mode/model, pass the matrix and hardware display comparisons, and document unsupported combinations.

## Settings writes — only after protocol verification

- [ ] **W-01 — Establish the write contract.** Verify actual endpoint/method/authentication, payload encoding, units, limits, acknowledgements, rate limits, permissions and persistence on a test controller. Generic Blynk assumptions are insufficient.
- [ ] **W-02 — Build safe write transport.** Reuse HA's session/timeouts, serialize per-controller writes, coordinate polls, preserve sanitized errors and read back results. After uncertain timeout, reread before retrying; document concurrency limits where the vendor lacks revision checks.
- [ ] **W-03 — Add opt-in capability gates.** Default to read-only. Enable writes only for verified model/firmware/field combinations with server-side validation and clear pending/confirmed/failed outcomes.
- [ ] **W-04 — Expose basic settings incrementally.** Verify thermal target, fixed-output %, ramp minutes and alarm thresholds before enabling corresponding climate/number entities. Verify mode/output/timing selectors and their dependencies separately; do not infer HVAC OFF semantics.
- [ ] **W-05 — Build lossless schedule serializers.** Require round-trip preservation of verified and opaque fields. Unexplained or unsupported formats remain read-only.
- [ ] **W-06 — Add whole-schedule editing.** Validate proposed schedules, reread current state, then apply a proven commit or safe ordered sequence. Confirm complete read-back and expose partial failures; no unproven atomicity or blind rollback promises.
- [ ] **W-07 — Validate write failure and conflict paths.** Test partial writes, lost acknowledgements, stale snapshots, simultaneous official-app edits, authentication/rate-limit errors, power loss and controller reboot. Verify physical/display outcomes under controlled conditions.
- [ ] **W-08 — Release writes separately.** Promote capabilities per model/firmware/mode, document recovery and disable-write paths, and repeat clean-install/soak/package validation before broader rollout.

**Order:** RC fixes and release checks first; V evidence unlocks R phases; W-01/W-02 can be researched after the read contract is understood, but user-facing writes require their evidence gates. Legacy migration is not a release requirement or future work item.

RC-01–RC-04 validation: 398 tests pass on each of HA 2026.9.2 and 2026.9.3 in both modes. Candidate 1.0.5 packages replace no prior release archive; hardware confirmation and the other release gates remain open.

## Capture review update — 23 September, including 16:02/16:05 follow-ups

- [x] **RC-08 — Correct model/channel timing decoding.** Operator-labelled Evo II firmware 0.2.4 captures establish Yellow v53=3 for Seasonal and 0 for Constant; the current decoder reports Periodic and unknown. Blue v113=3 corresponds to Periodic. Introduce a shared context-aware decoder and acceptance tests across sensors, schedule attributes and other consumers. Do not change code 3 globally or confuse Constant timing with fixed-output control. Latest labelled captures additionally confirm Yellow 1=Day & Night, 2=Multi and Blue 0=Constant, 2=Multi, 4=Seasons. The 16:16 follow-up confirms Blue Day & Night=1: all supported timing codes on both Evo II channels are now captured. Use the maintainer-confirmed Yellow/all-models and Red/III capability group; Periodic is Blue-only.
- [x] **Capture replay evidence:** sanitized 48 responses from twelve read runs, covering Evo I firmware 0.2.6 and Evo II/III 0.2.4; added HA entity replay and operator-labelled timing evidence tests. Passing replay characterizes the current decoder; RC-08 remains a real defect.
- [ ] **V-01 follow-up:** enum capture coverage is complete; validate nonzero Blue periodic interval/duration and seasonal date/slot experiments in `microclimate_capture_validation_20260923.md`. Yellow alarm thresholds 100/45 match the operator’s display; do not “correct” them.
- [ ] **Freshness validation:** investigate the frozen previous-day Evo III payload; successful cloud retrieval is not proof of fresh controller data.

Yellow v55/v56 are present but do not establish Periodic support: the maintainer confirms Periodic is Blue-only. Likewise, do not expose Red Periodic based on retained v85/v86 fields. No write contract is established by these read captures. Full model support, V-01 and the scheduling/write gates remain open.

- [x] **V-01 timing-code subtask:** all four Yellow and all five Blue modes have labelled Evo II firmware 0.2.4 captures. This closes enum evidence gathering, not RC-08 implementation or full scheduling/physical behaviour validation.

## Yellow Seasonal confirmation

- [x] **R-05 evidence — Yellow season/slot association.** Maintainer confirms Season 1 day/night = periods 1/2 (v32–v35), Season 2 = periods 3/4 (v36–v39), Season 3 = periods 5/6 (v40–v43), Season 4 = periods 7/8 (v44–v47). Even pins are start times; following odd pins are temperatures. v48 is channel ramp minutes (captured value 9).
- [x] **R-05 presentation:** all confirmed Yellow, Red and Blue Seasonal day/night groups are exposed, retaining raw slot data and mode-specific labels.
- [ ] **R-05 remaining evidence:** controller selection for zero dates, actual season boundaries/shared-date behaviour, rollover/date ordering and leap-day handling. Yellow, Red and Blue slot associations are all confirmed. Physical ramp progression and writes are separate checks, not unresolved Seasonal pin mappings.

## Blue Seasonal confirmation

- [x] **R-05 evidence — Blue season/slot association.** Maintainer confirms Season 1 day/night = v92–v95, Season 2 = v96–v99, Season 3 = v100–v103, Season 4 = v104–v107. Even pins are start times; following odd pins are temperatures. Preserve zero start times without assuming disabled semantics.
- [x] **R-05 presentation — Blue has no ramp in any timing mode.** Confirmed capability is implemented: four Seasonal day/night pairs, no typed ramp sensor/attributes, and on/off output capability. Raw v108 does not imply support.

The Blue excerpt is additional maintainer evidence, not a new complete capture or test run. No integration implementation changes were made by recording it.

## Season date confirmation

- [x] **R-05 evidence — season-start pin ordering.** Maintainer confirms Seasons 1–4 correspond to root v20/v21/v22/v23. Supplied example: Season 1 09/02 (9 February); Seasons 2–4 00/00. Current root metadata mapping agrees.
- [ ] **R-05 remaining date behaviour:** establish what 00/00 does operationally, verify distinct nonzero dates for Seasons 2–4, active-season selection and year rollover. Do not equate the zero-date sentinel with disabled without evidence.

## Multi slot reuse confirmation

- [x] **R-03 evidence — shared Multi slots.** Maintainer confirms the eight Seasonal time/setpoint pairs are reused in Multi as eight daily setpoint-change times: Yellow v32/v33 through v46/v47; Blue v92/v93 through v106/v107. Multi entries have no season grouping.
- [x] **R-03/R-05 presentation:** retain one raw slot model, presenting eight daily points in Multi and four season day/night pairs in Seasonal, selected by the corrected per-channel timing decoder.
- [ ] **R-03 remaining behaviour:** validate unused slots, duplicate times, midnight carry-over, ramp transitions and configuration persistence when switching modes. Do not infer these from shared pin addresses.

## Blue output and Red schedule clarification

- [x] **R-03/R-05 evidence — Red mapping.** Maintainer confirms Red v62/v63 through v76/v77 as the eight shared Multi/Seasonal pairs; Seasonal pairs group consecutively into Season 1 day/night through Season 4 day/night. Red ramp is v78, minutes. This agrees with the existing Evo III Red schema.
- [x] **Blue capability evidence:** on/off output, no dimming/pulse selection, no ramp. This supersedes earlier uncertainty about whether no-ramp applied only to Seasonal.
- [x] **RC-09 — Correct Blue capability presentation.** Remove misleading ramp and Pulse/Dimming interpretations from Blue's typed sensors, climate attributes and schedule presentation across its supported modes. Preserve raw values where useful; report on/off hardware capability without inferring it from v114. Add capability regressions. Keep output hardware distinct from control mode, timing mode and reported output percentages; do not invent duty-cycle or switch thresholds.

RC-09 is implemented in candidate 1.0.6. Existing capture replay tests that expect Blue Pulse/ramp readings characterize the old implementation and must be revised when the capability correction is implemented. Red schedule pin association is confirmed; physical schedule/ramp behaviour and write semantics remain open.

## R-01–R-03 implementation — candidate 1.0.7

- [x] Maintainer confirms first two time/setpoint pairs are Day and Night on every channel. Added `day_night` view with raw remaining periods retained.
- [x] Maintainer confirms no explicit Multi per-point enable control; midnight plus zero setpoint suggests unused. Added `likely_unused` annotation with inference evidence; entries are not removed or treated as definitively disabled.
- [x] Added field validity/presence status, opaque-field indexes and duplicate time observations without executing a schedule.
- [x] Built the evidence ledger and precise remaining experiment list.
- [ ] Full R-01 hardware capture coverage and R-03 physical transition validation remain open; see `microclimate_schedule_contract.md`.

## R-05 review of completion

- [x] R-05 configuration software and confirmed mappings complete in 1.0.7. Removed stale claims that Red slot associations or Blue ramp scope still needed confirmation.
- [ ] R-05 physical contract still needs S-01 zero-date rules, S-02 boundaries/shared dates, S-03 rollover/date ordering and S-04 leap-day behaviour. See `microclimate_R05_completion.md`. No speculative controller execution logic was added.

## R-06/R-07 closure — candidate 1.0.8

Solar functionality is not a missing hardware-validation item: it is unsupported per the maintainer. Earlier solar research items are superseded. Manual clock/timezone observations remain preserved without astronomical or active-period calculation. R-07 implementation and offline acceptance are complete; V-04/V-06 still cover live UI and long-duration behaviour.

## 1.0.9 — schedule entity visibility correction

- [x] Added individual enabled start-time and setpoint sensors for all eight pairs on each channel; 1.0.8 exposed these only as attributes. This closes the reported R-07 visibility gap. IDs follow physical slots; mode-aware names and availability prevent unrelated pairs appearing as applicable settings.
- [x] Verified separate sensors for all model profiles, thermal/fixed units, live mode changes, root valid/zero dates, shared polling, and failure availability.
