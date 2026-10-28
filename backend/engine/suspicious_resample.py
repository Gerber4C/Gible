"""Re-sample small suspicious classes, auto-bid, then audit them with DDS."""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
import random
from typing import Callable, Mapping

from .auction import Auction
from .cards import Hand
from .block_report_viewer import group_suspicious_cases
from .constrained_deals import ConstrainedDealSampler, HandConstraints, _compact
from .coverage_scan import (
    _contract, _history, complete_opponents,
)
from .dds_adapter import available_solver_info, calculate_available_table
from .hand_quality import assess_quality
from .outcome_metrics import (
    RULE_ID, assess_auction_groups, available_level, case_cell_key,
    case_process_key, classify_rates, game_success_ratio, reached_game,
    reclassify_analysis,
)
from .selector import choose_bid
from .simulator import simulate_auction


def _retained_flags(contract: str, original_flags: list[str], rates: Mapping) -> list[str]:
    current = set(classify_rates(
        contract, rates, rates.get('alternative_game_rates') or {},
    ))
    return [flag for flag in original_flags if flag in current]


def _current_suspicious_cases(source: Mapping) -> list[Mapping]:
    complete_cases = source.get('complete_cases')
    if complete_cases is None:
        return list(source['suspicious_cases'])
    if not isinstance(complete_cases, list):
        raise ValueError('source complete_cases must be a list')
    for original in complete_cases:
        if not isinstance(original, Mapping):
            raise ValueError('source complete_cases must contain mappings')
    budget = source.get('budget') or {}
    min_boards = budget.get('min_class_boards', 10)
    min_pairs = budget.get('min_class_pairs', 1)
    if not isinstance(min_boards, int) or isinstance(min_boards, bool) or min_boards < 1:
        min_boards = 10
    if not isinstance(min_pairs, int) or isinstance(min_pairs, bool) or min_pairs < 1:
        min_pairs = 1
    eligible = [case for case in complete_cases
                if isinstance(case.get('contract'), str)
                and case.get('declarer') in ('n', 's')]
    current = []
    handled = set()
    for members, analysis in assess_auction_groups(
            eligible, min_boards=min_boards, min_pairs=min_pairs):
        copies = []
        for original in members:
            case = dict(original)
            if analysis is None:
                case['analysis'] = reclassify_analysis(
                    case.get('contract'), case.get('analysis') or {})
            else:
                case['analysis'] = {
                    **analysis,
                    'flags': list(analysis.get('flags') or ()),
                    'rates': dict(analysis.get('rates') or {}),
                    'alternative_game_rates': dict(
                        analysis.get('alternative_game_rates') or {}),
                }
            copies.append(case)
            handled.add(id(original))
        if any(case['analysis'].get('flags') for case in copies):
            current.extend(case for case in copies if case['analysis'].get('flags'))
    unhandled = {}
    for original in complete_cases:
        if id(original) in handled:
            continue
        case = dict(original)
        analysis = case.get('analysis') or {}
        if not isinstance(analysis, Mapping):
            raise ValueError('source analysis must be a mapping')
        case['analysis'] = reclassify_analysis(case.get('contract'), analysis)
        unhandled.setdefault(
            (case_cell_key(case), case_process_key(case)), []).append(case)
    for copies in unhandled.values():
        current.extend(case for case in copies if case['analysis'].get('flags'))
    return current


def constraints_for_group(members: list[Mapping]) -> tuple[HandConstraints, HandConstraints]:
    """Keep each seat's complete original-plus-new HCP/K–R span within two."""
    if not members:
        raise ValueError('a suspicious group needs at least one source case')
    constraints = []
    for seat in ('north', 'south'):
        shape = tuple(members[0][f'{seat}_shape'])
        if any(tuple(item[f'{seat}_shape']) != shape for item in members):
            raise ValueError('source group mixes different suit shapes')
        hcp_values = [item[f'{seat}_hcp'] for item in members]
        kr_values = [item[f'{seat}_kr'] for item in members]
        if max(hcp_values) - min(hcp_values) > 2 or max(kr_values) - min(kr_values) > 2.000001:
            raise ValueError('source group exceeds the two-point class span')
        hcp_midpoint = (min(hcp_values) + max(hcp_values)) / 2
        hcp_low = max(0, min(35, math.floor(hcp_midpoint - .5)))
        hcp = (hcp_low, hcp_low + 2)
        kr_midpoint = (min(kr_values) + max(kr_values)) / 2
        kr = (round(kr_midpoint - 1, 3), round(kr_midpoint + 1, 3))
        constraints.append(HandConstraints(shape, hcp, kr))
    return tuple(constraints)


def _rates_for_contract(contract: str, declarer: str, boards: list[Mapping]) -> dict:
    level = int(contract[0])
    strain = contract[1:]
    wrong_rate, alternative_rates = game_success_ratio(contract, declarer, boards)
    return {
        'contract_failure': sum(table[strain][declarer] < level + 6 for table in boards) / len(boards),
        'missed_game': (sum(available_level(table, 'game') for table in boards) / len(boards)
                        if not reached_game(contract) else None),
        'missed_small_slam': (sum(available_level(table, 'small_slam') for table in boards) / len(boards)
                              if level < 6 else None),
        'missed_grand_slam': (sum(available_level(table, 'grand_slam') for table in boards) / len(boards)
                              if level < 7 else None),
        'wrong_game': wrong_rate,
        'alternative_game_rates': alternative_rates,
    }


def resample_groups(
    source: Mapping,
    profile,
    *,
    seed: int = 41,
    max_source_cases: int = 10,
    pairs_per_group: int = 20,
    ew_samples: int = 10,
    max_draws_per_group: int | None = None,
    solve_table: Callable = calculate_available_table,
    progress: Callable[[dict, int], None] | None = None,
) -> dict:
    """Reproduce every small class with fresh N/S pairs and E/W completions."""
    if source.get('schema_version') != 2 or not isinstance(source.get('suspicious_cases'), list):
        raise ValueError('source must be a coverage report with suspicious_cases')
    if min(max_source_cases, pairs_per_group, ew_samples) < 1:
        raise ValueError('class limit, pair count, and E/W sample count must be positive')
    if max_draws_per_group is None:
        max_draws_per_group = pairs_per_group * 500
    if max_draws_per_group < pairs_per_group:
        raise ValueError('max_draws_per_group must be at least pairs_per_group')

    suspicious_cases = _current_suspicious_cases(source)
    originals = {item['id']: item for item in suspicious_cases}
    source_groups = group_suspicious_cases(suspicious_cases)
    rng = random.Random(seed)
    groups = []
    skipped = 0
    for index, ids in enumerate(source_groups, 1):
        if len(ids) > max_source_cases:
            skipped += 1
            continue
        members = [originals[item_id] for item_id in ids]
        north_rule, south_rule = constraints_for_group(members)
        group_seed = rng.randrange(2**32)
        sampler = ConstrainedDealSampler(north_rule, south_rule, seed=group_seed)
        group = {
            'id': f'G{index:03d}', 'source_ids': ids, 'seed': group_seed,
            'constraints': {'north': vars(north_rule), 'south': vars(south_rule)},
            'summary': {'requested_pairs': pairs_per_group, 'draws': 0,
                        'pairs': 0, 'blocked': 0, 'complete': 0, 'limit': 0,
                        'dds_boards': 0, 'matching_auction': 0},
            'contracts': {}, 'deals': [], 'source_checks': [],
        }
        seen_pairs = set()
        all_boards = []
        contract_counts = Counter()
        original_auctions = {member['auction'] for member in members}
        empty = Auction.parse('', dealer='n', vulnerability='none')
        environment = {'dealer': 'n', 'vulnerability': 'none', 'scoring': 'IMP'}
        while group['summary']['pairs'] < pairs_per_group and group['summary']['draws'] < max_draws_per_group:
            group['summary']['draws'] += 1
            hands = sampler.deal()
            opening = choose_bid(profile, empty, hands['n'],
                                 {**environment, 'seat': 'n'})
            if opening.call != '1N':
                continue
            pair_key = (_compact(hands['n']), _compact(hands['s']))
            if pair_key in seen_pairs:
                continue
            seen_pairs.add(pair_key)
            trial = group['summary']['pairs'] + 1
            simulation = simulate_auction(
                profile, {'n': hands['n'], 's': hands['s']}, dealer='n',
                vulnerability='none', environment=environment,
            )
            if not simulation.calls or simulation.calls[0] != '1N':
                raise RuntimeError('opening filter and simulation disagreed')
            case = {
                'id': f"{group['id']}-{trial:03d}", 'trial': trial,
                'hands': {seat: _compact(hand) for seat, hand in hands.items()},
                'north_shape': list(north_rule.shape),
                'south_shape': list(south_rule.shape),
                'north_hcp': hands['n'].hcp, 'south_hcp': hands['s'].hcp,
                'north_kr': assess_quality(hands['n'])['kr_points'],
                'south_kr': assess_quality(hands['s'])['kr_points'],
                'status': simulation.status, 'calls': list(simulation.calls),
                'auction': simulation.compact_sequence(),
                'history': _history(simulation),
            }
            group['summary']['pairs'] += 1
            group['summary'][simulation.status] += 1
            group['summary']['matching_auction'] += case['auction'] in original_auctions
            if simulation.status == 'blocked':
                case['blocked'] = simulation.blocked
            elif simulation.status == 'complete':
                contract, declarer = _contract(simulation.calls)
                case.update(contract=contract, declarer=declarer)
                contract_counts[contract] += 1
            else:
                case['diagnostics'] = list(simulation.diagnostics)
            boards = []
            for sample_index in range(ew_samples):
                deal = hands if sample_index == 0 else complete_opponents(
                    sampler.rng, hands['n'], hands['s'])
                boards.append(solve_table(deal))
            case['dds_tables'] = boards
            all_boards.extend(boards)
            group['summary']['dds_boards'] += len(boards)
            if 'contract' in case:
                case['chosen_contract_rates'] = _rates_for_contract(
                    case['contract'], case['declarer'], boards)
            group['deals'].append(case)

        group['contracts'] = dict(sorted(contract_counts.items()))
        if group['summary']['pairs'] < pairs_per_group:
            group['sampling_warning'] = (
                f"Only {group['summary']['pairs']} matching 1NT openers after "
                f"{group['summary']['draws']} draws")
        for member in members:
            new_rates = (_rates_for_contract(member['contract'], member['declarer'], all_boards)
                         if all_boards else {})
            old_flags = list(member['analysis']['flags'])
            group['source_checks'].append({
                'source_id': member['id'], 'auction': member['auction'],
                'contract': member['contract'], 'declarer': member['declarer'],
                'original_boards': member['analysis'].get('dds_boards'),
                'new_boards': len(all_boards),
                'original_flags': old_flags,
                'original_rates': {flag: member['analysis']['rates'].get(flag)
                                   for flag in old_flags},
                'new_rates': {flag: new_rates.get(flag) for flag in old_flags},
                'retained_flags': _retained_flags(
                    member['contract'], old_flags, new_rates),
            })
        groups.append(group)
        if progress is not None:
            progress(group, len(source_groups))

    return {
        'schema_version': 1, 'kind': 'suspicious_resample',
        'wrong_game_rule': RULE_ID,
        'source_seed': source.get('seed'), 'seed': seed,
        'profile': {'id': profile.id, 'name': profile.name,
                    'version': profile.version},
        'solver': available_solver_info() if solve_table is calculate_available_table else {'package': 'injected'},
        'budget': {'max_source_cases': max_source_cases,
                   'pairs_per_group': pairs_per_group, 'ew_samples': ew_samples,
                   'max_draws_per_group': max_draws_per_group},
        'summary': {'source_groups': len(source_groups),
                    'resampled_groups': len(groups),
                    'skipped_large_groups': skipped,
                    'pairs': sum(group['summary']['pairs'] for group in groups),
                    'complete': sum(group['summary']['complete'] for group in groups),
                    'blocked': sum(group['summary']['blocked'] for group in groups),
                    'dds_boards': sum(group['summary']['dds_boards'] for group in groups),
                    'source_flags': sum(len(check['original_flags'])
                                        for group in groups for check in group['source_checks']),
                    'retained_flags': sum(len(check['retained_flags'])
                                          for group in groups for check in group['source_checks'])},
        'groups': groups,
        'method_note': ('Each new hand matches the named-suit shape of its group; across all source '
                        'and new hands in each seat, raw HCP and pure K-R each have a maximum-minus-minimum '
                        'of at most 2. North actually opens 1NT. N/S bidding sees only '
                        'each bidder’s own cards. DDS double-dummy success is a screening proxy, '
                        'not real-play probability. E/W re-completions of one N/S pair are correlated.'),
    }


def _additional_ew_tables(task: tuple[str, str, str, str, int, int],
                          solve_table: Callable = calculate_available_table) -> list[dict]:
    north_text, south_text, east_text, west_text, count, seed = task
    north, south = Hand.parse(north_text), Hand.parse(south_text)
    rng = random.Random(seed)
    seen = {(east_text, west_text)}
    boards = []
    while len(boards) < count:
        hands = complete_opponents(rng, north, south)
        pair = (_compact(hands['e']), _compact(hands['w']))
        if pair in seen:
            continue
        seen.add(pair)
        boards.append(solve_table(hands))
    return boards


def extend_ew_samples(
    report: Mapping,
    *,
    ew_samples: int = 10,
    workers: int = 8,
    solve_table: Callable = calculate_available_table,
    progress: Callable[[dict, int], None] | None = None,
) -> dict:
    """Add DDS completions to existing N/S pairs without changing their auctions.

    The original boards and case IDs remain intact, so saved group reviews still
    apply. Extra E/W deals use stable per-case seeds. Multiprocessing is limited
    to the built-in DDS solver; injected test solvers run in this process.
    """
    if report.get('kind') != 'suspicious_resample' or not isinstance(report.get('groups'), list):
        raise ValueError('expected a suspicious resampling report')
    old_count = report['budget']['ew_samples']
    if not isinstance(ew_samples, int) or ew_samples < old_count:
        raise ValueError('ew_samples must be at least the existing count')
    if not isinstance(workers, int) or workers < 1:
        raise ValueError('workers must be positive')
    if workers > 1 and solve_table is not calculate_available_table:
        raise ValueError('an injected solver requires workers=1')

    updated = deepcopy(report)
    jobs = []
    for group in updated['groups']:
        for case in group['deals']:
            boards = case['dds_tables']
            if len(boards) != old_count:
                raise ValueError(f"{case['id']}: existing DDS board count does not match budget")
            hands = case['hands']
            material = f"{report.get('seed')}:{case['id']}:ew-extra".encode('utf-8')
            case_seed = int.from_bytes(hashlib.sha256(material).digest()[:8], 'big')
            jobs.append((hands['n'], hands['s'], hands['e'], hands['w'],
                         ew_samples - old_count, case_seed))

    if ew_samples > old_count:
        if workers == 1:
            additional = map(lambda job: _additional_ew_tables(job, solve_table), jobs)
            pool = None
        else:
            pool = ProcessPoolExecutor(max_workers=workers)
            additional = pool.map(_additional_ew_tables, jobs)
        try:
            for group in updated['groups']:
                for case in group['deals']:
                    case['dds_tables'].extend(next(additional))
                if progress is not None:
                    progress(group, len(updated['groups']))
        finally:
            if pool is not None:
                pool.shutdown()

    for group in updated['groups']:
        all_boards = [table for case in group['deals'] for table in case['dds_tables']]
        group['summary']['dds_boards'] = len(all_boards)
        for case in group['deals']:
            if 'contract' in case:
                case['chosen_contract_rates'] = _rates_for_contract(
                    case['contract'], case['declarer'], case['dds_tables'])
        for check in group['source_checks']:
            new_rates = (_rates_for_contract(check['contract'], check['declarer'], all_boards)
                         if all_boards else {})
            check['new_boards'] = len(all_boards)
            check['new_rates'] = {flag: new_rates.get(flag)
                                  for flag in check['original_flags']}
            check['retained_flags'] = _retained_flags(
                check['contract'], check['original_flags'], new_rates)
    updated['budget']['ew_samples'] = ew_samples
    updated['summary']['dds_boards'] = sum(
        group['summary']['dds_boards'] for group in updated['groups'])
    updated['summary']['retained_flags'] = sum(
        len(check['retained_flags']) for group in updated['groups']
        for check in group['source_checks'])
    updated['ew_extension'] = {'from_samples': old_count, 'to_samples': ew_samples,
                               'method': 'fixed N/S pairs; additional E/W completions'}
    return updated


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Re-sample small suspicious 1NT classes')
    parser.add_argument('source', type=Path)
    parser.add_argument('--profile', default=None)
    parser.add_argument('--seed', type=int, default=41)
    parser.add_argument('--max-source-cases', type=int, default=10)
    parser.add_argument('--pairs-per-group', type=int, default=20)
    parser.add_argument('--ew-samples', type=int, default=10)
    parser.add_argument('--workers', type=int, default=8,
                        help='DDS workers when extending an existing report')
    parser.add_argument('--reviews', type=Path,
                        help='Optional saved group reviews to show in the HTML report')
    parser.add_argument('--max-draws-per-group', type=int)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    source = json.loads(args.source.read_text(encoding='utf-8'))
    from .loader import load_profile
    from .suspicious_resample_viewer import render_html
    from .suspicious_review_workflow import review_brief
    if source.get('kind') == 'suspicious_resample':
        report = extend_ew_samples(
            source, ew_samples=args.ew_samples, workers=args.workers,
            progress=lambda group, total: print(
                f'{group["id"]}/{total}: additional E/W boards complete', flush=True),
        )
    else:
        profile = load_profile(args.profile or source['profile']['id'])
        report = resample_groups(
            source, profile, seed=args.seed,
            max_source_cases=args.max_source_cases,
            pairs_per_group=args.pairs_per_group,
            ew_samples=args.ew_samples,
            max_draws_per_group=args.max_draws_per_group,
            progress=lambda group, total: print(
                f'{group["id"]}/{total}: {group["summary"]["pairs"]} pairs, '
                f'{group["summary"]["blocked"]} TD calls, '
                f'{group["summary"]["dds_boards"]} DDS boards', flush=True),
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n',
                           encoding='utf-8')
    html_path = args.output.with_suffix('.html')
    reviews = (json.loads(args.reviews.read_text(encoding='utf-8'))
               if args.reviews else None)
    html_path.write_text(render_html(report, reviews=reviews), encoding='utf-8')
    brief_path = args.output.with_name(args.output.stem + '-review-brief.json')
    brief_path.write_text(json.dumps(review_brief(report), ensure_ascii=False, indent=2) + '\n',
                          encoding='utf-8')
    summary = report['summary']
    print(f"{summary['resampled_groups']} groups; {summary['pairs']} N/S pairs; "
          f"{summary['dds_boards']} DDS boards; "
          f"{summary['retained_flags']}/{summary['source_flags']} old flags above threshold. "
          f"Report: {args.output}; viewer: {html_path}; review brief: {brief_path}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
