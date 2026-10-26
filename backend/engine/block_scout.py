"""Find reproducible blocked auctions in random, filtered full deals.

The scanner holds all four hands, but the bidding simulator receives only the
chosen partnership. The opponents therefore pass, just as in Table training.
It records evidence for later review; it never changes a profile or invents a
call to move past a block.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import time
from collections import Counter
from pathlib import Path
from typing import Mapping

from .auction import Auction
from .calls import is_contract_bid, normalize_call
from .deal_sampler import _matches, _normalize_constraints
from .loader import load_profile
from .model import PartnershipProfile
from .selector import choose_bid
from .simulator import simulate_auction
from .stratified_deals import HcpPairSampler
from .training_deals import PARTNER, SEATS, _compact, _deal


DEALER_CHOICES = {'ns': 'ns', 'ew': 'ew', 'random': SEATS}
VULNERABILITIES = ('none', 'ns', 'ew', 'both')
MAX_ATTEMPTS = 100000
MAX_SECONDS = 3600


def _integer(value: object, name: str, low: int, high: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not low <= value <= high:
        raise ValueError(f'{name} must be an integer from {low} to {high}')
    return value


def _history(simulation) -> list[dict]:
    history = []
    for record in simulation.call_records:
        explanation = record.explanation or {}
        origin = (explanation.get('internal_origin') or {}).get('selected') or {}
        public = (explanation.get('public_meaning') or {}).get('meaning') or {}
        history.append({
            'seat': record.seat, 'call': record.call,
            'source_id': origin.get('source_id'),
            'action': public.get('action') or public.get('action_type'),
        })
    return history


def scan_blocks(
    profile: PartnershipProfile,
    *,
    attempts: int = 1000,
    dealer: str = 'ns',
    vulnerability: str = 'none',
    opening: str | None = None,
    response: str | None = None,
    hand_constraints: Mapping | None = None,
    seed: int | None = None,
    max_seconds: float = 30,
    max_cases: int = 100,
    max_calls: int = 80,
    rare_hcp: Mapping | None = None,
) -> dict:
    """Search complete deals and return all block counts plus bounded examples.

    ``opening`` is the selected first call. ``response`` is the selected third
    call after the right-hand opponent passes. Seat constraints use the same
    min/max HCP and suit-length vocabulary as ``sample_deals``.
    """
    _integer(attempts, 'attempts', 1, MAX_ATTEMPTS)
    _integer(max_cases, 'max_cases', 0, MAX_ATTEMPTS)
    _integer(max_calls, 'max_calls', 1, 200)
    if isinstance(seed, bool) or (seed is not None and not isinstance(seed, int)):
        raise ValueError('seed must be an integer')
    if (isinstance(max_seconds, bool) or not isinstance(max_seconds, (int, float))
            or not 0 < max_seconds <= MAX_SECONDS):
        raise ValueError(f'max_seconds must be positive and at most {MAX_SECONDS}')
    if dealer not in (*SEATS, *DEALER_CHOICES):
        raise ValueError('dealer must be n, e, s, w, ns, ew, or random')
    if vulnerability not in VULNERABILITIES:
        raise ValueError('invalid vulnerability')
    if response is not None and opening is None:
        raise ValueError('response requires an opening filter')
    if response is not None and max_calls < 3:
        raise ValueError('max_calls must be at least 3 when filtering by response')
    opening = normalize_call(opening) if opening is not None else None
    response = normalize_call(response) if response is not None else None
    if opening is not None and not is_contract_bid(opening):
        raise ValueError('opening must be a contract bid')
    bounds = _normalize_constraints(hand_constraints)

    rare_sampler = None
    normalized_rare = None
    if rare_hcp is not None:
        if not isinstance(rare_hcp, Mapping) or set(rare_hcp) != {'share', 'opener', 'responder'}:
            raise ValueError('rare_hcp requires share, opener, and responder')
        share = rare_hcp['share']
        if (isinstance(share, bool) or not isinstance(share, (int, float))
                or not math.isfinite(share) or not 0 < share <= 1):
            raise ValueError('rare_hcp share must be greater than 0 and at most 1')
        rare_sampler = HcpPairSampler(rare_hcp['opener'], rare_hcp['responder'])
        normalized_rare = {'share': share,
                           'opener': list(rare_sampler.opener_hcp),
                           'responder': list(rare_sampler.responder_hcp)}

    chosen_seed = random.SystemRandom().randrange(2**63) if seed is None else seed
    rng = random.Random(chosen_seed)
    rare_attempts = round(attempts * normalized_rare['share']) if normalized_rare else 0
    schedule = ['rare_hcp'] * rare_attempts + ['natural'] * (attempts - rare_attempts)
    rng.shuffle(schedule)
    deadline = time.monotonic() + max_seconds
    summary = {'attempts': 0, 'hand_matches': 0, 'opening_matches': 0,
               'auction_matches': 0, 'complete': 0, 'blocked': 0, 'limit': 0,
               'strata': {label: {'attempts': 0, 'hand_matches': 0,
                                  'opening_matches': 0, 'auction_matches': 0,
                                  'complete': 0, 'blocked': 0, 'limit': 0}
                          for label in (('natural', 'rare_hcp') if rare_sampler else ('natural',))}}
    cases = []
    points = Counter()
    point_strata = Counter()
    first_trials = {}
    while summary['attempts'] < attempts and time.monotonic() < deadline:
        summary['attempts'] += 1
        trial = summary['attempts']
        stratum = schedule[trial - 1]
        stratum_summary = summary['strata'][stratum]
        stratum_summary['attempts'] += 1
        chosen_dealer = rng.choice(DEALER_CHOICES[dealer]) if dealer in DEALER_CHOICES else dealer
        hands = (rare_sampler.deal(rng, chosen_dealer) if stratum == 'rare_hcp'
                 else _deal(rng))
        if not all(_matches(hands[seat], bounds[seat]) for seat in SEATS):
            continue
        summary['hand_matches'] += 1
        stratum_summary['hand_matches'] += 1
        environment = {'dealer': chosen_dealer, 'vulnerability': vulnerability,
                       'scoring': 'IMP'}
        if opening is not None:
            before = Auction.parse('', dealer=chosen_dealer, vulnerability=vulnerability)
            if choose_bid(profile, before, hands[chosen_dealer], environment).call != opening:
                continue
        summary['opening_matches'] += 1
        stratum_summary['opening_matches'] += 1
        if response is not None:
            after = Auction.parse((opening, 'P'), dealer=chosen_dealer,
                                  vulnerability=vulnerability)
            partner = PARTNER[chosen_dealer]
            if choose_bid(profile, after, hands[partner], environment).call != response:
                continue
        summary['auction_matches'] += 1
        stratum_summary['auction_matches'] += 1

        bidding_hands = {seat: hands[seat] for seat in (chosen_dealer, PARTNER[chosen_dealer])}
        result = simulate_auction(profile, bidding_hands, dealer=chosen_dealer,
                                  vulnerability=vulnerability,
                                  environment=environment, max_calls=max_calls)
        if opening is not None and (not result.calls or result.calls[0] != opening):
            raise RuntimeError('opening filter and auction simulation disagreed')
        if response is not None and result.calls[:3] != (opening, 'P', response):
            raise RuntimeError('response filter and auction simulation disagreed')
        summary[result.status] += 1
        stratum_summary[result.status] += 1
        if result.status != 'blocked':
            continue
        block = result.blocked
        point = (block['auction'], block['seat'])
        points[point] += 1
        point_strata[(point, stratum)] += 1
        first_trials.setdefault(point, trial)
        if len(cases) < max_cases:
            cases.append({
                'trial': trial, 'stratum': stratum, 'dealer': chosen_dealer,
                'vulnerability': vulnerability,
                'hands': {seat: _compact(hand) for seat, hand in hands.items()},
                'calls': list(result.calls), 'auction': result.compact_sequence(),
                'history': _history(result), 'blocked': block,
                'review_status': 'unreviewed',
            })

    return {
        'schema_version': 1,
        'profile': {'id': profile.id, 'name': profile.name, 'version': profile.version},
        'seed': chosen_seed,
        'filters': {'dealer': dealer, 'vulnerability': vulnerability,
                    'opening': opening, 'response': response,
                    'hand_constraints': bounds, 'rare_hcp': normalized_rare},
        'budget': {'attempts': attempts, 'max_seconds': max_seconds,
                   'max_cases': max_cases, 'max_calls': max_calls},
        'termination': 'attempt_limit' if summary['attempts'] == attempts else 'time_limit',
        'summary': summary,
        'block_points': [
            {'auction': auction, 'seat': seat, 'count': count,
             'first_trial': first_trials[(auction, seat)],
             'strata': {label: point_strata[((auction, seat), label)]
                        for label in summary['strata']}}
            for (auction, seat), count in sorted(
                points.items(), key=lambda item: (-item[1], item[0]))
        ],
        'cases': cases,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Find blocked Gible auctions in filtered random deals.')
    parser.add_argument('--profile', default='daqiush_2over1')
    parser.add_argument('--dealer', default='ns', choices=(*SEATS, *DEALER_CHOICES))
    parser.add_argument('--vulnerability', default='none', choices=VULNERABILITIES)
    parser.add_argument('--opening', help='selected first call, e.g. 1NT')
    parser.add_argument('--response', help='selected response after opponent Pass, e.g. 2C')
    parser.add_argument('--constraints', type=Path, help='JSON file of per-seat HCP/suit-length bounds')
    parser.add_argument('--attempts', type=int, default=1000)
    parser.add_argument('--max-seconds', type=float, default=30)
    parser.add_argument('--max-cases', type=int, default=100)
    parser.add_argument('--max-calls', type=int, default=80)
    parser.add_argument('--seed', type=int)
    parser.add_argument('--rare-share', type=float,
                        help='share of attempted deals generated in the high-HCP stratum')
    parser.add_argument('--rare-opener-hcp',
                        help='inclusive opener HCP range, e.g. 15:17')
    parser.add_argument('--rare-responder-hcp',
                        help='inclusive responder HCP range, e.g. 20:22')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    rare_flags = (args.rare_share, args.rare_opener_hcp, args.rare_responder_hcp)
    if any(item is not None for item in rare_flags) and any(item is None for item in rare_flags):
        parser.error('rare sampling requires --rare-share, --rare-opener-hcp, and --rare-responder-hcp')
    def parse_range(text):
        try:
            low, high = text.split(':')
            return int(low), int(high)
        except (ValueError, AttributeError) as exc:
            parser.error(f'invalid HCP range {text!r}; use MIN:MAX')
            raise AssertionError('unreachable') from exc
    rare = ({'share': args.rare_share,
             'opener': parse_range(args.rare_opener_hcp),
             'responder': parse_range(args.rare_responder_hcp)}
            if args.rare_share is not None else None)
    constraints = (json.loads(args.constraints.read_text(encoding='utf-8'))
                   if args.constraints else None)
    profile = load_profile(args.profile)
    report = scan_blocks(profile, attempts=args.attempts, dealer=args.dealer,
                         vulnerability=args.vulnerability, opening=args.opening,
                         response=args.response, hand_constraints=constraints,
                         seed=args.seed, max_seconds=args.max_seconds,
                         max_cases=args.max_cases, max_calls=args.max_calls,
                         rare_hcp=rare)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n',
                           encoding='utf-8')
    summary = report['summary']
    print(f"{summary['attempts']} dealt; {summary['auction_matches']} matched; "
          f"{summary['blocked']} blocked at {len(report['block_points'])} points. "
          f'Report: {args.output}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
