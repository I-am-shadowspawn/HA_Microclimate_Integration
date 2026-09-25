import { describe, it, expect } from "vitest";
import {
  clock,
  parseClock,
  dateError,
  displayValue,
  nativeValue,
  makeDraft,
  dirty,
  patchFor,
  pointError,
  segments,
} from "../src/draft";
import { fixture } from "./snapshot";
describe("lossless draft and controller contract", () => {
  it("retains seconds and does not write on import", () => {
    const v = fixture();
    v.fields[1].value = 3661;
    const d = makeDraft(v);
    expect(clock(d.points[0].seconds)).toBe("01:01:01");
    expect(dirty(d)).toBe(false);
  });
  it("deletes with a compact full logical list", () => {
    const d = makeDraft(fixture("Multi", 8));
    d.points.splice(2, 1);
    const p = patchFor(d) as any;
    expect(p.schedule.points.map((v: any) => v.target_native)).toEqual([
      21, 22, 24, 25, 26, 27, 28,
    ]);
    expect(pointError(d)).toBe(null);
  });
  it("enforces minimum and reserved zero pair", () => {
    const d = makeDraft(fixture("Multi", 2));
    d.points.pop();
    expect(pointError(d)).toMatch("2–8");
    d.points.push({ draft_id: "x", seconds: 0, target_native: 0 });
    expect(pointError(d)).not.toBe(null);
  });
  it("detects holes instead of silently compacting", () => {
    const v = fixture();
    v.fields[3].value = 0;
    v.fields[4].value = 0;
    expect(makeDraft(v).repair).toBe(true);
  });
  it("has four named pairs for Seasonal", () =>
    expect(makeDraft(fixture("Seasonal", 8)).points).toHaveLength(8));
  it.each(["24:00:00", "23:60:00", "25:01", "-1:00"])(
    "rejects invalid clock %s",
    (v) => expect(parseClock(v)).toBe(null),
  );
  it("round trips exact seconds", () =>
    expect(parseClock(clock(86399))).toBe(86399));
  it.each([
    [["09/10", "01/01", "01/06", "01/07"], null],
    [["01/01", "02/12", "01/04", "01/11"], "cycle"],
    [["01/05", "01/09", "01/01", "01/03"], null],
    [["20/02", "01/02", "30/06", "20/06"], "cycle"],
    [["29/02", "01/04", "01/06", "01/08"], "calendar"],
  ])("validates calendar and cyclic order %j", (dates, error) => {
    const result = dateError(dates as string[]);
    if (error) expect(result).toContain(error);
    else expect(result).toBe(null);
  });
  it("converts Fahrenheit once and leaves percentage alone", () => {
    expect(
      nativeValue(displayValue(25.125, "°C", true), "°C", true),
    ).toBeCloseTo(25.125, 12);
    expect(displayValue(25, "%", true)).toBe(25);
  });
  it("renders carry-over without moving a physical day/night point", () => {
    const d = makeDraft(fixture("Day Night", 2));
    const rows = segments(d.points);
    expect(rows[0].carry).toBe(true);
    expect(d.points[0].source_slot).toBe(1);
  });
});
