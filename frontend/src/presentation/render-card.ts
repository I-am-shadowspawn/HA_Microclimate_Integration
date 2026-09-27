import { html, nothing } from "lit";
import type { MicroclimateCard } from "../card";
import { errorFor, pointError } from "../draft";
import { saveStatus } from "./save-status";
import { modelIconUrl } from "../model-icon";
export function renderCard(card: MicroclimateCard) {
    const v = card.view,
      d = card.working;
    const icon = v ? modelIconUrl(v.model) : null;
    const problem = card.draft ? errorFor(card.draft) : null;
    const points = d?.points ?? [];
    const selected = points.find((p) => p.draft_id === card.selected);
    const expected =
      card.localName === "microclimate-controller-card"
        ? "controller"
        : "channel";
    if (v && v.kind !== expected)
      return html`<ha-card
        >${card.t("wrong_device", { kind: expected })}</ha-card
      >`;
    return html`<ha-card
      ><header>
        <div class="identity">
          ${icon
            ? html`<img class="model-icon" src=${icon} alt=${v?.model ?? ""} width="48" height="48" />`
            : nothing}
          <div>
            <h2>${card._config?.title ?? v?.name ?? "Microclimate"}</h2>
            <div class="muted">
              ${v?.model ?? card.t("connecting")}${card.draft
                ? card.t("draft_preview")
                : ""}${v && !v.online ? card.t("offline") : ""}
            </div>
          </div>
        </div>
        ${!card.draft && card.canEdit
          ? html`<button class="primary" @click=${card.edit}>${card.t("edit")}</button>`
          : nothing}
      </header>
      ${card.pendingConfig
        ? html`<section
            role="dialog"
            aria-label=${card.t("unsaved")}
            class="alert"
          >
            <p>${card.t("unsaved_prompt")}</p>
            <div class="actions">
              <button @click=${() => card.navigate("stay")}>${card.t("stay")}</button
              ><button
                ?disabled=${card.saving || card.submissionUnknown}
                @click=${() => card.navigate("discard")}
              >
                ${card.t("discard_draft")}</button
              ><button
                ?disabled=${!!problem ||
                card.conflict ||
                card.saving ||
                !card.canEdit}
                @click=${() => card.navigate("save")}
              >
                ${card.t("save_then_switch")}
              </button>
            </div>
          </section>`
        : nothing}${card.error
        ? html`<div role="alert" class="alert error">${card.error}</div>`
        : nothing}${v?.schema_version !== 1 && v
        ? html`<div class="alert error">
            ${card.t("mismatch")}
          </div>`
        : nothing}
      ${v && d
        ? html`${v.kind === "controller"
            ? html`<h3>${card.t("season_dates")}</h3>
                <p class="muted">
                  ${card.t("dates_help")}
                </p>
                <div class="form">
                  ${v.fields
                    .filter((f) => f.kind === "date")
                    .map((f) => card.setting(f))}
                </div>`
            : html` <div class="badges">
                  ${v.fields
                    .filter((f) => f.kind === "enum")
                    .map(
                      (f) =>
                        html`<span class="badge"
                          >${f.value ?? card.t("unknown")}</span
                        >`,
                    )}
                </div>
                ${card._config?.show_observations !== false &&
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
                <h3>${card.t("schedule_heading")}</h3>
                <p class="muted">${card.t("controller_time")}</p>
                ${card.mode === "Seasonal"
                  ? html`<p class="muted">
                        ${card.t("seasonal_dates_help")}
                      </p>
                      ${[0, 1, 2, 3].map((i) =>
                        card.row(
                          points.slice(i * 2, i * 2 + 2),
                          card.t("season", { number: i + 1 }),
                          (v.fields.find(
                            (f) => f.key === `season_${i + 1}_start_pin`,
                          )?.value as string) ?? null,
                        ),
                      )}`
                  : ["Multi", "Day Night"].includes(card.mode)
                    ? card.row(
                        points,
                        card.mode === "Multi" ? card.t("multi") : card.t("day_and_night"),
                      )
                    : html`<div class="alert">
                        ${card.mode === "Constant"
                          ? card.t("constant_unmapped")
                          : card.mode === "Periodic"
                            ? card.t("periodic_unmapped")
                            : card.t("timing_unknown")}
                      </div>`}
                ${card.draft && card.mode === "Multi"
                  ? html`${d.repair
                        ? html`<div class="alert error">
                            ${card.t("repair_needed")}
                            <button @click=${card.repair}>
                              ${card.t("point_rebuild")}
                            </button>
                          </div>`
                        : nothing}
                      <div class="actions">
                        <button
                          ?disabled=${points.length >= 8 ||
                          card.saving ||
                          !card.allScheduleWritable}
                          @click=${card.add}
                        >
                          ${card.t("add_point")}</button
                        ><button
                          ?disabled=${points.length <= 2 ||
                          !selected ||
                          card.saving ||
                          !card.allScheduleWritable}
                          @click=${() =>
                            selected && card.removePoint(selected.draft_id)}
                        >
                          ${card.t("remove_selected")}
                        </button>
                      </div>
                      <p class="muted">
                        ${card.t("multi_help")}
                      </p>`
                  : nothing}
                ${!card.draft && d.repair
                  ? html`<div class="alert error">
                      ${pointError(d)} ${card.t("repair_observation")}
                    </div>`
                  : nothing}
                ${["Day Night", "Multi", "Seasonal"].includes(card.mode)
                  ? html`<div class="actions">
                      <button
                        ?disabled=${!!pointError(d)}
                        @click=${card.downloadPreset}
                      >${card.t("download_preset")}</button>
                      ${card.draft
                        ? html`<button
                              ?disabled=${card.saving || !card.canEdit || !card.allScheduleWritable}
                              @click=${() =>
                                (card.renderRoot.querySelector<HTMLInputElement>("#preset-file")?.click())}
                            >${card.t("import_preset")}</button>
                            <input
                              id="preset-file"
                              type="file"
                              accept=".json,application/json"
                              hidden
                              @change=${card.loadPreset}
                            />`
                        : nothing}
                    </div>
                    <p class="muted">${card.t("preset_help")}</p>`
                  : nothing}
                <details class="settings" ?open=${!!card.draft}>
                  <summary>${card.t("channel_settings")}</summary>
                  <p class="muted">
                    ${card.t("settings_help")}
                  </p>
                  <div class="form">
                    ${v.fields
                      .filter((f) => !f.index && !f.shared)
                      .map((f) => card.setting(f))}
                  </div>
                </details>`}`
        : nothing}
      ${saveStatus(card, problem)}
    </ha-card>`;
  }
