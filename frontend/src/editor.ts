import { DEFAULT_COLORS, validateColors } from "./colors";
import { LitElement, html, css, nothing } from "lit";
import type { Config, Hass } from "./types";
import { PREFIX } from "./types";
import { devices as decodeDevices } from "./protocol";
import { localize, type MessageKey } from "./localize";
export class MicroclimateEditor extends LitElement {
  static properties = {
    config: { state: true },
    devices: { state: true },
    error: { state: true },
    colorError: { state: true },
  };
  static styles = css`
    label {
      display: block;
      margin: 12px 0;
    }
    input,
    select {
      display: block;
      width: 100%;
      box-sizing: border-box;
      min-height: 44px;
      margin: 6px 0;
      font: inherit;
    }
    input[type="checkbox"] {
      width: auto;
      display: inline;
      min-height: 0;
    }
  `;
  t(key: MessageKey, params: Record<string, string | number> = {}) { return localize(key, this._hass?.language, params); }
  config?: Config;
  devices: { device_id: string; kind: string; name: string }[] = [];
  error = "";
  colorError = "";
  private _hass?: Hass;
  private epoch = 0;
  set hass(h: Hass) {
    if (this._hass === h) return;
    this._hass = h;
    const epoch = ++this.epoch;
    this.devices = [];
    void h.callWS<unknown>({ type: PREFIX + "list" }).then((raw) => {
      if (epoch !== this.epoch) return;
      const decoded = decodeDevices(raw);
      if (!decoded.ok) {
        this.error = this.t("device_list_invalid");
        return;
      }
      this.devices = decoded.value;
      this.error = "";
    }).catch(() => {
      if (epoch === this.epoch) this.error = this.t("device_list_unavailable");
    });
  }
  setConfig(c: Config) {
    this.config = { ...c };
  }
  private change(key: string, value: unknown) {
    this.config = { ...this.config!, [key]: value };
    this.dispatchEvent(
      new CustomEvent("config-changed", {
        detail: { config: this.config },
        bubbles: true,
        composed: true,
      }),
    );
  }
  private colors() {
    return this.config?.temperature_colors ?? DEFAULT_COLORS;
  }
  private changeColor(
    index: number,
    key: "temperature" | "color",
    value: string,
  ) {
    const colors = this.colors().map((c, i) =>
      i === index
        ? {
            ...c,
            [key]:
              key === "temperature"
                ? value.trim()
                  ? Number(value)
                  : NaN
                : value,
          }
        : { ...c },
    );
    try {
      validateColors(colors);
      this.colorError = "";
      this.change("temperature_colors", colors);
    } catch (e) {
      this.colorError = (e as Error).message;
    }
  }
  render() {
    const kind = this.config?.type.includes("controller")
      ? "controller"
      : "channel";
    return html`<p>
        ${this.error ||
        this.t("editor_intro")}
      </p>
      <label
        >${this.t("editor_device")}<select
          aria-label=${this.t("editor_device")}
          .value=${this.config?.device_id ?? ""}
          @change=${(e: Event) =>
            this.change("device_id", (e.target as HTMLSelectElement).value)}
        >
          <option value="">${this.t("editor_select_device")}</option>
          ${this.devices
            .filter((d) => d.kind === kind)
            .map(
              (d) =>
                html`<option
                  value=${d.device_id}
                  ?selected=${d.device_id === this.config?.device_id}
                >
                  ${d.name}
                </option>`,
            )}
        </select></label
      ><label
        >${this.t("editor_title")}<input
          .value=${this.config?.title ?? ""}
          @input=${(e: Event) =>
            this.change(
              "title",
              (e.target as HTMLInputElement).value,
            )} /></label
      ><label
        ><input
          type="checkbox"
          .checked=${!!this.config?.read_only}
          @change=${(e: Event) =>
            this.change("read_only", (e.target as HTMLInputElement).checked)}
        />${this.t("editor_read_only")}</label
      >${kind === "channel"
        ? html`<details>
            <summary>${this.t("editor_colors")}</summary>
            <p>
              ${this.t("editor_colors_help")}
            </p>
            ${this.colorError
              ? html`<p role="alert">${this.colorError}</p>`
              : nothing}
            ${this.colors().map(
              (c, i) =>
                html`<fieldset>
                  <legend>${this.t("editor_color_number", { number: i + 1 })}</legend>
                  <label
                    >${this.t("editor_lower")}<input
                      type="number"
                      min="0"
                      max="100"
                      step="any"
                      aria-label=${this.t("editor_color_lower", { number: i + 1 })}
                      .value=${String(c.temperature)}
                      @change=${(e: Event) =>
                        this.changeColor(
                          i,
                          "temperature",
                          (e.target as HTMLInputElement).value,
                        )}
                  /></label>
                  <label
                    >${this.t("editor_color")}<input
                      type="color"
                      aria-label=${this.t("editor_color_value", { number: i + 1 })}
                      .value=${c.color}
                      @input=${(e: Event) =>
                        this.changeColor(
                          i,
                          "color",
                          (e.target as HTMLInputElement).value,
                        )}
                  /></label>
                  <button
                    ?disabled=${this.colors().length === 1}
                    @click=${() => {
                      this.colorError = "";
                      this.change(
                        "temperature_colors",
                        this.colors().filter((_, j) => j !== i),
                      );
                    }}
                  >
                    ${this.t("editor_remove_color", { number: i + 1 })}
                  </button>
                </fieldset>`,
            )}
            <button
              ?disabled=${this.colors().length >= 101}
              @click=${() => {
                const used = new Set(this.colors().map((c) => c.temperature));
                let temperature = 0;
                while (used.has(temperature)) temperature++;
                this.change("temperature_colors", [
                  ...this.colors(),
                  { temperature, color: "#b52222" },
                ]);
              }}
            >
              ${this.t("editor_add_color")}
            </button>
            <button
              @click=${() => {
                this.colorError = "";
                this.change("temperature_colors", undefined);
              }}
            >
              ${this.t("editor_reset_color")}
            </button>
          </details>`
        : nothing}`;
  }
}
