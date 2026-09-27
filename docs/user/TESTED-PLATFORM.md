# Tested platform and initial public support baseline

> **Unofficial, independent project.** This integration and its custom cards are not affiliated with, endorsed by, or supported by Microclimate. Their only connection to Microclimate is that they work with its products. Product names are used solely to identify compatibility. For integration support, use this project’s [GitHub Issues](https://github.com/I-am-shadowspawn/HA_Microclimate_Integration/issues).

Confirmed by the maintainer on 25 September 2026 as the platform with full integration testing:

| Component | Version |
|---|---|
| Home Assistant Core | 2026.9.3 |
| Supervisor | 2026.09.2 |
| Home Assistant Operating System | 18.2 |
| Frontend | 20260826.7 |

The initial HACS minimum is Home Assistant Core 2026.9.3. Supervisor, OS and Frontend versions record the tested environment; they are not independent dependencies of this custom integration. Other installation types have not been established as fully tested by this report.

Automated integration suites also passed on Core 2026.9.2, but that does not lower the selected public minimum. Exact installed Microclimate release was not specified in this platform confirmation; do not infer new 1.3.0 clean-install or future V2/HACS acceptance from it. Future releases must validate the declared minimum and then-current supported stable Core version.

## Controller and firmware evidence

This matrix separates captured API responses from the maintainer's controller/app confirmations. A firmware version describes the captured controller, not a minimum or a promise that every release of that firmware has been tested. The detailed per-mode capture ledger is in the [schedule contract](../technical/SCHEDULE-CONTRACT.md).

| Model | Channels | Captured API evidence | Maintainer-confirmed behavior | Still unverified |
|---|---|---|---|---|
| Evo Connect | Yellow, Blue | Firmware 0.2.6: both channels reported Day Night in sanitized responses; no explicitly labelled mode-change sequence for other modes. | Yellow supports Constant, Day Night, Multi and Seasonal; Blue also supports Periodic. | Independent labelled mode/write sweeps, persistence and boundary behavior on this model. |
| Evo Connect II | Yellow, Blue | Firmware 0.2.4: labelled captures cover Constant, Day Night, Multi and Seasonal on Yellow, and those modes plus Periodic on Blue. | The maintainer confirmed all then-enabled configuration attributes on this model. | Firmware-specific persistence, conflicts, interrupted writes and long-running stability; the captured write logs do not identify their controller firmware. |
| Evo Connect III | Yellow, Red, Blue | Firmware 0.2.4: sanitized responses show Day Night on all three channels; other modes have no independently labelled capture sequence in the current ledger. | Yellow and Red share Constant, Day Night, Multi and Seasonal options; Blue also supports Periodic. The maintainer confirmed all then-enabled configuration attributes on this model. | Independent labelled mode sweeps, firmware-specific persistence and interrupted-write behavior. |
| Evo Connect Pro | Unknown | None. | None. | Compatibility, channels, firmware and all behavior. |

For every model, a reported timing mode does not establish a writable Constant target or Blue Periodic interval/duration. Those edits remain unavailable. The integration reads the controller-reported `C` or `F` unit with each response and keeps temperature numbers in that unit; see [write controls](WRITE-CONTROLS.md) for edit bounds. Controller-to-cloud communication is required; there is no local fallback.
