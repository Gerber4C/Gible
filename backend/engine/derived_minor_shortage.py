"""Derived choices after a shortage bid in the two-minor game-force route."""

from __future__ import annotations

from .derived_semantics import DerivationResult, derived_candidate
from .hand_quality import minor_game_control_points
from .legality import is_call_legal
from .rkcb_continuation import bid_rank


def derive(profile, auction, trace, evidence, allowed, hand=None):
    if hand is None:
        return DerivationResult(evidence)
    shortage = _last_shortage(trace)
    if shortage is None or shortage.get('shortage_suit') != 'H':
        return DerivationResult(evidence)
    if not _has_two_minor_force(trace):
        return DerivationResult(evidence)

    preferred = _preferred_minor(hand)
    if preferred == 'C':
        call = '4S'
        if call in allowed and is_call_legal(auction, call):
            meaning = {
                'nature_labels': ['artificial'],
                'call_act_types': ['support', 'slam_try'],
                'action_type': 'derived_shortage_club_support',
                'target_suit': 'C',
                'agreed_suit': 'C',
            }
            return DerivationResult(evidence, (derived_candidate(
                call, 'derive_shortage_club_support', meaning, evidence,
                effects=({'key': 'agreed_suit', 'suit': 'C'},), score=2),))
    call = '4N'
    if call in allowed and is_call_legal(auction, call):
        meaning = {
            'nature_labels': ['artificial'],
            'call_act_types': ['inquiry', 'keycard_asking'],
            'action_type': 'rkcb_1430',
            'target_suit': 'D',
            'agreed_suit': 'D',
        }
        effects = (
            {'key': 'agreed_suit', 'suit': 'D'},
            {'key': 'keycard_context', 'method': 'rkcb_1430',
             'trump_suit': 'D', 'ask_call': '4N', 'status': 'pending'},
        )
        return DerivationResult(evidence, (derived_candidate(
            '4N', 'derive_shortage_diamond_keycard', meaning, evidence,
            effects=effects, score=2),))
    return DerivationResult(evidence)


def _last_shortage(trace):
    if trace is None:
        return None
    for entry in reversed(trace.applied_meanings):
        if entry.get('call') in ('P', 'X', 'R'):
            continue
        meaning = entry.get('public_meaning', {}) or {}
        if meaning.get('action_type') == 'minor_shortage_slam_try':
            return {
                'shortage_suit': meaning.get('shortage_suit'),
                'call': entry.get('call'),
            }
        return None
    return None


def _has_two_minor_force(trace):
    return any(
        (entry.get('public_meaning', {}) or {}).get('action_type')
        == 'two_minor_game_force'
        for entry in trace.applied_meanings)


def _preferred_minor(hand):
    def quality(suit):
        return (
            hand.length(suit),
            minor_game_control_points(hand, suit,
                                      partner_long_suits=('C', 'D')),
            hand.honor_count(suit, ('A', 'K', 'Q')),
        )

    return 'D' if quality('D') >= quality('C') else 'C'
