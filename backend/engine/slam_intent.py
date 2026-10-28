"""Heuristic slam-intent detection from the acting hand and public strength.

The detector is deliberately information-safe: it uses only the acting hand
and a public minimum for partner. It does not see partner's actual cards.
Thresholds are project defaults, not bridge-population probabilities.
"""

from __future__ import annotations

from dataclasses import dataclass

from .cards import Hand
from .hand_quality import assess_quality


PARTNER_1NT_MIN = 15
PARTNER_DEFAULT_MIN = 12


@dataclass(frozen=True)
class SlamIntent:
    strain: str
    level: int | None
    grand: bool
    combined_min: int
    reason: str


def _suit_hcp(hand: Hand, suit: str) -> int:
    points = {'A': 4, 'K': 3, 'Q': 2, 'J': 1}
    return sum(points.get(rank, 0) for rank in hand.holding(suit))


def _good_concentrated(hand: Hand, suit: str | None = None) -> bool:
    if suit is None:
        suit = max('SHDC', key=lambda item: (hand.length(item), _suit_hcp(hand, item)))
    length = hand.length(suit)
    if length < 5:
        return False
    top_honors = sum(1 for rank in 'AKQ' if rank in hand.holding(suit))
    return (_suit_hcp(hand, suit) >= 9 and top_honors >= 2
            and assess_quality(hand)['good'])


def detect_slam_intent(
    hand: Hand,
    partner_min_hcp: int = PARTNER_1NT_MIN,
    *,
    strain: str | None = None,
) -> SlamIntent:
    """Return the likely slam target from own hand and partner's public minimum."""
    if not isinstance(hand, Hand):
        raise TypeError('hand must be a Hand')
    if isinstance(partner_min_hcp, bool) or not isinstance(partner_min_hcp, int) \
            or not 0 <= partner_min_hcp <= 37:
        raise ValueError('partner_min_hcp must be an integer from 0 to 37')
    combined = hand.hcp + partner_min_hcp

    if strain in ('C', 'D', 'H', 'S'):
        length = hand.length(strain)
        good = _good_concentrated(hand, strain)
        if ((length >= 7 and combined >= 33)
                or (length >= 6 and combined >= 35)) and good:
            return SlamIntent(strain, 7, True, combined,
                              'running suit and grand-slam strength')
        if (length >= 7 and combined >= 28) or (length >= 6 and combined >= 30):
            return SlamIntent(strain, 6, False, combined,
                              'running suit and small-slam strength')
        return SlamIntent(strain, None, False, combined,
                          'below suit-slam threshold')

    good = _good_concentrated(hand)
    if combined >= 37 or (combined >= 36 and good):
        return SlamIntent('N', 7, True, combined,
                          'grand-notrump strength')
    if combined >= 33 or (combined >= 32 and good):
        return SlamIntent('N', 6, False, combined,
                          'small-notrump strength')
    return SlamIntent('N', None, False, combined,
                      'below notrump-slam threshold')
