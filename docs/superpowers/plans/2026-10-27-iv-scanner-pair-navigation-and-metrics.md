# IV Scanner Pair Navigation and Outcome Metrics Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make every ten-pair IV Scanner sampling cell navigable pair by pair and replace the old odds-ratio/50% warnings with the approved success-ratio/60% rules.

**Architecture:** Put all DDS outcome formulas, warning thresholds, legacy reclassification, and per-board MAKE/SET/LOSE labels in one backend module. Coverage scanning records stable sampling-cell metadata; the IV API projects only actionable cells but keeps all sibling pairs. The frontend consumes those groups with a group list, a vertical Pair rail, and one selected-pair detail pane.

**Tech Stack:** Python 3.11 standard library and `unittest`; browser-native React modules; Node test runner; Playwright browser smoke tests.

**Design reference:** `docs/superpowers/specs/2026-10-27-iv-scanner-pair-navigation-and-metrics-design.md`

**Working-tree note:** This repository already contains staged and unstaged user work in files this feature must edit. Preserve those edits and patch only the named behavior. Do not create intermediate Git commits from this working tree: even path-limited commits would capture unrelated hunks in overlapping files. Each task ends with a scoped diff/test checkpoint instead; leave final commit selection to the user after review.

---

## Chunk 1: Metrics, report projection, and Pair navigation

### Task 1: Centralize completion metrics and warning rules

**Files:**
- Create: `backend/engine/outcome_metrics.py`
- Modify: `backend/engine/coverage_scan.py:145-280`
- Test: `backend/tests/test_outcome_metrics.py`
- Test: `backend/tests/test_coverage_scan.py:118-180`

- [ ] **Step 1: Write failing metric tests**

Create `backend/tests/test_outcome_metrics.py` with focused cases for the exact boundaries:

```python
import unittest

from engine.outcome_metrics import (
    RULE_ID, board_result, classify_rates, game_success_ratio,
)


class OutcomeMetricTests(unittest.TestCase):
    def test_wrong_uses_success_probability_ratio(self):
        ratio, alternatives = game_success_ratio(
            '4S', 'n', self.boards(chosen=4, nt=6, total=10))
        self.assertAlmostEqual(ratio, 2 / 3)
        self.assertEqual(alternatives['3NT'], .6)

    def test_best_other_at_set_line_suppresses_wrong(self):
        ratio, alternatives = game_success_ratio(
            '4S', 'n', self.boards(chosen=3, nt=4, total=10))
        self.assertIsNone(ratio)
        self.assertEqual(alternatives['3NT'], .4)

    def test_set_is_strictly_above_sixty_percent(self):
        self.assertNotIn('contract_failure', classify_rates(
            '4S', {'contract_failure': .6, 'wrong_game': None}, {}))
        self.assertIn('contract_failure', classify_rates(
            '4S', {'contract_failure': .61, 'wrong_game': None}, {}))

    def test_ratio_equality_does_not_warn(self):
        self.assertNotIn('wrong_game', classify_rates(
            '4S', {'contract_failure': .2, 'wrong_game': .8}, {'3NT': .5}))

    def test_matrix_result_keeps_outcome_and_missed_target(self):
        table = self.table(spades=7, nt=9, hearts=12)
        self.assertEqual(board_result('2S', 'n', table), {
            'outcome': 'SET', 'lose': True, 'missed_target': 'small slam',
        })

    def test_rule_identifier_is_stable(self):
        self.assertEqual(
            RULE_ID,
            'success_probability_ratio_0.8_best_above_0.4_set_above_0.6',
        )
```

Add small `table()` and `boards()` helpers in the test that create five-strain, two-seat DDS tables. Include cases for a perfect chosen game, no positive alternative, a non-game selected contract, `MAKE`, `SET`, and the highest of multiple missed targets. The perfect chosen-game case must explicitly assert a legal ratio greater than one, such as `1.0 / 0.5 == 2.0`.

Also cover every computed warning boundary: `missed_game`, `missed_small_slam`, and `missed_grand_slam` trigger only when their applicable rate is strictly greater than `.30`; equality at `.30` does not warn. Verify a new scan can produce all three missed-target flags without passing them through `existing_flags`, and verify an unrelated pre-existing flag is preserved. Add a legacy test whose rates omit all missed-target fields but whose flags contain `missed_game`; `reclassify_analysis` must preserve that flag while replacing stale SET/WRONG.

- [ ] **Step 2: Run the new tests and verify RED**

Run from `backend/`:

```powershell
..\.venv\Scripts\python.exe -m unittest tests.test_outcome_metrics -v
```

Expected: import failure for `engine.outcome_metrics`.

- [ ] **Step 3: Implement the metrics module**

Create `backend/engine/outcome_metrics.py` with these public values and functions:

```python
SET_FAILURE_THRESHOLD = .60
WRONG_RATIO_THRESHOLD = .80
BEST_OTHER_SUCCESS_FLOOR = .40
MISSED_THRESHOLD = .30
RULE_ID = 'success_probability_ratio_0.8_best_above_0.4_set_above_0.6'
GAME_TARGETS = {'3NT': ('NT', 9), '4S': ('S', 10), '4H': ('H', 10),
                '5D': ('D', 11), '5C': ('C', 11)}

def available_level(table, category): ...
def reached_game(contract): ...
def game_success_ratio(contract, declarer, boards): ...
def classify_rates(contract, rates, alternative_rates, existing_flags=(),
                   *, recompute_missed=True): ...
def reclassify_analysis(contract, analysis): ...
def board_result(contract, declarer, table): ...
```

Implement `game_success_ratio` as selected completion probability divided by the largest other-game completion probability. Return `(None, alternatives)` unless the selected contract is a game, boards exist, and the best alternative is strictly above `.40`. Never calculate odds.

For a new scan, `classify_rates(..., recompute_missed=True)` is the single owner of all five computed warning flags: `contract_failure`, `wrong_game`, `missed_game`, `missed_small_slam`, and `missed_grand_slam`. It removes stale instances of those five from `existing_flags`, preserves unrelated flags, then recomputes: SET only when `contract_failure > .60`; WRONG only for a finite ratio `< .80` with best-other success `> .40`; missed game only when the selected contract has not reached game and `missed_game > .30`; missed small slam only below level 6 and `missed_small_slam > .30`; missed grand slam only below level 7 and `missed_grand_slam > .30`. Missing or invalid rates do not warn.

`reclassify_analysis` accepts legacy mappings and calls `classify_rates(..., recompute_missed=False)`: it removes and recomputes only `contract_failure` and `wrong_game`, while preserving existing `missed_game`, `missed_small_slam`, and `missed_grand_slam` flags even when the legacy report has no corresponding rates. Probability inputs (`contract_failure`, missed-target rates, and alternative-game probabilities) must be finite numbers in `[0, 1]`. The recomputed completion ratio is not a probability: it is valid when finite and nonnegative and may exceed `1` (for example `1.0 / 0.5 == 2.0`). Invalid data makes only the relevant recomputed metric `None`. `board_result` returns the primary `MAKE`/`SET` outcome and independent LOSE evidence using the three target-level checks in the spec.

- [ ] **Step 4: Replace duplicate coverage formulas**

In `backend/engine/coverage_scan.py`, import the shared functions and constants. Keep explicit compatibility aliases `_available_level = available_level`, `_reached_game = reached_game`, and `wrong_game_rates = game_success_ratio` until Task 4 updates `suspicious_resample.py`. In `classify_suspicious`, build all five raw rates and call `classify_rates` without relying on caller-supplied missed flags; the helper must produce them. Set the raw report's existing `wrong_game_rule` field to `RULE_ID`; do not introduce a second metadata field.

- [ ] **Step 5: Run metric and coverage tests and verify GREEN**

```powershell
..\.venv\Scripts\python.exe -m unittest tests.test_outcome_metrics tests.test_coverage_scan -v
```

Expected: all tests pass; no `inf`, `Infinity`, or odds-ratio assertions remain.

- [ ] **Step 6: Inspect the metric-layer diff checkpoint**

```powershell
git diff --check -- backend/engine/outcome_metrics.py backend/engine/coverage_scan.py backend/tests/test_outcome_metrics.py backend/tests/test_coverage_scan.py
git diff -- backend/engine/outcome_metrics.py backend/engine/coverage_scan.py backend/tests/test_outcome_metrics.py backend/tests/test_coverage_scan.py
..\.venv\Scripts\python.exe -m py_compile engine/outcome_metrics.py
```

The compile command directly checks the new untracked module; ordinary `git diff` does not show untracked files.

### Task 2: Record every scheduled Pair and its sampling cell

**Files:**
- Modify: `backend/engine/coverage_scan.py:317-470`
- Test: `backend/tests/test_coverage_scan.py`

- [ ] **Step 1: Write failing sampling-cell tests**

Add tests that run a one-cell, three-pair scan and assert every record has:

```python
'coverage_cell': {
    'target_hcp': 10,
    'base_shape_index': 0,
    'base_shape': [6, 3, 2, 2],
    'pair_slot': 0,  # then 1 and 2
}
```

Add a bounded fake simulation result or profile that reaches the call limit and assert its record is retained in `limit_cases`, including hands, calls, auction, and `coverage_cell`. Assert the union of `cases`, `complete_cases`, and `limit_cases` contains all scheduled IDs exactly once.

- [ ] **Step 2: Run the new coverage tests and verify RED**

```powershell
..\.venv\Scripts\python.exe -m unittest tests.test_coverage_scan -v
```

Expected: missing `coverage_cell` and `limit_cases` assertions fail.

- [ ] **Step 3: Add explicit cell metadata and limit records**

Build the cell mapping from the existing `(hcp, base_shape, shape_index, slot)` schedule. Add it to the case before branching on simulation status. Introduce `limit_cases = []`; append call-limit cases there with `status='limit'`. Return `limit_cases` beside `cases` and `complete_cases`. Do not run DDS for blocked or limit cases.

- [ ] **Step 4: Run coverage tests and verify GREEN**

```powershell
..\.venv\Scripts\python.exe -m unittest tests.test_coverage_scan -v
```

Expected: all coverage tests pass and scheduled IDs are complete.

- [ ] **Step 5: Inspect the cell-identity diff checkpoint**

```powershell
git diff --check -- backend/engine/coverage_scan.py backend/tests/test_coverage_scan.py
```

### Task 3: Project actionable cells with all sibling Pairs

**Files:**
- Modify: `backend/engine/iv_scanner.py:20-155`
- Test: `backend/tests/test_iv_scanner.py`

- [ ] **Step 1: Write failing projection tests**

Expand the IV Scanner fixture to two sampling cells with three pairs each. In the first cell, give only pair 2 a warning and give all three distinct hands and auctions. Assert:

```python
[pair['id'] for pair in projected['groups'][0]['pairs']] == [1, 2, 3]
projected['groups'][0]['pairs'][0]['categories'] == []
projected['counts']['down'] == 1
```

Assert a completely clean second cell is absent. Add legacy fixtures without `coverage_cell`, including invalid/non-finite rates and stale SET/WRONG flags. Assert grouping uses stored South HCP plus named-suit shape, flags and counts are recomputed, and a missing legacy slot produces `incomplete=True` with the actual and expected counts. Add a legacy case whose South HCP or named-suit `south_shape` is missing/invalid so no cell can be inferred; assert it is retained in a stable one-Pair fallback group keyed by deal ID, with `actual_pair_count=1` and `incomplete=True`.

Assert the exact projected schema for an explicit cell:

```python
group = projected['groups'][0]
self.assertEqual(group['id'], '10:0')
self.assertEqual(group['south_hcp'], 10)
self.assertEqual(group['south_shape'], [6, 3, 2, 2])
self.assertEqual(group['warning_counts'],
                 {'block': 0, 'missed': 0, 'down': 1, 'wrong': 0})
self.assertEqual(group['actual_pair_count'], 3)
self.assertEqual(group['expected_pair_count'], 3)
self.assertFalse(group['incomplete'])
self.assertEqual(group['pairs'][0]['pair_slot'], 0)
self.assertEqual(group['pairs'][0]['status'], 'complete')
```

Add blocked and limit siblings and assert their statuses are `blocked` and `limit`; the limit pair carries no `ew_results` and remains selectable. Assert projected `wrong_game_rule == RULE_ID` even when the source report carries a legacy identifier.

Add an E/W-table fixture where one board is `MAKE`, one is `SET`, and one also loses a small slam; assert the projected `ew_results` objects preserve both dimensions.

- [ ] **Step 2: Run projection tests and verify RED**

```powershell
..\.venv\Scripts\python.exe -m unittest tests.test_iv_scanner -v
```

Expected: `groups` and grouped sibling assertions fail against the current flat `cases` projection.

- [ ] **Step 3: Implement a two-pass group projection**

In `project_report`:

1. Combine blocked, complete, and limit records.
2. Reclassify every complete record with `reclassify_analysis`.
3. Build compact pair records and per-board results with `board_result`.
4. Use explicit `coverage_cell` for new scans. For legacy scans with valid stored South HCP and named-suit shape, use `legacy:<south_hcp>:<S-H-D-C>` and ascending deal ID as pair order. If either value is missing or invalid and a cell cannot be inferred, retain the case in its own stable `legacy-fallback:<deal-id>` group; never raise or discard it. That group has one Pair, `actual_pair_count=1`, the report's normal `expected_pair_count`, and therefore `incomplete=True`.
5. Build groups with `expected_pair_count = budget.pairs_per_cell`.
6. Retain only groups with at least one nonempty pair category, while retaining every sibling within those groups.
7. Recalculate category counts and projected `summary.suspicious` from reclassified pairs.

Each group must contain `id`, `south_hcp`, `south_shape`, `warning_counts`, `actual_pair_count`, `expected_pair_count`, `incomplete`, and ordered `pairs`. Each pair must contain `pair_slot`, `status`, and the existing hand/auction/detail fields. Use `status` values `blocked`, `complete`, and `limit`; limit pairs have no fabricated contract or E/W results. Return `groups`, not a duplicate flat case collection. Recompute projected `counts`, `summary.suspicious`, and `wrong_game_rule=RULE_ID`. Keep `_json_safe` at the final response boundary.

- [ ] **Step 4: Run projection tests and verify GREEN**

```powershell
..\.venv\Scripts\python.exe -m unittest tests.test_iv_scanner -v
```

Expected: all tests pass, including strict `json.dumps(..., allow_nan=False)`.

- [ ] **Step 5: Check the existing large report through the projection**

```powershell
..\.venv\Scripts\python.exe -c "import json; from engine.iv_scanner import read_report; from engine.outcome_metrics import RULE_ID; r=read_report('iv-scan-daqiush_2over1-20261027T045900Z-7722eafd74c8.json'); assert r['wrong_game_rule']==RULE_ID; assert r['groups']; assert all(g['incomplete'] or len(g['pairs'])==10 for g in r['groups']); json.dumps(r, allow_nan=False); print(len(r['groups']), sum(len(g['pairs']) for g in r['groups']))"
```

Expected: the command succeeds; every returned full cell has ten pairs and no non-finite JSON values.

- [ ] **Step 6: Inspect the grouped-projection diff checkpoint**

```powershell
git diff --check -- backend/engine/iv_scanner.py backend/tests/test_iv_scanner.py
```

### Task 4: Keep resampling and standalone reports consistent

**Files:**
- Modify: `backend/engine/suspicious_resample.py:20-85`
- Modify: `backend/engine/block_report_viewer.py`
- Modify: `backend/engine/templates/block_report.html`
- Modify: `backend/engine/templates/suspicious_resample.html`
- Test: `backend/tests/test_suspicious_resample.py`
- Test: `backend/tests/test_suspicious_resample_viewer.py`
- Test: `backend/tests/test_block_report_viewer.py`

- [ ] **Step 1: Write failing cross-surface tests**

Replace odds-based expectations with direct completion ratios. Add boundary tests proving suspicious resampling uses `.60`, `.40`, and `.80`. Assert `resample_groups()` returns `wrong_game_rule: RULE_ID`, and `extend_ew_samples()` preserves that exact field after adding boards. Add renderer assertions that generated HTML contains “success probability ratio”, “SET > 60%”, and the new `RULE_ID`, and does not contain “odds ratio” or “Down > 50%”. Add an old-report renderer test that stale flags are reclassified before embedding; the metadata assertions must inspect Python report mappings directly, so a hard-coded template string cannot satisfy them.

- [ ] **Step 2: Run cross-surface tests and verify RED**

```powershell
..\.venv\Scripts\python.exe -m unittest tests.test_suspicious_resample tests.test_suspicious_resample_viewer tests.test_block_report_viewer -v
```

Expected: old threshold and wording assertions fail.

- [ ] **Step 3: Use the shared metric layer everywhere**

Remove local `.5` and odds assumptions from `suspicious_resample.py`; import the constants, ratio function, and classification helper. Make `resample_groups()` write `wrong_game_rule=RULE_ID` at report creation, and make `extend_ew_samples()` preserve that field unchanged while recomputing rates. Before `block_report_viewer` embeds a schema-v2 report, reclassify complete cases, rebuild `suspicious_cases`, and update the projected summary without changing the source mapping. Update both templates' labels and help text to describe completion probability ratio, SET above 60%, and best-other suppression at 40%.

- [ ] **Step 4: Run cross-surface tests and verify GREEN**

```powershell
..\.venv\Scripts\python.exe -m unittest tests.test_suspicious_resample tests.test_suspicious_resample_viewer tests.test_block_report_viewer -v
```

Expected: all tests pass and generated HTML contains only the new definitions.

- [ ] **Step 5: Inspect the report-semantics diff checkpoint**

```powershell
git diff --check -- backend/engine/suspicious_resample.py backend/engine/block_report_viewer.py backend/engine/templates/block_report.html backend/engine/templates/suspicious_resample.html backend/tests/test_suspicious_resample.py backend/tests/test_suspicious_resample_viewer.py backend/tests/test_block_report_viewer.py
```

### Task 5: Add frontend group filtering and Pair selection helpers

**Files:**
- Create: `frontend/src/lib/ivScanner.js`
- Create: `frontend/tests/iv_scanner.test.js`
- Modify: `frontend/src/components/IVScanner.js:1-170`

- [ ] **Step 1: Write failing pure frontend tests**

Test these exported functions with a two-group fixture:

```javascript
import {
  filterScannerGroups, pairBadges, selectPairForGroup,
} from '../src/lib/ivScanner.js';
```

Assert that a category or search match on one pair returns its entire group, default selection chooses the first matching pair, clean siblings remain selectable, and badges map exactly to `TD`, `SET`, `LOSE`, and `WRONG`. Add a test that multiple missed flags yield one LOSE badge.

Add assertions that a clean complete pair returns a visible `CLEAN` marker and a `status: 'limit'` pair returns `UNAVAILABLE`, never TD and never an E/W outcome.

- [ ] **Step 2: Run frontend tests and verify RED**

Run from `frontend/`:

```powershell
npm test
```

Expected: module-not-found failure for `src/lib/ivScanner.js`.

- [ ] **Step 3: Implement the pure UI helpers**

Create `frontend/src/lib/ivScanner.js` with no React dependency:

```javascript
export function pairBadges(pair) { ... }
export function pairMatches(pair, category, query) { ... }
export function filterScannerGroups(groups, category, query) { ... }
export function selectPairForGroup(group, category, query, preferredId) { ... }
```

`filterScannerGroups` returns complete group objects whenever any child matches. `selectPairForGroup` retains the preferred pair only within the current, unchanged filter/group context; otherwise it selects the first child matching the active filter, the first warned child, then the first child.

`pairBadges` returns `UNAVAILABLE` first for a limit pair, the exact aggregate warning mapping for warned pairs, and `CLEAN` for a warning-free complete pair. It never maps a limit pair to TD.

- [ ] **Step 4: Replace component-local flat grouping**

Import the helpers in `IVScanner.js`. Remove `nsCellKey` and `groupCasesByNsCell`. Read `report.groups`, track selected group ID and pair ID separately, and derive the selected pair through the helper. Treat `(selectedGroupId, category, query)` as the automatic-selection context: whenever any of those changes, discard the stale selection left in UI state from the preceding context and select the first Pair matching the new context. This is not a legacy/new-report distinction. A later click may select any sibling, including a clean sibling that does not itself match the active category, until the context changes again. Add component/helper tests that switch category, search, and group and verify this reset behavior. Update labels to `SET > 60%` and `chosen / best-other success ratio < 0.8`; display the metric prefix as `RATIO`, not `OR`.

- [ ] **Step 5: Run frontend tests and verify GREEN**

Run from `frontend/`:

```powershell
npm test
```

Expected: all Node tests pass.

- [ ] **Step 6: Inspect the UI-data diff checkpoint**

```powershell
git diff --check -- frontend/src/lib/ivScanner.js frontend/tests/iv_scanner.test.js frontend/src/components/IVScanner.js
node --check tests/iv_scanner.test.js
```

The Node test/import check directly covers the new untracked helper and test file.

### Task 6: Build the selected vertical Pair rail

**Files:**
- Modify: `frontend/src/components/IVScanner.js:90-360`
- Modify: `frontend/src/styles/app.css:1690-1810`
- Modify: `frontend/tests/iv_scanner.browser.cjs`
- Create: `frontend/tests/fixtures/iv_scanner_grouped_report.json`
- Create: `frontend/tests/iv_scanner_pairs.browser.cjs`

- [ ] **Step 1: Update the browser test before the UI**

Create a deterministic grouped-report fixture containing two actionable cells, ten pairs in each, two distinct auctions/hands, a clean pair, a limit pair, all four warning badges, and MAKE/SET/LOSE E/W results. Create `iv_scanner_pairs.browser.cjs` that intercepts `/api/scanner/reports`, `/api/scanner/reports/<fixture-id>`, and `/api/scanner/runs/current`, returning this fixture without starting a scan. Assert ten `.iv-pair-button` elements for the selected cell, click two pairs with distinct IDs/auctions, and verify `.iv-hands` and `.iv-auction-rows` both change. Switch category, search, and sampling cell in turn and assert the selected Pair resets to the first matching sibling; then manually select a clean sibling and assert it remains visible until the filter/group context changes. Assert exact rail badges, CLEAN and UNAVAILABLE states, absence of fabricated limit outcomes, and result cells with primary MAKE/SET plus optional LOSE/accessibility label. Assert the category count is a pair count while the list header reports matching cells.

Update the existing `iv_scanner.browser.cjs` only for new wording and response shape; keep its live background-scan coverage separate from the deterministic Pair-rail test.

- [ ] **Step 2: Start the local services in a persistent PTY, wait for readiness, then verify RED**

From the repository root, launch `restart.cmd` in its own long-running interactive terminal/tool session and keep that session open:

```powershell
.\restart.cmd --no-browser
```

The launcher waits for input, so do **not** append the readiness loop to that command and do not start it as a detached process without stdin. The executor must allocate a PTY, retain the returned running-session ID, and run the following readiness check in a second PowerShell/tool call:

```powershell
$deadline = (Get-Date).AddSeconds(60)
do { try { $ready = (Invoke-WebRequest -UseBasicParsing http://127.0.0.1:5173/ -TimeoutSec 2).StatusCode -eq 200 } catch { $ready = $false }; if (-not $ready) { Start-Sleep -Milliseconds 500 } } while (-not $ready -and (Get-Date) -lt $deadline)
if (-not $ready) { throw 'frontend did not become ready on port 5173' }
```

Then run from `frontend/` in that second session/call:

Run from `frontend/`:

```powershell
node tests/iv_scanner_pairs.browser.cjs
```

Expected: selectors for the Pair rail are absent.

- [ ] **Step 3: Implement the three-part inspection layout**

Keep the existing sampling-cell list at the left. Inside the right detail area, add:

```text
.iv-pair-workspace
  .iv-pair-rail
    button.iv-pair-button × pairs_per_cell
  .iv-pair-detail
```

Each button shows pair slot/deal ID, compact auction, and badges. Use `aria-pressed`, visible focus, and a selected accent. Render only the selected pair's hands, exact auction, diagnostics, warnings, and one-row E/W result matrix. Render MAKE/SET as the primary cell status and LOSE as a secondary marker with the highest missed target in its accessible label.

- [ ] **Step 4: Style desktop and narrow-screen layouts**

Use a restrained bridge-table visual language already present in `app.css`: deep green selected state, pale green surfaces, tabular deal IDs, and compact warning chips. Make the pair rail sticky and independently scrollable on desktop. At the existing narrow breakpoint, switch it to a horizontal scrolling row above the detail pane. Avoid rendering or hiding sibling buttons based on active category/search.

- [ ] **Step 5: Run browser and frontend tests and verify GREEN**

Run from `frontend/`:

```powershell
npm test
node tests/iv_scanner_pairs.browser.cjs
node tests/iv_scanner.browser.cjs
```

Expected: all frontend tests pass; the browser test confirms ten selectable pairs and synchronized hand/auction updates.

- [ ] **Step 6: Inspect the Pair-rail diff checkpoint**

```powershell
git diff --check -- frontend/src/components/IVScanner.js frontend/src/styles/app.css frontend/tests/iv_scanner.browser.cjs frontend/tests/iv_scanner_pairs.browser.cjs frontend/tests/fixtures/iv_scanner_grouped_report.json
node --check tests/iv_scanner_pairs.browser.cjs
node -e "JSON.parse(require('fs').readFileSync('tests/fixtures/iv_scanner_grouped_report.json','utf8')); console.log('fixture ok')"
```

The final two commands directly validate the new untracked browser test and fixture.

### Task 7: Verify the existing report and live application

**Files:**
- Modify only if needed by failures in the files named above.
- Generated artifact: `reports/block_scans/iv-scan-daqiush_2over1-20261027T045900Z-7722eafd74c8.html`

- [ ] **Step 1: Run focused backend suites**

```powershell
cd backend
..\.venv\Scripts\python.exe -m unittest tests.test_outcome_metrics tests.test_coverage_scan tests.test_iv_scanner tests.test_suspicious_resample tests.test_suspicious_resample_viewer tests.test_block_report_viewer -v
```

Expected: all focused backend tests pass.

- [ ] **Step 2: Run the full frontend suite**

```powershell
cd ..\frontend
npm test
node tests/iv_scanner_pairs.browser.cjs
node tests/iv_scanner.browser.cjs
```

Expected: all Node and browser tests pass without page errors.

- [ ] **Step 3: Regenerate the current standalone HTML report**

Run from `backend/`:

```powershell
..\.venv\Scripts\python.exe -m engine.block_report_viewer ..\reports\block_scans\iv-scan-daqiush_2over1-20261027T045900Z-7722eafd74c8.json
Select-String -Path ..\reports\block_scans\iv-scan-daqiush_2over1-20261027T045900Z-7722eafd74c8.html -Pattern 'odds ratio|赔率比'
```

Expected: the HTML timestamp is refreshed and `Select-String` returns no matches.

- [ ] **Step 4: Restart in the persistent PTY and exercise the live API**

Stop the persistent launcher from Task 6 cleanly by sending Enter to its PTY, then relaunch it from the repository root in that same interactive PTY and leave it running:

```powershell
.\restart.cmd --no-browser
```

In a separate PowerShell/tool call, repeat Task 6's 60-second readiness check. After both ports are ready, run:

```powershell
node -e "const RULE='success_probability_ratio_0.8_best_above_0.4_set_above_0.6'; fetch('http://127.0.0.1:8765/api/scanner/reports/iv-scan-daqiush_2over1-20261027T045900Z-7722eafd74c8.json').then(r=>r.json()).then(x=>{if(x.wrong_game_rule!==RULE||!x.groups.length||x.groups.some(g=>!g.incomplete&&g.pairs.length!==10))process.exit(2);console.log(x.wrong_game_rule,x.groups.length)})"
```

Expected: the new rule identifier and a positive group count; exit code zero.

- [ ] **Step 5: Manual acceptance check**

Open IV Scanner, select a cell, then select two N/S Pairs whose auctions differ. Confirm hands and auction change together; the Pair rail still shows all ten siblings; result cells say MAKE or SET and add LOSE only for a missed higher target; category/search filters retain all siblings in a matched cell.

- [ ] **Step 6: Inspect the final diff and commit any verification-only adjustments**

```powershell
git diff --check
git status --short
```

Expected: no whitespace errors; unrelated user changes remain untouched. Do not commit from this dirty working tree.

- [ ] **Step 7: Run full backend discovery as a regression audit**

Run from `backend/`:

```powershell
..\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
```

Expected: exactly the following pre-implementation baseline failures and no others (baseline captured 2026-10-27; 333 tests, 8 failures):

```text
FixtureBiddingTests.test_bidding_cases [meow_weak_five_hearts_transfers_over_one_notrump]
FixtureBiddingTests.test_bidding_cases [meow_non_invitational_five_hearts_passes_one_notrump]
FixtureBiddingTests.test_bidding_cases [meow_heart_any_help_response_shows_spades]
FixtureBiddingTests.test_bidding_cases [meow_spade_transfer_over_one_notrump]
FixtureFullAuctionTests.test_full_auction_cases [meow_spade_help_suit_game_try_reaches_game]
FixtureFullAuctionTests.test_full_auction_cases [meow_heart_any_help_game_try_reaches_game]
FixtureFullAuctionTests.test_full_auction_cases [meow_forcing_notrump_invite_is_accepted]
FixtureFullAuctionTests.test_full_auction_cases [meow_bergen_limit_raise_accepts_game]
```

Capture the final output and compare the failing subtest case names exactly; do not treat any additional failure as part of the baseline.
