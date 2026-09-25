import { DEFAULT_COLORS, validateColors } from "./colors";
import { LitElement, html, css, nothing } from "lit";
import type { Config, Hass } from "./types";
import { PREFIX } from "./types";
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
  config?: Config;
  devices: { device_id: string; kind: string; name: string }[] = [];
  error = "";
  colorError = "";
  private _hass?: Hass;
  set hass(h: Hass) {
    if (this._hass === h) return;
    const first = !this._hass;
    this._hass = h;
    if (first)
      void h
        .callWS<typeof this.devices>({ type: PREFIX + "list" })
        .then((d) => (this.devices = d))
        .catch(
          () =>
            (this.error = "Unable to list authorized Microclimate devices."),
        );
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
        "Select a registered Microclimate device. Entity renames do not change this binding."}
      </p>
      <label
        >Device<select
          aria-label="Device"
          .value=${this.config?.device_id ?? ""}
          @change=${(e: Event) =>
            this.change("device_id", (e.target as HTMLSelectElement).value)}
        >
          <option value="">Select device</option>
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
        >Title<input
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
        />Always read only</label
      >${kind === "channel"
        ? html`<details>
            <summary>Temperature colours</summary>
            <p>
              Inclusive lower bounds in °C, also when HA displays °F. Below the
              lowest bound uses its colour. Percentage targets use teal.
            </p>
            ${this.colorError
              ? html`<p role="alert">${this.colorError}</p>`
              : nothing}
            ${this.colors().map(
              (c, i) =>
                html`<fieldset>
                  <legend>Colour ${i + 1}</legend>
                  <label
                    >Lower temperature (°C)<input
                      type="number"
                      min="0"
                      max="100"
                      step="any"
                      aria-label=${`Colour ${i + 1} lower temperature °C`}
                      .value=${String(c.temperature)}
                      @change=${(e: Event) =>
                        this.changeColor(
                          i,
                          "temperature",
                          (e.target as HTMLInputElement).value,
                        )}
                  /></label>
                  <label
                    >Colour<input
                      type="color"
                      aria-label=${`Colour ${i + 1} value`}
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
                    Remove colour ${i + 1}
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
              Add temperature colour
            </button>
            <button
              @click=${() => {
                this.colorError = "";
                this.change("temperature_colors", undefined);
              }}
            >
              Reset temperature colours
            </button>
          </details>`
        : nothing}`;
  }
}
