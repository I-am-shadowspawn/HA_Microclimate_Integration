import type { Snapshot, Field } from "../src/types";

export function fixture(mode = "Multi", count = 3): Snapshot {
  const field = (
    key: string,
    kind: string,
    value: string | number | null,
    index: number | null = null,
  ): Field => ({
    key,
    kind,
    value,
    index,
    label: key,
    shared: key.startsWith("season"),
    entity_id: key,
    writable: true,
    reason: null,
    options:
      kind === "enum" ? ["Constant", "Day Night", "Multi", "Seasonal"] : [],
    unit: kind === "setpoint" ? "°C" : null,
    minimum: 0,
    maximum: 100,
    step: "any",
  });
  const fields = [field("Yellow_timing_type", "enum", mode)];
  for (let i = 1; i <= 8; i++) {
    fields.push(
      field(`Yellow_period_${i}_time`, "time", i <= count ? i * 3600 : 0, i),
      field(
        `Yellow_period_${i}_setpoint`,
        "setpoint",
        i <= count ? 20 + i : 0,
        i,
      ),
    );
  }
  for (let i = 1; i <= 4; i++)
    fields.push(field(`season_${i}_start_pin`, "date", `01/0${i}`));
  return {
    schema_version: 1,
    runtime_generation: "generation",
    revision: "revision",
    device_id: "channel",
    name: "Vivarium · Yellow",
    model: "Evo Connect 3",
    channel: "Yellow",
    kind: "channel",
    fields,
    observations: [],
    online: true,
    writes_enabled: true,
    busy: false,
  };
}
