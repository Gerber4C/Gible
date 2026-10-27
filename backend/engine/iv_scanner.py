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
from .outcome_metrics import RULE_ID, board_result, reclassify_analysis


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


def _pair_projection(case: dict, status: str, pair_slot: int | None) -> dict:
    analysis = (reclassify_analysis(case.get('contract'), case.get('analysis') or {})
                if status == 'complete' and isinstance(case.get('contract'), str)
                else dict(case.get('analysis') or {}))
    flags = list(analysis.get('flags') or ()) if status == 'complete' else []
    categories = (['block'] if status == 'blocked' else
                  sorted({FLAG_CATEGORY[flag] for flag in flags
                          if flag in FLAG_CATEGORY}))
    hands = case.get('hands') or {}
    pair = {
        'id': case.get('id'), 'pair_slot': pair_slot, 'status': status,
        'categories': categories,
        'hands': {seat: hands[seat] for seat in 'ns' if seat in hands},
        'north_hcp': case.get('north_hcp'), 'south_hcp': case.get('south_hcp'),
        'north_kr': case.get('north_kr'), 'south_kr': case.get('south_kr'),
        'north_shape': case.get('north_shape'), 'south_shape': case.get('south_shape'),
        'auction': case.get('auction'), 'calls': case.get('calls'),
    }
    if status == 'blocked':
        pair['blocked'] = case.get('blocked')
    elif status == 'complete':
        contract = case.get('contract')
        declarer = case.get('declarer')
        tables = case.get('dds_tables')
        results = []
        if (isinstance(contract, str) and declarer in ('n', 's')
                and isinstance(tables, list)):
            results = [board_result(contract, declarer, table) for table in tables]
        pair.update({
            'contract': contract, 'declarer': declarer, 'ew_results': results,
            'flags': flags, 'rates': analysis.get('rates', {}),
            'alternative_game_rates': analysis.get('alternative_game_rates', {}),
            'wrong_game_comparison': analysis.get('wrong_game_comparison', {}),
            'class_pairs': analysis.get('class_pairs'),
            'dds_boards': analysis.get('dds_boards'),
        })
    return pair


def project_report(report: dict, report_id: str) -> dict:
    """Project actionable sampling cells while retaining all sibling pairs."""
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
    grouped = {}
    records = [*((case, 'blocked') for case in collections['cases']),
               *((case, 'complete') for case in collections['complete_cases']),
               *((case, 'limit') for case in collections['limit_cases'])]
    for case, status in sorted(records, key=lambda item: item[0].get('id', 0)):
        group_id, south_hcp, south_shape, pair_slot, fallback = _cell_identity(case)
        group = grouped.setdefault(group_id, {
            'id': group_id, 'south_hcp': south_hcp, 'south_shape': south_shape,
            'fallback': fallback, 'pairs': [],
        })
        group['pairs'].append(_pair_projection(case, status, pair_slot))

    groups = []
    counts = {'block': 0, 'missed': 0, 'down': 0, 'wrong': 0}
    suspicious = 0
    for group in grouped.values():
        pairs = sorted(group['pairs'], key=lambda pair: (
            pair['pair_slot'] is None,
            pair['pair_slot'] if pair['pair_slot'] is not None else pair['id']))
        if pairs and all(pair['pair_slot'] is None for pair in pairs):
            for slot, pair in enumerate(pairs):
                pair['pair_slot'] = slot
        warning_counts = {category: sum(category in pair['categories'] for pair in pairs)
                          for category in counts}
        if not any(warning_counts.values()) and not group['fallback']:
            continue
        for category, count in warning_counts.items():
            counts[category] += count
        suspicious += sum(pair['status'] == 'complete' and bool(pair['categories'])
                          for pair in pairs)
        groups.append({
            'id': group['id'], 'south_hcp': group['south_hcp'],
            'south_shape': group['south_shape'], 'warning_counts': warning_counts,
            'actual_pair_count': len(pairs), 'expected_pair_count': expected,
            'incomplete': len(pairs) != expected, 'pairs': pairs,
        })
    summary = dict(report.get('summary') or {})
    summary['suspicious'] = suspicious
    return _json_safe({
        'id': report_id, 'profile': report.get('profile'),
        'seed': report.get('seed'), 'filters': report.get('filters'),
        'budget': report.get('budget'), 'summary': summary,
        'wrong_game_rule': RULE_ID,
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
            projected = project_report(report, path.name)
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
                             'report_id': None, 'error': None}
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
        try:
            report = scan_coverage(
                profile, seed=options['seed'],
                hcp_targets=tuple(range(options['hcp_min'], options['hcp_max'] + 1)),
                shapes=options['shapes'], pairs_per_cell=options['pairs_per_cell'],
                ew_samples=options['ew_samples'], progress=progress)
            timestamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
            stem = f"iv-scan-{options['profile']}-{timestamp}-{job_id}"
            self.root.mkdir(parents=True, exist_ok=True)
            json_path = self.root / f'{stem}.json'
            html_path = self.root / f'{stem}.html'
            temporary = self.root / f'{stem}.json.tmp'
            temporary.write_text(json.dumps(report, ensure_ascii=False) + '\n',
                                 encoding='utf-8')
            temporary.replace(json_path)
            html_path.write_text(render_html(report), encoding='utf-8')
            with self._lock:
                self._current.update(status='completed',
                                     report_id=json_path.name,
                                     completed_pairs=report['summary']['pairs'],
                                     dds_boards=report['summary']['dds_boards'])
        except Exception as exc:
            with self._lock:
                self._current.update(status='failed', error=str(exc))
