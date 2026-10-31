"""Derived two-suit keycard for the shortage route in the minor game force.

The state is a small public machine:

    pending -> answered -> queen_ask -> queen_answered
                                \\-> grand_invite -> invite_answered
                                                   \\-> pass_or_correct

Grand invitations are not enumerated per auction.  After an answer that shows a
queen, the asker invites in the lowest side suit whose king the hand lacks.
Side kings below that invitation which the asker already holds are deliberately
skipped.  Responder's control answers, counter-invitations, signoffs, and the
7C pass-or-correct rule are derived from the same public facts.
"""

from __future__ import annotations

from .derived_grand_invite import (
    Invitation, invitation_candidates, invitation_meaning, response_candidates,
    response_meaning, response_score, side_suits,
)
from .derived_semantics import DerivationResult, derived_candidate
from .legality import is_call_legal


def derive(profile, auction, trace, evidence, allowed, hand=None):
    state = _state(trace)
    if state is None:
        return _initial(auction, trace, evidence, allowed)
    status = state.get('status')
    if status == 'pending':
        return _primary_answer(auction, state, evidence, allowed, hand)
    if status == 'answered':
        return _after_primary(auction, trace, state, evidence, allowed, hand)
    if status == 'queen_ask':
        return _queen_answer(auction, state, evidence, allowed, hand)
    if status == 'queen_answered':
        return _after_queen_answer(auction, trace, state, evidence, allowed,
                                   hand)
    if status == 'grand_invite':
        return _grand_response(auction, state, evidence, allowed, hand)
    if status == 'invite_answered':
        return _after_grand_answer(auction, trace, state, evidence, allowed,
                                   hand)
    if status == 'pass_or_correct':
        return _after_pass_or_correct(auction, state, evidence, allowed, hand)
    return DerivationResult(evidence)


# ---------------------------------------------------------------------------
# State entry points


def _initial(auction, trace, evidence, allowed):
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
         'keycards_total': 6, 'asker': auction.actor_to_call},
    )
    return DerivationResult(evidence, (derived_candidate(
        '4N', 'derive_two_suit_keycard', meaning, evidence,
        effects=effects, score=3),))


def _primary_answer(auction, state, evidence, allowed, hand):
    if hand is None:
        return DerivationResult(evidence)
    answer = _answer(hand)
    if answer not in allowed or not is_call_legal(auction, answer):
        return DerivationResult(evidence)
    meaning = {
        'nature_labels': ['artificial'],
        'call_act_types': ['descriptive', 'keycard_answer'],
        'action_type': 'two_suit_keycard_answer',
        'contract_effect': 'none',
        'target_suit': state.get('low_suit', 'C'),
        'keycard_counts': list(_possible_counts(answer)),
        'queen_category': _queen_category(answer),
    }
    effects = (_next_state(
        state, status='answered', answer_call=answer, primary_answer=answer,
        category=_category(answer)),)
    return DerivationResult(evidence, (derived_candidate(
        answer, 'derive_two_suit_keycard_answer', meaning, evidence,
        effects=effects, score=2),))


def _queen_answer(auction, state, evidence, allowed, hand):
    if hand is None:
        return DerivationResult(evidence)
    answer = _queen_answer_for(hand)
    if answer not in allowed or not is_call_legal(auction, answer):
        return DerivationResult(evidence)
    meaning = {
        'nature_labels': ['artificial'],
        'call_act_types': ['descriptive', 'queen_answer'],
        'action_type': 'two_suit_keycard_queen_answer',
        'contract_effect': 'none',
        'target_suit': state.get('low_suit', 'C'),
        'queen_category': _queen_category(answer),
    }
    effects = (_next_state(
        state, status='queen_answered', answer_call=answer,
        queen_answer=answer, queen_category=_queen_category(answer)),)
    return DerivationResult(evidence, (derived_candidate(
        answer, 'derive_two_suit_keycard_queen_answer', meaning, evidence,
        effects=effects, score=2),))


def _after_primary(auction, trace, state, evidence, allowed, hand):
    if not _is_asker(auction, state):
        return DerivationResult(evidence)
    answer = state.get('primary_answer') or state.get('answer_call')
    if answer in ('5C', '5D'):
        result = []
        if '5H' in allowed and is_call_legal(auction, '5H'):
            meaning = {
                'nature_labels': ['artificial'],
                'call_act_types': ['inquiry', 'queen_ask'],
                'action_type': 'two_suit_keycard_queen_ask',
                'target_suit': state.get('low_suit', 'C'),
            }
            effects = (_next_state(state, status='queen_ask'),)
            result.append(derived_candidate(
                '5H', 'derive_two_suit_keycard_queen_ask', meaning,
                evidence, effects=effects, score=8))
        result.extend(_placement_derivations(
            auction, trace, state, evidence, allowed))
        return DerivationResult(evidence, tuple(result))
    if answer == '5H':
        return _placements_only(auction, trace, state, evidence, allowed)
    result = _invitation_derivations(
        hand, answer, state, evidence, allowed,
        allow_five_notrump=(answer == '5S'))
    result.extend(_placement_derivations(
        auction, trace, state, evidence, allowed))
    return DerivationResult(evidence, tuple(result))


def _after_queen_answer(auction, trace, state, evidence, allowed, hand):
    if not _is_asker(auction, state):
        return DerivationResult(evidence)
    answer = state.get('queen_answer') or state.get('answer_call')
    if answer == '6C':
        return _placements_only(auction, trace, state, evidence, allowed)
    result = _invitation_derivations(
        hand, answer, state, evidence, allowed,
        allow_five_notrump=(answer == '5S'))
    result.extend(_placement_derivations(
        auction, trace, state, evidence, allowed))
    return DerivationResult(evidence, tuple(result))


def _grand_response(auction, state, evidence, allowed, hand):
    invitation = _invitation_from_state(state)
    if invitation is None:
        return DerivationResult(evidence)
    responses = response_candidates(
        hand, invitation, state.get('low_suit', 'C'),
        state.get('high_suit', 'D'), allowed,
        prefer_accept_when_ready=True)
    result = []
    for response in responses:
        if response.call not in allowed or not is_call_legal(
                auction, response.call):
            continue
        meaning = response_meaning(
            response, invitation, state.get('low_suit', 'C'),
            state.get('high_suit', 'D'))
        if response.kind == 'accept':
            effects = (_next_state(
                state, status='pass_or_correct',
                grand_answer_call=response.call,
                shown_king=invitation.suit,
                accepted_grand=True),)
        elif response.kind == 'k_answer':
            effects = (_next_state(
                state, status='invite_answered',
                grand_answer_call=response.call,
                shown_king=response.control_suit),)
        else:
            effects = (_next_state(
                state, status='invite_answered',
                grand_answer_call=response.call),)
        rule = {
            'accept': 'derive_two_suit_keycard_grand_accept',
            'k_answer': 'derive_two_suit_keycard_grand_k_answer',
            'signoff': 'derive_two_suit_keycard_grand_signoff',
        }[response.kind]
        result.append(derived_candidate(
            response.call, rule, meaning, evidence,
            effects=effects, score=response_score(response)))
    return DerivationResult(evidence, tuple(result))


def _after_grand_answer(auction, trace, state, evidence, allowed, hand):
    if not _is_asker(auction, state):
        return DerivationResult(evidence)
    answer = state.get('grand_answer_call')
    if answer in ('6C', '6N'):
        grand = _grand_after_no_king(hand, state)
        result = []
        if 'P' in allowed and is_call_legal(auction, 'P'):
            result.append(derived_candidate(
                'P', 'derive_two_suit_keycard_grand_pass', {
                    'nature_labels': ['natural'],
                    'call_act_types': ['signoff', 'final_placement'],
                    'action_type': 'two_suit_keycard_grand_pass',
                    'target_suit': 'N' if answer == '6N'
                    else state.get('low_suit', 'C'),
                    'purpose_completed': True,
                }, evidence, score=5 if grand else 7))
        low_suit = state.get('low_suit', 'C')
        high_suit = state.get('high_suit', 'D')
        bonus = (('7D',) if _prefer_high_trump(hand, low_suit, high_suit)
                 else ('7C',)) if grand else ()
        result.extend(_placement_derivations(
            auction, trace, state, evidence, allowed, bonus_calls=bonus,
            excluded_calls=() if grand else ('7C', '7D')))
        return DerivationResult(evidence, tuple(result))
    result = _invitation_derivations(
        hand, answer, state, evidence, allowed, allow_five_notrump=False)
    low_suit = state.get('low_suit', 'C')
    high_suit = state.get('high_suit', 'D')
    if _all_side_kings_known(hand, state, low_suit, high_suit):
        bonus = (('7D',) if _prefer_high_trump(hand, low_suit, high_suit)
                 else ('7C',))
        excluded = ()
    else:
        # A side king is still missing after the control answer.  6NT is the
        # deterministic signoff; seven of a trump is no longer offered.
        bonus = ('6N',)
        excluded = ('7C', '7D')
    result.extend(_placement_derivations(
        auction, trace, state, evidence, allowed, bonus_calls=bonus,
        excluded_calls=excluded))
    return DerivationResult(evidence, tuple(result))


def _after_pass_or_correct(auction, state, evidence, allowed, hand):
    if not _is_asker(auction, state):
        return DerivationResult(evidence)
    low_suit = state.get('low_suit', 'C')
    high_suit = state.get('high_suit', 'D')
    prefer_high = _prefer_high_trump(hand, low_suit, high_suit)
    result = []
    if 'P' in allowed and is_call_legal(auction, 'P'):
        result.append(derived_candidate(
            'P', 'derive_two_suit_keycard_pass_or_correct', {
                'nature_labels': ['natural'],
                'call_act_types': ['signoff', 'final_placement'],
                'action_type': 'two_suit_keycard_pass_or_correct',
                'target_suit': low_suit,
                'agreed_suit': low_suit,
                'purpose_completed': True,
            }, evidence, score=5 if prefer_high else 7))
    if '7D' in allowed and is_call_legal(auction, '7D'):
        result.append(derived_candidate(
            '7D', 'derive_two_suit_keycard_grand_correction', {
                'nature_labels': ['natural'],
                'call_act_types': ['signoff', 'final_placement'],
                'action_type': 'two_suit_keycard_grand_correction',
                'target_suit': high_suit,
                'agreed_suit': high_suit,
                'purpose_completed': True,
            }, evidence, effects=(_next_state(
                state, status='completed', final_call='7D'),),
            score=7 if prefer_high else 5))
    return DerivationResult(evidence, tuple(result))


# ---------------------------------------------------------------------------
# Candidate builders


def _invitation_derivations(hand, answer_call, state, evidence, allowed,
                            *, allow_five_notrump):
    low_suit = state.get('low_suit', 'C')
    high_suit = state.get('high_suit', 'D')
    result = []
    for invitation in invitation_candidates(
            hand, answer_call, low_suit, high_suit, allowed,
            allow_five_notrump=allow_five_notrump):
        effects = (_next_state(
            state, status='grand_invite',
            invitation_call=invitation.call,
            invitation_kind=invitation.kind,
            invitation_suit=invitation.suit,
            skipped_kings=list(invitation.skipped_kings),
            unintentionally_skipped_kings=list(
                invitation.unintentionally_skipped_kings),
            grand_answer_call=None,
            shown_king=None),)
        result.append(derived_candidate(
            invitation.call,
            'derive_two_suit_keycard_grand_invitation',
            invitation_meaning(invitation, low_suit, high_suit), evidence,
            effects=effects, score=invitation.score))
    return result


def _placement_derivations(auction, trace, state, evidence, allowed,
                           *, bonus_calls=(), excluded_calls=()):
    last = _last_call(trace)
    low_suit = state.get('low_suit', 'C')
    high_suit = state.get('high_suit', 'D')
    result = []
    for call, suit in (('6C', low_suit), ('6D', high_suit), ('6N', 'N'),
                       ('7C', low_suit), ('7D', high_suit)):
        if call == last or call in excluded_calls:
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
        effects = (_next_state(state, status='completed', final_call=call),)
        result.append(derived_candidate(
            call, 'derive_two_suit_keycard_placement', meaning, evidence,
            effects=effects, score=7 if call in bonus_calls else 2))
    return result


def _placements_only(auction, trace, state, evidence, allowed):
    return DerivationResult(evidence, tuple(_placement_derivations(
        auction, trace, state, evidence, allowed)))


# ---------------------------------------------------------------------------
# State helpers


def _state(trace):
    if trace is None:
        return None
    for record in reversed(trace.current_state_records):
        if record.key == 'two_suit_keycard':
            return record.attributes
    return None


def _next_state(state, **updates):
    result = {'key': 'two_suit_keycard',
              **{key: value for key, value in state.items()
                 if key not in ('key', 'status')}}
    result.update(updates)
    return result


def _is_asker(auction, state):
    asker = state.get('asker')
    return asker is None or auction.actor_to_call == asker


def _last_call(trace):
    if trace is None:
        return None
    for entry in reversed(trace.applied_meanings):
        if entry.get('call') not in ('P', 'X', 'R'):
            return entry.get('call')
    return None


def _invitation_from_state(state):
    call = state.get('invitation_call')
    if not call:
        return None
    return Invitation(
        call=call,
        kind=state.get('invitation_kind') or (
            'five_notrump' if call == '5N' else 'six_level'),
        suit=state.get('invitation_suit'),
        skipped_kings=tuple(state.get('skipped_kings') or ()),
        unintentionally_skipped_kings=tuple(
            state.get('unintentionally_skipped_kings') or ()),
        score=0,
    )


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
    if trace is None:
        return False
    return any(
        (entry.get('public_meaning', {}) or {}).get('action_type')
        == 'two_minor_game_force'
        for entry in trace.applied_meanings)


# ---------------------------------------------------------------------------
# Hand reading


def _grand_after_no_king(hand, state):
    """Conservative surrogate for the requested sampled grand decision.

    With both side kings in the asker's hand and a keycard count that pairs
    with the 2-or-5 answer to all six keycards, a no-king reply still leaves
    the grand worth placing.  The sampler can replace this preference later.
    """
    if hand is None:
        return False
    keycards = (hand.ace_count()
                + int(hand.contains_rank('C', 'K'))
                + int(hand.contains_rank('D', 'K')))
    return (hand.contains_rank('H', 'K')
            and hand.contains_rank('S', 'K')
            and keycards in (1, 4)
            and state.get('primary_answer') in ('5S', '5N', '6C'))


def _all_side_kings_known(hand, state, low_suit, high_suit):
    if hand is None:
        return False
    sides = side_suits(low_suit, high_suit)
    known = {suit for suit in sides if hand.contains_rank(suit, 'K')}
    shown = state.get('shown_king')
    if shown in sides:
        known.add(shown)
    return set(sides) <= known


def _prefer_high_trump(hand, low_suit, high_suit):
    if hand is None:
        return False
    low_length = hand.length(low_suit)
    high_length = hand.length(high_suit)
    if low_length != high_length:
        return high_length > low_length
    low_honors = sum(hand.contains_rank(low_suit, rank) for rank in 'AKQJ')
    high_honors = sum(hand.contains_rank(high_suit, rank) for rank in 'AKQJ')
    return high_honors > low_honors


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


def _queen_answer_for(hand):
    low_q = hand.contains_rank('C', 'Q')
    high_q = hand.contains_rank('D', 'Q')
    if not low_q and not high_q:
        return '6C'
    if low_q and not high_q:
        return '5S'
    if high_q and not low_q:
        return '5N'
    if hand.contains_rank('H', 'K'):
        return '6H'
    if hand.contains_rank('S', 'K'):
        return '6S'
    return '6N'


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
