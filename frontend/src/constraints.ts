/** Strict draft/preset edits; reported observations must not be clamped here. */
export const MAX_TARGET = 100;
export const MAX_RAMP_MINUTES = 240;
export const SECONDS_PER_DAY = 86400;

export function boundedNumber(value: unknown, maximum = MAX_TARGET): value is number {
  return typeof value === "number" && Number.isFinite(value) && value >= 0 && value <= maximum;
}

export function validSeconds(value: unknown): value is number {
  return boundedNumber(value, SECONDS_PER_DAY - 1) && Number.isInteger(value);
}

export function validPointCount(mode: string, count: number): boolean {
  return mode === "Multi" ? count >= 2 && count <= 8
    : mode === "Day Night" ? count === 2
    : mode === "Seasonal" ? count === 8 : false;
}

export function dateOrdinal(value: unknown): number | null {
  if (typeof value !== "string" || value.length !== 5 || !/^[0-9]{2}\/[0-9]{2}$/.test(value)) return null;
  const [day, month] = value.split("/").map(Number);
  const date = new Date(Date.UTC(2001, month - 1, day));
  if (date.getUTCMonth() !== month - 1 || date.getUTCDate() !== day) return null;
  return Math.floor((date.getTime() - Date.UTC(2001, 0, 1)) / 86400000);
}
