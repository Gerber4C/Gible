from __future__ import annotations

import json
from pathlib import Path

from engine.auction import Auction
from engine.cards import Hand
from engine.explanation import explain
from engine.loader import load_convention_set
from engine.selector import choose_bid
from engine.simulator import simulate_auction
from engine.system_notes import generate_system_notes


def bid(request: dict) -> dict:
    convention_set_id = request["convention_set"]["id"]
    environment = request.get("environment", {})
    dealer = environment.get("dealer", "n")
    vulnerability = environment.get("vulnerability", "none")
    convention_set = load_convention_set(convention_set_id, Path(__file__).resolve().parent)
    auction = Auction.parse(request["auction"], dealer=dealer, vulnerability=vulnerability)
    hand = Hand.parse(request["hand"])
    selection = choose_bid(convention_set, auction, hand, environment)
    return explain(selection)


def system_notes(request: dict) -> dict:
    convention_set_id = request["convention_set"]["id"]
    convention_set = load_convention_set(convention_set_id, Path(__file__).resolve().parent)
    return {
        "format": "markdown",
        "convention_set": {
            "id": convention_set.id,
            "name": convention_set.name,
            "version": convention_set.version,
        },
        "content": generate_system_notes(convention_set),
    }


def simulate(request: dict) -> dict:
    convention_set_id = request["convention_set"]["id"]
    environment = request.get("environment", {})
    dealer = environment.get("dealer", "n")
    vulnerability = environment.get("vulnerability", "none")
    convention_set = load_convention_set(convention_set_id, Path(__file__).resolve().parent)
    simulation = simulate_auction(
        convention_set,
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
    }


if __name__ == "__main__":
    sample = {
        "convention_set": {"id": "meow_2over1"},
        "seat": "n",
        "auction": "1SP2SP",
        "hand": "SKQJT98HA43DA2CAK",
        "environment": {"dealer": "n", "vulnerability": "none", "scoring": "IMP"},
    }
    print(json.dumps(bid(sample), indent=2))
