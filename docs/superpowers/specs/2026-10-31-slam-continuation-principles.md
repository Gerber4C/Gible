# General Slam-Continuation Principles

**Date:** 2026-10-31  
**Status:** Working agreement for authored and derived slam routes

## Purpose

These rules describe how a slam auction continues after a fit or reference
trump exists. They are intended to replace per-auction enumeration of every
four-level and five-level continuation. An explicit profile agreement always
overrides these principles.

## 1. Reference trump

- The only eligible reference trump is the latest trump state for the side.
  Historical `agreed_suit` records never select an alternative trump.
- A provisional support cue may be converted to agreed trump by the next
  serious relay, cue, or keycard ask. A natural suggestion may flip the
  reference trump provisionally; Pass accepts it, while a keycard ask converts
  back to the asked trump.
- Once a trump is agreed, later calls must not silently flip it. Any exception
  is an explicit natural-suggestion or keycard rule.

## 2. Serious relay

A serious relay is available when:

- the partnership has found a major fit below 3NT and the auction is
  game-forcing, or
- the known fit is nine cards or longer, so 3NT is not a playable alternative.

With hearts agreed, 3S is the serious relay and 3NT shows spade control. With
spades agreed, 3NT is the serious relay.

The serious relay is stronger than a limited cue and has no upper bound. A cue
bid that declines the serious relay is a limited slam try: partner should
continue only with a maximum; after that cue, four of the major is the forcing
signoff.

## 3. Partner's forced response

After a serious relay, partner must show a control below game unless no control
exists:

- with hearts agreed, 3NT is the spade control; 4C and 4D are the other cues;
- with spades agreed, 4C, 4D, and 4H are the cues.

With no control, partner returns to four of the major. The first cue is forced
and promises no extra strength.

## 4. Serious initiator's continuation

After partner's forced cue, the serious initiator continues the control ladder
unless:

- a skipped side suit is uncontrolled in the initiator's hand (confirmed
  missing control), or
- no further cue is available;

in those cases the auction returns to game. If controls and strength are
complete, 4NT is the keycard ask instead. A later cue is no longer forcing.

## 5. Minor serious and the low-limit 4m reply

After `1NT–2S/2NT–3C/3D–3NT`, the serious relay is 3NT for the agreed minor.

- A low-limit opener replies **four of the agreed minor**. This 4m is forcing
  and is never the final contract.
- The serious bidder then chooses:
  - 4NT keycard for the minor, or
  - 5m as the game signoff.
- "Final 5m/6m/7m" means the allowed final levels, not a direct jump. After the
  4NT answer:
  - if the trump queen is needed, ask the queen;
  - otherwise, if kings are needed, bid 5NT as the single king ask;
  - after the 5NT answer, if more information is still needed, make the grand
    invitation;
  - otherwise place 5m, 6m, or 7m directly.
- Do not run a specific-king ladder: never ask which king, then which next
  king, one at a time. 5NT is the one king ask.
- A direct 6m/7m is allowed only when already justified, not as a substitute
  for keycard.
- A high-limit opener instead cues a side control. The ordinary serious control
  ladder then applies.
- No Pass below five of the minor is permitted after the low-limit 4m.

## 6. Keycard and grand-slam continuation

- 4NT is keycard only after the partnership has established the trump and
  either completed the serious cue exchange or chosen the low-limit 4m route.
- After the 4NT answer:
  - if the trump queen is needed, ask the queen;
  - otherwise, if kings are needed, bid 5NT as the single king ask;
  - after the 5NT answer, if more information is still needed, make the grand
    invitation;
  - otherwise place 5m/6m/7m directly.
- The 5NT answer shows a specific king: the **lowest king held**. It never
  chooses a higher king while a lower one exists. If that lowest king lies
  above six of the trump, the answer is allowed when the sampled expectation
  of 6NT or 7X is greater than the expectation of 6X; otherwise the responder
  cannot bypass 6X with that king. This comparison uses public-deal sampling
  and DDS, with a conservative deterministic fallback.
- Do not run a specific-king ladder: never ask which king, then which next
  king, one at a time. 5NT is the one king ask.
- Six of the agreed trump is a final small slam; seven is final. Partner Passes
  after a completed final placement.

## 7. Derived cue pool

When a reference trump exists and the auction is below game or slam, any legal
side-suit call that the profile has not explicitly authored is derived as a
control cue and added to the candidate pool automatically. Authored candidates
keep priority for the same call; derived cues remain available for hands and
routes where no authoring exists.

## 8. Failure behavior

If public evidence does not identify one trump, one control meaning, or one
legal final route, the engine must TD with a structured explanation. It must
not invent an agreement, and it must not read private cards from the other
hand.

## 9. Two-suit keycard grand invitation

After the two-suit keycard answer has shown a queen, the next step follows the
missing side king rather than a new specific-king ladder:

- `5S` answer: `5NT` is the generic grand invitation.
- `5NT` or `6C` answer: a six-level side-suit bid is the invitation, in the
  lowest side suit whose king the asker lacks.
- A lower side king already held by the asker is deliberately skipped. A lower
  side king the asker lacks is unintentionally skipped and must be ignored by
  responder.
- After a `5NT` invitation, `6C` = no side king, `6H` = heart king, `6S` =
  spade king without the heart king.
- After a `6H` invitation, `7C` = heart king and is pass-or-correct; `6S` =
  spade king without the heart king; a missing side king signs off in `6NT`.
- After a `6S` invitation, the spade king accepts (`7C`), while a skipped heart
  king or no king signs off in `6NT`.
- `7C` accepts the lower trump; Pass accepts it, while `7D` is the correction
  to the higher trump. The immediate response to a six-level invitation cannot
  use `7D`; the correction is legal only after `7C`.
- With both side kings and a compatible keycard count, responder may place
  `7C`/`7D` directly instead of stopping to answer a king.

Implementation: `backend/engine/derived_grand_invite.py` owns the suit/rank
rules, and `backend/engine/derived_two_suit_keycard.py` owns the public state
machine and replayable effects.

## 10. Artificial answers and the five-of-trump stop

Keycard answers, queen answers, king answers, and relays are non-contractual:
they never define the contract strain and never change the agreed trump. A
Pass after such an answer is therefore not an automatic acceptance of the
literal bid.

The stop target is always **five of the agreed trump**, derived separately from
the answer:

- if the artificial answer is already five of the trump, the stop is Pass;
- otherwise the stop is the five-level trump call (for example, a Voidwood
  `5D` answer with hearts agreed must stop in `5H`, never Pass `5D`);
- stop when two or more keycards are missing, or when one keycard is missing
  and the trump queen is denied;
- with no missing keycard, or one missing and the queen known, continue to six
  of the trump; with one missing and the queen unknown, ask the queen;
- when the stop target is unavailable, the engine continues or uses a defined
  relay/rescue rather than passing the artificial answer.

Implementation: `engine/keycard_stop.py` classifies non-contractual answers and
owns the stop geometry; `engine/derived_keycard_stop.py` fills the stop or
small-slam candidate from the public frame and the asker's keycards. The same
rule is mirrored in the saved-purpose continuation.

## Implementation mapping

- Minor serious 3NT and low-limit 4m:
  `daqiush_2over1/gadgets/one_notrump_invitations/gadget.bsl.py`
- Major serious relays after the second-minor route:
  `daqiush_2over1/gadgets/jacoby_major_transfers/gadget.bsl.py`
- Derived serious relay and forced responses: `engine/derived_fit_calls.py`
- Global Voidwood and inferred trumps: `engine/voidwood.py`
- Non-contractual answers and five-of-trump stop: `engine/keycard_stop.py`,
  `engine/derived_keycard_stop.py`
- Future generic derivation: the `derived_*` engine layer should fill any
  otherwise undefined call from these rules, with authored profile calls
  retaining priority.
