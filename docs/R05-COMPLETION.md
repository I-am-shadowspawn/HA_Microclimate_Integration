# R-05 — Seasonal completion status

> **Unofficial, independent project.** This integration and its custom cards are not affiliated with, endorsed by, or supported by Microclimate. Their only connection to Microclimate is that they work with its products. Product names are used solely to identify compatibility. For integration support, use this project’s [GitHub Issues](https://github.com/I-am-shadowspawn/HA_Microclimate_Integration/issues).

Reviewed against candidate 1.0.7 and the maintainer confirmations.

**The read-only Seasonal configuration view is implemented. R-05 as originally written also requires controller behaviour validation, so it cannot yet be marked fully complete.** No additional pin mapping is needed to display the confirmed settings. This review makes documentation/checklist corrections only; no new installation package or integration code change is required.

## Already complete

| Requirement | Evidence / implementation |
|---|---|
| Seasonal timing codes | Yellow/all models and Red/Evo III: 3; Blue/all models: 4. Evo II captures verify both channel codes; shared capability families are maintainer-confirmed. |
| Four seasons with day/night settings | Yellow v32–v47, Red v62–v77, Blue v92–v107. Each consecutive pair of schedule points is one season's day/night pair. Confirmed and implemented. |
| Season start-date ordering | Root v20/v21/v22/v23 are Season 1/2/3/4, DD/MM. Maintainer confirms the order and a Season 1 example 09/02. |
| Data scope and representation | One root date set is attached to each channel's Seasonal observations; per-channel time/setpoint pairs remain separate. Raw values, source pins and date validity are retained. |
| Ramp capability | Yellow v48 and Red v78 are minutes. Blue has no ramp or pulse/dimming selection. Implemented. |
| Missing, zero and invalid dates | Software distinguishes absent, invalid, supported calendar dates and the 00/00 sentinel. It does not invent an active season or treat 00/00 as disabled. |
| Read-only display and tests | `seasons.season_1` through `season_4`, each with start_date/day/night, appear only in Seasonal mode. Existing tests cover all three channel layouts and date parsing. Candidate 1.0.7's recorded matrix passed 458 tests per HA version in both modes; no tests rerun for this documentation-only review. |

## Evidence still needed to close the original R-05

| ID | Question / controlled experiment | Completion evidence |
|---|---|---|
| S-01 — zero dates | With one valid season date and others 00/00, what season does the controller actually select? If possible, compare with a second valid date, changing only that date. | Establish whether 00/00 means disabled/unset, fallback or another rule, including the all-zero case. The API value alone does not answer this. |
| S-02 — boundaries and shared date scope | Use four distinct valid start dates and clearly distinguishable but appropriate day/night setpoints. Observe a season boundary with two channels in Seasonal mode; record controller time/timezone, display and API before/after. | Confirm dates select the corresponding season, whether selection changes at local midnight or another time, and whether the root dates govern both channels. Record which day's/night's setting is applied at the boundary. |
| S-03 — year rollover and date ordering | On a controlled test device, observe December→January, including a date before the first nonzero season start. If the app allows duplicate or out-of-order season dates, record acceptance and actual selection. | Establish last-season carry-over, date-ordering requirements and duplicate-date handling, or document that the app rejects those configurations. Do not infer a selection rule from sorted dates alone. |
| S-04 — leap-day behaviour | Check whether the app accepts 29/02 and how the controller handles it in leap and non-leap years, using a suitable test setup or observed behaviour. | Establish rejection, skipping, date adjustment or other behaviour. The parser's ability to represent a recurring 29/02 is not evidence of the controller's rule. |

For each result, record model, firmware, anonymous device label, actual displayed settings/time, the single configuration change, and repeated getAll samples before/after. Display confirmation or existing reliable observations can establish a rule; otherwise the controlled experiment is needed. Use a test controller for date/time manipulation because it can affect outputs. No device writes or clock changes have been performed by this review.

These remaining checks validate the original controller contract. They are not a reason to add guessed season-selection logic to the current read-only integration. Full model/firmware support sweeps remain under V-01/V-02/R-01; write semantics remain under W tasks. Physical ramp progression is a separate behaviour check, not an unresolved Seasonal pin mapping.

## Checklist treatment

- R-05 implementation: complete for the confirmed configuration contract.
- R-05 controller behaviour validation: pending S-01 through S-04.
- Original R-05 parent item remains open until the required evidence exists.

The original repository and all released candidate ZIPs are unchanged. See `microclimate_TODO.md` for the updated active checklist.
