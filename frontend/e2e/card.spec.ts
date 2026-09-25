import { test, expect } from "@playwright/test";
test.beforeEach(async ({ page }) => {
  await page.route("**/*", (route) =>
    new URL(route.request().url()).hostname === "127.0.0.1"
      ? route.continue()
      : route.abort(),
  );
});
test("draft changes and Cancel never call save", async ({ page }) => {
  await page.goto("/frontend/demo/");
  await page.getByRole("button", { name: "Edit", exact: true }).click();
  for (const summary of await page.locator(".slot-table summary").all())
    await summary.click();
  await page
    .getByRole("spinbutton", { name: "Multi Point 1 target °C" })
    .fill("30");
  await page
    .getByRole("spinbutton", { name: "Multi Point 1 target °C" })
    .blur();
  await page.getByRole("button", { name: "Cancel", exact: true }).click();
  expect(await page.evaluate(() => (window as any).calls)).toEqual([]);
});
test("two time changes produce one final save", async ({ page }) => {
  await page.goto("/frontend/demo/?mode=Day%20Night");
  await page.getByRole("button", { name: "Edit", exact: true }).click();
  for (const summary of await page.locator(".slot-table summary").all())
    await summary.click();
  const time = page.getByLabel("Day & Night Day start", { exact: true });
  await time.fill("08:00:00");
  await time.blur();
  await time.fill("08:45:17");
  await time.blur();
  await page.getByRole("button", { name: "Save changes" }).click();
  const calls = await page.evaluate(() => (window as any).calls);
  expect(calls).toHaveLength(1);
  expect(calls[0].patch.schedule.points[0].seconds).toBe(31517);
  await expect(
    page.getByRole("button", { name: "Stop remaining changes" }),
  ).toBeVisible();
});
test("delete middle point compacts draft; add enforces capacity", async ({
  page,
}) => {
  await page.goto("/frontend/demo/?count=8");
  await page.getByRole("button", { name: "Edit", exact: true }).click();
  for (const summary of await page.locator(".slot-table summary").all())
    await summary.click();
  await expect(
    page.getByRole("button", { name: "Add point", exact: true }),
  ).toBeDisabled();
  await page.getByRole("button", { name: "Point 3", exact: true }).click();
  await page.getByRole("button", { name: "Remove selected" }).click();
  await expect(
    page.getByRole("button", { name: "Add point", exact: true }),
  ).toBeEnabled();
  expect(
    await page.evaluate(() => (window as any).card.draft.points.length),
  ).toBe(7);
});
test("seasonal has four rows and root owns date editing", async ({ page }) => {
  await page.goto("/frontend/demo/?mode=Seasonal&dark");
  await expect(page.getByText("Season 4", { exact: true })).toBeVisible();
  await expect(page.getByText("Starts 01/07", { exact: true })).toBeVisible();
  await page.goto("/frontend/demo/?kind=controller");
  await page.getByRole("button", { name: "Edit", exact: true }).click();
  await expect(page.getByLabel("Season 1 start")).toBeVisible();
});
test("readonly, Blue restrictions and minimum", async ({ page }) => {
  await page.goto("/frontend/demo/?readonly");
  await expect(
    page.getByRole("button", { name: "Edit", exact: true }),
  ).toHaveCount(0);
  await page.goto("/frontend/demo/?channel=Blue&count=2");
  await page.getByRole("button", { name: "Edit", exact: true }).click();
  await expect(
    page.getByRole("button", { name: "Remove selected" }),
  ).toBeDisabled();
  await expect(page.getByText("Ramp time", { exact: true })).toHaveCount(0);
});
for (const width of [320, 390, 768, 1280])
  for (const dark of [false, true])
    test(`layout ${width} ${dark ? "dark" : "light"}`, async ({ page }) => {
      await page.setViewportSize({ width, height: 1400 });
      await page.goto(`/frontend/demo/?mode=Seasonal${dark ? "&dark" : ""}`);
      await expect(
        page.getByRole("button", { name: "Edit", exact: true }),
      ).toBeVisible();
      expect(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= innerWidth,
        ),
      ).toBe(true);
      await page.screenshot({
        path: `test-results/seasonal-${width}-${dark ? "dark" : "light"}.png`,
        fullPage: true,
      });
    });

test("keyboard and pointer edits remain local, preserve untouched seconds", async ({
  page,
}) => {
  await page.goto("/frontend/demo/?mode=Day%20Night");
  await page.getByRole("button", { name: "Edit", exact: true }).click();
  const boundary = page.getByRole("button", {
    name: "Day & Night 07:00:00 boundary",
    exact: true,
  });
  await boundary.focus();
  await page.keyboard.press("ArrowRight");
  await expect(
    page.getByLabel("Day & Night Day start", { exact: true }),
  ).toHaveValue("07:01:00");
  const moved = page.getByRole("button", {
    name: "Day & Night 07:01:00 boundary",
    exact: true,
  });
  const box = await moved.boundingBox();
  await page.mouse.move(box!.x + 12, box!.y + 20);
  await page.mouse.down();
  await page.mouse.move(box!.x + 60, box!.y + 20, { steps: 8 });
  await page.mouse.up();
  expect(await page.evaluate(() => (window as any).calls)).toEqual([]);
  expect(
    await page
      .getByLabel("Day & Night Day start", { exact: true })
      .inputValue(),
  ).not.toBe("07:01:00");
});
test("polling never replaces draft; conflict and explicit review", async ({
  page,
}) => {
  await page.goto("/frontend/demo/");
  await page.getByRole("button", { name: "Edit", exact: true }).click();
  for (const summary of await page.locator(".slot-table summary").all())
    await summary.click();
  const target = page.getByRole("spinbutton", {
    name: "Multi Point 1 target °C",
  });
  await target.fill("35");
  await target.blur();
  await page.evaluate(() => {
    const w = window as any;
    w.view.revision = "external";
    w.view.fields.find((f: any) => f.key === "Yellow_period_1_setpoint").value =
      12;
    w.callbacks["microclimate_integration/card/subscribe"](
      structuredClone(w.view),
    );
  });
  await expect(target).toHaveValue("35");
  await expect(
    page.getByRole("button", { name: "Save changes" }),
  ).toBeDisabled();
  await page.getByRole("button", { name: "Refresh and review draft" }).click();
  await expect(
    page.getByRole("button", { name: "Save changes" }),
  ).toBeEnabled();
});
test("partial failure keeps draft and reports confirmed changes", async ({
  page,
}) => {
  await page.goto("/frontend/demo/");
  await page.getByRole("button", { name: "Edit", exact: true }).click();
  await page.getByRole("button", { name: "Remove selected" }).click();
  await page.getByRole("button", { name: "Save changes" }).click();
  await page.evaluate(() => {
    const w = window as any;
    w.callbacks["microclimate_integration/card/operation"]({
      operation_id: "job",
      sequence: 2,
      status: "partial",
      phase: "Finished",
      confirmed: 1,
      total: 4,
      fields: [
        { key: "x", label: "Point 1 target", status: "confirmed" },
        { key: "y", label: "Point 1 start", status: "failed" },
      ],
      reason: "rejected",
    });
  });
  await expect(
    page.getByText("partial · 1/4 confirmed", { exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Cancel", exact: true }),
  ).toBeVisible();
  expect(
    await page.evaluate(
      () =>
        (window as any).calls.filter((c: any) => c.type.endsWith("/save"))
          .length,
    ),
  ).toBe(1);
});
test("mode changes never reinterpret the draft", async ({ page }) => {
  await page.goto("/frontend/demo/");
  await page.getByRole("button", { name: "Edit", exact: true }).click();
  await page.getByLabel("Control mode", { exact: true }).selectOption("fixed");
  await page.getByRole("button", { name: "Save changes" }).click();
  const calls = await page.evaluate(() => (window as any).calls);
  expect(calls[0].patch).toEqual({
    kind: "mode",
    fields: { Yellow_control_pin: "fixed" },
  });
});
test("schema mismatch and offline prevent edits", async ({ page }) => {
  await page.goto("/frontend/demo/");
  await page.evaluate(() => {
    const w = window as any;
    w.view.schema_version = 2;
    w.callbacks["microclimate_integration/card/subscribe"](w.view);
  });
  await expect(
    page.getByRole("button", { name: "Edit", exact: true }),
  ).toHaveCount(0);
  await expect(page.getByText(/version mismatch/)).toBeVisible();
});
for (const scenario of [
  "Multi",
  "Day Night",
  "Seasonal",
  "Constant",
  "Periodic",
])
  test(`screenshot ${scenario} edit`, async ({ page }) => {
    await page.goto(
      `/frontend/demo/?mode=${encodeURIComponent(scenario)}&channel=Blue&dark`,
    );
    await page.getByRole("button", { name: "Edit", exact: true }).click();
    await page.screenshot({
      path: `test-results/${scenario.replaceAll(" ", "-")}-edit.png`,
      fullPage: true,
    });
  });

test("lost acknowledgement lookup never resubmits save", async ({ page }) => {
  await page.goto("/frontend/demo/");
  await page.evaluate(() => {
    const w = window as any;
    const original = w.card.hass.callWS;
    w.card.hass.callWS = async (msg: any) => {
      if (msg.type.endsWith("/save")) {
        await original(msg);
        throw new Error("Connection lost");
      }
      return await original(msg);
    };
  });
  await page.getByRole("button", { name: "Edit", exact: true }).click();
  await page.getByRole("button", { name: "Remove selected" }).click();
  await page.getByRole("button", { name: "Save changes" }).click();
  await expect(
    page.getByRole("button", { name: "Check request status" }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Save changes" }),
  ).toBeDisabled();
  await page.getByRole("button", { name: "Check request status" }).click();
  expect(
    await page.evaluate(
      () =>
        (window as any).calls.filter((m: any) => m.type.endsWith("/save"))
          .length,
    ),
  ).toBe(1);
});
test("dirty device switch provides Stay and Discard", async ({ page }) => {
  await page.goto("/frontend/demo/");
  await page.getByRole("button", { name: "Edit", exact: true }).click();
  await page.getByRole("button", { name: "Remove selected" }).click();
  await page.evaluate(() =>
    (window as any).card.setConfig({
      type: "custom:microclimate-channel-card",
      device_id: "different",
    }),
  );
  await expect(
    page.getByRole("dialog", { name: "Unsaved schedule changes" }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Stay", exact: true }).click();
  expect(
    await page.evaluate(() => (window as any).card._config.device_id),
  ).toBe("channel");
  expect(await page.evaluate(() => (window as any).calls.length)).toBe(0);
});
for (const count of [0, 1, 2, 8])
  test(`multi ${count} screenshot and validation`, async ({ page }) => {
    await page.goto(`/frontend/demo/?count=${count}&dark`);
    await page.getByRole("button", { name: "Edit", exact: true }).click();
    if (count < 2) {
      await expect(
        page.getByText("Unknown or incomplete boundaries", { exact: true }),
      ).toBeVisible();
      await expect(
        page.getByRole("button", { name: "Review/rebuild point list" }),
      ).toBeVisible();
      await expect(
        page.getByRole("button", { name: "Save changes" }),
      ).toBeDisabled();
    }
    await page.screenshot({
      path: `test-results/multi-${count}.png`,
      fullPage: true,
    });
  });
test("root dates, Fahrenheit and offline screenshots", async ({ page }) => {
  await page.goto("/frontend/demo/?kind=controller&dark");
  await page.getByRole("button", { name: "Edit", exact: true }).click();
  for (const summary of await page.locator(".slot-table summary").all())
    await summary.click();
  await page.getByLabel("Season 1 start").fill("29/02");
  await page.getByLabel("Season 1 start").blur();
  await expect(
    page.getByRole("button", { name: "Save changes" }),
  ).toBeDisabled();
  await page.screenshot({
    path: "test-results/root-invalid-date.png",
    fullPage: true,
  });
  await page.goto("/frontend/demo/?fahrenheit");
  await page.getByRole("button", { name: "Edit", exact: true }).click();
  for (const summary of await page.locator(".slot-table summary").all())
    await summary.click();
  await expect(
    page.getByRole("spinbutton", { name: "Multi Point 1 target °F" }),
  ).toHaveValue("80.6");
  await page.screenshot({
    path: "test-results/fahrenheit-edit.png",
    fullPage: true,
  });
  await page.getByRole("button", { name: "Cancel", exact: true }).click();
  await page.evaluate(() => {
    const w = window as any;
    w.view.online = false;
    w.callbacks["microclimate_integration/card/subscribe"](
      structuredClone(w.view),
    );
  });
  await expect(
    page.getByRole("button", { name: "Edit", exact: true }),
  ).toHaveCount(0);
  await page.screenshot({ path: "test-results/offline.png", fullPage: true });
});

test("mode selectors initialize to the observed values", async ({ page }) => {
  await page.goto("/frontend/demo/?mode=Multi");
  await page.getByRole("button", { name: "Edit", exact: true }).click();
  await expect(page.getByLabel("Control mode", { exact: true })).toHaveValue(
    "heating",
  );
  await expect(page.getByLabel("Timing mode", { exact: true })).toHaveValue(
    "Multi",
  );
  await expect(page.getByLabel("Output type", { exact: true })).toHaveValue(
    "pulse",
  );
});

test("visual configuration editor resolves device and emits config changes", async ({
  page,
}) => {
  await page.goto("/frontend/demo/");
  await page.evaluate(() => {
    const w = window as any;
    const editor = document.createElement("microclimate-card-editor") as any;
    editor.setConfig({
      type: "custom:microclimate-channel-card",
      device_id: "channel",
    });
    editor.addEventListener(
      "config-changed",
      (event: any) => (w.editorChange = event.detail.config),
    );
    editor.hass = w.card.hass;
    document.querySelector("#host")!.append(editor);
  });
  await expect(page.getByLabel("Device", { exact: true })).toHaveValue(
    "channel",
  );
  await page.getByLabel("Title", { exact: true }).fill("My vivarium");
  await page.getByLabel("Title", { exact: true }).blur();
  expect(await page.evaluate(() => (window as any).editorChange.title)).toBe(
    "My vivarium",
  );
  await page.getByLabel("Always read only", { exact: true }).check();
  expect(
    await page.evaluate(() => (window as any).editorChange.read_only),
  ).toBe(true);
});

test("read-only points keep their numbered identity when selected", async ({
  page,
}) => {
  await page.goto("/frontend/demo/");
  await page.locator(".slot-table summary").click();
  await expect(
    page.getByRole("button", { name: "Point 1", exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Point 4", exact: true }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Point 3", exact: true }).click();
  await expect(
    page.getByRole("button", { name: "Multi 07:00:00 boundary", exact: true }),
  ).toHaveAttribute("aria-pressed", "true");
  await expect(
    page.getByRole("button", { name: "Point 0", exact: true }),
  ).toHaveCount(0);
  expect(await page.evaluate(() => (window as any).calls)).toEqual([]);
});
