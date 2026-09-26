import { html, nothing } from "lit";
import { live } from "lit/directives/live.js";
import type { Field } from "../types";
import type { MicroclimateCard } from "../card";
import { changedFields, clock, dirty, displayValue } from "../draft";
export function reviewChanges(card: MicroclimateCard) {
    if (!card.draft) return [];
    const d = card.draft;
    const rows = Object.entries(changedFields(d)).map(([key, value]) => {
      const f = d.base.fields.find((f) => f.key === key)!;
      const fmt = (v: string | number | null) =>
        typeof v === "number" ? card.format(v, f) : (v ?? card.t("unknown"));
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
            kind === "time" ? clock(v) || card.t("unknown") : card.format(v, f);
          rows.push(
            `${f.label}: ${fmt(f.value as number | null)} → ${fmt(value)}${!p ? card.t("clear_tail") : ""}`,
          );
        }
      }
    }
    return rows;
}
export function setting(card: MicroclimateCard, f: Field) {
    const value =
      card.draft && Object.hasOwn(card.draft.values, f.key)
        ? card.draft.values[f.key]
        : f.value;
    const modeDirty = !!card.draft && dirty(card.draft);
    const disabled =
      card.saving ||
      !f.writable ||
      (f.kind === "enum" &&
        modeDirty &&
        !Object.hasOwn(changedFields(card.draft!), f.key));
    return html`<label class="field"
      ><span>${f.label}${card.unit(f) ? ` (${card.unit(f)})` : ""}</span>${!card.draft
        ? html`<strong
            >${typeof value === "number"
              ? card.format(value, f)
              : (value ?? card.t("unknown"))}</strong
          >`
        : f.kind === "enum"
          ? html`<select
              aria-label=${f.label}
              .value=${live(String(value ?? ""))}
              ?disabled=${disabled}
              @change=${(e: Event) => card.setField(f, e)}
            >
              <option value="" disabled>${card.t("unknown")}</option>
              ${f.options.map(
                (o) =>
                  html`<option value=${o} ?selected=${o === value}>
                    ${card.optionLabel(o)}
                  </option>`,
              )}
            </select>`
          : html`<input
              aria-label=${f.label}
              type=${f.kind === "date" ? "text" : "number"}
              placeholder=${f.kind === "date" ? "DD/MM" : ""}
              maxlength=${f.kind === "date" ? 5 : nothing}
              min=${displayValue(f.minimum, f.unit, card.fahrenheit)}
              max=${displayValue(f.maximum, f.unit, card.fahrenheit)}
              step=${f.step}
              .value=${live(
                value === null
                  ? ""
                  : typeof value === "number"
                    ? String(displayValue(value, f.unit, card.fahrenheit))
                    : String(value),
              )}
              ?disabled=${disabled}
              @input=${(e: Event) => card.setField(f, e)}
            />`}${!f.writable
        ? html`<small class="muted">${f.reason}</small>`
        : nothing}</label
    >`;
}
