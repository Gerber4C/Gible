from __future__ import annotations

from typing import Any

from .auction import Auction
from .axioms import evaluate_axioms
from .cards import Hand
from .candidate_generation import agreed_trump_fallback, default_candidate, generate_candidates
from .context import BidDecision, CandidatePool
from .decision import choose_candidate, _resolve_same_call_meanings
from .dds_adapter import DDSUnavailableError
from .deal_sampler import SamplingExhausted
from .model import PartnershipProfile
from .legality import illegal_calls_in_auction
from .memory import SeatMemory
from .purpose_axiom import complete_purpose, remember_selected_purpose, resolve_purpose, terminal_pass_candidate
from .replay import active_environment_for, replay_auction
from .slam_conventions import keycard_ask_restricted
from .slam_intent import detect_slam_intent
from .simulation_decision import (decide_minor_5422, is_minor_5422_decision,
                                  decide_minor_major_74, is_minor_major_74_decision,
                                  decide_two_major_spade_slam,
                                  is_two_major_spade_slam_decision,
                                  decide_six_four_major_after_three_notrump,
                                  is_six_four_major_after_three_notrump)


def _partner_minimum(auction: Auction, owner: str) -> int:
    partner = {'n': 's', 's': 'n', 'e': 'w', 'w': 'e'}[owner]
    for index, call in enumerate(auction.calls):
        if auction.actor_at(index) == partner and call == '1N':
            return 15
    return 12


def _apply_keycard_restrictions(auction: Auction, hand: Hand,
                                candidates, trace):
    kept = []
    for candidate in candidates:
        meaning = candidate.public_meaning or {}
        if candidate.call == '4N' and 'keycard_asking' in meaning.get(
                'call_act_types', ()):
            trump = meaning.get('agreed_suit') or meaning.get('target_suit')
            if trump in 'CDHS':
                grand = detect_slam_intent(
                    hand, _partner_minimum(auction, auction.actor_to_call),
                    strain=trump).grand
                if keycard_ask_restricted(hand, trump, grand_candidate=grand):
                    trace.warn(
                        '4NT keycard ask restricted for this keycard/queen '
                        'holding; cue-bid instead')
                    continue
        kept.append(candidate)
    return tuple(kept)


def choose_bid(
    profile: PartnershipProfile,
    auction: Auction,
    hand: Hand,
    environment: dict | None = None,
    private_memory: SeatMemory | dict[str, Any] | None = None,
) -> BidDecision:
    actor_memory = SeatMemory.coerce(private_memory)
    call_specifications = list(profile.call_specifications)
    trace = replay_auction(profile, auction, hand, environment)
    for illegal_call in illegal_calls_in_auction(auction):
        trace.warn(
            f"Illegal prior call {illegal_call.call} at auction position {illegal_call.index + 1}: {illegal_call.reason}"
        )
    active_environment = active_environment_for(profile, environment, auction)
    purpose = resolve_purpose(auction, trace, actor_memory)
    actor_memory = purpose.memory
    if purpose.error:
        trace.warn('Purpose axiom: ' + purpose.error)
        trace.axioms = {'obligations': [], 'errors': [
            {'code': 'PURPOSE_UNRESOLVED', 'message': purpose.error}],
            'rejected': [], 'evidence': []}
        return BidDecision(call=None, selected_candidate=None,
                           candidate_pool=CandidatePool((), auction), trace=trace,
                           private_memory=actor_memory)
    terminal = terminal_pass_candidate(auction, trace) if purpose.candidate is None else None
    candidates = ((purpose.candidate,) if purpose.candidate is not None else
                  (terminal,) if terminal is not None else
                  generate_candidates(profile, auction, hand, trace, active_environment, actor_memory))
    diagnostics_before_resolution = len(trace.diagnostics)
    candidates = _resolve_same_call_meanings(candidates, trace)
    if any('Ambiguous meaning for call' in message
           for message in trace.diagnostics[diagnostics_before_resolution:]):
        return BidDecision(call=None, selected_candidate=None,
                           candidate_pool=CandidatePool((), auction), trace=trace,
                           private_memory=actor_memory)
    candidates = _apply_keycard_restrictions(auction, hand, candidates, trace)
    fallback = None

    if not candidates and profile.missing_call_behavior == 'block':
        trace.warn('No authored call matches this hand and auction in the current profile. '
                   'This branch is not implemented or the hand needs an unsupported alternative; '
                   'no fallback call was made.')
        return BidDecision(call=None, selected_candidate=None,
                           candidate_pool=CandidatePool((), auction), trace=trace,
                           private_memory=actor_memory)

    if not candidates:
        fallback = default_candidate(call_specifications, auction)
        if fallback.call == "P":
            fallback = agreed_trump_fallback(auction, trace) or fallback
        candidates = (fallback,)

    candidates, trace.axioms = evaluate_axioms(auction, hand, trace, candidates, profile.axioms)
    if purpose.candidate is not None:
        trace.axioms['obligations'].append({
            'kind': 'purpose', 'purpose': purpose.purpose.kind,
            'source_index': purpose.purpose.source_index,
            'required_call': purpose.candidate.call})
    if fallback:
        outcome = f'defaulting to {fallback.call}' if candidates else f'fallback {fallback.call} rejected by axioms'
        trace.warn(f"No matching Call Specification for auction: {auction.compact_sequence()}; {outcome}")
    for error in trace.axioms['errors']:
        trace.warn(f"Axiom {error['code']}: {error['message']}")
    if not candidates:
        return BidDecision(call=None, selected_candidate=None, candidate_pool=CandidatePool((),auction),
                           trace=trace, private_memory=actor_memory)

    if is_minor_5422_decision(profile.id, auction):
        try:
            simulated = decide_minor_5422(auction, hand)
        except (DDSUnavailableError, SamplingExhausted, RuntimeError, ValueError) as exc:
            trace.warn('Minor-slam simulation unavailable: ' + str(exc))
            return BidDecision(call=None, selected_candidate=None,
                               candidate_pool=CandidatePool(candidates, auction),
                               trace=trace, private_memory=actor_memory)
        selected = next((item for item in candidates if item.call == simulated['call']), None)
        if selected is None:
            trace.warn('Minor-slam simulation chose a call absent from this profile')
            return BidDecision(call=None, selected_candidate=None,
                               candidate_pool=CandidatePool(candidates, auction),
                               trace=trace, private_memory=actor_memory)
        trace.simulation_decision = simulated
        candidates = (selected,)

    if is_minor_major_74_decision(profile.id, auction, hand):
        try:
            simulated = decide_minor_major_74(profile, auction, hand)
        except (DDSUnavailableError, SamplingExhausted, RuntimeError, ValueError) as exc:
            trace.warn('Seven-four slam comparison unavailable: ' + str(exc))
            return BidDecision(call=None, selected_candidate=None,
                               candidate_pool=CandidatePool(candidates, auction),
                               trace=trace, private_memory=actor_memory)
        selected = next((item for item in candidates if item.call == simulated['call']), None)
        if selected is None:
            trace.warn('Seven-four comparison chose a call absent from this profile')
            return BidDecision(call=None, selected_candidate=None,
                               candidate_pool=CandidatePool(candidates, auction),
                               trace=trace, private_memory=actor_memory)
        trace.simulation_decision = simulated
        candidates = (selected,)

    if is_two_major_spade_slam_decision(profile.id, auction, hand):
        try:
            simulated = decide_two_major_spade_slam(profile, auction, hand)
        except (DDSUnavailableError, SamplingExhausted, RuntimeError, ValueError) as exc:
            trace.warn('Two-major slam simulation unavailable: ' + str(exc))
            return BidDecision(call=None, selected_candidate=None,
                               candidate_pool=CandidatePool(candidates, auction),
                               trace=trace, private_memory=actor_memory)
        selected = next((item for item in candidates if item.call == simulated['call']), None)
        if selected is None:
            trace.warn('Two-major slam comparison chose a call absent from this profile')
            return BidDecision(call=None, selected_candidate=None,
                               candidate_pool=CandidatePool(candidates, auction),
                               trace=trace, private_memory=actor_memory)
        trace.simulation_decision = simulated
        candidates = (selected,)

    if is_six_four_major_after_three_notrump(profile.id, auction, hand):
        try:
            simulated = decide_six_four_major_after_three_notrump(profile, auction, hand)
        except (DDSUnavailableError, SamplingExhausted, RuntimeError, ValueError) as exc:
            trace.warn('Six-four major slam simulation unavailable: ' + str(exc))
            return BidDecision(call=None, selected_candidate=None,
                               candidate_pool=CandidatePool(candidates, auction),
                               trace=trace, private_memory=actor_memory)
        selected = next((item for item in candidates if item.call == simulated['call']), None)
        if selected is None:
            trace.warn('Six-four major simulation chose a call absent from this profile')
            return BidDecision(call=None, selected_candidate=None,
                               candidate_pool=CandidatePool(candidates, auction),
                               trace=trace, private_memory=actor_memory)
        trace.simulation_decision = simulated
        candidates = (selected,)

    decision = choose_candidate(
        candidates,
        profile.all_policy_functions,
        auction,
        hand,
        trace,
        active_environment,
        actor_memory,
    )
    updated_memory = actor_memory.remember_candidate(decision.selected)
    updated_memory = complete_purpose(updated_memory, purpose.purpose)
    updated_memory = remember_selected_purpose(updated_memory, auction, hand, decision.selected)
    checked, final_report = evaluate_axioms(auction, hand, trace, (decision.selected,), profile.axioms)
    if not checked:
        trace.axioms = final_report
        for error in final_report['errors']:
            trace.warn(f"Axiom {error['code']}: {error['message']}")
        return BidDecision(call=None, selected_candidate=None, candidate_pool=CandidatePool((),auction),
                           trace=trace, private_memory=actor_memory)
    return BidDecision(
        call=decision.selected.call,
        selected_candidate=decision.selected,
        candidate_pool=CandidatePool(decision.ordered, auction),
        trace=trace,
        policy_origin=decision.policy_origin,
        context=decision.context,
        private_memory=updated_memory,
    )


