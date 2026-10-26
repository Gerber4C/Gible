# IV Scanner Matrix Display Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Merge IV Scanner findings by NS cell and render N/S pair by E/W sample results in a horizontally scrollable matrix, with auctions wrapping every four calls.

**Architecture:** Keep report data and API contracts unchanged. Add pure frontend display helpers in `IVScanner.js`, derive grouped findings after existing filtering, and render a group list plus matrix detail. Use focused CSS for matrix overflow and call rows.

**Tech Stack:** Existing React-compatible `e()` helper, plain JavaScript, existing CSS, Playwright browser smoke test.

---

## Chunk 1: Grouping and auction presentation

### Task 1: Add pure display helpers and tests

**Files:**
- Modify: `frontend/src/components/IVScanner.js`
- Test: `frontend/tests/iv_scanner.browser.cjs`

- [ ] **Step 1: Add assertions for one merged NS-cell entry and four-call auction rows**
- [ ] **Step 2: Run the focused browser test and confirm the new assertions fail**
- [ ] **Step 3: Implement NS-cell grouping and auction chunking helpers**
- [ ] **Step 4: Run the focused browser test and confirm the assertions pass**

### Task 2: Render grouped findings and matrix details

**Files:**
- Modify: `frontend/src/components/IVScanner.js`
- Modify: `frontend/src/styles/app.css`
- Test: `frontend/tests/iv_scanner.browser.cjs`

- [ ] **Step 1: Render one selectable group per NS cell**
- [ ] **Step 2: Render N/S pair rows and E/W sample columns inside an overflow wrapper**
- [ ] **Step 3: Preserve category/search behavior against grouped data**
- [ ] **Step 4: Run the scanner browser test and verify the matrix and wrapped auction**

### Task 3: Update related documentation

**Files:**
- Modify: `docs/18_block_scout.md`

- [ ] **Step 1: Document grouped NS-cell and matrix behavior**
- [ ] **Step 2: Run the existing relevant tests**
