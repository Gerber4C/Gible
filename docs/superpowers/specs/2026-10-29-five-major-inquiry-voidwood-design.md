# Five-Major Inquiry Continuations and Voidwood Design

## Goal

Complete the Daqiush 2/1 continuations for game-forcing responder hands with
3-1 majors and 5-4 minors after `1NT-3C`, and replace the profile's
prefix-specific exclusion-keycard slice with a reusable Voidwood convention
driven by confirmed-trump state.

The implementation must prefer sampled DDS decisions where the system calls
for simulation, use a deterministic bridge-logic fallback when DDS is
unavailable, and report TD only when neither method can select a supported
call. It must generate symmetric heart/spade and club/diamond branches from
shared rules rather than treating one literal auction as the whole system.

## Scope

This change includes:

- the existing `1NT-3C` entry for 3-1 majors and 5-4 minors;
- continuations after opener's `3D`, `3H`, or `3S` response;
- confirmed-trump effects and final-placement meanings on those continuations;
- a dedicated simulation decision for the newly authored choice points;
- deterministic fallback classification for the same choice points;
- renaming the Daqiush `exclusion_keycard` gadget and public meanings to
  `voidwood`;
- making Voidwood available from any compatible Daqiush confirmed-trump state;
- a worst-case answer safety check before offering a Voidwood ask.

It excludes competitive Voidwood, the opponents-joint-strength variant that
turns Voidwood into a shortage slam invitation, and unrelated 1NT responder
routes. Those remain separate future work.

## Existing entry and public meanings

The `3C` inquiry already accepts both ordinary game-forcing hands and the
3-1-major, 5-4-minor class. This design does not create another entry call.

After `1NT-3C`:

- `3D` denies a five-card major;
- `3H` shows five or more hearts;
- `3S` shows five or more spades and denies five hearts.

After `3D`, a 3-1-major, 5-4-minor responder bids `3H` or `3S` to show the
singleton in the named major. This is descriptive, not a trump agreement.

## Decision order

At every newly simulated choice point, selection follows this order:

1. use the sampled-deal/DDS expected-value decision when available;
2. otherwise use the deterministic fallback defined for that position;
3. if DDS selects a call that is not authored, record the mismatch and run the
   deterministic fallback rather than emitting that call;
4. if the deterministic fallback cannot distinguish the authored candidates
   without inventing system meaning, return TD.

The deterministic result is not allowed to overwrite an available sampled
decision whose selected call is authored and legal. An unavailable,
unauthored, or illegal sampled result falls through to the deterministic
rules. A trace explanation records whether the result came from DDS,
deterministic fallback, or TD.

### Slam-interest classification

At every branch that asks whether responder still has slam interest, the
sampled comparison is authoritative. It compares stopping in the current game
with the reachable six-level contracts in the publicly known fits.

When sampled evaluation is unavailable, the route reuses the profile's
existing minor-slam threshold:

```text
slam_interest = responder K-R points >= MINOR_SLAM_KR (currently 14.0)
```

This is a deterministic fallback classification, not a new claim that K-R
alone decides the real slam. Keeping the threshold as the existing named
profile constant prevents this route from drifting away from other Daqiush
minor-slam decisions.

## No-five-card-major branch

The auction prefix is:

```text
1NT-Pass-3C-Pass-3D-Pass-3M-Pass
```

where responder's `3M` shows a singleton major.

### Opener prefers 3NT

The primary simulation compares 3NT with the authored suit-contract
alternatives using the same public-information sampling boundary used by the
other Daqiush simulation decisions. If 3NT has the highest expected result,
opener bids `3NT`, natural and final.

When DDS is unavailable, the existing stopper test in the shown singleton
major is necessary but not by itself sufficient. The fallback constructs the
structural candidates below. It chooses `3NT` only when opener has the stopper
and no suit candidate is structurally eligible. If both 3NT and one or more
suit candidates remain eligible, the deterministic fallback abstains and the
position becomes TD; it does not pretend a stopper alone settles expected
value.

### Opener rejects 3NT

When simulation does not prefer 3NT, opener selects among these structures.
When DDS is unavailable, each numbered item below is an exact eligibility
predicate. The fallback selects a call only when exactly one item is eligible;
overlapping eligible structures require simulation and otherwise become TD.
The special double-minor item suppresses the generic four-card-minor item when
its complete predicate is true:

1. **Both minors at least four cards.** Opener must hold at least four cards in
   each minor; `minor_game_control_points(opener, 'D',
   partner_long_suits=('C',))` must be at least `14.5`; and the shown singleton
   major may contain no `K`, `Q`, or `J` unless the holding also contains the
   ace and its only side honor is the king (`AK`, with or without small cards).
   Opener then bids `4M` in the shown singleton major. This establishes
   diamonds as trumps. The call does not promise control in the bid major.
2. **A four-card minor.** Opener bids that minor at the four level and
   immediately establishes it as trumps. This fallback item is eligible only
   when exactly one minor is at least four cards. With two four-card minors
   that fail item 1, simulation is required; without it, the result is TD.
3. **A possible 4-3 fit in the other major.** Opener must hold exactly four
   cards in `oM` and fewer than four cards in both minors. Opener bids `4oM`,
   natural placement in the known 4-3 fit.
4. **Three-three minors.** Opener bids `4NT`, an artificial request for a
   simulated final placement. This item is eligible when opener has exactly
   three cards in each minor and item 3 is not eligible. It is not Roman
   keycard and not quantitative.

After `4oM`, responder applies the common slam-interest classification. With
no remaining slam interest it Passes, making `4oM` final. With slam interest it
names the lowest legal five-card minor. The named minor and `oM` are then the
only candidate strains. The sampled final contracts are the current `5m`
contract (Pass), the cheapest legal `5oM`, `6m`, and `6oM`. Opener selects the
highest expected score. All four outcomes are final placements.

Without DDS, opener compares known combined length in the named minor and
`oM`; a tie is broken by `shapely_control_points(opener, (strain,))` evaluated
separately for the two candidate strains. The fallback chooses the unique
better strain at the cheapest legal five-level contract and never promotes
itself to slam. An exact length-and-point tie becomes TD. This fallback is
deliberately conservative because the responder has shown interest, not
guaranteed a slam.

After the three-three-minor `4NT`, responder/opener continuations are likewise
selected as final placements. Responder's five-card minor is the only
candidate strain; simulation compares `5m` and `6m`. Without DDS, responder
chooses `5m`. Both calls are signoffs and must not reopen an invitation merely
because their strain is new.

## Five-card-major branches

Let `M` be opener's shown five-card major and `oM` the other major.

### Responder has three-card support

- Without slam interest, responder raises directly to `4M`, final.
- With slam interest, responder bids the lowest legal `oM` call as an
  artificial strength-showing action. The heart and spade cases are generated
  from the same relative-major rule; `oM` is not hard-coded as one suit.

Further slam exploration remains simulation-led. Deterministic control and
fit logic may choose an authored continuation; otherwise the auction becomes
TD rather than inventing a cue meaning.

### Responder is singleton in opener's major

- Without slam interest, responder bids `3NT`, final.
- With slam interest, responder bids its five-card minor at the four level.

If responder bids `4C`, it shows five clubs and four diamonds. Opener may:

- bid `4D` to establish diamonds as trumps;
- bid `4H` or `4S` to establish clubs as trumps;
- bid `5C` as a final club contract.

If responder bids `4D`, it shows five diamonds and four clubs. Opener may:

- bid `4H` to establish clubs as trumps;
- bid `4S` to establish diamonds as trumps.

These calls select a trump strain; they do not promise control in the suit
bid. Simulation chooses among them first. Without DDS, the deterministic
fallback computes each candidate's known combined trump length and then
`minor_game_control_points` for that trump, retaining the other publicly shown
minor through `partner_long_suits`. It chooses the unique candidate with the
longest known fit; a length tie is broken by strictly higher control points.
If length and control points both tie, it chooses the lower legal call. This
last tie-break is conventional economy, not a claim that the contracts are
equally good.

## Terminology and relative suits

- `M`: the contextually referenced major;
- `oM`: the other major;
- `m`: the contextually referenced minor;
- `om`: the other minor.

The implementation must use these relationships when generating symmetric
rules. Tests cover both major orientations and both 5-4 minor orientations.

## Confirmed-trump effects

Every call described above as "establishes" or "sets" a suit writes a
confirmed-trump state immediately. Later 4NT/keycard, cue, and Voidwood
interpretation must use this state rather than reconstructing trump from a
literal auction string.

The confirmed example is:

```text
1NT-2H-2S-3D-3H
```

Here `3D` is responder's natural diamond suit and opener's `3H` supports it;
the auction is therefore in a confirmed **diamond-trump** state. A later `5C`
can be club-void Voidwood for diamonds.

## Voidwood convention

Rename the Daqiush gadget, public actions, descriptions, and state method from
`exclusion_keycard` / `exclusion_1430` to `voidwood`. User-facing explanations
use `Voidwood（缺门关键张）`.

Voidwood is eligible only when:

- the partnership has a confirmed trump suit;
- no keycard inquiry is already pending;
- the asker is void in the suit bid;
- the bid suit differs from trumps;
- the call is the one-level jump in the void suit (one full level above the
  cheapest legal call in that strain), and that jump is `4S` or higher;
- all five answer steps exist before the end of the legal call order;
- the worst-case answer safety check passes.

Calls are generated from confirmed-trump state and current legal auction
level, not from a closed list of complete prefixes or an undefined profile
table. Strains follow ordinary bridge order `C, D, H, S, NT`; the five answers
are the next five legal contract bids after the ask. A suit call below `4S`, a
non-jump, a trump-suit call, or an ask without five remaining answer steps is
not Voidwood. Existing uncontested 1NT transfer examples remain regression
cases, not the boundary of the feature.

## Voidwood answers

The bid suit is excluded when counting keycards. There are therefore four
effective keycards: the three non-void aces and the trump king. The five
answers, in order, are:

1. 0 or 3 keycards;
2. 1 or 4 keycards without the trump queen;
3. 1 or 4 keycards with the trump queen;
4. 2 keycards without the trump queen;
5. 2 keycards with the trump queen.

Existing continuations remain:

- after 0/3, the next step asks for the trump queen;
- after 0/3, two steps ask for kings when the ask remains below 5NT;
- after a 1/4 response below 5NT, the next step asks for kings;
- in a king response, the ace of the void suit is treated as that suit's king;
- after an initial answer at 5NT or above, every continuation is a grand-slam
  invitation and skipping a suit means its king is not required.

## Worst-case answer safety

Voidwood eligibility is not controlled by a fixed HCP or K-R threshold.
Before exposing the ask, the engine evaluates every answer category that is
consistent with the asker's private keycards.

For each category it determines:

- the physical answer bid;
- the lowest legal trump contract still reachable;
- the possible combined keycard totals after eliminating impossible 0/3 or
  1/4 interpretations using the asker's saved private count;
- whether playing at the six level is forced;
- whether every forced-six interpretation guarantees at least three of the
  four effective keycards, so the partnership is not missing two.

The ask is rejected if any possible answer forces the partnership above the
five-level trump contract without guaranteeing sufficient keycards for the
small slam. Trump-queen information is then used for grand-slam decisions,
not to excuse two missing keycards at the small-slam level.

For the confirmed example with diamonds trump and a club void:

```text
...-3H-Pass-5C
```

the first response is `5D`. A resolved zero-keycard response may stop there.
Every nonzero response is higher than `5D`, so the asker must be prepared to
play at least `6D` whenever partner has a nonzero number. If its own keycards
cannot guarantee that result is safe, `5C` is not an eligible call.

## Compatibility and migration

The Daqiush profile registers `voidwood`, not `exclusion_keycard`. Source files,
test names, explanations, and documentation use the new name. Replay of old
saved reports may recognize the old action/method strings as read-only aliases,
but new decisions and serialized explanations emit only `voidwood` names.

The unrelated Meow benchmark gadget is outside this rename unless it imports
shared engine helpers. Its public system identity is not silently changed.

## Error handling

- A simulated call absent from the authored candidates records a diagnostic
  and falls through to deterministic selection; it is never emitted directly.
- An unavailable DDS solver is a normal fallback condition, not an exception
  shown to the user.
- Invalid or contradictory trump/void state rejects the Voidwood candidate and
  records a diagnostic.
- If no simulation or deterministic rule can select a supported call, normal
  missing-call behavior reports TD with the exact auction and decision point.

## Verification

Tests are written before production changes and cover:

- the existing 3-1-major, 5-4-minor hand still enters through `3C`;
- both singleton-major reports after `3D`;
- DDS selection and DDS-unavailable fallback for 3NT versus every authored
  suit route;
- 4-4 minors with good controls and no major waste establishing diamonds;
- each four-card-minor trump choice, each 4-3 other-major placement, and the
  three-three-minor `4NT` route;
- final-purpose semantics after all simulated placements;
- five-card-heart and five-card-spade replies with responder holding three or
  one card;
- both five-club/four-diamond and five-diamond/four-club continuations;
- confirmed-trump state on every trump-setting call;
- profile loading under the `voidwood` name and absence of new emitted
  `exclusion_keycard` state;
- Voidwood from at least two distinct auction families sharing the same
  confirmed-trump state;
- all five answer steps for every legal level boundary used by the profile;
- the diamond-trump, club-void `5C` example;
- acceptance when a zero response can stop at five of trumps;
- rejection when any nonzero answer forces six while two keycards may be
  missing;
- acceptance when every nonzero forced-six branch guarantees at least three
  of four effective keycards;
- 0/3 and 1/4 disambiguation using the asker's private keycard count;
- Q and K continuations, including the void ace counting as that suit's king;
- heart/spade and club/diamond symmetry;
- regression coverage for ordinary 1430, the Meow benchmark, existing
  confirmed-trump prefixes, and TD reporting.

