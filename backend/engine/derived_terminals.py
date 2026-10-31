"""Derived natural 6NT placement and terminal Pass."""

from __future__ import annotations

from .derived_semantics import DerivationResult, derived_candidate
from .hand_quality import has_good_five_card_suit
from .legality import SIDE_BY_SEAT, is_call_legal


def _confirmed_no_trump(trace, evidence):
    """Only derive 6NT when no possible trump has been shown publicly.

    Absence of an agreed trump is not enough: a transfer superaccept, a
    natural suit, or a supported/guaranteed long suit can still establish a
    fit later.
    """
    if evidence.agreed_trump or evidence.provisional_trump:
        return False
    if evidence.plausible_trumps:
        return False
    if evidence.supported_suits.get(evidence.side):
        return False
    if evidence.guaranteed_long_suits.get(evidence.side):
        return False
    if trace is None:
        return True
    for entry in trace.applied_meanings:
        seat = entry.get('seat')
        if seat is None or SIDE_BY_SEAT.get(seat) != evidence.side:
            continue
        meaning = entry.get('public_meaning', {}) or {}
        if meaning.get('target_suit') in 'CDHS':
            return False
    return True


def derive_six_notrump(profile, auction, trace, evidence, allowed, hand=None):
    if '6N' not in allowed or not is_call_legal(auction, '6N'):
        return DerivationResult(evidence)
    if not _confirmed_no_trump(trace, evidence):
        return DerivationResult(evidence)
    if evidence.contract_level >= 4:
        return DerivationResult(evidence)
    if hand is None:
        return DerivationResult(evidence)
    partner_min = _partner_minimum(trace, evidence.actor)
    total = hand.hcp + partner_min
    qualifies = 33 <= total <= 35 or (total == 32
                                     and has_good_five_card_suit(hand))
    if not qualifies:
        return DerivationResult(evidence)
    meaning = {
        'nature_labels': ['natural'],
        'call_act_types': ['signoff', 'final_placement'],
        'action_type': 'derived_six_notrump_placement',
        'target_suit': 'N',
    }
    return DerivationResult(evidence, (derived_candidate(
        '6N', 'derive_six_notrump', meaning, evidence, score=1),))


def derive_terminal_pass(profile, auction, trace, evidence, allowed, hand=None):
    if 'P' not in allowed or not is_call_legal(auction, 'P'):
        return DerivationResult(evidence)
    if evidence.forcing:
        return DerivationResult(evidence)
    last = _last_meaning(trace)
    if last is None:
        return DerivationResult(evidence)
    seat = last.get('seat')
    partner = {'n': 's', 's': 'n', 'e': 'w', 'w': 'e'}[evidence.actor]
    if seat != partner:
        return DerivationResult(evidence)
    meaning = last.get('public_meaning', {}) or {}
    acts = set(meaning.get('call_act_types', ()) or ())
    if acts & {'forcing', 'game_forcing', 'inquiry', 'relay', 'directive'}:
        return DerivationResult(evidence)
    if any(record.key == 'nfrkcb' for record in trace.current_state_records):
        return DerivationResult(evidence)
    if evidence.provisional_trump:
        return DerivationResult(evidence)
    target = evidence.contract_strain or 'N'
    candidate = derived_candidate(
        'P', 'derive_terminal_pass', {
            'nature_labels': ['natural'],
            'call_act_types': ['signoff', 'final_placement'],
            'action_type': 'derived_terminal_pass',
            'target_suit': target,
        }, evidence, score=1)
    return DerivationResult(evidence, (candidate,))


def _last_meaning(trace):
    entries = [entry for entry in trace.applied_meanings if entry.get('seat')]
    return entries[-1] if entries else None


def _partner_minimum(trace, actor):
    partner = {'n': 's', 's': 'n', 'e': 'w', 'w': 'e'}[actor]
    for entry in reversed(trace.applied_meanings):
        if entry.get('seat') != partner:
            continue
        meaning = entry.get('public_meaning', {}) or {}
        value = meaning.get('hcp_min')
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return int(value)
    return 11
