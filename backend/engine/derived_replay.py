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


def _partner(seat):
    return {'n': 's', 's': 'n', 'e': 'w', 'w': 'e'}[seat]


def _nfrkcb_historical(call, rule, meaning, effects, evidence):
    return HistoricalDerivation(call, rule=rule, public_meaning=meaning,
                                effects=tuple(effects), evidence=evidence)
