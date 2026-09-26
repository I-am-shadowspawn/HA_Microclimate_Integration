import { css } from "lit";
export const cardStyles = css`
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
