# 1.3.0 compact exposure acceptance

> **Unofficial, independent project.** This integration and its custom cards are not affiliated with, endorsed by, or supported by Microclimate. Their only connection to Microclimate is that they work with its products. Product names are used solely to identify compatibility. For integration support, use this project’s [GitHub Issues](https://github.com/I-am-shadowspawn/HA_Microclimate_Integration/issues).

- [x] User confirms 1.2.2 functionality across all features (25 September 2026).
- [ ] Install 1.3.0 by clean recreation and reselect card devices; verify restricted-user permissions and compact entity counts in the testing instance.
- [ ] Persistence, failure injection and soak evidence remain separate from ordinary functional acceptance.
- [ ] Calculated current-period display and reusable schedule presets remain future scope.

Prior release checklist below is historical context; individual schedule entities were removed in 1.3.0. Current reinstall instructions supersede any old upgrade/ID-migration acceptance wording.

# 1.2.0 card acceptance follow-up

- [ ] Controlled live verification of Multi clearing, compaction, intermediate pair effects and persistence on every supported model/firmware.
- [ ] User deployment acceptance: real HA dashboard resource loading, restricted-user permissions and mobile browser usage.
- [ ] Constant target and Periodic duration/interval mapping remain separate future work; no speculative writes added.

# Microclimate — active TODO after 1.1.1

Updated 24 September 2026. The completed write implementation specification is recorded in microclimate_write_implementation_plan.md. Prior checklist/history is retained in docs/TODO-1.0.9-HISTORY.md. Unchecked items below require new hardware evidence or are explicitly outside the implemented scope.

## Delivered software

- [x] 1.1.1: Yellow/Red ramp controls and cyclic season-start validation, including fresh-baseline/readback checks. Time-edit optimization risks and single-action usage documented.

- [x] RC-01–RC-04: boundary/date/non-finite normalization and fresh-entry identity behavior.
- [x] R-02/R-03/R-05/R-07: typed/manual Day Night, Multi and Seasonal observations, per-field sensors and root dates. Physical behavior checks remain below.
- [x] R-06: solar scheduling excluded, as confirmed by the maintainer.
- [x] W-01 contract for this iteration: confirmed server/endpoints, v20/v32 write evidence and maintainer input constraints; no universal hardware certification inferred.
- [x] W-02: shared-session one-shot transport, per-entry serialization, readback, deadline, failure/auth/cancellation handling and poll coordination.
- [x] W-03: allowlisted controls, writes enabled by default per explicit revised specification; explicit disable honored. Diagnostics default enabled temporarily.
- [x] W-04: control/output/timing selectors, schedule setpoints, alarms, manual scheduled times and season dates. Observed targets/climate setters stay read-only.
- [x] W-05: preserve supported encoded time suffixes; infer plain-time template only from agreeing same-channel evidence; reject unsupported encoding.
- [x] W-07 software: mocked failure/conflict/lifecycle/HA service acceptance. Physical portions remain below.

## Hardware and operational validation

- [x] V-01 functional writes: maintainer confirms every enabled 1.1.0 attribute on Evo II (24 September 2026). Record as user-confirmed testing; no new capture/firmware details supplied.
- [x] V-02 Evo III functional writes: maintainer confirms every enabled 1.1.0 attribute (same report).
- [ ] New 1.1.1 acceptance: validate Yellow/Red ramp control at 0 and 240 minutes and representative whole-minute values; check accepted/rejected season ordering and cross-year dates against the live HA/controller setup.
- [ ] Persistence: validate mode-switch and reboot persistence separately; ordinary field testing is not treated as a persistence or soak result.
- [ ] V-02 remaining: complete Evo I write validation; exercise missing/disconnected probes and capture model/firmware details.
- [ ] V-03 / R-04: establish v24 power units, v25 semantics, and Blue Periodic interval/duration units, limits, relationship and phase reference. Keep these edits unavailable until known.
- [ ] V-04: install candidate in a controlled HA instance; check root/channel controls, metric/US display, names, saved options and user-disabled diagnostics. Verify observation IDs/customizations after upgrading 1.0.9.
- [ ] V-05 / W-07 physical: token expiry, throttling, lost acknowledgements, simultaneous official-app edits, connectivity/power loss and reboot. Verify API observations against actual behavior. Never infer remote rollback after an uncertain result.
- [ ] V-06: controlled 24–48-hour soak, including outage/restart, request rate, recorder/log growth, memory and recovery.
- [ ] V-07: exercise diagnostic logging/redaction and rotation with actual responses; review captures before sharing.
- [ ] R-01/R-03/R-05/R-08 physical: full profile/mode captures; duplicate-clock precedence, midnight carry-over, default zero versus intentional zero, season date ordering/year rollover/shared boundaries and unset dates. Read-only software is complete for the confirmed format; physical execution is not certified.
- [ ] W-08: promote the development candidate only after field/model evidence and controlled install/soak. Decide when to revert temporary diagnostic/write defaults.

## Future scope, not implementation gaps

- [ ] Establish a distinct Constant target pin, if supported; do not repurpose v8/v9/v10 or schedule slot 1.
- [x] Expose Yellow/Red ramp writes using the maintainer-confirmed 0–240 whole-minute bounds; Blue remains excluded.
- [ ] Validate periodic writes before exposing them. Blue has no ramp/pulse/dimming capability.
- [ ] W-06: whole-schedule editing requires an evidenced ordering/commit/recovery strategy; the API offers no proven atomic transaction.

No live deployment, controller write, physical validation or soak was performed by this implementation run. Original repository remains untouched.
