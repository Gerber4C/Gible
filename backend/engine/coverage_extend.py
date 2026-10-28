"""Top up undersized N/S sampling cells in an existing coverage report.

The extender keeps every stored cell's actual responder shape, HCP target,
North opening shape/HCP, and the first pair's K–R anchor. It samples only the
missing N/S pairs, re-runs the profile auction and DDS, then recomputes the
pooled cell assessment. Existing cells are never reshaped or discarded.
"""

from __future__ import annotations

import argparse
import json
import math
import random
from collections import Counter
from pathlib import Path
from typing import Callable, Mapping

from .auction import Auction
from .coverage_scan import (
    _contract,
    _history,
    _opening_assessment,
    complete_opponents,
    hand_kr,
    hand_shape,
    sample_partnership,
)
from .dds_adapter import calculate_available_table
from .joint_deal_sampler import (
    JointConstraintError,
    JointPartnershipPlan,
    OpenerModeConstraints,
    sample_conditioned_partnership,
)
from .opener_coverage import (
    OpenerStratum, build_north_summary, rotate_responder_shape,
    validate_cell_identity, validate_explicit_coverage_cell,
)
from .outcome_metrics import (
    RULE_ID, assess_auction_groups, case_cell_key, case_process_key,
)
from .selector import choose_bid
from .simulator import simulate_auction
from .training_deals import _compact


COLLECTIONS = (('blocked', 'cases'), ('complete', 'complete_cases'),
               ('limit', 'limit_cases'))


def _id_key(value):
    return (0, value) if isinstance(value, int) else (1, str(value))


def _case_key(case: Mapping):
    return _id_key(case.get('id'))


def _finite_number(value) -> bool:
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value))


def _valid_shape(value) -> bool:
    return (isinstance(value, (list, tuple)) and len(value) == 4
            and all(isinstance(length, int) and not isinstance(length, bool)
                    and length >= 0 for length in value)
            and sum(value) == 13)


def _report_cases(report: Mapping) -> dict[str, list[tuple[Mapping, str]]]:
    cells: dict[str, list[tuple[Mapping, str]]] = {}
    for status, key in COLLECTIONS:
        items = report.get(key, [])
        if not isinstance(items, list):
            raise ValueError(f'{key} must be a list')
        for case in items:
            if not isinstance(case, Mapping):
                raise ValueError(f'{key} must contain mappings')
            cells.setdefault(case_cell_key(case), []).append((case, status))
    return cells


def _cell_label(identity) -> str:
    return f'{identity[0]}:{identity[1]}'


def _explicit_requests(report: Mapping):
    north = (report.get('coverage') or {}).get('north')
    if not isinstance(north, Mapping) or north.get('schema_status') != 'explicit':
        return None
    requests = {}
    for position, item in enumerate(north.get('requested_strata') or ()):
        if not isinstance(item, Mapping):
            raise ValueError(
                f'coverage.north.requested_strata[{position}] must be an object')
        try:
            cell = validate_cell_identity(item.get('cell'))
            stratum = OpenerStratum(tuple(item.get('shape') or ()),
                                    item.get('mode'))
            OpenerModeConstraints(stratum.shape, stratum.mode, (0.0, 37.0))
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f'coverage.north.requested_strata[{position}]: {exc}') from exc
        identity = (cell['target_hcp'], cell['base_shape_index'])
        if identity[0] > 37:
            raise ValueError(
                f'cell {_cell_label(identity)}: target_hcp must be from 0 through 37')
        if identity in requests:
            raise ValueError(
                f'coverage.north.requested_strata contains duplicate cell '
                f'{_cell_label(identity)}')
        requests[identity] = {'shape': stratum.shape, 'mode': stratum.mode}

    failures = {}
    for position, failure in enumerate(north.get('cell_failures') or ()):
        if not isinstance(failure, Mapping):
            raise ValueError(
                f'coverage.north.cell_failures[{position}] must be an object')
        try:
            cell = validate_cell_identity(failure.get('cell'))
        except ValueError as exc:
            raise ValueError(
                f'coverage.north.cell_failures[{position}]: {exc}') from exc
        identity = (cell['target_hcp'], cell['base_shape_index'])
        if identity[0] > 37:
            raise ValueError(
                f'cell {_cell_label(identity)}: target_hcp must be from 0 through 37')
        if identity in failures:
            raise ValueError(
                f'duplicate cell_failures identity {_cell_label(identity)}')
        requested = requests.get(identity)
        if requested is None:
            raise ValueError(
                f'cell {_cell_label(identity)}: failure has no requested_strata record')
        for field in ('shape', 'mode'):
            expected = (list(requested['shape']) if field == 'shape'
                        else requested[field])
            if failure.get(field) != expected:
                raise ValueError(
                    f'cell {_cell_label(identity)}: cell_failures {field} '
                    f'conflicts with requested_strata')
        slots = failure.get('missing_pair_slots')
        if (not isinstance(slots, list)
                or any(not isinstance(slot, int) or isinstance(slot, bool)
                       or slot < 0 for slot in slots)
                or len(set(slots)) != len(slots)):
            raise ValueError(
                f'cell {_cell_label(identity)}: missing_pair_slots must be '
                f'a list of unique non-negative integers')
        failures[identity] = dict(failure)
    return {'requests': requests, 'failures': failures}


def _validated_filter_shapes(report: Mapping, identities) -> list[tuple[int, ...]]:
    filters = report.get('filters')
    if not isinstance(filters, Mapping) or not isinstance(filters.get('shapes'), list):
        raise ValueError('filters.shapes must be a list for explicit coverage')
    shapes = filters['shapes']
    validated = []
    for index, shape in enumerate(shapes):
        try:
            validated.append(rotate_responder_shape(shape, 0, 0))
        except ValueError as exc:
            raise ValueError(f'filters.shapes[{index}]: {exc}') from exc
    for identity in identities:
        index = identity[1]
        if index >= len(validated):
            raise ValueError(
                f'cell {_cell_label(identity)}: base_shape_index {index} is '
                f'out of range for filters.shapes')
    return validated


def _validate_explicit_report(report: Mapping):
    state = _explicit_requests(report)
    if state is None:
        return None
    shapes = _validated_filter_shapes(report, state['requests'])
    grouped = {}
    for key in ('cases', 'complete_cases', 'limit_cases'):
        for case in report.get(key, ()):
            raw_cell = case.get('coverage_cell')
            try:
                cell = validate_explicit_coverage_cell(raw_cell)
            except ValueError as exc:
                raise ValueError(f'{key} case {case.get("id")}: {exc}') from exc
            identity = (cell['target_hcp'], cell['base_shape_index'])
            label = _cell_label(identity)
            if identity[0] > 37:
                raise ValueError(
                    f'cell {label}: target_hcp must be from 0 through 37')
            requested = state['requests'].get(identity)
            if requested is None:
                raise ValueError(f'cell {label}: missing requested_strata record')
            if cell['base_shape'] != shapes[identity[1]]:
                raise ValueError(
                    f'cell {label}: base_shape conflicts with '
                    f'filters.shapes[{identity[1]}]')
            for field, actual, expected in (
                    ('opener_shape', cell['opener_shape'], requested['shape']),
                    ('opener_mode', cell['opener_mode'], requested['mode']),
                    ('south_shape', tuple(case.get('south_shape') or ()),
                     rotate_responder_shape(cell['base_shape'], *identity)),
                    ('south_hcp', case.get('south_hcp'), identity[0]),
                    ('north_shape', tuple(case.get('north_shape') or ()),
                     cell['opener_shape'])):
                if actual != expected:
                    raise ValueError(f'cell {label}: {field} conflicts with metadata')
            if (not isinstance(case.get('north_hcp'), int)
                    or isinstance(case.get('north_hcp'), bool)):
                raise ValueError(f'cell {label}: north_hcp must be an integer')
            allowed_hcp = {
                'normal': range(15, 18),
                'upgrade_14': (14,),
                'soft_18': (18,),
            }[cell['opener_mode']]
            if case['north_hcp'] not in allowed_hcp:
                raise ValueError(
                    f'cell {label}: north_hcp conflicts with opener_mode')
            for field in ('north_kr', 'south_kr'):
                if not _finite_number(case.get(field)):
                    raise ValueError(
                        f'cell {label}: {field} must be a finite number')
            grouped.setdefault(identity, []).append((raw_cell, case))
    for identity, members in grouped.items():
        cells = [cell for cell, _ in members]
        try:
            validate_explicit_coverage_cell(cells[0], siblings=cells[1:])
        except ValueError as exc:
            raise ValueError(f'cell {_cell_label(identity)}: {exc}') from exc
        slots = [cell['pair_slot'] for cell in cells]
        duplicate_slots = sorted(
            slot for slot, count in Counter(slots).items() if count > 1)
        if duplicate_slots:
            raise ValueError(
                f'cell {_cell_label(identity)}: pair_slot '
                f'{duplicate_slots[0]} is duplicate')
        for field in ('north_kr', 'south_kr'):
            values = [float(case[field]) for _, case in members]
            if max(values) - min(values) > 4:
                raise ValueError(
                    f'cell {_cell_label(identity)}: {field} aggregate span '
                    f'exceeds 4')
        failure = state['failures'].get(identity)
        if failure is not None:
            stored_slots = {cell['pair_slot'] for cell, _ in members}
            overlap = stored_slots.intersection(failure['missing_pair_slots'])
            if overlap:
                slot = min(overlap)
                raise ValueError(
                    f'cell {_cell_label(identity)}: missing_pair_slots '
                    f'overlaps stored pair_slot {slot}')
    return {**state, 'shapes': shapes}


def _cell_spec(members: list[tuple[Mapping, str]]) -> dict | None:
    first = min((case for case, _ in members), key=_case_key)
    south_shape = first.get('south_shape')
    north_shape = first.get('north_shape')
    south_hcp = first.get('south_hcp')
    north_hcp = first.get('north_hcp')
    north_kr = first.get('north_kr')
    south_kr = first.get('south_kr')
    if not (_valid_shape(south_shape) and _valid_shape(north_shape)):
        return None
    if not all(isinstance(value, int) and not isinstance(value, bool)
               and 0 <= value <= 37 for value in (south_hcp, north_hcp)):
        return None
    if not (_finite_number(north_kr) and _finite_number(south_kr)):
        return None
    cell = first.get('coverage_cell')
    explicit = (isinstance(cell, Mapping)
                and 'opener_shape' in cell and 'opener_mode' in cell)
    if explicit:
        identity = (cell.get('target_hcp'), cell.get('base_shape_index'))
        try:
            validated = validate_explicit_coverage_cell(
                cell, siblings=[case.get('coverage_cell') for case, _ in members
                                if case is not first])
        except ValueError as exc:
            raise ValueError(f'cell {_cell_label(identity)}: {exc}') from exc
        opener_shape = validated['opener_shape']
        opener_mode = validated['opener_mode']
        south_shape = rotate_responder_shape(
            validated['base_shape'], validated['target_hcp'],
            validated['base_shape_index'])
        return {
            'south_shape': tuple(south_shape),
            'north_shape': opener_shape,
            'south_hcp': validated['target_hcp'],
            'north_hcp': None,
            'reference': (float(north_kr), float(south_kr)),
            'coverage_cell': dict(cell),
            'explicit': True,
            'opener_shape': opener_shape,
            'opener_mode': opener_mode,
        }
    return {
        'south_shape': tuple(south_shape),
        'north_shape': tuple(north_shape),
        'south_hcp': south_hcp,
        'north_hcp': north_hcp,
        'reference': (float(north_kr), float(south_kr)),
        'coverage_cell': dict(cell) if isinstance(cell, Mapping) else None,
        'explicit': False,
    }


def _kr_envelope(cases, key):
    values = [float(case[key]) for case in cases if _finite_number(case.get(key))]
    if not values:
        return (0.0, 37.0)
    return (max(0.0, max(values) - 2), min(37.0, min(values) + 2))


def _sample_explicit(rng, spec, members, added_cases, assessment):
    cases = [case for case, _ in members] + list(added_cases)
    plan = JointPartnershipPlan(
        OpenerModeConstraints(
            spec['opener_shape'], spec['opener_mode'],
            _kr_envelope(cases, 'north_kr')),
        spec['south_shape'], spec['south_hcp'],
        _kr_envelope(cases, 'south_kr'))
    return sample_conditioned_partnership(
        plan, rng=rng, opening_assessment=assessment,
        complete_opponents=complete_opponents)


def _repair_explicit_slots(report, profile, rng, next_id, ew_samples,
                           solve_table, assessment, state=None):
    """Retry exactly the persisted missing slots of explicit failed cells."""
    state = state if state is not None else _validate_explicit_report(report)
    if state is None:
        return next_id, 0
    cells = _report_cases(report)
    by_identity = {}
    for members in cells.values():
        first = min((case for case, _ in members), key=_case_key)
        cell = first.get('coverage_cell') or {}
        identity = (cell.get('target_hcp'), cell.get('base_shape_index'))
        by_identity[identity] = members
    shapes = state['shapes']
    added = 0
    for identity, failure in list(state['failures'].items()):
        hcp, index = identity
        if not (isinstance(hcp, int) and not isinstance(hcp, bool)
                and isinstance(index, int) and not isinstance(index, bool)):
            continue
        members = by_identity.get(identity, [])
        if members:
            spec = _cell_spec(members)
        else:
            requested = state['requests'].get(identity)
            if requested is None:
                raise ValueError(
                    f'cell {_cell_label(identity)}: missing requested_strata record')
            base_shape = shapes[index]
            south_shape = rotate_responder_shape(base_shape, hcp, index)
            spec = {
                'south_shape': south_shape, 'south_hcp': hcp,
                'north_shape': tuple(requested['shape']),
                'north_hcp': None, 'reference': (0.0, 0.0),
                'coverage_cell': {
                    'target_hcp': hcp, 'base_shape_index': index,
                    'base_shape': list(base_shape), 'pair_slot': 0,
                    'opener_shape': list(requested['shape']),
                    'opener_mode': requested['mode'],
                },
                'explicit': True,
                'opener_shape': tuple(requested['shape']),
                'opener_mode': requested['mode'],
            }
        if spec is None or not spec.get('explicit'):
            continue
        if assessment is None:
            failure['reason'] = (
                'generation_error: North opening assessment is unavailable')
            continue
        added_cases = []
        remaining = []
        for slot in failure.get('missing_pair_slots') or ():
            if not isinstance(slot, int) or isinstance(slot, bool) or slot < 0:
                continue
            try:
                hands = _sample_explicit(
                    rng, spec, members, added_cases, assessment)
                simulation = simulate_auction(
                    profile, {'n': hands['n'], 's': hands['s']}, dealer='n',
                    vulnerability='none',
                    environment={'dealer': 'n', 'vulnerability': 'none',
                                 'scoring': 'IMP'}, max_calls=80,
                )
                if not simulation.calls or simulation.calls[0] != '1N':
                    raise RuntimeError('sampled North did not open 1NT')
                case = _new_case(next_id, hands, simulation,
                                 cell_meta=spec['coverage_cell'],
                                 pair_slot=slot)
                next_id += 1
                added += 1
                added_cases.append(case)
                if simulation.status == 'blocked':
                    case.update(blocked=simulation.blocked,
                                review_status='unreviewed')
                    report.setdefault('cases', []).append(case)
                elif simulation.status == 'complete':
                    contract, declarer = _contract(simulation.calls)
                    case.update(contract=contract, declarer=declarer)
                    boards = []
                    for sample in range(ew_samples):
                        deal = (hands if sample == 0
                                else complete_opponents(
                                    rng, hands['n'], hands['s']))
                        boards.append(solve_table(deal))
                    case['dds_tables'] = boards
                    report.setdefault('complete_cases', []).append(case)
                else:
                    case['status'] = 'limit'
                    report.setdefault('limit_cases', []).append(case)
            except (JointConstraintError, RuntimeError) as exc:
                failure['reason'] = f'generation_error: {exc}'
                remaining.append(slot)
        if remaining:
            failure['missing_pair_slots'] = remaining
        else:
            state['failures'].pop(identity, None)
    (report['coverage']['north'])['cell_failures'] = list(
        state['failures'].values())
    return next_id, added


def _next_pair_slot(members, target: int) -> int | None:
    slots = set()
    for case, _ in members:
        cell = case.get('coverage_cell')
        if isinstance(cell, Mapping):
            slot = cell.get('pair_slot')
            if isinstance(slot, int) and not isinstance(slot, bool) and slot >= 0:
                slots.add(slot)
    if not any(isinstance(case.get('coverage_cell'), Mapping)
               for case, _ in members):
        return None
    for slot in range(target + len(slots) + 1):
        if slot not in slots:
            return slot
    return max(slots, default=-1) + 1


def _opener_eligible(profile):
    empty = Auction.parse('', dealer='n', vulnerability='none')

    def eligible(hand):
        return choose_bid(
            profile, empty, hand,
            {'dealer': 'n', 'seat': 'n', 'vulnerability': 'none',
             'scoring': 'IMP'},
        ).call == '1N'

    return eligible


def _new_case(case_id: int, hands, simulation, *, cell_meta, pair_slot) -> dict:
    case = {
        'id': case_id, 'trial': case_id, 'stratum': 'coverage',
        'dealer': 'n', 'vulnerability': 'none',
        'hands': {seat: _compact(hand) for seat, hand in hands.items()},
        'north_hcp': hands['n'].hcp, 'south_hcp': hands['s'].hcp,
        'north_kr': hand_kr(hands['n']), 'south_kr': hand_kr(hands['s']),
        'north_shape': list(hand_shape(hands['n'])),
        'south_shape': list(hand_shape(hands['s'])),
        'calls': list(simulation.calls),
        'auction': simulation.compact_sequence(),
        'history': _history(simulation),
    }
    if cell_meta is not None:
        case['coverage_cell'] = {**cell_meta, 'pair_slot': pair_slot}
    return case


def _process_group_key(case: Mapping, status: str):
    return (case_process_key(case),
            case.get('contract') if status == 'complete' else None,
            case.get('declarer') if status == 'complete' else None,
            status)


def _simulation_group_key(simulation, contract=None, declarer=None):
    return (tuple(str(call) for call in simulation.calls),
            contract if simulation.status == 'complete' else None,
            declarer if simulation.status == 'complete' else None,
            simulation.status)


def _auction_label(case: Mapping) -> str:
    auction = case.get('auction')
    if isinstance(auction, str) and auction:
        return auction
    return ' '.join(str(call) for call in case.get('calls') or ())


def _slot_allocator(members):
    """Return a callable allocating unused pair slots, or None for legacy."""
    if not any(isinstance(case.get('coverage_cell'), Mapping)
               for case, _ in members):
        return None
    used = set()
    for case, _ in members:
        cell = case.get('coverage_cell')
        if isinstance(cell, Mapping):
            slot = cell.get('pair_slot')
            if isinstance(slot, int) and not isinstance(slot, bool) and slot >= 0:
                used.add(slot)

    def allocate():
        slot = 0
        while slot in used:
            slot += 1
        used.add(slot)
        return slot

    return allocate


def _members_identity(members):
    cell = members[0][0].get('coverage_cell') if members else None
    if not isinstance(cell, Mapping):
        return None
    return cell.get('target_hcp'), cell.get('base_shape_index')


def extend_process_pairs(
    report: Mapping,
    profile,
    *,
    target_pairs: int = 10,
    ew_samples: int | None = None,
    seed: int = 41,
    max_attempts_per_cell: int | None = None,
    allow_new_processes: bool = True,
    discovery_idle_limit: int | None = 100,
    solve_table: Callable = calculate_available_table,
    progress: Callable[[dict, int], None] | None = None,
) -> dict:
    """Top up every auction-process cell inside each sampling cell.

    New N/S pairs keep the sampling cell's exact shape/HCP/K–R constraints.
    Known process groups are filled first. Once they are complete, a candidate
    whose complete auction is a new process opens a new process sub-cell and
    is topped up to the same target while attempts remain. After
    ``discovery_idle_limit`` consecutive attempts without opening a new
    process, discovery stops for that cell; set it to ``None`` to keep trying
    until the attempt cap. Set ``allow_new_processes=False`` to discard unseen
    processes instead.
    """
    if report.get('schema_version') != 2:
        raise ValueError('source must be a coverage report (schema version 2)')
    if not isinstance(target_pairs, int) or isinstance(target_pairs, bool) or target_pairs < 1:
        raise ValueError('target_pairs must be a positive integer')
    if max_attempts_per_cell is not None and (
            not isinstance(max_attempts_per_cell, int)
            or isinstance(max_attempts_per_cell, bool)
            or max_attempts_per_cell < 1):
        raise ValueError('max_attempts_per_cell must be a positive integer')
    if discovery_idle_limit is not None and (
            not isinstance(discovery_idle_limit, int)
            or isinstance(discovery_idle_limit, bool)
            or discovery_idle_limit < 0):
        raise ValueError('discovery_idle_limit must be a non-negative integer or None')
    budget = report.get('budget') or {}
    if ew_samples is None:
        ew_samples = budget.get('ew_samples', 10)
    if not isinstance(ew_samples, int) or isinstance(ew_samples, bool) or not 1 <= ew_samples <= 20:
        raise ValueError('ew_samples must be an integer from 1 to 20')

    updated = json.loads(json.dumps(report))
    explicit_state = _validate_explicit_report(updated)
    cells = _report_cases(updated)
    original_identities = {_members_identity(members)
                           for members in cells.values()}
    zero_case_failures = (
        set(explicit_state['failures']) - original_identities
        if explicit_state is not None else set())
    ids = [case.get('id') for items in cells.values() for case, _ in items]
    numeric_ids = [value for value in ids if isinstance(value, int)]
    next_id = (max(numeric_ids) + 1) if numeric_ids else 1
    rng = random.Random(seed)
    eligible = _opener_eligible(profile)
    assessment = _opening_assessment(profile)
    next_id, added = _repair_explicit_slots(
        updated, profile, rng, next_id, ew_samples, solve_table, assessment,
        explicit_state)
    cells = _report_cases(updated)
    failed_identities = (set(explicit_state['failures'])
                         if explicit_state is not None else set())
    repair_created_identities = zero_case_failures - failed_identities
    attempted = 0
    skipped = []
    unreached = []
    discovered = []

    work = []
    for cell_key, members in sorted(cells.items()):
        if _members_identity(members) in failed_identities:
            continue
        groups: dict[tuple, list[Mapping]] = {}
        for case, status in members:
            groups.setdefault(_process_group_key(case, status), []).append(case)
        needed = {key: target_pairs - len(cases)
                  for key, cases in groups.items()
                  if len(cases) < target_pairs}
        if (not needed
                and not (allow_new_processes
                         and _members_identity(members)
                         in repair_created_identities)):
            continue
        spec = _cell_spec(members)
        if spec is None:
            skipped.append(cell_key)
            continue
        work.append((cell_key, members, groups, needed, spec))
    total_missing = sum(sum(needed.values()) for *_, needed, _ in work)
    initial_missing = total_missing
    discovered_index = {}

    for cell_key, members, groups, needed, spec in work:
        remaining_before = sum(needed.values())
        attempts = 0
        attempt_cap = max_attempts_per_cell or max(200, remaining_before * 20)
        allocate_slot = _slot_allocator(members)
        cell_added = 0
        idle_attempts = 0
        added_cases = []
        while attempts < attempt_cap:
            discovery_phase = not any(needed.values())
            if discovery_phase:
                if not allow_new_processes:
                    break
                if (discovery_idle_limit is not None
                        and idle_attempts >= discovery_idle_limit):
                    break
            attempts += 1
            attempted += 1
            try:
                if spec['explicit']:
                    if assessment is None:
                        skipped.append(cell_key)
                        break
                    hands = _sample_explicit(
                        rng, spec, members, added_cases, assessment)
                else:
                    hands = sample_partnership(
                        rng, spec['south_hcp'], spec['south_shape'],
                        opener_eligible=eligible,
                        opener_shape=spec['north_shape'],
                        opener_hcp=spec['north_hcp'],
                        reference=spec['reference'],
                    )
            except (JointConstraintError, RuntimeError) as exc:
                skipped.append(cell_key)
                break
            simulation = simulate_auction(
                profile, {'n': hands['n'], 's': hands['s']}, dealer='n',
                vulnerability='none',
                environment={'dealer': 'n', 'vulnerability': 'none',
                             'scoring': 'IMP'}, max_calls=80,
            )
            contract = declarer = None
            if simulation.status == 'complete':
                if not simulation.calls or simulation.calls[0] != '1N':
                    raise RuntimeError(
                        f'{cell_key}: sampled North did not open 1NT')
                contract, declarer = _contract(simulation.calls)
            key = _simulation_group_key(simulation, contract, declarer)
            created_new = False
            if key not in groups:
                if not allow_new_processes or any(needed.values()):
                    if discovery_phase:
                        idle_attempts += 1
                    continue
                groups[key] = []
                needed[key] = target_pairs
                total_missing += target_pairs
                item = {
                    'cell': cell_key,
                    'auction': ' '.join(str(call) for call in simulation.calls),
                    'status': simulation.status,
                    'target_pairs': target_pairs,
                    'pairs_added': 0,
                    'remaining': target_pairs,
                }
                discovered.append(item)
                discovered_index[(cell_key, key)] = item
                created_new = True
                idle_attempts = 0
            if needed.get(key, 0) <= 0:
                if discovery_phase and not created_new:
                    idle_attempts += 1
                continue
            slot = allocate_slot() if allocate_slot is not None else None
            case = _new_case(next_id, hands, simulation,
                             cell_meta=spec['coverage_cell'],
                             pair_slot=slot)
            sampled_key = case_cell_key(case)
            if sampled_key != cell_key:
                raise RuntimeError(
                    f'{cell_key}: sampled pair landed in {sampled_key}')
            next_id += 1
            added += 1
            cell_added += 1
            needed[key] -= 1
            groups[key].append(case)
            added_cases.append(case)
            item = discovered_index.get((cell_key, key))
            if item is not None:
                item['pairs_added'] += 1
                item['remaining'] = needed[key]
            if simulation.status == 'blocked':
                case.update(blocked=simulation.blocked,
                            review_status='unreviewed')
                updated.setdefault('cases', []).append(case)
            elif simulation.status == 'complete':
                case.update(contract=contract, declarer=declarer)
                boards = []
                for index in range(ew_samples):
                    deal = (hands if index == 0
                            else complete_opponents(rng, hands['n'], hands['s']))
                    boards.append(solve_table(deal))
                case['dds_tables'] = boards
                updated.setdefault('complete_cases', []).append(case)
            else:
                case['status'] = 'limit'
                updated.setdefault('limit_cases', []).append(case)
        for key, remaining in needed.items():
            if remaining > 0:
                sample = groups[key][0]
                unreached.append({
                    'cell': cell_key, 'auction': _auction_label(sample),
                    'status': key[-1], 'existing_pairs': len(groups[key]),
                    'remaining': remaining,
                })
        if progress is not None:
            progress({
                'cell': cell_key, 'cell_added': cell_added,
                'cell_attempts': attempts,
                'cell_remaining': sum(needed.values()),
                'added_pairs': added, 'total_missing': total_missing,
            }, total_missing)

    updated['budget'] = {**budget, 'pairs_per_process_cell': target_pairs,
                         'ew_samples': ew_samples}
    updated['wrong_game_rule'] = RULE_ID
    updated['extension'] = {
        'kind': 'process_pair_topup', 'target_pairs': target_pairs,
        'added_pairs': added, 'attempted_pairs': attempted,
        'initial_missing_pairs': initial_missing,
        'seed': seed, 'ew_samples': ew_samples,
        'max_attempts_per_cell': max_attempts_per_cell,
        'allow_new_processes': allow_new_processes,
        'discovery_idle_limit': discovery_idle_limit,
        'new_process_groups': len(discovered),
        'discovered_processes': discovered,
        'skipped_cells': skipped, 'unreached_groups': unreached,
    }
    _refresh_analysis(updated)
    _refresh_block_points(updated)
    _refresh_north_summary(updated)
    return updated


def _refresh_north_summary(report: Mapping) -> None:
    north = (report.get('coverage') or {}).get('north')
    if not isinstance(north, Mapping) or north.get('schema_status') != 'explicit':
        return
    cells = []
    assignments = {}
    for item in north.get('requested_strata') or ():
        cell = item.get('cell')
        if not isinstance(cell, Mapping):
            continue
        identity = (cell.get('target_hcp'), cell.get('base_shape_index'))
        if not all(isinstance(value, int) and not isinstance(value, bool)
                   for value in identity):
            continue
        cells.append({'target_hcp': identity[0],
                      'base_shape_index': identity[1]})
        assignments[identity] = OpenerStratum(
            tuple(item['shape']), item['mode'])
    generated = Counter()
    hcp_by_mode = {'normal': set(), 'upgrade_14': set(), 'soft_18': set()}
    for key in ('cases', 'complete_cases', 'limit_cases'):
        for case in report.get(key, []):
            cell = case.get('coverage_cell') or {}
            if 'opener_shape' not in cell or 'opener_mode' not in cell:
                continue
            identity = (cell.get('target_hcp'), cell.get('base_shape_index'))
            generated[identity] += 1
            if cell['opener_mode'] in hcp_by_mode:
                hcp_by_mode[cell['opener_mode']].add(case.get('north_hcp'))
    report['coverage']['north'] = build_north_summary(
        cells=cells, assignments=assignments,
        generated_pairs=dict(generated), north_hcp_by_mode=hcp_by_mode,
        cell_failures=list(north.get('cell_failures') or ()))


def _refresh_analysis(report: Mapping) -> None:
    budget = report.get('budget') or {}
    min_boards = budget.get('min_class_boards', 10)
    min_pairs = budget.get('min_class_pairs', 1)
    if not isinstance(min_boards, int) or isinstance(min_boards, bool) or min_boards < 1:
        min_boards = 10
    if not isinstance(min_pairs, int) or isinstance(min_pairs, bool) or min_pairs < 1:
        min_pairs = 1
    complete = report.get('complete_cases', [])
    suspicious_cases = []
    flagged_groups = 0
    unassessed = 0
    for members, analysis in assess_auction_groups(
            complete, min_boards=min_boards, min_pairs=min_pairs):
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
                unassessed += 1
        if analysis['flags']:
            flagged_groups += 1
            suspicious_cases.extend(members)
    report['suspicious_cases'] = suspicious_cases
    summary = dict(report.get('summary') or {})
    summary.update({
        'pairs': (len(report.get('cases', []))
                  + len(report.get('complete_cases', []))
                  + len(report.get('limit_cases', []))),
        'complete': len(report.get('complete_cases', [])),
        'blocked': len(report.get('cases', [])),
        'limit': len(report.get('limit_cases', [])),
        'dds_boards': sum(len(case.get('dds_tables') or ())
                          for case in report.get('complete_cases', [])),
        'suspicious': flagged_groups,
        'unassessed': unassessed,
    })
    report['summary'] = summary


def _refresh_block_points(report: Mapping) -> None:
    points = Counter()
    first = {}
    for case in report.get('cases', []):
        blocked = case.get('blocked') or {}
        auction = blocked.get('auction')
        seat = blocked.get('seat')
        if not isinstance(auction, str) or not isinstance(seat, str):
            continue
        points[(auction, seat)] += 1
        first.setdefault((auction, seat), case.get('id'))
    report['block_points'] = [
        {'auction': auction, 'seat': seat, 'count': count,
         'first_trial': first[(auction, seat)],
         'strata': {'coverage': count}}
        for (auction, seat), count in sorted(
            points.items(), key=lambda item: (-item[1], item[0]))
    ]


def extend_ns_pairs(
    report: Mapping,
    profile,
    *,
    target_pairs: int = 10,
    ew_samples: int | None = None,
    seed: int = 41,
    solve_table: Callable = calculate_available_table,
    progress: Callable[[dict, int], None] | None = None,
) -> dict:
    """Add N/S pairs to every existing sampling cell below ``target_pairs``."""
    if report.get('schema_version') != 2:
        raise ValueError('source must be a coverage report (schema version 2)')
    if not isinstance(target_pairs, int) or isinstance(target_pairs, bool) or target_pairs < 1:
        raise ValueError('target_pairs must be a positive integer')
    budget = report.get('budget') or {}
    declared = budget.get('pairs_per_cell', 1)
    if not isinstance(declared, int) or isinstance(declared, bool) or declared < 1:
        declared = 1
    effective_target = max(target_pairs, declared)
    if ew_samples is None:
        ew_samples = budget.get('ew_samples', 10)
    if not isinstance(ew_samples, int) or isinstance(ew_samples, bool) or not 1 <= ew_samples <= 20:
        raise ValueError('ew_samples must be an integer from 1 to 20')

    updated = json.loads(json.dumps(report))
    explicit_state = _validate_explicit_report(updated)
    cells = _report_cases(updated)
    ids = [case.get('id') for items in cells.values() for case, _ in items]
    numeric_ids = [value for value in ids if isinstance(value, int)]
    next_id = (max(numeric_ids) + 1) if numeric_ids else 1
    rng = random.Random(seed)
    eligible = _opener_eligible(profile)
    assessment = _opening_assessment(profile)
    next_id, added = _repair_explicit_slots(
        updated, profile, rng, next_id, ew_samples, solve_table, assessment,
        explicit_state)
    cells = _report_cases(updated)
    failed_identities = (set(explicit_state['failures'])
                         if explicit_state is not None else set())
    skipped = []
    missing_cells = []
    for cell_key, members in sorted(cells.items()):
        if _members_identity(members) in failed_identities:
            continue
        missing = effective_target - len(members)
        if missing <= 0:
            continue
        spec = _cell_spec(members)
        if spec is None:
            skipped.append(cell_key)
            continue
        missing_cells.append((cell_key, members, spec, missing))
    total_missing = sum(item[3] for item in missing_cells)
    for cell_key, members, spec, missing in missing_cells:
        slot = _next_pair_slot(members, effective_target)
        added_cases = []
        for _ in range(missing):
            try:
                if spec['explicit']:
                    if assessment is None:
                        skipped.append(cell_key)
                        break
                    hands = _sample_explicit(
                        rng, spec, members, added_cases, assessment)
                else:
                    hands = sample_partnership(
                        rng, spec['south_hcp'], spec['south_shape'],
                        opener_eligible=eligible,
                        opener_shape=spec['north_shape'],
                        opener_hcp=spec['north_hcp'],
                        reference=spec['reference'],
                    )
            except (JointConstraintError, RuntimeError) as exc:
                raise RuntimeError(
                    f'{cell_key}: could not sample another N/S pair: {exc}'
                ) from exc
            simulation = simulate_auction(
                profile, {'n': hands['n'], 's': hands['s']}, dealer='n',
                vulnerability='none',
                environment={'dealer': 'n', 'vulnerability': 'none',
                             'scoring': 'IMP'}, max_calls=80,
            )
            if not simulation.calls or simulation.calls[0] != '1N':
                raise RuntimeError(
                    f'{cell_key}: sampled North did not open 1NT')
            case = _new_case(next_id, hands, simulation,
                             cell_meta=spec['coverage_cell'],
                             pair_slot=slot)
            sampled_key = case_cell_key(case)
            if sampled_key != cell_key:
                raise RuntimeError(
                    f'{cell_key}: sampled pair landed in {sampled_key}')
            next_id += 1
            if slot is not None:
                slot += 1
            added += 1
            added_cases.append(case)
            if simulation.status == 'blocked':
                case.update(blocked=simulation.blocked,
                            review_status='unreviewed')
                updated.setdefault('cases', []).append(case)
            elif simulation.status == 'complete':
                contract, declarer = _contract(simulation.calls)
                case.update(contract=contract, declarer=declarer)
                boards = []
                for index in range(ew_samples):
                    deal = (hands if index == 0
                            else complete_opponents(rng, hands['n'], hands['s']))
                    boards.append(solve_table(deal))
                case['dds_tables'] = boards
                updated.setdefault('complete_cases', []).append(case)
            else:
                case['status'] = 'limit'
                updated.setdefault('limit_cases', []).append(case)
            if progress is not None:
                progress({'added_pairs': added, 'total_missing': total_missing,
                          'cell': cell_key}, total_missing)

    updated['budget'] = {**budget, 'pairs_per_cell': effective_target,
                         'ew_samples': ew_samples}
    updated['wrong_game_rule'] = RULE_ID
    updated['extension'] = {
        'kind': 'ns_pair_topup', 'target_pairs': effective_target,
        'declared_pairs_per_cell': declared, 'added_pairs': added,
        'seed': seed, 'ew_samples': ew_samples, 'skipped_cells': skipped,
    }
    _refresh_analysis(updated)
    _refresh_block_points(updated)
    _refresh_north_summary(updated)
    return updated


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description='Top up undersized N/S sampling cells in a coverage report')
    parser.add_argument('report', type=Path)
    parser.add_argument('--profile', default=None)
    parser.add_argument('--target-pairs', type=int, default=10)
    parser.add_argument('--scope', choices=('process', 'sampling'), default='process',
                        help='process: top up each auction-process cell; '
                             'sampling: top up each HCP/shape sampling cell')
    parser.add_argument('--max-attempts-per-cell', type=int, default=None,
                        help='sampling attempts allowed per cell in process scope')
    parser.add_argument('--discard-new-processes', action='store_true',
                        help='discard auctions not already present in the report')
    parser.add_argument('--discovery-idle-limit', type=int, default=100,
                        help='stop discovery after this many consecutive attempts '
                             'without a new process (0 disables discovery)')
    parser.add_argument('--ew-samples', type=int, default=None)
    parser.add_argument('--seed', type=int, default=41)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)

    from .block_report_viewer import render_html
    from .loader import load_profile

    source = json.loads(args.report.read_text(encoding='utf-8'))
    if not isinstance(source, Mapping):
        raise ValueError('report must be a JSON object')
    profile_id = args.profile or (source.get('profile') or {}).get('id')
    if not isinstance(profile_id, str) or not profile_id:
        raise ValueError('report has no profile id; pass --profile')

    def progress(state, total):
        print(f"{state.get('added_pairs', 0)}/{total}: {state['cell']} "
              f"added {state.get('cell_added', 1)} "
              f"attempts {state.get('cell_attempts', '-')} "
              f"remaining {state.get('cell_remaining', 0)}", flush=True)

    if args.scope == 'process':
        report = extend_process_pairs(
            source, load_profile(profile_id),
            target_pairs=args.target_pairs, ew_samples=args.ew_samples,
            seed=args.seed, max_attempts_per_cell=args.max_attempts_per_cell,
            allow_new_processes=not args.discard_new_processes,
            discovery_idle_limit=args.discovery_idle_limit,
            progress=progress,
        )
    else:
        report = extend_ns_pairs(
            source, load_profile(profile_id),
            target_pairs=args.target_pairs, ew_samples=args.ew_samples,
            seed=args.seed, progress=progress,
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, separators=(',', ':')) + '\n',
        encoding='utf-8')
    html_path = args.output.with_suffix('.html')
    html_path.write_text(render_html(report), encoding='utf-8')
    extension = report['extension']
    detail = ''
    if extension['kind'] == 'process_pair_topup':
        detail = (f"; {extension['attempted_pairs']} sampling attempts; "
                  f"{extension['new_process_groups']} new process groups; "
                  f"{len(extension['unreached_groups'])} process groups below target")
    print(f"{extension['added_pairs']} pairs added; "
          f"{report['summary']['pairs']} total pairs; "
          f"{report['summary']['dds_boards']} DDS boards; "
          f"{len(extension['skipped_cells'])} cells skipped{detail}. "
          f"Report: {args.output}; viewer: {html_path}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
