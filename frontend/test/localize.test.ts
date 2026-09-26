import { expect, it } from "vitest";
import { localize } from "../src/localize";

it("falls back to English and substitutes parameters without changing wire values", () => {
  expect(localize("point", "fr-CA", { number: 3 })).toBe("Point 3");
  expect(localize("point", "fr-CA", { number: 3 }, { fr: { point: "Repère {number}" } })).toBe("Repère 3");
  expect(localize("point", "fr-CA", { number: 3 }, { fr: {} })).toBe("Point 3");
  expect(localize("day_night_option", "fr-CA", {}, { fr: { day_night_option: "Jour et nuit" } })).toBe("Jour et nuit");
});
