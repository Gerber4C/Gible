"""Derived final trump placement after a 5S keycard answer."""

from __future__ import annotations

from .derived_semantics import DerivationResult, derived_candidate
from .legality import is_call_legal
from .rkcb_continuation import ordinary_rkcb_frame, partner_of_last_bidder


def derive(profile, auction, trace, evidence, allowed):
    frame = ordinary_rkcb_frame(trace)
    if frame is None or frame.status != 'answered':
        return DerivationResult(evidence)
    if frame.answer_call != '5S':
        return DerivationResult(evidence)
    if partner_of_last_bidder(auction) != auction.actor_to_call:
        return DerivationResult(evidence)
    trump = frame.trump
    result = []
    for call, score in (('6' + trump, 2), ('7' + trump, 1)):
        if call not in allowed or not is_call_legal(auction, call):
            continue
        meaning = {
            'nature_labels': ['natural'],
            'call_act_types': ['signoff', 'final_placement'],
            'action_type': 'keycard_final_placement',
            'target_suit': trump,
            'agreed_suit': trump,
            'purpose_completed': True,
        }
        result.append(derived_candidate(
            call, 'derive_keycard_final_placement', meaning, evidence,
            score=score))
    return DerivationResult(evidence, tuple(result))
