import { html, nothing } from "lit";
import type { MicroclimateCard } from "../card";
import { dirty } from "../draft";
export function saveStatus(card: MicroclimateCard, problem: string | null) {
  return html`
      ${card.submissionUnknown
        ? html`<div class="alert error">
            ${card.t("save_unresolved")}
            <button @click=${card.recoverRequest}>${card.t("check_request")}</button>
          </div>`
        : nothing}${card.notice
        ? html`<div role="status" class="alert">${card.notice}</div>`
        : nothing}
      ${card.draft
        ? html`${problem
              ? html`<div role="alert" class="alert error">${problem}</div>`
              : nothing}${card.conflict && !card.saving
              ? html`<div class="alert error">
                  ${card.t("settings_changed")}
                  <button @click=${card.rebase}>
                    ${card.t("refresh_review")}
                  </button>
                </div>`
              : nothing}
            <p class="muted">
              ${card.t("write_warning")}
            </p>
            <details class="review" open>
              <summary>
                ${card.t("changed_fields", { count: card.reviewChanges().length })}
              </summary>
              ${card.reviewChanges().map((line) => html`<div>${line}</div>`)}
            </details>
            <div class="actions">
              ${card.saving
                ? html`<button @click=${card.stop}>
                    ${card.t("stop_remaining")}
                  </button>`
                : html`<button @click=${card.cancel}>${card.t("cancel")}</button
                    ><button
                      class="primary"
                      ?disabled=${!dirty(card.draft) ||
                      !!problem ||
                      card.conflict ||
                      !card.canEdit ||
                      card.draft.repair ||
                      card.submissionUnknown}
                      @click=${card.save}
                    >
                      ${card.t("save_changes")}
                    </button>`}
            </div>`
        : nothing}
      ${card.job
        ? html`<section aria-live="polite" class="alert">
            <strong
              >${card.t("job_progress", { status: card.job.status, confirmed: card.job.confirmed, total: card.job.total })}</strong
            ><progress
              max=${Math.max(1, card.job.total)}
              value=${card.job.confirmed}
            ></progress
            >${card.job.reason
              ? html`<p>${card.job.reason_message ?? card.job.reason.replaceAll("_", " ")}</p>`
              : nothing}
            <details>
              <summary>${card.t("change_results")}</summary>
              ${card.job.fields.map(
                (f) => html`<div class="status">${f.label}: ${f.status}</div>`,
              )}
            </details>
          </section>`
        : nothing}
`;
}
