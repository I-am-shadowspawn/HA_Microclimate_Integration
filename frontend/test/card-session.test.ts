import { expect, it } from "vitest";
import { CardSession } from "../src/card-session";
import type { Hass, Job, Snapshot } from "../src/types";
import { PREFIX } from "../src/types";
import { fixture } from "./snapshot";

const flush = async () => { await Promise.resolve(); await Promise.resolve(); };
function deferred<T>() {
  let resolve!: (value: T) => void;
  const promise = new Promise<T>((done) => { resolve = done; });
  return { promise, resolve };
}
function transport(read: Snapshot, callWS?: (message: Record<string, unknown>) => Promise<unknown>) {
  const subscriptions = new Map<string, (value: unknown) => void>();
  const hass = {
    config: { unit_system: { temperature: "°C" } },
    connection: { subscribeMessage: async (callback: (value: unknown) => void, message: Record<string, unknown>) => {
      const key = String(message.type);
      subscriptions.set(key, callback);
      if (key.endsWith("/subscribe")) callback(read);
      return () => { if (subscriptions.get(key) === callback) subscriptions.delete(key); };
    } },
    callWS: callWS ?? (async () => null),
  } as Hass;
  return { hass, subscriptions };
}
function mounted(read = fixture()) {
  const selected: string[] = [];
  const state = new CardSession(() => {}, id => selected.push(id));
  const network = transport(read);
  state.setConfig({ type: "custom:microclimate-channel-card", device_id: "channel" });
  state.setHass(network.hass);
  state.connect();
  return { state, network, selected };
}

it("keeps an active draft while live snapshots refresh and fails closed on malformed data", async () => {
  const { state, network } = mounted();
  await flush();
  state.edit();
  const draft = state.draft!;
  const changed = fixture(); changed.revision = "new";
  network.subscriptions.get(PREFIX + "subscribe")!(changed);
  expect(state.draft).toBe(draft);
  expect(state.conflict).toBe(true);
  network.subscriptions.get(PREFIX + "subscribe")!({ ...changed, fields: null });
  expect(state.draft).toBe(draft);
  expect(state.view).toBeUndefined();
  expect(state.canEdit).toBe(false);
  expect(state.error).toMatch(/incomplete/);
});

it("ignores old device and connection callbacks", async () => {
  const { state, network } = mounted(); await flush();
  const old = network.subscriptions.get(PREFIX + "subscribe")!;
  const next = fixture(); next.device_id = "other";
  state.setConfig({ type: "custom:microclimate-channel-card", device_id: "other" });
  expect(state.view).toBeUndefined();
  old(fixture());
  expect(state.view).toBeUndefined();
  const newNetwork = transport(next);
  state.setHass(newNetwork.hass); await flush();
  expect(state.view?.device_id).toBe("other");
  old(fixture());
  expect(state.view?.device_id).toBe("other");
  state.disconnect();
  newNetwork.subscriptions.get(PREFIX + "subscribe")?.(fixture());
  expect(state.view?.device_id).toBe("other");
});

it("submits only once and recovers an invalid acknowledgement without replay", async () => {
  const response = deferred<unknown>();
  const calls: Record<string, unknown>[] = [];
  const state = new CardSession(() => {}, () => {});
  const network = transport(fixture(), async msg => { calls.push(msg); return msg.type === PREFIX + "save" ? response.promise : null; });
  state.setConfig({ type: "custom:microclimate-channel-card", device_id: "channel" });
  state.setHass(network.hass); state.connect(); await flush(); state.edit();
  state.draft = { ...state.draft!, points: state.draft!.points.slice(0, 2) };
  const first = state.save();
  await state.save();
  expect(calls.filter(c => c.type === PREFIX + "save")).toHaveLength(1);
  response.resolve({ operation_id: 99 });
  await first;
  expect(calls.filter(c => c.type === PREFIX + "request")).toHaveLength(1);
  expect(calls.filter(c => c.type === PREFIX + "save")).toHaveLength(1);
  expect(state.draft).toBeDefined();
  expect(state.submissionUnknown).toBe(true);
});

it("stale Save acknowledgements cannot attach a job to a new device", async () => {
  const response = deferred<unknown>();
  const state = new CardSession(() => {}, () => {});
  const network = transport(fixture(), async () => response.promise);
  state.setConfig({ type: "custom:microclimate-channel-card", device_id: "channel" });
  state.setHass(network.hass); state.connect(); await flush(); state.edit();
  state.draft = { ...state.draft!, points: state.draft!.points.slice(0, 2) };
  const save = state.save();
  state.draft = undefined;
  state.setConfig({ type: "custom:microclimate-channel-card", device_id: "other" });
  response.resolve({ operation_id: "old" }); await save;
  expect(state.job).toBeUndefined();
  expect(state.config?.device_id).toBe("other");
});

it("rejects mismatched and out-of-order job events without clearing the draft", async () => {
  const state = new CardSession(() => {}, () => {});
  const network = transport(fixture(), async () => ({ operation_id: "active" }));
  state.setConfig({ type: "custom:microclimate-channel-card", device_id: "channel" });
  state.setHass(network.hass); state.connect(); await flush(); state.edit();
  state.draft = { ...state.draft!, points: state.draft!.points.slice(0, 2) };
  await state.save();
  const cb = network.subscriptions.get(PREFIX + "operation")!;
  const event: Job = { operation_id: "active", sequence: 2, status: "running", phase: "Applying", confirmed: 0, total: 2, fields: [], reason: null };
  cb(event); cb({ ...event, sequence: 1, status: "succeeded" });
  cb({ ...event, sequence: 2, status: "succeeded" });
  expect(state.job?.status).toBe("running");
  cb({ ...event, operation_id: "another", status: "succeeded" });
  expect(state.draft).toBeDefined();
  expect(state.submissionUnknown).toBe(true);
});
