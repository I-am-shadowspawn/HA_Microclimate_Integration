import { CardSession } from "./card-session";
import { localize, type MessageKey } from "./localize";
import { validateColors } from "./colors";
import { newId } from "./id";
import { exportPreset, importPreset, MAX_PRESET_BYTES } from "./preset";
import { LitElement } from "lit";
import { cardStyles } from "./card-styles";
import { scheduleRow } from "./presentation/schedule-row";
import { reviewChanges, setting } from "./presentation/settings";
import { renderCard } from "./presentation/render-card";
import type { Config, Draft, Field, Hass, Point } from "./types";
import {
  makeDraft,
  displayValue,
  nativeValue,
  dirty,
} from "./draft";

export class MicroclimateCard extends LitElement {
  static properties = {
    selected: { state: true },
  };
  static styles = cardStyles;
  t(key: MessageKey, params: Record<string, string | number> = {}) { return localize(key, this.hass?.language, params); }
  optionLabel(value: string): string {
    const known: Record<string, MessageKey> = { fixed: "fixed", heating: "heating", cooling: "cooling",
      pulse: "pulse", dimming: "dimming", Constant: "constant", "Day Night": "day_night_option",
      Multi: "multi", Periodic: "periodic", Seasonal: "seasonal" };
    return known[value] ? this.t(known[value]) : value;
  }
  readonly session = new CardSession(() => this.requestUpdate(), id => { this.selected = id; });
  selected = "";
  observedDraft?: Draft;
  drag?: { id: string; x: number; pointer: number; start: number; el: HTMLElement; moved: boolean };
  get _config() { return this.session.config; }
  get _hass() { return this.session.hass; }
  get view() { return this.session.view; }
  get draft() { return this.session.draft; }
  set draft(value: Draft | undefined) { this.session.draft = value; }
  get job() { return this.session.job; }
  get error() { return this.session.error; }
  set error(value: string) { this.session.error = value; }
  get notice() { return this.session.notice; }
  set notice(value: string) { this.session.notice = value; }
  get saving() { return this.session.saving; }
  get submissionUnknown() { return this.session.submissionUnknown; }
  get pendingConfig() { return this.session.pendingConfig; }
  set pendingConfig(value: Config | undefined) { this.session.pendingConfig = value; }
  set hass(value: Hass) { this.session.setHass(value); }
  get hass() { return this.session.hass!; }
  setConfig(config: Config) { validateColors(config.temperature_colors); this.session.setConfig(config); }
  unload = (e: BeforeUnloadEvent) => {
    if (this.draft && dirty(this.draft)) { e.preventDefault(); e.returnValue = ""; }
  };
  connectedCallback() {
    super.connectedCallback();
    window.addEventListener("beforeunload", this.unload);
    this.session.connect();
  }
  disconnectedCallback() {
    super.disconnectedCallback();
    window.removeEventListener("beforeunload", this.unload);
    this.drag = undefined;
    this.session.disconnect();
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
  get fahrenheit() {
    return this._hass?.config?.unit_system.temperature === "°F";
  }
  get mode() {
    return (
      this.draft?.mode ??
      String(
        this.view?.fields.find(
          (f) => f.key === `${this.view?.channel}_timing_type`,
        )?.value ?? "",
      )
    );
  }
  get working() {
    if (this.draft) return this.draft;
    if (!this.view) return undefined;
    if (this.observedDraft?.base !== this.view)
      this.observedDraft = makeDraft(this.view);
    return this.observedDraft;
  }
  get conflict() { return this.session.conflict; }
  get canEdit() { return this.session.canEdit; }
  unit(field?: Field) {
    return field?.unit === "°C" || field?.unit === "°F"
      ? this.fahrenheit ? "°F" : "°C" : (field?.unit ?? "");
  }
  format(n: number | null, field?: Field) {
    return n === null
      ? this.t("unknown")
      : `${Number(displayValue(n, field?.unit ?? null, this.fahrenheit).toFixed(3))} ${this.unit(field)}`;
  }
  fieldFor(i: number, kind = "setpoint") {
    return this.view?.fields.find(
      (f) => f.key === `${this.view?.channel}_period_${i}_${kind}`,
    );
  }
  get allScheduleWritable() {
    const count = this.mode === "Day Night" ? 2 : 8;
    return Array.from({ length: count }, (_, i) =>
      ["time", "setpoint"].every(
        (kind) => this.fieldFor(i + 1, kind)?.writable,
      ),
    ).every(Boolean);
  }
  edit() { this.session.edit(); }
  navigate(choice: string) { this.session.navigate(choice); }
  cancel() { this.session.cancel(); }
  updatePoint(id: string, delta: Partial<Point>, reorder = true) {
    if (!this.draft || this.saving || !this.allScheduleWritable) return;
    const points = this.draft.points.map((p) =>
      p.draft_id === id ? { ...p, ...delta } : p,
    );
    if (reorder && this.mode === "Multi" && !this.draft.repair)
      points.sort((a, b) => (a.seconds ?? Infinity) - (b.seconds ?? Infinity));
    this.draft = { ...this.draft, points };
  }
  add() {
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
    const point = { draft_id: newId(), seconds,
      target_native: this.fieldFor(1)?.unit === "°F" ? 68 : 20 };
    this.draft = {
      ...this.draft,
      points: [...this.draft.points, point].sort(
        (a, b) => (a.seconds ?? Infinity) - (b.seconds ?? Infinity),
      ),
    };
    this.selected = point.draft_id;
    void this.focusPoint(point.draft_id);
  }
  removePoint(id: string) {
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
    if (this.selected) void this.focusPoint(this.selected);
  }
  async focusPoint(id: string) {
    await this.updateComplete;
    const handle = Array.from(this.renderRoot.querySelectorAll<HTMLElement>(".handle"))
      .find((candidate) => candidate.dataset.pointId === id);
    handle?.focus();
  }
  repair() {
    if (!this.draft) return;
    this.draft = {
      ...this.draft,
      repair: false,
      points: this.draft.points
        .filter((p) => !(p.seconds === 0 && p.target_native === 0))
        .sort((a, b) => (a.seconds ?? Infinity) - (b.seconds ?? Infinity)),
    };
    this.notice =
      this.t("repair_review");
  }
  downloadPreset() {
    if (!this.working || !this.view?.channel) return;
    try {
      const contents = JSON.stringify(exportPreset(this.working), null, 2);
      const url = URL.createObjectURL(new Blob([contents], { type: "application/json" }));
      const link = document.createElement("a");
      link.href = url;
      link.download = `microclimate-${this.mode.toLowerCase().replaceAll(" ", "-")}-schedule.json`;
      link.click();
      setTimeout(() => URL.revokeObjectURL(url), 0);
      this.notice = this.t("preset_downloaded");
    } catch (e) {
      this.error = (e as Error).message;
    }
  }
  async loadPreset(e: Event) {
    const input = e.target as HTMLInputElement;
    const file = input.files?.[0];
    input.value = "";
    if (!file || !this.draft || this.saving || !this.canEdit || !this.allScheduleWritable) return;
    try {
      if (file.size > MAX_PRESET_BYTES) throw new Error(this.t("preset_too_large"));
      const parsed: unknown = JSON.parse(await file.text());
      this.draft = importPreset(this.draft, parsed);
      this.selected = this.draft.points[0]?.draft_id ?? "";
      this.notice = this.t("preset_loaded");
      this.error = "";
    } catch (e) {
      this.error = e instanceof SyntaxError ? this.t("preset_json_invalid") : (e as Error).message;
    }
  }
  setField(f: Field, e: Event) {
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
  save() { return this.session.save(); }
  recoverRequest() { return this.session.recoverRequest(); }
  stop() { return this.session.stop(); }
  rebase() { this.session.rebase(); }
  pointerDown(e: PointerEvent, p: Point) {
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
  pointerMove(e: PointerEvent) {
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
  pointerUp() {
    this.drag = undefined;
  }
  key(e: KeyboardEvent, p: Point) {
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
  row(points: Point[], label: string, date?: string | null) { return scheduleRow(this, points, label, date); }
  reviewChanges() { return reviewChanges(this); }
  setting(f: Field) { return setting(this, f); }
  render() { return renderCard(this); }
}
