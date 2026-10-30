# Daqiush Quantitative Inquiry Routes Design

**Date:** 2026-10-30  
**Status:** Approved design; implementation pending  
**Scope:** Two uncontested Daqiush 1NT response routes and their explicitly
enumerated quantitative continuations.

## Goal

Add the currently missing good-16–17 responder routes without attempting the
larger redesign of all quantitative 4NT continuations:

1. selected hands use the 3C five-card-major inquiry before a quantitative 4NT;
2. the exact 4-3-2-4 hand class uses Stayman before a quantitative 4NT;
3. a Stayman reply can reveal an unshown spade fit, allowing opener to use 5C,
   ask for aces, and then place the partnership in the appropriate slam strain;
4. all behavior added in this slice is explicitly authored and testable.

The existing definition of a **good 16–17 HCP** hand remains authoritative. This
work does not relax or replace its HCP or K–R/quality boundary.

Shape notation in this document is spades-hearts-diamonds-clubs.

## Approach

Use small reusable predicates for the two responder families, but author their
calls and continuations explicitly in the existing Daqiush gadgets. This avoids
duplicating the quality boundary while also avoiding a premature general-purpose
quantitative inference engine.

Rejected alternatives:

- isolated auction-string special cases would be quick but would duplicate the
  same hand definition and invite priority conflicts;
- deriving every quantitative continuation globally is desirable later, but its
  interaction with natural 4NT, RKCB, NFRKCB, strain selection, interference,
  and simulation is larger than this bounded change.

## 3C Inquiry Family

### Eligibility

A good 16–17 HCP responder uses 3C when either condition holds:

1. `max(H,S) <= 3` and `max(C,D) <= 4`; this includes 3-3-3-4,
   2-3-4-4, and 3-2-4-4, while explicitly excluding every 5M, 5m, and 6m
   hand; or
2. responder is 4M-3-3-3.

These hands must be admitted to the existing five-card-major inquiry instead of
being captured first by generic 3NT, Stayman, or minor routes.

### After 3D

`1NT-Pass-3C-Pass-3D-Pass-4NT` is a natural quantitative invitation. It does not
set trumps and is not RKCB.

### After a shown five-card major

After `1NT-Pass-3C-Pass-3M-Pass`:

- with three or more cards in opener's shown major, responder makes the lowest
  legal other-major call to show the fit and slam interest:
  - after 3H, bid 3S;
  - after 3S, bid 4H;
- this artificial call immediately agrees opener's shown major as trumps;
- without three-card support, responder bids the natural quantitative 4NT.

The fit-showing call must outrank/suppress the existing simple 4M game placement
for this good-16–17 family. Other five-major-inquiry hand families retain their
current meanings and priorities. This specification supersedes the earlier
“leave 3S-4H unimplemented” restriction in `docs/15_daqiush_slam.md` only for
this exact good-16–17/three-card-support family. After the fit-showing call, the
agreed-major state and existing cue/keycard derivation may continue the auction;
if those mechanisms produce no unique supported call, the auction must TD rather
than invent a continuation.

## 2C Stayman Family

### Eligibility and public promise

The explicitly implemented hand in this slice is a good 16–17 HCP 4-3-2-4
responder. It begins with 2C.

After opener replies 2D or 2H, responder bids 4NT. This sequence publicly
promises:

- a four-card major;
- a non-4M-3-3-3 shape.

After a 2H reply, responder has no heart fit, so the promised four-card major is
spades. After a 2D reply opener has denied a four-card major, so no major fit is
available. After a 2S reply the partnership has already found a spade fit and
uses the existing fit-slam route instead of quantitative 4NT.

The new 4NT call must suppress the existing generic 3NT placement for this exact
family.

## Enumerated Quantitative 5C Continuation

This implementation deliberately enumerates the agreed continuation rather than
generalizing all quantitative auctions.

### Exact auction scope

The continuation in this section is authored only after these three prefixes:

- `1NT-Pass-2C-Pass-2D-Pass-4NT-Pass`;
- `1NT-Pass-2C-Pass-2H-Pass-4NT-Pass`;
- `1NT-Pass-3C-Pass-3D-Pass-4NT-Pass`.

It must not manufacture 5C after any other quantitative 4NT. Those auctions
remain governed by their existing authored calls or TD until the deferred general
redesign is approved.

### Meaning and selection of 5C

After a quantitative 4NT, opener's 5C means:

- opener accepts continued slam investigation;
- opener has an unshown distributional feature and is unwilling to place 6NT
  immediately;
- responder must answer aces and does not yet try to identify opener's feature.

The hidden feature is not restricted to four spades. Eligibility is fixed by
prefix; no feature may leak from one row into another:

| Prefix ending in quantitative 4NT | Features eligible for 5C and later natural description |
| --- | --- |
| `1NT-2C-2D-4NT` | at least five clubs or at least five diamonds |
| `1NT-2C-2H-4NT` | exactly four spades, at least five clubs, at least five diamonds, or at least five hearts |
| `1NT-3C-3D-4NT` | at least five clubs or at least five diamonds |

Only the `2C-2H-4NT` row publicly guarantees responder four spades. Therefore
only that row can treat opener's four spades as a known fit, expose 6S, or use
5S as the strain-aware stop. Any other feature remains unsupported until
explicitly authored.

For each exact prefix, the implementation enumerates only the legal feature
calls above and asks the existing public-information simulation selector to
compare the associated six-level strain against the notrump alternatives. If
multiple features are present, the selector chooses the candidate with the best
expected result; an exact tie uses the existing stable call-order tie break. If
simulation is unavailable, times out, or cannot distinguish a supported choice,
the bidder retains an already-authored deterministic quantitative action when
one exists; otherwise it TDs. It must not guess which feature to show.

The ace responses use the agreed steps:

- 5D = one or four aces;
- 5H = zero or three aces;
- 5S = two aces.

### Missing two aces

Only the four aces are counted; a trump king or any other keycard is irrelevant
to this quantitative ace check. Opener combines responder's answer with opener's
own aces and the physically possible public deal completions. “Missing two aces”
means **missing at least two**. If every compatible interpretation is missing at
least two aces, opener stops below slam:

- 5NT is the ordinary notrump stop;
- with the revealed spade fit, opener may stop in 5S;
- when the artificial ace response itself is 5S, Pass is the corresponding 5S
  stop.

No six-level descriptive call is made in this branch.

When the 1/4 or 0/3 response remains genuinely ambiguous after accounting for
opener's own hand, the selector samples only deals compatible with the public
auction and the response category. It computes the weighted share of compatible
samples in which the partnership is missing fewer than two aces:

- greater than 50%: take the six-level natural-description branch;
- exactly 50% or less: take the appropriate five-level stop;
- no compatible samples, timeout, or sampling failure: take the conservative
  five-level stop.

The stable tie rule is therefore “stop.” No private responder cards may be used
to resolve the category.

### Not missing two aces

If the selected ace interpretation says the partnership is not missing two aces,
opener is committed to a small slam and naturally describes the previously
hidden feature at the six level. The feature-to-call map is explicit:

- five or more clubs -> 6C;
- five or more diamonds -> 6D;
- five or more hearts -> 6H;
- the unshown four-card spade fit -> 6S.

If opener has multiple qualifying features, use the same public-information
simulation ranking and stable tie break that selected 5C. In particular, a
five-card heart suit can be shown by 6H.

These six-level calls are natural strain descriptions and final placements for
this bounded slice. Once opener has made one, the partnership cannot return to a
five-level contract. Responder now knows which feature motivated 5C and the
ordinary purpose/final-contract rule supplies Pass unless a separately authored
correction exists.

The five-level stop is also deterministic: when the known spade fit was the
selected strain, stop in 5S (bid 5S after a 5D/5H answer, or Pass over the
artificial 5S answer); otherwise stop in 5NT. If simulation cannot select the
spade strain, use 5NT or TD according to the existing deterministic-then-TD
fallback and never inspect responder's private hand.

## Simulation Boundary

Where the current simulation selector is available, it may decide whether a
known spade fit makes the 5C route preferable to immediate notrump placement.
The authored bidding meanings must not depend on private information from the
other hands. A simulation failure must not silently reinterpret 4NT or 5C; the
existing deterministic fallback or TD behavior remains in force.

This design does not introduce a new general simulation policy for all
quantitative invitations.

## Implementation Boundaries

Expected profile changes are limited to the existing Daqiush gadgets for:

- the 1NT-3C five-card-major inquiry;
- 1NT invitations/Stayman;
- a small shared helper only if it prevents duplicate good-16–17 predicates.

Do not change global 4NT inference, RKCB, NFRKCB, Voidwood, direct quantitative
responses outside these prefixes, or the current definition of a good hand.

## Validation

Add focused bidder tests proving:

1. all listed 3C shapes select 3C at the retained quality boundary;
2. nearby hands outside the quality boundary retain their existing call;
3. 3D is followed by quantitative 4NT;
4. a 3H fit uses 3S and a 3S fit uses 4H;
5. a shown five-card major without three-card support is followed by 4NT;
6. good 4-3-2-4 selects 2C and then 4NT over both 2D and 2H;
7. the same hand follows the existing fit route over 2S;
8. the 2H-4NT public meaning guarantees four spades and excludes 4M-3-3-3;
9. 5C is not explained as four spades only;
10. 5C is authored only after the three enumerated prefixes;
11. all three ace answers are selected correctly and count ordinary aces only;
12. partnership ace totals from zero through four take the correct branch,
    including ambiguous 1/4 and 0/3 categories without private-hand leakage;
13. missing-at-least-two-aces cases stop deterministically in 5NT or, with the
    selected known fit, 5S/Pass;
14. non-missing-two-aces cases naturally place 6C, 6D, 6H, or 6S;
15. hands with multiple eligible hidden features use simulation and stable
    tie-breaking, while unsupported/simulation-failure cases follow the stated
    fallback or TD;
16. 5M, 5m, and 6m boundary hands do not enter the new 3C family;
17. existing five-major inquiry, Stayman, quantitative, RKCB, and final-contract
    regression tests continue to pass.

## Deferred Quantitative Redesign

A later design must replace the enumerated continuation with a reusable
quantitative-invitation model covering:

- the full set of meanings for Pass, 5C, and direct 5D–5S responses;
- arbitrary hidden extra shapes;
- ace-answer interpretation and legal-space changes;
- five-level strain-aware stops;
- natural six-level descriptions and subsequent corrections;
- interference;
- simulation and deterministic fallback;
- clean separation from RKCB, NFRKCB, Voidwood, and natural 4NT.

That redesign is explicitly out of scope for this implementation.
