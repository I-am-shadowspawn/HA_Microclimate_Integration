import { html, nothing } from "lit";
import { live } from "lit/directives/live.js";
import { repeat } from "lit/directives/repeat.js";
import type { Point } from "../types";
import type { MicroclimateCard } from "../card";
import { clock, parseClock, displayValue, nativeValue, segments, pointError } from "../draft";
import { targetColors } from "../colors";
export function scheduleRow(card: MicroclimateCard, points: Point[], label: string, date?: string | null) {
    const timelineSegments =
      card.mode === "Multi" && card.working && pointError(card.working)
        ? []
        : segments(points);
    const f = card.fieldFor(1);
    const selected =
      points.find((p) => p.draft_id === card.selected) ?? points[0];
    return html`<section class="row">
      <div class="row-title">
        <span>${label}</span>${date !== undefined
          ? html`<small>${card.t("starts", { date: date ?? card.t("unknown") })}</small>`
          : nothing}
      </div>
      <div
        class="timeline"
        aria-label=${card.t("timeline_label", { label })}
      >
        ${timelineSegments.map(
          (s) =>
            html`<div
              class="segment ${s.carry ? "carry" : ""}"
              style=${`left:${s.start / 864}%;width:${(s.end - s.start) / 864}%;${targetColors(s.point.target_native, f?.unit, card._config?.temperature_colors)}`}
              title=${`${s.carry ? card.t("carry") : ""}${clock(s.start)}–${clock(s.end === 86400 ? 0 : s.end)} · ${card.format(s.point.target_native, f)}`}
            >
              <span
                >${s.end - s.start > 3600
                  ? card.format(s.point.target_native, f)
                  : ""}</span
              >
            </div>`,
        )}
        ${timelineSegments.length === 0
          ? html`<div class="empty muted">
              ${card.t("unknown_boundaries")}
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
                  data-point-id=${p.draft_id}
                  aria-label=${card.t("boundary_label", { label: card.mode === "Multi" ? card.t("point", { number: points.indexOf(p) + 1 }) : label + " " + (points.indexOf(p) % 2 === 0 ? card.t("day") : card.t("night")), time: clock(p.seconds) })}
                  aria-pressed=${selected?.draft_id === p.draft_id}
                  title=${clock(p.seconds)}
                  @click=${() => (card.selected = p.draft_id)}
                  @pointerdown=${(e: PointerEvent) => card.pointerDown(e, p)}
                  @pointermove=${card.pointerMove}
                  @pointerup=${card.pointerUp}
                  @pointercancel=${card.pointerUp}
                  @lostpointercapture=${card.pointerUp}
                  @keydown=${(e: KeyboardEvent) => card.key(e, p)}
                ></button>`,
        )}
      </div>
      <div class="axis">
        <span>00</span><span>04</span><span>08</span><span>12</span
        ><span>16</span><span>20</span><span>24</span>
      </div>
      ${card.draft && selected
        ? html`<label class="field slider">
            ${card.mode === "Multi"
              ? card.t("point", { number: points.indexOf(selected) + 1 })
              : points.indexOf(selected) % 2 === 0
                ? card.t("day")
                : card.t("night")}
            ${card.t("point_target_summary")} · ${clock(selected.seconds)} ·
            ${card.format(selected.target_native, card.fieldFor(1))}<input
              aria-label=${card.t("selected_target_label", { label })}
              type="range"
              min=${displayValue(
                0,
                card.fieldFor(1)?.unit ?? null,
                card.fahrenheit,
              )}
              max=${displayValue(
                100,
                card.fieldFor(1)?.unit ?? null,
                card.fahrenheit,
              )}
              step="0.5"
              .value=${String(
                displayValue(
                  selected.target_native ?? 0,
                  card.fieldFor(1)?.unit ?? null,
                  card.fahrenheit,
                ),
              )}
              ?disabled=${card.saving || !card.allScheduleWritable}
              @input=${(e: Event) =>
                card.updatePoint(selected.draft_id, {
                  target_native: nativeValue(
                    Number((e.target as HTMLInputElement).value),
                    card.fieldFor(1)?.unit ?? null,
                    card.fahrenheit,
                  ),
                })}
          /></label>`
        : nothing}
      <details class="slot-table">
        <summary>${card.t("slot_table", { label })}</summary>
        <div class="point-list">
          ${repeat(
            points,
            (p) => p.draft_id,
            (p, i) => {
              const prefix =
                card.mode === "Multi"
                  ? card.t("point", { number: card.working!.points.indexOf(p) + 1 })
                  : i % 2 === 0
                    ? card.t("day")
                    : card.t("night");
              return html`<div
                class="point ${card.selected === p.draft_id ? "selected" : ""}"
              >
                <button @click=${() => (card.selected = p.draft_id)}>
                  ${prefix}</button
                >${card.draft
                  ? html`<input
                        aria-label=${card.t("point_start", { label, point: prefix })}
                        type="time"
                        step="1"
                        .value=${live(clock(p.seconds))}
                        ?disabled=${card.saving || !card.allScheduleWritable}
                        @input=${(e: Event) =>
                          card.updatePoint(
                            p.draft_id,
                            {
                              seconds: parseClock(
                                (e.target as HTMLInputElement).value,
                              ),
                            },
                            false,
                          )}
                        @change=${() => card.updatePoint(p.draft_id, {})}
                      /><input
                        aria-label=${card.t("point_target", { label, point: prefix, unit: card.unit(f) })}
                        type="number"
                        min=${displayValue(0, f?.unit ?? null, card.fahrenheit)}
                        max=${displayValue(
                          100,
                          f?.unit ?? null,
                          card.fahrenheit,
                        )}
                        step="any"
                        .value=${live(
                          p.target_native === null
                            ? ""
                            : String(
                                displayValue(
                                  p.target_native,
                                  f?.unit ?? null,
                                  card.fahrenheit,
                                ),
                              ),
                        )}
                        ?disabled=${card.saving || !card.allScheduleWritable}
                        @input=${(e: Event) => {
                          const v = (e.target as HTMLInputElement).value;
                          card.updatePoint(p.draft_id, {
                            target_native:
                              v === ""
                                ? null
                                : nativeValue(
                                    Number(v),
                                    f?.unit ?? null,
                                    card.fahrenheit,
                                  ),
                          });
                        }}
                      />`
                  : html`<span>${clock(p.seconds) || card.t("unknown")}</span
                      ><span>${card.format(p.target_native, f)}</span>`}
              </div>`;
            },
          )}
        </div>
      </details>
    </section>`;
}
