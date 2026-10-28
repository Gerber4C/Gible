"""Keycard-ask eligibility rules that depend only on the asker's hand."""

from __future__ import annotations

from .cards import Hand


def keycard_ask_restricted(hand: Hand, trump: str, *,
                           grand_candidate: bool = False) -> bool:
    """Return whether this hand must not start the 4NT keycard ask.

    Hearts: one keycard without the trump queen must cue-bid instead.
    Diamonds: one keycard must cue-bid instead.
    Clubs: three keycards without a grand-slam intent must not ask 4NT.
    """
    if not isinstance(hand, Hand):
        raise TypeError('hand must be a Hand')
    if trump not in 'CDHS':
        return False
    keycards = hand.keycard_count(trump)
    queen = hand.contains_rank(trump, 'Q')
    if trump == 'H':
        return keycards == 1 and not queen
    if trump == 'D':
        return keycards == 1
    if trump == 'C':
        return keycards == 3 and not grand_candidate
    return False
