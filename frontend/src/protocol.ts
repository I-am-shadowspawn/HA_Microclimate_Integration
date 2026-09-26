/** Validate untrusted WebSocket shapes; observed values retain their native range. */
import type { Field, Job, Snapshot } from "./types";

type Result<T> = { ok: true; value: T } | { ok: false; reason: "malformed" | "unsupported" };
const ok = <T>(value: T): Result<T> => ({ ok: true, value });
const bad = <T>(reason: "malformed" | "unsupported" = "malformed"): Result<T> => ({ ok: false, reason });
const object = (v: unknown): v is Record<string, unknown> => !!v && typeof v === "object" && !Array.isArray(v);
const text = (v: unknown): v is string => typeof v === "string" && v.length > 0 && v.length <= 1024;
const id = (v: unknown): v is string => text(v) && v.length <= 128;
const finite = (v: unknown): v is number => typeof v === "number" && Number.isFinite(v);
const natural = (v: unknown): v is number => finite(v) && Number.isInteger(v) && v >= 0;
const nullableText = (v: unknown): v is string | null => v === null || typeof v === "string";
const nullableValue = (v: unknown): v is string | number | null => nullableText(v) || finite(v);
const kinds = new Set(["enum", "date", "time", "number", "setpoint", "ramp"]);
const statuses = new Set(["pending", "running", "succeeded", "failed", "partial", "uncertain", "stopped"]);
const fieldStatuses = new Set(["not-sent", "pending", "confirmed", "failed", "uncertain"]);

function field(v: unknown): v is Field {
  if (!object(v)) return false;
  return id(v.key) && kinds.has(String(v.kind)) && typeof v.label === "string" &&
    (v.index === null || (natural(v.index) && v.index >= 1 && v.index <= 8)) &&
    typeof v.shared === "boolean" && nullableValue(v.value) && id(v.entity_id) &&
    (v.validity === undefined || typeof v.validity === "string") &&
    typeof v.writable === "boolean" && nullableText(v.reason) &&
    Array.isArray(v.options) && v.options.every(text) &&
    nullableText(v.unit) && finite(v.minimum) && finite(v.maximum) &&
    (v.step === "any" || finite(v.step));
}

export function snapshot(value: unknown, deviceId: string): Result<Snapshot> {
  if (!object(value)) return bad();
  if (value.schema_version !== 1) return bad("unsupported");
  if (!id(value.runtime_generation) || !id(value.revision) || value.device_id !== deviceId ||
      !text(value.name) || !text(value.model) ||
      (value.kind !== "channel" && value.kind !== "controller") ||
      (value.kind === "channel" ? !text(value.channel) : value.channel !== null) ||
      !Array.isArray(value.fields) || !value.fields.every(field) ||
      !Array.isArray(value.observations) ||
      !value.observations.every((item) => object(item) && text(item.name) && typeof item.value === "string" && nullableText(item.unit)) ||
      typeof value.online !== "boolean" || typeof value.writes_enabled !== "boolean" || typeof value.busy !== "boolean") return bad();
  if (new Set(value.fields.map((f: Field) => f.key)).size !== value.fields.length) return bad();
  return ok(value as unknown as Snapshot);
}

export function job(value: unknown, operationId: string): Result<Job> {
  if (!object(value) || value.operation_id !== operationId || !natural(value.sequence) ||
      !text(value.status) || !statuses.has(value.status) || !text(value.phase) ||
      !natural(value.confirmed) || !natural(value.total) || value.confirmed > value.total ||
      !Array.isArray(value.fields) || !value.fields.every((f) => object(f) && id(f.key) &&
        typeof f.label === "string" && text(f.status) && fieldStatuses.has(f.status)) ||
      !nullableText(value.reason) ||
      (value.reason_message !== undefined && !nullableText(value.reason_message))) return bad();
  return ok(value as unknown as Job);
}

export function devices(value: unknown): Result<{ device_id: string; kind: "channel" | "controller"; name: string }[]> {
  if (!Array.isArray(value) || !value.every((v) => object(v) && id(v.device_id) &&
      (v.kind === "channel" || v.kind === "controller") && text(v.name))) return bad();
  return ok(value);
}

export function acknowledgement(value: unknown): Result<{ operation_id: string }> {
  return object(value) && id(value.operation_id) ? ok({ operation_id: value.operation_id }) : bad();
}

export function recovery(value: unknown): Result<{ operation_id: string } | null> {
  return value === null ? ok(null) : acknowledgement(value);
}

export function errorEnvelope(value: unknown): string | null {
  return object(value) && text(value.error) ? value.error : null;
}

export function safeError(value: unknown): { code?: string; message?: string } {
  if (!object(value)) return {};
  return { code: id(value.code) ? value.code : undefined, message: text(value.message) ? value.message : undefined };
}
