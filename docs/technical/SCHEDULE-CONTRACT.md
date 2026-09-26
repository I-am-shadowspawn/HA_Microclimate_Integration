> **Unofficial, independent project.** This integration and its custom cards are not affiliated with, endorsed by, or supported by Microclimate. Their only connection to Microclimate is that they work with its products. Product names are used solely to identify compatibility. For integration support, use this project’s [GitHub Issues](https://github.com/I-am-shadowspawn/HA_Microclimate_Integration/issues).

> **Maintainer follow-up, 24 September 2026:** functional testing of all enabled 1.1.0 attributes on Evo II and Evo III is confirmed by the maintainer. The report supplies no new capture or firmware attribution. Yellow/Red ramp writes (0–240 whole minutes) and cyclic season-order validation are added in 1.1.1 and need their own live acceptance. This confirmation supplements the earlier capture ledger; it does not claim reboot/persistence or boundary/soak tests.

> **Scope correction, candidate 1.0.8:** the maintainer confirms all schedules are manually timed. Sunrise/sunset automation and solar offsets are unsupported, so historical solar capture/research/editor items below are withdrawn. Unknown encoded fields remain raw; no solar semantics are inferred. R-06 is closed as not applicable. R-07 is implemented with readable live summaries and recorder exclusions; live UI/soak checks remain V-04/V-06.

# Schedule contract and R-01–R-03 evidence ledger

Source: 48 sanitized responses from 12 runs; Evo I firmware 0.2.6, Evo II/III firmware 0.2.4. This ledger records existing evidence; it does not claim new hardware experiments.

## Status

- **R-01: partial.** Evidence is indexed below and in `fixtures/schedule_contract.json`. Independent model/firmware sweeps and physical edge cases remain hardware-dependent. Solar functionality is unsupported, not an outstanding capture requirement.
- **R-02: implemented for established semantics.** Supported raw values/fields are retained; typed observations expose presence/validity and source pins. Unknown semantics remain explicitly unsupported/unverified rather than guessed.
- **R-03: read-only implementation complete; physical validation partial.** First two pairs are Day/Night; Multi exposes eight daily points. Midnight/duplicate behaviour is preserved and tested as data, not simulated as controller execution.

## Per-model mode coverage

“Labelled” requires an explicit operator label retained with that run. A raw code is weaker evidence. Maintainer confirmations of shared capability families supplement this matrix.

| Model | Channel | Mode / code | Observed runs | Explicitly labelled runs |
|---|---|---|---|---|
| Evo Connect | Yellow | Constant / 0 | none | none |
| Evo Connect | Yellow | Day Night / 1 | 20260923T154221Z-kwxxrllz, 20260923T154234Z-1u_yj_mu | none |
| Evo Connect | Yellow | Multi / 2 | none | none |
| Evo Connect | Yellow | Seasonal / 3 | none | none |
| Evo Connect | Blue | Constant / 0 | none | none |
| Evo Connect | Blue | Day Night / 1 | 20260923T154221Z-kwxxrllz, 20260923T154234Z-1u_yj_mu | none |
| Evo Connect | Blue | Multi / 2 | none | none |
| Evo Connect | Blue | Periodic / 3 | none | none |
| Evo Connect | Blue | Seasonal / 4 | none | none |
| Evo Connect 2 | Yellow | Constant / 0 | 20260923T154258Z-naxlheci, 20260923T160504Z-w0x9t9hf, 20260923T161425Z-h68vr6tv | 20260923T160504Z-w0x9t9hf, 20260923T161425Z-h68vr6tv |
| Evo Connect 2 | Yellow | Day Night / 1 | 20260923T161243Z-0t5chryz, 20260923T161619Z-bxa27uzc | 20260923T161243Z-0t5chryz, 20260923T161619Z-bxa27uzc |
| Evo Connect 2 | Yellow | Multi / 2 | 20260923T161340Z-9ybnn1ih | 20260923T161340Z-9ybnn1ih |
| Evo Connect 2 | Yellow | Seasonal / 3 | 20260923T155359Z-o8nx14qu, 20260923T160254Z-6cextzcs | 20260923T160254Z-6cextzcs |
| Evo Connect 2 | Blue | Constant / 0 | 20260923T161425Z-h68vr6tv | 20260923T161425Z-h68vr6tv |
| Evo Connect 2 | Blue | Day Night / 1 | 20260923T161619Z-bxa27uzc | 20260923T161619Z-bxa27uzc |
| Evo Connect 2 | Blue | Multi / 2 | 20260923T161340Z-9ybnn1ih | 20260923T161340Z-9ybnn1ih |
| Evo Connect 2 | Blue | Periodic / 3 | 20260923T154258Z-naxlheci, 20260923T155359Z-o8nx14qu, 20260923T160254Z-6cextzcs, 20260923T160504Z-w0x9t9hf | 20260923T160254Z-6cextzcs, 20260923T160504Z-w0x9t9hf |
| Evo Connect 2 | Blue | Seasonal / 4 | 20260923T161243Z-0t5chryz | 20260923T161243Z-0t5chryz |
| Evo Connect 3 | Yellow | Constant / 0 | none | none |
| Evo Connect 3 | Yellow | Day Night / 1 | 20260923T154209Z-0oobijyl, 20260923T154246Z-in_re18s | none |
| Evo Connect 3 | Yellow | Multi / 2 | none | none |
| Evo Connect 3 | Yellow | Seasonal / 3 | none | none |
| Evo Connect 3 | Red | Constant / 0 | none | none |
| Evo Connect 3 | Red | Day Night / 1 | 20260923T154209Z-0oobijyl, 20260923T154246Z-in_re18s | none |
| Evo Connect 3 | Red | Multi / 2 | none | none |
| Evo Connect 3 | Red | Seasonal / 3 | none | none |
| Evo Connect 3 | Blue | Constant / 0 | none | none |
| Evo Connect 3 | Blue | Day Night / 1 | 20260923T154209Z-0oobijyl, 20260923T154246Z-in_re18s | none |
| Evo Connect 3 | Blue | Multi / 2 | none | none |
| Evo Connect 3 | Blue | Periodic / 3 | none | none |
| Evo Connect 3 | Blue | Seasonal / 4 | none | none |

## Observation contract

- `periods` always retains all eight mapped pairs and their source pins. `reported_period_count` counts reported data, not enabled or valid periods.
- `day_night.day` and `.night` reference periods 1 and 2 only. Other returned slots remain in `periods` without being claimed applicable.
- `daily_points` exists only in Multi and retains controller slot order. `duplicate_clock_times` lists repeated parsed clock times without choosing precedence.
- `seasons` exists only in Seasonal; each of the four groups contains a root `start_date`, day and night. A zero date is a `sentinel`, not automatically a disabled season.
- `start.status` and `setpoint_status`: `absent` (pin omitted), `invalid` (present but malformed/out of range/null after API normalization), `unsupported` (unrecognized encoding or unknown control semantics), or `valid`. Valid zero is retained.
- `activation=likely_unused` in Multi identifies a parsed midnight/zero-setpoint pair, with `activation_evidence=maintainer_inference_not_explicit_enable_flag`. The pair remains present. Other points remain `activation=unverified`; no explicit enabled/disabled flag is fabricated.
- Clock tokens have typed interpretations; unexpected solar tokens remain unsupported raw input. Every accepted NUL-separated field remains in `fields` and `raw`; unassigned fields retain their indexes in `opaque_fields`. Timezone recognition is independent of clock parsing. No offsets or day masks are guessed.
- Losslessness applies to accepted, bounded scalar payloads. The existing API boundary normalizes non-finite numbers/containers to null; bounded observation rejects oversized/control-character values. These cannot be reconstructed here. Raw capture/debug evidence remains the source for rejected inputs.
- Temperature/fixed-percentage and nonnegative ramp validation remain shared with the integration. Periodic values stay unparsed until their units are established.

## Remaining controlled tests (R-01/R-03)

1. Evo I and Evo III: independently capture every supported timing mode per channel, with firmware/display labels. Unsupported Periodic on Yellow/Red must not be forced.
2. Preserve unknown extra encoded fields in manual clock captures. Assign meanings only after a corresponding supported setting is independently observed; do not seek unsupported sunrise/sunset controls.
3. Multi: compare a default midnight/zero pair with an intentionally configured midnight/zero point, if the app allows it; establish whether those are distinguishable.
4. Duplicate times: assign two different safe setpoints at one time on a controlled test setup and observe actual precedence. Preserve both in HA until verified.
5. Midnight: observe a transition across midnight, including which prior-day setpoint carries forward. Confirm actual controller output/setpoint rather than calculating it from stored times.
6. Toggle Day Night/Multi and return: capture whether all eight stored pairs persist, reset or are rewritten. Check one channel changes without collateral edits to another.

No live controller writes or execution-engine assumptions are part of this implementation.
