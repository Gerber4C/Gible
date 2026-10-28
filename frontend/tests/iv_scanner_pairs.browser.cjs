// Deterministic IV Scanner check against a split-cell fixture. Only the
// frontend dev server is required; every API call is fulfilled locally.
const { chromium } = require("playwright");
const { expect } = require("playwright/test");
const path = require("node:path");
const fs = require("node:fs/promises");

const FIXTURE_PATH = path.resolve(__dirname, "fixtures/iv_scanner_grouped_report.json");
const REPORT_ID = "iv-scanner-fixture-pairs.json";

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
  const fixture = JSON.parse(await fs.readFile(FIXTURE_PATH, "utf8"));
  const browser = await chromium.launch({ headless: true });
  const errors = [];
  try {
    const page = await browser.newPage({ viewport: { width: 1500, height: 1000 } });
    page.on("pageerror", (error) => errors.push(error.message));
    await page.route("http://127.0.0.1:8765/**", async (route) => {
      const url = new URL(route.request().url());
      const respond = (body) => route.fulfill({ json: body });
      if (url.pathname === "/api/profiles") {
        return respond({ profiles: [{ id: "daqiush_2over1", name: "Daqiush 2/1", version: "0.1.0" }] });
      }
      if (url.pathname === "/api/profiles/daqiush_2over1/files") return respond({ files: [] });
      if (url.pathname === "/api/scanner/reports") {
        return respond({ reports: [{
          id: REPORT_ID, profile: { id: "daqiush_2over1" }, seed: 23,
          summary: fixture.summary, counts: fixture.counts, budget: fixture.budget,
          modified_at: "2026-10-27T00:00:00+00:00",
        }] });
      }
      if (url.pathname === `/api/scanner/reports/${REPORT_ID}`) return respond(fixture);
      if (url.pathname === "/api/scanner/runs/current") return respond({ run: null });
      return route.fulfill({ status: 404, json: { error: "not_found" } });
    });

    await page.goto("http://127.0.0.1:5173/");
    await page.waitForLoadState("networkidle");
    await page.getByRole("button", { name: "IV Scanner" }).click();
    await expect(page.getByRole("heading", { name: "IV Scanner" })).toBeVisible();

    await expect(page.locator(".iv-category-block strong")).toHaveText("1");
    await expect(page.locator(".iv-category-missed strong")).toHaveText("2");
    await expect(page.locator(".iv-category-down strong")).toHaveText("1");
    await expect(page.locator(".iv-category-wrong strong")).toHaveText("1");
    await expect(page.locator(".iv-list-tools")).toContainText("5 findings · 6 N/S pairs");
    await expect(page.locator(".iv-case")).toHaveCount(5);

    // Overview lists every cell·process group, including clean ones.
    await page.getByRole("button", { name: "Overview · 总览" }).click();
    await expect(page.locator(".iv-list-tools")).toContainText("all 11 cell·process groups · page 1/1");
    await expect(page.locator(".iv-case")).toHaveCount(11);
    await expect(page.locator(".iv-tag-clean").first()).toBeVisible();
    await expect(page.locator(".iv-pager")).toContainText("Page 1 / 1");
    await page.getByRole("button", { name: "Findings" }).click();
    await expect(page.locator(".iv-case")).toHaveCount(5);

    // First split cell: single-pair WRONG process.
    await page.locator(".iv-case").nth(0).click();
    await expect(page.locator(".iv-pair-button")).toHaveCount(1);
    await expect(page.locator(".iv-pair-button[aria-pressed='true']")).toContainText("#2");
    await expect(page.locator(".iv-case.selected .iv-tag-wrong")).toBeVisible();
    await expect(page.locator(".iv-warning-list")).toContainText("RATIO");
    await expect(page.locator(".iv-ew-outcome").first()).toHaveText(/MAKE|SET/);

    // Second split cell: a different process with SET and a LOSE marker.
    const firstHands = await page.locator(".iv-hands").textContent();
    const firstAuction = await page.locator(".iv-auction-rows").textContent();
    await page.locator(".iv-case").nth(1).click();
    await expect(page.locator(".iv-pair-button")).toHaveCount(1);
    await expect(page.locator(".iv-pair-button[aria-pressed='true']")).toContainText("#3");
    await expect(page.locator(".iv-case.selected .iv-tag-down")).toBeVisible();
    await expect(page.locator(".iv-warning-list")).toContainText("SET ·");
    await expect(page.locator(".iv-ew-lose").first()).toHaveAttribute("title", "Missed small slam");
    await expect(page.locator(".iv-hands")).not.toHaveText(firstHands);
    await expect(page.locator(".iv-auction-rows")).not.toHaveText(firstAuction);

    // Third split cell: two pairs merged by one auction process.
    await page.locator(".iv-case").nth(2).click();
    await expect(page.locator(".iv-pair-button")).toHaveCount(2);
    await expect(page.locator(".iv-pair-button[aria-pressed='true']")).toContainText("#4");
    await expect(page.locator(".iv-case.selected .iv-tag-missed")).toBeVisible();
    const mergedHands = await page.locator(".iv-hands").textContent();
    const mergedAuction = await page.locator(".iv-auction-rows").textContent();
    await page.locator(".iv-pair-button").nth(1).click();
    await expect(page.locator(".iv-pair-button[aria-pressed='true']")).toContainText("#10");
    await expect(page.locator(".iv-hands")).not.toHaveText(mergedHands);
    await expect(page.locator(".iv-auction-rows")).toHaveText(mergedAuction);

    // Blocked process stays a TD-only cell.
    await page.locator(".iv-case").nth(3).click();
    await expect(page.locator(".iv-case.selected .iv-tag-block")).toBeVisible();
    await expect(page.locator(".iv-block-diagnostic")).toBeVisible();
    await expect(page.locator(".iv-call-td")).toHaveText("TD");
    await expect(page.locator(".iv-call-td")).toHaveAttribute("aria-label", "TD at S");
    await expect(page.locator(".iv-ew-strip")).toHaveCount(0);

    // Threshold sliders reclassify the same report without refetching.
    await setRange(page, "SET 宕 failure", 0.5);
    await expect(page.locator(".iv-category-down strong")).toHaveText("3");
    await expect(page.locator(".iv-list-tools")).toContainText("6 findings · 7 N/S pairs");
    await page.getByRole("button", { name: "Reset" }).click();
    await expect(page.locator(".iv-category-down strong")).toHaveText("1");
    await expect(page.locator(".iv-list-tools")).toContainText("5 findings · 6 N/S pairs");

    await setRange(page, "WRONG 错 success ratio", 0.9);
    await expect(page.locator(".iv-category-wrong strong")).toHaveText("2");
    await expect(page.locator(".iv-list-tools")).toContainText("6 findings · 7 N/S pairs");
    await page.getByRole("button", { name: "Reset" }).click();
    await expect(page.locator(".iv-category-wrong strong")).toHaveText("1");

    await setRange(page, "LOSE 丢 availability", 0.2);
    await expect(page.locator(".iv-category-missed strong")).toHaveText("3");
    await expect(page.locator(".iv-list-tools")).toContainText("6 findings · 7 N/S pairs");
    await page.getByRole("button", { name: "Reset" }).click();
    await expect(page.locator(".iv-category-missed strong")).toHaveText("2");

    await setRange(page, "WRONG best-other floor", 0.6);
    await expect(page.locator(".iv-category-wrong strong")).toHaveText("0");
    await expect(page.locator(".iv-list-tools")).toContainText("4 findings · 5 N/S pairs");
    await page.getByRole("button", { name: "Reset" }).click();
    await expect(page.locator(".iv-category-wrong strong")).toHaveText("1");

    // Numeric entry and the on-screen arrow buttons drive the same thresholds.
    const setValue = page.getByLabel("SET 宕 failure value");
    await setValue.fill("50");
    await setValue.press("Enter");
    await expect(page.locator(".iv-category-down strong")).toHaveText("3");
    await page.getByRole("button", { name: "Reset" }).click();
    await expect(page.locator(".iv-category-down strong")).toHaveText("1");

    await expect(setValue).toHaveValue("60");
    for (let index = 0; index < 10; index += 1) {
      await page.getByRole("button", { name: "Increase SET 宕 failure" }).click();
    }
    await expect(setValue).toHaveValue("70");
    await expect(page.locator(".iv-category-down strong")).toHaveText("0");
    await page.getByRole("button", { name: "Decrease SET 宕 failure" }).click();
    await expect(setValue).toHaveValue("69");
    await page.getByRole("button", { name: "Reset" }).click();
    await expect(setValue).toHaveValue("60");

    const wrongValue = page.getByLabel("WRONG 错 success ratio value");
    await wrongValue.fill("0.90");
    await wrongValue.press("Enter");
    await expect(page.locator(".iv-category-wrong strong")).toHaveText("2");
    await page.getByRole("button", { name: "Reset" }).click();
    await expect(wrongValue).toHaveValue("0.80");

    // Category and search filters keep the whole split cell and reset selection.
    await page.locator(".iv-category-down").click();
    await expect(page.locator(".iv-list-tools")).toContainText("1 findings · 1 N/S pairs");
    await expect(page.locator(".iv-case")).toHaveCount(1);
    await expect(page.locator(".iv-pair-button[aria-pressed='true']")).toContainText("#3");

    await page.getByRole("button", { name: "Show all" }).click();
    await page.getByRole("searchbox", { name: "Search scanner findings" }).fill("10");
    await expect(page.locator(".iv-case")).toHaveCount(1);
    await expect(page.locator(".iv-pair-button")).toHaveCount(2);
    await expect(page.locator(".iv-pair-button[aria-pressed='true']")).toContainText("#10");
    await expect(page.locator(".iv-list-tools")).toContainText("1 findings · 1 N/S pairs");

    if (errors.length) throw new Error(errors.join("\n"));
    console.log("PASS: IV Scanner split cells, merged pair rail, and live threshold sliders");
  } finally {
    await browser.close();
  }
})().catch((error) => { console.error(error); process.exitCode = 1; });
