import { describe, expect, it } from "vitest";
import { makeDraft, dirty } from "../src/draft";
import { exportPreset, importPreset } from "../src/preset";
import { fixture } from "./snapshot";

describe("portable schedule presets", () => {
  it("exports only native schedule values, without device identity or credentials", () => {
    const preset = exportPreset(makeDraft(fixture("Multi", 3)));
    expect(preset).toEqual({
      format: "microclimate.schedule.v1",
      mode: "Multi",
      unit: "celsius",
      points: [
        { seconds: 3600, target_native: 21 },
        { seconds: 7200, target_native: 22 },
        { seconds: 10800, target_native: 23 },
      ],
    });
    expect(JSON.stringify(preset)).not.toContain("device_id");
  });

  it("imports as a local draft, leaving the source snapshot unchanged", () => {
    const base = fixture("Multi", 2);
    const draft = makeDraft(base);
    const preset = exportPreset(makeDraft(fixture("Multi", 3)));
    const imported = importPreset(draft, preset);
    expect(imported.points).toHaveLength(3);
    expect(dirty(imported)).toBe(true);
    expect(dirty(draft)).toBe(false);
    expect(base.fields.find((f) => f.key === "Yellow_period_3_time")?.value).toBe(0);
  });

  it("blocks a different mode, unit and invalid point sequence", () => {
    const draft = makeDraft(fixture("Multi", 3));
    const preset = exportPreset(draft);
    expect(() => importPreset(draft, { ...preset, unit: "percent" })).toThrow("unit");
    expect(() => importPreset(draft, { ...preset, mode: "Seasonal" })).toThrow("mode");
    expect(() => importPreset(draft, { ...preset, points: [...preset.points].reverse() })).toThrow("chronological");
    expect(() => importPreset(draft, { ...preset, points: [{ seconds: 0, target_native: 0 }, preset.points[1]] })).toThrow("reserved");
  });
});
