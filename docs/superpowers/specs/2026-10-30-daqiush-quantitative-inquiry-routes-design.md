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

1. responder has no four-card major and no five-card minor; this includes
   3-3-3-4, 2-3-4-4, and 3-2-4-4; or
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
current meanings and priorities.

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

### Meaning of 5C

After a quantitative 4NT, opener's 5C means:

- opener accepts continued slam investigation;
- opener has an unshown distributional feature and is unwilling to place 6NT
  immediately;
- responder must answer aces and does not yet try to identify opener's feature.

The hidden feature is not restricted to four spades. In the covered Stayman
route it can include:

- four spades;
- a five-card club or diamond suit;
- five hearts;
- any other feature must remain unsupported until explicitly authored.

The ace responses use the agreed steps:

- 5D = one or four aces;
- 5H = zero or three aces;
- 5S = two aces.

### Missing two aces

Opener combines responder's answer with opener's own aces. If the partnership is
missing two aces, opener stops below slam:

- 5NT is the ordinary notrump stop;
- with the revealed spade fit, opener may stop in 5S;
- when the artificial ace response itself is 5S, Pass is the corresponding 5S
  stop.

No six-level descriptive call is made in this branch.

### Not missing two aces

If the partnership is not missing two aces, opener is committed to a small slam
and naturally describes the previously hidden feature at the six level. Covered
calls include 6C, 6D, 6H, and 6S as the hand requires. In particular, a five-card
heart suit can be shown by 6H.

These six-level calls are natural strain descriptions and final placements for
this bounded slice. Once opener has made one, the partnership cannot return to a
five-level contract. Responder now knows which feature motivated 5C and the
ordinary purpose/final-contract rule supplies Pass unless a separately authored
correction exists.

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
10. all three ace answers are selected correctly;
11. missing-two-aces cases stop in 5NT or, with the known fit, 5S/Pass;
12. non-missing-two-aces cases naturally place 6C, 6D, 6H, or 6S;
13. existing five-major inquiry, Stayman, quantitative, RKCB, and final-contract
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
