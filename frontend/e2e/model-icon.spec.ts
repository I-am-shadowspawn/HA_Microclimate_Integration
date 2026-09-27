import { expect, test } from "@playwright/test";

for (const [model, file] of [
  ["Evo Connect", "evo-connect.png"],
  ["Evo Connect 2", "evo-connect-ii.png"],
  ["Evo Connect 3", "evo-connect-iii.png"],
]) {
  test(`card displays ${model} artwork`, async ({ page }) => {
    await page.goto(`/frontend/demo/?model=${encodeURIComponent(model)}`);
    const image = page.locator("microclimate-channel-card").locator(".model-icon");
    await expect(image).toHaveAttribute("src", `/microclimate_integration/${file}`);
    await expect(image).toHaveAttribute("alt", model);
    await expect.poll(() => image.evaluate((element: HTMLImageElement) => element.naturalWidth)).toBeGreaterThan(0);
  });
}

test("controller card displays its model artwork", async ({ page }) => {
  await page.goto("/frontend/demo/?kind=controller&model=Evo%20Connect%202");
  const image = page.locator("microclimate-controller-card .model-icon");
  await expect(image).toHaveAttribute("src", "/microclimate_integration/evo-connect-ii.png");
  await expect.poll(() => image.evaluate((element: HTMLImageElement) => element.naturalWidth)).toBeGreaterThan(0);
});
