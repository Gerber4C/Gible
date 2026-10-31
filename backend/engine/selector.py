from __future__ import annotations

from dataclasses import replace
from types import SimpleNamespace

from typing import Any

from .auction import Auction
from .axioms import evaluate_axioms
from .cards import Hand
from .candidate_generation import agreed_trump_fallback, default_candidate, generate_candidates
from .context import BidDecision, CandidatePool
from .decision import choose_candidate, _ordered_with_selected_first, _resolve_same_call_meanings
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
    lowest_counterinvite_king, ordinary_response, ordinary_rkcb_frame,
    partner_of_last_bidder,
)
from .context import CallCandidate
from .nfrkcb_policy import answer_effect, decide_offer
from .slam_conventions import keycard_ask_restricted
from .slam_intent import detect_slam_intent
from .cue_slam_policy import (cue_gate, cue_three_way, decide_from_hands,
                              partner_promised_kr, sample_process_hands,
                              signoff_override)
from .five_major_inquiry_policy import (
    decide_five_major_inquiry, inquiry_decision_kind,
    quantitative_ace_decision)
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
    purpose_controls = purpose.purpose is not None
    if purpose.candidate is not None:
        candidates = (purpose.filtered_candidates
                      if purpose.filtered_candidates is not None
                      else (purpose.candidate,))
    elif terminal is not None:
        candidates = (terminal,)
    elif purpose_controls or not profile.derived_semantics:
        candidates = generated
    else:
        from .derived_evidence import collect_evidence
        from .derived_semantics import derive_candidates, reserved_calls
        evidence = collect_evidence(profile, auction, trace)
        reserved = reserved_calls(profile, auction, trace, active_environment)
        derived = derive_candidates(profile, auction, trace, evidence, reserved, hand)
        for conflict in derived.conflicts:
            trace.warn(f"Derived semantics {conflict['code']}: "
                       + conflict.get('message', ''))
        trace.derivation = {
            'candidates': [
                {'call': candidate.call,
                 'rule': candidate.metadata.get('derived_rule'),
                 'confidence': candidate.metadata.get('derived_confidence'),
                 'evidence': candidate.metadata.get('derived_evidence')}
                for candidate in derived.candidates],
            'conflicts': list(derived.conflicts),
        }
        authored_calls = {candidate.call for candidate in generated}
        derived_candidates = tuple(
            replace(candidate, score=candidate.score - 1000)
            if generated else candidate
            for candidate in derived.candidates
            if candidate.call not in authored_calls)
        candidates = tuple(generated) + derived_candidates
    pool_candidates_full = tuple(candidates)
    nfrkcb = _nfrkcb_response(profile, auction, trace, hand, candidates)
    if nfrkcb == 'error':
        trace.warn('NFRKCB response needs sampled evidence')
        return BidDecision(call=None, selected_candidate=None,
                           candidate_pool=CandidatePool((), auction), trace=trace,
                           private_memory=actor_memory)
    if nfrkcb is not None:
        candidates = (nfrkcb,)
    last_meaning = next(
        (entry for entry in reversed(trace.applied_meanings)
         if entry.get('call') not in ('P', 'X', 'R')), None)
    if (last_meaning is not None
            and (last_meaning.get('public_meaning') or {}).get('action_type')
            == 'minor_slam_stopper_notrump'):
        keycard_continuation = next(
            (candidate for candidate in candidates if candidate.call == '4NT'),
            None)
        if keycard_continuation is not None:
            candidates = (keycard_continuation,)
    keycard_stop_rules = {
        'derive_keycard_five_of_trump_stop',
        'derive_keycard_small_slam_placement',
        'derive_voidwood_five_of_trump_stop',
        'derive_voidwood_small_slam_placement',
    }
    keycard_stop = next(
        (candidate for candidate in candidates
         if candidate.metadata.get('derived_rule') in keycard_stop_rules),
        None)
    if keycard_stop is not None:
        candidates = (keycard_stop,)
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

    new_quantitative_5c = any(
        (candidate.public_meaning or {}).get('action_type')
        == 'quantitative_5c_feature_ask' for candidate in candidates)
    if is_minor_5422_decision(profile.id, auction) and not new_quantitative_5c:
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

    ace_decision = quantitative_ace_decision(
        profile, auction, hand, trace=trace)
    if ace_decision is not None:
        keep = ({'5N', '5S', 'P'} if ace_decision.branch == 'stop'
                else {'6C', '6D', '6H', '6S'})
        filtered = tuple(c for c in candidates if c.call in keep)
        if not filtered:
            trace.warn('Quantitative ace decision produced no legal call: '
                       + ace_decision.reason)
            return BidDecision(call=None, selected_candidate=None,
                               candidate_pool=CandidatePool((), auction),
                               trace=trace, private_memory=actor_memory)
        candidates = filtered

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
    pool_candidates = _ordered_with_selected_first(
        decision.selected, pool_candidates_full)
    return BidDecision(
        call=decision.selected.call,
        selected_candidate=decision.selected,
        candidate_pool=CandidatePool(pool_candidates, auction),
        trace=trace,
        policy_origin=decision.policy_origin,
        context=decision.context,
        private_memory=updated_memory,
    )




def _nfrkcb_response(profile, auction, trace, hand, candidates):
    offer = None
    for record in reversed(trace.current_state_records):
        if (record.key == 'nfrkcb'
                and record.attribute('method') == 'nfrkcb_offer'):
            offer = record
            break
    if offer is None:
        return None
    offerer = offer.attribute('offerer')
    partner = {'n': 's', 's': 'n', 'e': 'w', 'w': 'e'}[offerer]
    if auction.actor_to_call != partner:
        return None
    trump = offer.attribute('trump_suit')
    if trump not in 'CDHS':
        return None
    decision = decide_offer(profile, auction, trace, hand, trump)
    if decision.unavailable or decision.call is None:
        return 'error'
    origin = {'namespace': 'derived', 'object_type': 'rule',
              'object_id': 'nfrkcb_response',
              'qualified_id': 'derived/rule:nfrkcb_response'}
    if decision.call == 'P':
        return CallCandidate(
            'P', origin,
            {'nature_labels': ['natural'],
             'call_act_types': ['signoff', 'final_placement'],
             'action_type': 'nfrkcb_accept', 'target_suit': 'N',
             'agreed_suit': trump},
            'derived_semantics', 'nfrkcb_response', 2, (),
            capabilities=('place_contract',),
            metadata={'derived_rule': 'nfrkcb_pass',
                      'derived_effects': [answer_effect(trump, offerer, 'P')]})
    response = ordinary_response(hand, trump)
    return CallCandidate(
        response.call, origin,
        {'nature_labels': ['artificial'],
         'call_act_types': ['descriptive', 'keycard_answer'],
         'action_type': 'nfrkcb_answer', 'target_suit': trump,
         'agreed_suit': trump,
         'keycard_counts': list(response.keycard_counts),
         'trump_queen': response.trump_queen},
        'derived_semantics', 'nfrkcb_response', 2, (),
        capabilities=('keycard_answer',),
        metadata={'derived_rule': 'nfrkcb_answer',
                  'derived_effects': [answer_effect(trump, offerer,
                                                    response.call)]})
