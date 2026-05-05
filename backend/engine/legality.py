from __future__ import annotations

from dataclasses import dataclass

from .auction import Auction
from .calls import ContractBid, SUITS, is_contract_bid, normalize_call


SIDE_BY_SEAT = {
    "n": "ns",
    "s": "ns",
    "e": "ew",
    "w": "ew",
}


@dataclass(frozen=True)
class ContractState:
    call: str
    index: int
    seat: str
    side: str
    doubled: bool
    redoubled: bool


@dataclass(frozen=True)
class IllegalCall:
    call: str
    index: int
    reason: str


def auction_is_complete(auction: Auction) -> bool:
    calls = auction.calls
    if len(calls) < 4:
        return False
    if all(call == "P" for call in calls[:4]):
        return True
    state = last_contract_state(auction)
    if state is None:
        return False
    return len(calls) >= state.index + 4 and calls[-3:] == ("P", "P", "P")


def legal_calls(auction: Auction) -> tuple[str, ...]:
    if auction_is_complete(auction):
        return ()

    calls = ["P"]
    calls.extend(_legal_contract_bids(auction))
    if is_call_legal(auction, "X"):
        calls.append("X")
    if is_call_legal(auction, "R"):
        calls.append("R")
    return tuple(calls)


def is_call_legal(auction: Auction, call: str) -> bool:
    canonical = normalize_call(call)
    if auction_is_complete(auction):
        return False
    if canonical == "P":
        return True
    if is_contract_bid(canonical):
        return _is_contract_legal(auction, canonical)
    if canonical == "X":
        return _is_double_legal(auction)
    if canonical == "R":
        return _is_redouble_legal(auction)
    return False


def illegal_calls_in_auction(auction: Auction) -> tuple[IllegalCall, ...]:
    illegal = []
    for index, call in enumerate(auction.calls):
        prior = Auction(calls=auction.calls[:index], dealer=auction.dealer, vulnerability=auction.vulnerability)
        if not is_call_legal(prior, call):
            illegal.append(IllegalCall(call=call, index=index, reason=_illegal_reason(prior, call)))
    return tuple(illegal)


def last_contract_state(auction: Auction) -> ContractState | None:
    calls = auction.calls
    for index in range(len(calls) - 1, -1, -1):
        if is_contract_bid(calls[index]):
            doubled = False
            redoubled = False
            for later_call in calls[index + 1 :]:
                if later_call == "X":
                    doubled = True
                    redoubled = False
                elif later_call == "R":
                    redoubled = True
            seat = auction.actor_at(index)
            return ContractState(
                call=calls[index],
                index=index,
                seat=seat,
                side=SIDE_BY_SEAT[seat],
                doubled=doubled,
                redoubled=redoubled,
            )
    return None


def _legal_contract_bids(auction: Auction) -> tuple[str, ...]:
    return tuple(f"{level}{suit}" for level in range(1, 8) for suit in SUITS if _is_contract_legal(auction, f"{level}{suit}"))


def _is_contract_legal(auction: Auction, call: str) -> bool:
    state = last_contract_state(auction)
    if state is None:
        return True
    return ContractBid.parse(call).rank > ContractBid.parse(state.call).rank


def _is_double_legal(auction: Auction) -> bool:
    state = last_contract_state(auction)
    if state is None or state.doubled:
        return False
    return SIDE_BY_SEAT[auction.actor_to_call] != state.side


def _is_redouble_legal(auction: Auction) -> bool:
    state = last_contract_state(auction)
    if state is None or not state.doubled or state.redoubled:
        return False
    return SIDE_BY_SEAT[auction.actor_to_call] == state.side


def _illegal_reason(auction: Auction, call: str) -> str:
    canonical = normalize_call(call)
    if auction_is_complete(auction):
        return "auction is already complete"
    if is_contract_bid(canonical):
        state = last_contract_state(auction)
        if state is not None:
            return f"contract bid does not outrank current contract {state.call}"
    if canonical == "X":
        return "double requires an undoubled contract by the opposing side"
    if canonical == "R":
        return "redouble requires a doubled contract by our side"
    return "call is not legal in this auction"
