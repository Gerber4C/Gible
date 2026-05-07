from __future__ import annotations

from typing import Any

from .auction import Auction
from .cards import Hand
from .candidate_generation import default_candidate, generate_candidates
from .context import BidDecision, CandidatePool
from .decision import choose_candidate
from .model import PartnershipProfile
from .legality import illegal_calls_in_auction
from .memory import SeatMemory
from .replay import active_environment_for, replay_auction


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
    candidates = generate_candidates(profile, auction, hand, trace, active_environment, actor_memory)

    if not candidates:
        fallback = default_candidate(call_specifications, auction)
        trace.warn(f"No matching Call Specification for auction: {auction.compact_sequence()}; defaulting to {fallback.call}")
        fallback_pool = CandidatePool((fallback,), auction)
        return BidDecision(
            call=fallback.call,
            selected_candidate=fallback,
            candidate_pool=fallback_pool,
            trace=trace,
            policy_origin=None,
            private_memory=actor_memory.remember_candidate(fallback),
        )

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
    return BidDecision(
        call=decision.selected.call,
        selected_candidate=decision.selected,
        candidate_pool=CandidatePool(decision.ordered, auction),
        trace=trace,
        policy_origin=decision.policy_origin,
        context=decision.context,
        private_memory=updated_memory,
    )


