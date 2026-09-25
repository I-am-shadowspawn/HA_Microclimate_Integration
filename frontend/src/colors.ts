import type { TemperatureColor } from "./types";

// Native Celsius thresholds stay stable when HA displays Fahrenheit.
export const DEFAULT_COLORS: TemperatureColor[] = [
  { temperature: 0, color: "#f6c85f" },
  { temperature: 20, color: "#f5a623" },
  { temperature: 25, color: "#ef7d16" },
  { temperature: 30, color: "#d94b24" },
  { temperature: 35, color: "#b52222" },
];
export function validateColors(
  value: unknown,
): asserts value is TemperatureColor[] | undefined {
  if (value === undefined) return;
  if (
    !Array.isArray(value) ||
    value.length === 0 ||
    value.some(
      (v) =>
        !v ||
        typeof v.temperature !== "number" ||
        !Number.isFinite(v.temperature) ||
        v.temperature < 0 ||
        v.temperature > 100 ||
        typeof v.color !== "string" ||
        !/^#[0-9a-f]{6}$/i.test(v.color),
    ) ||
    new Set(value.map((v) => v.temperature)).size !== value.length
  )
    throw new Error(
      "Temperature colours require unique Celsius bounds from 0 to 100 and #RRGGBB colours.",
    );
}
export function colorFor(value: number | null, stops = DEFAULT_COLORS): string {
  if (value === null || !Number.isFinite(value)) return "#737373";
  const sorted = [...stops].sort((a, b) => a.temperature - b.temperature);
  return (sorted.filter((s) => value >= s.temperature).at(-1) ?? sorted[0])
    .color;
}
export function textColor(color: string): string {
  const components = [1, 3, 5].map((i) => {
    const v = parseInt(color.slice(i, i + 2), 16) / 255;
    return v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4;
  });
  const luminance =
    components[0] * 0.2126 + components[1] * 0.7152 + components[2] * 0.0722;
  return luminance > 0.179 ? "#000000" : "#ffffff";
}
export function targetColors(
  value: number | null,
  unit?: string | null,
  stops?: TemperatureColor[],
) {
  const color = unit === "°C" ? colorFor(value, stops) : "#327b80";
  return `--segment-color:${color};--segment-text:${textColor(color)}`;
}
