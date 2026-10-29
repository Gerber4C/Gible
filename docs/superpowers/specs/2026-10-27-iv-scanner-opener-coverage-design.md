# IV Scanner Opener Coverage and Conditional Deal Generation Design

## Goal

IV Scanner must cover the complete Daqiush 1NT opening space instead of the
three fixed North shapes currently used by the coverage scan. The scanner is a
coverage tool, so different named shapes receive equal or nearly equal quota.
Within one named shape, however, hands retain their true conditional frequency:
common honor layouts must remain more common than rare layouts.

The change must also make rare constrained hands practical to generate. It must
not return to blind shuffling and rejection for shape and HCP constraints.

## Existing defect

The current scan uses only these exact North shapes in S/H/D/C order:

- `4-3-3-3`
- `4-4-3-2`
- `5-3-3-2`

North is not rotated among the named suits. Consequently every five-card-major
North hand has five spades, never five hearts. In the existing report,
`1NT-Pass-3C-Pass` therefore produces 3D and 3S responses but no 3H response.
The scan also omits the permitted `6322`, `5422`, `4441`, and `5431` families.

## Coverage population

### Normal shapes

Generate every named-suit permutation of the seven shape families accepted by
the Daqiush 1NT opening:

- `4333`
- `4432`
- `5332`
- `6322`
- `5422`
- `4441`
- `5431`

Apply the system's structural restrictions before creating quotas:

- neither major may contain six or more cards;
- a five-card major may not coexist with four or more cards in the other major.

This produces 68 legal named shapes. Each of the 68 shapes receives an equal or
near-equal number of ordinary coverage cells. Within a shape, ordinary 15–17
HCP hands are sampled in proportion to the number of legal card combinations,
not with equal quota per HCP or honor pattern.

### Exceptional ranges

Exceptional openings receive guaranteed minimum coverage because their natural
frequency is too low to guarantee their appearance:

- every legal named `5332` arrangement gets at least one 14-HCP upgrade cell;
- every legal named `4432` arrangement gets at least one soft 18-HCP downgrade
  cell.

Hands within each exceptional stratum are still weighted by the number of
legal card combinations. Guaranteed quota applies to the stratum, not to each
honor layout.

## Sampling-cell allocation

The existing South grid remains the outer scan budget: requested South HCP
crossed with requested South base shape. Complete North coverage requires 92
cells: 68 normal shape strata, 12 named `5332` upgrade strata, and 12 named
`4432` soft-18 strata. Small Quick or test scans remain legal but explicitly
report incomplete North coverage.

Use this deterministic allocation algorithm:

1. sort the 68 normal shapes lexicographically in S/H/D/C order;
2. sort the 12 upgrade shapes and 12 soft-18 shapes the same way, with upgrade
   ordered before soft-18 when their normalized positions tie;
3. merge the 68-item normal pool and 24-item exceptional pool by normalized
   rank `(index + 0.5) / pool_size`, comparing by integer cross multiplication;
   this yields one stable, evenly interleaved 92-stratum sequence;
4. for fewer than 92 South cells, use the corresponding prefix and report every
   omitted stratum in `ungenerated_strata`;
5. for 92 or more cells, assign the full sequence once, then assign every extra
   cell to the 68 normal shapes in lexicographic round-robin order;
6. turn the selected strata into quota slots, retaining an occurrence index for
   repeated normal strata;
7. build a bipartite graph between quota slots and South cells. At minimum an
   edge requires `north_length[suit] + rotated_south_length[suit] <= 13` for all
   four suits and compatible combined HCP bounds. Keep the compatibility
   predicate isolated so any additional hard-feasibility rule discovered by the
   exact counter can be added without changing quota semantics;
8. order South cells by SHA-256 of the versioned stable key
   `north-stratum-v1:<south-hcp>:<south-base-shape-index>`. Order quota slots by
   ascending compatible-cell count, then stratum key and occurrence index. Run
   a deterministic augmenting-path maximum matching with neighbors in the
   hashed South-cell order;
9. if no complete matching exists, raise an allocation error containing the
   available/required cell counts and unmatched quota slots. Never assign an
   incompatible pair and hope the card sampler repairs it;
10. only after assignment, shuffle execution order using the scan seed.

Thus 24- and 91-cell scans are accepted but marked incomplete; a 92-cell scan
is the smallest complete scan. In the normal 529-cell grid, each exceptional
stratum receives one cell and each normal shape receives seven or eight cells.
The matching is seed-independent and quota-preserving. Errors and summaries
state both `available_cells` and `required_cells=92`.

All `pairs_per_cell` partnerships in one cell use the same North named shape
and opening mode. They also retain the existing within-cell HCP and K–R span
limits. This preserves the meaning of a comparable N/S cell while expanding
global North coverage.

The old shortcut that forces North to `4333` for South HCP above 19 is removed.

## Joint conditional sampler

### Inputs

The sampler receives:

- exact North and South named shapes;
- North mode: normal 15–17, 14 upgrade, or soft 18 downgrade;
- South exact HCP;
- optional North/South K–R anchors for later pairs in the same cell;
- a deterministic random source.

### Hard-constraint counting

Deal North and South jointly. For each suit, enumerate mutually disjoint North
and South holdings of their required lengths. Dynamic programming tracks:

- North and South HCP totals;
- cards still required in each suit;
- required hard honor structures;
- the number of legal completions below every partial choice.

Choices are sampled in proportion to their legal completion counts. Therefore
every complete N/S card assignment satisfying the hard constraints has the
same probability. This is essential: choosing North uniformly and then South
uniformly would bias North hands because different North holdings leave
different numbers of compatible South hands.

Hard constraints include:

- exact suit lengths and thirteen cards per hand;
- disjoint cards;
- South's exact HCP;
- North's normal or exceptional HCP range;
- pure K–R totals for both hands, represented in the existing exact twentieth
  units with the appropriate fixed shape adjustment;
- the later-pair K–R anchor ranges for both hands;
- QJ doubleton structure required by the soft-18 mode;
- honor-singleton requirements when a shape contains a singleton.
- the 14-point upgrade minimum, the 17-point five-major ceiling, and the
  `5M4m22` / `5M4m31` softness thresholds.

Impossible partial choices have zero completion count and are never entered.
This provides the requested backtracking behavior without greedy honor choices
or blind whole-deal shuffling.

### Final consistency check

All current Daqiush opening and anchor conditions are expressible through the
counted HCP, exact K–R units, shape, and honor-structure state and therefore
belong inside the completion count. After drawing, run the authored
`opening_assessment` and anchor checks once as an invariant. A failure is a
sampler/authoring mismatch and raises a diagnostic error; it is not handled by
probabilistic whole-hand retry. Once N/S passes the invariant, split the
remaining 26 cards randomly between East and West exactly as today.

Counting plans and suit-level combination tables are cached by immutable
constraint key. State counts use Python arbitrary-precision integers. All
combinations and DP states have canonical ordering, so enabling or warming the
cache cannot alter results for a fixed random seed. The cache may change
performance but never sampling semantics.

## Failure behavior

The sampler must never silently fall back to an unconstrained deal. A zero
hard-completion count fails immediately. An invariant mismatch reports:

- North named shape and mode;
- South shape and HCP;
- requested anchors;
- hard-completion count and the exact failed authored predicate.

This identifies a bad quota definition or implementation mismatch without
hanging the scan. The former probabilistic final-predicate retry budget is
removed because rare opening constraints are part of the counted population.

At scan level, catch a cell-generation error, record the assigned stratum and
stable South cell with `reason="generation_error: <diagnostic>"`, skip that
cell's ungenerated pair slots, and continue scanning other cells. Return a
strictly marked partial report with `coverage.north.complete=false` and a
nonzero `summary.generation_errors`; do not raise after report construction and
do not silently substitute another stratum or random deal. Allocation failure
before execution still raises immediately because no quota-preserving schedule
exists.

The hardest currently known `5M4m22` stratum must generate ten valid N/S pairs
within 30 seconds in a dedicated benchmark test on the project test host. This
is a generous regression ceiling, not a target latency. Schedule construction
itself must remain sub-second and perform no card generation.

## Report schema and observability

Each case's `coverage_cell` gains stable North-stratum metadata:

- `opener_shape` in S/H/D/C order;
- `opener_mode`: `normal`, `upgrade_14`, or `soft_18`.

The report's `coverage.north` object has this explicit schema:

- `schema_status`: `explicit` for new reports or `legacy` when reconstructed
  metadata is unavailable;
- `required_cells`: `92`;
- `available_cells`: number of requested South cells;
- `complete`: whether all 92 strata were scheduled and generated;
- `requested_strata`: ordered objects `{shape: [S,H,D,C], mode, cell, status}`
  actually assigned to cells, including repeated normal strata in stable
  South-cell order. `status` is `generated`, `partial`, or `failed`;
- `observed_strata`: distinct generated `{shape, mode}` objects;
- `cell_counts`: mapping from every one of the 92 stable keys
  `mode:S-H-D-C` to scheduled cell count, including zeroes;
- `pair_counts`: the same complete key set mapped to generated N/S pair count;
- `hcp_by_mode`: sorted observed North HCP values for each mode;
- `cell_failures`: authoritative ordered objects
  `{shape, mode, cell, missing_pair_slots, reason}` for assigned cells that did
  not generate all requested pairs;
- `ungenerated_strata`: derived ordered objects `{shape, mode, cell, reason}`. Omitted
  prefix strata use `cell=null` and `reason="insufficient_cells"`; failed
  assigned cells are derived from `cell_failures` and carry the concrete error.

Every non-null `cell` uses the same exact object form everywhere:

```json
{"target_hcp": 10, "base_shape_index": 4}
```

Matching diagnostics, requested strata, cell failures, ungenerated strata,
coverage-cell metadata, extension, and IV projection all use those two integer
fields as the common cell identity. Stable textual IDs may be derived as
`"<target_hcp>:<base_shape_index>"` but never replace the object in stored
summary schema.

This two-field summary identity is distinct from a case-level
`coverage_cell`, which also carries `base_shape`, `pair_slot`, `opener_shape`,
and `opener_mode`. Use separate validators for those two forms so summary
records cannot accumulate case-only fields and explicit cases are not rejected
for carrying their required generation metadata.

`complete` is false whenever `available_cells < required_cells`, any required
stratum is omitted, or `cell_failures` is nonempty. Cell counts measure quota
fairness; pair counts measure generated sample volume and may increase after
extension.

Existing South coverage fields remain intact. IV Scanner projected groups copy
`opener_shape` and `opener_mode` from `coverage_cell`; pair records retain the
complete cell object. Old reports without North-stratum metadata remain
readable with `coverage.north.schema_status="legacy"`; no strata, modes, or
counts are invented.

## Coverage extension

Coverage extension must use the same joint conditional sampler. For every
cell it validates that all existing explicit cases agree on `opener_shape` and
`opener_mode`, reconstructs the North constraints from those two fields, and
reconstructs the South constraints from the existing cell metadata. A normal
mode remains a natural 15–17 population; extension must not pin it to the first
pair's exact North HCP.

Extension treats the persisted `requested_strata` schedule and `cell_failures`
as authoritative even when a failed cell has zero cases. It retries exactly the
missing pair slots of failed or partial explicit cells. A successful retry
removes or shrinks the corresponding failure record and updates requested
status; another failure preserves the record with the new concrete reason.

For a zero-case cell, reconstruct South constraints from the validated top-level
scan filters, not from a nonexistent first case: look up
`filters.shapes[base_shape_index]`, rotate that base shape left by
`(target_hcp + base_shape_index) % 4`, and use `target_hcp` as South's exact
HCP. Recover North shape and mode from the authoritative requested record. If
the saved filters are absent, malformed, or inconsistent with existing cases,
explicit extension fails with a field-specific `ValueError`; it never guesses
or falls back to legacy sampling.

Both extension scopes run the same missing-sampling-slot repair pre-pass.
`extend_process_pairs` retains the recovered cases and lets their auctions
create the initially absent process groups, then applies its ordinary process
top-up/discovery rules. Its `allow_new_processes` switch controls later
exploratory discovery, not repair of persisted missing sampling slots.

Added pairs obey the cell's aggregate HCP/K–R span limits. After extension,
recompute `requested_strata` statuses, `observed_strata`, `cell_counts`,
`pair_counts`, `hcp_by_mode`, `cell_failures`, `ungenerated_strata`, and
`complete` from the requested schedule, all stored cases, and remaining failure
records. Do not carry stale summary counts forward. Legacy cells without
explicit North metadata retain the old extension path and remain labelled
legacy; they are never relabelled as explicit.

## Verification

Tests must demonstrate:

1. exactly 68 normal named shapes are generated by the structural enumerator;
2. all 68 occur in a full scanner schedule;
3. every legal named 14-point `5332` and soft-18 `4432` exceptional stratum is
   scheduled at least once;
4. quotas among normal shapes differ by at most one cell after exceptional
   reservations;
5. the deterministic matching assigns every selected quota slot to a South
   cell with four suit sums no greater than 13, including all 529 default cells;
6. every one of the 529 assigned default constraints has a positive exact joint
   DP completion count without drawing cards;
7. every generated N/S pair has 13 cards each, no duplicate card, exact shapes,
   correct South HCP, and a North hand accepted by the authored 1NT predicate;
8. later pairs in a cell respect the existing HCP and K–R span rules;
9. the weighted branch selector uses completion counts, verified with exact
   small fixtures or deterministic boundary draws rather than flaky frequency
   assertions;
10. fixed seeds reproduce identical N/S hands and schedules;
11. impossible constraints fail promptly with the diagnostic context above;
12. generated `1NT-Pass-3C-Pass` positions contain actual 3D, 3H, and 3S
    opener responses;
13. current report readers accept both new metadata and old reports;
14. allocation boundary tests cover 24, 91, 92, and 529 cells and verify the
    exact completeness and omitted-strata semantics;
15. the hardest `5M4m22` case meets the 30-second ten-pair regression ceiling;
16. DP completion counts safely exceed 64-bit range where appropriate;
17. cold and warm caches produce the same hands for the same seed;
18. coverage extension preserves mode semantics and recomputes every North
    summary field;
19. IV projection retains group and pair North-stratum metadata;
20. exact legacy `schema_status` behavior is covered;
21. the full backend regression suite introduces no failures beyond the
    freshly captured live dirty-worktree baseline; failures that disappear are
    allowed, and the comparison is by test identity rather than failure count.

## Non-goals

- Weighting different named shapes by real-world occurrence probability.
- Changing the Daqiush 1NT opening definition.
- Changing responder coverage quotas.
- Using DDS or concealed opponent cards to choose bids.
- Treating IV Scanner counts as population-frequency estimates.

## Owner bug report — 1NT responder routes (2026-10-27, implemented)

Implementation status (2026-10-27): items 1–4 are authored in the daqiush
profile (Texas/Jacoby KR bands, minor transfer + other-minor + cue routes,
and the second-minor 3NT continuation table). The exclusion keycard routes
and the grand-slam acceptance quantiles are described in
`docs/15_daqiush_slam.md`. The 3C minor-ask route below is still a design
specification, not yet authored.

1. **7-card major transfers.** Jacoby weak transfers allow 6 and 7 cards;
   Texas likewise, with the seventh card measured by K-R: game strength
   uses Texas, an invitation transfers and raises to three, and a weaker
   hand transfers and passes. A 5M332 hand with 17–18 HCP names its lowest
   three-card side minor with 6C/6D (partner may continue with a five-card
   suit; an eight-card fit stops, otherwise 6NT); 5NT is the grand-slam
   invitation. IMPLEMENTED.
2. **Strong 7-card minor.** A very strong 7C hand settles in 5C and misses
   slam. Owner route: bid 2S (transfer to 3C), then 3M cue — the 3M cue
   initiates the trump agreement while cue-bidding (different from
   post-agreement cueing). General minor-fit stop-asking principle: with
   opponents silent and our side holding two or more unbid suits, bidding a
   suit asks for a stopper there; if partner holds the stoppers for the
   other ask-suits and lacks slam strength, 3NT. Otherwise: minimum 4m
   (non-forcing inside the game-forcing process; partner simulates pass,
   5m, or continued cueing); non-minimum cues.
3. **6-4 minors with slam interest block.** Transfer to one minor first,
   then bid the other minor.
4. **1NT-2H-2S-3C-3NT continuation.** Responder then: if no slam interest,
   a six-card major bids 4S (signoff); without a six-card major but with a
   six-card minor, 5C (opener simulates). With slam interest: 5-4 suits
   bid 4NT / 6NT / 5NT (quantitative / small-slam signoff / grand-slam
   invite forcing; answer tables per docs/15_daqiush_slam.md); 6-4 suits
   cue a new suit (agreeing spades); 5-5 / 5-6 suits bid 4C — partner
   bids any four-level suit (including spades) as a cue (clubs agreed),
   4NT shows no fit, and responder then simulates.

   Mirror symmetric: spades↔hearts, clubs↔diamonds.

### 3C minor-ask route with 3-1 majors and 5-4 minors (game-forcing+)

Responder with a 3-1 major split and 5-4 minors bids **3C** uniformly.
Opener 3D asks for the major short-suit position. Responder then shows the
singleton/void suit. Opener next:

- rolls forward; if the 3NT expected value is high, 3NT;
- else: four-card minor at the four level (that suit agreed); prefers the
  4-3 major fit by bidding the lowest other major; if opener still has
  slam interest responder bids the lowest five-card minor, then opener
  simulates — all signoffs;
- 4-4+ minors, good controls, no wasted major honors (no KQJ, or AK):
  4M (diamonds agreed);
- 3-3 minors but a poor 3NT simulation: 4NT (opener simulates; all
  signoffs).

Opener 3M (supporting the three-card major):

- responder's five-card minor matches opener's three: no slam interest
  raises 4M; otherwise the lowest other major is cue-shown as strong.
- responder's five-card minor matches opener's one: no slam interest 3NT;
  otherwise the five-card minor at the four level. Opener then: clubs
  (5C4D) — 4D agrees diamonds, 4H/S cue agrees clubs, or raises 5C;
  diamonds (5D4C) — 4H/S agree clubs/diamonds respectively, none
  promising controls.
