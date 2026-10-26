// Start gible.cmd first. Requires Playwright and an installed browser.
const playwrightModule = process.env.PLAYWRIGHT_MODULE || "playwright";
const { chromium } = require(playwrightModule);
const { expect } = require(`${playwrightModule}/test`);
const assert = require("node:assert/strict");
const path = require("node:path");

(async () => {
  const browserChannel = process.env.GIBLE_BROWSER || process.env.PARTNER_BROWSER;
  const browser = await chromium.launch({ headless: true, ...(browserChannel ? { channel: browserChannel } : {}) });
  const errors = [];
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 960 } });
    page.on("pageerror", (error) => { errors.push(error.message); console.error("Browser exception:", error.message); });
    page.on("requestfailed", (request) => console.error("Request failed:", request.url(), request.failure()));
    const requests = [];
    page.on("request", (request) => {
      if (request.url().endsWith("/api/simulate")) requests.push(request.postDataJSON());
    });
    await page.goto("http://127.0.0.1:5173");
    await expect(page).toHaveTitle("Gible");
    await expect(page.locator(".brand h1")).toHaveText("Gible");
    await page.getByRole("button", { name: "Table", exact: true }).click();
    await expect(page.locator(".deal-health")).toHaveText("52 cards · Valid deal");
    await expect(page.locator(".suit-input")).toHaveCount(8);
    const north = page.getByRole("textbox", { name: "North spades", exact: true });
    const hearts = page.getByRole("textbox", { name: "North hearts", exact: true });
    const original = await north.inputValue();
    const fillOpponents = page.getByRole("button", { name: "Fill E/W hands", exact: true });

    await north.focus();
    await north.press("End");
    await north.press("ArrowRight");
    await expect(hearts).toBeFocused();
    assert.equal(await hearts.evaluate((input) => input.selectionStart), 0);
    await hearts.press("ArrowLeft");
    await expect(north).toBeFocused();
    assert.equal(await north.evaluate((input) => input.selectionStart), original.length);
    await north.press("Home");
    await north.press("ArrowLeft");
    await expect(north).toBeFocused();
    await north.press("ArrowRight");
    await expect(north).toBeFocused();
    assert.equal(await north.evaluate((input) => input.selectionStart), 1);
    await north.press("Home");
    await north.press("Shift+ArrowRight");
    await north.press("ArrowRight");
    await expect(north).toBeFocused();
    const clubs = page.getByRole("textbox", { name: "North clubs", exact: true });
    await clubs.focus();
    await clubs.press("End");
    await clubs.press("ArrowRight");
    await expect(clubs).toBeFocused();
    console.log("PASS: cursor boundaries, ordinary movement, selections and first/last suit");

    await north.fill(" a q 7 ");
    await north.press("Tab");
    await expect(north).toHaveValue("AQ7");
    for (const invalid of ["AQ77", "AQ7Z", "AQ7S", "A-"]) {
      await north.fill(invalid);
      await expect(north).toHaveAttribute("aria-invalid", "true");
      await expect(page.getByRole("button", { name: "Start auction", exact: true })).toBeDisabled();
      await expect(fillOpponents).toBeDisabled();
    }
    await north.fill("AQ");
    await expect(page.locator(".north .hand-validation")).toContainText("currently 12");
    await expect(fillOpponents).toBeDisabled();
    await north.fill(original);
    const south = page.getByRole("textbox", { name: "South spades", exact: true });
    const originalSouth = await south.inputValue();
    await south.fill("A2");
    await expect(north).toHaveAttribute("aria-invalid", "true");
    await expect(south).toHaveAttribute("aria-invalid", "true");
    await expect(page.locator(".north .hand-validation")).toContainText("South");
    await expect(fillOpponents).toBeDisabled();
    await south.fill(originalSouth);
    await expect(page.locator(".deal-health")).toContainText("Valid deal");
    assert.equal(requests.length, 0, "Invalid edits must not trigger an auction request");
    console.log("PASS: normalization, invalid ranks, wrong counts and cross-hand duplicates");

    await page.getByRole("button", { name: "Show E/W hands" }).click();
    await expect(page.locator(".suit-input")).toHaveCount(16);
    const east = page.getByRole("textbox", { name: "East spades", exact: true });
    const originalEast = await east.inputValue();
    await east.fill("AZ");
    await page.getByRole("button", { name: "Hide E/W hands" }).click();
    await expect(page.getByRole("button", { name: "Start auction", exact: true })).toBeDisabled();
    await expect(page.locator(".east")).toContainText("Check hand");
    await page.getByRole("button", { name: "Show E/W hands" }).click();
    await expect(east).toHaveValue("AZ");
    await east.fill(originalEast);
    await expect(page.locator(".deal-health")).toContainText("Valid deal");
    console.log("PASS: hiding preserves opponents and does not bypass validation");

    const nsInputs = page.locator(".north .suit-input, .south .suit-input");
    const nsBeforeFill = await nsInputs.evaluateAll((inputs) => inputs.map((input) => input.value));
    await east.fill(original); // Old E/W cards conflict with North, but are replaceable.
    await expect(fillOpponents).toBeEnabled();
    await fillOpponents.click();
    await expect(page.locator(".deal-health")).toHaveText("52 cards · Valid deal");
    assert.deepEqual(await nsInputs.evaluateAll((inputs) => inputs.map((input) => input.value)), nsBeforeFill);
    const ewBeforeFill = await page.locator(".east .suit-input, .west .suit-input").evaluateAll((inputs) => inputs.map((input) => input.value));
    await east.fill("AZ");
    await page.getByRole("button", { name: "Hide E/W hands" }).click();
    await expect(fillOpponents).toBeEnabled();
    await fillOpponents.click();
    await expect(page.locator(".suit-input")).toHaveCount(8);
    await expect(page.locator(".deal-health")).toHaveText("52 cards · Valid deal");
    await page.getByRole("button", { name: "Show E/W hands" }).click();
    assert.notDeepEqual(await page.locator(".east .suit-input, .west .suit-input").evaluateAll((inputs) => inputs.map((input) => input.value)), ewBeforeFill);
    assert.deepEqual(await nsInputs.evaluateAll((inputs) => inputs.map((input) => input.value)), nsBeforeFill);
    console.log("PASS: E/W completion preserves N/S, replaces conflicts and invalid hidden hands, and can re-deal");

    await page.getByRole("button", { name: "Hide E/W hands" }).click();
    await page.getByRole("button", { name: "Clear E/W hands", exact: true }).click();
    await expect(page.getByRole("button", { name: "Hide E/W hands" })).toBeVisible();
    assert.deepEqual(await page.locator(".east .suit-input, .west .suit-input").evaluateAll(
      (inputs) => inputs.map((input) => input.value)), Array(8).fill(""));
    assert.deepEqual(await nsInputs.evaluateAll((inputs) => inputs.map((input) => input.value)), nsBeforeFill);
    await expect(page.locator(".deal-health")).toContainText("Check hands");
    await expect(page.getByRole("button", { name: "Start auction", exact: true })).toBeDisabled();
    await fillOpponents.click();
    await expect(page.locator(".deal-health")).toContainText("Valid deal");
    console.log("PASS: clear E/W preserves N/S, reveals blanks and resets auction eligibility");

    await page.getByRole("button", { name: "Show full auction" }).click();
    await expect(page.locator(".auction-call-card:not(.empty)").first()).toBeVisible({ timeout: 15000 });
    assert.deepEqual(Object.keys(requests.at(-1).hands).sort(), ["n", "s"]);
    const callCount = await page.locator(".auction-call-card:not(.empty)").count();
    const visibleCalls = page.locator(".auction-call-card:not(.empty)");
    await visibleCalls.first().hover();
    await expect(page.locator(".auction-tooltip")).toBeVisible();
    await page.mouse.move(4, 4);
    await expect(page.locator(".auction-tooltip")).toHaveCount(0);
    await visibleCalls.first().click();
    await page.mouse.move(4, 4);
    await expect(page.locator(".auction-tooltip")).toBeVisible();
    if (callCount > 1) {
      const firstExplanation = await page.locator(".auction-tooltip").innerText();
      await visibleCalls.nth(1).click();
      await expect(page.locator(".auction-tooltip")).not.toHaveText(firstExplanation);
    }
    await page.locator(".deal-health").click();
    await expect(page.locator(".auction-tooltip")).toHaveCount(0);
    await visibleCalls.first().focus();
    await visibleCalls.first().press("Enter");
    await expect(page.locator(".auction-tooltip")).toBeVisible();
    await page.keyboard.press("Escape");
    await expect(page.locator(".auction-tooltip")).toHaveCount(0);
    console.log("PASS: call explanations hover, pin by click or keyboard, switch and close outside");
    const analysisRequests = [];
    await page.route("**/api/analysis/contracts", async (route) => {
      analysisRequests.push(route.request().postDataJSON());
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({
        mode: "analysis_only", sample_count: 2, attempts: 12, seed: 17,
        estimates: [{ contract: "4H", declarer: "n", made: 1, sample_count: 2, completion_rate: 0.5 }],
      }) });
    });
    await page.getByRole("button", { name: "Show analysis tools" }).click();
    await page.getByRole("textbox", { name: "Contracts to analyze" }).fill("4HN");
    await expect(page.getByRole("button", { name: "Analyze", exact: true })).toBeEnabled();
    await page.getByRole("button", { name: "Analyze", exact: true }).click();
    await expect(page.locator(".contract-analysis-results")).toContainText("1/2 made (50%)");
    assert.deepEqual(Object.keys(analysisRequests[0]).sort(),
      ["auction", "dealer", "hand", "profile", "sample_count", "seat", "targets", "vulnerability"]);
    assert.equal(analysisRequests[0].seat, ["n", "e", "s", "w"][callCount % 4]);
    assert.deepEqual(analysisRequests[0].targets, [{ level: 4, strain: "H", declarer: "n" }]);
    console.log("PASS: contract analysis stays separate from bidding and sends only the acting hand");
    const routeRequests = [];
    await page.route("**/api/analysis/routes", async (route) => {
      routeRequests.push(route.request().postDataJSON());
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({
        mode: "route_experiment", sample_count: 2, attempts: 12, seed: 17,
        routes: [
          { first_call: "4C", status: "evaluated", completed: 2, made: 1, failed: 1,
            blocked: 0, contracts: [{ contract: "4H", declarer: "n", count: 2, made: 1 }], block_reasons: [] },
          { first_call: "2D", status: "unavailable", reason: "Continuation is not authored",
            completed: 0, made: 0, failed: 0, blocked: 2, contracts: [], block_reasons: [] },
        ],
      }) });
    });
    await page.getByRole("button", { name: "Show first call" }).click();
    await page.getByRole("button", { name: "Show next call" }).click();
    const routePanel = page.getByRole("region", { name: "Route experiment" });
    await routePanel.getByRole("textbox", { name: "First calls to compare" }).fill("4C, 2D");
    await routePanel.getByRole("textbox", { name: "Route experiment seed" }).fill("17");
    await routePanel.getByRole("button", { name: "Compare routes" }).click();
    await expect(routePanel.locator(".contract-analysis-results")).toContainText("2/2 completed");
    await expect(routePanel.locator(".contract-analysis-results")).toContainText("Route unavailable");
    assert.deepEqual(Object.keys(routeRequests[0]).sort(),
      ["auction", "dealer", "first_calls", "hand", "profile", "sample_count", "seat", "seed", "vulnerability"]);
    assert.equal(routeRequests[0].auction, "1NP");
    assert.deepEqual(routeRequests[0].first_calls, ["4C", "2D"]);
    if (await page.getByRole("button", { name: "Show full auction" }).isEnabled()) {
      await page.getByRole("button", { name: "Show full auction" }).click();
    }
    console.log("PASS: route report distinguishes completed and unavailable branches without sending hidden hands");
    await north.fill("AQ7Z");
    await expect(page.locator(".auction-call-card:not(.empty)")).toHaveCount(0);
    await north.fill(original);
    await expect(page.locator(".auction-call-card:not(.empty)")).toHaveCount(callCount, { timeout: 15000 });
    console.log("PASS: real backend auction, clearing invalid replay and refreshing corrected hands");

    const before = await page.locator(".suit-input").evaluateAll((inputs) => inputs.map((input) => input.value));
    await page.getByRole("button", { name: "Random deal", exact: true }).click();
    await expect(page.locator(".auction-call-card:not(.empty)")).toHaveCount(0);
    await expect(page.locator(".deal-health")).toHaveText("52 cards · Valid deal");
    const after = await page.locator(".suit-input").evaluateAll((inputs) => inputs.map((input) => input.value));
    assert.notDeepEqual(after, before);
    const cards = [];
    for (const seat of ["North", "East", "South", "West"]) {
      let count = 0;
      for (const suit of ["spades", "hearts", "diamonds", "clubs"]) {
        const ranks = await page.getByRole("textbox", { name: `${seat} ${suit}`, exact: true }).inputValue();
        count += ranks.length;
        cards.push(...[...ranks].map((rank) => `${suit}:${rank}`));
      }
      assert.equal(count, 13);
    }
    assert.equal(new Set(cards).size, 52);
    await page.getByRole("button", { name: "Hide E/W hands" }).click();
    await page.getByRole("button", { name: "Show E/W hands" }).click();
    assert.deepEqual(await page.locator(".suit-input").evaluateAll((inputs) => inputs.map((input) => input.value)), after);
    console.log("PASS: random full deal, 52 unique cards, reset and visibility preservation");

    // A response from the previous deal must not restore its auction after re-dealing.
    await page.route("**/api/simulate", async (route) => {
      const response = await route.fetch();
      await new Promise((resolve) => setTimeout(resolve, 500));
      await route.fulfill({ response });
    });
    const pending = page.waitForResponse("**/api/simulate");
    await page.getByRole("button", { name: "Start auction", exact: true }).click();
    await expect(page.locator(".auction-empty.waiting")).toBeVisible();
    await page.getByRole("button", { name: "Random deal", exact: true }).click();
    await pending;
    await expect(page.locator(".auction-call-card:not(.empty)")).toHaveCount(0);
    await expect(page.getByRole("button", { name: "Start auction", exact: true })).toBeEnabled();
    console.log("PASS: stale auction response ignored after a new deal");

    for (const width of [1440, 1024]) {
      await page.setViewportSize({ width, height: 900 });
      await expect(page.getByRole("textbox", { name: "South clubs", exact: true })).toBeAttached();
      const layout = await page.evaluate(() => ({
        pageWidth: document.documentElement.clientWidth,
        contentWidth: document.documentElement.scrollWidth,
        tableWidth: document.querySelector(".bridge-layout").clientWidth,
        tableContent: document.querySelector(".bridge-layout").scrollWidth,
      }));
      assert.ok(layout.contentWidth <= layout.pageWidth, JSON.stringify(layout));
      assert.ok(layout.tableContent <= layout.tableWidth + 1, JSON.stringify(layout));
      if (process.env.TABLE_SCREENSHOT_DIR) await page.screenshot({ path: path.join(process.env.TABLE_SCREENSHOT_DIR, `table-${width}.png`) });
    }
    await page.setViewportSize({ width: 1024, height: 600 });
    for (const visible of [true, false]) {
      if (!visible) await page.getByRole("button", { name: "Hide E/W hands" }).click();
      const southClubs = page.getByRole("textbox", { name: "South clubs", exact: true });
      await southClubs.scrollIntoViewIfNeeded();
      await expect(southClubs).toBeInViewport();
      await southClubs.click();
      await expect(southClubs).toBeFocused();
    }
    assert.deepEqual(errors, []);
    console.log("PASS: responsive layout and no browser exceptions");
  } finally {
    await browser.close();
  }
})().catch((error) => { console.error(error); process.exit(1); });
