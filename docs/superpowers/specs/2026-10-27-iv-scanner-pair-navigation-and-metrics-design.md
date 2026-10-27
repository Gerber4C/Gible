# IV Scanner Pair Navigation and Outcome Metrics

Date: 2026-10-27

## Goal

Make an IV Scanner finding understandable at the level of one sampled North/South partnership while preserving the context of the ten partnerships generated in the same sampling cell. Replace the wrong-game odds ratio with a direct completion-probability ratio and raise the contract-failure threshold to 60%.

## Terms

- **Sampling cell:** one requested South HCP value plus one requested South shape. A full scan generates `pairs_per_cell` N/S partnerships in each cell; the normal full report uses ten.
- **N/S Pair:** one concrete North hand and South hand with its own automatic auction and contract.
- **Comparable class:** the existing DDS assessment class: both hands have identical shapes and each hand's HCP and K–R spans no more than two points. This remains the statistical population for completion rates and is independent of the sampling-cell grouping used for navigation.
- **Other game:** any of `3NT`, `4S`, `4H`, `5D`, or `5C`, excluding the selected contract.

## Report Data Projection

The scanner retains its full raw report. The browser-facing projection performs a two-pass transformation:

1. Project every raw case into a compact pair record, including clean pairs with no warning.
2. Group pair records by sampling cell.
3. Return only sampling cells containing at least one TD or suspicious pair, but include every N/S Pair from each returned cell.

Each projected pair record contains:

- stable deal ID and pair position within the cell;
- North and South hands, shapes, HCP, and K–R;
- the pair's actual calls and compact auction string;
- contract and declarer;
- its TD diagnostics or warning categories;
- E/W outcome samples and the computed assessment rates.

Each projected group contains a stable cell ID, its South HCP and shape, expected pair count, actual pair records, and aggregated warning counts. New scans should record cell identity and pair slot explicitly. Legacy scans derive them from the report filters and pair order so the existing report remains usable without being rerun.

For new scans, every scheduled case records `coverage_cell` with the target HCP,
unrotated base-shape index, unrotated base shape, and zero-based pair slot. Blocked,
complete, and call-limit cases are all retained in the raw report, so the cell rail
can account for every scheduled pair. A call-limit pair is shown as unavailable
for contract analysis with its captured hand and partial auction.

Legacy reports do not have this field. Their cell key is defined exactly as the
stored South HCP plus stored named-suit `south_shape`; this deliberately uses
the rotated shape rather than attempting to recover the original base shape.
The old generator applies one deterministic rotation to all replicates in a
cell, so its existing records group consistently. Pair order is ascending deal
ID and slot is its position in that group. If a legacy report omitted a
call-limit case, the API cannot recover its hand and shows the group as
incomplete rather than inventing a pair.

The projection must remain strict JSON: non-finite legacy numeric values become `null`.

## Pair Navigation UI

The selected layout is **B: vertical Pair rail**.

The findings list continues to select a sampling cell. The detail region then has two columns:

- A narrow, sticky vertical rail lists all N/S Pairs in that cell in pair-slot order. Each entry shows deal ID, compact auction, and aggregate warning badges mapped exactly as follows: `block` to `TD`, `contract_failure` to `SET`, every missed-game/slam flag to one `LOSE` badge, and `wrong_game` to `WRONG`. A clean pair is explicitly marked clean rather than omitted.
- The main detail pane shows only the selected pair: its exact North and South holdings, its exact auction by seat, TD diagnostics or warning calculations, and its E/W result strip.

Selecting a different rail entry replaces all detail-pane content with that pair's data. Selecting a group or category defaults to the first pair matching the active category; without a category filter it defaults to the first warned pair, then the first pair.

Category and text filters select sampling cells rather than deleting individual
rail entries. A cell matches a category when any pair carries that category. A
text search matches when any pair's deal ID, auction, or North/South holding
matches. After a cell matches, all of its siblings remain in the rail. The first
matching pair is selected by default. Category totals continue to count warned
pairs; the results header separately reports the number of matching sampling
cells, so pair counts and cell counts are never presented as the same measure.

The rail is a set of accessible buttons with a clear selected state and keyboard focus. It scrolls independently when necessary. On narrow screens it becomes a horizontally scrolling row above the detail pane.

The UI renders only the selected group's rail and selected pair detail. It does not create detailed DOM for every pair in the report, keeping the large report responsive.

### E/W Result Matrix Vocabulary

Each selected pair shows its E/W samples with bridge-specific labels:

- `MAKE`: the selected contract makes on that E/W completion;
- `SET`: the selected contract goes down on that E/W completion;
- `LOSE`: a higher target that the partnership did not bid can make on that
  completion.

The per-sample LOSE calculation uses the existing availability tests and is
independent of the aggregate 30% missed-warning threshold:

1. If the selected contract has not reached game and any `3NT`, `4S`, `4H`,
   `5D`, or `5C` game is available on the board, add LOSE.
2. If the selected contract is below level six and any strain can take twelve
   tricks from an N/S seat, add LOSE.
3. If the selected contract is below level seven and any strain can take
   thirteen tricks from an N/S seat, add LOSE.
4. Multiple satisfied checks still produce one LOSE marker; its accessible
   label lists the highest missed target (`game`, `small slam`, or `grand slam`).

Outcome and missed-target evidence are separate dimensions. A matrix cell has
one primary outcome (`MAKE` or `SET`) and may additionally carry a `LOSE`
marker. Thus `SET + LOSE` preserves both facts instead of hiding either one.
Blocked or call-limit pairs have no fabricated DDS outcome cells.

## Outcome Formulas

For a selected game, calculate over the existing comparable-class DDS boards:

```text
chosen_success = boards where the selected game makes / all class boards
best_other_success = maximum completion rate among the other four games
wrong_game_ratio = chosen_success / best_other_success
```

Rules:

1. **SET / 宕:** report when selected-contract failure rate is strictly greater than `0.60`, equivalently `chosen_success < 0.40`.
2. **WRONG / 错:** report when `best_other_success > 0.40` and `wrong_game_ratio < 0.80`.
3. If `best_other_success <= 0.40`, suppress WRONG. A selected contract weak enough to satisfy the ratio in that situation is covered by SET under rule 1.
4. If no other game has a positive success rate, the wrong-game ratio is `null` and WRONG is not reported.
5. A selected game with 100% success produces a finite ratio and cannot trigger WRONG.
6. Threshold equality does not trigger: failure exactly 60%, best-other success exactly 40%, or ratio exactly 0.80 produces no corresponding warning.

`best_other_success` uses the existing alternative-game semantics: for each
other game, a board succeeds when that game can be made from either N/S
declarer seat, and the highest of the four rates is selected. WRONG applies only
when the selected contract is itself one of the five games. SET continues to
apply to any supported contract with DDS evidence.

The report metadata uses `success_probability_ratio_0.8_best_above_0.4_set_above_0.6` as the rule identifier. The UI labels the value as a completion ratio, not an odds ratio.

## Legacy Reports

When opening an older report, the API recalculates SET and WRONG from its stored `contract_failure` and `alternative_game_rates` values. It first removes old SET/WRONG flags, then adds only the flags produced by the new rules. It recalculates pair categories, category counts, and the projected suspicious total from those flags. It does not trust the stored odds-ratio value, old SET/WRONG flags, or old summary counts. This lets the existing report immediately follow the new definitions without rerunning DDS.

A legacy `contract_failure` or alternative-game rate is usable only when it is
a finite number from zero through one. Invalid or missing contract-failure data,
an unrecognized selected game, or no valid alternative rate makes WRONG
unassessed (`null`). Invalid contract-failure data also prevents SET from being
recomputed. Other valid warning flags remain intact.

Other warning types and raw DDS evidence are unchanged. The IV Scanner API,
coverage report renderer, suspicious-resample calculation, suspicious-resample
renderer, and their explanatory labels all use the same shared thresholds and
formula. A previously generated standalone HTML file remains a historical
snapshot until it is regenerated from the JSON report; regeneration uses the
new rules.

## Error Handling

- Missing, invalid, or empty alternative-game rates produce no WRONG warning.
- Missing class evidence keeps the case unassessed as today.
- A legacy cell that cannot be derived is retained as a one-pair group instead of being discarded.
- Expected cell size comes from `budget.pairs_per_cell`, never a hard-coded ten.
  A report with fewer records displays the actual count and an incomplete-cell note.

## Verification

Backend tests cover:

- direct probability ratio rather than odds ratio;
- SET at greater than 60%, including equality boundaries;
- suppression of WRONG when the best other game is at or below 40%;
- legacy flag recalculation;
- recomputed projected categories, counts, and suspicious total;
- sampling-cell projection with `pairs_per_cell` pairs and distinct auctions;
- retained call-limit pairs in new reports and incomplete legacy cells;
- strict JSON for legacy non-finite values.

Frontend tests cover:

- all ten pair selectors are visible for a ten-pair cell;
- selecting a pair changes hands and auction together;
- selected, clean, and warned rail states;
- active-category default selection;
- category and search filters retain every sibling in a matched cell;
- completion-ratio and 60% SET labels.
- result cells use MAKE/SET for the contract outcome and add LOSE only for a
  missed higher game or slam.

Suspicious-resample and standalone-renderer tests verify the same formula,
thresholds, metadata identifier, and user-facing wording across every report
surface.

A browser smoke test opens the existing large report, selects two N/S Pairs with different auctions, and confirms that the displayed hands and auction change together.

## Out of Scope

- Changing how N/S hands are sampled.
- Changing the comparable-class HCP/K–R definition.
- Changing DDS or the E/W sample count.
- Ranking alternative contracts by score or vulnerability.
