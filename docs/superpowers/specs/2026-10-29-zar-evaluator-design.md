# Conservative Zar Evaluator Design

## Goal

Add Zar hand evaluation as an independent, reusable engine service. The first
release exposes scores and their component breakdowns but does not alter any
existing bidding decision, axiom, profile, scanner classification, or K–R
result. Call sites will be chosen separately after the evaluator is available.

## Version boundary

The evaluator uses the conservative fit adjustment commonly documented in
later Zar summaries, not Petkov's original unconditional `+3` for every card
in a fit beyond eight. The selected fit table is the one summarized at
<https://en.wikipedia.org/wiki/Zar_Points>: an extra primary-fit card is worth
2 with a void and 1 with a singleton, while secondary nine- and ten-card fits
are worth 1 and 2 respectively.

The first release includes:

- base Zar evaluation for one hand;
- conservative primary-fit adjustment when combined trump length is known;
- conservative secondary-fit adjustment when combined side-suit length is
  known;
- a structured, inspectable component breakdown.

It excludes:

- Petkov's original aggressive super-fit adjustment;
- M4 joint misfit adjustment;
- opponent-suit, finesse-position, or inferred partner-shape adjustments;
- contract thresholds and automatic bidding decisions.

These exclusions prevent incomplete partner information and overlapping fit
features from silently changing a score.

## Base score

For a hand whose suit lengths sorted from longest to shortest are
`a >= b >= c >= d`:

```text
base_zar = hcp + controls + shape
controls = 2 * aces + kings
shape = (a + b) + (a - d)
```

This makes the effective honor weights `A=6, K=4, Q=2, J=1` before any fit
adjustment. Suit identity does not affect the base score.

## Conservative primary-fit adjustment

Primary-fit adjustment is available only when the caller supplies an agreed
trump suit and a known combined trump length of at least eight.

For each combined trump beyond eight:

- add 2 when the evaluated hand has a void in a side suit;
- add 1 when its shortest side suit is a singleton;
- add 0 when its shortest side suit is a doubleton or longer.

The trump suit is excluded when determining side-suit shortness. At exactly
eight combined trumps the adjustment is zero. The function rejects impossible
combined lengths and inconsistent suit inputs rather than guessing.

## Conservative secondary-fit adjustment

When the caller supplies the combined length of a known secondary fit:

- eight or fewer cards: add 0;
- nine cards: add 1;
- ten or more cards: add 2.

The secondary suit must differ from the agreed trump suit. For this release,
"secondary fit" means both hands hold at least three cards in that suit. This
admits ordinary 5-3, 4-4, 6-3, and similar genuine double fits while excluding
a singleton opposite eight cards, which is a one-sided long suit rather than a
working secondary fit. Consequently, a side suit cannot simultaneously be the
void or singleton that generates the primary-fit adjustment and the known
secondary fit. The adjustment is capped at 2 and does not depend on shortness.
It is omitted when the caller does not know the combined side-suit length.

## Public API

The module is `backend.engine.zar` and exposes these immutable dataclasses and
function:

```python
@dataclass(frozen=True)
class ZarFitContext:
    trump_suit: str
    combined_trumps: int
    secondary_suit: str | None = None
    combined_secondary: int | None = None

@dataclass(frozen=True)
class ZarEvaluation:
    version: str
    hcp: int
    controls: int
    shape_points: int
    base_points: int
    primary_fit_points: int
    secondary_fit_points: int
    total_points: int

def evaluate_zar(hand: Hand, fit: ZarFitContext | None = None) -> ZarEvaluation:
    ...
```

Passing `fit=None` is the only base-only form. A `ZarFitContext` always contains
a complete primary-fit pair (`trump_suit`, `combined_trumps`). The secondary
fields must either both be omitted or both be supplied. Secondary context is
therefore never accepted without an agreed primary trump.

## Public result

The service returns the frozen `ZarEvaluation` with exactly these fields, in
the same order as the public dataclass:

```text
version = "conservative"
hcp
controls
shape_points
base_points
primary_fit_points
secondary_fit_points
total_points
```

The component values are the authoritative explanation. `total_points` is
their sum. Keeping components separate lets future callers avoid counting the
same fit or shortness value twice and allows a later M4 evaluator to remain a
separate joint-hand operation.

## API placement

Create `backend/engine/zar.py` alongside `hand_quality.py`, with no dependency
on profiles or auction state. It accepts the existing immutable `Hand` model
plus explicit fit context. No bidding, BSL, profile, scanner, axiom, or auction
module imports or registers it in this release. As elsewhere in the engine,
the evaluator expects the caller to supply an already valid 13-card `Hand`;
card-set validation remains the responsibility of the existing model/parser.

## Validation and errors

Reject:

- unknown suit identifiers;
- combined lengths that are booleans, non-integers, or outside `0..13`;
- a primary-fit context below eight cards;
- a combined length smaller than the evaluated hand's length in that suit;
- a secondary suit equal to the trump suit;
- exactly one of `secondary_suit` and `combined_secondary` being supplied;
- a secondary combined length below eight;
- a secondary fit in which either the evaluated hand or the implied partner
  has fewer than three cards;
- simultaneous fits whose implied partner lengths in the two named suits sum
  to more than 13.

Omitted fit context means base-only evaluation and is not an error.

For each supplied suit, implied partner length is:

```text
combined length - evaluated hand length
```

It must be an integer in `0..13`. These checks guarantee that explicit fit
context can belong to at least one legal partner hand. They do not try to infer
the partner's remaining two suit lengths.

Examples:

- Hand has four spades; `S/9` is valid and implies five partner spades.
- Hand has four spades and three clubs; `S/9` plus `C/8` is valid and implies
  partner lengths 5-5 in the named suits.
- The same hand with `S/13` plus `C/10` is invalid because it would require
  partner to hold nine spades and seven clubs.
- Hand has one club; `C/9` cannot be supplied as a secondary fit because the
  evaluated hand lacks the required three-card participation.

## Verification

Tests are written before production code and cover:

- representative base shapes: 4333, 4432, 5332, 5422, 5431, and extreme
  distributions;
- control totals and the effective `6-4-2-1` honor weighting;
- invariance under permutation of suit identities for base evaluation;
- exactly eight trumps;
- nine and ten trumps with a void, singleton, or no side-suit shortage;
- secondary fits of eight, nine, and ten cards;
- valid and impossible implied partner lengths across one and two fits;
- rejection of partial fit contexts, booleans, and fractional lengths;
- component totals and version marker;
- all invalid contexts listed above;
- regression confirmation that existing K–R and bidding tests remain green.

## Documentation

Document Zar next to K–R in the engine architecture and axiom documentation,
explicitly stating that it is available but not yet used for decisions. Cite
the selected conservative fit version so future work does not accidentally
replace it with the original aggressive super-fit rule.
