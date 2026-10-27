"""Balanced 1NT test deals and DDS-based terminal-auction diagnostics.

The class comparison uses exact suit lengths for both partners and at most
two HCP and two K–R points' distance for each hand. DDS is analysis evidence
only: it never supplies a bidder with unseen cards.
"""

from __future__ import annotations

import itertools
import json
import random
import argparse
from collections import Counter
from functools import cache
from pathlib import Path
from typing import Callable, Mapping

from .auction import Auction
from .cards import Hand, SUITS
from .deal_sampler import _hand_from_cards
from .dds_adapter import calculate_available_table
from .hand_quality import assess_quality
from .legality import last_contract_state
from .outcome_metrics import (
    GAME_TARGETS,
    RULE_ID,
    available_level,
    classify_rates,
    game_success_ratio,
    reached_game,
)
from .selector import choose_bid
from .simulator import simulate_auction
from .training_deals import _compact, _deal


RANKS = 'AKQJT98765432'
POINTS = {'A': 4, 'K': 3, 'Q': 2, 'J': 1}
DECK = tuple((suit, rank) for suit in SUITS for rank in RANKS)
# Full-scan responder shapes: rows 1–22 and 24 of the standard
# shape-probability table. Everything from 5-1-7-0 and rarer patterns is
# excluded, while every feasible (longest suit, longest two suits) pair in
# the 4–8 / 7–11 grid remains covered. Scan runs rotate these profiles among
# the named suits.
COVERAGE_SHAPES = (
    (4, 4, 3, 2), (5, 3, 3, 2), (5, 4, 3, 1), (5, 4, 2, 2), (4, 3, 3, 3),
    (6, 3, 2, 2), (6, 4, 2, 1), (6, 3, 3, 1), (5, 5, 2, 1), (4, 4, 4, 1),
    (7, 3, 2, 1), (6, 4, 3, 0), (5, 4, 4, 0), (5, 5, 3, 0), (6, 5, 1, 1),
    (6, 5, 2, 0), (7, 2, 2, 2), (7, 4, 1, 1), (7, 4, 2, 0), (7, 3, 3, 0),
    (8, 2, 2, 1), (8, 3, 1, 1), (8, 3, 2, 0),
)
# North varies by quota cell, while pairs inside one cell hold the same shape
# so their outcomes can be compared as genuinely similar partnership hands.
OPENING_SHAPES = (
    (4, 3, 3, 3), (4, 4, 3, 2), (5, 3, 3, 2),
)


def _sample_hand(rng: random.Random, available: tuple, shape: tuple[int, ...],
                 target_hcp: int) -> tuple | None:
    """Uniformly draw a hand of exact suit lengths and exact HCP, if feasible."""
    if len(shape) != 4 or sum(shape) != 13:
        raise ValueError('shape must contain four suit lengths totaling 13')
    groups = []
    for suit, length in zip(SUITS, shape):
        ranks = tuple(card for card in available if card[0] == suit)
        if length > len(ranks):
            return None
        by_hcp = {}
        for combo in itertools.combinations(ranks, length):
            points = sum(POINTS.get(rank, 0) for _, rank in combo)
            by_hcp.setdefault(points, []).append(combo)
        groups.append(by_hcp)

    @cache
    def count(index: int, remaining: int) -> int:
        if index == 4:
            return int(remaining == 0)
        return sum(len(combos) * count(index + 1, remaining - points)
                   for points, combos in groups[index].items()
                   if points <= remaining)

    if not count(0, target_hcp):
        return None
    cards = []
    remaining = target_hcp
    for index, choices in enumerate(groups):
        total = count(index, remaining)
        draw = rng.randrange(total)
        for points, combos in choices.items():
            future = count(index + 1, remaining - points) if points <= remaining else 0
            weight = len(combos) * future
            if draw < weight:
                cards.extend(combos[draw // future])
                remaining -= points
                break
            draw -= weight
    return tuple(cards)


def sample_partnership(
    rng: random.Random,
    responder_hcp: int,
    responder_shape: tuple[int, int, int, int],
    *,
    opener_eligible: Callable[[Hand], bool],
    opener_shape: tuple[int, int, int, int] | None = None,
    opener_hcp: int | None = None,
    reference: tuple[float, float] | None = None,
    max_tries: int = 2000,
) -> dict[str, Hand]:
    """Deal N/S to quotas, then randomize E/W without leaking them to bidding."""
    if not isinstance(responder_hcp, int) or isinstance(responder_hcp, bool) or not 0 <= responder_hcp <= 22:
        raise ValueError('responder_hcp must be 0..22')
    if opener_shape is not None and opener_hcp is None:
        raise ValueError('opener_shape requires opener_hcp')
    for _ in range(max_tries):
        if opener_shape is None:
            north = _deal(rng)['n']
        else:
            opener_cards = _sample_hand(rng, DECK, opener_shape, opener_hcp)
            if opener_cards is None:
                continue
            north = _hand_from_cards(opener_cards)
        if not 14 <= north.hcp <= 18 or not opener_eligible(north):
            continue
        if reference is not None and abs(hand_kr(north) - reference[0]) > 2:
            continue
        north_cards = {(suit, rank) for suit in SUITS for rank in north.holding(suit)}
        remaining = tuple(card for card in DECK if card not in north_cards)
        south_cards = _sample_hand(rng, remaining, responder_shape, responder_hcp)
        if south_cards is None:
            continue
        south = _hand_from_cards(south_cards)
        if reference is not None and abs(hand_kr(south) - reference[1]) > 2:
            continue
        return complete_opponents(rng, north, south)
    raise RuntimeError(f'could not construct 1NT deal for {responder_hcp} HCP / {responder_shape}')


def complete_opponents(rng: random.Random, north: Hand, south: Hand) -> dict[str, Hand]:
    """Randomly complete E/W while keeping the same N/S hands."""
    used = {(suit, rank) for hand in (north, south) for suit in SUITS
            for rank in hand.holding(suit)}
    remaining = [card for card in DECK if card not in used]
    rng.shuffle(remaining)
    return {'n': north, 'e': _hand_from_cards(remaining[:13]),
            's': south, 'w': _hand_from_cards(remaining[13:])}


def hand_shape(hand: Hand) -> tuple[int, int, int, int]:
    return tuple(hand.length(suit) for suit in SUITS)


def hand_kr(hand: Hand) -> float:
    return assess_quality(hand)['kr_points']


_available_level = available_level
_reached_game = reached_game
wrong_game_rates = game_success_ratio


def classify_suspicious(
    subject: Mapping,
    records: list[Mapping],
    tables: Mapping[int, list[Mapping]],
    *,
    min_boards: int = 10,
    min_pairs: int = 2,
) -> dict:
    """Estimate outcomes within a same-shape class whose full spans are <=2."""
    dimensions = ('north_hcp', 'south_hcp', 'north_kr', 'south_kr')
    candidates = [record for record in records
                  if record['id'] != subject['id']
                  and record['north_shape'] == subject['north_shape']
                  and record['south_shape'] == subject['south_shape']
                  and all(abs(record[key] - subject[key]) <= 2 for key in dimensions)]
    candidates.sort(key=lambda record: (
        max(abs(record[key] - subject[key]) for key in dimensions),
        sum(abs(record[key] - subject[key]) for key in dimensions),
        record['id']))
    neighbors = [subject]
    bounds = {key: [subject[key], subject[key]] for key in dimensions}
    for record in candidates:
        if not all(max(bounds[key][1], record[key]) - min(bounds[key][0], record[key]) <= 2
                   for key in dimensions):
            continue
        neighbors.append(record)
        for key in dimensions:
            bounds[key][0] = min(bounds[key][0], record[key])
            bounds[key][1] = max(bounds[key][1], record[key])
    boards = [table for record in neighbors for table in tables.get(record['id'], ())]
    result = {'status': 'insufficient_data', 'class_pairs': len(neighbors),
              'dds_boards': len(boards), 'flags': [], 'rates': {}}
    if len(neighbors) < min_pairs or len(boards) < min_boards:
        return result
    level = int(subject['contract'][0])
    strain = subject['contract'][1:]
    declarer = subject['declarer']
    counts = {
        'contract_failure': sum(table[strain][declarer] < level + 6 for table in boards),
        'missed_game': sum(available_level(table, 'game') for table in boards),
        'missed_small_slam': sum(available_level(table, 'small_slam') for table in boards),
        'missed_grand_slam': sum(available_level(table, 'grand_slam') for table in boards),
    }
    rates = {name: count / len(boards) for name, count in counts.items()}
    rates['wrong_game'], alternative_rates = game_success_ratio(
        subject['contract'], declarer, boards)
    result.update(status='assessed', rates=rates,
                  alternative_game_rates=alternative_rates)
    result['flags'] = classify_rates(
        subject['contract'], rates, alternative_rates,
        existing_flags=result['flags'],
    )
    return result


def _history(simulation) -> list[dict]:
    history = []
    for record in simulation.call_records:
        selected = ((record.explanation or {}).get('internal_origin') or {}).get('selected') or {}
        history.append({'seat': record.seat, 'call': record.call,
                        'source_id': selected.get('source_id')})
    return history


def _contract(calls: tuple[str, ...], *, dealer: str = 'n',
              vulnerability: str = 'none') -> tuple[str, str]:
    auction = Auction(calls, dealer=dealer, vulnerability=vulnerability)
    state = last_contract_state(auction)
    if state is None:
        raise RuntimeError('completed 1NT auction has no contract')
    strain = state.call[1]
    declarer = next(
        (auction.actor_at(index) for index, call in enumerate(calls)
         if auction.actor_at(index) in 'ns' and len(call) == 2
         and call[0] in '1234567' and call[1] == strain),
        None,
    )
    if declarer is None:
        raise RuntimeError('cannot determine declarer')
    return state.call[0] + ('NT' if strain == 'N' else strain), declarer


def scan_coverage(
    profile,
    *,
    seed: int = 23,
    hcp_targets=tuple(range(23)),
    shapes=COVERAGE_SHAPES,
    pairs_per_cell: int = 2,
    ew_samples: int = 10,
    min_class_boards: int = 10,
    min_class_pairs: int = 2,
    solve_table: Callable = calculate_available_table,
    progress: Callable[[dict, int], None] | None = None,
) -> dict:
    """Cover South HCP/shapes with North 1NT, then evaluate completed auctions.

    Each independent N/S pair is auctioned once; E/W are completed anew for
    each DDS board. Synthetic sampling weights are test coverage, not bridge
    population frequencies.
    """
    if pairs_per_cell < 1 or ew_samples < 1 or min_class_boards < 1 or min_class_pairs < 1:
        raise ValueError('all sampling and class minimum counts must be positive')
    rng = random.Random(seed)
    cells = [(hcp, tuple(shape), index) for hcp in hcp_targets
             for index, shape in enumerate(shapes)]
    rng.shuffle(cells)
    schedule = [(hcp, shape, index, slot) for hcp, shape, index in cells
                for slot in range(pairs_per_cell)]
    empty_auction = Auction.parse('', dealer='n', vulnerability='none')

    def opener_eligible(hand):
        return choose_bid(profile, empty_auction, hand,
                          {'dealer': 'n', 'seat': 'n', 'vulnerability': 'none',
                           'scoring': 'IMP'}).call == '1N'

    cases = []
    complete_cases = []
    limit_cases = []
    class_records = []
    tables_by_id = {}
    points = Counter()
    point_first = {}
    summary = {'pairs': 0, 'complete': 0, 'blocked': 0, 'limit': 0,
               'dds_boards': 0, 'suspicious': 0, 'unassessed': 0}
    observed_hcp = set()
    observed_longest = set()
    observed_top_two = set()
    observed_shapes = set()
    observed_cells = set()
    anchor_quality = {}
    for trial, (hcp, base_shape, shape_index, slot) in enumerate(schedule, 1):
        # Keep the two independent pairs in each quota cell comparable while
        # rotating suit placement and North's 1NT shape across cells.
        rotation = (hcp + shape_index) % 4
        rotated = base_shape[rotation:] + base_shape[:rotation]
        opener_shape = (OPENING_SHAPES[(hcp * len(shapes) + shape_index) % len(OPENING_SHAPES)]
                        if hcp <= 19 else (4, 3, 3, 3))
        opener_hcp = 15 + ((hcp + shape_index) % 3) if hcp <= 19 else 15
        key = (hcp, base_shape)
        try:
            hands = sample_partnership(
                rng, hcp, rotated, opener_eligible=opener_eligible,
                opener_shape=opener_shape, opener_hcp=opener_hcp,
                reference=anchor_quality.get(key) if slot else None,
            )
        except RuntimeError as exc:
            raise RuntimeError(
                f'coverage cell HCP={hcp}, South={rotated}, North={opener_shape}, '
                f'North HCP={opener_hcp}, replicate={slot + 1} failed'
            ) from exc
        if slot == 0:
            anchor_quality[key] = (hand_kr(hands['n']), hand_kr(hands['s']))
        south_shape = hand_shape(hands['s'])
        observed_hcp.add(hcp)
        observed_longest.add(max(south_shape))
        top_two = sum(sorted(south_shape, reverse=True)[:2])
        observed_top_two.add(top_two)
        observed_cells.add((hcp, max(south_shape), top_two))
        observed_shapes.add(south_shape)
        bidding_hands = {seat: hands[seat] for seat in 'ns'}
        simulation = simulate_auction(
            profile, bidding_hands, dealer='n', vulnerability='none',
            environment={'dealer': 'n', 'vulnerability': 'none', 'scoring': 'IMP'},
            max_calls=80,
        )
        if not simulation.calls or simulation.calls[0] != '1N':
            raise RuntimeError('sampled opener did not bid 1NT in the auction')
        summary['pairs'] += 1
        summary[simulation.status] += 1
        case = {
            'id': trial, 'trial': trial, 'stratum': 'coverage', 'dealer': 'n',
            'vulnerability': 'none',
            'hands': {seat: _compact(hand) for seat, hand in hands.items()},
            'north_hcp': hands['n'].hcp, 'south_hcp': hands['s'].hcp,
            'north_kr': hand_kr(hands['n']), 'south_kr': hand_kr(hands['s']),
            'north_shape': hand_shape(hands['n']), 'south_shape': south_shape,
            'calls': list(simulation.calls), 'auction': simulation.compact_sequence(),
            'history': _history(simulation),
            'coverage_cell': {
                'target_hcp': hcp,
                'base_shape_index': shape_index,
                'base_shape': list(base_shape),
                'pair_slot': slot,
            },
        }
        if simulation.status == 'blocked':
            case.update(blocked=simulation.blocked, review_status='unreviewed')
            cases.append(case)
            point = (simulation.blocked['auction'], simulation.blocked['seat'])
            points[point] += 1
            point_first.setdefault(point, trial)
        elif simulation.status == 'complete':
            contract, declarer = _contract(simulation.calls)
            case.update(contract=contract, declarer=declarer)
            class_records.append(case)
            boards = []
            for index in range(ew_samples):
                deal = hands if index == 0 else complete_opponents(rng, hands['n'], hands['s'])
                boards.append(solve_table(deal))
            tables_by_id[trial] = boards
            case['dds_tables'] = boards
            summary['dds_boards'] += len(boards)
            complete_cases.append(case)
        elif simulation.status == 'limit':
            case['status'] = 'limit'
            limit_cases.append(case)
        if progress is not None:
            progress(summary.copy(), len(schedule))

    suspicious_cases = []
    for case in complete_cases:
        analysis = classify_suspicious(case, class_records, tables_by_id,
                                       min_boards=min_class_boards,
                                       min_pairs=min_class_pairs)
        case['analysis'] = analysis
        if analysis['status'] != 'assessed':
            summary['unassessed'] += 1
        if analysis['flags']:
            summary['suspicious'] += 1
            suspicious_cases.append(case)
    return {
        'schema_version': 2,
        'profile': {'id': profile.id, 'name': profile.name, 'version': profile.version},
        'seed': seed,
        'wrong_game_rule': RULE_ID,
        'filters': {'dealer': 'n', 'opening': '1N', 'vulnerability': 'none',
                    'hcp_targets': list(hcp_targets), 'shapes': [list(s) for s in shapes]},
        'budget': {'pairs_per_cell': pairs_per_cell, 'ew_samples': ew_samples,
                   'min_class_boards': min_class_boards,
                   'min_class_pairs': min_class_pairs},
        'coverage': {'responder_hcp': sorted(observed_hcp),
                     'longest_suit': sorted(observed_longest),
                     'top_two_suits': sorted(observed_top_two),
                     'longest_top_two_pairs': [list(pair) for pair in sorted(
                         {(longest, top_two) for _, longest, top_two in observed_cells})],
                     'cells': [list(cell) for cell in sorted(observed_cells)],
                     'exact_shapes': [list(shape) for shape in sorted(observed_shapes)]},
        'summary': summary,
        'block_points': [
            {'auction': auction, 'seat': seat, 'count': count,
             'first_trial': point_first[(auction, seat)],
             'strata': {'coverage': count}}
            for (auction, seat), count in sorted(
                points.items(), key=lambda item: (-item[1], item[0]))
        ],
        'cases': cases,
        'complete_cases': complete_cases,
        'limit_cases': limit_cases,
        'suspicious_cases': suspicious_cases,
        'solver': 'DDS via available adapter',
        'method_note': ('DDS double-dummy completion is a test proxy, not an '
                        'estimate of single-dummy declarer success. Synthetic '
                        'coverage frequencies are not population frequencies.'),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Balanced North-1NT coverage and DDS audit')
    parser.add_argument('--profile', default='daqiush_2over1')
    parser.add_argument('--seed', type=int, default=23)
    parser.add_argument('--pairs-per-cell', type=int, default=2)
    parser.add_argument('--ew-samples', type=int, default=10)
    parser.add_argument('--min-class-boards', type=int, default=10)
    parser.add_argument('--min-class-pairs', type=int, default=2)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    from .loader import load_profile
    report = scan_coverage(
        load_profile(args.profile), seed=args.seed,
        pairs_per_cell=args.pairs_per_cell, ew_samples=args.ew_samples,
        min_class_boards=args.min_class_boards,
        min_class_pairs=args.min_class_pairs,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n',
                           encoding='utf-8')
    print(f"{report['summary']['pairs']} pairs; {report['summary']['blocked']} TD calls; "
          f"{report['summary']['suspicious']} suspicious; "
          f"{report['summary']['dds_boards']} DDS boards. Report: {args.output}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
