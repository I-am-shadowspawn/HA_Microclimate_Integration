import { describe, expect, it } from "vitest";
import { modelIconUrl } from "../src/model-icon";

describe("controller model artwork", () => {
  it.each([
    ["Evo Connect", "evo-connect.png"],
    ["Evo Connect 2", "evo-connect-ii.png"],
    ["Evo Connect 3", "evo-connect-iii.png"],
  ])("selects the bundled icon for %s", (model, file) => {
    expect(modelIconUrl(model)).toBe(`/microclimate_integration/${file}`);
  });

  it("does not guess an icon for an unknown model", () => {
    expect(modelIconUrl("unverified model")).toBeNull();
  });
});
