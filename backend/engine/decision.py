from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .auction import Auction
from .cards import Hand
from .context import BridgeContext, CallCandidate, CandidatePool
from .legality import legal_calls
from .memory import SeatMemory
from .model import PolicyFunction
from .trace import AuctionTrace


@dataclass(frozen=True)
class DecisionResult:
    selected: CallCandidate
    ordered: tuple[CallCandidate, ...]
    policy_origin: dict[str, Any] | None
    context: BridgeContext


def choose_candidate(
    candidates: tuple[CallCandidate, ...],
    policy_functions: tuple[PolicyFunction, ...],
    auction: Auction,
    hand: Hand,
    trace: AuctionTrace,
    environment: dict[str, Any],
    private_memory: SeatMemory,
) -> DecisionResult:
    candidates = _resolve_same_call_meanings(candidates, trace)
    pool = CandidatePool(candidates, auction)
    decision_context = BridgeContext.from_trace(
        phase="decision",
        auction=auction,
        hand=hand,
        environment=environment,
        trace=trace,
        legal_calls=legal_calls(auction),
        candidates=pool,
        memory=private_memory,
    )
    selected_by_function = _select_by_policy_function(policy_functions, decision_context, pool, trace)
    if selected_by_function is not None:
        selected, policy_origin = selected_by_function
        return DecisionResult(
            selected=selected,
            ordered=_ordered_with_selected_first(selected, candidates),
            policy_origin=policy_origin,
            context=decision_context,
        )

    ordered = tuple(sorted(candidates, key=pool._sort_key, reverse=True))
    if len(ordered) > 1 and ordered[0].score == ordered[1].score:
        trace.warn(f"Ambiguous top score for {ordered[0].call} and {ordered[1].call}")

    return DecisionResult(
        selected=ordered[0],
        ordered=ordered,
        policy_origin=None,
        context=decision_context,
    )


def _select_by_policy_function(
    policy_functions: tuple[PolicyFunction, ...],
    ctx: BridgeContext,
    pool: CandidatePool,
    trace: AuctionTrace,
) -> tuple[CallCandidate, dict[str, Any]] | None:
    for policy_function in policy_functions:
        try:
            result = policy_function.procedure(ctx, pool)
        except Exception as exc:
            trace.warn(f"Policy function {policy_function.qualified_id} failed: {exc}")
            continue
        if result is None:
            continue
        if result not in pool.candidates:
            trace.warn(
                f"Policy function {policy_function.qualified_id} returned an object that is not in the current candidate pool"
            )
            continue
        return result, policy_function.origin_dict()
    return None


def _ordered_with_selected_first(selected: CallCandidate, candidates: tuple[CallCandidate, ...]) -> tuple[CallCandidate, ...]:
    rest = [candidate for candidate in sorted(candidates, key=lambda item: item.score, reverse=True) if candidate is not selected]
    return (selected, *rest)


def _resolve_same_call_meanings(
    candidates: tuple[CallCandidate, ...],
    trace: AuctionTrace,
) -> tuple[CallCandidate, ...]:
    grouped: dict[str, list[CallCandidate]] = {}
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
        route_selected = _private_route_candidate_for_implemented_call(group)
        if route_selected is not None:
            resolved.append(route_selected)
            continue
        ordered_group = sorted(group, key=lambda candidate: candidate.score, reverse=True)
        origins = ", ".join(candidate.origin["qualified_id"] for candidate in ordered_group)
        trace.warn(f"Ambiguous meaning for call {call}: {origins}")
        resolved.extend(ordered_group)
    return tuple(resolved)


def _same_final_pass_action(group: list[CallCandidate]) -> bool:
    return all(
        candidate.call == "P" and candidate.public_meaning.get("action_type") == "pass_final_contract"
        for candidate in group
    )


def _private_route_candidate_for_implemented_call(group: list[CallCandidate]) -> CallCandidate | None:
    private_route_candidates = [candidate for candidate in group if candidate.private_route_origin is not None]
    non_private_route_candidates = [candidate for candidate in group if candidate.private_route_origin is None]
    if not private_route_candidates or not non_private_route_candidates:
        return None
    implemented = []
    for private_route_candidate in private_route_candidates:
        if any(
            private_route_candidate.origin == candidate.origin and private_route_candidate.public_meaning == candidate.public_meaning
            for candidate in non_private_route_candidates
        ):
            implemented.append(private_route_candidate)
    if not implemented:
        return None
    return sorted(implemented, key=lambda candidate: candidate.score, reverse=True)[0]

