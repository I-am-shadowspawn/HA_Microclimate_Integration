# Microclimate cards — 1.3.2

> **Unofficial, independent project.** This integration and its custom cards are not affiliated with, endorsed by, or supported by Microclimate. Their only connection to Microclimate is that they work with its products. Product names are used solely to identify compatibility. For integration support, use this project’s [GitHub Issues](https://github.com/I-am-shadowspawn/HA_Microclimate_Integration/issues).

The release includes **Microclimate channel** and **Microclimate controller** cards. Install the backend and its bundled card together. The minimum supported Home Assistant Core version is 2026.9.3.

## Clean reinstall required

For the 1.3.0 compact transition, follow [the clean-install runbook](CLEAN-INSTALL-1.3.0.md). If already on the compact series, install 1.3.2 and retain the entry and card configuration. Update the JavaScript module resource to `/microclimate_integration/microclimate-cards.js?v=1.3.2`, then refresh the frontend. Preserve any custom colour configuration.

Individual time/setpoint entities no longer exist. Keep the channel's **Reported schedule periods** sensor enabled: the card requires READ access to show its schedule and CONTROL access to edit it. It is an ordinary enabled sensor rather than a diagnostic entity; raw-pin diagnostics can remain disabled. Other controls and root dates retain separate permissions. The sensor itself remains read-only; validated writes go through the card API.

For a complete Day Night, Multi or Seasonal schedule, **Download preset** saves a device-free JSON template. **Import preset** appears in Edit mode and changes only the local draft until Save. Import on another compatible card to copy a schedule; shared season dates are not copied. See [preset format and HA actions](SCHEDULE-PRESETS.md).

## Install and add cards

1. Back up your Home Assistant configuration. Extract the install ZIP into your HA configuration directory so it contains `custom_components/microclimate_integration/manifest.json` and `frontend/microclimate-cards.js` beneath the integration folder. Restart HA after replacing the integration.
2. In dashboard settings → Resources (enable Advanced Mode in your user profile if necessary), add `/microclimate_integration/microclimate-cards.js?v=1.3.2`, type **JavaScript module**. Add it once. If upgrading a previous card resource, change its version query and reload the browser.
3. Edit a dashboard, Add card, choose **Microclimate channel**, then select the registered Yellow/Red/Blue channel device. Add one per channel you want displayed.
4. Add **Microclimate controller** separately and select the root device to edit shared season dates.

The visual editor lists only accessible Microclimate devices. It handles entity renaming; do not construct entity names manually. YAML equivalents:

```yaml
type: custom:microclimate-channel-card
device_id: YOUR_CHANNEL_DEVICE_REGISTRY_ID
# Optional:
title: Vivarium — Yellow
read_only: false
show_observations: true
```

```yaml
type: custom:microclimate-controller-card
device_id: YOUR_ROOT_DEVICE_REGISTRY_ID
read_only: false
```

Copy the device ID from its HA device-page URL, or use the visual editor. `read_only: false` permits the **Edit** action; it does not open editing automatically. `read_only: true` hides Edit. The HA user also needs access to the relevant entities; integration writes must be enabled and controls must not be disabled in the entity registry. The card cannot bypass those restrictions.

The integration serves its bundled JavaScript locally. There are no runtime CDNs, device tokens in the browser, automatic dashboard modifications, or additional device polling loops.

## View and edit

Cards open read-only. **Edit** creates a local draft. Numeric inputs, slider movements, dragging and arrow keys never send updates. **Cancel** discards that draft. **Save changes** reviews and sends the final values; separate hour/minute edits produce one complete time value.

Day/Night has two named boundaries/targets. Seasonal has four Day/Night rows; dates alongside them are shared root settings and are edited in the controller card. Values retain their physical Day/Night identity even when the Day interval crosses midnight. Equal Day/Night boundaries cannot be saved.

Multi has 2–8 distinct chronological points. **Add point** proposes a local point (review its time/target); **Remove selected** promotes later points and clears the unused tail when saved. Insertion shifts later points down. Two points are the minimum; eight are the maximum. A full schedule can be edited by removing then adding in the same draft. Dragging across a neighbour reorders the logical points. HA physical-slot entity IDs stay unchanged.

The combined midnight/zero target is reserved for unused Multi slots. Midnight with a nonzero target and zero target at another time are valid. A malformed, unordered, duplicate or incomplete existing Multi table enters a repair state: choose **Review/rebuild point list**, correct unknown values, then review the full result before Save. No opening/refresh action repairs the controller automatically. An empty table does not establish that the controller is OFF.

The timeline is a configured daily preview, not proof of which point is physically active. The hatched leading segment is the previous day's configured continuation. There is no automatic solar scheduling, weekly program or animated ramp curve. All times are controller-local clock values. Direct input supports seconds; dragging snaps to five minutes, arrow keys one minute and Shift+arrow five minutes. Use the numeric inputs instead of dragging on a small screen. 24:00 is an axis label only; writable times end at 23:59:59.

Thermal targets/alarms use HA's chosen °C/°F presentation and convert edited values once to native Celsius. Fixed-output targets use %. Native bounds remain 0–100; ramp is 0–240 whole minutes. Blue has no ramp/output-type control. Mode selectors are saved individually before editing settings under their new meaning. Do not interpret a temperature draft as percentage values.

**All timing modes share the same stored schedule pairs.** Changing one mode's pairs changes what another mode later sees. The card does not keep independent programs or restore hidden mode backups. Constant target and Blue Periodic duration/interval editing remain unmapped and are explicitly unavailable.

Season dates use DD/MM, valid normal calendar bounds, no 29/02, and a strictly sequential annual cycle allowing one year wrap. Existing `00/00` siblings are unset; a new date cannot be cleared to `00/00`. The server chooses a valid intermediate order for multiple changed dates. If no such order exists, it sends nothing; stage a smaller valid change or use the controller editor. Missing/malformed siblings need correction before a validated sequence can be written.

## Save results and recovery

Save is **sequential, not atomic**. A time and its target are separate vendor writes; shifted points can briefly produce duplicated or mixed pairs. Updates may affect active control immediately. Review the changed-field list before Save. The API provides no transaction, remote lock or compare-and-swap.

The integration holds a common per-entry lock, confirms each write through readback, and stops at the first rejection, mismatch, uncertainty or detected conflict. Another channel card on the same controller reports busy while the operation runs. Ordinary HA services use the same lock; other controllers remain independent. There is no automatic update retry or rollback.

Progress distinguishes confirmed, failed, uncertain and not-sent fields. **Stop remaining changes** stops future dispatches after the current request finishes; it cannot undo anything already sent. Success requires a final combined readback. The normal operation limit is 10 minutes, with each per-pin operation limited to 60 seconds.

External changes invalidate a draft. **Refresh and review draft** deliberately compares the desired result against fresh observations; it does not silently rebase. A changed mode or connection requires discarding and starting a new draft. External-app races between read and write remain possible despite preflight checks.

A partial Save retains its draft and per-field results. Review observed values before a new Save. If the initial Save acknowledgement is lost, **Check request status** performs a read-only lookup; it never resends a vendor update. Reconnect can recover retained progress. The server keeps up to 20 completed jobs per entry for one hour. HA restart discards job history and changes the runtime generation; no queued/draft update is replayed. If no history remains, inspect the controller and current HA observations before starting again.

Drafts are in-memory only. Page reload warns about unsaved changes and never submits them. Changing the configured device prompts Save/Discard/Stay. Save or cancel before navigating away from the dashboard; a destroyed card cannot retain its draft. A browser disconnect does not automatically cancel an already dispatched operation.

## Troubleshooting

- **Unknown**: missing/invalid data or an unset date; it is never filled with an invented zero.
- **Edit absent/disabled**: check entity permissions, integration write option, unavailable/disabled controls, other active saves and matching backend/card versions.
- **Version mismatch/custom element missing**: install the entire 1.3.2 integration, register the module resource, restart HA and reload the browser cache.
- **Time-template conflict**: affected slots have incompatible preserved metadata. Capture the observed encodings for investigation; do not discard timezone/opaque suffixes to force a write.
- **Invalid date path**: no sequence of the requested single-pin updates preserves a valid calendar. No writes were dispatched.

## Offline preview and development

From the development archive's `frontend` directory, use Node 24 and npm:

```bash
npm ci
npm run typecheck
npm run lint
npm test
npm run build
npx playwright install chromium
npm run test:e2e
```

For a local mock preview, run `python3 -m http.server 8767 --bind 127.0.0.1` from the development root and open `http://127.0.0.1:8767/frontend/demo/`. Query examples: `?mode=Seasonal&dark`, `?kind=controller`, `?channel=Blue&count=2`. The mock host contains no credentials and does not call the vendor.

Hardware acceptance is separate from these offline tests: verify final Multi compaction, cleared-tail interpretation, intermediate effects and persistence on each controller model/firmware. No live controller was operated during development of this release.

## Timeline layout and temperature colours

Each seasonal row has its own target slider directly below the timeline in Edit mode. Select a boundary to choose Day/Night or a Multi point, then adjust its target. The label names the target and its start time. Slot tables are collapsed initially in both viewing and editing; expand a row's **slot table** to enter exact times/values. Save/Cancel retain the same local-draft behavior.

Default temperature colours progress from amber through orange to red, with inclusive lower bounds at 0, 20, 25, 30 and 35 °C. Both pieces of a slot spanning midnight have the same colour and hatching. A point starting at exactly midnight does not create a split slot.

Open the channel card's visual configuration editor, expand **Temperature colours**, and edit each lower temperature bound and colour. Add/remove thresholds or reset to defaults. Thresholds always use Celsius, even if HA displays Fahrenheit; percentage targets use teal and are not interpreted as temperatures. Colours are discrete bands, not interpolated. Below the lowest configured threshold uses that threshold's colour. Labels automatically choose black or white for contrast.

Equivalent YAML (unique numeric bounds 0–100, six-digit hexadecimal colours; ordering is automatic):

```yaml
type: custom:microclimate-channel-card
device_id: YOUR_CHANNEL_DEVICE_ID
temperature_colors:
  - temperature: 0
    color: "#f6c85f"
  - temperature: 22
    color: "#f5a623"
  - temperature: 26
    color: "#ef7d16"
  - temperature: 30
    color: "#d94b24"
  - temperature: 35
    color: "#b52222"
```
