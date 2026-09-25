export interface Field {
  key: string;
  kind: string;
  label: string;
  index: number | null;
  shared: boolean;
  value: string | number | null;
  entity_id: string;
  validity?: string;
  writable: boolean;
  reason: string | null;
  options: string[];
  unit: string | null;
  minimum: number;
  maximum: number;
  step: number | "any";
}
export interface Snapshot {
  schema_version: number;
  runtime_generation: string;
  revision: string;
  device_id: string;
  name: string;
  model: string;
  channel: string | null;
  kind: "channel" | "controller";
  fields: Field[];
  observations: { name: string; value: string; unit: string | null }[];
  online: boolean;
  writes_enabled: boolean;
  busy: boolean;
  error?: string;
}
export interface Point {
  draft_id: string;
  source_slot?: number;
  seconds: number | null;
  target_native: number | null;
}
export interface Draft {
  base: Snapshot;
  values: Record<string, string | number | null>;
  points: Point[];
  mode: string;
  repair: boolean;
}
export interface TemperatureColor {
  temperature: number;
  color: string;
}
export interface Config {
  type: string;
  device_id: string;
  title?: string;
  read_only?: boolean;
  show_observations?: boolean;
  temperature_colors?: TemperatureColor[];
}
export interface Job {
  operation_id: string;
  sequence: number;
  status: string;
  phase: string;
  confirmed: number;
  total: number;
  fields: { key: string; label: string; status: string }[];
  reason: string | null;
  error?: string;
}
export interface Hass {
  config: { unit_system: { temperature: string } };
  callWS<T>(message: Record<string, unknown>): Promise<T>;
  connection: {
    subscribeMessage<T>(
      callback: (value: T) => void,
      message: Record<string, unknown>,
    ): Promise<() => void>;
    addEventListener?(type: string, callback: () => void): void;
    removeEventListener?(type: string, callback: () => void): void;
  };
}
export const PREFIX = "microclimate_integration/card/";
export const terminal = (job?: Job) =>
  !job ||
  ["succeeded", "failed", "partial", "uncertain", "stopped"].includes(
    job.status,
  );
