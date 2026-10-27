# IV Scanner Complete Opener Coverage Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give IV Scanner equal-quota coverage of every legal Daqiush 1NT opener shape while drawing each fixed-shape N/S partnership from its true conditional card-combination distribution.

**Architecture:** Add a deterministic North-stratum scheduler and a joint completion-count sampler that tracks both hands' shape, HCP, exact K–R units, and opening-quality state. Integrate them into new scans and explicit-cell extension, expose exact North coverage metadata, and preserve a labelled legacy path for old reports.

**Tech Stack:** Python 3.11 standard library (`dataclasses`, `functools`, `hashlib`, arbitrary-precision integers), existing BSL profile loader, `unittest`.

**Design reference:** `docs/superpowers/specs/2026-10-27-iv-scanner-opener-coverage-design.md`

**Working-tree note:** The repository already contains overlapping staged, unstaged, and untracked user work, including `coverage_scan.py`, `coverage_extend.py`, IV Scanner projection, report templates, and frontend files. Preserve those changes. Do not reset, replace whole files, stage broad paths, or create intermediate commits. Use scoped tests and diffs; the user will decide the final combined commit after review.

**Command convention:** Every command block is standalone and begins in the repository root. Backend commands explicitly `Push-Location backend` and always `Pop-Location`. Git/path checks run only after returning to root. For new untracked files, use `py_compile`, direct reads, and explicit trailing-whitespace scans; do not alter the existing index with intent-to-add.

**Latest observed backend baseline (2026-10-27):** `340` tests, exactly `4` failures. Re-capture the complete FAIL-or-ERROR identity set immediately before implementation because the dirty workspace is active; final regression means `after_issue_ids - before_issue_ids == empty`, so an old issue disappearing is allowed.

```text
DaqiushOpeningTests.test_missing_continuations_and_competition_block
DaqiushResampleFollowupTests.test_six_five_major_minor_values_second_suit
DaqiushResampleFollowupTests.test_six_five_spade_minor_also_values_second_suit
TrainingDealTests.test_daqiush_texas_response_is_selected_for_both_partnership_directions [opener='n']
```

---

## Chunk 1: Strata, weighted joint sampling, and scan integration

### Task 0: Capture the live dirty-worktree and regression baseline

**Files:**
- Modify: none

- [ ] **Step 1: Save the current workspace status outside the repository**

Run from repository root:

```powershell
git status --short | Set-Content "$env:TEMP\gible-opener-coverage-status-before.txt"
Get-Content "$env:TEMP\gible-opener-coverage-status-before.txt"
```

This is the preservation checklist. Do not remove or overwrite entries outside the authorized files named by this plan.

- [ ] **Step 2: Capture machine-comparable backend failure IDs**

```powershell
Push-Location backend
$output = & ..\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py" 2>&1
$exitCode = $LASTEXITCODE
$output | Tee-Object "$env:TEMP\gible-opener-coverage-tests-before.txt"
$issues = @($output | Where-Object { $_ -match '^(FAIL|ERROR): (.+)$' } |
    ForEach-Object { if ($_ -match '^(FAIL|ERROR): (.+)$') { $Matches[2] } } |
    Sort-Object -Unique)
Set-Content "$env:TEMP\gible-opener-coverage-issues-before.txt" -Value $issues
@("python_exit=$exitCode") + ($output | Select-Object -Last 8) |
    Set-Content "$env:TEMP\gible-opener-coverage-result-before.txt"
Pop-Location
```

Expected at plan-writing time: 340 tests and the four issue IDs listed in the header. If the live set differs, the captured file becomes authoritative and the discrepancy is reported before implementation continues. Preserve the exit/result file as evidence; a new import or setup `ERROR` is part of the regression set, not an ignorable runner detail.

### Task 1: Define and allocate the 92 opener strata

**Files:**
- Create: `backend/engine/opener_coverage.py`
- Create: `backend/tests/test_opener_coverage.py`

- [ ] **Step 1: Write failing shape-enumeration tests**

Create tests for this public API:

```python
from engine.opener_coverage import (
    OpenerStratum,
    allocate_opener_strata,
    normal_named_shapes,
    required_opener_strata,
    rotate_responder_shape,
    stratum_key,
    validate_cell_identity,
    validate_explicit_coverage_cell,
)
```

Assert `normal_named_shapes()` returns 68 unique S/H/D/C tuples with exact family counts:

```python
{
    (4, 3, 3, 3): 4,
    (4, 4, 3, 2): 12,
    (5, 3, 3, 2): 12,
    (6, 3, 2, 2): 6,
    (5, 4, 2, 2): 10,
    (4, 4, 4, 1): 4,
    (5, 4, 3, 1): 20,
}
```

Every shape must sum to 13, have no six-card major, and have no `5+M/4+oM`. Assert `required_opener_strata()` contains 68 `normal`, 12 `upgrade_14`, and 12 `soft_18` strata in stable order.

Also test two deliberately separate validators here, before extension or projection needs them:

- `validate_cell_identity` accepts exactly `{target_hcp, base_shape_index}` and rejects extra keys;
- `validate_explicit_coverage_cell` accepts the full case object with required `base_shape`, `pair_slot`, `opener_shape`, and `opener_mode`, while validating its two-key identity and the consistency of sibling cases.

Booleans, missing fields, unknown modes, malformed shapes, and inconsistent sibling metadata fail with a field-specific `ValueError`.

Assert `rotate_responder_shape(base_shape, target_hcp, base_shape_index)` rotates left by `(target_hcp + base_shape_index) % 4`; schedule construction and zero-case extension must share this helper.

- [ ] **Step 2: Write failing quota-boundary tests**

Build synthetic South cell identities `(hcp, base_shape_index)` and test:

- 24 cells: accepted, `complete=False`, 68 omitted strata;
- 91 cells: accepted, `complete=False`, one omitted stratum;
- 92 cells: every required stratum exactly once and `complete=True`;
- 529 cells: every exceptional stratum once; every normal shape seven or eight times;
- changing the run seed does not change cell-to-stratum assignment;
- changing only execution order does not change assignments;
- the same South cells in a different input order produce the same mapping.
- every selected North/South assignment has per-suit length sum at most 13;
- all 529 default cells receive a compatible assignment with quota preserved.

The return object must include `assignments`, `required_cells`, `available_cells`, `complete`, and structured `ungenerated_strata`.

- [ ] **Step 3: Run the tests and verify RED**

Run from `backend/`:

```powershell
Push-Location backend
..\.venv\Scripts\python.exe -m unittest tests.test_opener_coverage -v
Pop-Location
```

Expected: import failure for `engine.opener_coverage`.

- [ ] **Step 4: Implement immutable strata and the stable allocator**

Use this data model:

```python
@dataclass(frozen=True, order=True)
class OpenerStratum:
    shape: tuple[int, int, int, int]
    mode: str  # normal | upgrade_14 | soft_18

def stratum_key(item: OpenerStratum) -> str:
    return f"{item.mode}:{'-'.join(map(str, item.shape))}"
```

Generate permutations rather than maintaining a handwritten list. Filter with the two structural opening restrictions. Build the 92-item base sequence by merging the normal and exceptional pools using normalized rank and integer cross multiplication. Turn the selected prefix/full-plus-normal-round-robin sequence into quota slots.

Build a bipartite graph from quota slots to South cells. At minimum, an edge requires all four named-suit sums to be at most 13 and compatible combined HCP bounds. Order slots by ascending degree, then stratum key and occurrence; order neighbor cells by SHA-256 of:

```text
north-stratum-v1:<south-hcp>:<south-base-shape-index>
```

Run a deterministic augmenting-path maximum matching. Do not use Python's process-randomized `hash()` and do not accept the scan seed in the allocator. A failed perfect matching raises a typed allocation error containing `available_cells`, `required_cells`, and unmatched slots.

Implement the explicit metadata validator in this module so scan, extension, outcome cell keys, IV projection, and viewer can share it in later tasks.

- [ ] **Step 5: Run tests and verify GREEN**

Run from repository root:

```powershell
Push-Location backend
..\.venv\Scripts\python.exe -m unittest tests.test_opener_coverage -v
..\.venv\Scripts\python.exe -m py_compile engine/opener_coverage.py
Pop-Location
```

Expected: all opener-stratum tests pass.

- [ ] **Step 6: Inspect the scoped diff**

Run from repository root:

```powershell
$newFiles = @('backend/engine/opener_coverage.py', 'backend/tests/test_opener_coverage.py')
$bad = Select-String -Path $newFiles -Pattern '[ \t]+$'
if ($bad) { $bad; throw 'trailing whitespace in new files' }
Get-Content -Raw $newFiles | Out-Null
```

The direct read/compile checks cover the new untracked file, which ordinary `git diff` does not display.

### Task 2: Build the joint completion-count sampler

**Files:**
- Create: `backend/engine/joint_deal_sampler.py`
- Modify: `backend/engine/constrained_deals.py:20-115`
- Create: `backend/tests/test_joint_deal_sampler.py`
- Modify: `backend/tests/test_constrained_deals.py`

- [ ] **Step 1: Write failing low-level count and weighting tests**

Test these focused interfaces:

```python
from engine.joint_deal_sampler import (
    JointConstraintError,
    JointPartnershipPlan,
    OpenerModeConstraints,
    sample_conditioned_partnership,
)
```

Add a small exact suit-bucket fixture using three ranks and one card per hand. Assert it has six concrete ordered N/S allocations, grouped bucket weights sum to six, and deterministic boundary RNG draws select branches in direct proportion to their completion counts. Do not use a statistical frequency assertion.

Enumerate every integer draw boundary in that fixture. Assert each of the six concrete ordered N/S assignments appears exactly once across draws `0..5`; this proves bucket grouping does not make honor structures equiprobable.

Add a multi-layer fixture whose total completion count exceeds `2**63`; assert the exact Python integer remains positive and unchanged after cache reuse.

- [ ] **Step 2: Write failing full-deck sampler tests**

For representative `normal`, `upgrade_14`, and `soft_18` constraints, draw repeatable partnerships and assert:

- N/S each have 13 unique cards and no overlap;
- exact named shapes;
- exact South HCP;
- normal North has 15–17 HCP, upgrade has 14, soft-18 has 18;
- the real `opening_assessment` accepts every North hand;
- soft 18 contains a QJ doubleton;
- an honor singleton is Q/K/A;
- K–R bounds and dynamic cell envelopes are obeyed;
- cold and warm caches return identical cards for the same seed.

Construct an impossible constraint and assert immediate `JointConstraintError` containing North shape/mode, South shape/HCP, requested K–R envelopes, and `completion_count=0`. Assert there is no random-deal fallback.

Inject an authored invariant callback that rejects a hand already admitted by the counted target states. Assert one immediate `JointConstraintError` includes the failed predicate/result plus all North/South constraints and completion count, and assert there is no retry or RNG fallback.

- [ ] **Step 3: Verify RED**

```powershell
Push-Location backend
..\.venv\Scripts\python.exe -m unittest tests.test_joint_deal_sampler tests.test_constrained_deals -v
Pop-Location
```

Expected: missing module/API failures.

- [ ] **Step 4: Share exact K–R unit conversion**

In `constrained_deals.py`, promote the existing fixed shape adjustment into a small public helper:

```python
def kr_shape_adjustment_units(shape) -> int:
    return -10 if sorted(shape) == [3, 3, 3, 4] else -20
```

Keep `_HandPlan` behavior unchanged and add a regression test proving its existing target counts and seeded sample remain unchanged.

- [ ] **Step 5: Implement joint suit buckets and DP layers**

For each suit and required `(north_length, south_length)`, enumerate every North combination and every South combination from the remaining ranks. Group concrete `(north_combo, south_combo)` pairs by:

```text
(north_hcp, north_kr_units, south_hcp, south_kr_units, feature_bits)
```

Feature bits cover QJ doubleton and honor-singleton requirements. Cache immutable suit buckets by suit/length/feature requirements. Build four DP layers whose values are arbitrary-precision completion counts. Prune states outside the maximum HCP/K–R envelopes.

At the target layer, retain only states satisfying:

- South exact HCP and current aggregate South K–R envelope;
- normal North HCP 15–17;
- upgrade North HCP 14 and K–R at least 15;
- soft-18 North HCP 18, K–R at most 16, and QJ-doubleton flag;
- 17-point five-major K–R strictly below 17;
- `5M4m22`: `KR - HCP <= -1.5`;
- `5M4m31`: `KR - HCP <= -0.5`;
- current aggregate North K–R envelope.

Select the final target state with weight equal to its completion count. Walk layers backward using `prior_count * concrete_bucket_count` as the branch weight. After selecting a grouped bucket, select each concrete `(north_holding, south_holding)` pair uniformly inside that bucket. Canonicalize target states, prior states, grouped buckets, and concrete holdings before drawing. Together these three weighted choices are the executable joint-uniformity contract.

- [ ] **Step 6: Add the authored invariant and E/W completion**

`sample_conditioned_partnership` creates `Hand` objects, calls the passed authored `opening_assessment`, and raises `JointConstraintError` if the result is not eligible. This is an invariant failure, not a retry. Then use the existing `complete_opponents` behavior to shuffle the remaining 26 cards between E/W.

Do not import `coverage_scan` from the sampler; accept an E/W completion callback or return N/S so the caller avoids a dependency cycle.

- [ ] **Step 7: Verify GREEN and performance**

```powershell
Push-Location backend
..\.venv\Scripts\python.exe -m unittest tests.test_joint_deal_sampler tests.test_constrained_deals -v
..\.venv\Scripts\python.exe -m py_compile engine/joint_deal_sampler.py engine/constrained_deals.py
Pop-Location
```

Add a separately named benchmark-style unittest that generates ten partnerships for the hardest known `5-2-4-2` normal stratum with a compatible South constraint and asserts elapsed time below 30 seconds. It must remain deterministic and must not call DDS.

Add a full-default feasibility test that builds the 529 compatible assignments from Task 1 and constructs each exact joint plan without drawing cards. Assert every `plan.total > 0`. This test may take longer than the sub-second pure allocator test, but it must not run bidding or DDS.

If this exact counter exposes a zero-completion allocation, loop back rather than weakening the assertion or adding sampler retry: add the concrete incompatibility as a RED allocator test in `test_opener_coverage.py`, extend the isolated hard-compatibility edge predicate in `opener_coverage.py`, rerun all Task 1 allocation/quota tests, and then rerun all 529 plan-count checks. These two Task 1 files are explicitly authorized for that focused loop-back.

- [ ] **Step 8: Inspect the sampler diff**

```powershell
$newFiles = @('backend/engine/joint_deal_sampler.py', 'backend/tests/test_joint_deal_sampler.py')
$bad = Select-String -Path $newFiles -Pattern '[ \t]+$'
if ($bad) { $bad; throw 'trailing whitespace in new files' }
git diff --check -- backend/engine/constrained_deals.py backend/tests/test_constrained_deals.py
```

### Task 3: Integrate strata and joint sampling into coverage scans

**Files:**
- Modify: `backend/engine/coverage_scan.py:35-365`
- Modify: `backend/tests/test_coverage_scan.py`

- [ ] **Step 1: Write failing schedule and metadata tests**

Add tests that construct the full 529-cell schedule without running auctions or DDS and assert:

- all 68 normal shapes occur;
- all 24 exceptional strata occur;
- normal cell quotas are seven or eight;
- no `south_hcp > 19 => North 4333` shortcut remains;
- assignment is completed before seeded execution-order shuffle.

For a one-cell partial scan, assert `coverage.north.complete=False`, `required_cells=92`, `available_cells=1`, and 91 structured omissions.

Add exact schema fixtures for 24, 91, and 92 cells. Assert `requested_strata` preserves stable cell order and repeated normal occurrences; `observed_strata` is distinct and ordered by the required-stratum sequence; `cell_counts` and `pair_counts` contain all 92 stable keys including zero values; omissions use the common cell object or `null` and exact `reason="insufficient_cells"`.

- [ ] **Step 2: Write failing generated-deal integration tests**

Run small targeted cell sets with a fake auction/DDS boundary where appropriate. Assert every emitted blocked/complete/limit case has:

```python
case['coverage_cell']['opener_shape']
case['coverage_cell']['opener_mode']
```

and that the values match `north_shape` and the generated North HCP/quality. Across targeted normal five-heart, five-spade, and no-five-major strata, call `choose_bid(profile, Auction.parse('1NP3CP'), north)` and assert `3H`, `3S`, and `3D` are all present.

Add a multi-pair cell test that checks the running min/max K–R span for both N and S never exceeds two; do not merely compare each pair with the first pair.

Inject one zero-completion/generation failure after some pair slots have succeeded. Assert the scan continues, persists `cell_failures` with the exact `{target_hcp, base_shape_index}` object and missing slots, marks the requested stratum `partial`, derives a generation-error omission, increments `summary.generation_errors`, and returns a partial report without fallback. Add the zero-case variant with requested status `failed`.

- [ ] **Step 3: Verify RED**

```powershell
Push-Location backend
..\.venv\Scripts\python.exe -m unittest tests.test_coverage_scan -v
Pop-Location
```

Expected: opener scheduling/metadata/coverage-summary assertions fail.

- [ ] **Step 4: Separate schedule construction from execution**

Add a pure `build_coverage_schedule(hcp_targets, shapes, pairs_per_cell)` that:

1. builds stable South cells;
2. calls `allocate_opener_strata` exactly once with the complete South-cell list;
3. expands the returned global cell-to-stratum mapping over every pair slot;
4. returns allocation metadata;
5. leaves seeded shuffling to `scan_coverage` after construction.

This function must not load a profile, draw cards, run bidding, or call DDS.

- [ ] **Step 5: Replace fixed opener sampling**

Remove `OPENING_SHAPES` and the arithmetic `opener_shape/opener_hcp` choice from the scan loop. Use `sample_conditioned_partnership` with the scheduled stratum, South exact HCP/rotated shape, and the current aggregate K–R envelopes.

Maintain each cell's observed min/max North and South K–R. Before adding a later pair, calculate allowable new ranges that keep `new_max - new_min <= 2`. Update envelopes only after a pair is accepted.

Keep `_sample_hand` or the old `sample_partnership` only if another public/legacy caller still needs it; label it legacy and do not route new explicit scans through it.

- [ ] **Step 6: Emit exact North coverage summaries**

Use a shared summary builder in `opener_coverage.py` to populate `coverage.north` with the exact schema from the design. Count scheduled cells separately from generated pairs. If an assigned cell fails, store or update its authoritative `cell_failures` record, skip only its missing slots, continue other cells, and return a visibly partial report; never re-raise after report construction and never substitute another stratum.

- [ ] **Step 7: Verify GREEN**

```powershell
Push-Location backend
..\.venv\Scripts\python.exe -m unittest tests.test_opener_coverage tests.test_joint_deal_sampler tests.test_coverage_scan -v
Pop-Location
```

Expected: all strata, sampler, scan metadata, K–R span, and 3D/3H/3S tests pass.

- [ ] **Step 8: Inspect the scan diff**

```powershell
git diff --check -- backend/engine/coverage_scan.py backend/tests/test_coverage_scan.py
```

## Chunk 2: Extension, readers, and end-to-end verification

### Task 4: Make explicit-cell extension use the same joint sampler

**Files:**
- Modify: `backend/engine/coverage_extend.py`
- Modify: `backend/tests/test_coverage_extend.py`

- [ ] **Step 1: Write failing explicit-extension tests**

Create an explicit normal cell whose first North hand has 15 HCP. Extend it with seeded samples and assert the sampler receives mode `normal` with range 15–17, not fixed HCP 15. Add tests for `upgrade_14` and `soft_18` reconstruction.

For every explicit cell, assert all stored cases agree on `opener_shape`, `opener_mode`, South shape, and South target HCP. Conflicting metadata must raise `ValueError` naming the cell and fields rather than silently trusting the first pair.

Add tests that both `extend_ns_pairs` and `extend_process_pairs` call the joint sampler for explicit cells, while a legacy cell without North metadata still follows the old sampler and remains labelled legacy.

Add zero-case and partial `cell_failures` fixtures. Extension must discover them from the persisted requested schedule even when no case exists, retry exactly `missing_pair_slots`, remove the failure after full success, or preserve it with the new reason after another failure.

Test zero-case recovery separately for both scopes. Both run a common missing-sampling-slot repair pre-pass. In process scope, the recovered case is retained, its auction creates the initially absent process group, and only subsequent exploratory discovery is governed by `allow_new_processes`; the switch must not suppress authoritative failure repair.

- [ ] **Step 2: Write failing span and summary tests**

Extend a cell whose existing K–R values already span nearly two points. For both `extend_ns_pairs` and `extend_process_pairs`, add multiple pairs and assert each successive sampler envelope is exactly:

```text
new_kr >= existing_max - 2
new_kr <= existing_min + 2
```

for North and South, followed by a final aggregate span no greater than two.

After extension, assert every North summary field is recomputed from requested schedule + all cases + remaining failures: requested statuses, stable/deduplicated `observed_strata`, complete 92-key `cell_counts`, complete 92-key `pair_counts`, `hcp_by_mode`, `cell_failures`, derived `ungenerated_strata`, `complete`, `required_cells`, and `available_cells`. Cover a partial scan with `insufficient_cells`, a successfully cleared failure, and a still-failing assigned cell with its concrete reason.

- [ ] **Step 3: Verify RED**

```powershell
Push-Location backend
..\.venv\Scripts\python.exe -m unittest tests.test_coverage_extend -v
Pop-Location
```

Expected: exact-HCP pinning, old sampler calls, or missing summary assertions fail.

- [ ] **Step 4: Refactor cell specifications by schema status**

Replace the single `_cell_spec` assumption with explicit and legacy variants. For cells with cases, the explicit variant validates full `coverage_cell` metadata and consistency against the requested record. For a zero-case cell, reconstruct South constraints from authoritative data: validate `filters.shapes`, look up `filters.shapes[base_shape_index]`, rotate the base shape left by `(target_hcp + base_shape_index) % 4` (the same shared helper used by schedule construction), use exact `target_hcp`, and recover North shape/mode from `requested_strata`. It never derives a normal-mode HCP range from a first hand. Missing/malformed filters or disagreement with existing cases raises a field-specific `ValueError`; do not guess or fall back to legacy sampling.

Use one internal sampling helper and one missing-slot repair pre-pass from both extension scopes so their semantics cannot diverge. Process extension treats repair-generated auctions as real discovered process groups before ordinary process top-up.

- [ ] **Step 5: Recompute North coverage after extension**

Call the shared summary builder over all blocked/complete/limit records after additions. Preserve `schema_status="legacy"` for an old report even if actual hand shapes are present; never invent modes.

- [ ] **Step 6: Verify GREEN**

```powershell
Push-Location backend
..\.venv\Scripts\python.exe -m unittest tests.test_coverage_extend tests.test_coverage_scan -v
Pop-Location
```

Expected: all extension and scan tests pass.

- [ ] **Step 7: Inspect the extension diff**

```powershell
$files = @('backend/engine/coverage_extend.py', 'backend/tests/test_coverage_extend.py')
$bad = Select-String -Path $files -Pattern '[ \t]+$'
if ($bad) { $bad; throw 'trailing whitespace in extension files' }
git diff --check -- $files
```

### Task 5: Preserve North coverage through IV Scanner and reports

**Files:**
- Modify: `backend/engine/iv_scanner.py:80-315`
- Modify: `backend/engine/outcome_metrics.py:120-185`
- Modify: `backend/engine/block_report_viewer.py`
- Modify: `backend/tests/test_iv_scanner.py`
- Modify: `backend/tests/test_block_report_viewer.py`
- Modify: `docs/18_block_scout.md`

- [ ] **Step 1: Write failing projection and legacy tests**

For an explicit report, assert every projected group contains `opener_shape` and `opener_mode`, every pair retains the full `coverage_cell`, and the top-level response retains `coverage.north` unchanged except for strict JSON normalization.

Assert the exact contract: requested records use `{shape, mode, cell, status}` with cell `{target_hcp, base_shape_index}`; observed strata are deduplicated in required-stratum order; both count mappings contain all 92 keys; 24/91-cell omissions retain stable order and exact `insufficient_cells`; generation failures retain their cell and concrete reason. A malformed sibling disagreement makes the report invalid instead of silently choosing the first case.

For a legacy report with no North-stratum metadata, assert:

```python
projected['coverage']['north']['schema_status'] == 'legacy'
```

and assert no requested/observed strata or modes are inferred from actual hidden hands. Malformed explicit metadata must make only that report unreadable/list-skipped under the existing safe-reader behavior.

- [ ] **Step 2: Verify RED**

```powershell
Push-Location backend
..\.venv\Scripts\python.exe -m unittest tests.test_iv_scanner tests.test_block_report_viewer -v
Pop-Location
```

Expected: missing group/pair/top-level metadata assertions fail.

- [ ] **Step 3: Centralize coverage-cell validation**

Move or add a shared validator in `opener_coverage.py` for explicit `opener_shape` and `opener_mode`. Make `case_cell_key`, IV projection, extension, and report rendering use it rather than maintaining different accepted forms.

Keep existing cell IDs stable for old reports. New explicit identity may continue to use the South cell ID because the schedule assigns exactly one North stratum per South cell; validate that all siblings agree before projecting.

- [ ] **Step 4: Project and document the metadata**

Copy North stratum fields to each IV group and preserve the complete cell object on pairs. Normalize absent old metadata to the exact legacy marker. Update `docs/18_block_scout.md` to explain 92-stratum completeness, partial Quick scans, equal shape quota versus within-shape conditional weighting, and the new coverage summary fields.

- [ ] **Step 5: Verify GREEN**

```powershell
Push-Location backend
..\.venv\Scripts\python.exe -m unittest tests.test_iv_scanner tests.test_block_report_viewer tests.test_coverage_extend -v
Pop-Location
```

Expected: explicit and legacy report tests pass.

- [ ] **Step 6: Inspect the reader/documentation diff**

```powershell
git diff --check -- backend/engine/iv_scanner.py backend/engine/outcome_metrics.py backend/engine/block_report_viewer.py backend/tests/test_iv_scanner.py backend/tests/test_block_report_viewer.py docs/18_block_scout.md
```

### Task 6: End-to-end verification and existing-report safety

**Files:**
- Modify only files named above if verification exposes an in-scope defect.

- [ ] **Step 1: Run the complete focused backend suite**

Run from `backend/`:

```powershell
Push-Location backend
..\.venv\Scripts\python.exe -m unittest tests.test_opener_coverage tests.test_joint_deal_sampler tests.test_constrained_deals tests.test_coverage_scan tests.test_coverage_extend tests.test_iv_scanner tests.test_block_report_viewer -v
Pop-Location
```

Expected: all focused tests pass.

- [ ] **Step 2: Verify a full 529-cell schedule without DDS**

Add or run a diagnostic entry point that constructs the schedule and prints only quota metadata. Assert:

```text
available_cells=529
required_cells=92
complete=true
normal_shapes=68
exceptional_strata=24
normal_cell_count_min=7
normal_cell_count_max=8
```

This check must finish below one second and must not load DDS.

Then construct the exact joint plan for every one of the 529 assignments without drawing cards. Assert all completion counts are positive and print the minimum-count cell/stratum. This second feasibility check is separate from the sub-second allocator check.

- [ ] **Step 3: Verify real five-major reply coverage**

Using generated North hands from the joint sampler and the loaded Daqiush profile, run the `1NP3CP` decision and assert the observed call set is exactly or at least:

```python
{'3D', '3H', '3S'}
```

Print one reproducible deal ID/seed for each answer.

- [ ] **Step 4: Verify the hardest sampler stratum**

Run the dedicated ten-pair `5M4m22` performance test alone and record elapsed time and completion count:

```powershell
Push-Location backend
..\.venv\Scripts\python.exe -m unittest tests.test_joint_deal_sampler.JointDealSamplerTests.test_hardest_soft_shape_generates_ten_pairs_within_budget -v
Pop-Location
```

Expected: pass in under 30 seconds with no rejection fallback.

- [ ] **Step 5: Read the existing large legacy report**

```powershell
Push-Location backend
..\.venv\Scripts\python.exe -c "from engine.iv_scanner import read_report; r=read_report('iv-scan-daqiush_2over1-20261027T045900Z-7722eafd74c8.json'); assert r['coverage']['north']['schema_status']=='legacy'; print(len(r['groups']))"
Pop-Location
```

Expected: the historical report remains readable; no opener mode is invented.

- [ ] **Step 6: Run strict syntax and JSON checks**

```powershell
Push-Location backend
..\.venv\Scripts\python.exe -m py_compile engine/opener_coverage.py engine/joint_deal_sampler.py engine/coverage_scan.py engine/coverage_extend.py engine/iv_scanner.py
Pop-Location
git diff --check
git status --short
```

Expected: no syntax or whitespace errors; unrelated existing user changes remain present.

- [ ] **Step 7: Run full backend discovery and compare the exact baseline**

```powershell
Push-Location backend
$output = & ..\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py" 2>&1
$exitCode = $LASTEXITCODE
$output | Tee-Object "$env:TEMP\gible-opener-coverage-tests-after.txt"
$issues = @($output | Where-Object { $_ -match '^(FAIL|ERROR): (.+)$' } |
    ForEach-Object { if ($_ -match '^(FAIL|ERROR): (.+)$') { $Matches[2] } } |
    Sort-Object -Unique)
Set-Content "$env:TEMP\gible-opener-coverage-issues-after.txt" -Value $issues
@("python_exit=$exitCode") + ($output | Select-Object -Last 8) |
    Set-Content "$env:TEMP\gible-opener-coverage-result-after.txt"
Pop-Location
$newFailures = Compare-Object `
    @(Get-Content "$env:TEMP\gible-opener-coverage-issues-before.txt") `
    @(Get-Content "$env:TEMP\gible-opener-coverage-issues-after.txt") |
    Where-Object SideIndicator -eq '=>'
if ($newFailures) { $newFailures; throw 'new backend regression failures' }
Get-Content "$env:TEMP\gible-opener-coverage-result-before.txt"
Get-Content "$env:TEMP\gible-opener-coverage-result-after.txt"
```

Immediately before implementation, capture the full FAIL-or-ERROR identity set from a fresh run as `before_issue_ids`. After implementation capture `after_issue_ids` from this command. Expected: `after_issue_ids - before_issue_ids` is empty. Existing issues may disappear; comparing only counts, ignoring `ERROR`, or requiring old failures to persist is incorrect. Retain the process exit codes and final unittest summaries in the handoff evidence.

Compare the workspace preservation checklist:

```powershell
git status --short | Set-Content "$env:TEMP\gible-opener-coverage-status-after.txt"
Compare-Object `
    (Get-Content "$env:TEMP\gible-opener-coverage-status-before.txt") `
    (Get-Content "$env:TEMP\gible-opener-coverage-status-after.txt")
```

Every new or changed line must belong to an authorized plan path. Any disappearance or unexpected status change in a pre-existing unrelated path is a preservation failure.

- [ ] **Step 8: Perform a final requirements audit**

Read the design specification line by line and build an explicit 21-row matrix: verification item, test name/command, and observed evidence. Record schedule counts, focused test totals, minimum completion-count stratum, hardest-stratum elapsed time, extension failure-recovery result, legacy-read result, and before/after full-suite failure sets in the implementation handoff. Do not claim completion from agent reports alone.
