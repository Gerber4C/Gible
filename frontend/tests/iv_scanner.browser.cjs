// The frontend server must be running. An alternate backend port can be used
// so this check does not interrupt a user's existing Gible backend process.
const { chromium } = require("playwright");
const { expect } = require("playwright/test");
const path = require("node:path");
const fs = require("node:fs/promises");

(async () => {
  const browser = await chromium.launch({ headless: true });
  const errors = [];
  try {
    const page = await browser.newPage({ viewport: { width: 1500, height: 1000 } });
    page.on("pageerror", (error) => errors.push(error.message));
    const backendPort = process.env.GIBLE_TEST_BACKEND_PORT;
    if (backendPort) {
      await page.route("http://127.0.0.1:8765/api/**", async (route) => {
        const url = route.request().url().replace(":8765/", `:${backendPort}/`);
        const response = await route.fetch({ url });
        await route.fulfill({ response });
      });
    }
    await page.goto("http://127.0.0.1:5173/");
    await page.waitForLoadState("networkidle");
    await page.getByRole("button", { name: "IV Scanner" }).click();
    await expect(page.getByRole("heading", { name: "IV Scanner" })).toBeVisible();
    await expect(page.locator(".iv-category-block > span").first()).toHaveText("01 / 卡 / BLOCKED");
    await expect(page.locator(".iv-category-missed > span").first()).toHaveText("02 / 丢 / LOSE");
    await expect(page.locator(".iv-category-down > span").first()).toHaveText("03 / 宕 / SET");
    await expect(page.locator(".iv-category-wrong > span").first()).toHaveText("04 / 错 / WRONG");
    await expect(page.locator(".iv-category-block strong")).toHaveText("304");
    await expect(page.locator(".iv-category-missed strong")).toHaveText("106");
    await expect(page.locator(".iv-category-down strong")).toHaveText("66");
    await expect(page.locator(".iv-category-wrong strong")).toHaveText("7");
    await page.locator(".iv-category-wrong").click();
    await expect(page.locator(".iv-list-tools")).toContainText("7 findings");
    await page.getByRole("searchbox", { name: "Search scanner findings" }).fill("169");
    await expect(page.locator(".iv-case")).toHaveCount(1);
    await page.locator(".iv-case").click();
    await expect(page.locator(".iv-detail-heading")).toContainText("DEAL #169");
    await expect(page.locator(".iv-ns-matrix")).toBeVisible();
    await expect(page.locator(".iv-auction-row")).toHaveCount(2);
    await page.screenshot({ path: path.resolve(__dirname, "../../reports/block_scans/iv-scanner-preview.png") });

    await page.locator(".iv-category-block").click();
    await page.locator('input[aria-label="Search scanner findings"]').fill("");
    await page.locator(".iv-case").first().click();
    await expect(page.locator(".iv-ns-matrix")).toContainText("BLOCK 卡");

    await page.locator(".iv-fields input").nth(0).fill("10");
    await page.locator(".iv-fields input").nth(1).fill("10");
    await page.locator(".iv-fields input").nth(2).fill("1");
    await page.getByRole("button", { name: "Start scan" }).click();
    await expect(page.locator(".iv-progress")).toBeVisible();
    await expect(page.locator(".iv-progress-completed")).toBeVisible({ timeout: 120000 });
    await expect(page.locator(".iv-progress-completed")).toContainText("3/3 pairs");
    const run = await page.evaluate(async (port) => {
      const response = await fetch(`http://127.0.0.1:${port || 8765}/api/scanner/runs/current`);
      return (await response.json()).run;
    }, backendPort);
    if (run?.report_id && /^iv-scan-[\w.-]+\.json$/.test(run.report_id)) {
      const root = path.resolve(__dirname, "../../reports/block_scans");
      await fs.unlink(path.join(root, run.report_id));
      await fs.unlink(path.join(root, run.report_id.replace(/\.json$/, ".html")));
    }
    if (errors.length) throw new Error(errors.join("\n"));
    console.log("PASS: IV Scanner navigation, four findings, filtering, deal detail, and background scan");
  } finally {
    await browser.close();
  }
})().catch((error) => { console.error(error); process.exitCode = 1; });
