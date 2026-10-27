// Deterministic Pair-rail check against a grouped fixture. Only the
// frontend dev server is required; every API call is fulfilled locally.
const { chromium } = require("playwright");
const { expect } = require("playwright/test");
const path = require("node:path");
const fs = require("node:fs/promises");

const FIXTURE_PATH = path.resolve(__dirname, "fixtures/iv_scanner_grouped_report.json");
const REPORT_ID = "iv-scanner-fixture-pairs.json";

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
    await expect(page.locator(".iv-list-tools")).toContainText("20 findings · 2 NS cells");
    await expect(page.locator(".iv-case")).toHaveCount(2);

    await page.locator(".iv-case").first().click();
    await expect(page.locator(".iv-pair-button")).toHaveCount(10);
    const selected = page.locator(".iv-pair-button[aria-pressed='true']");
    await expect(selected).toContainText("#1");
    await expect(page.locator(".iv-badge-clean").first()).toBeVisible();

    const handsBefore = await page.locator(".iv-hands").innerText();
    const auctionBefore = await page.locator(".iv-auction-rows").innerText();
    await page.locator(".iv-pair-button").nth(1).click();
    await expect(page.locator(".iv-pair-button[aria-pressed='true']")).toContainText("#2");
    await expect(page.locator(".iv-hands")).not.toHaveText(handsBefore);
    await expect(page.locator(".iv-auction-rows")).not.toHaveText(auctionBefore);
    await expect(page.locator(".iv-warning-list")).toContainText("RATIO");

    await page.locator(".iv-pair-button").nth(2).click();
    await expect(page.locator(".iv-pair-button[aria-pressed='true']")).toContainText("#3");
    await expect(page.locator(".iv-warning-list")).toContainText("SET > 60%");
    await expect(page.locator(".iv-ew-outcome").first()).toHaveText(/MAKE|SET/);
    await expect(page.locator(".iv-ew-lose").first()).toHaveAttribute("title", "Missed small slam");

    await page.locator(".iv-pair-button").nth(4).click();
    await expect(page.locator(".iv-block-diagnostic")).toBeVisible();
    await expect(page.locator(".iv-ew-strip")).toHaveCount(0);

    await page.locator(".iv-pair-button").nth(5).click();
    await expect(page.locator(".iv-detail-heading h3")).toContainText("Call limit");
    await expect(page.locator(".iv-ew-strip")).toHaveCount(0);

    await expect(page.locator(".iv-badge-unavailable")).toHaveCount(1);
    await expect(page.locator(".iv-badge-td")).toHaveCount(1);
    await expect(page.locator(".iv-badge-set")).toHaveCount(1);
    await expect(page.locator(".iv-badge-lose")).toHaveCount(1);
    await expect(page.locator(".iv-badge-wrong")).toHaveCount(1);

    await page.locator(".iv-category-down").click();
    await expect(page.locator(".iv-list-tools")).toContainText("1 findings · 1 NS cells");
    await expect(page.locator(".iv-pair-button")).toHaveCount(10);
    await expect(page.locator(".iv-pair-button[aria-pressed='true']")).toContainText("#3");

    await page.locator(".iv-pair-button").first().click();
    await expect(page.locator(".iv-pair-button[aria-pressed='true']")).toContainText("#1");
    await expect(page.locator(".iv-warning-list")).toHaveCount(0);

    await page.locator(".iv-category-wrong").click();
    await expect(page.locator(".iv-pair-button[aria-pressed='true']")).toContainText("#2");
    await page.locator(".iv-category-wrong").click();
    await page.getByRole("searchbox", { name: "Search scanner findings" }).fill("17");
    await expect(page.locator(".iv-case")).toHaveCount(1);
    await expect(page.locator(".iv-pair-button")).toHaveCount(10);
    await expect(page.locator(".iv-pair-button[aria-pressed='true']")).toContainText("#17");

    if (errors.length) throw new Error(errors.join("\n"));
    console.log("PASS: IV Scanner pair rail, synchronized pair detail, badges, and filter-reset behavior");
  } finally {
    await browser.close();
  }
})().catch((error) => { console.error(error); process.exitCode = 1; });
