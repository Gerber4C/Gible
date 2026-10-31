"""Derived five-of-trump stop and small-slam placement after keycard answers.

The answer bid itself is artificial.  The asker's decision is derived from the
public answer category and their own keycards:

* two or more missing keycards -> stop in five of the agreed trump;
* one missing keycard with the trump queen denied -> stop there too;
* no missing keycard, or one missing with the queen known -> six of the trump.

When the answer is already five of the trump, the stop is Pass.
"""

from __future__ import annotations

from .derived_semantics import DerivationResult, derived_candidate
from .keycard_stop import (
    possible_missing_counts, placement_required, small_slam_meaning,
    stop_candidate_call, stop_meaning, stop_required,
)
from .legality import is_call_legal
from .rkcb_continuation import ordinary_rkcb_frame, partner_of_last_bidder


def derive(profile, auction, trace, evidence, allowed, hand=None):
    if hand is None or trace is None:
        return DerivationResult(evidence)
    if auction.actor_to_call != partner_of_last_bidder(auction):
        return DerivationResult(evidence)
    frame = ordinary_rkcb_frame(trace)
    if frame is not None:
        return _ordinary(auction, trace, evidence, allowed, hand, frame)
    return _voidwood(auction, trace, evidence, allowed, hand)


def _ordinary(auction, trace, evidence, allowed, hand, frame):
    if frame.status != 'answered' or frame.continuation_stage is not None:
        return DerivationResult(evidence)
    if not frame.keycard_counts:
        return DerivationResult(evidence)
    # The existing ordinary placement and grand-answer families own 5S and the
    # high answers; this family only adds the five-of-trump stop decision.
    if frame.answer_call not in ('5C', '5D', '5H'):
        return DerivationResult(evidence)
    own = hand.keycard_count(frame.trump)
    missing = possible_missing_counts(own, frame.keycard_counts, 5)
    if len(missing) != 1:
        return DerivationResult(evidence)
    missing_count = missing.pop()
    if stop_required(missing_count, frame.trump_queen):
        call = stop_candidate_call(
            auction, frame.trump, _last_non_pass_call(auction))
        if call is None or call not in allowed or not is_call_legal(auction, call):
            return DerivationResult(evidence)
        effect = _ordinary_completed(frame)
        return DerivationResult(evidence, (derived_candidate(
            call, 'derive_keycard_five_of_trump_stop',
            stop_meaning(frame.trump), evidence,
            effects=(effect,), score=10),))
    if placement_required(missing_count, frame.trump_queen):
        call = '6' + frame.trump
        if call not in allowed or not is_call_legal(auction, call):
            return DerivationResult(evidence)
        effect = _ordinary_completed(frame)
        return DerivationResult(evidence, (derived_candidate(
            call, 'derive_keycard_small_slam_placement',
            small_slam_meaning(frame.trump), evidence,
            effects=(effect,), score=10),))
    return DerivationResult(evidence)


def _voidwood(auction, trace, evidence, allowed, hand):
    answer = _latest_voidwood_answer(trace)
    if answer is None:
        return DerivationResult(evidence)
    ask = answer.attribute('ask')
    asker = _voidwood_asker(trace, ask)
    if asker is None or auction.actor_to_call != asker:
        return DerivationResult(evidence)
    answer_call = answer.attribute('answer_call')
    if answer_call is not None and _last_non_pass_call(auction) != answer_call:
        return DerivationResult(evidence)
    trump = answer.attribute('trump')
    void = answer.attribute('void')
    counts = answer.attribute('keycard_counts') or ()
    if trump not in 'CDHS' or void not in 'CDHS' or not counts:
        return DerivationResult(evidence)
    own = hand.keycard_count(trump, excluded_suit=void)
    missing = possible_missing_counts(own, counts, 4)
    if len(missing) != 1:
        return DerivationResult(evidence)
    missing_count = missing.pop()
    queen = answer.attribute('effective_trump_queen')
    if stop_required(missing_count, queen):
        call = stop_candidate_call(
            auction, trump, _last_non_pass_call(auction))
        if call is None or call not in allowed or not is_call_legal(auction, call):
            return DerivationResult(evidence)
        effects = _voidwood_completed(answer, trump, void)
        return DerivationResult(evidence, (derived_candidate(
            call, 'derive_voidwood_five_of_trump_stop',
            stop_meaning(trump), evidence,
            effects=effects, score=10),))
    if placement_required(missing_count, queen):
        call = '6' + trump
        if call not in allowed or not is_call_legal(auction, call):
            return DerivationResult(evidence)
        effects = _voidwood_completed(answer, trump, void)
        return DerivationResult(evidence, (derived_candidate(
            call, 'derive_voidwood_small_slam_placement',
            small_slam_meaning(trump), evidence,
            effects=effects, score=10),))
    return DerivationResult(evidence)


def _ordinary_completed(frame):
    return {
        'key': 'keycard_context', 'method': 'rkcb_1430',
        'trump_suit': frame.trump, 'status': 'completed',
        'answer_call': frame.answer_call,
        'answer_category': frame.answer_category,
        'keycard_counts': list(frame.keycard_counts),
    }


def _voidwood_completed(answer, trump, void):
    return (
        {'key': 'keycard_context', 'method': 'voidwood',
         'trump_suit': trump, 'excluded_suit': void,
         'ask_call': answer.attribute('ask'), 'status': 'completed'},
        {'key': 'voidwood', 'method': 'voidwood', 'trump': trump,
         'void': void, 'ask': answer.attribute('ask'),
         'status': 'completed'},
    )


def _latest_voidwood_answer(trace):
    for record in reversed(trace.current_state_records):
        if record.key == 'voidwood_answer':
            return record
    return None


def _voidwood_asker(trace, ask):
    for entry in reversed(trace.applied_meanings):
        meaning = entry.get('public_meaning', {}) or {}
        if (entry.get('call') == ask
                and meaning.get('action_type') == 'voidwood_ask'):
            return entry.get('seat')
    return None


def _last_non_pass_call(auction):
    for call in reversed(auction.calls):
        if call not in ('P', 'X', 'R'):
            return call
    return None
