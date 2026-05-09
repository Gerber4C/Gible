from __future__ import annotations

from typing import Any

from .auction import Auction
from .candidate_generation import call_for_call_specification
from .cards import Hand
from .context import BridgeContext
from .effects import apply_effect
from .evaluator import evaluate
from .frame_runtime import advance_frame_states, recover_frame_states
from .matcher import historical_pattern_for, matches_context
from .model import PartnershipProfile
from .private_route_runtime import advance_private_routes, recover_private_routes
from .trace import AuctionTrace


def replay_auction(
    profile: PartnershipProfile,
    auction: Auction,
    hand: Hand | None = None,
    environment: dict | None = None,
) -> AuctionTrace:
    trace = AuctionTrace()
    call_specifications = list(profile.call_specifications)
    for index, call in enumerate(auction.calls):
        if call == "P":
            continue
        pattern = historical_pattern_for(auction.calls, index)
        prior_auction = Auction(calls=auction.calls[:index], dealer=auction.dealer, vulnerability=auction.vulnerability)
        active_environment = active_environment_for(profile, environment, prior_auction)
        matches = [
            item
            for item in call_specifications
            if item.has_meaning
            and matches_context(item.context, prior_auction)
            and call_for_call_specification(item, prior_auction, trace) == call
            and _condition_passes(item.requires, prior_auction, hand or Hand.from_dict({}), trace, active_environment)
        ]
        if not matches:
            trace.warn(f"Undefined prior call {call} at auction position {index + 1}")
            continue
        if len(matches) > 1:
            trace.warn(f"Ambiguous prior call {call} at auction position {index + 1}")
        call_specification = matches[0]
        origin = call_specification.origin_dict()
        for effect in call_specification.effects:
            apply_effect(trace, effect, origin, hand, active_environment)
        trace.add_applied_meaning(
            {
                "call": call,
                "auction_pattern": pattern,
                "origin": origin,
                "public_meaning": call_specification.meaning.to_dict(),
            }
        )
        advance_frame_states(trace, call_specification)
        advance_private_routes(profile, trace, call, call_specification)
        recover_frame_states(profile, trace, call, prior_auction)
        recover_private_routes(profile, trace, call, prior_auction)
    return trace


def _condition_passes(condition, auction: Auction, hand: Hand, trace: AuctionTrace, environment: dict) -> bool:
    if not condition:
        return True
    if callable(condition):
        ctx = BridgeContext.from_trace(
            phase="replay",
            auction=auction,
            hand=hand,
            environment=environment,
            trace=trace,
        )
        return bool(condition(ctx))
    return evaluate(condition, hand, trace, environment)


def active_environment_for(profile: PartnershipProfile, environment: dict | None, auction: Auction | None = None) -> dict:
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
        evaluator.id: evaluator.definition
        for evaluator in profile.named_evaluators
        if evaluator.evaluator_type in {"python_function", "expression"}
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
