from __future__ import annotations

import json
from pathlib import Path

from engine.auction import Auction
from engine.cards import Hand
from engine.calls import ContractBid
from engine.contract_evaluation import ContractTarget, compare_contract_targets
from engine.route_evaluation import compare_authored_routes
from engine.dds_adapter import available_solver_info, calculate_available_table
from engine.deal_sampler import SamplingExhausted, sample_deals
from engine.explanation import explain
from engine.legality import SIDE_BY_SEAT, auction_is_complete, illegal_calls_in_auction, last_contract_state
from engine.loader import load_profile
from engine.public_evidence import derive_public_evidence
from engine.replay import replay_auction
from engine.matcher import matches_context
from engine.calls import normalize_call
from engine.selector import choose_bid
from engine.simulator import simulate_auction
from engine.system_notes import generate_system_notes
from engine.training_deals import generate_training_deal


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
        "status": simulation.status,
        "blocked": simulation.blocked,
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


def training_deal(request: dict) -> dict:
    profile_id = request['profile']['id']
    profile = load_profile(profile_id, Path(__file__).resolve().parent)
    return generate_training_deal(
        profile,
        opening=request['opening'],
        response=request.get('response'),
        opener=request.get('opener', 'ns'),
        vulnerability=request.get('vulnerability', 'none'),
        seed=request.get('seed'),
        max_attempts=request.get('max_attempts', 2000),
    )


def contract_analysis(request: dict, *, solve_table=None) -> dict:
    """Analyze explicit contract targets using only an actor hand and public calls.

    This endpoint never receives a full Table deal and never creates a bidding
    candidate. The target list is supplied for review, not chosen by Gible.
    """
    allowed = {'profile', 'auction', 'dealer', 'vulnerability', 'seat', 'hand',
               'seed', 'sample_count', 'max_attempts', 'targets'}
    unexpected = set(request) - allowed
    if unexpected:
        raise ValueError('Unsupported analysis field: ' + ', '.join(sorted(unexpected)))
    profile_id = request['profile']['id']
    profile = load_profile(profile_id, Path(__file__).resolve().parent)
    auction = Auction.parse(request['auction'], dealer=request.get('dealer', 'n'),
                            vulnerability=request.get('vulnerability', 'none'))
    if illegal_calls_in_auction(auction):
        raise ValueError('Auction contains an illegal call')
    if auction_is_complete(auction):
        raise ValueError('Cannot analyze a completed auction as the next bidder')
    seat = request['seat']
    if seat != auction.actor_to_call:
        raise ValueError('The acting seat must be next to call in the auction')
    hand = Hand.parse(request['hand'])
    hand.validate(validate_count=True)
    raw_targets = request['targets']
    if not isinstance(raw_targets, list) or not 1 <= len(raw_targets) <= 8:
        raise ValueError('Provide between one and eight explicit analysis targets')
    targets = []
    current = last_contract_state(auction)
    public_calls = replay_auction(profile, auction).applied_meanings
    for item in raw_targets:
        if not isinstance(item, dict) or set(item) != {'level', 'strain', 'declarer'}:
            raise ValueError('Each target needs level, strain and declarer')
        target = ContractTarget(**item)
        if SIDE_BY_SEAT[target.declarer] != SIDE_BY_SEAT[seat]:
            raise ValueError('Target declarer must belong to the acting partnership')
        natural_denom = 'N' if target.strain == 'NT' else target.strain
        first_natural = next((entry['seat'] for entry in public_calls
                              if SIDE_BY_SEAT[entry['seat']] == SIDE_BY_SEAT[seat]
                              and entry['call'][0] in '1234567'
                              and entry['call'][1] == natural_denom
                              and 'natural' in entry['public_meaning'].get('nature_labels', ())), None)
        if first_natural is not None and target.declarer != first_natural:
            raise ValueError(f'Target declarer for {target.strain} must be {first_natural.upper()}')
        if current is not None and ContractBid.parse(target.contract).rank < ContractBid.parse(current.call).rank:
            raise ValueError('Target contract cannot be below the current contract')
        if current is not None and target.contract == current.call and current.side != SIDE_BY_SEAT[seat]:
            raise ValueError('Opponent contract cannot be our target at the same level')
        targets.append(target)
    evidence = derive_public_evidence(profile, auction)
    samples = sample_deals(seat, hand, public_evidence=evidence,
                           sample_count=request.get('sample_count', 10),
                           seed=request.get('seed'),
                           max_attempts=request.get('max_attempts', 5000))
    estimates = compare_contract_targets(samples.deals, targets,
                                         solve_table=solve_table or calculate_available_table)
    return {
        'mode': 'analysis_only', 'profile': profile.id,
        'auction': auction.compact_sequence(), 'acting_seat': seat,
        'public_evidence': list(evidence.labels),
        'sample_count': len(samples.deals), 'attempts': samples.attempts,
        'seed': samples.seed,
        'estimates': [estimate.to_dict() for estimate in estimates],
    }


def route_analysis(request: dict, *, solve_table=None) -> dict:
    """Compare authored first-response routes on paired hypothetical deals."""
    allowed = {'profile', 'auction', 'dealer', 'vulnerability', 'seat', 'hand',
               'seed', 'sample_count', 'max_attempts', 'first_calls'}
    unexpected = set(request) - allowed
    if unexpected:
        raise ValueError('Unsupported route analysis field: ' + ', '.join(sorted(unexpected)))
    profile = load_profile(request['profile']['id'], Path(__file__).resolve().parent)
    auction = Auction.parse(request['auction'], dealer=request.get('dealer', 'n'),
                            vulnerability=request.get('vulnerability', 'none'))
    if auction.calls != ('1N', 'P'):
        raise ValueError('This first experiment supports only the first response to 1NT')
    if request['seat'] != auction.actor_to_call:
        raise ValueError('The acting seat must be next to call')
    hand = Hand.parse(request['hand'])
    hand.validate(validate_count=True)
    raw_calls = request.get('first_calls')
    if not isinstance(raw_calls, list) or not 1 <= len(raw_calls) <= 3:
        raise ValueError('Provide one to three first_calls')
    try:
        first_calls = [normalize_call(call) for call in raw_calls]
    except (TypeError, ValueError) as exc:
        raise ValueError('Invalid first call') from exc
    if len(set(first_calls)) != len(first_calls):
        raise ValueError('first_calls must be distinct')
    for call in first_calls:
        if not any(spec.call == call and not spec.default_policy
                   and matches_context(spec.context, auction)
                   for spec in profile.call_specifications):
            raise ValueError(f'No authored route starts with {call} here')
    sample_count = request.get('sample_count', 8)
    if isinstance(sample_count, bool) or not isinstance(sample_count, int) or not 1 <= sample_count <= 20:
        raise ValueError('sample_count must be from 1 to 20 for route experiments')
    evidence = derive_public_evidence(profile, auction)
    try:
        samples = sample_deals(request['seat'], hand, public_evidence=evidence,
                               sample_count=sample_count, seed=request.get('seed'),
                               max_attempts=request.get('max_attempts', 5000))
    except SamplingExhausted as exc:
        raise ValueError(str(exc)) from exc
    routes = compare_authored_routes(profile, auction, hand, samples.deals,
                                     first_calls,
                                     solve_table=solve_table or calculate_available_table)
    return {
        'mode': 'route_experiment', 'profile': profile.id,
        'profile_version': profile.version,
        'auction': auction.compact_sequence(), 'dealer': auction.dealer,
        'vulnerability': auction.vulnerability, 'acting_seat': request['seat'],
        'opponent_model': 'pass', 'solver':
            available_solver_info() if solve_table is None else
            {'package': 'injected', 'version': None},
        'public_evidence': list(evidence.labels),
        'sample_count': len(samples.deals), 'attempts': samples.attempts,
        'seed': samples.seed, 'routes': list(routes),
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
