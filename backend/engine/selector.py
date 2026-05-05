from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .auction import Auction
from .cards import Hand
from .calls import normalize_call
from .convention import CallSelectionPolicy, CallSpecification, ConventionSet
from .evaluator import evaluate, evaluate_expression, evaluate_selection
from .legality import illegal_calls_in_auction, is_call_legal
from .matcher import historical_pattern_for, matches_context, matches_pattern
from .trace import AuctionStateVariable, PlanState, ProtocolFrameState, SemanticFact, SemanticTrace


@dataclass(frozen=True)
class Candidate:
    call: str
    origin: dict[str, Any]
    public_meaning: dict[str, Any]
    algorithm: str
    call_specification_id: str
    score: int
    criteria_results: tuple[dict[str, Any], ...]
    plan_origin: dict[str, Any] | None = None


@dataclass(frozen=True)
class Selection:
    call: str | None
    selected: Candidate | None
    candidates: tuple[Candidate, ...]
    trace: SemanticTrace
    selection_policy: dict[str, Any] | None = None


def choose_bid(convention_set: ConventionSet, auction: Auction, hand: Hand, environment: dict | None = None) -> Selection:
    call_specifications = list(convention_set.call_specifications)
    trace = replay_auction(convention_set, auction, hand, environment)
    for illegal_call in illegal_calls_in_auction(auction):
        trace.warn(
            f"Illegal prior call {illegal_call.call} at auction position {illegal_call.index + 1}: {illegal_call.reason}"
        )
    candidates = []
    active_environment = _active_environment(convention_set, environment, auction)
    for call_specification in call_specifications:
        if call_specification.default_policy or not call_specification.has_selection:
            continue
        if not matches_context(call_specification.context, auction):
            continue
        if not evaluate(call_specification.requires, hand, trace, active_environment):
            continue
        if not evaluate(call_specification.applicability, hand, trace, active_environment):
            continue
        if not evaluate(call_specification.selection.get("applicability", {}), hand, trace, active_environment):
            continue
        candidate = _candidate(call_specification, hand, trace, active_environment)
        if candidate is not None:
            if not is_call_legal(auction, candidate.call):
                trace.warn(
                    "Illegal candidate "
                    f"{candidate.call} from {candidate.origin['qualified_id']} "
                    f"for auction {auction.compact_sequence()}"
                )
                continue
            candidates.append(candidate)
    for candidate in _plan_candidates(convention_set, auction, hand, trace, active_environment, tuple(candidates)):
        if not is_call_legal(auction, candidate.call):
            trace.warn(
                "Illegal plan candidate "
                f"{candidate.call} from {candidate.origin['qualified_id']} "
                f"for auction {auction.compact_sequence()}"
            )
            continue
        candidates.append(candidate)
    candidates = tuple(candidates)

    if not candidates:
        fallback = _default_candidate(call_specifications, auction)
        trace.warn(f"No matching Call Specification for auction: {auction.compact_sequence()}; defaulting to {fallback.call}")
        return Selection(call=fallback.call, selected=fallback, candidates=(fallback,), trace=trace, selection_policy=None)

    best, ordered, policy_origin = _select_candidate(
        candidates,
        convention_set.call_selection_policies,
        auction,
        hand,
        trace,
        active_environment,
    )
    return Selection(call=best.call, selected=best, candidates=ordered, trace=trace, selection_policy=policy_origin)


def replay_auction(
    convention_set: ConventionSet,
    auction: Auction,
    hand: Hand | None = None,
    environment: dict | None = None,
) -> SemanticTrace:
    trace = SemanticTrace()
    call_specifications = list(convention_set.call_specifications)
    for index, call in enumerate(auction.calls):
        if call == "P":
            continue
        pattern = historical_pattern_for(auction.calls, index)
        prior_auction = Auction(calls=auction.calls[:index], dealer=auction.dealer, vulnerability=auction.vulnerability)
        active_environment = _active_environment(convention_set, environment, prior_auction)
        matches = [
            item
            for item in call_specifications
            if item.has_meaning
            and matches_context(item.context, prior_auction)
            and item.call == call
            and evaluate(item.requires, hand or Hand.from_dict({}), trace, active_environment)
        ]
        if hand is not None:
            matches = [item for item in matches if evaluate(item.applicability, hand, trace, active_environment)]
        if not matches:
            trace.warn(f"Undefined prior call {call} at auction position {index + 1}")
            continue
        if len(matches) > 1:
            trace.warn(f"Ambiguous prior call {call} at auction position {index + 1}")
        call_specification = matches[0]
        origin = call_specification.origin_dict()
        for effect in call_specification.effects:
            _apply_effect(trace, effect, origin, hand, active_environment)
        trace.add_applied_meaning(
            {
                "call": call,
                "auction_pattern": pattern,
                "origin": origin,
                "public_meaning": call_specification.meaning,
            }
        )
        _advance_protocol_frames(trace, call_specification)
        _advance_bidding_plans(convention_set, trace, call, call_specification)
        _recover_protocol_frames(convention_set, trace, call, prior_auction)
        _recover_bidding_plans(convention_set, trace, call, prior_auction)
    return trace


def _active_environment(convention_set: ConventionSet, environment: dict | None, auction: Auction | None = None) -> dict:
    active_environment = dict(environment or {})
    if auction is not None:
        active_environment.setdefault("seat", auction.actor_to_call)
        active_environment.setdefault("dealer", auction.dealer)
        active_environment.setdefault("vulnerability", auction.vulnerability)
        active_environment.setdefault("seat_position", _opening_seat_position(auction))
        active_environment.setdefault(
            "vulnerability_relation",
            _vulnerability_relation(active_environment["seat"], auction.vulnerability),
        )
    active_environment["_named_evaluators"] = {
        evaluator.id: evaluator.definition for evaluator in convention_set.named_evaluators if evaluator.evaluator_type == "expression"
    }
    return active_environment


def _vulnerability_relation(seat: str, vulnerability: str) -> str:
    seat = str(seat).lower()
    vulnerability = str(vulnerability).lower()
    if vulnerability == "none":
        return "none"
    if vulnerability == "both":
        return "both"
    our_side = "ns" if seat in ("n", "s") else "ew"
    if vulnerability == our_side:
        return "unfavorable"
    return "favorable"


def _opening_seat_position(auction: Auction) -> int | None:
    if len(auction.calls) > 3:
        return None
    if any(call != "P" for call in auction.calls):
        return None
    return len(auction.calls) + 1


def _candidate(
    call_specification: CallSpecification,
    hand: Hand,
    trace: SemanticTrace,
    environment: dict | None,
) -> Candidate | None:
    evaluation = evaluate_selection(call_specification.selection, hand, trace, environment)
    if not evaluation["eligible"]:
        return None
    return Candidate(
        call=call_specification.call,
        origin=call_specification.origin_dict(),
        public_meaning=call_specification.meaning,
        algorithm=evaluation["algorithm"],
        call_specification_id=call_specification.id,
        score=evaluation["score"],
        criteria_results=tuple(evaluation["criteria_results"]),
    )


def _plan_candidates(
    convention_set: ConventionSet,
    auction: Auction,
    hand: Hand,
    trace: SemanticTrace,
    environment: dict[str, Any],
    call_specification_candidates: tuple[Candidate, ...],
) -> tuple[Candidate, ...]:
    candidates = []
    candidates.extend(
        _entry_plan_candidates(convention_set, auction, hand, trace, environment, call_specification_candidates)
    )
    for state in trace.plan_states:
        if state.status != "active":
            continue
        plan = _plan_for_state(convention_set, state)
        if plan is None:
            trace.warn(f"Active Bidding Plan state {state.plan_id} no longer has a loaded plan")
            continue
        if not evaluate(plan.preconditions, hand, trace, environment):
            continue
        node = plan.workflow.get("nodes", {}).get(state.current_node, {})
        if node.get("kind") != "make_call":
            continue
        if node.get("requires") and not evaluate(node["requires"], hand, trace, environment):
            continue
        call = normalize_call(node["call"])
        implementation = _matching_candidate_for_call(call_specification_candidates, call)
        if node.get("requires_call_specification", False) and implementation is None:
            trace.warn(f"Bidding Plan {plan.origin_dict()['qualified_id']} requires a Call Specification for {call}")
            continue
        score = int(node.get("score", 100))
        candidates.append(
            Candidate(
                call=call,
                origin=implementation.origin if implementation else plan.origin_dict(),
                public_meaning=node.get(
                    "meaning",
                    implementation.public_meaning if implementation else {
                        "nature_labels": ["plan_continuation"],
                        "call_act_types": ["final_placement"],
                        "action_type": "plan_make_call",
                        "alertable": False,
                    },
                ),
                algorithm="bidding_plan",
                call_specification_id=f"{plan.id}:{state.current_node}",
                score=score,
                criteria_results=tuple(
                    [
                    {
                        "criterion_id": "plan_preconditions",
                        "evaluator": "condition",
                        "passed": True,
                        "required": True,
                        "value": plan.preconditions,
                        "contribution": score,
                    },
                    ]
                    + (
                        [
                            {
                                "criterion_id": "implemented_by_call_specification",
                                "evaluator": "call_specification_lookup",
                                "passed": True,
                                "required": True,
                                "value": implementation.origin["qualified_id"],
                                "contribution": 0,
                            }
                        ]
                        if implementation
                        else []
                    )
                ),
                plan_origin=plan.origin_dict(),
            )
        )
    return tuple(candidates)


def _entry_plan_candidates(
    convention_set: ConventionSet,
    auction: Auction,
    hand: Hand,
    trace: SemanticTrace,
    environment: dict[str, Any],
    call_specification_candidates: tuple[Candidate, ...],
) -> list[Candidate]:
    candidates = []
    for plan in convention_set.bidding_plans:
        if not plan.entry_candidate:
            continue
        if _plan_state_exists(trace, plan):
            continue
        if not matches_context(plan.context, auction):
            continue
        if not evaluate(plan.preconditions, hand, trace, environment):
            continue
        implementation = _matching_candidate_for_call(call_specification_candidates, plan.entry_call)
        if implementation is None:
            trace.warn(f"Bidding Plan {plan.origin_dict()['qualified_id']} cannot enter because {plan.entry_call} has no eligible Call Specification")
            continue
        selection_result = _evaluate_plan_selection(plan, hand, trace, environment)
        if not selection_result["eligible"]:
            continue
        candidates.append(
            Candidate(
                call=plan.entry_call,
                origin=implementation.origin,
                public_meaning=implementation.public_meaning,
                algorithm="bidding_plan_entry",
                call_specification_id=f"{plan.id}:entry",
                score=selection_result["score"],
                criteria_results=tuple(selection_result["criteria_results"]),
                plan_origin=plan.origin_dict(),
            )
        )
    return candidates


def _evaluate_plan_selection(
    plan,
    hand: Hand,
    trace: SemanticTrace,
    environment: dict[str, Any],
) -> dict[str, Any]:
    if plan.selection:
        return evaluate_selection(plan.selection, hand, trace, environment)
    return {
        "eligible": True,
        "score": plan.entry_score,
        "criteria_results": [
            {
                "criterion_id": "plan_preconditions",
                "evaluator": "condition",
                "passed": True,
                "required": True,
                "value": plan.preconditions,
                "contribution": plan.entry_score,
            }
        ],
    }


def _matching_candidate_for_call(candidates: tuple[Candidate, ...], call: str) -> Candidate | None:
    normalized_call = normalize_call(call)
    matching = [candidate for candidate in candidates if candidate.call == normalized_call and candidate.plan_origin is None]
    if not matching:
        return None
    return sorted(matching, key=lambda candidate: candidate.score, reverse=True)[0]


def _plan_state_exists(trace: SemanticTrace, plan) -> bool:
    qualified_id = plan.origin_dict()["qualified_id"]
    return any(state.origin.get("qualified_id") == qualified_id and state.status == "active" for state in trace.plan_states)


def _select_candidate(
    candidates: tuple[Candidate, ...],
    policies: tuple[CallSelectionPolicy, ...],
    auction: Auction,
    hand: Hand,
    trace: SemanticTrace,
    environment: dict[str, Any],
) -> tuple[Candidate, tuple[Candidate, ...], dict[str, Any] | None]:
    policy = _matching_policy(policies, auction)
    if policy is not None and policy.algorithm not in ("highest_score", "weighted_score_highest", "ordered_condition"):
        trace.warn(f"Unsupported Call Selection Policy algorithm {policy.algorithm}; falling back to highest_score")

    candidates = _resolve_same_call_meanings(candidates, policy, trace)
    if policy is not None and policy.algorithm == "ordered_condition":
        selected = _select_by_ordered_condition(candidates, policy, hand, trace, environment)
        if selected is not None:
            return selected, _ordered_with_selected_first(selected, candidates), policy.origin_dict()

    ordered = tuple(sorted(candidates, key=lambda candidate: candidate.score, reverse=True))
    if len(ordered) > 1 and ordered[0].score == ordered[1].score:
        trace.warn(f"Ambiguous top score for {ordered[0].call} and {ordered[1].call}")

    if policy is None:
        return ordered[0], ordered, None

    return ordered[0], ordered, policy.origin_dict()


def _select_by_ordered_condition(
    candidates: tuple[Candidate, ...],
    policy: CallSelectionPolicy,
    hand: Hand,
    trace: SemanticTrace,
    environment: dict[str, Any],
) -> Candidate | None:
    for choice in policy.choices:
        condition = choice.get("when", {})
        if condition and not evaluate(condition, hand, trace, environment):
            continue
        choose_call = choice.get("choose_call")
        if choose_call is None:
            trace.warn(f"Call Selection Policy {policy.qualified_id} has a choice without choose_call")
            continue
        normalized_call = normalize_call(choose_call)
        matching = [candidate for candidate in candidates if candidate.call == normalized_call]
        if matching:
            return sorted(matching, key=lambda candidate: candidate.score, reverse=True)[0]
        trace.warn(
            f"Call Selection Policy {policy.qualified_id} chose {normalized_call}, "
            "but no eligible candidate had that call"
        )
    if policy.fallback not in ("highest_score", "weighted_score_highest"):
        trace.warn(f"Unsupported Call Selection Policy fallback {policy.fallback}; falling back to highest_score")
    return None


def _ordered_with_selected_first(selected: Candidate, candidates: tuple[Candidate, ...]) -> tuple[Candidate, ...]:
    rest = [candidate for candidate in sorted(candidates, key=lambda item: item.score, reverse=True) if candidate is not selected]
    return (selected, *rest)


def _resolve_same_call_meanings(
    candidates: tuple[Candidate, ...],
    policy: CallSelectionPolicy | None,
    trace: SemanticTrace,
) -> tuple[Candidate, ...]:
    grouped: dict[str, list[Candidate]] = {}
    for candidate in candidates:
        grouped.setdefault(candidate.call, []).append(candidate)

    resolved = []
    for call, group in grouped.items():
        if len(group) == 1:
            resolved.extend(group)
            continue
        if _same_final_pass_action(group):
            resolved.append(sorted(group, key=lambda candidate: candidate.score, reverse=True)[0])
            continue
        plan_selected = _plan_candidate_for_implemented_call(group)
        if plan_selected is not None:
            resolved.append(plan_selected)
            continue
        ordered_group = sorted(group, key=lambda candidate: candidate.score, reverse=True)
        resolution = policy.same_call_resolution if policy is not None else "diagnose"
        if resolution in ("highest_score", "weighted_score_highest"):
            if len(ordered_group) > 1 and ordered_group[0].score == ordered_group[1].score:
                trace.warn(f"Ambiguous meaning for call {call}: equal scores under same-call resolution policy")
            resolved.append(ordered_group[0])
            continue

        origins = ", ".join(candidate.origin["qualified_id"] for candidate in ordered_group)
        trace.warn(f"Ambiguous meaning for call {call}: {origins}")
        resolved.extend(ordered_group)
    return tuple(resolved)


def _same_final_pass_action(group: list[Candidate]) -> bool:
    return all(
        candidate.call == "P" and candidate.public_meaning.get("action_type") == "pass_final_contract"
        for candidate in group
    )


def _plan_candidate_for_implemented_call(group: list[Candidate]) -> Candidate | None:
    plan_candidates = [candidate for candidate in group if candidate.plan_origin is not None]
    non_plan_candidates = [candidate for candidate in group if candidate.plan_origin is None]
    if not plan_candidates or not non_plan_candidates:
        return None
    implemented = []
    for plan_candidate in plan_candidates:
        if any(
            plan_candidate.origin == candidate.origin and plan_candidate.public_meaning == candidate.public_meaning
            for candidate in non_plan_candidates
        ):
            implemented.append(plan_candidate)
    if not implemented:
        return None
    return sorted(implemented, key=lambda candidate: candidate.score, reverse=True)[0]


def _matching_policy(policies: tuple[CallSelectionPolicy, ...], auction: Auction) -> CallSelectionPolicy | None:
    for policy in policies:
        context = policy.scope.get("context")
        if context is None or matches_context(context, auction):
            return policy
    return None


def _recover_protocol_frames(convention_set: ConventionSet, trace: SemanticTrace, call: str, prior_auction: Auction) -> None:
    for frame in convention_set.protocol_frames:
        if frame.source_call != call:
            continue
        if not matches_context(frame.context, prior_auction):
            continue
        trace.add_protocol_frame(
            ProtocolFrameState(
                frame_id=frame.id,
                frame_type=frame.frame_type,
                status="active",
                variables=frame.variables,
                origin=frame.origin_dict(),
                current_stage=frame.stages[0] if frame.stages else None,
            )
        )


def _advance_protocol_frames(trace: SemanticTrace, call_specification: CallSpecification) -> None:
    if not trace.protocol_frames:
        return

    action_type = call_specification.meaning.get("action_type")
    call_act_types = set(call_specification.call_act_types) | set(call_specification.meaning.get("call_act_types", []))
    updated = []
    for frame in trace.protocol_frames:
        if frame.status != "active":
            updated.append(frame)
            continue

        if _frame_should_close(frame, action_type, call_act_types):
            updated.append(
                ProtocolFrameState(
                    frame_id=frame.frame_id,
                    frame_type=frame.frame_type,
                    status="closed",
                    variables=frame.variables,
                    origin=frame.origin,
                    current_stage=frame.current_stage,
                )
            )
            continue

        next_stage = _next_protocol_stage(frame, action_type)
        if next_stage != frame.current_stage:
            updated.append(
                ProtocolFrameState(
                    frame_id=frame.frame_id,
                    frame_type=frame.frame_type,
                    status=frame.status,
                    variables=frame.variables,
                    origin=frame.origin,
                    current_stage=next_stage,
                )
            )
            continue

        updated.append(frame)
    trace.protocol_frames = updated


def _next_protocol_stage(frame: ProtocolFrameState, action_type: str | None) -> str | None:
    if action_type not in ("transfer_completion", "superaccept"):
        return frame.current_stage
    if frame.current_stage == "opener_rebid" and frame.frame_type in ("major_transfer", "minor_transfer", "transfer"):
        return "responder_continuation"
    return frame.current_stage


def _frame_should_close(frame: ProtocolFrameState, action_type: str | None, call_act_types: set[str]) -> bool:
    if frame.frame_type not in ("major_transfer", "minor_transfer", "transfer"):
        return False
    return action_type in ("final_placement", "signoff") or "final_placement" in call_act_types


def _recover_bidding_plans(convention_set: ConventionSet, trace: SemanticTrace, call: str, prior_auction: Auction) -> None:
    for plan in convention_set.bidding_plans:
        if plan.entry_call != call:
            continue
        if not matches_context(plan.context, prior_auction):
            continue
        trace.add_plan_state(
            PlanState(
                plan_id=plan.id,
                goal=plan.goal,
                owner=plan.owner,
                current_node=plan.start_node,
                status="active",
                origin=plan.origin_dict(),
            )
        )


def _advance_bidding_plans(
    convention_set: ConventionSet,
    trace: SemanticTrace,
    call: str,
    call_specification: CallSpecification,
) -> None:
    if not trace.plan_states:
        return

    updated = []
    for state in trace.plan_states:
        if state.status != "active":
            updated.append(state)
            continue
        plan = _plan_for_state(convention_set, state)
        if plan is None:
            updated.append(state)
            continue
        node = plan.workflow.get("nodes", {}).get(state.current_node, {})
        if node.get("kind") == "make_call" and normalize_call(node["call"]) == call:
            next_node = node.get("goto") or node.get("then")
            if next_node:
                next_node_data = plan.workflow.get("nodes", {}).get(next_node, {})
                updated.append(
                    PlanState(
                        plan_id=state.plan_id,
                        goal=state.goal,
                        owner=state.owner,
                        current_node=next_node,
                        status=_plan_status_for_node(next_node_data),
                        origin=state.origin,
                    )
                )
                continue
            updated.append(
                PlanState(
                    plan_id=state.plan_id,
                    goal=state.goal,
                    owner=state.owner,
                    current_node=state.current_node,
                    status="closed",
                    origin=state.origin,
                )
            )
            continue
        if node.get("kind") != "wait_for_call":
            updated.append(state)
            continue
        next_node = _matching_plan_branch_target(node, call, call_specification, trace)
        if next_node is None:
            updated.append(state)
            continue
        next_node_data = plan.workflow.get("nodes", {}).get(next_node, {})
        updated.append(
            PlanState(
                plan_id=state.plan_id,
                goal=state.goal,
                owner=state.owner,
                current_node=next_node,
                status=_plan_status_for_node(next_node_data),
                origin=state.origin,
            )
        )
    trace.plan_states = updated


def _plan_for_state(convention_set: ConventionSet, state: PlanState):
    for plan in convention_set.bidding_plans:
        if plan.origin_dict()["qualified_id"] == state.origin.get("qualified_id"):
            return plan
    return None


def _matching_plan_branch_target(
    node: dict[str, Any],
    call: str,
    call_specification: CallSpecification,
    trace: SemanticTrace,
) -> str | None:
    for branch in node.get("branches", []) or []:
        if _plan_branch_matches(branch.get("when", {}), call, call_specification, trace):
            return branch.get("goto")
    return None


def _plan_branch_matches(
    predicate: dict[str, Any],
    call: str,
    call_specification: CallSpecification,
    trace: SemanticTrace,
) -> bool:
    kind = predicate.get("kind")
    if kind == "call_is":
        return normalize_call(predicate["value"]) == call
    if kind == "call_act_type_is":
        value = predicate["value"]
        return value in call_specification.call_act_types or value in call_specification.meaning.get("call_act_types", [])
    if kind == "state_has":
        return trace.state_has(predicate["query"])
    if kind == "state_missing":
        return not trace.state_has(predicate["query"])
    return False


def _plan_status_for_node(node: dict[str, Any]) -> str:
    kind = node.get("kind")
    if kind == "end_plan":
        return "closed"
    if kind == "fail_plan":
        return "failed"
    return "active"


def _default_candidate(call_specifications: list[CallSpecification], auction: Auction) -> Candidate:
    for call_specification in call_specifications:
        if not call_specification.default_policy:
            continue
        if call_specification.auction_pattern != "*" and not matches_pattern(call_specification.auction_pattern, auction):
            continue
        return _candidate_from_default_call_specification(call_specification)
    return _hard_fallback_candidate()


def _candidate_from_default_call_specification(call_specification: CallSpecification) -> Candidate:
    return Candidate(
        call=call_specification.call,
        origin=call_specification.origin_dict(),
        public_meaning=call_specification.meaning,
        algorithm="default_policy",
        call_specification_id=call_specification.id,
        score=0,
        criteria_results=(),
    )


def _hard_fallback_candidate() -> Candidate:
    return Candidate(
        call="P",
        origin={
            "namespace": "default",
            "convention_id": "default_policy",
            "convention_name": "Default Policy",
            "convention_version": "0.0.1",
            "object_type": "call_specification",
            "object_id": "cs_1",
            "qualified_id": "default/default_policy@0.0.1:call_specification:cs_1",
            "author": {
                "name": "Meow Li",
                "contact": None,
                "organization": None,
            },
        },
        public_meaning={
            "nature_labels": ["default"],
            "call_act_types": ["final_placement"],
            "action_type": "fallback_pass",
            "alertable": False,
        },
        algorithm="default_policy",
        call_specification_id="cs_1",
        score=0,
        criteria_results=(),
    )


def _materialize_effect(
    effect: dict[str, Any],
    hand: Hand | None,
    trace: SemanticTrace,
    environment: dict[str, Any],
) -> dict[str, Any]:
    active_hand = hand or Hand.from_dict({})
    return {key: _materialize_value(value, active_hand, trace, environment) for key, value in effect.items()}


def _apply_effect(
    trace: SemanticTrace,
    effect: dict[str, Any],
    origin: dict[str, Any],
    hand: Hand | None,
    environment: dict[str, Any],
) -> None:
    materialized = _materialize_effect(effect, hand, trace, environment)
    if "state" in materialized:
        trace.add_auction_state(AuctionStateVariable.from_dict(materialized["state"], origin))
        return
    if "state_update" in materialized:
        trace.add_auction_state(AuctionStateVariable.from_dict(materialized["state_update"], origin))
        return
    trace.add_fact(SemanticFact.from_dict(materialized, origin))


def _materialize_value(value: Any, hand: Hand, trace: SemanticTrace, environment: dict[str, Any]) -> Any:
    if isinstance(value, dict) and "expr" in value:
        return evaluate_expression(value["expr"], hand, trace, environment)
    if isinstance(value, list):
        return [_materialize_value(item, hand, trace, environment) for item in value]
    if isinstance(value, dict):
        return {key: _materialize_value(item, hand, trace, environment) for key, item in value.items()}
    return value
