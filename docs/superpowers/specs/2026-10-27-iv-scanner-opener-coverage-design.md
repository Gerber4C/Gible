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
6. map that allocation to South cells sorted by SHA-256 of the versioned stable
   key `north-stratum-v1:<south-hcp>:<south-base-shape-index>`; this spreads
   exceptional strata across both South dimensions without using the run seed;
7. only after assignment, shuffle execution order using the scan seed.

Thus 24- and 91-cell scans are accepted but marked incomplete; a 92-cell scan
is the smallest complete scan. In the normal 529-cell grid, each exceptional
stratum receives one cell and each normal shape receives seven or eight cells.
Errors and summaries state both `available_cells` and `required_cells=92`.

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
- a deterministic random source and bounded retry budget.

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
- `requested_strata`: ordered objects `{shape: [S,H,D,C], mode}` actually
  assigned to cells;
- `observed_strata`: distinct generated `{shape, mode}` objects;
- `cell_counts`: mapping from stable key `mode:S-H-D-C` to scheduled cell count;
- `pair_counts`: the same keys mapped to generated N/S pair count;
- `hcp_by_mode`: sorted observed North HCP values for each mode;
- `ungenerated_strata`: ordered objects `{shape, mode, reason}`, using reason
  `insufficient_cells` for a legal partial scan or the concrete generation
  error for a failed assigned stratum.

`complete` is false whenever `available_cells < required_cells`, even if every
assigned cell generated successfully. Cell counts measure quota fairness;
pair counts measure generated sample volume and may increase after extension.

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

Added pairs obey the cell's aggregate HCP/K–R span limits. After extension,
recompute `observed_strata`, `cell_counts`, `pair_counts`, `hcp_by_mode`,
`ungenerated_strata`, and `complete` from all stored cases. Do not carry stale
summary counts forward. Legacy cells without explicit North metadata retain the
old extension path and remain labelled legacy; they are never relabelled as
explicit.

## Verification

Tests must demonstrate:

1. exactly 68 normal named shapes are generated by the structural enumerator;
2. all 68 occur in a full scanner schedule;
3. every legal named 14-point `5332` and soft-18 `4432` exceptional stratum is
   scheduled at least once;
4. quotas among normal shapes differ by at most one cell after exceptional
   reservations;
5. every generated N/S pair has 13 cards each, no duplicate card, exact shapes,
   correct South HCP, and a North hand accepted by the authored 1NT predicate;
6. later pairs in a cell respect the existing HCP and K–R span rules;
7. the weighted branch selector uses completion counts, verified with exact
   small fixtures or deterministic boundary draws rather than flaky frequency
   assertions;
8. fixed seeds reproduce identical N/S hands and schedules;
9. impossible constraints fail promptly with the diagnostic context above;
10. generated `1NT-Pass-3C-Pass` positions contain actual 3D, 3H, and 3S
    opener responses;
11. current report readers accept both new metadata and old reports;
12. allocation boundary tests cover 24, 91, 92, and 529 cells and verify the
    exact completeness and omitted-strata semantics;
13. the hardest `5M4m22` case meets the 30-second ten-pair regression ceiling;
14. DP completion counts safely exceed 64-bit range where appropriate;
15. cold and warm caches produce the same hands for the same seed;
16. coverage extension preserves mode semantics and recomputes every North
    summary field;
17. IV projection retains group and pair North-stratum metadata;
18. exact legacy `schema_status` behavior is covered;
19. the full backend regression suite introduces no failures beyond the
    existing, separately recorded Meow fixture baseline.

## Non-goals

- Weighting different named shapes by real-world occurrence probability.
- Changing the Daqiush 1NT opening definition.
- Changing responder coverage quotas.
- Using DDS or concealed opponent cards to choose bids.
- Treating IV Scanner counts as population-frequency estimates.
