# Derived Bidding Semantics

The derivation layer fills predictable meanings only after explicit profile
meanings and committed private purposes. It is enabled per profile with
`derived_semantics=True` so existing profiles keep their current behavior until
they opt in. It never rewrites an authored meaning
and never treats one call as both natural and artificial.

## Evidence

`engine/derived_evidence.py` builds a frozen public-evidence object from replay:
current contract, natural and guaranteed-long suits, supports, enemy suits,
unset/provisional/agreed trump, plausible trumps, forcing status, legal calls
below 4NT, and 3NT availability. It reads no private cards. More than two
plausible trumps produces a structured conflict.

## Families

- **4NT** (`derived_four_notrump.py`): agreed trump is keycard; a three-level
  auction is quantitative unless a forcing sole-trump exception applies;
  four-level raises are pinned first, then selectors pair with remaining
  candidate trumps in ascending order. Covered auctions leave 4NT natural.
- **NFRKCB** (`nfrkcb_policy.py`): a 4NT suggestion becomes `nfrkcb_offer`
  only in a single-suit provisional context. Pass accepts; the responder's
  actual 1430 answer creates `nfrkcb_answered`. Two-suit auctions never offer
  it.
- **Three-level fits** (`derived_fit_calls.py`): major fits expose the
  serious relay (3NT, or 3S with hearts when 3NT is reserved) and genuine
  control cues. Minor fits preserve 3NT space: a new suit is a stopper
  inquiry while 3NT is live, otherwise a control cue.
- **6NT** (`derived_terminals.py`): an otherwise undefined jump to 6NT is
  natural when no fit is known and public strength totals 33-35 HCP, or 32
  with `hand_quality.has_good_five_card_suit`.
- **Pass**: after partner's non-forcing, non-inquiry call, Pass is a natural
  final-placement willingness. A committed purpose, pending trump selection,
  NFRKCB response, or forcing obligation suppresses it.

## Priority, replay, and failure

The selector order is explicit candidate > active Purpose > derived candidate
> fallback > TD. A call whose authored definition owns the public context stays
reserved even if the current hand fails its private applicability, so no second
meaning is invented.

`engine/derived_replay.py` reconstructs the same one public meaning and effect
set during hand-free replay. Effects use the ordinary state machinery, so
derived trump selectors, keycard frames, and NFRKCB states are visible to later
turns. Ambiguity produces structured diagnostics (`FOUR_NOTRUMP_*`,
`MINOR_FIT_AMBIGUOUS_NEW_SUIT`, `AMBIGUOUS_DERIVED_CALL`, `NO_DERIVED_MEANING`)
rather than a guessed call. Trace serialization carries the rule, public
evidence, confidence, and conflicts but no private cards or private purposes.
