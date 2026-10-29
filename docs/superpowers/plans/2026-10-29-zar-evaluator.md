# Conservative Zar Evaluator Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an independently callable conservative Zar evaluator without changing any current bidding, axiom, profile, scanner, or K–R behavior.

**Architecture:** Create one pure engine module containing immutable fit-context and result types plus a single evaluator function. Keep base scoring and conservative fit scoring in the same small module because they share validation and result assembly, while leaving M4 and decision integration explicitly out of scope.

**Tech Stack:** Python 3, frozen dataclasses, existing `engine.cards.Hand`, `unittest`.

---

## File map

- Create `backend/engine/zar.py`: public dataclasses, validation, base score, and conservative fit adjustments.
- Create `backend/tests/test_zar.py`: focused unit and validation tests for the public API.
- Modify `docs/03_engine_architecture.md`: list the independent evaluator beside K–R.
- Modify `docs/11_axioms.md`: document score semantics and state that no axiom calls it yet.

Existing dirty IV Scanner files are unrelated and must not be staged or edited.
Every command below starts at the repository root unless it uses
`Push-Location backend; ...; Pop-Location` explicitly.

## Chunk 1: Evaluator and regression verification

### Task 1: Base Zar evaluation

**Files:**
- Create: `backend/tests/test_zar.py`
- Create: `backend/engine/zar.py`

- [x] **Step 1: Write failing base-score tests**

Create `backend/tests/test_zar.py` with imports deliberately targeting the
missing module and tests equivalent to:

```python
import unittest
from dataclasses import FrozenInstanceError, fields

from engine.cards import Hand


class ZarEvaluationTests(unittest.TestCase):
    def evaluate(self, compact, fit=None):
        from engine.zar import evaluate_zar
        return evaluate_zar(Hand.parse(compact), fit)

    def test_base_score_separates_hcp_controls_and_shape(self):
        result = self.evaluate('SAJ975HK864DQ32C4')  # 5431
        self.assertEqual(result.version, 'conservative')
        self.assertEqual(result.hcp, 10)
        self.assertEqual(result.controls, 3)
        self.assertEqual(result.shape_points, 13)
        self.assertEqual(result.base_points, 26)
        self.assertEqual(result.primary_fit_points, 0)
        self.assertEqual(result.secondary_fit_points, 0)
        self.assertEqual(result.total_points, 26)

    def test_shape_points_cover_representative_distributions(self):
        cases = {
            'SAKQJH432D432C432': 8,       # 4333
            'SAKQJH5432D432C32': 10,     # 4432
            'SAKQJ9H432D432C32': 11,     # 5332
            'SAKQJ9H5432D32C32': 12,     # 5422
            'SAKQJ9H5432D432C2': 13,     # 5431
            'SAKQJT98765432H-D-C-': 26,  # 13-0-0-0
        }
        for compact, expected in cases.items():
            with self.subTest(compact=compact):
                self.assertEqual(self.evaluate(compact).shape_points, expected)

    def test_base_shape_is_invariant_under_suit_permutation(self):
        first = self.evaluate('SAKQJ9H5432D432C2')
        second = self.evaluate('S2H432DAKQJ9C5432')
        self.assertEqual(first.shape_points, second.shape_points)
        self.assertEqual(first.base_points, second.base_points)

    def test_controls_weight_aces_twice_and_kings_once(self):
        self.assertEqual(self.evaluate('SA432HA432D432C32').controls, 4)
        self.assertEqual(self.evaluate('SK432HK432D432C32').controls, 2)

    def test_public_result_is_frozen_with_exact_ordered_fields(self):
        from engine.zar import ZarFitContext
        result = self.evaluate('SAJ975HK864DQ32C4')
        self.assertEqual(
            tuple(field.name for field in fields(result)),
            ('version', 'hcp', 'controls', 'shape_points', 'base_points',
             'primary_fit_points', 'secondary_fit_points', 'total_points'),
        )
        with self.assertRaises(FrozenInstanceError):
            result.total_points = 0
        context = ZarFitContext('S', 8)
        with self.assertRaises(FrozenInstanceError):
            context.combined_trumps = 9
```

Use only valid 13-card compact hands. Correct any example whose rank count is
not 13 before running the test; do not weaken `Hand.parse` validation.

- [x] **Step 2: Run the focused test and verify RED**

Run from the repository root:

```powershell
Push-Location backend; python -m unittest tests.test_zar -v; Pop-Location
```

Expected: FAIL because `engine.zar` does not exist.

- [x] **Step 3: Implement immutable result types and base score**

Create `backend/engine/zar.py`:

```python
"""Conservative Zar hand and fit evaluation.

This module is independent of bidding decisions. Base scoring follows Zar
Petkov; fit adjustments use the documented conservative variant.
"""

from __future__ import annotations

from dataclasses import dataclass

from .cards import Hand


VERSION = 'conservative'


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
    lengths = sorted((hand.length(suit) for suit in 'SHDC'), reverse=True)
    longest, second, _, shortest = lengths
    controls = 2 * hand.ace_count() + hand.king_count()
    shape_points = longest + second + longest - shortest
    base_points = hand.hcp + controls + shape_points
    primary_fit_points = 0
    secondary_fit_points = 0
    if fit is not None:
        primary_fit_points, secondary_fit_points = _fit_points(hand, fit)
    return ZarEvaluation(
        VERSION, hand.hcp, controls, shape_points, base_points,
        primary_fit_points, secondary_fit_points,
        base_points + primary_fit_points + secondary_fit_points,
    )


def _fit_points(hand: Hand, fit: ZarFitContext) -> tuple[int, int]:
    raise NotImplementedError('fit scoring is added in Task 2')
```

Do not export or register the evaluator anywhere else.

- [x] **Step 4: Run base tests and verify GREEN**

Run:

```powershell
Push-Location backend; python -m unittest tests.test_zar -v; Pop-Location
```

Expected: all current base tests PASS.

- [x] **Step 5: Commit the base evaluator**

```powershell
git add -- backend/engine/zar.py backend/tests/test_zar.py
git commit -m "feat: add base Zar hand evaluation"
```

### Task 2: Conservative primary and secondary fit scoring

**Files:**
- Modify: `backend/tests/test_zar.py`
- Modify: `backend/engine/zar.py`

- [x] **Step 1: Write failing primary-fit tests**

Add tests that import `ZarFitContext` and assert:

```python
def test_primary_fit_uses_side_suit_shortage(self):
    from engine.zar import ZarFitContext
    cases = (
        ('SAKQ2H8765432D32C-', 9, 2),
        ('SAKQ2H8765432D32C-', 10, 4),
        ('SAKQ2H876543D32C4', 9, 1),
        ('SAKQ2H876543D32C4', 10, 2),
        ('SAKQ2H8765D432C32', 9, 0),
        ('SAKQ2H8765D432C32', 10, 0),
    )
    for compact, combined, expected in cases:
        with self.subTest(compact=compact, combined=combined):
            result = self.evaluate(compact, ZarFitContext('H', combined))
            self.assertEqual(result.primary_fit_points, expected)

def test_eight_card_fit_adds_nothing(self):
    from engine.zar import ZarFitContext
    result = self.evaluate('SAKQ2H876543D32C4', ZarFitContext('H', 8))
    self.assertEqual(result.primary_fit_points, 0)

def test_invalid_primary_fit_contexts_are_rejected(self):
    from engine.zar import ZarFitContext
    ordinary = 'SAKQ2H876D432C543'
    nine_spades = 'SAKQJT9876H32D2C2'
    cases = (
        (ordinary, ZarFitContext('X', 8), 'Unknown suit'),
        (ordinary, ZarFitContext('S', True), 'combined_trumps'),
        (ordinary, ZarFitContext('S', 8.5), 'combined_trumps'),
        (ordinary, ZarFitContext('S', -1), 'combined_trumps'),
        (ordinary, ZarFitContext('S', 14), 'combined_trumps'),
        (ordinary, ZarFitContext('S', 7), 'eight-card fit'),
        (nine_spades, ZarFitContext('S', 8), 'own trumps'),
    )
    for compact, context, message in cases:
        with self.subTest(compact=compact, context=context):
            with self.assertRaisesRegex(ValueError, message):
                self.evaluate(compact, context)
```

Ensure all literal hands contain 13 cards. Expected formula is
`max(combined_trumps - 8, 0) * shortage_rate`, where shortage rate is 2 for a
side-suit void, 1 for a side-suit singleton, and 0 otherwise.

- [x] **Step 2: Run primary-fit tests and verify RED**

Run:

```powershell
Push-Location backend; python -m unittest tests.test_zar -v; Pop-Location
```

Expected: primary scoring and primary validation tests FAIL because
`_fit_points` raises `NotImplementedError`.

- [x] **Step 3: Implement primary-fit normalization and scoring**

In `backend/engine/zar.py`, import `normalize_suit_name`. Add a strict length
validator that rejects booleans and non-integers. Normalize the trump suit,
require combined length `8..13`, require it not be below the evaluated hand's
length, and compute the minimum of the three side-suit lengths.

Minimal shape:

```python
def _card_count(value: object, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f'{field} must be an integer')
    if not 0 <= value <= 13:
        raise ValueError(f'{field} must be in 0..13')
    return value


def _fit_points(hand: Hand, fit: ZarFitContext) -> tuple[int, int]:
    trump = normalize_suit_name(fit.trump_suit)
    combined_trumps = _card_count(fit.combined_trumps, 'combined_trumps')
    if combined_trumps < 8:
        raise ValueError('combined_trumps must describe an eight-card fit')
    own_trumps = hand.length(trump)
    if combined_trumps < own_trumps:
        raise ValueError('combined_trumps cannot be shorter than own trumps')
    shortest_side = min(hand.length(suit) for suit in 'SHDC'
                        if normalize_suit_name(suit) != trump)
    rate = 2 if shortest_side == 0 else 1 if shortest_side == 1 else 0
    primary = (combined_trumps - 8) * rate
    # Secondary validation and score are added after their failing tests.
    if fit.secondary_suit is not None or fit.combined_secondary is not None:
        raise NotImplementedError('secondary fit scoring not implemented')
    return primary, 0
```

- [x] **Step 4: Run focused tests and verify GREEN**

Run:

```powershell
Push-Location backend; python -m unittest tests.test_zar -v; Pop-Location
```

Expected: all tests written so far PASS.

- [x] **Step 5: Write the failing secondary-score test**

Add only the happy-path scoring test first:

```python
def test_secondary_fit_points_are_capped_at_two(self):
    from engine.zar import ZarFitContext
    cases = (
        ('SAKQ2H876D432C543', 8, 0),
        ('SAKQ2H876D432C543', 9, 1),
        ('SAKQ2H876D432C543', 10, 2),
        # Five own hearts leave exactly eight partner hearts; with five
        # partner spades the two implied holdings total a legal thirteen.
        ('SAKQ2H87654D32C43', 13, 2),
    )
    for compact, combined, expected in cases:
        with self.subTest(compact=compact, combined=combined):
            result = self.evaluate(
                compact, ZarFitContext('S', 9, 'H', combined),
            )
            self.assertEqual(result.secondary_fit_points, expected)
            self.assertEqual(
                result.total_points,
                result.base_points + result.primary_fit_points + expected,
            )

def test_unknown_secondary_suit_is_rejected(self):
    from engine.zar import ZarFitContext
    with self.assertRaisesRegex(ValueError, 'Unknown suit'):
        self.evaluate(
            'SAKQ2H876D432C543', ZarFitContext('S', 9, 'X', 8),
        )
```

- [x] **Step 6: Run the secondary-score test and verify RED**

```powershell
Push-Location backend; python -m unittest tests.test_zar -v; Pop-Location
```

Expected: the score and unknown-secondary tests both FAIL on the deliberate
secondary `NotImplementedError`.

- [x] **Step 7: Implement the secondary happy path**

Replace the secondary `NotImplementedError` branch with the minimal scoring
needed for valid, complete contexts:

```python
if fit.secondary_suit is None and fit.combined_secondary is None:
    return primary, 0
secondary = normalize_suit_name(fit.secondary_suit)
combined_secondary = fit.combined_secondary
secondary_points = (0 if combined_secondary == 8
                    else 1 if combined_secondary == 9 else 2)
return primary, secondary_points
```

- [x] **Step 8: Run the secondary-score test and verify GREEN**

```powershell
Push-Location backend; python -m unittest tests.test_zar -v; Pop-Location
```

Expected: both newly added tests PASS.

- [x] **Step 9: Write the failing paired-field and suit test**

```python
def test_secondary_fields_and_suits_are_validated(self):
    from engine.zar import ZarFitContext
    compact = 'SAKQ2H876D432C543'
    cases = (
        (ZarFitContext('S', 9, 'H', None), 'supplied together'),
        (ZarFitContext('S', 9, None, 8), 'supplied together'),
        (ZarFitContext('S', 9, 'S', 9), 'differ'),
    )
    for context, message in cases:
        with self.subTest(context=context):
            with self.assertRaisesRegex(ValueError, message):
                self.evaluate(compact, context)
```

- [x] **Step 10: Run paired-field and suit test to verify RED**

```powershell
Push-Location backend; python -m unittest tests.test_zar.ZarEvaluationTests.test_secondary_fields_and_suits_are_validated -v; Pop-Location
```

Expected: FAIL because incomplete and same-suit contexts are not rejected with
the specified errors.

- [x] **Step 11: Implement paired-field and suit validation**

Add this before normalizing the secondary suit:

```python
secondary_present = fit.secondary_suit is not None
secondary_length_present = fit.combined_secondary is not None
if secondary_present != secondary_length_present:
    raise ValueError('secondary_suit and combined_secondary must be supplied together')
if not secondary_present:
    return primary, 0
secondary = normalize_suit_name(fit.secondary_suit)
if secondary == trump:
    raise ValueError('secondary_suit must differ from trump_suit')
```

- [x] **Step 12: Run paired-field and suit test to verify GREEN**

```powershell
Push-Location backend; python -m unittest tests.test_zar.ZarEvaluationTests.test_secondary_fields_and_suits_are_validated -v; Pop-Location
```

Expected: PASS.

- [x] **Step 13: Write the failing secondary-length test**

```python
def test_secondary_length_is_a_legal_known_fit(self):
    from engine.zar import ZarFitContext
    ordinary = 'SAKQ2H876D432C543'
    nine_spades = 'SAKQJT9876H32D2C2'
    cases = (
        (ordinary, ZarFitContext('S', 9, 'H', True), 'combined_secondary'),
        (ordinary, ZarFitContext('S', 9, 'H', 7), 'eight-card fit'),
        (ordinary, ZarFitContext('S', 9, 'H', 14), 'combined_secondary'),
        (nine_spades, ZarFitContext('H', 8, 'S', 8), 'own secondary'),
    )
    for compact, context, message in cases:
        with self.subTest(compact=compact, context=context):
            with self.assertRaisesRegex(ValueError, message):
                self.evaluate(compact, context)
```

- [x] **Step 14: Run secondary-length test to verify RED**

```powershell
Push-Location backend; python -m unittest tests.test_zar.ZarEvaluationTests.test_secondary_length_is_a_legal_known_fit -v; Pop-Location
```

Expected: FAIL because secondary lengths are not yet type-, range-, or
own-holding-validated.

- [x] **Step 15: Implement secondary-length validation**

Add:

```python
combined_secondary = _card_count(fit.combined_secondary, 'combined_secondary')
if combined_secondary < 8:
    raise ValueError('combined_secondary must describe an eight-card fit')
own_secondary = hand.length(secondary)
if combined_secondary < own_secondary:
    raise ValueError('combined_secondary cannot be shorter than own secondary holding')
```

- [x] **Step 16: Run secondary-length test to verify GREEN**

```powershell
Push-Location backend; python -m unittest tests.test_zar.ZarEvaluationTests.test_secondary_length_is_a_legal_known_fit -v; Pop-Location
```

Expected: PASS.

- [x] **Step 17: Write the failing three-card-participation test**

```python
def test_secondary_fit_requires_three_cards_in_each_hand(self):
    from engine.zar import ZarFitContext
    cases = (
        ('SAKQ2H8765D432C32', ZarFitContext('S', 9, 'C', 8)),
        ('SAKQJT98H876D32C4', ZarFitContext('H', 8, 'S', 8)),
    )
    for compact, context in cases:
        with self.subTest(compact=compact):
            with self.assertRaisesRegex(ValueError, 'each hand'):
                self.evaluate(compact, context)
```

- [x] **Step 18: Run three-card-participation test to verify RED**

```powershell
Push-Location backend; python -m unittest tests.test_zar.ZarEvaluationTests.test_secondary_fit_requires_three_cards_in_each_hand -v; Pop-Location
```

Expected: FAIL because a one- or two-card holding is still accepted.

- [x] **Step 19: Implement three-card participation validation**

Add:

```python
partner_secondary = combined_secondary - own_secondary
if own_secondary < 3 or partner_secondary < 3:
    raise ValueError('secondary fit requires at least three cards in each hand')
```

- [x] **Step 20: Run three-card-participation test to verify GREEN**

```powershell
Push-Location backend; python -m unittest tests.test_zar.ZarEvaluationTests.test_secondary_fit_requires_three_cards_in_each_hand -v; Pop-Location
```

Expected: PASS.

- [x] **Step 21: Write the failing joint partner-length test**

```python
def test_two_fits_cannot_require_more_than_thirteen_partner_cards(self):
    from engine.zar import ZarFitContext
    with self.assertRaisesRegex(ValueError, 'thirteen partner cards'):
        self.evaluate(
            'SAKQ2H876D432C543',
            ZarFitContext('S', 13, 'H', 10),
        )
```

- [x] **Step 22: Run joint partner-length test to verify RED**

```powershell
Push-Location backend; python -m unittest tests.test_zar.ZarEvaluationTests.test_two_fits_cannot_require_more_than_thirteen_partner_cards -v; Pop-Location
```

Expected: FAIL because the impossible context is accepted.

- [x] **Step 23: Implement joint partner-length validation**

Add:

```python
partner_trumps = combined_trumps - own_trumps
if partner_trumps + partner_secondary > 13:
    raise ValueError('combined fits require more than thirteen partner cards')
```

- [x] **Step 24: Run the full evaluator file to verify GREEN**

```powershell
Push-Location backend; python -m unittest tests.test_zar -v; Pop-Location
```

Expected: all Zar tests PASS with no warnings.

- [x] **Step 25: Commit conservative fit scoring**

```powershell
git add -- backend/engine/zar.py backend/tests/test_zar.py
git commit -m "feat: add conservative Zar fit adjustments"
```

### Task 3: Documentation and complete verification

**Files:**
- Modify: `docs/03_engine_architecture.md`
- Modify: `docs/11_axioms.md`

- [x] **Step 1: Document module ownership and non-integration**

In `docs/03_engine_architecture.md`, add `backend/engine/zar.py` beside
`hand_quality.py` and state:

```text
Implements base Zar and conservative fit adjustments as an independent service.
It is not registered with BSL, profiles, axioms, scanners, or bidding selection.
```

In `docs/11_axioms.md`, after the K–R section, document:

- the base formula;
- conservative primary and secondary fit tables;
- the component result fields;
- M4 and original `+3` super-fit are intentionally absent;
- no axiom currently consumes Zar;
- the selected conservative fit table source:
  <https://en.wikipedia.org/wiki/Zar_Points>.

- [x] **Step 2: Run focused evaluator and K–R regression tests**

Run from the repository root:

```powershell
Push-Location backend; python -m unittest tests.test_zar tests.test_hand_quality tests.test_axioms tests.test_axiom_integration -v; Pop-Location
```

Expected: all tests PASS. Existing K–R outputs remain unchanged.

- [x] **Step 3: Run the full backend suite**

Run from the repository root:

```powershell
Push-Location backend; python -m unittest discover -s tests -v; Pop-Location
```

Expected: full suite PASS. If an unrelated pre-existing failure appears, record
the exact test and verify it also fails on the pre-Zar commit before deciding
whether it belongs to this work.

- [x] **Step 4: Check the diff for accidental integration or unrelated files**

Run from repository root:

```powershell
git diff --check
git status --short
git diff -- backend/engine/zar.py backend/tests/test_zar.py docs/03_engine_architecture.md docs/11_axioms.md
rg -n "engine\.zar|from \.zar|import zar" backend --glob '!backend/engine/zar.py' --glob '!backend/tests/test_zar.py'
```

Expected: no whitespace errors; no existing IV Scanner files are staged or
modified by this implementation; the final search prints no call-site imports
of `engine.zar`.

- [x] **Step 5: Commit documentation**

```powershell
git add -- docs/03_engine_architecture.md docs/11_axioms.md
git commit -m "docs: describe conservative Zar evaluation"
```

- [x] **Step 6: Report the available API**

Handoff must state that callers may import:

```python
from engine.zar import ZarFitContext, evaluate_zar
```

and that the feature is deliberately not active in bidding yet.

## Execution record (2026-10-29)

- All 36 steps executed on branch `feature/zar-evaluator`
  (commits `b612e48`, `f6e42b4`, `7c97a6b`) and merged into `main`.
- `backend/tests/test_zar.py`: 20 tests PASS.
- Full backend suite on the merged `main`: 448 tests PASS (skipped=1).
- Spec examples re-verified against `evaluate_zar`:
  - a four-spade hand with `S/9` is accepted;
  - `S/9` plus `C/8` is accepted;
  - `S/13` plus `C/10` is rejected (implied partner lengths exceed 13 cards);
  - a one-card secondary holding is rejected by the three-card
    participation rule.
- No call site imports `engine.zar`; it stays an independent service.
- Available API: `from engine.zar import ZarFitContext, evaluate_zar`.
  Deliberately not wired into bidding, axioms, profiles, scanners, or K–R
  in this release.
