"""Derived cue bids in an already agreed trump strain.

This family fills side-suit calls that the profile has not explicitly
authored.  It is deliberately meaning-only: selection still decides whether a
cue, game, or keycard is the best route.
"""

from __future__ import annotations

from .derived_semantics import DerivationResult, derived_candidate
from .legality import is_call_legal
from .rkcb_continuation import bid_rank


def derive(profile, auction, trace, evidence, allowed):
    trump = evidence.agreed_trump or evidence.provisional_trump
    if not isinstance(trump, str) or trump not in 'CDHS':
        return DerivationResult(evidence)
    if evidence.contract_level < 4:
        return DerivationResult(evidence)
    game = ('4' + trump) if trump in 'HS' else ('5' + trump)
    if evidence.contract_level >= int(game[0]):
        return DerivationResult(evidence)

    candidates = []
    for call in sorted((item for item in allowed
                        if item not in ('P', 'X', 'R', '4N', '5N')),
                       key=bid_rank):
        if len(call) != 2 or call[1] not in 'CDHS':
            continue
        if call[1] == trump:
            continue
        if bid_rank(call) >= bid_rank(game):
            continue
        if not is_call_legal(auction, call):
            continue
        meaning = {
            'nature_labels': ['artificial'],
            'call_act_types': ['control_showing', 'slam_try'],
            'action_type': 'derived_control_cue',
            'target_suit': trump,
            'agreed_suit': trump,
            'control_suit': call[1],
        }
        candidates.append(derived_candidate(
            call, 'derive_control_cue', meaning, evidence, score=1))
    return DerivationResult(evidence, tuple(candidates))
