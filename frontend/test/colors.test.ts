import { describe, it, expect } from "vitest";
import {
  colorFor,
  validateColors,
  targetColors,
  textColor,
} from "../src/colors";
import { segments } from "../src/draft";
describe("temperature colours", () => {
  it("uses inclusive ordered lower bounds with a lowest fallback", () => {
    const stops = [
      { temperature: 30, color: "#ff0000" },
      { temperature: 20, color: "#ffaa00" },
    ];
    expect(colorFor(0, stops)).toBe("#ffaa00");
    expect(colorFor(29.9, stops)).toBe("#ffaa00");
    expect(colorFor(30, stops)).toBe("#ff0000");
    expect(colorFor(100, stops)).toBe("#ff0000");
    expect(colorFor(null)).toBe("#737373");
    expect(targetColors(100, "%", stops)).toContain("#327b80");
    expect(textColor("#ffffff")).toBe("#000000");
    expect(textColor("#000000")).toBe("#ffffff");
  });
  it("rejects unsafe colours and invalid or duplicate thresholds", () => {
    for (const value of [
      [],
      null,
      [{ temperature: NaN, color: "#ffffff" }],
      [{ temperature: -1, color: "#ffffff" }],
      [{ temperature: 101, color: "#ffffff" }],
      [{ temperature: 0, color: "red;display:none" }],
      [
        { temperature: 0, color: "#ffffff" },
        { temperature: 0, color: "#000000" },
      ],
    ])
      expect(() => validateColors(value)).toThrow();
    expect(() => validateColors(undefined)).not.toThrow();
  });
  it("marks both pieces of a midnight crossing and neither for a midnight boundary", () => {
    const points = [
      { draft_id: "day", seconds: 7200, target_native: 20 },
      { draft_id: "night", seconds: 72000, target_native: 30 },
    ];
    const result = segments(points);
    expect(result.filter((s) => s.carry).map((s) => s.point.draft_id)).toEqual([
      "night",
      "night",
    ]);
    expect(
      segments([{ ...points[0], seconds: 0 }, points[1]]).some((s) => s.carry),
    ).toBe(false);
  });
});
