from __future__ import annotations

from typing import Any

from .auction import Auction
from .calls import normalize_call
from .matcher import matches_context
from .model import CallSpec, PartnershipProfile, PrivateRouteSpec
from .trace import AuctionTrace, PrivateRouteState


def recover_private_routes(profile: PartnershipProfile, trace: AuctionTrace, call: str, prior_auction: Auction) -> None:
    for route in profile.private_routes:
        if route.entry_call != call:
            continue
        if not matches_context(route.context, prior_auction):
            continue
        trace.add_private_route_state(
            PrivateRouteState(
                route_id=route.id,
                goal=route.goal,
                owner=route.owner,
                current_node=route.start_node,
                status="active",
                origin=route.origin_dict(),
            )
        )


def advance_private_routes(
    profile: PartnershipProfile,
    trace: AuctionTrace,
    call: str,
    call_specification: CallSpec,
) -> None:
    if not trace.private_route_states:
        return

    updated = []
    for state in trace.private_route_states:
        if state.status != "active":
            updated.append(state)
            continue
        route = private_route_for_state(profile, state)
        if route is None:
            updated.append(state)
            continue
        node = route.workflow.get("nodes", {}).get(state.current_node, {})
        if node.get("kind") == "make_call" and normalize_call(node["call"]) == call:
            updated.append(_advance_make_call_node(route, state, node))
            continue
        if node.get("kind") != "wait_for_call":
            updated.append(state)
            continue
        next_node = _matching_private_route_branch_target(node, call, call_specification, trace)
        if next_node is None:
            updated.append(state)
            continue
        next_node_data = route.workflow.get("nodes", {}).get(next_node, {})
        updated.append(
            PrivateRouteState(
                route_id=state.route_id,
                goal=state.goal,
                owner=state.owner,
                current_node=next_node,
                status=_private_route_status_for_node(next_node_data),
                origin=state.origin,
            )
        )
    trace.private_route_states = updated


def private_route_for_state(profile: PartnershipProfile, state: PrivateRouteState) -> PrivateRouteSpec | None:
    for route in profile.private_routes:
        if route.origin_dict()["qualified_id"] == state.origin.get("qualified_id"):
            return route
    return None


def _advance_make_call_node(route: PrivateRouteSpec, state: PrivateRouteState, node: dict[str, Any]) -> PrivateRouteState:
    next_node = node.get("goto") or node.get("then")
    if next_node:
        next_node_data = route.workflow.get("nodes", {}).get(next_node, {})
        return PrivateRouteState(
            route_id=state.route_id,
            goal=state.goal,
            owner=state.owner,
            current_node=next_node,
            status=_private_route_status_for_node(next_node_data),
            origin=state.origin,
        )
    return PrivateRouteState(
        route_id=state.route_id,
        goal=state.goal,
        owner=state.owner,
        current_node=state.current_node,
        status="closed",
        origin=state.origin,
    )


def _matching_private_route_branch_target(
    node: dict[str, Any],
    call: str,
    call_specification: CallSpec,
    trace: AuctionTrace,
) -> str | None:
    for branch in node.get("branches", []) or []:
        if _private_route_branch_matches(branch.get("when", {}), call, call_specification, trace):
            return branch.get("goto")
    return None


def _private_route_branch_matches(
    predicate: dict[str, Any],
    call: str,
    call_specification: CallSpec,
    trace: AuctionTrace,
) -> bool:
    kind = predicate.get("kind")
    if kind == "call_is":
        return normalize_call(predicate["value"]) == call
    if kind == "call_act_type_is":
        value = predicate["value"]
        return value in call_specification.call_act_types or value in call_specification.meaning.to_dict().get("call_act_types", [])
    if kind == "state_has":
        return trace.state_has(predicate["query"])
    if kind == "state_missing":
        return not trace.state_has(predicate["query"])
    return False


def _private_route_status_for_node(node: dict[str, Any]) -> str:
    kind = node.get("kind")
    if kind == "end_route":
        return "closed"
    if kind == "fail_route":
        return "failed"
    return "active"
