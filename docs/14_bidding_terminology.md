# Bidding Terminology Glossary

Date: 2026-10-22
Status: shared vocabulary with reusable runtime evidence; profile thresholds remain scoped.

This glossary records explicitly supplied definitions. Definitions that can vary
between profiles must retain their scope. A term is not permission to substitute
an approximate numeric test without the profile author's confirmation.

## Confirmed vocabulary

| Term | Owner's definition | Scope / caution |
| --- | --- | --- |
| 有大牌 / an honor for this phrase | Q or higher: Q, K, A | Owner's general bidding terminology, supplied with Daqiush 2/1. J does not qualify for this phrase. This does not change ordinary HCP or K-R calculations. |
| 硬点 / hard values | Many A/K, few Q/J, concentrated honors | Daqiush: qualitative definition confirmed; exact predicate not yet specified. |
| 14+ / 17− / 点力软 | Evaluate using K-R | Daqiush has approved provisional opening cutoffs in its profile notes; these are not universal thresholds. |
| 绝对高限 / absolute maximum | Raw HCP minus the confirmed Q/J wastage deductions; 16 remaining with four trumps or 15 with five | Daqiush: see the exact formula and positive examples in the profile notes; independent of opening K-R cutoffs. |
| 扣叫 / cue bid | Meaning depends on the active auction branch | Daqiush: normally a second-round-or-better control, but forced, space-limited, partner-suit and other explicit exceptions apply; see slam notes. |
| 临界 / borderline | Calibration label requiring an explicit action before execution | Do not silently convert or randomize. The owner subsequently resolved B/D to no 1NT; they are no longer pending borderline cases. |
| 罕有 / rare | Uncommon but permitted in principle | Daqiush 1NT: 5M4m31 and singleton A are not categorically banned; rarity alone gives no executable threshold or sampling probability. |

## Reusable hand-quality principles

The owner requested that these concepts remain available for later agreements,
not only the Daqiush 1NT opening. Preserve the qualitative meaning separately
from each profile's numerical selection rules.

- **Hard values:** many A/K, few Q/J, and concentrated honors. Retain the
  actual holdings as evidence, not just a total score.
- **Soft values:** the contrasting tendency toward Q/J-heavy values and
  vulnerable or unsupported honors. This is a qualitative interpretation of
  the owner's descriptions and calibration hands; a universal threshold has
  not been agreed.
- **Good/bad points at equal HCP:** consider honor concentration, honors in
  long/partner suits versus short/opponent suits, A/K versus Q/J, and shape,
  as the owner specified for the hand-quality axiom.
- **Wastage is contextual:** keep suit fit and auction information explicit.
  Do not equate every Q/J with wasted points or every short-suit honor with
  the same penalty. Use only information available to the acting player.
- **K-R is a broader evaluation:** pure K-R includes more than honor hardness.
  Keep HCP, K-R and their difference distinct. A higher K-R score does not
  automatically make a hand a better candidate for a particular opening.
- **Scope numerical rules:** the confirmed doubleton Q/J and unsupported
  Q/J deductions in the Daqiush absolute-maximum test start from raw HCP.
  Do not subtract them again from K-R or apply the four/five-trump thresholds
  to unrelated decisions. Other profiles may explicitly reuse the calculation.
- **Long-suit dominance in a 7–4 hand:** when the four-card side suit is poor
  and the seven-card primary suit is strong, compare slam completion in both
  strains over the same deals compatible with the public auction. If the
  seven-card suit performs better even when partner has four-plus cards in
  the side suit, treat the side suit as absent for route selection. This is a
  reusable bidding principle, not a fixed suit-quality or HCP cutoff. The
  first executable instance is Daqiush's Stayman major-fit versus long-minor
  choice; it samples unknown hands and never reads the actual partner hand.

The A–M calibration review in the Daqiush notes records why a single K-R opening
interval is insufficient. The owner confirmed different standards for ordinary
HCP-range soft hands and 14-HCP upgrade candidates: G opens 1NT; B/D do not.
The subsequently approved initial cutoffs are stored in that profile's BSL
gadget; they do not establish universal cutoffs for other bidding contexts.

### Runtime access

BSL conditions and policies can read `ctx.hand_quality` for existing K-R evidence
and `ctx.honor_texture` for per-suit holdings, A/K and Q/J counts and the named
`daqiush_qj_discount_v1` model. The latter reports `hcp`, `deduction`, and
`adjusted_hcp`, with individual deduction reasons. Both use only the acting
player's hand; both return `None` when that hand is unavailable. No generic
hard/soft boolean or partner's actual cards are supplied.

The support thresholds (four trumps: 16; five: 15) live in the Daqiush gadget,
not the generic evaluator. No new singleton penalty is invented by the Q/J
model; this does not assert that singleton honors are never wasted in play.

## Awaiting precise definitions for Daqiush 2/1

- 好套 (good suit): holdings, length, or an approved evaluator/test.
- 硬点 (hard points): executable thresholds for the confirmed qualitative definition.
- 废点 / 无废点 (wasted points / no wasted points): suit/holding context.
- 14+ / 17− / 点力很软 outside the approved initial 1NT cutoffs: contextual boundaries.
- 低限 / 非低限 / 高限: ranges and qualitative boundary rules; absolute maximum for four/five-card support is now defined separately.
- 有大牌非单张大牌: exact supported-suit length/holding requirement.
- QT以上: exact stopper holding/length for the specified auction branch.
- 全控制: which first-/second-round controls, and which suits must qualify.

See [Daqiush 2/1 notes](13_daqiush_2over1.md) for the source and clarification
register. Existing general Axiom behavior remains documented in
[Axioms](11_axioms.md); importing a term here does not change it.

Detailed cue-bidding, control, keycard and quantitative-invitation terms are
recorded in [Daqiush slam agreements](15_daqiush_slam.md). Their explicit
exceptions take precedence over a simplified glossary description.
