// The frontend server must be running. An alternate backend port can be used
// so this check does not interrupt a user's existing Gible backend process.
const { chromium } = require("playwright");
const { expect } = require("playwright/test");
const path = require("node:path");
const fs = require("node:fs/promises");

async function setRange(page, label, value) {
  await page.getByRole("slider", { name: label, exact: true }).evaluate((element, next) => {
    const setter = Object.getOwnPropertyDescriptor(
      window.HTMLInputElement.prototype, "value").set;
    setter.call(element, String(next));
    element.dispatchEvent(new Event("input", { bubbles: true }));
    element.dispatchEvent(new Event("change", { bubbles: true }));
  }, value);
}

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
    await expect(page.locator(".iv-category-block > span").first()).toHaveText("01 / 裁 / TD");
    await expect(page.locator(".iv-category-missed > span").first()).toHaveText("02 / 丢 / LOSE");
    await expect(page.locator(".iv-category-down > span").first()).toHaveText("03 / 宕 / SET");
    await expect(page.locator(".iv-category-wrong > span").first()).toHaveText("04 / 错 / WRONG");
    await expect(page.locator(".iv-category-block strong")).toHaveText("232", { timeout: 30000 });
    await expect(page.locator(".iv-category-missed strong")).toHaveText("264");
    await expect(page.locator(".iv-category-down strong")).toHaveText("60");
    await expect(page.locator(".iv-category-wrong strong")).toHaveText("3");

    await page.getByRole("button", { name: "Overview · 总览" }).click();
    await expect(page.locator(".iv-pager")).toContainText("Page 1 / 8");
    await expect(page.locator(".iv-case")).toHaveCount(100);
    await expect(page.locator(".iv-tag-clean").first()).toBeVisible();
    await page.getByRole("button", { name: "Next overview page" }).click();
    await expect(page.locator(".iv-pager")).toContainText("Page 2 / 8");
    await page.getByRole("button", { name: "Findings" }).click();

    await page.locator(".iv-category-wrong").click();
    await expect(page.locator(".iv-list-tools")).toContainText("3 findings · 20 N/S pairs");
    await page.getByRole("searchbox", { name: "Search scanner findings" }).fill("1431");
    await expect(page.locator(".iv-case")).toHaveCount(1);
    await page.locator(".iv-case").click();
    await expect(page.locator(".iv-pair-button")).toHaveCount(10);
    await expect(page.locator(".iv-pair-button[aria-pressed='true']")).toContainText("#1431");
    await expect(page.locator(".iv-warning-list")).toContainText("RATIO");
    await expect(page.locator(".iv-ew-strip")).toBeVisible();
    await page.screenshot({ path: path.resolve(__dirname, "../../reports/block_scans/iv-scanner-preview.png") });

    const downBefore = Number(await page.locator(".iv-category-down strong").textContent());
    await setRange(page, "SET 宕 failure", 0.7);
    const downAfter = Number(await page.locator(".iv-category-down strong").textContent());
    if (!(downAfter < downBefore)) {
      throw new Error(`raising SET threshold did not reduce findings: ${downBefore} -> ${downAfter}`);
    }
    await page.getByRole("button", { name: "Reset" }).click();
    await expect(page.locator(".iv-category-down strong")).toHaveText(String(downBefore));

    await page.locator(".iv-category-block").click();
    await page.locator('input[aria-label="Search scanner findings"]').fill("");
    await page.locator(".iv-case").first().click();
    await expect(page.locator(".iv-block-diagnostic")).toBeVisible();
    await expect(page.locator(".iv-call-td")).toBeVisible();

    await page.locator(".iv-fields input").nth(0).fill("10");
    await page.locator(".iv-fields input").nth(1).fill("10");
    await page.locator(".iv-fields input").nth(2).fill("1");
    await page.getByRole("button", { name: "Start scan" }).click();
    await expect(page.locator(".iv-progress")).toBeVisible();
    await expect(page.locator(".iv-progress-completed")).toBeVisible({ timeout: 240000 });
    await expect(page.locator(".iv-progress-completed")).toContainText("23/23 pairs");
    const run = await page.evaluate(async (port) => {
      const response = await fetch(`http://127.0.0.1:${port || 8765}/api/scanner/runs/current`);
      return (await response.json()).run;
    }, backendPort);
    if (run?.report_id && /^iv-scan-[\w.-]+\.json$/.test(run.report_id)) {
      const root = path.resolve(__dirname, "../../reports/block_scans");
      await fs.unlink(path.join(root, run.report_id)).catch(() => {});
      await fs.unlink(path.join(root, run.report_id.replace(/\.json$/, ".html"))).catch(() => {});
    }
    if (errors.length) throw new Error(errors.join("\n"));
    console.log("PASS: IV Scanner navigation, four findings, cell/pair filtering, pair detail, and background scan");
  } finally {
    await browser.close();
  }
})().catch((error) => { console.error(error); process.exitCode = 1; });
