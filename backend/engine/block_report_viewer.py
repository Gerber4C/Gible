"""Render a block-scout JSON report as a self-contained offline HTML page."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Mapping

from .outcome_metrics import RULE_ID, reclassify_analysis


TEMPLATE = Path(__file__).resolve().parent / 'templates' / 'block_report.html'
PLACEHOLDER = '__BLOCK_REPORT_JSON__'


def group_suspicious_cases(cases: list[Mapping]) -> list[list[int]]:
    """Partition nearby cases without allowing a group to drift past ±2 points."""
    groups: list[list[Mapping]] = []
    for case in sorted(cases, key=lambda item: item['id']):
        for group in groups:
            if all(
                case['north_shape'] == member['north_shape']
                and case['south_shape'] == member['south_shape']
                and all(abs(case[field] - member[field]) <= 2 for field in (
                    'north_hcp', 'south_hcp', 'north_kr', 'south_kr'))
                for member in group
            ):
                group.append(case)
                break
        else:
            groups.append([case])
    return [[item['id'] for item in group] for group in groups]


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
        complete_cases = []
        for source in report['complete_cases']:
            case = dict(source)
            case['analysis'] = reclassify_analysis(
                case.get('contract'), case.get('analysis') or {})
            complete_cases.append(case)
        suspicious_cases = [case for case in complete_cases
                            if case['analysis'].get('flags')]
        summary = dict(report.get('summary') or {})
        summary['suspicious'] = len(suspicious_cases)
        report['complete_cases'] = complete_cases
        report['suspicious_cases'] = suspicious_cases
        report['summary'] = summary
        report['wrong_game_rule'] = RULE_ID
        report['suspicious_groups'] = group_suspicious_cases(report['suspicious_cases'])
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
