from __future__ import annotations

from dataclasses import replace
from types import SimpleNamespace

from typing import Any

from .auction import Auction
from .axioms import evaluate_axioms
from .cards import Hand
from .candidate_generation import agreed_trump_fallback, default_candidate, generate_candidates
from .context import BidDecision, CandidatePool
from .decision import choose_candidate, _resolve_same_call_meanings
from .dds_adapter import DDSUnavailableError
from .deal_sampler import SamplingExhausted
from .hand_quality import assess_quality
from .honor_quality import assess_honor_texture
from .model import PartnershipProfile
from .legality import illegal_calls_in_auction
from .memory import SeatMemory
from .purpose_axiom import complete_purpose, remember_selected_purpose, resolve_purpose, terminal_pass_candidate
from .replay import active_environment_for, replay_auction
from .rkcb_continuation import (
    lowest_counterinvite_king, ordinary_rkcb_frame, partner_of_last_bidder,
)
from .slam_conventions import keycard_ask_restricted
from .slam_intent import detect_slam_intent
from .cue_slam_policy import (cue_gate, cue_three_way, decide_from_hands,
                              partner_promised_kr, sample_process_hands,
                              signoff_override)
from .five_major_inquiry_policy import (
    decide_five_major_inquiry, inquiry_decision_kind)
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
    generated = generate_candidates(profile, auction, hand, trace,
                                    active_environment, actor_memory)
    generated = _apply_keycard_restrictions(auction, hand, generated, trace)
    purpose = resolve_purpose(auction, trace, actor_memory, hand, generated,
                              profile)
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
    if purpose.candidate is not None:
        candidates = (purpose.filtered_candidates
                      if purpose.filtered_candidates is not None
                      else (purpose.candidate,))
    elif terminal is not None:
        candidates = (terminal,)
    else:
        candidates = generated
    frame = ordinary_rkcb_frame(trace)
    if (frame is not None
            and frame.continuation_stage == 'grand_invitation'
            and partner_of_last_bidder(auction) == auction.actor_to_call):
        counter = lowest_counterinvite_king(hand, frame, auction)
        selected = next((candidate for candidate in candidates
                         if candidate.call == counter), None) if counter else None
        if selected is None:
            selected = next((candidate for candidate in candidates
                             if candidate.call == f'6{frame.trump}'), None)
        if selected is None:
            selected = next((candidate for candidate in candidates
                             if candidate.call == 'P'), None)
        if selected is not None:
            candidates = (selected,)
    diagnostics_before_resolution = len(trace.diagnostics)
    candidates = _resolve_same_call_meanings(candidates, trace)
    if any('Ambiguous meaning for call' in message
           for message in trace.diagnostics[diagnostics_before_resolution:]):
        return BidDecision(call=None, selected_candidate=None,
                           candidate_pool=CandidatePool((), auction), trace=trace,
                           private_memory=actor_memory)
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

    inquiry_kind = inquiry_decision_kind(profile.id, auction)
    if inquiry_kind is not None:
        inquiry = decide_five_major_inquiry(
            profile, auction, hand, trace=trace)
        trace.simulation_decision = {
            'kind': inquiry_kind, 'call': inquiry.call,
            'source': inquiry.source, 'reason': inquiry.reason}
        if inquiry.call is None:
            trace.warn('Five-major inquiry fallback is inconclusive: '
                       + inquiry.reason)
            return BidDecision(call=None, selected_candidate=None,
                               candidate_pool=CandidatePool(candidates, auction),
                               trace=trace, private_memory=actor_memory)
        from .calls import normalize_call
        target_call = normalize_call(inquiry.call)
        selected = next((item for item in candidates
                         if item.call == target_call), None)
        if selected is None:
            trace.warn('Five-major inquiry selected a call absent from this '
                       'profile: ' + inquiry.call)
            return BidDecision(call=None, selected_candidate=None,
                               candidate_pool=CandidatePool(candidates, auction),
                               trace=trace, private_memory=actor_memory)
        candidates = (selected,)

    cue_context = cue_three_way(auction, trace)
    if cue_context is not None:
        trump, partner = cue_context
        keycard = next((c for c in candidates if c.call == '4N'), None)
        game = next((c for c in candidates
                     if c.call != '4N'
                     and {'signoff', 'final_placement'} & set(
                         (c.public_meaning or {}).get('call_act_types', ()))),
                    None)
        cue_candidates = [c for c in candidates
                          if c.call != '4N'
                          and {'control_showing', 'slam_try'} & set(
                              (c.public_meaning or {}).get('call_act_types', ()))]
        if keycard is not None and game is not None and cue_candidates:
            side = 'ns' if auction.actor_to_call in 'ns' else 'ew'
            vulnerable = auction.vulnerability in ('both', side)
            try:
                deals = sample_process_hands(
                    profile, auction, trace, hand, partner)
            except (SamplingExhausted, RuntimeError, ValueError) as exc:
                trace.warn('Cue-continuation sampling unavailable: ' + str(exc))
                deals = ()
            deterministic = ((keycard,) if keycard is not None and hand.hcp >= 16
                             else (game,))
            if deals:
                try:
                    simulated = decide_from_hands(
                        hand, trump, tuple(deal[partner] for deal in deals),
                        game_call=game.call,
                        cue_calls=[c.call for c in cue_candidates],
                        deals=deals,
                        promised_kr=partner_promised_kr(trace, partner))
                except (DDSUnavailableError, RuntimeError, ValueError) as exc:
                    trace.warn('Cue-continuation simulation unavailable: ' + str(exc))
                    # Deterministic first: without samples or DDS, use the
                    # authored keycard gate, otherwise the authored game.
                    # A cue above game still needs the +EV roll-out gate.
                    candidates = deterministic
                else:
                    if (simulated.call not in ('4N', game.call)
                            and trump in 'HS'):
                        # Owner rule: a cue above 4M must show a positive
                        # expected gain, measured by rolling the authored
                        # auction forward from prefix + cue.
                        gate = cue_gate(
                            profile, auction, cue_call=simulated.call,
                            trump=trump, game_call=game.call, partner=partner,
                            hand=hand,
                            partner_hands=tuple(deal[partner] for deal in deals),
                            environment=active_environment, deals=deals,
                            vulnerable=vulnerable)
                        if not gate['plus_ev']:
                            trace.warn(
                                'Cue above game is not +EV: '
                                f"roll-out {gate['rollout_ev']:.0f} vs stop "
                                f"{gate['stop_ev']:.0f}, blocked "
                                f"{gate['blocked']}, finals "
                                f"{gate['final_contracts']}")
                            simulated = replace(
                                simulated,
                                call=game.call,
                                reason='cue above game is not +EV: '
                                       + simulated.reason)
                    selected = next((c for c in candidates
                                     if c.call == simulated.call), None)
                    if selected is not None:
                        trace.simulation_decision = {
                            'call': simulated.call,
                            'reason': simulated.reason,
                            'extra_kr_threshold': simulated.extra_kr_threshold}
                        candidates = (selected,)
            else:
                candidates = deterministic

    override = signoff_override(trace, auction.actor_to_call)
    if override is not None:
        trump, signoff_bidder, signoff_call = override
        keycard = next((c for c in candidates if c.call == '4N'), None)
        pass_candidate = next((c for c in candidates if c.call == 'P'), None)
        if keycard is not None and pass_candidate is not None:
            maximum = next(
                (item.definition for item in profile.named_evaluators
                 if item.id == 'absolute_maximum_' + trump), None)

            def _not_maximum(hand):
                if maximum is None:
                    return True
                context = SimpleNamespace(
                    hand=hand, hand_quality=assess_quality(hand),
                    honor_texture=assess_honor_texture(hand))
                return maximum(context) is not True

            try:
                deals = sample_process_hands(
                    profile, auction, trace, hand, signoff_bidder,
                    extra_filter=_not_maximum)
            except (SamplingExhausted, RuntimeError, ValueError) as exc:
                trace.warn('Signoff-override sampling unavailable: ' + str(exc))
                deals = ()
            if deals:
                try:
                    simulated = decide_from_hands(
                        hand, trump,
                        tuple(deal[signoff_bidder] for deal in deals),
                        game_call=signoff_call, cue_calls=(), deals=deals,
                        promised_kr=partner_promised_kr(trace, signoff_bidder))
                except (DDSUnavailableError, RuntimeError, ValueError) as exc:
                    trace.warn('Signoff-override simulation unavailable: ' + str(exc))
                    # Deterministic fallback: a hand far above the range that
                    # signed off may still ask keycards; otherwise respect the
                    # signoff. The simulation refines this when DDS is present.
                    candidates = ((keycard,) if hand.hcp >= 18
                                  else (pass_candidate,))
                else:
                    selected = keycard if simulated.call == '4N' else pass_candidate
                    trace.simulation_decision = {
                        'call': selected.call,
                        'reason': 'signoff override: ' + simulated.reason,
                        'extra_kr_threshold': simulated.extra_kr_threshold}
                    candidates = (selected,)
            else:
                candidates = ((keycard,) if hand.hcp >= 18 else (pass_candidate,))

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
    if purpose.completes:
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


