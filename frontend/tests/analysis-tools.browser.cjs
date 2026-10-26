// Start the local frontend and backend first. Requires Playwright and a browser.
const playwrightModule = process.env.PLAYWRIGHT_MODULE || "playwright";
const { chromium } = require(playwrightModule);
const { expect } = require(`${playwrightModule}/test`);
const assert = require("node:assert/strict");

(async () => {
  const browserChannel = process.env.GIBLE_BROWSER || process.env.PARTNER_BROWSER;
  const browser = await chromium.launch({ headless: true, ...(browserChannel ? { channel: browserChannel } : {}) });
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 960 } });
    await page.goto("http://127.0.0.1:5173");
    await page.getByRole("button", { name: "Table", exact: true }).click();

    const table = page.locator(".bridge-layout");
    const height = () => table.evaluate((element) => element.getBoundingClientRect().height);
    const collapsedHeight = await height();
    const show = page.getByRole("button", { name: "Show analysis tools" });
    await expect(show).toHaveAttribute("aria-expanded", "false");
    await expect(page.locator(".contract-analysis").first()).toBeHidden();

    await show.click();
    await expect(page.getByRole("region", { name: "Contract analysis" })).toBeVisible();
    const expandedHeight = await height();
    assert.ok(collapsedHeight > expandedHeight, "Collapsed tools should give more height to the table");
    await page.getByRole("textbox", { name: "Contracts to analyze" }).fill("3NTN");
    await page.getByRole("button", { name: "Hide analysis tools" }).click();
    await expect(page.locator(".contract-analysis").last()).toBeHidden();
    assert.ok(Math.abs(await height() - collapsedHeight) < 2, "Table should regain its height");

    await page.getByRole("button", { name: "Show analysis tools" }).click();
    await expect(page.getByRole("textbox", { name: "Contracts to analyze" })).toHaveValue("3NTN");
    console.log("PASS: analysis tools hide, restore table space, and preserve input");
  } finally {
    await browser.close();
  }
})().catch((error) => { console.error(error); process.exitCode = 1; });
