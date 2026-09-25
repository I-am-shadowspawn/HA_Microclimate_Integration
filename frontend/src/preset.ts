import { newId } from "./id";
import { pointError } from "./draft";
import type { Draft, Point } from "./types";

export const PRESET_FORMAT = "microclimate.schedule.v1";
export const MAX_PRESET_BYTES = 4096;
type PresetPoint = { seconds: number; target_native: number };
export interface SchedulePreset {
  format: typeof PRESET_FORMAT;
  mode: "Day Night" | "Multi" | "Seasonal";
  unit: "celsius" | "percent";
  points: PresetPoint[];
}

function unitOf(d: Draft): SchedulePreset["unit"] {
  const field = d.base.fields.find(
    (f) => f.key === `${d.base.channel}_period_1_setpoint`,
  );
  if (field?.unit === "°C") return "celsius";
  if (field?.unit === "%") return "percent";
  throw new Error("Schedule unit is unavailable.");
}

export function exportPreset(d: Draft): SchedulePreset {
  if (!["Day Night", "Multi", "Seasonal"].includes(d.mode) || pointError(d))
    throw new Error("Complete the supported schedule before exporting.");
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
    throw new Error("Invalid schedule preset.");
  const preset = value as Partial<SchedulePreset>;
  if (
    Object.keys(preset).sort().join(",") !== "format,mode,points,unit" ||
    preset.format !== PRESET_FORMAT
  )
    throw new Error("Unsupported schedule preset format.");
  if (preset.mode !== d.mode || preset.unit !== unitOf(d))
    throw new Error("Preset mode and native units must match this channel.");
  if (!Array.isArray(preset.points))
    throw new Error("Invalid schedule points.");
  const required = d.mode === "Day Night" ? 2 : d.mode === "Seasonal" ? 8 : null;
  if (
    preset.points.length < 2 ||
    preset.points.length > 8 ||
    (required !== null && preset.points.length !== required)
  )
    throw new Error("Incorrect number of schedule points.");
  const points: Point[] = preset.points.map((p) => {
    if (
      !p ||
      typeof p !== "object" ||
      Object.keys(p).sort().join(",") !== "seconds,target_native" ||
      !Number.isInteger(p.seconds) ||
      p.seconds < 0 ||
      p.seconds >= 86400 ||
      typeof p.target_native !== "number" ||
      !Number.isFinite(p.target_native) ||
      p.target_native < 0 ||
      p.target_native > 100
    )
      throw new Error("Invalid schedule point.");
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
