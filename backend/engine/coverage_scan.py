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
from types import SimpleNamespace
from typing import Callable, Mapping

from .auction import Auction
from .cards import Hand, SUITS
from .deal_sampler import _hand_from_cards
from .dds_adapter import calculate_available_table
from .hand_quality import assess_quality
from .joint_deal_sampler import (
    JointConstraintError,
    JointPartnershipPlan,
    OpenerModeConstraints,
    sample_conditioned_partnership,
)
from .legality import last_contract_state
from .opener_coverage import (
    REQUIRED_CELLS,
    allocate_opener_strata,
    build_north_summary,
    rotate_responder_shape,
)
from .outcome_metrics import (
    RULE_ID,
    assess_auction_groups,
    available_level,
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


def _opening_assessment(profile):
    """Return the authored ``opening_assessment`` predicate, or None."""
    for item in profile.all_evaluator_specs:
        if item.id == 'opening_assessment':
            definition = item.definition

            def assess(hand):
                return definition(SimpleNamespace(
                    hand=hand, hand_quality=assess_quality(hand)))

            return assess
    return None


def _has_explicit_opener_coverage(profile) -> bool:
    return _opening_assessment(profile) is not None


def _south_cell_records(hcp_targets, shapes):
    return [
        {'target_hcp': hcp, 'base_shape_index': index,
         'base_shape': list(shape)}
        for hcp in hcp_targets
        for index, shape in enumerate(shapes)
    ]


def build_coverage_schedule(hcp_targets, shapes, pairs_per_cell: int) -> dict:
    """Build the seed-independent opener-stratum schedule without drawing."""
    cells = _south_cell_records(hcp_targets, shapes)
    allocation = allocate_opener_strata(cells)
    assignments = dict(allocation['assignments'])
    entries = []
    for cell in cells:
        identity = (cell['target_hcp'], cell['base_shape_index'])
        stratum = assignments[identity]
        for slot in range(pairs_per_cell):
            entries.append({
                'target_hcp': identity[0],
                'base_shape_index': identity[1],
                'base_shape': cell['base_shape'],
                'pair_slot': slot,
                'opener_shape': list(stratum.shape),
                'opener_mode': stratum.mode,
            })
    return {'entries': entries, **allocation}



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


def _envelope(minimum, maximum, slot):
    if slot == 0 or minimum is None or maximum is None:
        return (0.0, 37.0)
    return (max(0.0, maximum - 2), min(37.0, minimum + 2))


def scan_coverage(
    profile,
    *,
    seed: int = 23,
    hcp_targets=tuple(range(23)),
    shapes=COVERAGE_SHAPES,
    pairs_per_cell: int = 2,
    ew_samples: int = 10,
    min_class_boards: int = 10,
    min_class_pairs: int = 1,
    solve_table: Callable = calculate_available_table,
    progress: Callable[[dict, int], None] | None = None,
) -> dict:
    """Cover the complete Daqiush 1NT opener space and South quota cells."""
    if pairs_per_cell < 1 or ew_samples < 1 or min_class_boards < 1 or min_class_pairs < 1:
        raise ValueError('all sampling and class minimum counts must be positive')

    rng = random.Random(seed)
    south_records = _south_cell_records(hcp_targets, shapes)
    explicit = _has_explicit_opener_coverage(profile)
    allocation = allocate_opener_strata(south_records) if explicit else None
    assignments = dict(allocation['assignments']) if explicit else {}
    rng.shuffle(south_records)
    schedule = []
    for cell in south_records:
        identity = (cell['target_hcp'], cell['base_shape_index'])
        stratum = assignments.get(identity) if explicit else None
        for slot in range(pairs_per_cell):
            schedule.append((cell, stratum, slot))

    empty_auction = Auction.parse('', dealer='n', vulnerability='none')

    def opener_eligible(hand):
        return choose_bid(profile, empty_auction, hand,
                          {'dealer': 'n', 'seat': 'n', 'vulnerability': 'none',
                           'scoring': 'IMP'}).call == '1N'

    opening_assessment = _opening_assessment(profile) if explicit else None

    cases = []
    complete_cases = []
    limit_cases = []
    points = Counter()
    point_first = {}
    summary = {'pairs': 0, 'complete': 0, 'blocked': 0, 'limit': 0,
               'dds_boards': 0, 'suspicious': 0, 'unassessed': 0,
               'generation_errors': 0}
    observed_hcp = set()
    observed_longest = set()
    observed_top_two = set()
    observed_shapes = set()
    observed_cells = set()
    anchor_quality = {}
    north_min = {}
    north_max = {}
    south_min = {}
    south_max = {}
    generated_pairs = Counter()
    north_hcp_by_mode = {'normal': set(), 'upgrade_14': set(), 'soft_18': set()}
    cell_failures = []
    failed_cells = set()

    for trial, (cell, stratum, slot) in enumerate(schedule, 1):
        hcp = cell['target_hcp']
        shape_index = cell['base_shape_index']
        base_shape = tuple(cell['base_shape'])
        identity = (hcp, shape_index)
        key = (hcp, base_shape)
        if identity in failed_cells:
            continue
        rotated = rotate_responder_shape(base_shape, hcp, shape_index)
        try:
            if explicit:
                nk_min, nk_max = _envelope(
                    north_min.get(identity), north_max.get(identity), slot)
                sk_min, sk_max = _envelope(
                    south_min.get(identity), south_max.get(identity), slot)
                plan = JointPartnershipPlan(
                    OpenerModeConstraints(stratum.shape, stratum.mode,
                                          (nk_min, nk_max)),
                    rotated, hcp, (sk_min, sk_max))
                hands = sample_conditioned_partnership(
                    plan, rng=rng, opening_assessment=opening_assessment,
                    complete_opponents=complete_opponents)
                n_kr = hand_kr(hands['n'])
                s_kr = hand_kr(hands['s'])
                north_min[identity] = min(north_min.get(identity, n_kr), n_kr)
                north_max[identity] = max(north_max.get(identity, n_kr), n_kr)
                south_min[identity] = min(south_min.get(identity, s_kr), s_kr)
                south_max[identity] = max(south_max.get(identity, s_kr), s_kr)
                north_hcp_by_mode[stratum.mode].add(hands['n'].hcp)
                opener_shape = stratum.shape
                opener_mode = stratum.mode
            else:
                opener_shape = (OPENING_SHAPES[(hcp * len(shapes) + shape_index)
                                               % len(OPENING_SHAPES)]
                                if hcp <= 19 else (4, 3, 3, 3))
                opener_hcp = 15 + ((hcp + shape_index) % 3) if hcp <= 19 else 15
                hands = sample_partnership(
                    rng, hcp, rotated, opener_eligible=opener_eligible,
                    opener_shape=opener_shape, opener_hcp=opener_hcp,
                    reference=anchor_quality.get(key) if slot else None,
                )
                opener_mode = None
                if slot == 0:
                    anchor_quality[key] = (hand_kr(hands['n']), hand_kr(hands['s']))
            generated_pairs[identity] += 1
        except (JointConstraintError, RuntimeError) as exc:
            failed_cells.add(identity)
            summary['generation_errors'] += 1
            cell_failures.append({
                'shape': list(stratum.shape) if stratum is not None else list(opener_shape),
                'mode': stratum.mode if stratum is not None else 'normal',
                'cell': {'target_hcp': hcp, 'base_shape_index': shape_index},
                'missing_pair_slots': list(range(slot, pairs_per_cell)),
                'reason': f'generation_error: {exc}',
            })
            if progress is not None:
                progress(summary.copy(), len(schedule))
            continue

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
        coverage_cell = {
            'target_hcp': hcp,
            'base_shape_index': shape_index,
            'base_shape': list(base_shape),
            'pair_slot': slot,
        }
        if explicit:
            coverage_cell['opener_shape'] = list(opener_shape)
            coverage_cell['opener_mode'] = opener_mode
        case = {
            'id': trial, 'trial': trial, 'stratum': 'coverage', 'dealer': 'n',
            'vulnerability': 'none',
            'hands': {seat: _compact(hand) for seat, hand in hands.items()},
            'north_hcp': hands['n'].hcp, 'south_hcp': hands['s'].hcp,
            'north_kr': hand_kr(hands['n']), 'south_kr': hand_kr(hands['s']),
            'north_shape': hand_shape(hands['n']), 'south_shape': south_shape,
            'calls': list(simulation.calls), 'auction': simulation.compact_sequence(),
            'history': _history(simulation),
            'coverage_cell': coverage_cell,
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
            boards = []
            for index in range(ew_samples):
                deal = hands if index == 0 else complete_opponents(rng, hands['n'], hands['s'])
                boards.append(solve_table(deal))
            case['dds_tables'] = boards
            summary['dds_boards'] += len(boards)
            complete_cases.append(case)
        elif simulation.status == 'limit':
            case['status'] = 'limit'
            limit_cases.append(case)
        if progress is not None:
            progress(summary.copy(), len(schedule))

    suspicious_cases = []
    flagged_groups = 0
    for members, analysis in assess_auction_groups(
            complete_cases, min_boards=min_class_boards,
            min_pairs=min_class_pairs):
        if analysis is None:
            analysis = {'status': 'insufficient_data',
                        'class_pairs': len(members), 'dds_boards': 0,
                        'flags': [], 'rates': {}}
        for case in members:
            case['analysis'] = {
                **analysis,
                'flags': list(analysis.get('flags') or ()),
                'rates': dict(analysis.get('rates') or {}),
                'alternative_game_rates': dict(
                    analysis.get('alternative_game_rates') or {}),
            }
            if analysis['status'] != 'assessed':
                summary['unassessed'] += 1
        if analysis['flags']:
            flagged_groups += 1
            suspicious_cases.extend(members)
    summary['suspicious'] = flagged_groups

    coverage_south = {
        'responder_hcp': sorted(observed_hcp),
        'longest_suit': sorted(observed_longest),
        'top_two_suits': sorted(observed_top_two),
        'longest_top_two_pairs': [list(pair) for pair in sorted(
            {(longest, top_two) for _, longest, top_two in observed_cells})],
        'cells': [list(cell) for cell in sorted(observed_cells)],
        'exact_shapes': [list(shape) for shape in sorted(observed_shapes)],
    }
    coverage_north = (
        build_north_summary(
            cells=_south_cell_records(hcp_targets, shapes),
            assignments=assignments,
            generated_pairs=dict(generated_pairs),
            north_hcp_by_mode=north_hcp_by_mode,
            cell_failures=cell_failures,
        ) if explicit else {'schema_status': 'legacy'}
    )
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
        'coverage': {**coverage_south, 'north': coverage_north},
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
    parser.add_argument('--min-class-pairs', type=int, default=1)
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
