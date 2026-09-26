/** Card-specific live session, draft and Save ownership. No DOM rendering. */
import type { Config, Draft, Hass, Job, Snapshot } from "./types";
import { PREFIX, terminal } from "./types";
import { changedFields, dirty, errorFor, makeDraft, patchFor } from "./draft";
import { newId } from "./id";
import { acknowledgement, errorEnvelope, job as decodeJob, recovery, safeError, snapshot as decodeSnapshot } from "./protocol";
import { localize, type MessageKey } from "./localize";

export class CardSession {
  constructor(private readonly changed: () => void, private readonly onSelect: (id: string) => void) {}
  hass?: Hass;
  t(key: MessageKey, params: Record<string, string | number> = {}) { return localize(key, this.hass?.language, params); }
  connected = false;
  private requestId?: string;
  private navigateAfterSave = false;
  private unsubscribe?: () => void;
  private unsubJob?: () => void;
  private epoch = 0;
  private watch = 0;
  private subscribed = "";
  private _view: Snapshot | undefined = undefined;
  get view(): Snapshot | undefined { return this._view; }
  set view(value: Snapshot | undefined) { this._view = value; this.changed(); }
  private _draft: Draft | undefined = undefined;
  get draft(): Draft | undefined { return this._draft; }
  set draft(value: Draft | undefined) { this._draft = value; this.changed(); }
  private _job: Job | undefined = undefined;
  get job(): Job | undefined { return this._job; }
  set job(value: Job | undefined) { this._job = value; this.changed(); }
  private _error: string = "";
  get error(): string { return this._error; }
  set error(value: string) { this._error = value; this.changed(); }
  private _notice: string = "";
  get notice(): string { return this._notice; }
  set notice(value: string) { this._notice = value; this.changed(); }
  private _saving: boolean = false;
  get saving(): boolean { return this._saving; }
  set saving(value: boolean) { this._saving = value; this.changed(); }
  private _submissionUnknown: boolean = false;
  get submissionUnknown(): boolean { return this._submissionUnknown; }
  set submissionUnknown(value: boolean) { this._submissionUnknown = value; this.changed(); }
  private _pendingConfig: Config | undefined = undefined;
  get pendingConfig(): Config | undefined { return this._pendingConfig; }
  set pendingConfig(value: Config | undefined) { this._pendingConfig = value; this.changed(); }
  private _config: Config | undefined = undefined;
  get config(): Config | undefined { return this._config; }
  set config(value: Config | undefined) { this._config = value; this.changed(); }
  private reconnect = () => {
    this.release();
    void this.subscribe();
  };
  setHass(value: Hass) {
    const changed = this.hass?.connection !== value.connection;
    if (changed) {
      this.hass?.connection.removeEventListener?.("ready", this.reconnect);
      this.release();
    }
    this.hass = value;
    if (changed) value.connection.addEventListener?.("ready", this.reconnect);
    void this.subscribe();
  }
  setConfig(config: Config) {
    if (!config.device_id || typeof config.device_id !== "string")
      throw new Error(this.t("select_device"));
    if (this.config?.device_id !== config.device_id) {
      if (this.draft && dirty(this.draft)) {
        this.pendingConfig = config;
        return;
      }
      this.release();
      this.view = undefined;
      this.job = undefined;
      this.onSelect("");
      this.requestId = undefined;
      this.submissionUnknown = false;
      this.saving = false;
    }
    this.config = { ...config };
    void this.subscribe();
  }
  connect() {
    this.connected = true;
    this.hass?.connection.addEventListener?.("ready", this.reconnect);
    void this.subscribe();
  }
  disconnect() {
    this.connected = false;
    this.hass?.connection.removeEventListener?.("ready", this.reconnect);
    this.release();
  }
  private release() {
    this.epoch++;
    this.watch++;
    if (this.saving && this.requestId && !this.job) this.submissionUnknown = true;
    this.unsubscribe?.();
    this.unsubJob?.();
    this.unsubscribe = undefined;
    this.unsubJob = undefined;
    this.subscribed = "";
  }
  private async subscribe() {
    if (!this.connected || !this.hass || !this.config || this.subscribed)
      return;
    const epoch = this.epoch;
    this.subscribed = this.config.device_id;
    try {
      const unsub = await this.hass!.connection.subscribeMessage<unknown>(
        (v) => {
          if (epoch !== this.epoch) return;
          const error = errorEnvelope(v);
          if (error) {
            this.error = this.t("snapshot_unavailable");
            this.view = undefined;
            return;
          }
          const decoded = decodeSnapshot(v, this.config!.device_id);
          if (!decoded.ok) {
            this.error = this.t(decoded.reason === "unsupported" ? "schema_mismatch" : "snapshot_invalid");
            this.view = undefined;
            return;
          }
          this.view = decoded.value;
          this.error = "";
        },
        { type: PREFIX + "subscribe", device_id: this.config.device_id },
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
          this.t("subscribe_failed");
      }
    }
  }
  private async watchJob(operation_id: string) {
    const watch = ++this.watch;
    this.unsubJob?.();
    const epoch = this.epoch;
    const unsub = await this.hass!.connection.subscribeMessage<unknown>(
      (raw) => {
        if (epoch !== this.epoch || watch !== this.watch) return;
        if (errorEnvelope(raw)) {
          this.error =
            this.t("job_unavailable");
          this.saving = false;
          this.submissionUnknown = true;
          return;
        }
        const decoded = decodeJob(raw, operation_id);
        if (!decoded.ok) {
          this.error = this.t("job_invalid");
          this.saving = false;
          this.submissionUnknown = true;
          return;
        }
        const j = decoded.value;
        if (this.job?.operation_id === j.operation_id && j.sequence <= this.job.sequence)
          return;
        this.job = j;
        if (terminal(j)) {
          this.saving = false;
          if (j.status === "succeeded") {
            this.draft = undefined;
            this.submissionUnknown = false;
            this.requestId = undefined;
            this.notice = this.t("confirmed");
            if (this.navigateAfterSave && this.pendingConfig) {
              const config = this.pendingConfig;
              this.pendingConfig = undefined;
              this.navigateAfterSave = false;
              this.setConfig(config);
            }
          } else
            this.notice =
              this.t("partial");
        }
      },
      { type: PREFIX + "operation", operation_id },
    );
    if (epoch !== this.epoch || watch !== this.watch) unsub();
    else this.unsubJob = unsub;
  }
  edit() {
    if (!this.canEdit) return;
    this.draft = makeDraft(this.view!);
    this.job = undefined;
    this.notice = "";
    this.onSelect(this.draft.points[0]?.draft_id ?? "");
  }
  navigate(choice: string) {
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
  cancel() {
    this.draft = undefined;
    this.notice = this.t("draft_discarded");
    this.error = "";
  }
  async save() {
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
    const epoch = this.epoch, requestId = this.requestId, deviceId = this.config!.device_id;
    try {
      const raw = await this.hass!.callWS<unknown>({
        type: PREFIX + "save",
        schema_version: 1,
        device_id: this.config!.device_id,
        runtime_generation: this.draft.base.runtime_generation,
        base_revision: this.draft.base.revision,
        request_id: this.requestId,
        patch: patchFor(this.draft),
      });
      if (epoch !== this.epoch || requestId !== this.requestId || deviceId !== this.config?.device_id) return;
      const result = acknowledgement(raw);
      if (!result.ok) throw new Error(this.t("ack_invalid"));
      this.job = {
        operation_id: result.value.operation_id,
        sequence: -1,
        status: "pending",
        phase: "Preflight",
        confirmed: 0,
        total: 0,
        fields: [],
        reason: null,
      };
      await this.watchJob(result.value.operation_id);
    } catch (e) {
      this.saving = false;
      if (epoch !== this.epoch || requestId !== this.requestId || deviceId !== this.config?.device_id) return;
      const error = safeError(e);
      this.submissionUnknown = !error.code;
      this.error = error.message ?? this.t("ack_lost");
      if (this.submissionUnknown) await this.recoverRequest();
    }
  }
  async recoverRequest() {
    if (!this.requestId) return;
    const epoch = this.epoch, requestId = this.requestId, deviceId = this.config!.device_id;
    try {
      const raw = await this.hass!.callWS<unknown>({
        type: PREFIX + "request",
        device_id: this.config!.device_id,
        request_id: this.requestId,
      });
      if (epoch !== this.epoch || requestId !== this.requestId || deviceId !== this.config?.device_id) return;
      const result = recovery(raw);
      if (!result.ok) throw new Error(this.t("recovery_invalid"));
      if (result.value) {
        this.submissionUnknown = false;
        this.saving = true;
        await this.watchJob(result.value.operation_id);
      } else
        this.error =
          this.t("no_record");
    } catch {
      if (epoch !== this.epoch || requestId !== this.requestId || deviceId !== this.config?.device_id) return;
      this.error = this.t("recovery_unavailable");
    }
  }
  async stop() {
    if (this.job) {
      const epoch = this.epoch, operationId = this.job.operation_id;
      try {
        await this.hass!.callWS({
          type: PREFIX + "stop",
          operation_id: operationId,
        });
        if (epoch !== this.epoch || operationId !== this.job?.operation_id) return;
        this.notice = this.t("stopping");
      } catch {
        if (epoch === this.epoch) this.error = this.t("stop_failed");
      }
    }
  }
  rebase() {
    if (!this.draft || !this.view) return;
    const retained = this.draft;
    const fresh = makeDraft(this.view);
    const changes = changedFields(retained);
    if (
      fresh.mode !== retained.mode ||
      fresh.base.runtime_generation !== retained.base.runtime_generation
    ) {
      this.error =
        this.t("rebase_blocked");
      return;
    }
    this.draft = {
      ...retained,
      base: this.view,
      values: { ...fresh.values, ...changes },
    };
    this.job = undefined;
    this.notice =
      this.t("rebase_review");
  }
  get conflict() {
    return !!this.draft && !!this.view && (this.draft.base.revision !== this.view.revision ||
      this.draft.base.runtime_generation !== this.view.runtime_generation);
  }
  get canEdit() {
    return !!this.view && this.view.schema_version === 1 && this.view.online && !this.view.busy &&
      this.view.writes_enabled && !this.config?.read_only && this.view.fields.some((f) => f.writable);
  }
}
