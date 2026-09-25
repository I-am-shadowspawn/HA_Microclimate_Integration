# Observation and edit validation contract

This is an unofficial, independent integration, not affiliated with, endorsed by or supported by Microclimate. Product names identify compatibility only.

The executable examples are [validation_contract.json](../fixtures/validation_contract.json). Both Python and TypeScript tests load that same reviewed, synthetic file. These examples distinguish reported data from values a user may write; applying edit limits to all observations would lose useful controller information.

## Contract

| Value | Observation | Edit |
| --- | --- | --- |
| Temperature | Parse finite Celsius readings, including negative values and values above 100. A misleading °F suffix remains the documented upstream Celsius nuance. | Finite 0–100 inclusive, in native Celsius. Fahrenheit is a card display/input conversion only. |
| Output/setpoint percentage | Output percentage observations accept only 0–100; invalid values are unknown. Fixed-output schedule setpoints use percent. | Finite 0–100 inclusive. Never Fahrenheit-convert percent. |
| Ramp minutes | Finite nonnegative observations remain reportable, including fractional values and values above the edit maximum. | Whole minutes 0–240 inclusive; only channels exposing the mapped control. |
| Missing/non-finite | Unknown; never silently replace with zero. The card retains unknown projected values. | Reject null, booleans, NaN, infinity and invalid types. Backend native numeric controls also accept numeric strings/Decimal; JSON card drafts and preset points require numbers. This adapter difference is deliberate. |
| Season date | Preserve raw values, unset `00/00`, yearless leap possibilities and short-year uncertainty under the observation parser. | Exact ASCII `DD/MM`, normal non-leap calendar bounds. No `29/02`, year suffix, whitespace or writing `00/00`. Existing unset sibling dates may remain unset. |
| Season order | Report what the controller returns. | Known non-unset dates must be distinct and follow one annual cycle, allowing a year rollover. Missing or malformed sibling dates block validation. |
| Time | Preserve raw time strings and opaque metadata, even when an interpretation is unavailable. | Whole seconds 0–86399. The backend accepts naive whole-second time objects for native serialization; JSON drafts use integer seconds. |
| Mode/options | Unknown enum values stay unknown. Integral numeric representations are normalized for observed values. | Require an exact supported option label from the model/channel field definition. Yellow/Red and Blue have different timing families; Evo Connect Blue is fixed-output only. |
| Schedule shape | Incomplete/unknown schedules remain observable; do not normalize them into editable defaults. | Day/Night has 2 points; Seasonal has 8 (four day/night pairs); Multi has 2–8 strictly increasing times. Duplicate daily boundaries are invalid. Multi's `00:00:00`/0 pair is reserved for unused trailing slots. Active points are consecutive. |

Unchanged values are not edits. A local draft may therefore retain observations that cannot be written. Whole-schedule changes must validate the complete submitted schedule. Authentication, entity permissions, write availability, stale-context checks and readback confirmation remain separate server checks.

Time writes replace only the two verified leading clock fields and retain the complete NUL-delimited suffix. Mismatched clocks, unsupported encodings or unknown timezones are rejected. The card sends seconds only; it never reconstructs vendor wire strings. Backend inference for scalar times still requires safe sibling timezone evidence.

## Ownership and consolidation audit

| Previously duplicated rule | Current owner/consumers |
| --- | --- |
| Numeric maxima in write validation, number entities and card metadata | Python `constraints.py`; `write_contract.py`, `number.py`, `card_model.py` consume it. Observation parsing in `validation.py` remains separate. |
| Seconds and point counts in backend draft/preset validation | Python `constraints.py`; `edit_plan.py`, `schedule_templates.py`, `card_model.py` use compatible helpers. |
| Numeric/seconds/count checks in card draft and preset import | TypeScript `constraints.ts`; `draft.ts` and `preset.ts` consume it. Shared vectors catch cross-language drift. |
| Strict date parsing in annual-order and changed-field checks | TypeScript `dateOrdinal`; Python `date_string` remains the server authority. Changed unset dates are rejected before Save, as on the server. |
| Model enum families, pin applicability and native units | Canonical Python pin/capability definitions and `write_contract.py`; the card consumes projected options, writable state and units. No second TypeScript model table. |
| Observation date/time interpretation vs vendor encoding | Python `schedule.py` observes; `write_contract.py` serializes. The two are intentionally not merged. |

The vectors cover enum families, unknown/non-finite values, Celsius/percent behavior, 0/100 and 0/240 boundaries, date ordering and leap/sentinel dates, time bounds/opaque suffixes, schedule cardinality and model/channel applicability. Python asserts actual projection and serialization. TypeScript asserts draft/preset validation and consumption of server-owned metadata, without pretending to parse the vendor response itself.

## Maintaining the contract

Add a vector with separate observation and edit expectations before changing a rule. Both test suites must pass. Preserve deliberate adapter differences explicitly instead of broadening coercion to make tests agree. The fixture is included in the development archive and contains no tokens or real device identifiers.

```sh
.matrix/ha-2026.9.3/bin/python -m pytest -c pytest-review.ini tests/test_validation_contract_vectors.py
cd frontend
npx vitest run test/validation-contract.test.ts
```

See [testing instructions](../README-TESTING.md) for creating the locked environment and running the complete release gate. Version 1.4.1 changes no entity IDs, pin mappings, transport behavior or observation limits.
