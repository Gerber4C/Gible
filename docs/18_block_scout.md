# Block-point collection (stage 1)

`backend/engine/block_scout.py` searches seeded random **complete deals** under
specified conditions. It runs the selected partnership's actual bidding logic;
the opponents Pass, matching the current Table training setup. It records a
block exactly where `simulate_auction` reports one, without making a fallback
call or changing the profile.

Run from `backend/`:

```powershell
python -m engine.block_scout --profile daqiush_2over1 --dealer ns --opening 1NT --attempts 500 --seed 23 --output ../reports/block_scans/daqiush-1nt.json
```

`--dealer` accepts a seat (`n/e/s/w`), a partnership (`ns/ew`), or `random`.
`--response 2C` further keeps only deals where the partner actually chooses
2♣ after the opening and an opponent Pass. `--vulnerability` accepts `none`,
`ns`, `ew`, or `both`. `--max-seconds`, `--max-cases`, and `--max-calls` bound a
run. The default time limit is 30 seconds. Reuse the reported seed and options
to reproduce the same sampled deals; use the same budgets for a full replay.

Optional `--constraints bounds.json` filters complete deals **before** bidding.
Suit-length bounds are inclusive. The keys are fixed seat letters, so use a
fixed dealer if a bound is intended for the opener:

```json
{
  "n": {"min_hcp": 15, "max_hcp": 17},
  "s": {"min_lengths": {"hearts": 5}, "max_lengths": {"clubs": 2}}
}
```

## Oversample rare high-point partnerships

For the illustrated 1NT hands with a 16-HCP opener and a 21-HCP responder,
reserve a share of **attempted deals** for that strength combination:

```powershell
python -m engine.block_scout --profile daqiush_2over1 --dealer ns --opening 1NT --attempts 500 --seed 23 --rare-share 0.4 --rare-opener-hcp 16:16 --rare-responder-hcp 21:21 --output ../reports/block_scans/daqiush-1nt-rare.json
```

Use ranges such as `15:17` and `20:22` to include nearby hands. The scanner
constructs each rare deal directly from the honor cards, then fills the low
cards randomly. It still checks whether the opener **actually selects 1NT**;
high HCP alone never forces an opening. The specified share applies before
that call filter, so the share among matching 1NT auctions can differ. Each
case carries `stratum: natural` or `rare_hcp`; the summary and block-point
counts are split by stratum. This is deliberate test weighting, not a bridge
probability estimate. The unweighted natural stratum remains available as a
baseline.

The report is JSON with `schema_version`, profile identity, seed, filters,
budgets, and counters. `block_points` counts each distinct auction-prefix and
seat. `cases` contains up to `--max-cases` examples, each with all four hands,
the calls and seats, the selected source IDs where available, the blocked seat,
and the engine's diagnostics and axiom findings. The case field
`review_status: unreviewed` is a handoff marker, not a diagnosis. Complete and
call-limit auctions are counted separately; only actual `blocked` outcomes
become block cases. Reports under `reports/block_scans/` are ignored by Git.

## Browse a scan report

Generate an offline HTML viewer for any saved JSON report:

```powershell
python -m engine.block_report_viewer ../reports/block_scans/daqiush-1nt-rare.json
```

The command writes an `.html` file beside the JSON file. Open it in a browser;
it needs no running server or network access. The left panel groups block
points by auction prefix and blocked seat. Search or filter by ordinary/rare
sample, then step through the saved examples. Each example shows all four
hands, the full auction in seat order, the next blocked seat, and the engine's
diagnostics. The viewer only displays saved cases: if the report's
`--max-cases` limit omitted a hand for a counted block point, rerun the scan
with a larger limit.

## Balanced 1NT coverage and DDS audit

The coverage scanner fixes **North as the 1NT opener** and samples South at
every raw HCP value from 0 through 22. Its 23 representative South shapes
cover every feasible combination of longest suit 4–8 cards and
longest-two-suit total 7–11 cards (23 × 23 = 529 quota cells). Suit placement
is rotated deterministically for each HCP/shape identity. Those cells are
allocated across 92 North strata: 68 legal named normal shapes, twelve
14-HCP 5332 upgrades, and twelve soft-18 4432 shapes. A normal stratum is the
ordinary natural 15–17 HCP range; it is not pinned to one HCP value or to the
first generated hand. The profile bids using each player's own information;
opponents Pass. Each completed auction is checked with fresh East/West
completions using DDS.

A minimal real full scan uses one N/S pair and one E/W completion per cell.
The class minima must also be one so each single-board group is assessable:

```powershell
cd backend
..\.venv\Scripts\python.exe -m engine.coverage_scan --profile daqiush_2over1 --seed 23 --pairs-per-cell 1 --ew-samples 1 --min-class-boards 1 --min-class-pairs 1 --output ../reports/block_scans/daqiush-1nt-coverage-seed23-minimal.json
..\.venv\Scripts\python.exe -m engine.block_report_viewer ../reports/block_scans/daqiush-1nt-coverage-seed23-minimal.json
```

This is still a real 529-cell profile scan, not a unit-test shortcut. For
stronger outcome rates, raise `--pairs-per-cell`, `--ew-samples`, and the two
class minima together.

The exact-counter feasibility check constructs all 529 allocated constraints,
does not call DDS, and requires a positive joint completion count for every
one. It is intentionally opt-in:

```powershell
cd backend
$env:GIBLE_RUN_SLOW_COVERAGE = '1'
..\.venv\Scripts\python.exe -m unittest tests.test_joint_deal_sampler.JointDealSamplerTests.test_all_default_allocations_have_an_exact_joint_completion -v
Remove-Item Env:GIBLE_RUN_SLOW_COVERAGE
```

The focused real-profile selector check records three reproducible
`(target_hcp, base_shape_index, joint_seed)` identities: `(0,0,0)` → 3D,
`(0,1,0)` → 3S, and `(0,3,0)` → 3H after `1NT-Pass-3C-Pass`. It uses the
allocated stratum, exact joint sampler, Daqiush opening assessment, and actual
selector. Run it with:

```powershell
cd backend
..\.venv\Scripts\python.exe -m unittest tests.test_joint_deal_sampler.JointDealSamplerTests.test_real_allocated_strata_cover_every_five_card_major_inquiry_reply -v
```

After a real scan, inspect which saved hands produced each reply (including
their coverage-cell identities) with:

```powershell
@'
import json
from pathlib import Path
p = Path('../reports/block_scans/daqiush-1nt-coverage-seed23-minimal.json')
r = json.loads(p.read_text(encoding='utf-8'))
for c in r['cases'] + r['complete_cases'] + r['limit_cases']:
    if c.get('calls', [])[:4] == ['1N', 'P', '3C', 'P'] and len(c['calls']) > 4 and c['calls'][4] in ('3D', '3H', '3S'):
        print(c['calls'][4], c['coverage_cell'], c['hands']['n'])
'@ | ..\.venv\Scripts\python.exe -
```

The HTML viewer has **Blocked**, **Suspicious**, and **All deals** sections.
Suspicious hands are grouped by class; use the left/right buttons to compare
hands in one class. Every pair of members has the same named-suit shapes for
both partners, and each partner's HCP and K–R differ by no more than two.
Every sampled deal has a scan-order number such as `#0042`, shown in the
detail heading and in the all-deals list. Search for `42` or `#0042` to
find it. Quote the report seed together with the number when referring to a
deal from another run (for example, `seed 23, #0042`). The JSON `id` and
`trial` fields carry the same number.

A comparable
class has exactly the same North and South lengths in each named suit, and
the full range of each player's raw HCP and Kaplan–Rubens score is at most 2.
Pairs in one sampling cell that also produce the identical complete auction
are merged: their DDS boards are pooled and all member pairs share one set of
rates. A cell whose pairs diverge into different auctions splits into one cell
per process.
For the displayed final contract, a DDS failure rate above 60% is flagged.
If the auction stopped below game, small slam, or grand slam, a DDS rate
above 30% for any makeable contract at that level is flagged. A **wrong game**
warning applies only to an actual `3NT`, `4S`, `4H`, `5D`, or `5C` contract:
the selected game's completion probability divided by the best alternative
game's completion probability must be below 0.8, and the best alternative
itself must clear 40%. Completion probabilities are `success / all boards`
across the pooled DDS boards of the cell; alternative-game rates are listed
separately and can overlap. A class
with fewer than `--min-class-boards` DDS boards or
`--min-class-pairs` distinct North/South hands is marked insufficient rather
than suspicious. Pairs within each quota cell keep exact North/South shapes
and exact South HCP. North HCP follows its mode (normal 15–17, upgrade 14, or
soft 18), and each new K–R draw uses the current aggregate envelope rather
than a pinned first-pair anchor. These are terminal-auction screening signals, not a
diagnosis of which earlier bid was wrong. DDS is double-dummy, and synthetic
coverage weights are not real-world frequencies. The report records the
number of matching North/South pairs and DDS boards for every estimate.

The intended later workflow is separate:

1. **Collect** reproducible block evidence (implemented here).
2. **Resolve from sources:** inspect the selected profile's BSL, policy,
   system notes, and applicable baseline agreements. Do not infer an agreement
   merely from a plausible bridge bid.
3. **Ask the owner:** group only unresolved, genuinely ambiguous block points
   into specific questions, with representative hands and auction prefixes.

The scanner still does not invent a system agreement or edit profile files.
For suspicious resampling reports it now prepares a compact review brief;
the suggestion writer (a local LLM or this chat) reads the actual agreements,
and the offline report lets the owner edit and approve each proposed call.

## Generate deals with exact N/S shapes and point ranges

`engine.constrained_deals` generates complete four-hand deals from exact
North and South suit lengths (spades, hearts, diamonds, clubs) and inclusive
raw HCP and pure Kaplan–Rubens ranges. It then runs automatic N/S bidding
with the selected profile; E/W Pass, as in the coverage scanner. The default
profile is Daqiush 2/1. For example:

```powershell
cd backend
python -m engine.constrained_deals --profile daqiush_2over1 --north-shape 4,3,3,3 --north-hcp 15:17 --north-kr 14.5:19 --south-shape 6,3,2,2 --south-hcp 8:11 --south-kr 8:15 --count 1000 --seed 73 --output ../reports/block_scans/constrained-bidding-seed73.json
```

The command writes JSON and an HTML viewer beside it. In the viewer,
**Blocked** groups failures by auction prefix, while **All deals** lets you
search any deal number and inspect its full auction and final contract or
diagnostic. The JSON stores numbered blocked, completed, and call-limit
cases separately. It records full hands and North/South HCP and K–R values.
This report runs no DDS or contract success analysis. The supplied ranges do
not themselves guarantee any particular opening; the profile chooses bids.

The joint generator counts exact legal North/South completions under the fixed
named shapes, HCP targets/mode, and K–R envelopes, then samples backward by
those completion counts. It is uniform over legal concrete N/S card
assignments within those fixed constraints; it does not draw North first and
blindly reject the remaining deck for South. A suit is rejected immediately
when its North and South lengths total more than 13. A/K/Q/J/T/9/8 remain
explicit in the count. Only ranks 2–7 share the score-state `x` abstraction,
and the chosen state is refilled uniformly from its legal concrete 2–7
allocations before any opponents are completed or DDS is called. Fixed seeds
therefore reproduce the same concrete N/S assignments. The distribution is
conditional on the requested synthetic constraints and is not a natural
bridge-frequency estimate.

## IV Scanner in the local web workspace

Open **IV Scanner** beside System Editor and Table. It reads existing coverage
reports and can start a new North-1NT scan in the background. The scan sweeps
all twenty-three South shapes from the standard shape-probability table (rows
1–22 and 24), South's HCP range, the number of independent N/S pairs per cell,
E/W completions per pair, and a reproducible seed. The default is ten E/W
completions. Progress remains visible while the other pages are usable;
completed reports are saved under `reports/block_scans/`.

A full scan also covers the complete Daqiush 1NT opener space. The 529 South
cells are matched to 92 North strata: 68 legal named normal shapes (4333,
4432, 5332, 6322, 5422, 4441 and 5431, excluding a six-card major and a
five-card major with four or more in the other major), 12 guaranteed 14-HCP
5332 upgrade strata, and 12 guaranteed soft-18 4432 strata. Within a named
shape, hands keep their conditional card-combination frequency; different
named shapes receive equal or near-equal cell quotas. Each `coverage_cell`
records `opener_shape` and `opener_mode`, and the report carries a
`coverage.north` summary. A scan with fewer than 92 strata still runs but marks
`coverage.north.complete=false` and lists every omitted or failed stratum.
For explicit reports, `coverage.north.requested_strata` is the authoritative
cell-to-stratum schedule, while `coverage.north.cell_failures` records concrete
generation failures and their exact missing pair slots. The remaining summary
fields describe what was actually generated, so a partial report preserves
both its requested coverage and its failures instead of silently appearing
complete.
Legacy reports without this metadata remain readable with
`coverage.north.schema_status="legacy"`; no strata or modes are invented for
them.

The four finding filters are: **TD**, no supported next call; **丢**, a game
or slam is available more than the configured share of comparable DDS boards
but was not bid; **宕**, the chosen contract fails more than the configured
share; and **错**, the chosen game's completion probability divided by the best
alternative game's completion probability falls below the configured ratio
while the best alternative also clears its own floor. Comparable hands have
the same named-suit shapes and each seat's complete HCP and K–R spans stay
within two points. Pairs in one sampling cell with the identical complete
auction are merged into one cell and their DDS boards are pooled; different
auctions split into separate cells. The browser omits bulky DDS tables and
shows every N/S pair of a selected cell in a vertical rail; picking one pair
shows that pair's exact hands, auction, diagnostics, warnings, and its own E/W
outcome strip marked MAKE, SET, and LOSE. A blocked auction ends with an
orange TD call tile naming the seat that could not bid. Findings has a
**Findings / Overview** switch: Overview lists every cell·process group,
including clean ones, 100 per page with Prev/Next paging; search still applies,
while category filters remain on the Findings view. Reading a report exposes
sliders, direct numeric entry, and ←/→ step buttons
for the SET failure share, the LOSE missed-share, the WRONG success ratio, and
the WRONG best-other floor; TD has no threshold. Categories and counts
reclassify immediately, while default thresholds remain 60%, 30%, 0.8, and
40%. The saved
JSON and standalone HTML retain full evidence.

## Top up undersized cell·process groups

The browser groups one cell per sampling cell × complete auction, so a report
can show groups with one to three N/S pairs even when every HCP/shape sampling
cell already contains ten. The extender tops up every existing process group:

```powershell
cd backend
..\.venv\Scripts\python.exe -m engine.coverage_extend ..\reports\block_scans\old-report.json --target-pairs 10 --seed 41 --output ..\reports\block_scans\old-report-topup.json
```

`--target-pairs` defaults to 10. For an explicit report, the extender validates
and obeys `coverage.north.requested_strata` and `cell_failures`; stored cases
cannot override that authoritative cell schedule. It reconstructs even a
zero-case failed cell from the report filters plus requested stratum, and a
common repair pre-pass retries exactly the persisted missing pair slots before
either extension scope starts its ordinary top-up. Normal North hands retain
their natural 15–17 range; only `upgrade_14` and `soft_18` are exact-HCP modes.
The K–R envelope is recomputed after every accepted pair from the current
aggregate minimum and maximum, so it is not a fixed first-pair anchor.

The default `--scope process` samples new N/S pairs under the parent sampling
cell's exact South shape/HCP and authoritative North shape/mode. Known process
groups are filled first.
Once they reach the target, remaining sampling attempts may discover an
auction not present in the report; that candidate opens a new process
sub-cell, which is then topped up to the same target before another new
process is considered. `--discard-new-processes` restores the older behavior
of discarding unseen auctions. Discovery stops after
`--discovery-idle-limit` consecutive attempts that do not open a new process
(default 100; `0` disables discovery, and `None` in the Python API keeps
trying until the attempt cap). `--max-attempts-per-cell` caps sampling per
parent cell; groups still short of the target are listed in
`extension.unreached_groups`, and newly opened groups are listed in
`extension.discovered_processes`. `--ew-samples` overrides the stored E/W count
and the seed reproduces the additions. `--scope sampling` tops up each parent
HCP/shape sampling cell instead. Both explicit scopes use the same repair,
validation, and dynamic-envelope rules. After extension, the aggregate
analysis, block points, suspicious cases, counts, DDS-board totals, coverage
observations, and the complete `coverage.north` summary are recomputed from
the resulting cases rather than retaining stale source-report totals.

Reports with `coverage.north.schema_status="legacy"` use the legacy
reconstruction path because they have no authoritative requested-strata or
failure metadata. That compatibility path retains its stored opener HCP and
reference behavior and must not be interpreted as the explicit Task 4 rules.

Added pairs cost one DDS solve per E/W sample, and rejected candidates still
run an auction. Discovery uses the same per-cell attempt cap, so a large old
report can take a long time; rare processes may not reach the target. Cells
whose stored metadata cannot define a sampling rule are listed in
`extension.skipped_cells` and left unchanged. Parent cells that already meet
every process target are not re-sampled, so discovery only happens in cells
that initially had a deficit.

## Re-sample small suspicious classes

Use the previous 1NT coverage report to revisit **every suspicious class
with at most ten source cases**. The command draws 20 new North/South pairs
per class, gives each pair ten different East/West completions, runs the
profile's automatic auction, and checks each board with DDS:

```powershell
cd backend
..\.venv\Scripts\python.exe -m engine.suspicious_resample ..\reports\block_scans\daqiush-1nt-coverage-seed23.json --profile daqiush_2over1 --seed 41 --pairs-per-group 20 --ew-samples 10 --output ..\reports\block_scans\daqiush-1nt-resample-seed41.json
```

The command also writes a standalone HTML report and a `-review-brief.json`
file beside the JSON. Each
class shows the original numbered cases and warnings, the warning rates on
fresh deals, the automatic contracts or blocks, and every fresh numbered
deal with its two hands and auction. Search the left column by class ID or
original case number; filter classes by warning outcome or blocking. Only
the selected class appears on the right. Expand a deal to see suit-by-suit
hands, its calls in seat order, and any blocking diagnostic. The original
and fresh warning rates show their DDS board counts. The fresh pairs match the original
class's exact named-suit shapes. Across all original and fresh hands for each
seat, raw HCP's maximum minus minimum and K–R's maximum minus minimum are
both at most 2. North must actually choose 1NT.

The displayed warning comparison holds the *original* contract and
declarer fixed while changing the hands. The fresh auction is also run
separately, so the report can reveal whether the system still reaches that
contract or gets blocked. These targeted samples are test coverage, not
natural hand frequencies. All E/W completions of the same N/S pair share
the partnership hands, so treat the pair count as the independent sample
count. DDS sees all four hands and is only a screening proxy for real play.

To add E/W completions to an existing resampling report while keeping every
N/S hand, auction, case ID, and group review, use the resampling report as
input. The original DDS boards are retained and warning rates are recomputed:

```powershell
cd backend
..\.venv\Scripts\python.exe -m engine.suspicious_resample ..\reports\block_scans\daqiush-1nt-resample-span2-seed41.json --ew-samples 10 --workers 8 --reviews ..\docs\reviews\daqiush-1nt-seed41.json --output ..\reports\block_scans\daqiush-1nt-resample-span2-seed41-ew10.json
```

### Review proposed system changes

The review brief contains numbered groups, representative hands, auctions,
block diagnostics, and the source warning rates without bulky DDS tables. It
also records the authority order: Daqiush overrides conflicting Newrui/CBB
agreements. Supply that brief and the referenced system files to a suggestion
writer. A proposal should name the **next call and exact auction** whenever a
recorded agreement supports it; otherwise mark the missing definition rather
than guessing. Suggestions are separate from the sampled report and do not
change the bidding engine.

To show a completed suggestions JSON beside the evidence, run from the
repository root:

```powershell
.\.venv\Scripts\python.exe -m backend.engine.suspicious_resample_viewer reports\block_scans\daqiush-1nt-resample-span2-seed41.json --reviews docs\reviews\daqiush-1nt-seed41.json --output reports\block_scans\daqiush-1nt-resample-span2-seed41-review.html
```

The offline page has editable proposed calls, reasons, source references and
review notes. Mark each group **agree**, **needs changes**, or **reject**;
move to the next unreviewed group, and export the JSON. The page tries to
preserve edits in browser storage, but the exported JSON is the durable review
record. Import it into the same report later to continue. A report signature
prevents accidentally applying its decisions to another sample. After
approval, code changes and a new scan are separate steps; the review page
never silently writes or activates a bidding rule.
