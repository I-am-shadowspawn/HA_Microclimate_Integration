import { validateColors, targetColors } from "./colors";
import { newId } from "./id";
import { LitElement, html, css, nothing } from "lit";
import { repeat } from "lit/directives/repeat.js";
import { live } from "lit/directives/live.js";
import type { Config, Draft, Field, Hass, Job, Point, Snapshot } from "./types";
import { PREFIX, terminal } from "./types";
import {
  makeDraft,
  clock,
  parseClock,
  displayValue,
  nativeValue,
  dirty,
  errorFor,
  patchFor,
  segments,
  pointError,
  changedFields,
} from "./draft";

export class MicroclimateCard extends LitElement {
  static properties = {
    view: { state: true },
    draft: { state: true },
    job: { state: true },
    error: { state: true },
    selected: { state: true },
    saving: { state: true },
    notice: { state: true },
    submissionUnknown: { state: true },
    pendingConfig: { state: true },
    _config: { state: true },
    _hass: { state: true },
  };
  static styles = css`
    :host {
      display: block;
      color: var(--primary-text-color, #20252c);
      font-family: var(--paper-font-body1_-_font-family, system-ui);
      font-size: 14px;
    }
    * {
      box-sizing: border-box;
    }
    ha-card {
      display: block;
      background: var(--ha-card-background, var(--card-background-color, #fff));
      border: 1px solid var(--divider-color, #d9dfe5);
      border-radius: var(--ha-card-border-radius, 16px);
      padding: 20px;
      overflow: hidden;
    }
    header {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 12px;
    }
    h2 {
      font-size: 21px;
      font-weight: 600;
      line-height: 1.3;
      margin: 0 0 5px;
      overflow-wrap: anywhere;
    }
    h3 {
      font-size: 14px;
      margin: 20px 0 10px;
    }
    .muted {
      color: var(--secondary-text-color, #68737e);
      font-size: 12px;
      line-height: 1.6;
    }
    button,
    input,
    select {
      font: inherit;
      color: inherit;
    }
    button {
      min-height: 44px;
      border: 1px solid var(--divider-color, #bac7d2);
      border-radius: 9px;
      background: transparent;
      padding: 8px 13px;
      cursor: pointer;
    }
    button.primary {
      background: var(--primary-color, #007fa3);
      border-color: transparent;
      color: var(--text-primary-color, #fff);
    }
    button:disabled {
      opacity: 0.45;
      cursor: default;
    }
    button:focus-visible,
    input:focus-visible,
    select:focus-visible {
      outline: 3px solid var(--primary-color, #007fa3);
      outline-offset: 2px;
    }
    .badges,
    .actions,
    .observations {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }
    .badges {
      margin: 16px 0;
    }
    .badge {
      background: var(--secondary-background-color, #eff3f6);
      padding: 6px 9px;
      border-radius: 6px;
      font-size: 12px;
    }
    .observations {
      margin: 16px 0;
    }
    .observation {
      flex: 1;
      min-width: 90px;
      padding: 10px;
      background: var(--secondary-background-color, #eff3f6);
      border-radius: 8px;
    }
    .observation strong {
      display: block;
      font-size: 18px;
    }
    .row {
      margin: 16px 0 24px;
    }
    .row-title {
      display: flex;
      justify-content: space-between;
      gap: 10px;
      margin-bottom: 12px;
      font-weight: 600;
    }
    .row-title small {
      font-weight: 400;
    }
    .timeline {
      height: 72px;
      position: relative;
      border-radius: 8px;
      background: var(--secondary-background-color, #edf1f5);
      margin: 22px 0 6px;
    }
    .segment {
      position: absolute;
      top: 0;
      bottom: 0;
      border-right: 1px solid #ffffff80;
      background: var(--segment-color);
      color: var(--segment-text);
      overflow: hidden;
      display: flex;
      align-items: center;
      justify-content: center;
      white-space: nowrap;
      font-size: 12px;
    }
    .segment.carry {
      background:
        repeating-linear-gradient(
          135deg,
          #ffffff28 0px,
          #ffffff28 5px,
          transparent 5px,
          transparent 10px
        ),
        var(--segment-color);
    }
    .segment:first-child {
      border-radius: 8px 0 0 8px;
    }
    .segment:last-of-type {
      border-radius: 0 8px 8px 0;
    }
    .handle {
      position: absolute;
      top: -14px;
      bottom: -5px;
      width: 24px;
      min-height: 40px;
      padding: 0;
      transform: translateX(-50%);
      border: 0;
      background: transparent;
      touch-action: pan-y;
      z-index: 2;
    }
    .handle::before {
      content: "";
      display: block;
      width: 3px;
      background: var(--primary-text-color, #20252c);
      height: 80%;
      margin: auto;
    }
    .handle::after {
      content: "◆";
      position: absolute;
      top: 0;
      left: 3px;
      color: var(--primary-color, #007fa3);
      font-size: 22px;
    }
    .handle[aria-pressed="true"]::before {
      background: var(--primary-color, #007fa3);
      width: 5px;
    }
    .axis {
      display: flex;
      justify-content: space-between;
      color: var(--secondary-text-color, #68737e);
      font-size: 11px;
    }
    .point-list {
      display: grid;
      gap: 8px;
      margin: 12px 0;
    }
    .point {
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      align-items: center;
      gap: 8px;
    }
    .point.selected {
      border-left: 3px solid var(--primary-color, #007fa3);
      padding-left: 6px;
    }
    .point button {
      text-align: left;
    }
    .point span {
      font-variant-numeric: tabular-nums;
    }
    .form {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }
    .field {
      display: grid;
      gap: 5px;
      min-width: 0;
    }
    input,
    select {
      width: 100%;
      min-width: 0;
      min-height: 42px;
      border: 1px solid var(--divider-color, #bac7d2);
      background: var(--card-background-color, #fff);
      border-radius: 7px;
      padding: 8px;
    }
    input[type="range"] {
      padding: 0;
      accent-color: var(--primary-color, #007fa3);
    }
    .alert {
      margin: 12px 0;
      padding: 10px 12px;
      border-radius: 8px;
      background: var(--secondary-background-color, #eff3f6);
      line-height: 1.5;
      overflow-wrap: anywhere;
    }
    .error {
      border-left: 3px solid var(--error-color, #c84436);
    }
    .actions {
      justify-content: flex-end;
      margin-top: 18px;
    }
    .settings {
      margin-top: 20px;
      border-top: 1px solid var(--divider-color, #d9dfe5);
      padding-top: 14px;
    }
    summary {
      cursor: pointer;
      min-height: 36px;
      font-weight: 600;
    }
    .review {
      font-size: 12px;
      line-height: 1.7;
      max-height: 160px;
      overflow: auto;
    }
    progress {
      width: 100%;
      accent-color: var(--primary-color, #007fa3);
    }
    .status {
      font-size: 12px;
    }
    .empty {
      padding: 22px;
      text-align: center;
    }
    .slider {
      margin: 14px 0;
    }
    .sr {
      position: absolute;
      clip: rect(0, 0, 0, 0);
      width: 1px;
      height: 1px;
      overflow: hidden;
    }
    @media (max-width: 360px) {
      ha-card {
        padding: 12px;
      }
      .form {
        grid-template-columns: 1fr;
      }
      .point {
        grid-template-columns: 1fr 1fr;
      }
      .point button {
        grid-column: 1/-1;
      }
      .row-title {
        flex-wrap: wrap;
      }
      .segment {
        font-size: 10px;
      }
    }
  `;
  _config?: Config;
  _hass?: Hass;
  view?: Snapshot;
  draft?: Draft;
  job?: Job;
  error = "";
  notice = "";
  selected = "";
  saving = false;
  submissionUnknown = false;
  private requestId?: string;
  pendingConfig?: Config;
  private navigateAfterSave = false;
  private observedDraft?: Draft;
  private unsubscribe?: () => void;
  private unsubJob?: () => void;
  private epoch = 0;
  private subscribed = "";
  private drag?: {
    id: string;
    x: number;
    pointer: number;
    start: number;
    el: HTMLElement;
    moved: boolean;
  };
  private unload = (e: BeforeUnloadEvent) => {
    if (this.draft && dirty(this.draft)) {
      e.preventDefault();
      e.returnValue = "";
    }
  };
  private reconnect = () => {
    this.release();
    void this.subscribe();
  };
  set hass(value: Hass) {
    const changed = this._hass?.connection !== value.connection;
    if (changed) {
      this._hass?.connection.removeEventListener?.("ready", this.reconnect);
      this.release();
    }
    this._hass = value;
    if (changed) value.connection.addEventListener?.("ready", this.reconnect);
    void this.subscribe();
  }
  get hass() {
    return this._hass!;
  }
  setConfig(config: Config) {
    validateColors(config.temperature_colors);
    if (!config.device_id || typeof config.device_id !== "string")
      throw new Error("Select a Microclimate device.");
    if (this._config?.device_id !== config.device_id) {
      if (this.draft && dirty(this.draft)) {
        this.pendingConfig = config;
        return;
      }
      this.release();
      this.view = undefined;
      this.job = undefined;
    }
    this._config = { ...config };
    void this.subscribe();
  }
  connectedCallback() {
    super.connectedCallback();
    window.addEventListener("beforeunload", this.unload);
    this._hass?.connection.addEventListener?.("ready", this.reconnect);
    void this.subscribe();
  }
  disconnectedCallback() {
    super.disconnectedCallback();
    window.removeEventListener("beforeunload", this.unload);
    this._hass?.connection.removeEventListener?.("ready", this.reconnect);
    this.release();
  }
  private release() {
    this.epoch++;
    this.unsubscribe?.();
    this.unsubJob?.();
    this.unsubscribe = undefined;
    this.unsubJob = undefined;
    this.subscribed = "";
  }
  private async subscribe() {
    if (!this.isConnected || !this._hass || !this._config || this.subscribed)
      return;
    const epoch = this.epoch;
    this.subscribed = this._config.device_id;
    try {
      const unsub = await this._hass.connection.subscribeMessage<Snapshot>(
        (v) => {
          if (epoch !== this.epoch) return;
          if (v.error) {
            this.error = v.error;
            this.view = undefined;
            return;
          }
          this.view = v;
          this.error = "";
        },
        { type: PREFIX + "subscribe", device_id: this._config.device_id },
      );
      if (epoch !== this.epoch) {
        unsub();
        return;
      }
      this.unsubscribe = unsub;
      if (this.job) await this.watchJob(this.job.operation_id);
      else if (this.submissionUnknown) await this.recoverRequest();
    } catch {
      if (epoch === this.epoch) {
        this.subscribed = "";
        this.error =
          "Unable to load this device. Check the integration version, device and permissions.";
      }
    }
  }
  private async watchJob(operation_id: string) {
    this.unsubJob?.();
    const epoch = this.epoch;
    const unsub = await this.hass.connection.subscribeMessage<Job>(
      (j) => {
        if (epoch !== this.epoch) return;
        if (j.error) {
          this.error =
            "Save status unavailable. Refresh and review before another Save.";
          this.saving = false;
          return;
        }
        if (
          this.job?.operation_id === j.operation_id &&
          j.sequence < this.job.sequence
        )
          return;
        this.job = j;
        if (terminal(j)) {
          this.saving = false;
          if (j.status === "succeeded") {
            this.draft = undefined;
            this.submissionUnknown = false;
            this.requestId = undefined;
            this.notice = "Changes confirmed by API readback.";
            if (this.navigateAfterSave && this.pendingConfig) {
              const config = this.pendingConfig;
              this.pendingConfig = undefined;
              this.navigateAfterSave = false;
              this.setConfig(config);
            }
          } else
            this.notice =
              "Some changes may already be applied. Refresh and review before saving again.";
        }
      },
      { type: PREFIX + "operation", operation_id },
    );
    if (epoch !== this.epoch) unsub();
    else this.unsubJob = unsub;
  }
  static getConfigElement() {
    return document.createElement("microclimate-card-editor");
  }
  static getStubConfig() {
    return { device_id: "" };
  }
  getCardSize() {
    return this.view?.kind === "controller"
      ? 5
      : this.mode === "Seasonal"
        ? 15
        : 8;
  }
  getGridOptions() {
    return { columns: 12, min_columns: 6 };
  }
  private get fahrenheit() {
    return this._hass?.config?.unit_system.temperature === "°F";
  }
  private get mode() {
    return (
      this.draft?.mode ??
      String(
        this.view?.fields.find(
          (f) => f.key === `${this.view?.channel}_timing_type`,
        )?.value ?? "",
      )
    );
  }
  private get working() {
    if (this.draft) return this.draft;
    if (!this.view) return undefined;
    if (this.observedDraft?.base !== this.view)
      this.observedDraft = makeDraft(this.view);
    return this.observedDraft;
  }
  private get conflict() {
    return (
      !!this.draft &&
      !!this.view &&
      (this.draft.base.revision !== this.view.revision ||
        this.draft.base.runtime_generation !== this.view.runtime_generation)
    );
  }
  private get canEdit() {
    return (
      !!this.view &&
      this.view.schema_version === 1 &&
      this.view.online &&
      !this.view.busy &&
      this.view.writes_enabled &&
      !this._config?.read_only &&
      this.view.fields.some((f) => f.writable)
    );
  }
  private unit(field?: Field) {
    return field?.unit === "°C" && this.fahrenheit ? "°F" : (field?.unit ?? "");
  }
  private format(n: number | null, field?: Field) {
    return n === null
      ? "Unknown"
      : `${Number(displayValue(n, field?.unit ?? null, this.fahrenheit).toFixed(3))} ${this.unit(field)}`;
  }
  private fieldFor(i: number, kind = "setpoint") {
    return this.view?.fields.find(
      (f) => f.key === `${this.view?.channel}_period_${i}_${kind}`,
    );
  }
  private get allScheduleWritable() {
    const count = this.mode === "Day Night" ? 2 : 8;
    return Array.from({ length: count }, (_, i) =>
      ["time", "setpoint"].every(
        (kind) => this.fieldFor(i + 1, kind)?.writable,
      ),
    ).every(Boolean);
  }
  private edit() {
    if (!this.canEdit) return;
    this.draft = makeDraft(this.view!);
    this.job = undefined;
    this.notice = "";
    this.selected = this.draft.points[0]?.draft_id ?? "";
  }
  private navigate(choice: string) {
    if (choice === "stay") {
      this.pendingConfig = undefined;
      return;
    }
    if (choice === "save") {
      this.navigateAfterSave = true;
      void this.save();
      return;
    }
    const config = this.pendingConfig;
    this.pendingConfig = undefined;
    this.draft = undefined;
    if (config) this.setConfig(config);
  }
  private cancel() {
    this.draft = undefined;
    this.notice = "Draft discarded; no changes sent.";
    this.error = "";
  }
  private updatePoint(id: string, delta: Partial<Point>, reorder = true) {
    if (!this.draft || this.saving || !this.allScheduleWritable) return;
    const points = this.draft.points.map((p) =>
      p.draft_id === id ? { ...p, ...delta } : p,
    );
    if (reorder && this.mode === "Multi" && !this.draft.repair)
      points.sort((a, b) => (a.seconds ?? Infinity) - (b.seconds ?? Infinity));
    this.draft = { ...this.draft, points };
  }
  private add() {
    if (
      !this.draft ||
      this.draft.points.length >= 8 ||
      !this.allScheduleWritable
    )
      return;
    const used = new Set(this.draft.points.map((p) => p.seconds));
    let seconds = 43200;
    while (used.has(seconds) && seconds < 86399) seconds++;
    if (used.has(seconds)) {
      seconds = 1;
      while (used.has(seconds)) seconds++;
    }
    const point = { draft_id: newId(), seconds, target_native: 20 };
    this.draft = {
      ...this.draft,
      points: [...this.draft.points, point].sort(
        (a, b) => (a.seconds ?? Infinity) - (b.seconds ?? Infinity),
      ),
    };
    this.selected = point.draft_id;
  }
  private removePoint(id: string) {
    if (
      !this.draft ||
      this.draft.points.length <= 2 ||
      !this.allScheduleWritable
    )
      return;
    this.draft = {
      ...this.draft,
      points: this.draft.points.filter((p) => p.draft_id !== id),
    };
    this.selected = this.draft.points[0]?.draft_id ?? "";
  }
  private repair() {
    if (!this.draft) return;
    this.draft = {
      ...this.draft,
      repair: false,
      points: this.draft.points
        .filter((p) => !(p.seconds === 0 && p.target_native === 0))
        .sort((a, b) => (a.seconds ?? Infinity) - (b.seconds ?? Infinity)),
    };
    this.notice =
      "Review the rebuilt list before Save. Unknown values require correction.";
  }
  private setField(f: Field, e: Event) {
    if (!this.draft || this.saving) return;
    const input = e.target as HTMLInputElement;
    let value: string | number | null = input.value;
    if (["number", "ramp", "setpoint"].includes(f.kind))
      value =
        input.value === ""
          ? null
          : nativeValue(Number(input.value), f.unit, this.fahrenheit);
    this.draft = {
      ...this.draft,
      values: { ...this.draft.values, [f.key]: value },
    };
  }
  private async save() {
    if (
      !this.draft ||
      !dirty(this.draft) ||
      errorFor(this.draft) ||
      this.conflict ||
      this.saving ||
      this.submissionUnknown ||
      !this.canEdit
    )
      return;
    this.saving = true;
    this.error = "";
    this.requestId = newId();
    try {
      const result = await this.hass.callWS<{ operation_id: string }>({
        type: PREFIX + "save",
        schema_version: 1,
        device_id: this._config!.device_id,
        runtime_generation: this.draft.base.runtime_generation,
        base_revision: this.draft.base.revision,
        request_id: this.requestId,
        patch: patchFor(this.draft),
      });
      this.job = {
        operation_id: result.operation_id,
        sequence: -1,
        status: "pending",
        phase: "Preflight",
        confirmed: 0,
        total: 0,
        fields: [],
        reason: null,
      };
      await this.watchJob(result.operation_id);
    } catch (e) {
      this.saving = false;
      const error = e as { message?: string; code?: string };
      this.submissionUnknown = !error.code;
      this.error =
        error.message ??
        "Save acknowledgement was lost. Check request status before any further Save.";
      if (this.submissionUnknown) await this.recoverRequest();
    }
  }
  private async recoverRequest() {
    if (!this.requestId) return;
    try {
      const result = await this.hass.callWS<{ operation_id: string } | null>({
        type: PREFIX + "request",
        device_id: this._config!.device_id,
        request_id: this.requestId,
      });
      if (result) {
        this.submissionUnknown = false;
        this.saving = true;
        await this.watchJob(result.operation_id);
      } else
        this.error =
          "No retained Save record found. Verify controller settings before discarding this draft; it will not be resubmitted automatically.";
    } catch {
      this.error =
        "Cannot determine Save status. Reconnect and check again; no update has been retried.";
    }
  }
  private async stop() {
    if (this.job)
      try {
        await this.hass.callWS({
          type: PREFIX + "stop",
          operation_id: this.job.operation_id,
        });
        this.notice =
          "Stopping after the current request; applied changes remain.";
      } catch {
        this.error = "Could not stop. Check the current operation status.";
      }
  }
  private rebase() {
    if (!this.draft || !this.view) return;
    const retained = this.draft;
    const fresh = makeDraft(this.view);
    const changes = changedFields(retained);
    if (
      fresh.mode !== retained.mode ||
      fresh.base.runtime_generation !== retained.base.runtime_generation
    ) {
      this.error =
        "Mode or connection changed. Discard this draft and edit fresh settings.";
      return;
    }
    this.draft = {
      ...retained,
      base: this.view,
      values: { ...fresh.values, ...changes },
    };
    this.job = undefined;
    this.notice =
      "Draft retained against fresh observations. Review every difference before a new Save.";
  }
  private pointerDown(e: PointerEvent, p: Point) {
    if (!this.draft || this.saving || !this.allScheduleWritable) return;
    const el = e.currentTarget as HTMLElement;
    this.selected = p.draft_id;
    this.drag = {
      id: p.draft_id,
      x: e.clientX,
      pointer: e.pointerId,
      start: p.seconds ?? 0,
      el,
      moved: false,
    };
    el.setPointerCapture(e.pointerId);
  }
  private pointerMove(e: PointerEvent) {
    const drag = this.drag;
    if (!drag || drag.pointer !== e.pointerId) return;
    if (Math.abs(e.clientX - drag.x) < 5 && !drag.moved) return;
    drag.moved = true;
    e.preventDefault();
    const rect = drag.el.parentElement!.getBoundingClientRect();
    const seconds = Math.min(
      86399,
      Math.max(
        0,
        Math.round((((e.clientX - rect.left) / rect.width) * 86400) / 300) *
          300,
      ),
    );
    this.updatePoint(drag.id, { seconds });
  }
  private pointerUp() {
    this.drag = undefined;
  }
  private key(e: KeyboardEvent, p: Point) {
    if (!this.draft || this.saving) return;
    if (e.key === "ArrowLeft" || e.key === "ArrowRight") {
      e.preventDefault();
      this.updatePoint(p.draft_id, {
        seconds: Math.max(
          0,
          Math.min(
            86399,
            (p.seconds ?? 0) +
              (e.key === "ArrowRight" ? 1 : -1) * (e.shiftKey ? 300 : 60),
          ),
        ),
      });
    } else if (e.key === "Delete" && this.mode === "Multi") {
      e.preventDefault();
      this.removePoint(p.draft_id);
    }
  }
  private row(points: Point[], label: string, date?: string | null) {
    const timelineSegments =
      this.mode === "Multi" && this.working && pointError(this.working)
        ? []
        : segments(points);
    const f = this.fieldFor(1);
    const selected =
      points.find((p) => p.draft_id === this.selected) ?? points[0];
    return html`<section class="row">
      <div class="row-title">
        <span>${label}</span>${date !== undefined
          ? html`<small>Starts ${date ?? "Unknown"}</small>`
          : nothing}
      </div>
      <div
        class="timeline"
        aria-label=${`${label} configured 24-hour timeline`}
      >
        ${timelineSegments.map(
          (s) =>
            html`<div
              class="segment ${s.carry ? "carry" : ""}"
              style=${`left:${s.start / 864}%;width:${(s.end - s.start) / 864}%;${targetColors(s.point.target_native, f?.unit, this._config?.temperature_colors)}`}
              title=${`${s.carry ? "Configured carry-over · " : ""}${clock(s.start)}–${clock(s.end === 86400 ? 0 : s.end)} · ${this.format(s.point.target_native, f)}`}
            >
              <span
                >${s.end - s.start > 3600
                  ? this.format(s.point.target_native, f)
                  : ""}</span
              >
            </div>`,
        )}
        ${timelineSegments.length === 0
          ? html`<div class="empty muted">
              Unknown or incomplete boundaries
            </div>`
          : nothing}
        ${repeat(
          points,
          (p) => p.draft_id,
          (p) =>
            p.seconds === null
              ? nothing
              : html`<button
                  class="handle"
                  style=${`left:${p.seconds / 864}%`}
                  aria-label=${`${label} ${clock(p.seconds)} boundary`}
                  aria-pressed=${selected?.draft_id === p.draft_id}
                  title=${clock(p.seconds)}
                  @click=${() => (this.selected = p.draft_id)}
                  @pointerdown=${(e: PointerEvent) => this.pointerDown(e, p)}
                  @pointermove=${this.pointerMove}
                  @pointerup=${this.pointerUp}
                  @pointercancel=${this.pointerUp}
                  @keydown=${(e: KeyboardEvent) => this.key(e, p)}
                ></button>`,
        )}
      </div>
      <div class="axis">
        <span>00</span><span>04</span><span>08</span><span>12</span
        ><span>16</span><span>20</span><span>24</span>
      </div>
      ${this.draft && selected
        ? html`<label class="field slider">
            ${this.mode === "Multi"
              ? `Point ${points.indexOf(selected) + 1}`
              : points.indexOf(selected) % 2 === 0
                ? "Day"
                : "Night"}
            target · ${clock(selected.seconds)} ·
            ${this.format(selected.target_native, this.fieldFor(1))}<input
              aria-label=${`${label} selected target slider`}
              type="range"
              min=${displayValue(
                0,
                this.fieldFor(1)?.unit ?? null,
                this.fahrenheit,
              )}
              max=${displayValue(
                100,
                this.fieldFor(1)?.unit ?? null,
                this.fahrenheit,
              )}
              step="0.5"
              .value=${String(
                displayValue(
                  selected.target_native ?? 0,
                  this.fieldFor(1)?.unit ?? null,
                  this.fahrenheit,
                ),
              )}
              ?disabled=${this.saving || !this.allScheduleWritable}
              @input=${(e: Event) =>
                this.updatePoint(selected.draft_id, {
                  target_native: nativeValue(
                    Number((e.target as HTMLInputElement).value),
                    this.fieldFor(1)?.unit ?? null,
                    this.fahrenheit,
                  ),
                })}
          /></label>`
        : nothing}
      <details class="slot-table">
        <summary>${label} slot table</summary>
        <div class="point-list">
          ${repeat(
            points,
            (p) => p.draft_id,
            (p, i) => {
              const prefix =
                this.mode === "Multi"
                  ? `Point ${this.working!.points.indexOf(p) + 1}`
                  : i % 2 === 0
                    ? "Day"
                    : "Night";
              return html`<div
                class="point ${this.selected === p.draft_id ? "selected" : ""}"
              >
                <button @click=${() => (this.selected = p.draft_id)}>
                  ${prefix}</button
                >${this.draft
                  ? html`<input
                        aria-label=${`${label} ${prefix} start`}
                        type="time"
                        step="1"
                        .value=${live(clock(p.seconds))}
                        ?disabled=${this.saving || !this.allScheduleWritable}
                        @input=${(e: Event) =>
                          this.updatePoint(
                            p.draft_id,
                            {
                              seconds: parseClock(
                                (e.target as HTMLInputElement).value,
                              ),
                            },
                            false,
                          )}
                        @change=${() => this.updatePoint(p.draft_id, {})}
                      /><input
                        aria-label=${`${label} ${prefix} target ${this.unit(f)}`}
                        type="number"
                        min=${displayValue(0, f?.unit ?? null, this.fahrenheit)}
                        max=${displayValue(
                          100,
                          f?.unit ?? null,
                          this.fahrenheit,
                        )}
                        step="any"
                        .value=${live(
                          p.target_native === null
                            ? ""
                            : String(
                                displayValue(
                                  p.target_native,
                                  f?.unit ?? null,
                                  this.fahrenheit,
                                ),
                              ),
                        )}
                        ?disabled=${this.saving || !this.allScheduleWritable}
                        @input=${(e: Event) => {
                          const v = (e.target as HTMLInputElement).value;
                          this.updatePoint(p.draft_id, {
                            target_native:
                              v === ""
                                ? null
                                : nativeValue(
                                    Number(v),
                                    f?.unit ?? null,
                                    this.fahrenheit,
                                  ),
                          });
                        }}
                      />`
                  : html`<span>${clock(p.seconds) || "Unknown"}</span
                      ><span>${this.format(p.target_native, f)}</span>`}
              </div>`;
            },
          )}
        </div>
      </details>
    </section>`;
  }
  private reviewChanges() {
    if (!this.draft) return [];
    const d = this.draft;
    const rows = Object.entries(changedFields(d)).map(([key, value]) => {
      const f = d.base.fields.find((f) => f.key === key)!;
      const fmt = (v: string | number | null) =>
        typeof v === "number" ? this.format(v, f) : (v ?? "Unknown");
      return `${f.label}: ${fmt(f.value)} → ${fmt(value)}`;
    });
    if (["Multi", "Day Night", "Seasonal"].includes(d.mode)) {
      const count = d.mode === "Day Night" ? 2 : 8;
      for (let i = 1; i <= count; i++) {
        const p = d.points[i - 1];
        for (const kind of ["time", "setpoint"]) {
          const f = d.base.fields.find(
            (f) => f.key === `${d.base.channel}_period_${i}_${kind}`,
          );
          if (!f) continue;
          const value = p ? (kind === "time" ? p.seconds : p.target_native) : 0;
          if (value === f.value) continue;
          const fmt = (v: number | null) =>
            kind === "time" ? clock(v) || "Unknown" : this.format(v, f);
          rows.push(
            `${f.label}: ${fmt(f.value as number | null)} → ${fmt(value)}${!p ? " (clear tail)" : ""}`,
          );
        }
      }
    }
    return rows;
  }
  private setting(f: Field) {
    const value =
      this.draft && Object.hasOwn(this.draft.values, f.key)
        ? this.draft.values[f.key]
        : f.value;
    const modeDirty = !!this.draft && dirty(this.draft);
    const disabled =
      this.saving ||
      !f.writable ||
      (f.kind === "enum" &&
        modeDirty &&
        !Object.hasOwn(changedFields(this.draft!), f.key));
    return html`<label class="field"
      ><span>${f.label}${this.unit(f) ? ` (${this.unit(f)})` : ""}</span>${!this
        .draft
        ? html`<strong
            >${typeof value === "number"
              ? this.format(value, f)
              : (value ?? "Unknown")}</strong
          >`
        : f.kind === "enum"
          ? html`<select
              aria-label=${f.label}
              .value=${live(String(value ?? ""))}
              ?disabled=${disabled}
              @change=${(e: Event) => this.setField(f, e)}
            >
              <option value="" disabled>Unknown</option>
              ${f.options.map(
                (o) =>
                  html`<option value=${o} ?selected=${o === value}>
                    ${o}
                  </option>`,
              )}
            </select>`
          : html`<input
              aria-label=${f.label}
              type=${f.kind === "date" ? "text" : "number"}
              placeholder=${f.kind === "date" ? "DD/MM" : ""}
              maxlength=${f.kind === "date" ? 5 : nothing}
              min=${displayValue(f.minimum, f.unit, this.fahrenheit)}
              max=${displayValue(f.maximum, f.unit, this.fahrenheit)}
              step=${f.step}
              .value=${live(
                value === null
                  ? ""
                  : typeof value === "number"
                    ? String(displayValue(value, f.unit, this.fahrenheit))
                    : String(value),
              )}
              ?disabled=${disabled}
              @input=${(e: Event) => this.setField(f, e)}
            />`}${!f.writable
        ? html`<small class="muted">${f.reason}</small>`
        : nothing}</label
    >`;
  }
  render() {
    const v = this.view,
      d = this.working;
    const problem = this.draft ? errorFor(this.draft) : null;
    const points = d?.points ?? [];
    const selected = points.find((p) => p.draft_id === this.selected);
    const expected =
      this.localName === "microclimate-controller-card"
        ? "controller"
        : "channel";
    if (v && v.kind !== expected)
      return html`<ha-card
        >Select a ${expected} device for this card.</ha-card
      >`;
    return html`<ha-card
      ><header>
        <div>
          <h2>${this._config?.title ?? v?.name ?? "Microclimate"}</h2>
          <div class="muted">
            ${v?.model ?? "Connecting…"}${this.draft
              ? " · Draft preview"
              : ""}${v && !v.online ? " · Offline" : ""}
          </div>
        </div>
        ${!this.draft && this.canEdit
          ? html`<button class="primary" @click=${this.edit}>Edit</button>`
          : nothing}
      </header>
      ${this.pendingConfig
        ? html`<section
            role="dialog"
            aria-label="Unsaved schedule changes"
            class="alert"
          >
            <p>Save or discard this draft before changing devices?</p>
            <div class="actions">
              <button @click=${() => this.navigate("stay")}>Stay</button
              ><button
                ?disabled=${this.saving || this.submissionUnknown}
                @click=${() => this.navigate("discard")}
              >
                Discard draft</button
              ><button
                ?disabled=${!!problem ||
                this.conflict ||
                this.saving ||
                !this.canEdit}
                @click=${() => this.navigate("save")}
              >
                Save then switch
              </button>
            </div>
          </section>`
        : nothing}${this.error
        ? html`<div role="alert" class="alert error">${this.error}</div>`
        : nothing}${v?.schema_version !== 1 && v
        ? html`<div class="alert error">
            Card/backend version mismatch. Update both before editing.
          </div>`
        : nothing}
      ${v && d
        ? html`${v.kind === "controller"
            ? html`<h3>Season start dates</h3>
                <p class="muted">
                  Shared by every channel on this controller. Dates follow one
                  annual cycle; a December/January wrap is allowed.
                </p>
                <div class="form">
                  ${v.fields
                    .filter((f) => f.kind === "date")
                    .map((f) => this.setting(f))}
                </div>`
            : html` <div class="badges">
                  ${v.fields
                    .filter((f) => f.kind === "enum")
                    .map(
                      (f) =>
                        html`<span class="badge"
                          >${f.value ?? "Unknown"}</span
                        >`,
                    )}
                </div>
                ${this._config?.show_observations !== false &&
                v.observations.length
                  ? html`<div class="observations">
                      ${v.observations.map(
                        (o) =>
                          html`<div class="observation">
                            <span class="muted">${o.name}</span
                            ><strong>${o.value} ${o.unit ?? ""}</strong>
                          </div>`,
                      )}
                    </div>`
                  : nothing}
                <h3>Configured schedule · controller local time</h3>
                ${this.mode === "Seasonal"
                  ? html`<p class="muted">
                        Dates shared by all channels. Edit dates in the
                        controller card.
                      </p>
                      ${[0, 1, 2, 3].map((i) =>
                        this.row(
                          points.slice(i * 2, i * 2 + 2),
                          `Season ${i + 1}`,
                          (v.fields.find(
                            (f) => f.key === `season_${i + 1}_start_pin`,
                          )?.value as string) ?? null,
                        ),
                      )}`
                  : ["Multi", "Day Night"].includes(this.mode)
                    ? this.row(
                        points,
                        this.mode === "Multi" ? "Multi" : "Day & Night",
                      )
                    : html`<div class="alert">
                        ${this.mode === "Constant"
                          ? "Constant target writing is not mapped."
                          : this.mode === "Periodic"
                            ? "Periodic interval/duration editing is not supported."
                            : "Timing mode unknown."}
                      </div>`}
                ${this.draft && this.mode === "Multi"
                  ? html`${d.repair
                        ? html`<div class="alert error">
                            Existing points need review. Opening this card makes
                            no changes.
                            <button @click=${this.repair}>
                              Review/rebuild point list
                            </button>
                          </div>`
                        : nothing}
                      <div class="actions">
                        <button
                          ?disabled=${points.length >= 8 ||
                          this.saving ||
                          !this.allScheduleWritable}
                          @click=${this.add}
                        >
                          Add point</button
                        ><button
                          ?disabled=${points.length <= 2 ||
                          !selected ||
                          this.saving ||
                          !this.allScheduleWritable}
                          @click=${() =>
                            selected && this.removePoint(selected.draft_id)}
                        >
                          Remove selected
                        </button>
                      </div>
                      <p class="muted">
                        2–8 consecutive points. Inserting/removing shifts later
                        points; unused tail slots are cleared.
                      </p>`
                  : nothing}
                ${!this.draft && d.repair
                  ? html`<div class="alert error">
                      ${pointError(d)} Edit to review/rebuild; observations are
                      unchanged.
                    </div>`
                  : nothing}
                <details class="settings" ?open=${!!this.draft}>
                  <summary>Channel settings</summary>
                  <p class="muted">
                    Save each mode change separately. Schedule modes share the
                    same stored time/target pairs.
                  </p>
                  <div class="form">
                    ${v.fields
                      .filter((f) => !f.index && !f.shared)
                      .map((f) => this.setting(f))}
                  </div>
                </details>`}`
        : nothing}
      ${this.submissionUnknown
        ? html`<div class="alert error">
            Save result is unresolved.
            <button @click=${this.recoverRequest}>Check request status</button>
          </div>`
        : nothing}${this.notice
        ? html`<div role="status" class="alert">${this.notice}</div>`
        : nothing}
      ${this.draft
        ? html`${problem
              ? html`<div role="alert" class="alert error">${problem}</div>`
              : nothing}${this.conflict && !this.saving
              ? html`<div class="alert error">
                  Settings changed since editing began.
                  <button @click=${this.rebase}>
                    Refresh and review draft
                  </button>
                </div>`
              : nothing}
            <p class="muted">
              Save sends changes sequentially. Intermediate settings may affect
              the controller; confirmed changes cannot be rolled back
              automatically.
            </p>
            <details class="review" open>
              <summary>
                ${this.reviewChanges().length} changed fields · review
              </summary>
              ${this.reviewChanges().map((line) => html`<div>${line}</div>`)}
            </details>
            <div class="actions">
              ${this.saving
                ? html`<button @click=${this.stop}>
                    Stop remaining changes
                  </button>`
                : html`<button @click=${this.cancel}>Cancel</button
                    ><button
                      class="primary"
                      ?disabled=${!dirty(this.draft) ||
                      !!problem ||
                      this.conflict ||
                      !this.canEdit ||
                      this.draft.repair ||
                      this.submissionUnknown}
                      @click=${this.save}
                    >
                      Save changes
                    </button>`}
            </div>`
        : nothing}
      ${this.job
        ? html`<section aria-live="polite" class="alert">
            <strong
              >${this.job.status} · ${this.job.confirmed}/${this.job.total}
              confirmed</strong
            ><progress
              max=${Math.max(1, this.job.total)}
              value=${this.job.confirmed}
            ></progress
            >${this.job.reason
              ? html`<p>${this.job.reason.replaceAll("_", " ")}</p>`
              : nothing}
            <details>
              <summary>Change results</summary>
              ${this.job.fields.map(
                (f) => html`<div class="status">${f.label}: ${f.status}</div>`,
              )}
            </details>
          </section>`
        : nothing}
    </ha-card>`;
  }
}
