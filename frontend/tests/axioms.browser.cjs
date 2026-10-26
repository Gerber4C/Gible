// Start the frontend server first. All backend responses are mocked.
const playwrightModule = process.env.PLAYWRIGHT_MODULE || "playwright";
const { chromium } = require(playwrightModule);
const { expect } = require(`${playwrightModule}/test`);
const assert = require("node:assert/strict");
const path = require("node:path");

(async () => {
  const browserChannel = process.env.GIBLE_BROWSER || process.env.PARTNER_BROWSER;
  const browser = await chromium.launch({ headless: true, ...(browserChannel ? { channel: browserChannel } : {}) });
  const errors = [];
  const injection = '<img src=x onerror="window.axiomInjected=true">';
  const report = {
    obligations: [{ kind: "game_force" }],
    errors: [{ code: "force_pass", message: `Pass violates game force. ${injection}` }],
    rejected: [{ call: "P" }], quality: { good: false, score: -1, features: {} }, evidence: [],
  };
  const record = { seat: "n", call: "1H", explanation: { diagnostics: [], axioms: { ...report, status: "selected" } } };
  try {
    for (const priorCalls of [false, true]) {
      const page = await browser.newPage({ viewport: { width: 1440, height: 960 } });
      page.on("pageerror", (error) => { errors.push(error.message); console.error("Browser exception:", error.message); });
      page.on("requestfailed", (request) => console.error("Request failed:", request.url(), request.failure()));
      // Optional local copies of the CDN modules for offline browser environments.
      const esmCache = process.env.GIBLE_ESM_CACHE || process.env.PARTNER_ESM_CACHE;
      if (esmCache) await page.route("https://esm.sh/**", (route) => route.fulfill({
        path: path.join(esmCache, decodeURIComponent(new URL(route.request().url()).pathname).replaceAll("/", "_")),
        contentType: "text/javascript", headers: { "Access-Control-Allow-Origin": "*" },
      }));
      let requestCount = 0;
      await page.route("http://127.0.0.1:8765/api/**", (route) => {
        const url = new URL(route.request().url());
        let response = {};
        if (url.pathname === "/api/profiles") response = { profiles: [{ id: "meow_2over1", name: "Test" }] };
        else if (url.pathname.endsWith("/files")) response = { files: [] };
        else if (url.pathname === "/api/simulate") {
          requestCount += 1;
          response = { status: "blocked", records: priorCalls ? [record, { seat: "e", call: "P" }] : [],
            calls: priorCalls ? ["1H", "P"] : [], blocked: { auction: priorCalls ? "1HP" : "", seat: priorCalls ? "s" : "n",
              diagnostics: [`No acceptable call. ${injection}`], axioms: report } };
        }
        return route.fulfill({ json: response });
      });
      await page.goto(process.env.GIBLE_FRONTEND_URL || process.env.PARTNER_FRONTEND_URL || "http://127.0.0.1:5173");
      await page.getByRole("button", { name: "Table", exact: true }).click();
      await page.getByRole("button", { name: "Show full auction", exact: true }).click();
      const blocked = page.locator(".auction-blocked");
      await expect(blocked).toContainText(`Auction blocked · ${priorCalls ? "South" : "North"}`);
      await expect(blocked).toContainText("No acceptable call.");
      await expect(blocked).toContainText(injection);
      await expect(blocked).toContainText("force_pass");
      await expect(page.locator(".statusbar")).toContainText("Auction blocked");
      await expect(page.locator(".auction-call-card:not(.empty)")).toHaveCount(priorCalls ? 2 : 0);
      await expect(page.getByRole("button", { name: "Show full auction", exact: true })).toBeDisabled();
      await expect(page.getByRole("button", { name: priorCalls ? "Show next call" : "Start auction", exact: true })).toBeDisabled();
      await expect(page.locator(".auction-panel img")).toHaveCount(0);
      if (priorCalls) {
        await page.locator(".auction-call-card:not(.empty)").first().focus();
        await expect(page.locator(".auction-tooltip")).toContainText("Axioms:");
        await expect(page.locator(".auction-tooltip")).toContainText("game force");
        await expect(page.locator(".auction-tooltip")).toContainText("force_pass");
        await expect(page.locator(".auction-tooltip")).toContainText(injection);
        await page.getByRole("button", { name: "Step backward", exact: true }).click();
        await page.getByRole("button", { name: "Step backward", exact: true }).click();
        await expect(page.locator(".auction-call-card:not(.empty)")).toHaveCount(0);
        await page.getByRole("button", { name: "Start auction", exact: true }).click();
        await expect(page.locator(".auction-call-card:not(.empty)")).toHaveCount(1);
        await page.getByRole("button", { name: "Show full auction", exact: true }).click();
        await expect(page.locator(".auction-call-card:not(.empty)")).toHaveCount(2);
      }
      assert.equal(requestCount, 1, "Replaying an existing blocked result must not request another simulation");
      assert.equal(await page.evaluate(() => window.axiomInjected), undefined);
      await page.getByRole("button", { name: "Random deal", exact: true }).click();
      await expect(blocked).toHaveCount(0);
      await expect(page.getByRole("button", { name: "Start auction", exact: true })).toBeEnabled();
      console.log(`PASS: blocked ${priorCalls ? "prior-call replay" : "zero-call result"}, safe diagnostics and reset`);
      await page.close();
    }
    assert.deepEqual(errors, []);
  } finally {
    await browser.close();
  }
})().catch((error) => { console.error(error); process.exit(1); });
