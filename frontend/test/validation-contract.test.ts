import { describe, expect, it } from "vitest";
import vectors from "../../fixtures/validation_contract.json";
import { boundedNumber, validSeconds } from "../src/constraints";
import { clock, parseClock, dateError, errorFor, makeDraft, pointError, displayValue, nativeValue, patchFor } from "../src/draft";
import { importPreset, PRESET_FORMAT } from "../src/preset";
import { fixture } from "./snapshot";
import type { Field, Point } from "../src/types";

function decoded(value: unknown): unknown {
  if (value && typeof value === "object" && "special" in value) {
    return { nan: NaN, infinity: Infinity, negative_infinity: -Infinity }[value.special as "nan"];
  }
  return value;
}
function fieldDraft(kind: string, value: unknown, maximum = 100) {
  const base = fixture();
  base.fields = [{ ...base.fields[0], key: "edit", kind, value: -999, maximum, options: [] }];
  const draft = makeDraft(base);
  draft.values.edit = value as Field["value"];
  return draft;
}

describe("shared observation/edit contract vectors", () => {
  it.each(vectors.numbers)("numeric boundaries $value", (row) => {
    const value = decoded(row.value);
    expect(boundedNumber(value)).toBe(row.draft_number);
    expect(errorFor(fieldDraft("number", value)) === null).toBe(row.draft_number);
    expect(errorFor(fieldDraft("ramp", value, 240)) === null).toBe(row.draft_ramp);
    // Backend observations outside edit bounds are displayed and retained, not clamped.
    const base = fixture("Day Night", 2);
    base.fields.find(f => f.key === "Yellow_period_1_setpoint")!.value = row.observation_temperature;
    expect(makeDraft(base).points[0].target_native).toBe(row.observation_temperature);
    if (row.observation_temperature !== null) {
      const n = row.observation_temperature;
      expect(nativeValue(displayValue(n, "°C", true), "°C", true)).toBeCloseTo(n, 10);
      expect(displayValue(n, "%", true)).toBe(n);
    }
  });
  it.each(vectors.seconds)("whole seconds $value", row => {
    const value = decoded(row.value);
    expect(validSeconds(value)).toBe(row.valid);
    if (validSeconds(value)) expect(parseClock(clock(value))).toBe(value);
  });
  it.each(vectors.dates)("changed season date $value", row => {
    const draft = fieldDraft("date", row.value);
    draft.base.channel = null;
    expect(errorFor(draft) === null).toBe(row.edit_valid);
  });
  it.each(vectors.annual_cycles)("annual order $dates", row => {
    expect(dateError(row.dates) === null).toBe(row.valid);
  });
  it.each(vectors.enums)("server enum family $model $key", row => {
    for (const [value, valid] of row.edits) {
      const draft = fieldDraft("enum", value);
      draft.base.fields[0].options = row.options;
      expect(errorFor(draft) === null).toBe(valid);
    }
  });
  it.each(vectors.schedules)("schedule shape $mode $points", row => {
    const draft = makeDraft(fixture(row.mode));
    draft.points = row.points.map((point, index) => ({ ...point, draft_id: String(index) }));
    expect(pointError(draft) === null).toBe(row.valid);
    const template = { format: PRESET_FORMAT, mode: row.mode, unit: "celsius", points: row.points };
    if (row.valid) expect(importPreset(draft, template).points).toHaveLength(row.points.length);
    else expect(() => importPreset(draft, template)).toThrow();
  });
  it.each(vectors.applicability)("honours server edit applicability $model $channel $slot", row => {
    // Profile/mode applicability is calculated by Python; the card consumes writable/options/unit.
    const draft = fieldDraft("setpoint", 25);
    draft.base.fields[0].writable = row.writable;
    draft.base.fields[0].unit = row.unit;
    expect(errorFor(draft) === null).toBe(row.writable);
    expect(nativeValue(displayValue(25, row.unit, true), row.unit, true)).toBeCloseTo(25, 10);
  });
  it.each(vectors.time_encoding)("time edit carries seconds only $raw", row => {
    const base = fixture("Day Night", 2);
    base.fields.find(f => f.key === "Yellow_period_1_time")!.value = row.observed_seconds;
    const draft = makeDraft(base);
    expect(draft.points[0].seconds).toBe(row.observed_seconds);
    draft.points[0].seconds = row.seconds;
    const patch = patchFor(draft) as { schedule: { points: Point[] } };
    expect(patch.schedule.points[0].seconds).toBe(row.seconds);
    expect(JSON.stringify(patch)).not.toContain("Europe/London");
    // Opaque fields are owned and preserved by backend serialization, never reconstructed here.
  });
});
