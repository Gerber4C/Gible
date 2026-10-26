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
every raw HCP value from 0 through 22. Its 13 representative South shapes
cover every feasible combination of longest suit 4–8 cards and
longest-two-suit total 7–11 cards (23 × 13 = 299 quota cells). The scan
rotates suit placements. North is constructed in one of three common 1NT
shapes (4333, 4432, 5332), with 15–17 HCP, then kept only when the selected
profile actually opens 1NT. High-HCP South cells use a 15-HCP 4333 North
hand for feasibility. The profile bids using each player's own information;
opponents Pass. Each completed auction is checked with fresh East/West
completions using DDS:

```powershell
cd backend
..\.venv\Scripts\python.exe -m engine.coverage_scan --profile daqiush_2over1 --seed 23 --pairs-per-cell 2 --ew-samples 10 --min-class-boards 10 --min-class-pairs 2 --output ../reports/block_scans/daqiush-1nt-coverage-seed23.json
..\.venv\Scripts\python.exe -m engine.block_report_viewer ../reports/block_scans/daqiush-1nt-coverage-seed23.json
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
For the displayed final contract, a DDS failure rate above 50% is flagged.
If the auction stopped below game, small slam, or grand slam, a DDS rate
above 30% for any makeable contract at that level is flagged. A **wrong game**
warning applies only to an actual `3NT`, `4S`, `4H`, `5D`, or `5C` contract:
the selected game's success odds divided by the best alternative game's
success odds must be below 0.8. Success odds are `success / failure` across
all DDS boards in the class; alternative-game rates are listed separately and
can overlap. A class
with fewer than `--min-class-boards` DDS boards or
`--min-class-pairs` distinct North/South hands is marked insufficient rather
than suspicious. Pairs within each quota cell are generated with the same
North/South shapes and HCP, and each partner's K–R score stays within 2 of
the first pair. These are terminal-auction screening signals, not a
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

The generator counts suit combinations by both scores, then draws only
qualifying hands. South draws from the deck remaining after North; East and
West randomly split the other 26 cards. Fixed seeds reproduce the same
output. Contradictory shape or HCP requirements fail immediately; if North
hands repeatedly leave no eligible South hand, the generator stops after
`--max-tries` draws per deal and reports the failure. The selection is
conditional on the requested constraints and is not a natural-frequency
estimate or a uniform distribution over all qualifying N/S pairs.

## IV Scanner in the local web workspace

Open **IV Scanner** beside System Editor and Table. It reads existing coverage
reports and can start a new North-1NT scan in the background. The scan sweeps
all twenty-three South shapes from the standard shape-probability table (rows
1–22 and 24), South's HCP range, the number of independent N/S pairs per cell,
E/W completions per pair, and a reproducible seed. The default is ten E/W
completions. Progress remains visible while the other pages are usable;
completed reports are saved under `reports/block_scans/`.

The four finding filters are: **Block**, no supported next call; **丢**, a game
or slam is available more than 30% of comparable DDS boards but was not bid;
**宕**, the chosen contract fails on more than 50%; and **错**, the selected
game's success odds divided by the best alternative game's success odds is
below 0.8. Success odds are `success / failure` across all comparable boards.
Comparable hands have the same named-suit shapes and each seat's complete HCP
and K–R spans stay within two points. The browser omits bulky DDS tables,
merges findings from the same N/S cell, and shows the sampled N/S pairs against
their E/W completions in a horizontally scrollable matrix. The selected
auction is rendered in rows of four calls, alongside numbered N/S hands,
warning rates, alternative games, and the number of DDS boards. The saved JSON
and standalone HTML retain full evidence.

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
