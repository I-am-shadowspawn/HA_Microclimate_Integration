# Microclimate 1.2.2 — channel card presentation

> **Unofficial, independent project.** This integration and its custom cards are not affiliated with, endorsed by, or supported by Microclimate. Their only connection to Microclimate is that they work with its products. Product names are used solely to identify compatibility. For integration support, use this project’s [GitHub Issues](https://github.com/I-am-shadowspawn/HA_Microclimate_Integration/issues).

Implemented the requested card changes:

- Target slider immediately beneath each timeline (including one per seasonal row), with target name, start time and value. Slot tables collapse initially; expand for precise entry.
- Temperature colours depend on native Celsius values, with amber/orange/red defaults. Configurable inclusive lower bounds and six-digit hex colours in YAML and the visual card editor. Unordered thresholds are sorted for lookup; invalid/duplicate thresholds are rejected. Values below the first threshold use that colour. Fahrenheit display does not change the native thresholds; percentage targets remain teal. Text chooses black or white for contrast.
- Midnight-spanning slots use the same colour and hatching on both sides. A boundary at midnight is not marked as a split slot.

Explicit Save/Cancel and server validation/write paths remain unchanged. No integration Python source changed, verified byte-for-byte against 1.2.1. No live device requests or original-repository edits.

## Validation

Strict TypeScript, ESLint, production build, 21 unit tests and 43 Chromium browser tests passed. Browser regressions cover collapsed tables, sliders beside their respective row, local-only edits, configurable colours, Fahrenheit consistency, midnight continuity and visual-editor validation, plus previous Save/Cancel/loading/date-input tests. Desktop seasonal edit and 320-pixel dark seasonal previews were visually inspected.

The focused 38-test HA card/API suite passed on HA 2026.9.3. The full historical HA matrix was not rerun for this frontend-only change.

## Install

Replace the integration using the install ZIP and restart HA. Edit the existing JavaScript module resource to `/microclimate_integration/microclimate-cards.js?v=1.2.2`, then hard-refresh/reload the frontend. Existing cards do not need recreation. See CARD-USAGE.md for configuration examples. Real dashboard acceptance remains with the user.
