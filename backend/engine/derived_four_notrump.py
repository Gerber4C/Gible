"""Derived 4NT and trump-selector mapping.

Only otherwise undefined calls are considered. Raises are pinned first, then
remaining selectors are paired with candidate trumps in ascending bridge order.
"""

from __future__ import annotations

from .derived_semantics import DerivationResult, derived_candidate
from .nfrkcb_policy import offer_effect, single_suit_offer
from .legality import is_call_legal
from .rkcb_continuation import bid_rank


def derive(profile, auction, trace, evidence, allowed):
    if '4N' not in allowed or not is_call_legal(auction, '4N'):
        return DerivationResult(evidence)
    if len(evidence.plausible_trumps) > 2:
        return DerivationResult(evidence, conflicts=(
            {'code': 'FOUR_NOTRUMP_TOO_MANY_TRUMPS',
             'plausible_trumps': list(evidence.plausible_trumps),
             'message': 'Derived 4NT supports at most two plausible trumps'},))

    candidates = []
    conflicts = []
    if evidence.agreed_trump:
        candidates.append(_keycard(evidence, evidence.agreed_trump))
        return DerivationResult(evidence, tuple(candidates))

    raises = [item for item in evidence.classified_calls
              if item.kind == 'raise' and item.establishes_trump]
    selectors = [item for item in evidence.classified_calls
                 if item.kind == 'selector' and item.establishes_trump]
    candidates.extend(_selector_candidates(selectors, allowed, evidence))

    candidate_trumps = list(evidence.plausible_trumps)
    if not candidate_trumps:
        return DerivationResult(evidence, tuple(candidates))

    if evidence.contract_level <= 3:
        if (evidence.forcing and len(candidate_trumps) == 1
                and not raises and not selectors):
            candidates.append(_keycard(evidence, candidate_trumps[0]))
        else:
            candidates.append(_quantitative(evidence))
        return DerivationResult(evidence, tuple(candidates))

    if evidence.contract_level == 4:
        mapping, error = _four_level_mapping(
            candidate_trumps, raises, selectors)
        if error:
            conflicts.append(error)
        elif mapping == 'quantitative':
            candidates.append(_quantitative(evidence))
        else:
            candidates.append(_keycard(evidence, mapping))
        return DerivationResult(evidence, tuple(candidates), tuple(conflicts))

    return DerivationResult(evidence, tuple(candidates), tuple(conflicts))


def _four_level_mapping(trumps, raises, selectors):
    if len(trumps) == 1:
        if raises or selectors:
            return None, {
                'code': 'FOUR_NOTRUMP_ALREADY_COVERED',
                'message': 'A lower raise or selector already covers the sole trump',
            }
        return trumps[0], None
    raise_suits = {item.establishes_trump for item in raises}
    remaining = [suit for suit in trumps if suit not in raise_suits]
    if not raises:
        if len(selectors) == 1 and len(trumps) == 2:
            return trumps[1], None
        if len(selectors) == 2 and len(trumps) == 2:
            return 'quantitative', None
        return None, {
            'code': 'FOUR_NOTRUMP_SELECTOR_COUNT_MISMATCH',
            'message': 'Selectors and candidate trumps do not pair uniquely',
        }
    if len(raises) == 1:
        if not selectors:
            return remaining[0], None
        return 'quantitative', None
    if len(raises) + len(selectors) >= len(trumps):
        return 'quantitative', None
    return None, {
        'code': 'FOUR_NOTRUMP_UNRESOLVED_MAPPING',
        'message': 'Raise/selector counts do not fit a unique 4NT mapping',
    }


def _selector_candidates(selectors, allowed, evidence):
    result = []
    for item in selectors:
        if item.call not in allowed:
            continue
        meaning = {
            'nature_labels': ['artificial'],
            'call_act_types': ['trump_selector'],
            'action_type': 'derived_trump_selector',
            'target_suit': item.establishes_trump,
            'agreed_suit': item.establishes_trump,
        }
        effects = ({'key': 'trump_state', 'status': 'provisional',
                    'suit': item.establishes_trump},)
        result.append(derived_candidate(
            item.call, 'derive_four_notrump_selector', meaning, evidence,
            effects=effects, score=1))
    return result


def _keycard(evidence, trump):
    meaning = {
        'nature_labels': ['artificial'],
        'call_act_types': ['inquiry', 'keycard_asking'],
        'action_type': 'rkcb_1430',
        'target_suit': trump,
        'agreed_suit': trump,
    }
    effects = (
        {'key': 'agreed_suit', 'suit': trump},
        {'key': 'keycard_context', 'method': 'rkcb_1430',
         'trump_suit': trump, 'ask_call': '4N', 'status': 'pending'},
    )
    return derived_candidate('4N', 'derive_four_notrump_keycard', meaning,
                             evidence, effects=effects, score=2)


def _quantitative(evidence):
    meaning = {
        'nature_labels': ['natural'],
        'call_act_types': ['quantitative_invite'],
        'action_type': 'quantitative_4nt',
        'target_suit': 'N',
    }
    suit = single_suit_offer(evidence)
    effects = ()
    if suit is not None:
        meaning['call_act_types'] = ['quantitative_invite', 'nfrkcb_offer']
        meaning['nfrkcb_method'] = 'nfrkcb_offer'
        meaning['agreed_suit'] = suit
        effects = (offer_effect(suit, evidence.actor),)
    return derived_candidate('4N', 'derive_four_notrump_quantitative',
                             meaning, evidence, effects=effects, score=1)
