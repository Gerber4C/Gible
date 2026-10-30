# Derived Bidding Semantics Design

**Date:** 2026-10-30  
**Status:** Approved direction; specification and plan only in this cycle  
**Implementation boundary:** This document is not implemented as part of the
ordinary-RKCB work.

## 1. Goal

Profiles should describe agreements and exceptions, not enumerate every
auction prefix. A global derived-semantics layer fills predictable meanings
from public auction structure. It runs after explicit profile meanings and
before fallback/TD.

The layer must be explainable: every inferred call records its rule, public
evidence, candidate trump set, competing interpretations, and confidence. It
must TD rather than silently choose when the rules do not identify one safe
meaning.

## 2. Priority

Meaning priority is:

1. explicit profile meaning;
2. a committed private purpose already established by an earlier call;
3. derived semantics in this document;
4. profile fallback;
5. TD/block behavior.

Derived semantics never rewrites an explicit meaning and never treats the
same call simultaneously as natural and artificial.

## 3. Shared public evidence

The derivation layer builds one immutable evidence object containing:

- current contract and level;
- whose side bid each strain;
- natural long suits and supported suits;
- unset, provisional, or agreed trump;
- the set of plausible trump suits;
- forcing/game-forcing status;
- enemy suits;
- every legal call below 4NT classified as a natural call, raise, enemy-suit
  cue, non-natural new-suit selector, own-suit selector, or unresolved call;
- whether 3NT is a playable/available target;
- authored calls and meanings that have priority.

The first implementation supports at most two plausible trump suits. A state
with three or more plausible trumps is outside the deterministic mapping and
TDs with those candidates listed.

Classification is semantic, not textual. An own suit or a non-enemy suit can
be a selector/cue when a natural interpretation is impossible in context.

## 4. Separate rule families in one framework

The framework contains separate rule families rather than one giant rule:

1. **Trump selection:** derives provisional/agreed trump from raises, selectors,
   and 4NT.
2. **Control bidding:** derives genuine control cues after trumps are agreed.
3. **Contract choice:** uses deterministic rules or sampling for 3NT, game,
   slam, and stopping decisions.
4. **Terminal behavior:** derives natural Pass after partner's call when no
   force or unfinished purpose prohibits it.

A selector that establishes trumps must use `trump_selector`, not
`control_showing`. Once the suit is agreed, later suitable new suits can be
genuine control cues.

## 5. Derived 4NT

Only an otherwise undefined legal 4NT is eligible.

### 5.1 Already agreed trump

With agreed trumps, 4NT is ordinary keycard asking for that suit unless an
explicit method overrides it.

### 5.2 Auction still at the three level

When trumps are not agreed and the auction is still at the three level, 4NT is
normally quantitative. The engine may derive “set trumps and ask keycards”
only when public evidence proves all of:

- the auction is forcing enough that Pass/3NT is not the intended resolution;
- exactly one plausible trump suit remains;
- no lower raise or selector can establish it.

Otherwise 4NT remains quantitative or TDs if quantitative meaning conflicts
with explicit evidence.

### 5.3 Auction at the four level

Let `T` be the ordered plausible-trump set, `R` the available natural raises,
and `C` the available selector/cue calls below 4NT.

- The mapping applies only when `1 <= |T| <= 2`; with more candidates it TDs.
- A raise is pinned to its own suit before selectors are assigned.
- Remaining selectors and candidates are paired in ascending bridge order.
  If their counts differ and none of the explicit cases below resolves the
  sole remaining candidate through 4NT, the result TDs.
- If `|R union C| >= |T|`, all candidates are covered below 4NT; 4NT is a
  nonforcing suggestion to play 4NT, not a keycard ask. Some auctions have no
  hand that can reasonably make this suggestion; those cases do not
  manufacture the call.
- With one raise, at least one selector, and two candidate trumps: the raise
  sets its own suit; the selector sets the other suit; 4NT is not keycard.
- With one raise, no selector, and two candidates: the raise sets its suit;
  4NT sets the other suit and asks its keycards.
- With one selector, no raise, and two candidates: the selector sets the lower
  candidate; 4NT sets the higher candidate and asks its keycards.
- With two selectors and two candidates: the lower selector sets the lower
  candidate and the higher selector sets the higher candidate. Neither
  selector promises control.
- With exactly one plausible trump and no lower raise or selector capable of
  setting it, 4NT sets that sole suit and asks its keycards. If any lower call
  can set it, that call is used and 4NT is not inferred as keycard merely for
  convenience.

When counts, legality, or natural meanings do not fit one case uniquely, the
engine TDs.

## 6. NFRKCB versus natural continuation

An inferred 4NT suggestion can create NFRKCB only in a single-suit context:

- partner has shown one long suit;
- that suit is provisional trump;
- partner has not shown a second natural long suit.

Pass accepts the suggestion to play 4NT. An ordinary 1430 response rejects the
signoff and starts NFRKCB for the provisional suit.

The responder does not receive both choices without a decision rule. It
samples partner hands consistent with the single-suit provisional auction and
compares playing 4NT with the NFRKCB slam routes. Pass is selected when 4NT is
the best supported destination; a 1430 answer is selected only when continuing
toward slam is preferred and the actual hand supplies that answer. If sampling
is unavailable, a deterministic keycard/strength safety rule may continue
only when unambiguous; otherwise TD. A 1430 answer changes the public method
from `nfrkcb_offer` to `nfrkcb_answered`; Pass completes it.

If partner has shown two natural suits, later suit bids retain natural
meanings. They are not interpreted as NFRKCB answers merely because their
levels resemble 1430.

Canonical distinction:

- `1NT-2C-2D-3C-3NT-4C-4NT`: single-suit provisional clubs; Pass accepts and
  a 1430 answer rejects through NFRKCB.
- `1NT-2H-2S-3C-3NT-4C-4NT`: two natural suits; responder's 5C is natural.

## 7. Three-level fits

### 7.1 Major fit

After a major fit is established at the three level, classification order is:

1. retain explicit natural or conventional profile meanings;
2. identify the profile's serious/non-serious relay (`3NT`, or `3S` with
   hearts agreed when 3NT is reserved as a spade control);
3. treat an otherwise non-natural new suit as a control cue, without bypassing
   the unique critical control;
4. expose game, further cue, and keycard routes;
5. use simulation only to choose among those already-defined routes.

The framework derives:

- available control cues in both directions;
- serious/non-serious 3NT or the profile's space-preserving substitute;
- game placement, continued cueing, and keycard entry;
- sampled resolution when total strength, control, or strain choice cannot be
  decided deterministically.

The rule applies symmetrically to hearts and spades. It must not encode only
one suit's literal prefixes.

### 7.2 Minor fit

After a minor fit is established at the three level, classification order is:

1. retain explicit and natural meanings;
2. while 3NT is live, classify a below-3NT call in the sole unshown enemy or
   unstopped suit as a stopper inquiry;
3. when slam interest is already public or 3NT is no longer live, classify a
   non-natural new suit as a control cue;
4. otherwise expose the ambiguity and TD unless public/profile evidence
   selects one meaning.

A new-suit call can therefore be:

- a stopper inquiry for 3NT;
- a control cue for a minor slam;
- a natural call when public shape permits it.

The framework first preserves 3NT space. Simulation never decides what a call
means; it compares the already-classified 3NT and minor-suit contract routes.
When a route would cross 3NT, this comparison is mandatory. Without a decisive
deterministic rule or available simulation, it TDs rather than treating every
new suit as a cue.

## 8. Derived jump to 6NT

An otherwise undefined jump to 6NT from below 4NT is a natural small-slam
placement when:

- no fit is known;
- the bidder's strength plus partner's publicly guaranteed minimum is 33 to
  35 HCP;
- a good five-card suit may lower the required total by one point.

The exact good-five-card predicate uses the shared hand-quality subsystem and
must not be redefined inside the inference engine.

## 9. Derived Pass

After partner's call, Pass defaults to “willing to play the current contract”
when all of the following hold:

- Pass is legal;
- no forcing or game-forcing obligation requires action;
- no committed private purpose requires a response;
- the current call is not an unresolved inquiry;
- Pass does not incorrectly abandon a still-pending trump-selection or
  NFRKCB response.

This derived Pass is natural, nonforcing, and a final-placement willingness.
It does not erase an explicitly authored forcing Pass.

## 10. Decision and failure order

Where a rule needs judgment, the order is:

1. exact public/deterministic inference;
2. sampled deals and DDS/contract evaluation;
3. deterministic safety fallback explicitly allowed by the rule;
4. TD.

No broad “reasonable bridge call” fallback may manufacture a meaning.

## 11. Planned verification

The implementation plan must include table-driven tests for:

- explicit meanings overriding every derived family;
- all four-level raise/selector count cases;
- three-level 4NT staying quantitative unless the exceptional proof succeeds;
- agreed-trump 4NT becoming keycard;
- single-suit NFRKCB versus two-suit natural continuations;
- symmetric three-level heart/spade fits;
- minor stopper inquiries and crossing-3NT simulation;
- 33–35 HCP jump 6NT, including the good-five-card reduction;
- derived partner-call Pass and every obligation that suppresses it;
- ambiguous evidence producing TD with a structured explanation.

