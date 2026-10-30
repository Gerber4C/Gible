"""Derived three-level fit calls.

Major fits expose the serious/non-serious relay and genuine control cues.
Minor fits preserve 3NT space: a new suit below 3NT is a stopper inquiry while
3NT is live; after slam interest it is a control cue. Simulation may choose
among these already-classified routes but never defines a meaning.
"""

from __future__ import annotations

from .derived_semantics import DerivationResult, derived_candidate
from .legality import is_call_legal, legal_calls
from .rkcb_continuation import bid_rank


def derive(profile, auction, trace, evidence, allowed):
    if evidence.agreed_trump is None or evidence.agreed_trump not in 'CDHS':
        return DerivationResult(evidence)
    if evidence.contract_level > 3:
        return DerivationResult(evidence)
    candidates = []
    conflicts = []
    if evidence.agreed_trump in 'HS':
        candidates.extend(_major_fit_candidates(auction, evidence, allowed))
    else:
        result = _minor_fit_candidates(auction, evidence, allowed)
        candidates.extend(result.candidates)
        conflicts.extend(result.conflicts)
    return DerivationResult(evidence, tuple(candidates), tuple(conflicts))


def _major_fit_candidates(auction, evidence, allowed):
    result = []
    relay = _serious_relay(auction, evidence, allowed)
    relay_call = relay.call if relay is not None else None
    if relay is not None:
        result.append(relay)
    for call in sorted((item for item in allowed
                        if item not in ('P', 'X', 'R')), key=bid_rank):
        if (call in ('P', 'X', 'R', '3NT', '4NT')
                or call == relay_call or call[0] not in '34'):
            continue
        if call[1] not in 'CDHS' or call[1] == evidence.agreed_trump:
            continue
        if bid_rank(call) > bid_rank('4' + evidence.agreed_trump):
            continue
        meaning = {
            'nature_labels': ['artificial'],
            'call_act_types': ['control_showing', 'slam_try'],
            'action_type': 'derived_major_control_cue',
            'target_suit': evidence.agreed_trump,
            'agreed_suit': evidence.agreed_trump,
            'control_suit': call[1],
        }
        result.append(derived_candidate(
            call, 'derive_major_control_cue', meaning, evidence, score=1))
    return result


def _serious_relay(auction, evidence, allowed):
    if evidence.agreed_trump == 'H' and '3NT' not in allowed:
        call = '3S'
    else:
        call = '3NT'
    if call not in allowed or not is_call_legal(auction, call):
        return None
    meaning = {
        'nature_labels': ['artificial'],
        'call_act_types': ['serious_relay', 'inquiry'],
        'action_type': 'derived_serious_relay',
        'target_suit': evidence.agreed_trump,
        'agreed_suit': evidence.agreed_trump,
    }
    return derived_candidate(call, 'derive_serious_relay', meaning, evidence,
                             score=2)


def _minor_fit_candidates(auction, evidence, allowed):
    from .derived_semantics import DerivationResult
    result = []
    conflicts = []
    stopper_live = evidence.three_notrump_available and is_call_legal(
        auction, '3NT')
    stopper_suits = set(evidence.enemy_suits)
    if not stopper_suits:
        stopper_suits = {call[1] for call in allowed
                         if call[0] == '3' and call[1] in 'CDHS'
                         and call[1] != evidence.agreed_trump}
    natural_new = [call for call in sorted((item for item in allowed
                                            if item not in ('P', 'X', 'R')),
                                           key=bid_rank)
                   if call[0] in '23' and call[1] in 'CDHS'
                   and call[1] != evidence.agreed_trump]
    for call in natural_new:
        suit = call[1]
        if stopper_live and suit in stopper_suits:
            meaning = {
                'nature_labels': ['artificial'],
                'call_act_types': ['stopper_inquiry', 'inquiry'],
                'action_type': 'derived_minor_stopper_inquiry',
                'target_suit': evidence.agreed_trump,
                'agreed_suit': evidence.agreed_trump,
                'stopper_suit': suit,
            }
            result.append(derived_candidate(
                call, 'derive_minor_stopper_inquiry', meaning, evidence,
                score=2))
        elif not stopper_live:
            meaning = {
                'nature_labels': ['artificial'],
                'call_act_types': ['control_showing', 'slam_try'],
                'action_type': 'derived_minor_control_cue',
                'target_suit': evidence.agreed_trump,
                'agreed_suit': evidence.agreed_trump,
                'control_suit': suit,
            }
            result.append(derived_candidate(
                call, 'derive_minor_control_cue', meaning, evidence, score=1))
        else:
            conflicts.append({
                'code': 'MINOR_FIT_AMBIGUOUS_NEW_SUIT',
                'call': call,
                'message': ('A new minor-suit call could be natural, a stopper '
                            'inquiry, or a control cue'),
            })
    return DerivationResult(evidence, tuple(result), tuple(conflicts))
