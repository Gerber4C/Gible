"""Render a block-scout JSON report as a self-contained offline HTML page."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Mapping

from .outcome_metrics import (
    RULE_ID, assess_auction_groups, case_cell_key, case_process_key,
    reclassify_analysis,
)


TEMPLATE = Path(__file__).resolve().parent / 'templates' / 'block_report.html'
PLACEHOLDER = '__BLOCK_REPORT_JSON__'


def _case_id_key(case: Mapping):
    value = case.get('id')
    return (0, value) if isinstance(value, int) else (1, str(value))


def group_suspicious_cases(cases: list[Mapping]) -> list[list[int]]:
    """Group one sampling cell's identical bidding process into one unit."""
    grouped: dict[tuple, list] = {}
    order = []
    for case in sorted(cases, key=_case_id_key):
        key = (case_cell_key(case), case_process_key(case))
        if key not in grouped:
            grouped[key] = []
            order.append(key)
        grouped[key].append(case['id'])
    return [grouped[key] for key in order]


def _budget_minimums(report: Mapping) -> tuple[int, int]:
    budget = report.get('budget') or {}
    min_boards = budget.get('min_class_boards', 10)
    min_pairs = budget.get('min_class_pairs', 1)
    if not isinstance(min_boards, int) or isinstance(min_boards, bool) or min_boards < 1:
        min_boards = 10
    if not isinstance(min_pairs, int) or isinstance(min_pairs, bool) or min_pairs < 1:
        min_pairs = 1
    return min_boards, min_pairs


def _pooled_copies(members, analysis):
    copies = []
    for source in members:
        case = dict(source)
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
    return copies


def render_html(report: Mapping) -> str:
    if not isinstance(report, Mapping) or report.get('schema_version') not in (1, 2):
        raise ValueError('expected a block-scout schema version 1 or coverage schema version 2 report')
    if not isinstance(report.get('cases'), list) or not isinstance(report.get('block_points'), list):
        raise ValueError('report requires cases and block_points lists')
    if report['schema_version'] == 2 and (
            not isinstance(report.get('complete_cases'), list)
            or not isinstance(report.get('suspicious_cases'), list)):
        raise ValueError('coverage report requires complete_cases and suspicious_cases lists')
    if report['schema_version'] == 2:
        report = dict(report)
        min_boards, min_pairs = _budget_minimums(report)
        complete = report['complete_cases']
        eligible = [case for case in complete
                    if isinstance(case, Mapping)
                    and isinstance(case.get('contract'), str)
                    and case.get('declarer') in ('n', 's')]
        complete_cases = []
        suspicious_cases = []
        suspicious_groups = []
        handled = set()
        unhandled = {}
        flagged_groups = 0
        for members, analysis in assess_auction_groups(
                eligible, min_boards=min_boards, min_pairs=min_pairs):
            copies = _pooled_copies(members, analysis)
            complete_cases.extend(copies)
            handled.update(id(member) for member in members)
            if any(case['analysis'].get('flags') for case in copies):
                flagged_groups += 1
                suspicious_groups.append([case['id'] for case in copies])
                suspicious_cases.extend(
                    case for case in copies if case['analysis'].get('flags'))
        for source in complete:
            if id(source) in handled:
                continue
            case = dict(source)
            case['analysis'] = reclassify_analysis(
                case.get('contract'), case.get('analysis') or {})
            unhandled.setdefault(
                (case_cell_key(case), case_process_key(case)), []).append(case)
        for copies in unhandled.values():
            complete_cases.extend(copies)
            if any(case['analysis'].get('flags') for case in copies):
                flagged_groups += 1
                suspicious_groups.append([case.get('id') for case in copies])
                suspicious_cases.extend(
                    case for case in copies if case['analysis'].get('flags'))
        summary = dict(report.get('summary') or {})
        summary['suspicious'] = flagged_groups
        report['complete_cases'] = complete_cases
        report['suspicious_cases'] = suspicious_cases
        report['summary'] = summary
        report['wrong_game_rule'] = RULE_ID
        report['suspicious_groups'] = suspicious_groups
    # JSON is a JavaScript literal here. Escape HTML-significant characters so
    # strings from diagnostics cannot close the inline script element.
    payload = json.dumps(report, ensure_ascii=False, separators=(',', ':'))
    payload = (payload.replace('&', r'\u0026')
               .replace('<', r'\u003c').replace('>', r'\u003e')
               .replace('\u2028', r'\u2028').replace('\u2029', r'\u2029'))
    template = TEMPLATE.read_text(encoding='utf-8')
    if template.count(PLACEHOLDER) != 1:
        raise RuntimeError('block report template has no unique data placeholder')
    return template.replace(PLACEHOLDER, payload)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Visualize a TD scan JSON report offline.')
    parser.add_argument('report', type=Path)
    parser.add_argument('--output', type=Path, help='HTML path; defaults beside the JSON report')
    args = parser.parse_args(argv)
    report = json.loads(args.report.read_text(encoding='utf-8'))
    output = args.output or args.report.with_suffix('.html')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_html(report), encoding='utf-8')
    print(f'TD report: {output}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
