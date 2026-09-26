import { message } from "./localize";
import { newId } from "./id";
import { boundedNumber, validSeconds, validPointCount, dateOrdinal } from "./constraints";
import type { Draft, Snapshot, Point } from "./types";
export const isEmpty = (p: Point) => p.seconds === 0 && p.target_native === 0;
export const clock = (seconds: number | null) =>
  seconds === null
    ? ""
    : `${Math.floor(seconds / 3600)
        .toString()
        .padStart(2, "0")}:${Math.floor((seconds / 60) % 60)
        .toString()
        .padStart(2, "0")}:${(seconds % 60).toString().padStart(2, "0")}`;
export function parseClock(value: string): number | null {
  if (!/^\d{2}:\d{2}(:\d{2})?$/.test(value)) return null;
  const [h, m, s = 0] = value.split(":").map(Number);
  return h < 24 && m < 60 && s < 60 ? h * 3600 + m * 60 + s : null;
}
export const displayValue = (
  n: number,
  unit: string | null,
  fahrenheit: boolean,
) => (unit === "°C" && fahrenheit ? (n * 9) / 5 + 32 : n);
export const nativeValue = (
  n: number,
  unit: string | null,
  fahrenheit: boolean,
) => (unit === "°C" && fahrenheit ? ((n - 32) * 5) / 9 : n);
export function makeDraft(base: Snapshot): Draft {
  const mode = String(
    base.fields.find((f) => f.key === `${base.channel}_timing_type`)?.value ??
      "",
  );
  const points: Point[] = [];
  const count =
    mode === "Day Night" ? 2 : ["Multi", "Seasonal"].includes(mode) ? 8 : 0;
  for (let i = 1; i <= count; i++)
    points.push({
      draft_id: newId(),
      source_slot: i,
      seconds:
        (base.fields.find((f) => f.key === `${base.channel}_period_${i}_time`)
          ?.value as number) ?? null,
      target_native:
        (base.fields.find(
          (f) => f.key === `${base.channel}_period_${i}_setpoint`,
        )?.value as number) ?? null,
    });
  if (mode === "Multi")
    while (points.length && isEmpty(points.at(-1)!)) points.pop();
  const d = {
    base,
    values: Object.fromEntries(
      base.fields
        .filter((f) => !f.index && (!f.shared || !base.channel))
        .map((f) => [f.key, f.value]),
    ),
    points,
    mode,
    repair: false,
  };
  d.repair = mode === "Multi" && pointError(d) !== null;
  return d;
}
export function pointError(d: Draft): string | null {
  if (!["Multi", "Day Night", "Seasonal"].includes(d.mode)) return null;
  if (!validPointCount(d.mode, d.points.length))
    return d.mode === "Multi" ? message("multi_count") : message("mode_count", { mode: d.mode, count: d.mode === "Day Night" ? 2 : 8 });
  if (
    d.points.some(
      (p) =>
        !validSeconds(p.seconds) || !boundedNumber(p.target_native),
    )
  )
    return message("complete_points");
  if (d.mode === "Multi") {
    if (d.points.some(isEmpty))
      return message("empty_point");
    if (
      d.points.some((p, i) => i > 0 && p.seconds! <= d.points[i - 1].seconds!)
    )
      return message("multi_order");
  } else if (
    d.points.some(
      (p, i) => i % 2 === 0 && p.seconds === d.points[i + 1]?.seconds,
    )
  )
    return message("day_night_order");
  return null;
}
export function dateError(values: (string | number | null)[]): string | null {
  const ord: number[] = [];
  for (const v of values) {
    if (v === "00/00") continue;
    if (typeof v !== "string" || !/^\d{2}\/\d{2}$/.test(v))
      return message("dates_format");
    const ordinal = dateOrdinal(v);
    if (ordinal === null)
      return message("dates_calendar");
    ord.push(ordinal);
  }
  if (new Set(ord).size !== ord.length)
    return message("dates_distinct");
  if (
    ord.length > 1 &&
    ord.reduce(
      (sum, n, i) => sum + ((ord[(i + 1) % ord.length] - n + 365) % 365),
      0,
    ) !== 365
  )
    return message("dates_cycle");
  return null;
}
export function changedFields(d: Draft) {
  return Object.fromEntries(
    Object.entries(d.values).filter(
      ([k, v]) => v !== d.base.fields.find((f) => f.key === k)?.value,
    ),
  );
}
export function scheduleChanged(d: Draft): boolean {
  const original = makeDraft(d.base);
  return (
    JSON.stringify(d.points.map((p) => [p.seconds, p.target_native])) !==
    JSON.stringify(original.points.map((p) => [p.seconds, p.target_native]))
  );
}
export function patchFor(d: Draft): Record<string, unknown> {
  const fields = changedFields(d);
  const modeKeys = Object.keys(fields).filter(
    (k) => d.base.fields.find((f) => f.key === k)?.kind === "enum",
  );
  if (modeKeys.length) return { kind: "mode", fields };
  const patch: Record<string, unknown> = {
    kind: d.base.channel ? "channel" : "season_dates",
    fields,
  };
  if (scheduleChanged(d)) patch.schedule = { mode: d.mode, points: d.points };
  return patch;
}
export const dirty = (d: Draft) =>
  Object.keys(changedFields(d)).length > 0 || scheduleChanged(d);
export function errorFor(d: Draft): string | null {
  const changed = changedFields(d);
  const keys = Object.keys(changed);
  const modes = keys.filter(
    (k) => d.base.fields.find((f) => f.key === k)?.kind === "enum",
  );
  if (modes.length && (keys.length > 1 || scheduleChanged(d)))
    return message("separate_mode");
  for (const key of keys) {
    const f = d.base.fields.find((f) => f.key === key)!;
    const v = changed[key];
    if (!f.writable) return message("not_editable", { label: f.label });
    if (
      ["number", "setpoint", "ramp"].includes(f.kind) &&
      (!boundedNumber(v, f.maximum) ||
        v < f.minimum ||
        (f.kind === "ramp" && !Number.isInteger(v)))
    )
      return message("range_error", { label: f.label, minimum: f.minimum, maximum: f.maximum,
        suffix: f.kind === "ramp" ? message("whole_minutes") : "" });
    if (f.kind === "date" && dateOrdinal(v) === null)
      return message("date_edit");
    if (f.kind === "enum" && (typeof v !== "string" || !f.options.includes(v)))
      return message("option_edit");
  }
  if (!d.base.channel && keys.length) {
    // Unset siblings remain unset; changed fields may not be cleared.
    const dates = d.base.fields
      .filter((f) => f.kind === "date")
      .map(
        (f) => changed[f.key] ?? (f.validity === "unset" ? "00/00" : f.value),
      );
    return dateError(dates);
  }
  if (scheduleChanged(d)) return pointError(d);
  return null;
}
export function segments(points: Point[]) {
  if (
    !points.length ||
    points.some((p) => p.seconds === null || p.target_native === null)
  )
    return [];
  const sorted = [...points].sort((a, b) => a.seconds! - b.seconds!);
  if (new Set(sorted.map((p) => p.seconds)).size !== sorted.length) return [];
  const result = sorted.map((p, i) => ({
    point: p,
    start: p.seconds!,
    end: sorted[i + 1]?.seconds ?? 86400,
    carry: i === sorted.length - 1 && sorted[0].seconds! > 0,
  }));
  if (sorted[0].seconds! > 0)
    result.unshift({
      point: sorted.at(-1)!,
      start: 0,
      end: sorted[0].seconds!,
      carry: true,
    });
  return result;
}
