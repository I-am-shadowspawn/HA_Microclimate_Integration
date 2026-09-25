import { test, expect } from "@playwright/test";

test("season-date typing survives HA updates before blur", async ({ page }) => {
  await page.goto("/frontend/demo/?kind=controller");
  await page.getByRole("button", { name: "Edit", exact: true }).click();
  const input = page.getByLabel("Season 3 start", { exact: true });
  await input.focus();
  await input.press("ControlOrMeta+A");
  let typed = "";
  for (const character of "15/06") {
    await input.pressSequentially(character);
    typed += character;
    await page.evaluate(async () => {
      const card = (window as any).card;
      card.hass = { ...card.hass };
      await card.updateComplete;
    });
    await expect(input).toHaveValue(typed);
  }
  await expect(
    page.getByRole("button", { name: "Save changes", exact: true }),
  ).toBeEnabled();
  expect(await page.evaluate(() => (window as any).calls)).toEqual([]);
  await page.getByRole("button", { name: "Cancel", exact: true }).click();
  expect(await page.evaluate(() => (window as any).calls)).toEqual([]);
});

test("channel renders and saves on an insecure HTTP origin", async ({
  page,
}) => {
  await page.route("http://microclimate.test/**", async (route) => {
    const url = new URL(route.request().url());
    const response = await page.request.get(
      `http://127.0.0.1:8767${url.pathname}${url.search}`,
    );
    await route.fulfill({ response });
  });
  await page.goto("http://microclimate.test/frontend/demo/");
  expect(await page.evaluate(() => window.isSecureContext)).toBe(false);
  expect(await page.evaluate(() => typeof crypto.randomUUID)).toBe("undefined");
  await page.locator(".slot-table summary").click();
  await expect(
    page.getByRole("button", { name: "Point 1", exact: true }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Edit", exact: true }).click();
  await page.getByRole("button", { name: "Add point", exact: true }).click();
  await page.getByRole("button", { name: "Save changes", exact: true }).click();
  const calls = await page.evaluate(() => (window as any).calls);
  expect(calls).toHaveLength(1);
  expect(calls[0].request_id).toMatch(
    /^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/,
  );
});

test("schedule numeric input survives updates without blur or dispatch", async ({
  page,
}) => {
  await page.goto("/frontend/demo/");
  await page.getByRole("button", { name: "Edit", exact: true }).click();
  for (const summary of await page.locator(".slot-table summary").all())
    await summary.click();
  const input = page.getByRole("spinbutton", {
    name: "Multi Point 1 target °C",
    exact: true,
  });
  await input.focus();
  await input.press("ControlOrMeta+A");
  let typed = "";
  for (const c of "36") {
    await input.pressSequentially(c);
    typed += c;
    await page.evaluate(async () => {
      const card = (window as any).card;
      card.hass = { ...card.hass };
      await card.updateComplete;
    });
    await expect(input).toHaveValue(typed);
  }
  expect(await page.evaluate(() => (window as any).calls)).toEqual([]);
});

test("Multi time input retains focus across a neighbouring boundary until commit", async ({
  page,
}) => {
  await page.goto("/frontend/demo/");
  await page.getByRole("button", { name: "Edit", exact: true }).click();
  for (const summary of await page.locator(".slot-table summary").all())
    await summary.click();
  const input = page.getByLabel("Multi Point 1 start", { exact: true });
  await input.focus();
  await input.evaluate((el) => {
    const input = el as HTMLInputElement;
    input.value = "05:00:00";
    input.dispatchEvent(new Event("input", { bubbles: true, composed: true }));
  });
  await page.evaluate(async () => {
    const card = (window as any).card;
    card.hass = { ...card.hass };
    await card.updateComplete;
  });
  await expect(input).toBeFocused();
  await expect(input).toHaveValue("05:00:00");
  await input.dispatchEvent("change");
  await expect(
    page.getByLabel("Multi Point 2 start", { exact: true }),
  ).toHaveValue("05:00:00");
  expect(await page.evaluate(() => (window as any).calls)).toEqual([]);
});

test("controller can save a valid date over HTTP; invalid annual order stays blocked", async ({
  page,
}) => {
  await page.route("http://microclimate.test/**", async (route) => {
    const url = new URL(route.request().url());
    await route.fulfill({
      response: await page.request.get(
        `http://127.0.0.1:8767${url.pathname}${url.search}`,
      ),
    });
  });
  await page.goto("http://microclimate.test/frontend/demo/?kind=controller");
  await page.getByRole("button", { name: "Edit", exact: true }).click();
  const input = page.getByLabel("Season 3 start", { exact: true });
  await input.fill("01/12");
  await expect(
    page.getByRole("button", { name: "Save changes", exact: true }),
  ).toBeDisabled();
  await expect(
    page.getByText(/Seasons must follow one annual cycle/),
  ).toBeVisible();
  await input.fill("15/06");
  await page.getByRole("button", { name: "Save changes", exact: true }).click();
  const calls = await page.evaluate(() => (window as any).calls);
  expect(calls).toHaveLength(1);
  expect(calls[0].patch).toEqual({
    kind: "season_dates",
    fields: { season_3_start_pin: "15/06" },
  });
});
