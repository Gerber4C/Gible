"""Derived two-suit keycard for the shortage route in the minor game force."""

from __future__ import annotations

from .derived_semantics import DerivationResult, derived_candidate
from .legality import is_call_legal


def derive(profile, auction, trace, evidence, allowed, hand=None):
    if trace is not None and trace.state_exists(
            {'key': 'two_suit_keycard', 'status': 'answered'}):
        return _placements(auction, trace, evidence, allowed)
    if trace is not None and trace.state_exists(
            {'key': 'two_suit_keycard', 'status': 'pending'}):
        if hand is None:
            return DerivationResult(evidence)
        answer = _answer(hand)
        if answer not in allowed or not is_call_legal(auction, answer):
            return DerivationResult(evidence)
        meaning = {
            'nature_labels': ['artificial'],
            'call_act_types': ['descriptive', 'keycard_answer'],
            'action_type': 'two_suit_keycard_answer',
            'target_suit': 'C',
            'keycard_counts': list(_possible_counts(answer)),
            'queen_category': _queen_category(answer),
        }
        effects = (
            {'key': 'two_suit_keycard', 'status': 'answered',
             'method': 'two_suit_keycard', 'answer_call': answer,
             'category': _category(answer)},
        )
        return DerivationResult(evidence, (derived_candidate(
            answer, 'derive_two_suit_keycard_answer', meaning, evidence,
            effects=effects, score=2),))

    shortage = _last_shortage(trace)
    if shortage != 'S' or not _has_two_minor_force(trace):
        return DerivationResult(evidence)
    if '4N' not in allowed or not is_call_legal(auction, '4N'):
        return DerivationResult(evidence)
    meaning = {
        'nature_labels': ['artificial'],
        'call_act_types': ['inquiry', 'keycard_asking'],
        'action_type': 'two_suit_keycard',
        'target_suit': 'C',
        'suits': ['C', 'D'],
        'keycards_total': 6,
    }
    effects = (
        {'key': 'two_suit_keycard', 'status': 'pending',
         'method': 'two_suit_keycard', 'low_suit': 'C', 'high_suit': 'D',
         'keycards_total': 6},
    )
    return DerivationResult(evidence, (derived_candidate(
        '4N', 'derive_two_suit_keycard', meaning, evidence,
        effects=effects, score=3),))


def _placements(auction, trace, evidence, allowed):
    last = None
    for entry in reversed(trace.applied_meanings):
        if entry.get('call') not in ('P', 'X', 'R'):
            last = entry
            break
    if last is None or (last.get('public_meaning', {}) or {}).get(
            'action_type') != 'two_suit_keycard_answer':
        return DerivationResult(evidence)
    answer_call = last.get('call')
    result = []
    for call, suit in (('6C', 'C'), ('6D', 'D'), ('6N', 'N'),
                       ('7C', 'C'), ('7D', 'D')):
        if call == answer_call:
            continue
        if call not in allowed or not is_call_legal(auction, call):
            continue
        meaning = {
            'nature_labels': ['natural'],
            'call_act_types': ['signoff', 'final_placement'],
            'action_type': 'two_suit_keycard_placement',
            'target_suit': suit,
            'agreed_suit': suit if suit in 'CD' else None,
            'purpose_completed': True,
        }
        result.append(derived_candidate(
            call, 'derive_two_suit_keycard_placement', meaning, evidence,
            score=2))
    return DerivationResult(evidence, tuple(result))


def _last_shortage(trace):
    if trace is None:
        return None
    for entry in reversed(trace.applied_meanings):
        if entry.get('call') in ('P', 'X', 'R'):
            continue
        meaning = entry.get('public_meaning', {}) or {}
        if meaning.get('action_type') == 'minor_shortage_slam_try':
            return meaning.get('shortage_suit')
        return None
    return None


def _has_two_minor_force(trace):
    return any(
        (entry.get('public_meaning', {}) or {}).get('action_type')
        == 'two_minor_game_force'
        for entry in trace.applied_meanings)


def _answer(hand):
    keycards = (hand.ace_count()
                + int(hand.contains_rank('C', 'K'))
                + int(hand.contains_rank('D', 'K')))
    low_q = hand.contains_rank('C', 'Q')
    high_q = hand.contains_rank('D', 'Q')
    if keycards in (1, 4):
        return '5C'
    if keycards in (0, 3, 6):
        return '5D'
    if keycards in (2, 5):
        if low_q and high_q:
            return '6C'
        if low_q:
            return '5S'
        if high_q:
            return '5N'
        return '5H'
    return None


def _category(answer):
    return {
        '5C': '14', '5D': '036', '5H': '25_none',
        '5S': '25_low', '5N': '25_high', '6C': '25_both',
    }[answer]


def _possible_counts(answer):
    return {
        '5C': (1, 4), '5D': (0, 3, 6), '5H': (2, 5), '5S': (2, 5),
        '5N': (2, 5), '6C': (2, 5),
    }[answer]


def _queen_category(answer):
    return {
        '5H': 'none', '5S': 'low', '5N': 'high', '6C': 'both',
    }.get(answer)
