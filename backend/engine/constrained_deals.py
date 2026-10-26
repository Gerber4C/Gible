"""Random complete deals under exact N/S shapes and inclusive HCP/K–R ranges.

Within a hand's constraints, suit combinations are counted by HCP and K–R
twentieths before drawing. This reaches narrow K–R bands without discarding
otherwise valid hands. North is drawn first; South is drawn from the cards
remaining after North, so the joint-pair distribution is not uniform.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
import itertools
import json
import math
from pathlib import Path
import random

from .cards import Hand, RANK_POINTS, SUITS
from .deal_sampler import _hand_from_cards
from .hand_quality import _kr_suit, assess_quality


RANKS = 'AKQJT98765432'
DECK = tuple((suit, rank) for suit in SUITS for rank in RANKS)


@dataclass(frozen=True)
class HandConstraints:
    """S/H/D/C lengths, raw HCP interval, and pure K–R interval."""

    shape: tuple[int, int, int, int]
    hcp: tuple[int, int]
    kr: tuple[float, float]

    def __post_init__(self):
        if (len(self.shape) != 4 or any(isinstance(n, bool) or not isinstance(n, int)
                                         or not 0 <= n <= 13 for n in self.shape)
                or sum(self.shape) != 13):
            raise ValueError('shape must be four S/H/D/C lengths totaling 13')
        if (len(self.hcp) != 2 or any(isinstance(n, bool) or not isinstance(n, int)
                                       or not 0 <= n <= 37 for n in self.hcp)
                or self.hcp[0] > self.hcp[1]):
            raise ValueError('HCP must be an inclusive integer interval within 0..37')
        if (len(self.kr) != 2 or any(isinstance(n, bool) or not isinstance(n, (int, float))
                                      or not math.isfinite(n) for n in self.kr)
                or self.kr[0] > self.kr[1]):
            raise ValueError('K-R must be an inclusive finite numeric interval')


class _HandPlan:
    """Count legal suit combinations, then sample one with those counts."""

    def __init__(self, available: tuple, rule: HandConstraints):
        self.buckets = []
        for suit, length in zip(SUITS, rule.shape):
            suit_cards = tuple(card for card in available if card[0] == suit)
            if length > len(suit_cards):
                raise ValueError('not enough available cards in a required suit')
            groups = defaultdict(list)
            for combo in itertools.combinations(suit_cards, length):
                hcp = sum(RANK_POINTS.get(rank, 0) for _, rank in combo)
                kr_units = _kr_suit(''.join(rank for _, rank in combo))['twentieths']
                groups[(hcp, kr_units)].append(combo)
            self.buckets.append(groups)

        # assess_quality adds -1 point for general shape, or -0.5 for 4333.
        shape_adjustment = -10 if sorted(rule.shape) == [3, 3, 3, 4] else -20
        min_kr = math.ceil(rule.kr[0] * 20 - 1e-8) - shape_adjustment
        max_kr = math.floor(rule.kr[1] * 20 + 1e-8) - shape_adjustment
        self.layers = [{(0, 0): 1}]
        for groups in self.buckets:
            next_layer = defaultdict(int)
            for (hcp, kr_units), count in self.layers[-1].items():
                for (add_hcp, add_kr), combos in groups.items():
                    if hcp + add_hcp <= rule.hcp[1] and kr_units + add_kr <= max_kr:
                        next_layer[(hcp + add_hcp, kr_units + add_kr)] += count * len(combos)
            self.layers.append(next_layer)
        self.targets = [(state, count) for state, count in self.layers[-1].items()
                        if rule.hcp[0] <= state[0] <= rule.hcp[1]
                        and min_kr <= state[1] <= max_kr]
        self.total = sum(count for _, count in self.targets)
        if not self.total:
            raise ValueError('no hand satisfies the shape, HCP, and K-R ranges')

    def sample(self, rng: random.Random) -> tuple:
        draw = rng.randrange(self.total)
        for state, count in self.targets:
            if draw < count:
                target = state
                break
            draw -= count
        cards = []
        for index in range(3, -1, -1):
            options = []
            total = 0
            for (hcp, kr_units), combos in self.buckets[index].items():
                previous = (target[0] - hcp, target[1] - kr_units)
                weight = self.layers[index].get(previous, 0) * len(combos)
                if weight:
                    options.append((previous, combos, weight))
                    total += weight
            draw = rng.randrange(total)
            for previous, combos, weight in options:
                if draw < weight:
                    cards.extend(combos[draw // self.layers[index][previous]])
                    target = previous
                    break
                draw -= weight
        return tuple(cards)


class ConstrainedDealSampler:
    """Draw full deals while both named N/S hands meet their own constraints."""

    def __init__(self, north: HandConstraints, south: HandConstraints, *,
                 seed: int | None = None, max_tries: int = 1000):
        if any(a + b > 13 for a, b in zip(north.shape, south.shape)):
            raise ValueError('North and South require more than 13 cards in a suit')
        if north.hcp[0] + south.hcp[0] > 40:
            raise ValueError('North and South minimum HCP cannot total more than 40')
        if not isinstance(max_tries, int) or max_tries < 1:
            raise ValueError('max_tries must be a positive integer')
        self.north = north
        self.south = south
        self.seed = seed
        self.rng = random.Random(seed)
        self.max_tries = max_tries
        self.north_plan = _HandPlan(DECK, north)

    def deal(self) -> dict[str, Hand]:
        for _ in range(self.max_tries):
            north_cards = self.north_plan.sample(self.rng)
            north_set = set(north_cards)
            remaining = tuple(card for card in DECK if card not in north_set)
            try:
                south_cards = _HandPlan(remaining, self.south).sample(self.rng)
            except ValueError:
                continue
            south_set = set(south_cards)
            rest = [card for card in remaining if card not in south_set]
            self.rng.shuffle(rest)
            return {'n': _hand_from_cards(north_cards),
                    'e': _hand_from_cards(rest[:13]),
                    's': _hand_from_cards(south_cards),
                    'w': _hand_from_cards(rest[13:])}
        raise RuntimeError(f'could not satisfy both hands after {self.max_tries} North draws; '
                           'the joint constraints may be impossible or too narrow')

    def sample(self, count: int) -> list[dict[str, Hand]]:
        if not isinstance(count, int) or isinstance(count, bool) or count < 1:
            raise ValueError('count must be a positive integer')
        return [self.deal() for _ in range(count)]


def bid_constrained_deals(sampler: ConstrainedDealSampler, profile, count: int, *,
                          dealer: str = 'n', vulnerability: str = 'none',
                          max_calls: int = 80) -> dict:
    """Generate constrained deals and run N/S bidding with E/W passing."""
    if not isinstance(count, int) or isinstance(count, bool) or count < 1:
        raise ValueError('count must be a positive integer')
    if dealer not in 'nesw':
        raise ValueError('dealer must be n, e, s, or w')
    if max_calls < 4:
        raise ValueError('max_calls must be at least 4')
    from .auction import Auction
    from .coverage_scan import _contract, _history
    from .legality import last_contract_state
    from .simulator import simulate_auction

    summary = {'pairs': 0, 'complete': 0, 'blocked': 0, 'limit': 0,
               'suspicious': 0, 'unassessed': 0, 'dds_boards': 0}
    blocked_cases = []
    complete_cases = []
    limit_cases = []
    points = Counter()
    first_trials = {}
    for trial in range(1, count + 1):
        hands = sampler.deal()
        simulation = simulate_auction(
            profile, {seat: hands[seat] for seat in 'ns'}, dealer=dealer,
            vulnerability=vulnerability,
            environment={'dealer': dealer, 'vulnerability': vulnerability,
                         'scoring': 'IMP'}, max_calls=max_calls,
        )
        summary['pairs'] += 1
        summary[simulation.status] += 1
        case = {
            'id': trial, 'trial': trial, 'stratum': 'constrained',
            'dealer': dealer, 'vulnerability': vulnerability,
            'hands': {seat: _compact(hand) for seat, hand in hands.items()},
            'north_hcp': hands['n'].hcp, 'south_hcp': hands['s'].hcp,
            'north_kr': assess_quality(hands['n'])['kr_points'],
            'south_kr': assess_quality(hands['s'])['kr_points'],
            'north_shape': list(sampler.north.shape),
            'south_shape': list(sampler.south.shape),
            'calls': list(simulation.calls),
            'auction': simulation.compact_sequence(),
            'history': _history(simulation), 'status': simulation.status,
        }
        if simulation.status == 'blocked':
            case['blocked'] = simulation.blocked
            blocked_cases.append(case)
            point = (simulation.blocked['auction'], simulation.blocked['seat'])
            points[point] += 1
            first_trials.setdefault(point, trial)
        elif simulation.status == 'complete':
            auction = Auction(simulation.calls, dealer=dealer,
                              vulnerability=vulnerability)
            if last_contract_state(auction) is None:
                case.update(contract=None, declarer=None)
            else:
                contract, declarer = _contract(simulation.calls, dealer=dealer,
                                               vulnerability=vulnerability)
                case.update(contract=contract, declarer=declarer)
            complete_cases.append(case)
        else:
            case['diagnostics'] = list(simulation.diagnostics)
            limit_cases.append(case)

    return {
        'schema_version': 2,
        'profile': {'id': profile.id, 'name': profile.name,
                    'version': profile.version},
        'seed': sampler.seed,
        'constraints': {'north': vars(sampler.north),
                        'south': vars(sampler.south)},
        'filters': {'mode': 'constrained', 'dealer': dealer,
                    'vulnerability': vulnerability, 'opening': None},
        'budget': {'count': count, 'max_calls': max_calls,
                   'max_tries': sampler.max_tries},
        'summary': summary,
        'block_points': [
            {'auction': auction, 'seat': seat, 'count': number,
             'first_trial': first_trials[(auction, seat)],
             'strata': {'constrained': number}}
            for (auction, seat), number in sorted(
                points.items(), key=lambda item: (-item[1], item[0]))
        ],
        'cases': blocked_cases,
        'complete_cases': complete_cases,
        'limit_cases': limit_cases,
        'suspicious_cases': [],
        'method_note': 'N/S auto-bid using their own hands; E/W Pass. No DDS analysis.',
    }


def _shape_arg(value: str) -> tuple[int, int, int, int]:
    try:
        shape = tuple(int(part) for part in value.split(','))
    except ValueError as exc:
        raise argparse.ArgumentTypeError('shape must be S,H,D,C lengths') from exc
    if len(shape) != 4:
        raise argparse.ArgumentTypeError('shape must be S,H,D,C lengths')
    return shape


def _range_arg(value: str, numeric_type):
    try:
        return tuple(numeric_type(part) for part in value.split(':'))
    except ValueError as exc:
        raise argparse.ArgumentTypeError('range must be lower:upper') from exc


def _compact(hand: Hand) -> str:
    return ''.join(code + (hand.holding(suit) or '-') for code, suit in zip('SHDC', SUITS))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Deal exact N/S shapes inside HCP and K-R ranges')
    for seat in ('north', 'south'):
        parser.add_argument(f'--{seat}-shape', type=_shape_arg, required=True,
                            help='four S,H,D,C lengths, e.g. 4,3,3,3')
        parser.add_argument(f'--{seat}-hcp', type=lambda v: _range_arg(v, int), required=True,
                            help='inclusive raw HCP lower:upper')
        parser.add_argument(f'--{seat}-kr', type=lambda v: _range_arg(v, float), required=True,
                            help='inclusive pure K-R lower:upper')
    parser.add_argument('--count', type=int, default=100)
    parser.add_argument('--seed', type=int, default=23)
    parser.add_argument('--max-tries', type=int, default=1000)
    parser.add_argument('--profile', default='daqiush_2over1')
    parser.add_argument('--dealer', choices='nesw', default='n')
    parser.add_argument('--vulnerability', choices=('none', 'ns', 'ew', 'both'),
                        default='none')
    parser.add_argument('--max-calls', type=int, default=80)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    north = HandConstraints(args.north_shape, args.north_hcp, args.north_kr)
    south = HandConstraints(args.south_shape, args.south_hcp, args.south_kr)
    sampler = ConstrainedDealSampler(north, south, seed=args.seed,
                                     max_tries=args.max_tries)
    from .loader import load_profile
    from .block_report_viewer import render_html
    payload = bid_constrained_deals(
        sampler, load_profile(args.profile), args.count, dealer=args.dealer,
        vulnerability=args.vulnerability, max_calls=args.max_calls,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n',
                           encoding='utf-8')
    html_output = args.output.with_suffix('.html')
    html_output.write_text(render_html(payload), encoding='utf-8')
    print(f"{payload['summary']['pairs']} deals, {payload['summary']['complete']} "
          f"complete, {payload['summary']['blocked']} blocked; "
          f"report: {args.output}; viewer: {html_output}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
