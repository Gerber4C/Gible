"""Local, bounded IV Scanner jobs and compact browser-facing reports."""

from __future__ import annotations

import json
import re
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .block_report_viewer import render_html
from .coverage_scan import COVERAGE_SHAPES, scan_coverage
from .loader import load_profile


REPORT_ROOT = Path(__file__).resolve().parents[2] / 'reports' / 'block_scans'
FLAG_CATEGORY = {
    'contract_failure': 'down',
    'missed_game': 'missed',
    'missed_small_slam': 'missed',
    'missed_grand_slam': 'missed',
    'wrong_game': 'wrong',
}


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


def project_report(report: dict, report_id: str) -> dict:
    """Strip DDS tables while keeping every actionable numbered case."""
    if report.get('schema_version') != 2 or not isinstance(report.get('cases'), list):
        raise ValueError('Expected a coverage scan report')
    cases = []
    counts = {'block': 0, 'missed': 0, 'down': 0, 'wrong': 0}
    all_cases = sorted([*report['cases'], *report.get('complete_cases', [])],
                       key=lambda item: item['id'])
    for case in all_cases:
        flags = case.get('analysis', {}).get('flags', ())
        categories = (['block'] if 'blocked' in case else
                      sorted({FLAG_CATEGORY[flag] for flag in flags
                              if flag in FLAG_CATEGORY}))
        if not categories:
            continue
        for category in categories:
            counts[category] += 1
        analysis = case.get('analysis', {})
        contract = case.get('contract')
        declarer = case.get('declarer')
        ew_results = []
        if (isinstance(contract, str) and len(contract) >= 2
                and declarer in 'ns' and isinstance(case.get('dds_tables'), list)):
            level = int(contract[0])
            strain = 'NT' if contract[1:] == 'NT' else contract[1]
            for table in case['dds_tables']:
                tricks = table.get(strain, {}).get(declarer)
                ew_results.append('made' if isinstance(tricks, int) and tricks >= level + 6
                                  else 'down')
        cases.append({
            'id': case['id'], 'categories': categories,
            'hands': {seat: case['hands'][seat] for seat in 'ns'},
            'north_hcp': case['north_hcp'], 'south_hcp': case['south_hcp'],
            'north_kr': case['north_kr'], 'south_kr': case['south_kr'],
            'north_shape': case['north_shape'], 'south_shape': case['south_shape'],
            'auction': case['auction'], 'calls': case['calls'],
            'contract': contract, 'declarer': declarer, 'ew_results': ew_results,
            'blocked': case.get('blocked'), 'flags': list(flags),
            'rates': analysis.get('rates', {}),
            'alternative_game_rates': analysis.get('alternative_game_rates', {}),
            'class_pairs': analysis.get('class_pairs'),
            'dds_boards': analysis.get('dds_boards'),
        })
    return {
        'id': report_id, 'profile': report.get('profile'),
        'seed': report.get('seed'), 'filters': report.get('filters'),
        'budget': report.get('budget'), 'summary': report.get('summary'),
        'counts': counts, 'cases': cases,
        'method_note': report.get('method_note'),
    }


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
            if report.get('schema_version') != 2 or not isinstance(report.get('cases'), list):
                continue
            projected = project_report(report, path.name)
        except (OSError, ValueError, KeyError, TypeError):
            continue
        results.append({'id': path.name, 'profile': projected['profile'],
                        'seed': projected['seed'], 'summary': projected['summary'],
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
