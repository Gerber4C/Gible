"""Deterministic fallbacks for the Daqiush five-major inquiry."""

from __future__ import annotations

from dataclasses import dataclass

from .cards import Hand, normalize_suit_name
from .hand_quality import minor_game_control_points, minor_slam_interest


@dataclass(frozen=True)
class InquiryDecision:
    call: str | None
    source: str
    reason: str
    agreed_suit: str | None = None
    final: bool = False


def deterministic_after_singleton(
        opener: Hand, *, singleton_major: str) -> InquiryDecision:
    """Choose an exact no-DDS fallback after responder shows a singleton major."""
    reported = _major_code(singleton_major)
    other_major = 'S' if reported == 'H' else 'H'
    minor_lengths = {suit: opener.length(suit) for suit in 'CD'}

    if (_both_minor_special(opener, reported, minor_lengths)):
        return InquiryDecision(
            call='4' + reported,
            source='deterministic',
            reason='Both minors, sufficient controls, and no waste in the reported major',
            agreed_suit='D',
        )

    candidates: list[tuple[str, str | None, str]] = []
    long_minors = [suit for suit in 'CD' if minor_lengths[suit] >= 4]
    ambiguous_minors = len(long_minors) == 2
    if len(long_minors) == 1:
        minor = long_minors[0]
        candidates.append(('4' + minor, minor, 'Unique four-card-or-longer minor'))

    other_major_candidate = (opener.length(other_major) == 4
                             and all(length < 4 for length in minor_lengths.values()))
    if other_major_candidate:
        candidates.append(('4' + other_major, other_major,
                           'Unique possible four-three fit in the other major'))
    elif minor_lengths == {'C': 3, 'D': 3}:
        candidates.append(('4NT', None, 'Exact three-three minors'))

    has_stopper = opener.honor_count(reported, ('A', 'K', 'Q')) >= 1
    if has_stopper and not candidates and not ambiguous_minors:
        return InquiryDecision(
            call='3NT', source='deterministic',
            reason='Reported singleton major is stopped and no suit route is eligible',
            final=True,
        )
    if not has_stopper and len(candidates) == 1:
        call, agreed_suit, reason = candidates[0]
        return InquiryDecision(call=call, source='deterministic', reason=reason,
                               agreed_suit=agreed_suit)

    reason = ('Both four-card minors require simulation' if ambiguous_minors
              else 'Notrump and a suit route overlap' if has_stopper and candidates
              else 'Structural routes do not identify one unique call')
    return InquiryDecision(call=None, source='inconclusive', reason=reason)


def _major_code(suit: str) -> str:
    normalized = normalize_suit_name(suit)
    if normalized not in ('hearts', 'spades'):
        raise ValueError('Singleton report must name a major')
    return normalized[0].upper()


def _both_minor_special(opener: Hand, reported: str,
                        minor_lengths: dict[str, int]) -> bool:
    if not all(length >= 4 for length in minor_lengths.values()):
        return False
    if minor_game_control_points(
            opener, 'D', partner_long_suits=('C',)) < 14.5:
        return False
    holding = opener.holding(reported)
    side_honors = {rank for rank in 'KQJ' if rank in holding}
    return not side_honors or (side_honors == {'K'} and 'A' in holding)
