import { test, expect } from "@playwright/test";
for (const mode of ["Multi", "Seasonal", "Day Night"]) {
  test(`${mode} sliders precede collapsed tables and edits stay local`, async ({
    page,
  }) => {
    await page.goto(`/frontend/demo/?mode=${encodeURIComponent(mode)}`);
    await expect(page.locator(".slot-table[open]")).toHaveCount(0);
    await page.getByRole("button", { name: "Edit", exact: true }).click();
    const rows = page.locator(".row");
    await expect(rows).toHaveCount(mode === "Seasonal" ? 4 : 1);
    for (const row of await rows.all()) {
      await expect(row.locator('input[type="range"]')).toBeVisible();
      await expect(row.locator(".slot-table")).not.toHaveAttribute("open");
      expect(
        await row.evaluate((el) => {
          const slider = el.querySelector(".slider")!;
          return Boolean(
            slider.compareDocumentPosition(el.querySelector(".slot-table")!) &
              Node.DOCUMENT_POSITION_FOLLOWING,
          );
        }),
      ).toBe(true);
    }
    const row = rows.last();
    await row.locator(".handle").last().click();
    await row.locator('input[type="range"]').fill("31");
    await row.locator("summary").click();
    await expect(row.locator('input[type="number"]').last()).toHaveValue("31");
    expect(await page.evaluate(() => (window as any).calls)).toEqual([]);
    await page.screenshot({
      path: `test-results/1.2.2-${mode.replaceAll(" ", "-")}.png`,
      fullPage: true,
    });
  });
}
test("configured colours follow native temperature and both midnight pieces match", async ({
  page,
}) => {
  await page.goto("/frontend/demo/?mode=Seasonal&fahrenheit");
  await page.evaluate(() => {
    const card = (window as any).card;
    card.setConfig({
      ...card._config,
      temperature_colors: [
        { temperature: 0, color: "#ffaa00" },
        { temperature: 25, color: "#ff0000" },
      ],
    });
  });
  for (const row of await page.locator(".row").all()) {
    const pieces = row.locator(".segment.carry");
    await expect(pieces).toHaveCount(2);
    const styles = await pieces.evaluateAll((els) =>
      els.map((el) => ({
        background: getComputedStyle(el).backgroundColor,
        image: getComputedStyle(el).backgroundImage,
      })),
    );
    expect(styles[0]).toEqual(styles[1]);
    expect(styles[0].image).toContain("repeating-linear-gradient");
  }
  const colors = await page
    .locator(".segment")
    .evaluateAll((els) =>
      els.map((el) => getComputedStyle(el).backgroundColor),
    );
  expect(
    colors.every((c) => ["rgb(255, 170, 0)", "rgb(255, 0, 0)"].includes(c)),
  ).toBe(true);
});
test("visual editor changes thresholds and colours and rejects invalid configuration", async ({
  page,
}) => {
  await page.goto("/frontend/demo/");
  await page.evaluate(() => {
    const w = window as any;
    const e = document.createElement("microclimate-card-editor") as any;
    e.setConfig(w.card._config);
    e.hass = w.card.hass;
    e.addEventListener(
      "config-changed",
      (event: any) => (w.editorChange = event.detail.config),
    );
    document.querySelector("#host")!.append(e);
  });
  await page.getByText("Temperature colours", { exact: true }).click();
  await page.getByLabel("Colour 2 lower temperature °C").fill("22");
  await page.getByLabel("Colour 2 lower temperature °C").blur();
  await page.getByLabel("Colour 2 value", { exact: true }).fill("#ff0000");
  expect(
    await page.evaluate(
      () => (window as any).editorChange.temperature_colors[1],
    ),
  ).toEqual({ temperature: 22, color: "#ff0000" });
  await page.getByLabel("Colour 2 lower temperature °C").fill("0");
  await page.getByLabel("Colour 2 lower temperature °C").blur();
  await expect(page.getByRole("alert")).toContainText("unique Celsius bounds");
  expect(
    await page.evaluate(
      () => (window as any).editorChange.temperature_colors[1].temperature,
    ),
  ).toBe(22);
  await page.getByRole("button", { name: "Reset temperature colours" }).click();
  expect(
    await page.evaluate(() => (window as any).editorChange.temperature_colors),
  ).toBeUndefined();
});
