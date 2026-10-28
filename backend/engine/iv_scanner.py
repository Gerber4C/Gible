"""Local, bounded IV Scanner jobs and compact browser-facing reports."""

from __future__ import annotations

import json
import math
import re
import threading
import uuid
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path

from .block_report_viewer import render_html
from .coverage_scan import COVERAGE_SHAPES, scan_coverage
from .loader import load_profile
from .outcome_metrics import (
    RULE_ID, assess_auction_groups, board_result, case_process_key,
    reclassify_analysis,
)


REPORT_ROOT = Path(__file__).resolve().parents[2] / 'reports' / 'block_scans'
FLAG_CATEGORY = {
    'contract_failure': 'down',
    'missed_game': 'missed',
    'missed_small_slam': 'missed',
    'missed_grand_slam': 'missed',
    'wrong_game': 'wrong',
}


def _json_safe(value):
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [_json_safe(item) for item in value]
    return value


def scan_options(request: dict) -> dict:
    """Validate a bounded North-1NT scan request."""
    if not isinstance(request, dict) or set(request) - {
            'profile', 'seed', 'hcp_min', 'hcp_max',
            'pairs_per_cell', 'ew_samples'}:
        raise ValueError('Unsupported scanner setting')
    profile_id = request.get('profile', 'daqiush_2over1')
    if not isinstance(profile_id, str) or not re.fullmatch(r'[A-Za-z0-9_-]+', profile_id):
        raise ValueError('Invalid profile id')
    settings = {'seed': request.get('seed', 23),
                'hcp_min': request.get('hcp_min', 0),
                'hcp_max': request.get('hcp_max', 22),
                'pairs_per_cell': request.get('pairs_per_cell', 2),
                'ew_samples': request.get('ew_samples', 10)}
    bounds = {'seed': (0, 2**32 - 1), 'hcp_min': (0, 22),
              'hcp_max': (0, 22), 'pairs_per_cell': (1, 20),
              'ew_samples': (1, 20)}
    for key, value in settings.items():
        lower, upper = bounds[key]
        if isinstance(value, bool) or not isinstance(value, int) or not lower <= value <= upper:
            raise ValueError(f'{key} must be an integer from {lower} to {upper}')
    if settings['hcp_min'] > settings['hcp_max']:
        raise ValueError('hcp_min cannot exceed hcp_max')
    settings.update(profile=profile_id, shapes=COVERAGE_SHAPES)
    settings['planned_pairs'] = ((settings['hcp_max'] - settings['hcp_min'] + 1)
                                 * len(settings['shapes']) * settings['pairs_per_cell'])
    return settings


def _valid_hcp(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and 0 <= value <= 37


def _valid_shape(value) -> bool:
    return (isinstance(value, (list, tuple)) and len(value) == 4
            and all(isinstance(length, int) and not isinstance(length, bool)
                    and length >= 0 for length in value)
            and sum(value) == 13)


def _cell_identity(case: dict) -> tuple[str, int | None, list[int] | None, int | None, bool]:
    cell = case.get('coverage_cell')
    if isinstance(cell, dict):
        hcp = cell.get('target_hcp')
        shape = cell.get('base_shape')
        shape_index = cell.get('base_shape_index')
        pair_slot = cell.get('pair_slot')
        if (_valid_hcp(hcp) and _valid_shape(shape)
                and isinstance(shape_index, int) and not isinstance(shape_index, bool)
                and shape_index >= 0
                and isinstance(pair_slot, int) and not isinstance(pair_slot, bool)
                and pair_slot >= 0):
            return f'{hcp}:{shape_index}', hcp, list(shape), pair_slot, False
    hcp = case.get('south_hcp')
    shape = case.get('south_shape')
    if _valid_hcp(hcp) and _valid_shape(shape):
        shape = list(shape)
        return f"legacy:{hcp}:{'-'.join(map(str, shape))}", hcp, shape, None, False
    return f"legacy-fallback:{case.get('id')}", (
        hcp if _valid_hcp(hcp) else None), (
        list(shape) if _valid_shape(shape) else None), None, True


def _id_sort_key(value):
    return (0, value) if isinstance(value, int) else (1, str(value))


def _auction_label(case: dict) -> str:
    auction = case.get('auction')
    if isinstance(auction, str) and auction:
        return auction
    calls = case.get('calls')
    if isinstance(calls, (list, tuple)) and calls:
        return ' '.join(str(call) for call in calls)
    return 'no-calls'


def _pair_projection(case: dict, status: str, pair_slot: int | None,
                     analysis: dict | None, categories: list[str],
                     *, include_results: bool = True) -> dict:
    hands = case.get('hands') or {}
    pair = {
        'id': case.get('id'), 'pair_slot': pair_slot, 'status': status,
        'categories': categories,
        'hands': {seat: hands[seat] for seat in 'ns' if seat in hands},
        'north_hcp': case.get('north_hcp'), 'south_hcp': case.get('south_hcp'),
        'north_kr': case.get('north_kr'), 'south_kr': case.get('south_kr'),
        'north_shape': case.get('north_shape'), 'south_shape': case.get('south_shape'),
        'auction': case.get('auction'), 'calls': case.get('calls'),
        'coverage_cell': case.get('coverage_cell'),
    }
    if status == 'blocked':
        pair['blocked'] = case.get('blocked')
    elif status == 'complete':
        contract = case.get('contract')
        declarer = case.get('declarer')
        tables = case.get('dds_tables')
        results = []
        if (include_results and isinstance(contract, str) and declarer in ('n', 's')
                and isinstance(tables, list)):
            results = [board_result(contract, declarer, table) for table in tables]
        analysis = analysis or {}
        pair.update({
            'contract': contract, 'declarer': declarer, 'ew_results': results,
            'flags': list(analysis.get('flags') or ()),
            'rates': analysis.get('rates', {}),
            'alternative_game_rates': analysis.get('alternative_game_rates', {}),
            'wrong_game_comparison': analysis.get('wrong_game_comparison', {}),
            'analysis_status': analysis.get('status'),
            'class_pairs': analysis.get('class_pairs'),
            'dds_boards': analysis.get('dds_boards'),
        })
    return pair


def _north_coverage(report: Mapping) -> dict:
    """Return explicit North coverage or a strict legacy marker."""
    north = (report.get('coverage') or {}).get('north')
    if isinstance(north, Mapping) and north.get('schema_status') == 'explicit':
        return dict(north)
    return {'schema_status': 'legacy'}


def _budget_minimums(report: Mapping) -> tuple[int, int]:
    budget = report.get('budget') or {}
    min_boards = budget.get('min_class_boards', 10)
    min_pairs = budget.get('min_class_pairs', 1)
    if not isinstance(min_boards, int) or isinstance(min_boards, bool) or min_boards < 1:
        min_boards = 10
    if not isinstance(min_pairs, int) or isinstance(min_pairs, bool) or min_pairs < 1:
        min_pairs = 1
    return min_boards, min_pairs


def project_report(report: dict, report_id: str, *,
                   include_pairs: bool = True) -> dict:
    """Project every sampling cell split by its distinct bidding processes."""
    if not isinstance(report, Mapping) or report.get('schema_version') != 2:
        raise ValueError('Expected a coverage scan report')
    budget = report.get('budget')
    if not isinstance(budget, Mapping):
        raise ValueError('Coverage scan budget must be a mapping')
    collections = {
        'cases': report.get('cases'),
        'complete_cases': report.get('complete_cases', []),
        'limit_cases': report.get('limit_cases', []),
    }
    if any(not isinstance(items, list)
           or any(not isinstance(item, Mapping) for item in items)
           for items in collections.values()):
        raise ValueError('Coverage scan cases must be lists of mappings')
    expected = budget.get('pairs_per_cell', 1)
    if not isinstance(expected, int) or isinstance(expected, bool) or expected < 1:
        expected = 1
    process_target = budget.get('pairs_per_process_cell')
    if not isinstance(process_target, int) or isinstance(process_target, bool) or process_target < 1:
        process_target = None
    min_boards, min_pairs = _budget_minimums(report)

    complete = collections['complete_cases']
    analyses = {}
    for members, analysis in assess_auction_groups(
            complete, min_boards=min_boards, min_pairs=min_pairs):
        for member in members:
            analyses[member.get('id')] = analysis

    records = [*((case, 'blocked') for case in collections['cases']),
               *((case, 'complete') for case in complete),
               *((case, 'limit') for case in collections['limit_cases'])]
    records.sort(key=lambda item: _id_sort_key(item[0].get('id')))

    parent_counts = {}
    parent_pairs = {}
    for case, _ in records:
        cell_id, _, _, _, _ = _cell_identity(case)
        parent_counts[cell_id] = parent_counts.get(cell_id, 0) + 1
        parent_pairs.setdefault(cell_id, []).append(case)
    legacy_slots = {}
    for cell_id, members in parent_pairs.items():
        if all(_cell_identity(case)[3] is None for case in members):
            for slot, case in enumerate(members):
                legacy_slots[id(case)] = slot

    grouped = {}
    for case, status in records:
        cell_id, south_hcp, south_shape, pair_slot, fallback = _cell_identity(case)
        if pair_slot is None:
            pair_slot = legacy_slots.get(id(case))
        process = case_process_key(case)
        key = (cell_id, process,
               case.get('contract') if status == 'complete' else None,
               case.get('declarer') if status == 'complete' else None,
               status)
        group = grouped.setdefault(key, {
            'cell_id': cell_id, 'south_hcp': south_hcp,
            'south_shape': south_shape, 'fallback': fallback,
            'auction': _auction_label(case), 'entries': [],
        })
        group['entries'].append((case, status, pair_slot))

    def pair_order(entry):
        case, _, slot = entry
        return (slot is None, slot if slot is not None else 0,
                _id_sort_key(case.get('id')))

    groups = []
    used_ids = set()
    counts = {'block': 0, 'missed': 0, 'down': 0, 'wrong': 0}
    total_unassessed = 0
    for group in grouped.values():
        entries = sorted(group['entries'], key=pair_order)
        complete_members = [case for case, status, _ in entries if status == 'complete']
        group_analysis = None
        if complete_members:
            group_analysis = analyses.get(complete_members[0].get('id'))
        group_categories = set()
        pairs = []
        unassessed = 0
        for case, status, pair_slot in entries:
            cell = case.get('coverage_cell') or {}
            if 'opener_shape' in cell and 'opener_shape' not in group:
                group['opener_shape'] = cell.get('opener_shape')
                group['opener_mode'] = cell.get('opener_mode')
            analysis = None
            categories = []
            if status == 'blocked':
                categories = ['block']
            elif status == 'complete':
                analysis = analyses.get(case.get('id'))
                if analysis is None:
                    analysis = reclassify_analysis(
                        case.get('contract'), case.get('analysis') or {})
                if analysis.get('status') != 'assessed':
                    unassessed += 1
                categories = sorted({FLAG_CATEGORY[flag]
                                     for flag in analysis.get('flags') or ()
                                     if flag in FLAG_CATEGORY})
            group_categories.update(categories)
            if include_pairs:
                pairs.append(_pair_projection(
                    case, status, pair_slot, analysis, categories))
        warning_counts = {category: int(category in group_categories)
                          for category in counts}
        for category in group_categories:
            counts[category] += 1
        base_id = f"{group['cell_id']}|{group['auction']}"
        group_id = base_id
        suffix = 2
        while group_id in used_ids:
            group_id = f"{base_id}#{suffix}"
            suffix += 1
        used_ids.add(group_id)
        group_data = {
            'id': group_id, 'parent_id': group['cell_id'],
            'south_hcp': group['south_hcp'],
            'south_shape': group['south_shape'],
            'auction': group['auction'],
            'warning_counts': warning_counts,
            'actual_pair_count': len(entries),
            'parent_pair_count': parent_counts[group['cell_id']],
            'expected_pair_count': process_target or expected,
            'incomplete': (
                len(entries) != process_target
                if process_target is not None
                else parent_counts[group['cell_id']] != expected),
            'pairs': pairs,
        }
        if group.get('opener_shape') is not None:
            group_data['opener_shape'] = group['opener_shape']
            group_data['opener_mode'] = group['opener_mode']
        groups.append(group_data)
        total_unassessed += unassessed

    summary = dict(report.get('summary') or {})
    summary['suspicious'] = sum(
        1 for group in groups if any(group['warning_counts'].values()))
    summary['unassessed'] = total_unassessed
    return _json_safe({
        'id': report_id, 'profile': report.get('profile'),
        'seed': report.get('seed'), 'filters': report.get('filters'),
        'budget': report.get('budget'), 'summary': summary,
        'wrong_game_rule': RULE_ID,
        'coverage': {'north': _north_coverage(report)},
        'counts': counts, 'groups': groups,
        'method_note': report.get('method_note'),
    })


def _report_path(report_id: str, root: Path) -> Path:
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*\.json', report_id):
        raise ValueError('Invalid scanner report id')
    path = (root / report_id).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError('Invalid scanner report id')
    return path


def read_report(report_id: str, root: Path = REPORT_ROOT) -> dict:
    path = _report_path(report_id, root)
    if not path.is_file():
        raise FileNotFoundError(report_id)
    return project_report(json.loads(path.read_text(encoding='utf-8')), report_id)


def list_reports(root: Path = REPORT_ROOT) -> list[dict]:
    if not root.exists():
        return []
    results = []
    for path in root.glob('*.json'):
        if 'coverage' not in path.stem and not path.stem.startswith('iv-scan-'):
            continue
        try:
            report = json.loads(path.read_text(encoding='utf-8'))
            if (not isinstance(report, Mapping)
                    or report.get('schema_version') != 2
                    or not isinstance(report.get('cases'), list)):
                continue
            projected = project_report(report, path.name, include_pairs=False)
        except (OSError, ValueError, KeyError, TypeError):
            continue
        results.append({'id': path.name, 'profile': projected['profile'],
                        'seed': projected['seed'], 'summary': projected['summary'],
                        'wrong_game_rule': projected['wrong_game_rule'],
                        'counts': projected['counts'], 'budget': projected['budget'],
                        'modified_at': datetime.fromtimestamp(
                            path.stat().st_mtime, timezone.utc).isoformat()})
    return sorted(results, key=lambda item: item['modified_at'], reverse=True)


class ScannerJobs:
    """One local background scan at a time; results persist as report files."""

    def __init__(self, root: Path = REPORT_ROOT):
        self.root = root
        self._lock = threading.Lock()
        self._current: dict | None = None

    def status(self) -> dict | None:
        with self._lock:
            return dict(self._current) if self._current else None

    def start(self, request: dict) -> dict:
        options = scan_options(request)
        profile = load_profile(options['profile'])
        with self._lock:
            if self._current and self._current['status'] in ('queued', 'running'):
                raise ValueError('A scanner run is already in progress')
            job_id = uuid.uuid4().hex[:12]
            self._current = {'id': job_id, 'status': 'queued',
                             'profile': options['profile'],
                             'planned_pairs': options['planned_pairs'],
                             'completed_pairs': 0, 'dds_boards': 0,
                             'report_id': None, 'snapshot_pairs': 0,
                             'error': None}
            snapshot = dict(self._current)
        threading.Thread(target=self._run, args=(job_id, options, profile),
                         daemon=True, name='iv-scanner').start()
        return snapshot

    def _run(self, job_id: str, options: dict, profile) -> None:
        def progress(summary: dict, total: int) -> None:
            with self._lock:
                if self._current and self._current['id'] == job_id:
                    self._current.update(status='running',
                                         completed_pairs=summary['pairs'],
                                         planned_pairs=total,
                                         dds_boards=summary['dds_boards'])

        timestamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        stem = f"iv-scan-{options['profile']}-{timestamp}-{job_id}"
        self.root.mkdir(parents=True, exist_ok=True)
        json_path = self.root / f'{stem}.json'
        html_path = self.root / f'{stem}.html'
        temporary = self.root / f'{stem}.json.tmp'

        def snapshot(report: dict) -> None:
            # Atomic write so the browser never reads a half-written report.
            temporary.write_text(
                json.dumps(report, ensure_ascii=False) + '\n',
                encoding='utf-8')
            temporary.replace(json_path)
            with self._lock:
                if self._current and self._current['id'] == job_id:
                    self._current.update(
                        report_id=json_path.name,
                        snapshot_pairs=(report.get('summary') or {}).get('pairs', 0))

        try:
            report = scan_coverage(
                profile, seed=options['seed'],
                hcp_targets=tuple(range(options['hcp_min'], options['hcp_max'] + 1)),
                shapes=options['shapes'], pairs_per_cell=options['pairs_per_cell'],
                ew_samples=options['ew_samples'], progress=progress,
                snapshot=snapshot,
                snapshot_every=options.get('snapshot_every', 20))
            snapshot(report)
            html_path.write_text(render_html(report), encoding='utf-8')
            with self._lock:
                self._current.update(status='completed',
                                     report_id=json_path.name,
                                     completed_pairs=report['summary']['pairs'],
                                     dds_boards=report['summary']['dds_boards'])
        except Exception as exc:
            with self._lock:
                self._current.update(status='failed', error=str(exc))
