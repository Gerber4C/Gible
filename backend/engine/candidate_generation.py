from __future__ import annotations

from typing import Any

from .auction import Auction
from .call_space import steps_after
from .calls import normalize_call
from .cards import Hand
from .context import BridgeContext, CallCandidate
from .evaluator import evaluate
from .legality import is_call_legal, legal_calls
from .matcher import matches_context, matches_pattern
from .memory import SeatMemory
from .model import CallSpec, PartnershipProfile
from .trace import AuctionTrace, PrivateRouteState


def generate_candidates(
    profile: PartnershipProfile,
    auction: Auction,
    hand: Hand,
    trace: AuctionTrace,
    environment: dict[str, Any],
    private_memory: SeatMemory,
) -> tuple[CallCandidate, ...]:
    call_specification_candidates = []
    for call_specification in profile.call_specifications:
        if call_specification.default_policy:
            continue
        if not matches_context(call_specification.context, auction):
            continue
        if not _condition_passes(call_specification.requires, auction, hand, trace, environment):
            continue
        if not _condition_passes(call_specification.applicability, auction, hand, trace, environment):
            continue

        candidate = _candidate(call_specification, auction, hand, trace, environment)
        if candidate is None:
            continue
        if not is_call_legal(auction, candidate.call):
            trace.warn(
                "Illegal candidate "
                f"{candidate.call} from {candidate.origin['qualified_id']} "
                f"for auction {auction.compact_sequence()}"
            )
            continue
        call_specification_candidates.append(candidate)

    candidates = list(call_specification_candidates)
    for candidate in _private_route_candidates(
        profile,
        auction,
        hand,
        trace,
        environment,
        tuple(call_specification_candidates),
        private_memory,
    ):
        if not is_call_legal(auction, candidate.call):
            trace.warn(
                "Illegal PrivateRoute candidate "
                f"{candidate.call} from {candidate.origin['qualified_id']} "
                f"for auction {auction.compact_sequence()}"
            )
            continue
        candidates.append(candidate)
    return tuple(candidates)


def call_for_call_specification(
    call_specification: CallSpec,
    auction: Auction,
    trace: AuctionTrace,
) -> str | None:
    if call_specification.call is not None:
        return call_specification.call
    template = call_specification.call_template.get("relative_call", call_specification.call_template)
    if not template:
        return None
    kind = template.get("type")
    if kind == "step_after_state_call":
        records = trace.matching_state(template.get("query", {}))
        if not records:
            return None
        anchor = records[-1].attribute(template.get("attribute", "ask_call"))
        if anchor is None:
            return None
        return steps_after(anchor, int(template.get("step", 1)))
    if kind == "step_after_last_contract":
        from .call_space import last_contract_call

        anchor = last_contract_call(auction)
        if anchor is None:
            return None
        return steps_after(anchor, int(template.get("step", 1)))
    raise ValueError(f"Unsupported relative call template: {kind}")


def default_candidate(call_specifications: list[CallSpec], auction: Auction) -> CallCandidate:
    for call_specification in call_specifications:
        if not call_specification.default_policy:
            continue
        if call_specification.auction_pattern != "*" and not matches_pattern(call_specification.auction_pattern, auction):
            continue
        return _candidate_from_default_call_specification(call_specification)
    return _hard_fallback_candidate()


def _candidate(
    call_specification: CallSpec,
    auction: Auction,
    hand: Hand,
    trace: AuctionTrace,
    environment: dict[str, Any],
) -> CallCandidate | None:
    call = call_for_call_specification(call_specification, auction, trace)
    if call is None:
        return None
    evaluation = {"score": 0, "criteria_results": (), "algorithm": "python_applies"}
    return CallCandidate(
        call=call,
        origin=call_specification.origin_dict(),
        public_meaning=call_specification.meaning.to_dict(),
        source_kind="call_spec",
        source_id=call_specification.id,
        score=evaluation["score"],
        criterion_results=tuple(evaluation["criteria_results"]),
        implementation_origin=call_specification.origin_dict(),
        capabilities=call_specification.capabilities,
        metadata={"selection_algorithm": evaluation["algorithm"]},
    )


def _condition_passes(
    condition,
    auction: Auction,
    hand: Hand,
    trace: AuctionTrace,
    environment: dict[str, Any],
) -> bool:
    if not condition:
        return True
    if callable(condition):
        ctx = BridgeContext.from_trace(
            phase="candidate",
            auction=auction,
            hand=hand,
            environment=environment,
            trace=trace,
            legal_calls=legal_calls(auction),
        )
        return bool(condition(ctx))
    return evaluate(condition, hand, trace, environment)


def _meaning_dict(value: Any) -> dict[str, Any]:
    if hasattr(value, "to_dict"):
        return value.to_dict()
    return dict(value or {})


def _private_route_candidates(
    profile: PartnershipProfile,
    auction: Auction,
    hand: Hand,
    trace: AuctionTrace,
    environment: dict[str, Any],
    call_specification_candidates: tuple[CallCandidate, ...],
    private_memory: SeatMemory,
) -> tuple[CallCandidate, ...]:
    entry_candidates = _entry_private_route_candidates(profile, auction, hand, trace, environment, call_specification_candidates)
    active_candidates = []
    for state in trace.private_route_states:
        candidate = _active_private_route_candidate(
            profile,
            state,
            hand,
            trace,
            environment,
            call_specification_candidates,
        )
        if candidate is not None:
            active_candidates.append(candidate)
    memory_candidates = [
        candidate
        for candidate in active_candidates
        if private_memory.has_selected_route(candidate.private_route_origin)
    ]
    if memory_candidates:
        active_candidates = memory_candidates
    return tuple(entry_candidates + active_candidates)


def _active_private_route_candidate(
    profile: PartnershipProfile,
    state: PrivateRouteState,
    hand: Hand,
    trace: AuctionTrace,
    environment: dict[str, Any],
    call_specification_candidates: tuple[CallCandidate, ...],
) -> CallCandidate | None:
    if state.status != "active":
        return None
    route = _private_route_for_state(profile, state)
    if route is None:
        trace.warn(f"Active PrivateRoute state {state.route_id} no longer has a loaded route")
        return None
    if not _condition_passes(route.preconditions, Auction(calls=()), hand, trace, environment):
        return None
    node = route.workflow.get("nodes", {}).get(state.current_node, {})
    if node.get("kind") != "make_call":
        return None
    return _private_route_make_call_candidate(route, state, node, hand, trace, environment, call_specification_candidates)


def _private_route_make_call_candidate(
    route,
    state: PrivateRouteState,
    node: dict[str, Any],
    hand: Hand,
    trace: AuctionTrace,
    environment: dict[str, Any],
    call_specification_candidates: tuple[CallCandidate, ...],
) -> CallCandidate | None:
    if node.get("requires") and not _condition_passes(node["requires"], Auction(calls=()), hand, trace, environment):
        return None
    call = normalize_call(node["call"])
    implementation = _matching_candidate_for_call(call_specification_candidates, call)
    if node.get("requires_call_specification", False) and implementation is None:
        trace.warn(f"PrivateRoute {route.origin_dict()['qualified_id']} requires a Call Specification for {call}")
        return None
    return _implemented_private_route_candidate(
        call=call,
        route=route,
        node_id=state.current_node,
        node=node,
        implementation=implementation,
        source_kind="private_route_continuation",
    )


def _implemented_private_route_candidate(
    *,
    call: str,
    route,
    node_id: str,
    node: dict[str, Any],
    implementation: CallCandidate | None,
    source_kind: str,
) -> CallCandidate:
    score = int(node.get("score", route.entry_score if node_id == "entry" else 100))
    private_route_origin = route.origin_dict()
    implementation_origin = implementation.origin if implementation else None
    capabilities = _merge_capabilities(route.capabilities, node.get("capabilities", ()), implementation.capabilities if implementation else ())
    return CallCandidate(
        call=call,
        origin=implementation.origin if implementation else private_route_origin,
        public_meaning=_meaning_dict(
            node.get(
                "meaning",
                implementation.public_meaning if implementation else {
                    "nature_labels": ["private_route_continuation"],
                    "call_act_types": ["final_placement"],
                    "action_type": "private_route_make_call",
                    "alertable": False,
                },
            )
        ),
        source_kind=source_kind,
        source_id=f"{route.id}:{node_id}",
        score=score,
        criterion_results=_private_route_candidate_criterion_results(route, score, implementation),
        private_route_origin=private_route_origin,
        implementation_origin=implementation_origin,
        capabilities=capabilities,
        metadata={
            "route_id": route.id,
            "route_node": node_id,
            "route_goal": route.goal,
            "implemented_by_call_specification": implementation_origin,
        },
    )


def _private_route_candidate_criterion_results(route, score: int, implementation: CallCandidate | None) -> tuple[dict[str, Any], ...]:
    results = [
        {
            "criterion_id": "private_route_preconditions",
            "evaluator": "condition",
            "passed": True,
            "required": True,
            "value": route.preconditions,
            "contribution": score,
        }
    ]
    if implementation:
        results.append(
            {
                "criterion_id": "implemented_by_call_specification",
                "evaluator": "call_specification_lookup",
                "passed": True,
                "required": True,
                "value": implementation.origin["qualified_id"],
                "contribution": 0,
            }
        )
    return tuple(results)


def _entry_private_route_candidates(
    profile: PartnershipProfile,
    auction: Auction,
    hand: Hand,
    trace: AuctionTrace,
    environment: dict[str, Any],
    call_specification_candidates: tuple[CallCandidate, ...],
) -> list[CallCandidate]:
    candidates = []
    for route in profile.private_routes:
        candidate = _private_route_entry_candidate(route, auction, hand, trace, environment, call_specification_candidates)
        if candidate is not None:
            candidates.append(candidate)
    return candidates


def _private_route_entry_candidate(
    route,
    auction: Auction,
    hand: Hand,
    trace: AuctionTrace,
    environment: dict[str, Any],
    call_specification_candidates: tuple[CallCandidate, ...],
) -> CallCandidate | None:
    if not route.entry_candidate:
        return None
    if _private_route_state_exists(trace, route):
        return None
    if not matches_context(route.context, auction):
        return None
    if not _condition_passes(route.preconditions, auction, hand, trace, environment):
        return None
    implementation = _matching_candidate_for_call(call_specification_candidates, route.entry_call)
    if implementation is None:
        trace.warn(f"PrivateRoute {route.origin_dict()['qualified_id']} cannot enter because {route.entry_call} has no eligible Call Specification")
        return None
    return CallCandidate(
        call=route.entry_call,
        origin=implementation.origin,
        public_meaning=implementation.public_meaning,
        source_kind="private_route_entry",
        source_id=f"{route.id}:entry",
        score=route.entry_score,
        criterion_results=_private_route_candidate_criterion_results(route, route.entry_score, implementation),
        private_route_origin=route.origin_dict(),
        implementation_origin=implementation.origin,
        capabilities=_merge_capabilities(route.capabilities, implementation.capabilities),
        metadata={
            "route_id": route.id,
            "route_node": "entry",
            "route_goal": route.goal,
            "implemented_by_call_specification": implementation.origin,
        },
    )


def _matching_candidate_for_call(candidates: tuple[CallCandidate, ...], call: str) -> CallCandidate | None:
    normalized_call = normalize_call(call)
    matching = [candidate for candidate in candidates if candidate.call == normalized_call and candidate.private_route_origin is None]
    if not matching:
        return None
    return sorted(matching, key=lambda candidate: candidate.score, reverse=True)[0]


def _merge_capabilities(*sources) -> tuple[str, ...]:
    merged: list[str] = []
    for source in sources:
        if isinstance(source, str):
            items = (source,)
        else:
            items = tuple(source or ())
        for item in items:
            text = str(item)
            if text not in merged:
                merged.append(text)
    return tuple(merged)


def _private_route_state_exists(trace: AuctionTrace, route) -> bool:
    qualified_id = route.origin_dict()["qualified_id"]
    return any(state.origin.get("qualified_id") == qualified_id and state.status == "active" for state in trace.private_route_states)


def _private_route_for_state(profile: PartnershipProfile, state: PrivateRouteState):
    for route in profile.private_routes:
        if route.origin_dict()["qualified_id"] == state.origin.get("qualified_id"):
            return route
    return None


def _candidate_from_default_call_specification(call_specification: CallSpec) -> CallCandidate:
    return CallCandidate(
        call=call_specification.call or "P",
        origin=call_specification.origin_dict(),
        public_meaning=call_specification.meaning.to_dict(),
        source_kind="default_policy",
        source_id=call_specification.id,
        score=0,
        criterion_results=(),
        implementation_origin=call_specification.origin_dict(),
        capabilities=call_specification.capabilities,
    )


def _hard_fallback_candidate() -> CallCandidate:
    return CallCandidate(
        call="P",
        origin={
            "namespace": "default",
            "gadget_id": "default_policy",
            "gadget_name": "Default Policy",
            "gadget_version": "0.0.1",
            "object_type": "call_spec",
            "object_id": "cs_1",
            "qualified_id": "default/default_policy@0.0.1:call_spec:cs_1",
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
        source_kind="default_policy",
        source_id="cs_1",
        score=0,
        criterion_results=(),
        capabilities=("fallback", "place_contract"),
    )
