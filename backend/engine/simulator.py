from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .auction import Auction
from .calls import normalize_call
from .cards import Hand
from .convention import ConventionSet
from .explanation import explain
from .legality import auction_is_complete
from .selector import choose_bid


PARTNERS = {
    "n": "s",
    "s": "n",
    "e": "w",
    "w": "e",
}


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

    def compact_sequence(self) -> str:
        return "".join(self.calls)


def simulate_auction(
    convention_set: ConventionSet,
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
    active_environment.setdefault("dealer", dealer)
    active_environment.setdefault("vulnerability", vulnerability)

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
        partner_hand = parsed_hands.get(PARTNERS[actor])
        selection_environment = {
            **active_environment,
            "seat": actor,
            "partner_hand": partner_hand,
        }
        selection = choose_bid(convention_set, auction, hand, selection_environment)
        explanation = explain(selection)
        call = normalize_call(explanation["call"])
        diagnostics.extend(explanation.get("diagnostics", []))
        records.append(SimulatedCall(seat=actor, call=call, explanation=explanation))
        calls.append(call)

    if len(calls) >= max_calls and not auction_is_complete(Auction(calls=tuple(calls), dealer=dealer, vulnerability=vulnerability)):
        diagnostics.append(f"Simulation stopped after max_calls={max_calls}")

    return SimulatedAuction(calls=tuple(calls), call_records=tuple(records), diagnostics=tuple(diagnostics))
