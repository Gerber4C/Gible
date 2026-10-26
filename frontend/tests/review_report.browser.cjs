const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  try {
    const page = await browser.newPage({ acceptDownloads: true });
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    const report = path.resolve(__dirname, '../../reports/block_scans/daqiush-1nt-resample-span2-seed41-review.html');
    await page.goto(pathToFileURL(report).href);
    await page.locator('[data-group="G012"]').click();
    assert.match(await page.locator('#review-call').inputValue(), /4NT/);
    await page.locator('#review-proposal').fill('审核中的测试修改：4NT问关键张');
    await page.locator('[data-decision="approved"]').click();
    assert.equal(await page.locator('[data-decision="approved"]').getAttribute('aria-pressed'), 'true');
    await page.locator('[data-review-nav="next"]').click();
    await page.locator('[data-review-nav="previous"]').click();
    assert.match(await page.locator('#review-proposal').inputValue(), /审核中的测试修改/);
    await page.reload();
    assert.match(await page.locator('#review-proposal').inputValue(), /审核中的测试修改/);
    const downloadPromise = page.waitForEvent('download');
    await page.locator('#review-export').click();
    const download = await downloadPromise;
    const exported = JSON.parse(fs.readFileSync(await download.path(), 'utf8'));
    assert.equal(exported.groups.G012.decision, 'approved');
    assert.match(exported.groups.G012.proposal, /审核中的测试修改/);
    const original = path.resolve(__dirname, '../../docs/reviews/daqiush-1nt-seed41.json');
    await page.locator('#review-import').setInputFiles(original);
    await page.waitForFunction(() => document.getElementById('review-save-state').textContent.includes('已导入'));
    assert.equal(await page.locator('#review-proposal').inputValue(),
      JSON.parse(fs.readFileSync(original, 'utf8')).groups.G012.proposal);
    await page.locator('.review-panel').scrollIntoViewIfNeeded();
    await page.screenshot({ path: path.resolve(__dirname, '../../reports/block_scans/review-ui-desktop.png'), fullPage: false });
    assert.equal(errors.length, 0, errors.join('\n'));
    console.log('PASS: 88-group review, edit, navigation, local save, export');
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
