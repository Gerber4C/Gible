from __future__ import annotations

from typing import Any

from .auction import Auction
from .axiom_facts import INVITES, tags
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
from .legality import SIDE_BY_SEAT
from .trump_state import is_transition_effect


def replay_auction(
    profile: PartnershipProfile,
    auction: Auction,
    hand: Hand | None = None,
    environment: dict | None = None,
) -> AuctionTrace:
    trace = AuctionTrace()
    call_specifications = list(profile.call_specifications)
    for index, call in enumerate(auction.calls):
        seat = auction.actor_at(index)
        trace.active_seat = seat
        trace.perspective_side = SIDE_BY_SEAT[seat]
        pattern = historical_pattern_for(auction.calls, index)
        prior_auction = Auction(calls=auction.calls[:index], dealer=auction.dealer, vulnerability=auction.vulnerability)
        active_environment = active_environment_for(profile, environment, prior_auction)
        def matching(item):
            return (item.has_meaning and not item.default_policy
                    and (call != 'P' or item.effects or tags(item.meaning.to_dict()) & (INVITES | {'forcing','game_forcing','accept','reject'}))
                    and matches_context(item.context, prior_auction)
                    and call_for_call_specification(item, prior_auction, trace) == call
                    and _public_condition_passes(item.requires, prior_auction, trace, active_environment))

        overrides = [item for item in call_specifications
                     if any(is_transition_effect(effect) for effect in item.effects) and matching(item)]
        if overrides:
            matches = overrides
        else:
            trace.promote_for_call(seat)
            matches = [item for item in call_specifications if matching(item)]
        call_specification = _unique_match(matches)
        if len(matches) > 1 and call_specification is None:
            trace.warn(f"Ambiguous prior call {call} at auction position {index + 1}")
        if not matches:
            if call != "P":
                trace.warn(f"Undefined prior call {call} at auction position {index + 1}")
            continue
        if call_specification is None:
            continue
        origin = call_specification.origin_dict()
        state_start = len(trace.state_records)
        for effect in call_specification.effects:
            try:
                apply_effect(trace, effect, origin, _PublicHand(), active_environment)
            except _PrivateHandUnavailable:
                trace.warn(f"Private hand-dependent effect omitted from public replay: {origin['qualified_id']}")
        trace.add_applied_meaning(
            {
                "call": call,
                "index": index,
                "seat": seat,
                "effects": [r.to_dict() for r in trace.state_records[state_start:]],
                "auction_pattern": pattern,
                "origin": origin,
                "public_meaning": call_specification.meaning.to_dict(),
            }
        )
        advance_frame_states(trace, call_specification)
        advance_private_routes(profile, trace, call, call_specification)
        recover_frame_states(profile, trace, call, prior_auction)
        recover_private_routes(profile, trace, call, prior_auction)
    trace.active_seat = None
    trace.perspective_side = SIDE_BY_SEAT[auction.actor_to_call]
    return trace


class _PrivateHandUnavailable(Exception):
    pass


class _PublicHand:
    def __getattr__(self, name):
        raise _PrivateHandUnavailable(name)


def _public_condition_passes(condition, auction: Auction, trace: AuctionTrace, environment: dict) -> bool:
    """Unknown private predicates cannot disprove a call already seen publicly."""
    if not condition:
        return True
    if callable(condition):
        ctx = BridgeContext.from_trace(phase='replay', auction=auction, hand=None,
                                       environment=environment, trace=trace)
        try:
            return bool(condition(ctx))
        except (AttributeError, TypeError, _PrivateHandUnavailable):
            return True
    if 'all' in condition:
        return all(_public_condition_passes(item, auction, trace, environment) for item in condition['all'])
    if 'any' in condition:
        return any(_public_condition_passes(item, auction, trace, environment) for item in condition['any'])
    if 'not' in condition:
        if _uses_private_hand(condition['not']):
            return True
        return not _public_condition_passes(condition['not'], auction, trace, environment)
    if _uses_private_hand(condition):
        public_parts = {key: value for key, value in condition.items()
                        if not str(key).startswith('self.') and not _uses_private_hand(value)}
        return evaluate(public_parts, _PublicHand(), trace, environment) if public_parts else True
    return evaluate(condition, _PublicHand(), trace, environment)


def _uses_private_hand(value) -> bool:
    if isinstance(value, dict):
        if any(str(key).startswith('self.') for key in value):
            return True
        if str(value.get('var', '')).startswith('self.'):
            return True
        if value.get('op') in ('length', 'hcp', 'balanced', 'honor_count', 'contains_rank',
                               'keycard_count', 'ace_count', 'king_count'):
            return True
        return any(_uses_private_hand(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return any(_uses_private_hand(item) for item in value)
    return False


def _unique_match(matches):
    if not matches:
        return None
    def rank(item):
        return (item.priority, item.context.get('auction_pattern') != '*',
                bool(item.context.get('seat_positions')))
    ranked = sorted(matches, key=rank, reverse=True)
    if len(ranked) > 1 and rank(ranked[0]) == rank(ranked[1]):
        return None
    return ranked[0]


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
    # Applies to direct decisions and replay, including caller-supplied environments.
    # Public partner evidence belongs in recovered state/knowledge, not a real hand.
    active_environment.pop("partner_hand", None)
    if auction is not None:
        active_environment["seat"] = auction.actor_to_call
        active_environment["dealer"] = auction.dealer
        active_environment["vulnerability"] = auction.vulnerability
        active_environment["seat_position"] = _opening_seat_position(auction)
        active_environment["vulnerability_relation"] = _vulnerability_relation(
            active_environment["seat"], auction.vulnerability)
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
