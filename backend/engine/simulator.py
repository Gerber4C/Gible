from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .auction import Auction
from .calls import normalize_call
from .cards import Hand
from .memory import SeatMemory
from .model import PartnershipProfile
from .explanation import explain
from .legality import auction_is_complete
from .selector import choose_bid


@dataclass(frozen=True)
class SimulatedCall:
    seat: str
    call: str
    explanation: dict[str, Any] | None


@dataclass(frozen=True)
class SimulatedAuction:
    calls: tuple[str, ...]
    call_records: tuple[SimulatedCall, ...]
    diagnostics: tuple[str, ...]
    private_memories: dict[str, Any]
    status: str = "complete"
    blocked: dict[str, Any] | None = None

    def compact_sequence(self) -> str:
        return "".join(self.calls)


def simulate_auction(
    profile: PartnershipProfile,
    hands: dict[str, str | Hand],
    dealer: str = "n",
    vulnerability: str = "none",
    environment: dict[str, Any] | None = None,
    max_calls: int = 80,
) -> SimulatedAuction:
    parsed_hands = {seat.lower(): Hand.parse(hand) if isinstance(hand, str) else hand for seat, hand in hands.items()}
    calls: list[str] = []
    records: list[SimulatedCall] = []
    diagnostics: list[str] = []
    active_environment = dict(environment or {})
    # The runner owns all supplied hands; an individual bidder must not see them.
    active_environment.pop("partner_hand", None)
    active_environment.setdefault("dealer", dealer)
    active_environment.setdefault("vulnerability", vulnerability)
    private_memories: dict[str, SeatMemory] = {seat: SeatMemory() for seat in parsed_hands}
    blocked = None

    while len(calls) < max_calls:
        auction = Auction(calls=tuple(calls), dealer=dealer, vulnerability=vulnerability)
        if auction_is_complete(auction):
            break
        actor = auction.actor_to_call
        if actor not in parsed_hands:
            call = "P"
            records.append(SimulatedCall(seat=actor, call=call, explanation=None))
            calls.append(call)
            continue

        hand = parsed_hands[actor]
        selection_environment = {
            **active_environment,
            "seat": actor,
        }
        selection = choose_bid(profile, auction, hand, selection_environment, private_memories.get(actor))
        private_memories[actor] = selection.private_memory
        explanation = explain(selection)
        diagnostics.extend(explanation.get("diagnostics", []))
        if selection.call is None:
            blocked = {'auction':auction.compact_sequence(),'seat':actor,
                       'diagnostics':explanation['diagnostics'],'axioms':explanation['axioms']}
            break
        call = normalize_call(explanation["call"])
        records.append(SimulatedCall(seat=actor, call=call, explanation=explanation))
        calls.append(call)

    if len(calls) >= max_calls and not auction_is_complete(Auction(calls=tuple(calls), dealer=dealer, vulnerability=vulnerability)):
        diagnostics.append(f"Simulation stopped after max_calls={max_calls}")

    return SimulatedAuction(
        calls=tuple(calls),
        call_records=tuple(records),
        diagnostics=tuple(diagnostics),
        private_memories={seat: memory.to_dict() for seat, memory in private_memories.items()},
        status='blocked' if blocked else ('complete' if auction_is_complete(Auction(tuple(calls),dealer,vulnerability)) else 'limit'),
        blocked=blocked,
    )
