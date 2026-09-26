import { describe, expect, it } from "vitest";
import { acknowledgement, devices, errorEnvelope, job, recovery, safeError, snapshot } from "../src/protocol";
import { fixture } from "./snapshot";
import vectors from "../../fixtures/validation_contract.json";

const goodJob = {
  operation_id: "op", sequence: 1, status: "running", phase: "Applying changes",
  confirmed: 1, total: 2, fields: [{ key: "a", label: "A", status: "confirmed" }], reason: null,
};

describe("untrusted card protocol", () => {
  it("accepts permissive observations without granting writes", () => {
    const view = fixture();
    view.fields[1].value = -15;
    view.fields[2].value = 500;
    view.fields.splice(3, 1); // Permission-filtered schedules may omit a field.
    expect(snapshot(view, "channel")).toEqual({ ok: true, value: view });
    for (const row of vectors.numbers) {
      if (row.observation_temperature === null) continue;
      view.fields[1].value = row.observation_temperature;
      expect(snapshot(view, "channel").ok).toBe(true);
    }
  });
  it("rejects missing, duplicated, malformed or cross-device fields", () => {
    const view = fixture();
    expect(snapshot(view, "different").ok).toBe(false);
    expect(snapshot({ ...view, fields: [...view.fields, view.fields[0]] }, "channel").ok).toBe(false);
    expect(snapshot({ ...view, fields: [{ ...view.fields[0], writable: "yes" }] }, "channel").ok).toBe(false);
    expect(snapshot({ ...view, fields: [{ ...view.fields[0], value: Infinity }] }, "channel").ok).toBe(false);
    expect(snapshot({ ...view, observations: null }, "channel").ok).toBe(false);
    expect(snapshot({ ...view, schema_version: 2 }, "channel")).toEqual({ ok: false, reason: "unsupported" });
    expect(snapshot({ ...view, another: true }, "channel").ok).toBe(true);
  });
  it("validates jobs, identifiers, acknowledgements and editor lists", () => {
    expect(job(goodJob, "op").ok).toBe(true);
    expect(job(goodJob, "other").ok).toBe(false);
    expect(job({ ...goodJob, confirmed: 3 }, "op").ok).toBe(false);
    expect(job({ ...goodJob, sequence: -1 }, "op").ok).toBe(false);
    expect(job({ ...goodJob, status: "invented" }, "op").ok).toBe(false);
    expect(job({ ...goodJob, fields: [{ key: "a", label: "A", status: "invented" }] }, "op").ok).toBe(false);
    expect(acknowledgement({ operation_id: "op" }).ok).toBe(true);
    expect(acknowledgement({ operation_id: 4 }).ok).toBe(false);
    expect(recovery(null)).toEqual({ ok: true, value: null });
    expect(recovery({ operation_id: "op" }).ok).toBe(true);
    expect(devices([{ device_id: "one", kind: "channel", name: "One" }]).ok).toBe(true);
    expect(devices([{ device_id: "one", kind: "unknown", name: "One" }]).ok).toBe(false);
    expect(errorEnvelope({ error: "unavailable" })).toBe("unavailable");
    expect(safeError(null)).toEqual({});
  });
});
