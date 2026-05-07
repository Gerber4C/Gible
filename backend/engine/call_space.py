from __future__ import annotations

from dataclasses import dataclass

from .auction import Auction
from .calls import SUITS, ContractBid, is_contract_bid, normalize_call


CONTRACT_ORDER = tuple(f"{level}{suit}" for level in range(1, 8) for suit in SUITS)
CONTRACT_RANK = {call: index for index, call in enumerate(CONTRACT_ORDER)}


@dataclass(frozen=True)
class CallRelation:
    call: str
    is_contract: bool
    level: int | None = None
    denomination: str | None = None
    last_contract: str | None = None
    steps_over_last_contract: int | None = None


def contract_rank(call: str) -> int:
    return CONTRACT_RANK[normalize_call(call)]


def contract_at_rank(rank: int) -> str | None:
    if rank < 0 or rank >= len(CONTRACT_ORDER):
        return None
    return CONTRACT_ORDER[rank]


def steps_after(anchor_call: str, steps: int) -> str | None:
    anchor = normalize_call(anchor_call)
    if not is_contract_bid(anchor):
        raise ValueError(f"Step anchor must be a contract bid: {anchor_call}")
    if steps < 1:
        raise ValueError("Step number must be at least 1")
    return contract_at_rank(contract_rank(anchor) + steps)


def steps_between(anchor_call: str, response_call: str) -> int | None:
    anchor = normalize_call(anchor_call)
    response = normalize_call(response_call)
    if not is_contract_bid(anchor) or not is_contract_bid(response):
        return None
    distance = contract_rank(response) - contract_rank(anchor)
    return distance if distance > 0 else None


def last_contract_call(auction: Auction) -> str | None:
    for call in reversed(auction.calls):
        if is_contract_bid(call):
            return call
    return None


def relation_to_last_contract(auction: Auction, call: str) -> CallRelation:
    normalized = normalize_call(call)
    if not is_contract_bid(normalized):
        return CallRelation(call=normalized, is_contract=False)

    contract = ContractBid.parse(normalized)
    last_contract = last_contract_call(auction)
    return CallRelation(
        call=normalized,
        is_contract=True,
        level=contract.level,
        denomination=contract.suit,
        last_contract=last_contract,
        steps_over_last_contract=steps_between(last_contract, normalized) if last_contract else None,
    )
