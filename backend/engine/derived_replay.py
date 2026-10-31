"""Hand-free reconstruction of a derived historical call."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .derived_evidence import collect_evidence
from .derived_semantics import derive_candidates, reserved_calls
from .nfrkcb_policy import answer_effect
from .rkcb_continuation import ordinary_response


@dataclass(frozen=True)
class HistoricalDerivation:
    call: str
    rule: str | None = None
    public_meaning: dict[str, Any] | None = None
    effects: tuple[dict[str, Any], ...] = ()
    conflict: dict[str, Any] | None = None
    evidence: Any = None


def derive_historical_call(profile, auction, call, trace) -> HistoricalDerivation:
    evidence = collect_evidence(profile, auction, trace)
    offer = _nfrkcb_offer(trace)
    if offer is not None and auction.actor_to_call == _partner(offer.attribute('offerer')):
        trump = offer.attribute('trump_suit')
        offerer = offer.attribute('offerer')
        if call == 'P':
            return _nfrkcb_historical(call, 'nfrkcb_accept', {
                'nature_labels': ['natural'],
                'call_act_types': ['signoff', 'final_placement'],
                'action_type': 'nfrkcb_accept',
                'target_suit': 'N',
                'agreed_suit': trump,
            }, (answer_effect(trump, offerer, 'P'),), evidence)
        if call in ('5C', '5D', '5H', '5S'):
            counts = {'5C': [1, 4], '5D': [0, 3], '5H': [2], '5S': [2]}[call]
            meaning = {
                'nature_labels': ['artificial'],
                'call_act_types': ['descriptive', 'keycard_answer'],
                'action_type': 'nfrkcb_answer',
                'target_suit': trump,
                'agreed_suit': trump,
                'keycard_counts': counts,
            }
            effects = (
                answer_effect(trump, offerer, call),
                {'key': 'keycard_context', 'method': 'rkcb_1430',
                 'trump_suit': trump, 'status': 'answered',
                 'answer_call': call, 'answer_category': 'nfrkcb',
                 'keycard_counts': counts},
            )
            return _nfrkcb_historical(call, 'nfrkcb_answer', meaning,
                                      effects, evidence)
    two_suit = _two_suit_keycard_historical(trace, call, evidence)
    if two_suit is not None:
        return two_suit
    shortage = _minor_shortage_context(trace)
    if shortage == 'S' and call == '4N':
        return HistoricalDerivation(
            call, rule='derive_two_suit_keycard',
            public_meaning={
                'nature_labels': ['artificial'],
                'call_act_types': ['inquiry', 'keycard_asking'],
                'action_type': 'two_suit_keycard',
                'target_suit': 'C',
                'suits': ['C', 'D'],
                'keycards_total': 6,
            },
            effects=(
                {'key': 'two_suit_keycard', 'status': 'pending',
                 'method': 'two_suit_keycard', 'low_suit': 'C',
                 'high_suit': 'D', 'keycards_total': 6,
                 'asker': auction.actor_to_call},
            ),
            evidence=evidence)
    if shortage == 'H' and call == '4S':
        return HistoricalDerivation(
            call, rule='derive_shortage_club_support',
            public_meaning={
                'nature_labels': ['artificial'],
                'call_act_types': ['support', 'slam_try'],
                'action_type': 'derived_shortage_club_support',
                'target_suit': 'C',
                'agreed_suit': 'C',
            },
            effects=({'key': 'agreed_suit', 'suit': 'C'},),
            evidence=evidence)
    if shortage == 'H' and call == '4N':
        return HistoricalDerivation(
            call, rule='derive_shortage_diamond_keycard',
            public_meaning={
                'nature_labels': ['artificial'],
                'call_act_types': ['inquiry', 'keycard_asking'],
                'action_type': 'rkcb_1430',
                'target_suit': 'D',
                'agreed_suit': 'D',
            },
            effects=(
                {'key': 'agreed_suit', 'suit': 'D'},
                {'key': 'keycard_context', 'method': 'rkcb_1430',
                 'trump_suit': 'D', 'ask_call': '4N', 'status': 'pending'},
            ),
            evidence=evidence)
    reserved = reserved_calls(profile, auction, trace)
    if call in reserved:
        return HistoricalDerivation(call, conflict={
            'code': 'EXPLICIT_CALL_RESERVED',
            'call': call,
            'message': 'An explicit profile definition owns this call',
        }, evidence=evidence)
    result = derive_candidates(profile, auction, trace, evidence, reserved)
    matches = [candidate for candidate in result.candidates
               if candidate.call == call]
    if len(matches) == 1:
        candidate = matches[0]
        return HistoricalDerivation(
            call, rule=candidate.metadata.get('derived_rule'),
            public_meaning=dict(candidate.public_meaning),
            effects=tuple(candidate.metadata.get('derived_effects', ())),
            evidence=evidence)
    if len(matches) > 1:
        return HistoricalDerivation(
            call, conflict={'code': 'AMBIGUOUS_DERIVED_MEANING',
                            'call': call,
                            'rules': [item.metadata.get('derived_rule')
                                      for item in matches],
                            'message': 'Multiple derived meanings claim this call'},
            evidence=evidence)
    if call == '6N':
        # 6NT is hand-dependent when selected, but its public meaning is a
        # natural final small-slam placement. Replay cannot see the earlier
        # actor's hand, so publish that meaning here instead of leaving the
        # next player with an undefined prior call.
        return HistoricalDerivation(
            call, rule='derive_six_notrump_placement',
            public_meaning={
                'nature_labels': ['natural'],
                'call_act_types': ['signoff', 'final_placement'],
                'action_type': 'derived_six_notrump_placement',
                'target_suit': 'N',
                'purpose_completed': True,
            },
            evidence=evidence)
    conflicts = [item for item in result.conflicts
                 if item.get('call') in (None, call)]
    return HistoricalDerivation(
        call,
        conflict=(conflicts[0] if conflicts else {
            'code': 'NO_DERIVED_MEANING',
            'call': call,
            'message': 'No derivation rule assigns this call',
        }),
        evidence=evidence)


def _nfrkcb_offer(trace):
    for record in reversed(trace.current_state_records):
        if (record.key == 'nfrkcb'
                and record.attribute('method') == 'nfrkcb_offer'):
            return record
    return None


_TWO_SUIT_PRIMARY_ANSWERS = ('5C', '5D', '5H', '5S', '5N', '6C')
_TWO_SUIT_QUEEN_ANSWERS = ('6C', '5S', '5N', '6H', '6S', '6N')
_TWO_SUIT_PLACEMENTS = ('6C', '6D', '6N', '7C', '7D')


def _two_suit_keycard_historical(trace, call, evidence):
    record = _two_suit_keycard_latest(trace)
    if record is None:
        return None
    state = dict(record.attributes)
    status = state.get('status')
    low_suit = state.get('low_suit') or 'C'
    high_suit = state.get('high_suit') or 'D'

    if status == 'pending' and call in _TWO_SUIT_PRIMARY_ANSWERS:
        category = {
            '5C': '14', '5D': '036', '5H': '25_none',
            '5S': '25_low', '5N': '25_high', '6C': '25_both',
        }[call]
        counts = {
            '5C': (1, 4), '5D': (0, 3, 6), '5H': (2, 5),
            '5S': (2, 5), '5N': (2, 5), '6C': (2, 5),
        }[call]
        return HistoricalDerivation(
            call, rule='derive_two_suit_keycard_answer',
            public_meaning={
                'nature_labels': ['artificial'],
                'call_act_types': ['descriptive', 'keycard_answer'],
                'action_type': 'two_suit_keycard_answer',
                'contract_effect': 'none',
                'target_suit': low_suit,
                'keycard_counts': list(counts),
                'queen_category': _queen_category(call),
            },
            effects=(_carry_replay(
                state, status='answered', answer_call=call,
                primary_answer=call, category=category),),
            evidence=evidence)

    if status == 'answered':
        answer = state.get('primary_answer') or state.get('answer_call')
        if call == '5H' and answer in ('5C', '5D'):
            return HistoricalDerivation(
                call, rule='derive_two_suit_keycard_queen_ask',
                public_meaning={
                    'nature_labels': ['artificial'],
                    'call_act_types': ['inquiry', 'queen_ask'],
                    'action_type': 'two_suit_keycard_queen_ask',
                    'target_suit': low_suit,
                },
                effects=(_carry_replay(state, status='queen_ask'),),
                evidence=evidence)
        if _two_suit_invitation_allowed(call, answer):
            return _two_suit_invitation_historical(
                call, state, evidence)
        if call in _TWO_SUIT_PLACEMENTS:
            return _two_suit_placement_historical(
                call, state, evidence)

    if status == 'queen_ask' and call in _TWO_SUIT_QUEEN_ANSWERS:
        category = {
            '6C': 'none', '5S': 'low', '5N': 'high',
            '6H': 'both_hk', '6S': 'both_sk', '6N': 'both_none',
        }[call]
        return HistoricalDerivation(
            call, rule='derive_two_suit_keycard_queen_answer',
            public_meaning={
                'nature_labels': ['artificial'],
                'call_act_types': ['descriptive', 'queen_answer'],
                'action_type': 'two_suit_keycard_queen_answer',
                'contract_effect': 'none',
                'target_suit': low_suit,
                'queen_category': category,
            },
            effects=(_carry_replay(
                state, status='queen_answered', answer_call=call,
                queen_answer=call, queen_category=category),),
            evidence=evidence)

    if status == 'queen_answered':
        answer = state.get('queen_answer') or state.get('answer_call')
        if _two_suit_invitation_allowed(call, answer):
            return _two_suit_invitation_historical(
                call, state, evidence)
        if call in _TWO_SUIT_PLACEMENTS:
            return _two_suit_placement_historical(
                call, state, evidence)

    if status == 'grand_invite' and call in ('6C', '6H', '6S', '6N', '7C'):
        invitation = state.get('invitation_call')
        if call == '7C':
            return HistoricalDerivation(
                call, rule='derive_two_suit_keycard_grand_accept',
                public_meaning={
                    'nature_labels': ['natural'],
                    'call_act_types': ['signoff', 'final_placement',
                                       'grand_accept'],
                    'action_type': 'two_suit_keycard_grand_accept',
                    'target_suit': low_suit,
                    'agreed_suit': low_suit,
                    'pass_or_correct': 'pure',
                    'control_suit': state.get('invitation_suit'),
                    'purpose_completed': True,
                },
                effects=(_carry_replay(
                    state, status='pass_or_correct',
                    grand_answer_call=call,
                    shown_king=state.get('invitation_suit'),
                    accepted_grand=True),),
                evidence=evidence)
        if call in ('6H', '6S') and call != invitation:
            return HistoricalDerivation(
                call, rule='derive_two_suit_keycard_grand_k_answer',
                public_meaning={
                    'nature_labels': ['artificial'],
                    'call_act_types': ['descriptive', 'control_showing',
                                       'slam_try', 'invite'],
                    'action_type': 'two_suit_keycard_grand_k_answer',
                    'contract_effect': 'none',
                    'target_suit': low_suit,
                    'suits': [low_suit, high_suit],
                    'control_suit': call[1],
                    'invitation_call': invitation,
                    'skipped_kings': list(state.get('skipped_kings') or ()),
                },
                effects=(_carry_replay(
                    state, status='invite_answered',
                    grand_answer_call=call, shown_king=call[1]),),
                evidence=evidence)
        if call in ('6C', '6N'):
            return HistoricalDerivation(
                call, rule='derive_two_suit_keycard_grand_signoff',
                public_meaning={
                    'nature_labels': ['natural'],
                    'call_act_types': ['signoff', 'final_placement',
                                       'invite_minus'],
                    'action_type': 'two_suit_keycard_grand_signoff',
                    'target_suit': 'N' if call == '6N' else low_suit,
                    'suits': [low_suit, high_suit],
                    'purpose_completed': True,
                },
                effects=(_carry_replay(
                    state, status='invite_answered',
                    grand_answer_call=call),),
                evidence=evidence)

    if status == 'invite_answered':
        answer = state.get('grand_answer_call')
        if answer == '6H' and call == '6S':
            return _two_suit_invitation_historical(
                call, state, evidence, skipped_kings=('H',))
        if call in _TWO_SUIT_PLACEMENTS:
            return _two_suit_placement_historical(
                call, state, evidence)

    if status == 'pass_or_correct' and call == '7D':
        return HistoricalDerivation(
            call, rule='derive_two_suit_keycard_grand_correction',
            public_meaning={
                'nature_labels': ['natural'],
                'call_act_types': ['signoff', 'final_placement'],
                'action_type': 'two_suit_keycard_grand_correction',
                'target_suit': high_suit,
                'agreed_suit': high_suit,
                'purpose_completed': True,
            },
            effects=(_carry_replay(
                state, status='completed', final_call=call),),
            evidence=evidence)
    return None


def _two_suit_invitation_allowed(call, answer):
    if call == '5N':
        return answer == '5S'
    if call in ('6H', '6S'):
        return answer in ('5S', '5N', '6C', '6H', '6S')
    return False


def _two_suit_invitation_historical(call, state, evidence,
                                    skipped_kings=None):
    low_suit = state.get('low_suit') or 'C'
    high_suit = state.get('high_suit') or 'D'
    kind = 'five_notrump' if call == '5N' else 'six_level'
    suit = None if call == '5N' else call[1]
    if skipped_kings is None:
        skipped = () if call != '6S' else ('H',)
    else:
        skipped = tuple(skipped_kings)
    return HistoricalDerivation(
        call, rule='derive_two_suit_keycard_grand_invitation',
        public_meaning={
            'nature_labels': ['artificial'],
            'call_act_types': ['invite', 'slam_try'],
            'action_type': 'two_suit_keycard_grand_invitation',
            'target_suit': low_suit,
            'suits': [low_suit, high_suit],
            'invitation_kind': kind,
            'invitation_suit': suit,
            'skipped_kings': list(skipped),
            'unintentionally_skipped_kings': [],
        },
        effects=(_carry_replay(
            state, status='grand_invite', invitation_call=call,
            invitation_kind=kind, invitation_suit=suit,
            skipped_kings=list(skipped),
            unintentionally_skipped_kings=[],
            grand_answer_call=None, shown_king=None),),
        evidence=evidence)


def _two_suit_placement_historical(call, state, evidence):
    suit = 'N' if call == '6N' else call[1]
    return HistoricalDerivation(
        call, rule='derive_two_suit_keycard_placement',
        public_meaning={
            'nature_labels': ['natural'],
            'call_act_types': ['signoff', 'final_placement'],
            'action_type': 'two_suit_keycard_placement',
            'target_suit': suit,
            'agreed_suit': suit if suit in 'CD' else None,
            'purpose_completed': True,
        },
        effects=(_carry_replay(
            state, status='completed', final_call=call),),
        evidence=evidence)


def _carry_replay(state, **updates):
    result = {'key': 'two_suit_keycard',
              **{key: value for key, value in state.items()
                 if key not in ('key', 'status')}}
    result.update(updates)
    return result


def _queen_category(call):
    return {
        '5H': 'none', '5S': 'low', '5N': 'high', '6C': 'both',
    }.get(call)


def _minor_shortage_context(trace):
    has_two_minor = any(
        (entry.get('public_meaning', {}) or {}).get('action_type')
        == 'two_minor_game_force'
        for entry in trace.applied_meanings)
    if not has_two_minor:
        return None
    for entry in reversed(trace.applied_meanings):
        if entry.get('call') in ('P', 'X', 'R'):
            continue
        meaning = entry.get('public_meaning', {}) or {}
        if meaning.get('action_type') == 'minor_shortage_slam_try':
            return meaning.get('shortage_suit')
        return None
    return None


def _two_suit_keycard_latest(trace):
    for record in reversed(trace.current_state_records):
        if record.key == 'two_suit_keycard':
            return record
    return None


def _partner(seat):
    return {'n': 's', 's': 'n', 'e': 'w', 'w': 'e'}[seat]


def _nfrkcb_historical(call, rule, meaning, effects, evidence):
    return HistoricalDerivation(call, rule=rule, public_meaning=meaning,
                                effects=tuple(effects), evidence=evidence)
