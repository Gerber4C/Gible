from __future__ import annotations

import json
from pathlib import Path

from engine.auction import Auction
from engine.cards import Hand
from engine.explanation import explain
from engine.loader import load_profile
from engine.selector import choose_bid
from engine.simulator import simulate_auction
from engine.system_notes import generate_system_notes


def bid(request: dict) -> dict:
    profile_id = request["profile"]["id"]
    environment = request.get("environment", {})
    dealer = environment.get("dealer", "n")
    vulnerability = environment.get("vulnerability", "none")
    profile = load_profile(profile_id, Path(__file__).resolve().parent)
    auction = Auction.parse(request["auction"], dealer=dealer, vulnerability=vulnerability)
    hand = Hand.parse(request["hand"])
    selection = choose_bid(profile, auction, hand, environment, request.get("private_memory"))
    return explain(selection)


def system_notes(request: dict) -> dict:
    profile_id = request["profile"]["id"]
    profile = load_profile(profile_id, Path(__file__).resolve().parent)
    return {
        "format": "markdown",
        "profile": {
            "id": profile.id,
            "name": profile.name,
            "version": profile.version,
        },
        "content": generate_system_notes(profile),
    }


def simulate(request: dict) -> dict:
    profile_id = request["profile"]["id"]
    environment = request.get("environment", {})
    dealer = environment.get("dealer", "n")
    vulnerability = environment.get("vulnerability", "none")
    profile = load_profile(profile_id, Path(__file__).resolve().parent)
    simulation = simulate_auction(
        profile,
        request["hands"],
        dealer=dealer,
        vulnerability=vulnerability,
        environment=environment,
        max_calls=request.get("max_calls", 80),
    )
    return {
        "auction": simulation.compact_sequence(),
        "calls": list(simulation.calls),
        "records": [
            {
                "seat": record.seat,
                "call": record.call,
                "explanation": record.explanation,
            }
            for record in simulation.call_records
        ],
        "diagnostics": list(simulation.diagnostics),
        "private_memories": simulation.private_memories,
    }


if __name__ == "__main__":
    sample = {
        "profile": {"id": "meow_2over1"},
        "seat": "n",
        "auction": "1SP2SP",
        "hand": "SKQJT98HA43DA2CAK",
        "environment": {"dealer": "n", "vulnerability": "none", "scoring": "IMP"},
    }
    print(json.dumps(bid(sample), indent=2))
