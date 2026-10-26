"""Contextual HCP adjustment after partner shows a splinter short suit."""

from __future__ import annotations

from .cards import Hand, RANK_POINTS


def splinter_suit_points(holding: str) -> float:
    """Retained value of honors opposite a singleton or void, per Daqiush rules."""
    honors = set(holding.upper())
    if 'A' in honors:
        if 'K' in honors:
            return 7 if 'Q' in honors else 6
        return 5 if 'Q' in honors else 4
    if 'K' in honors:
        return 1.5 if 'Q' in honors else 1
    return 0


def splinter_adjusted_hcp(hand: Hand, short_suit: str) -> float:
    holding = hand.holding(short_suit)
    ordinary = sum(RANK_POINTS.get(rank, 0) for rank in holding)
    return hand.hcp - ordinary + splinter_suit_points(holding)
