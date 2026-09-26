import { message } from "./localize";
import { newId } from "./id";
import { boundedNumber, validSeconds, validPointCount } from "./constraints";
import { pointError } from "./draft";
import type { Draft, Point } from "./types";

export const PRESET_FORMAT = "microclimate.schedule.v1";
export const MAX_PRESET_BYTES = 4096;
type PresetPoint = { seconds: number; target_native: number };
export interface SchedulePreset {
  format: typeof PRESET_FORMAT;
  mode: "Day Night" | "Multi" | "Seasonal";
  unit: "celsius" | "fahrenheit" | "percent";
  points: PresetPoint[];
}

function unitOf(d: Draft): SchedulePreset["unit"] {
  const field = d.base.fields.find(
    (f) => f.key === `${d.base.channel}_period_1_setpoint`,
  );
  if (field?.unit === "°C") return "celsius";
  if (field?.unit === "°F") return "fahrenheit";
  if (field?.unit === "%") return "percent";
  throw new Error(message("preset_unit_missing"));
}

export function exportPreset(d: Draft): SchedulePreset {
  if (!["Day Night", "Multi", "Seasonal"].includes(d.mode) || pointError(d))
    throw new Error(message("preset_incomplete"));
  return {
    format: PRESET_FORMAT,
    mode: d.mode as SchedulePreset["mode"],
    unit: unitOf(d),
    points: d.points.map((p) => ({
      seconds: p.seconds!,
      target_native: p.target_native!,
    })),
  };
}

export function importPreset(d: Draft, value: unknown): Draft {
  if (!value || typeof value !== "object" || Array.isArray(value))
    throw new Error(message("preset_invalid"));
  const preset = value as Partial<SchedulePreset>;
  if (
    Object.keys(preset).sort().join(",") !== "format,mode,points,unit" ||
    preset.format !== PRESET_FORMAT
  )
    throw new Error(message("preset_format"));
  if (preset.mode !== d.mode || preset.unit !== unitOf(d))
    throw new Error(message("preset_mode"));
  if (!Array.isArray(preset.points))
    throw new Error(message("preset_points"));
  if (!validPointCount(d.mode, preset.points.length))
    throw new Error(message("preset_count"));
  const points: Point[] = preset.points.map((p) => {
    if (
      !p ||
      typeof p !== "object" ||
      Object.keys(p).sort().join(",") !== "seconds,target_native" ||
      !validSeconds(p.seconds) || !boundedNumber(p.target_native, d.base.fields.find(
        (f) => f.key === `${d.base.channel}_period_1_setpoint`)?.maximum ?? 100)
    )
      throw new Error(message("preset_point"));
    return {
      draft_id: newId(),
      seconds: p.seconds,
      target_native: p.target_native,
    };
  });
  const next = { ...d, points, repair: false };
  const error = pointError(next);
  if (error) throw new Error(error);
  return next;
}
