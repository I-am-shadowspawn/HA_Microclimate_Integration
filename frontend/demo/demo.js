import "/custom_components/microclimate_integration/frontend/microclimate-cards.js";
const params = new URLSearchParams(location.search),
  mode = params.get("mode") || "Multi",
  kind = params.get("kind") || "channel",
  count = Number(params.get("count") || 4),
  channel = params.get("channel") || "Yellow";
if (params.has("dark")) document.body.classList.add("dark");
const f = (key, kind, value, index = null, options = []) => ({
  key,
  kind,
  value,
  index,
  options,
  label: key.startsWith("season_")
    ? `Season ${key.split("_")[1]} start`
    : key.endsWith("_control_pin")
      ? "Control mode"
      : key.endsWith("_timing_type")
        ? "Timing mode"
        : key.endsWith("_output_type")
          ? "Output type"
          : key.endsWith("_ramp_time")
            ? "Ramp time"
            : key.endsWith("_lower_alarm")
              ? "Lower alarm threshold"
              : key.endsWith("_upper_alarm")
                ? "Upper alarm threshold"
                : key.replaceAll("_", " "),
  shared: key.startsWith("season"),
  entity_id: index === null ? key : `sensor.${channel.toLowerCase()}_schedule`,
  authorization_scope: index === null ? "entity" : "channel_schedule",
  writable: true,
  reason: null,
  unit:
    kind === "setpoint" || kind === "number"
      ? "°C"
      : kind === "ramp"
        ? "min"
        : null,
  minimum: 0,
  maximum: kind === "ramp" ? 240 : 100,
  step: kind === "ramp" ? 1 : "any",
});
const fields = [];
for (let i = 1; i <= 4; i++)
  fields.push(
    f(
      `season_${i}_start_pin`,
      "date",
      ["09/10", "01/01", "01/06", "01/07"][i - 1],
    ),
  );
if (kind === "channel") {
  fields.push(
    f(`${channel}_control_pin`, "enum", "heating", null, [
      "fixed",
      "heating",
      "cooling",
    ]),
    f(`${channel}_timing_type`, "enum", mode, null, [
      "Constant",
      "Day Night",
      "Multi",
      "Seasonal",
      ...(channel === "Blue" ? ["Periodic"] : []),
    ]),
  );
  if (channel !== "Blue")
    fields.push(
      f(`${channel}_output_type`, "enum", "pulse", null, ["pulse", "dimming"]),
      f(`${channel}_ramp_time`, "ramp", 9),
    );
  fields.push(
    f(`${channel}_lower_alarm`, "number", 18),
    f(`${channel}_upper_alarm`, "number", 38),
  );
  for (let i = 1; i <= 8; i++) {
    fields.push(
      f(
        `${channel}_period_${i}_time`,
        "time",
        mode === "Multi" && i > count
          ? 0
          : mode === "Seasonal" || mode === "Day Night"
            ? i % 2
              ? 25200
              : 68400
            : i * 10800 - 7200,
        i,
      ),
      f(
        `${channel}_period_${i}_setpoint`,
        "setpoint",
        mode === "Multi" && i > count ? 0 : i % 2 ? 27 : 22,
        i,
      ),
    );
  }
}
window.view = {
  schema_version: 1,
  runtime_generation: "generation",
  revision: "revision",
  device_id: kind,
  name:
    kind === "controller" ? "Rainforest controller" : `Rainforest · ${channel}`,
  model: "Evo Connect 3",
  channel: kind === "controller" ? null : channel,
  kind,
  fields,
  observations: [],
  online: true,
  writes_enabled: true,
  busy: false,
};
window.calls = [];
window.callbacks = {};
let job;
const hass = {
  config: {
    unit_system: { temperature: params.has("fahrenheit") ? "°F" : "°C" },
  },
  connection: {
    async subscribeMessage(cb, msg) {
      window.callbacks[msg.type] = cb;
      if (msg.type.endsWith("/subscribe")) cb(structuredClone(window.view));
      if (msg.type.endsWith("/operation")) cb(job);
      return () => delete window.callbacks[msg.type];
    },
  },
  async callWS(msg) {
    window.calls.push(msg);
    if (msg.type.endsWith("/list"))
      return [{ device_id: kind, kind, name: window.view.name }];
    if (msg.type.endsWith("/save")) {
      job = {
        operation_id: "job",
        sequence: 1,
        status: "running",
        phase: "Applying changes",
        confirmed: 0,
        total: 2,
        fields: [],
        reason: null,
      };
      return { operation_id: "job" };
    }
  },
};
const card = document.createElement(
  kind === "controller"
    ? "microclimate-controller-card"
    : "microclimate-channel-card",
);
card.setConfig({
  type: "custom:" + card.localName,
  device_id: kind,
  read_only: params.has("readonly"),
});
card.hass = hass;
document.querySelector("#host").append(card);
window.card = card;
