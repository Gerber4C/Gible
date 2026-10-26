"""Render a compact, offline reader for suspicious-class resampling."""

from __future__ import annotations

import json
import argparse
from pathlib import Path

from .suspicious_review_workflow import review_signature, validate_reviews


TEMPLATE = Path(__file__).resolve().parent / 'templates' / 'suspicious_resample.html'
PLACEHOLDER = '__SUSPICIOUS_RESAMPLE_JSON__'
DEAL_FIELDS = ('id', 'hands', 'calls', 'status', 'contract', 'blocked',
               'north_hcp', 'south_hcp', 'north_kr', 'south_kr',
               'chosen_contract_rates')


def render_html(report: dict, reviews: dict | None = None) -> str:
    """Keep the report self-contained without loading full DDS tables into the UI."""
    if report.get('kind') not in (None, 'suspicious_resample') or not isinstance(report.get('groups'), list):
        raise ValueError('expected a suspicious resampling report')
    display = {
        'seed': report.get('seed'), 'source_seed': report.get('source_seed'),
        'budget': report['budget'], 'summary': report['summary'],
        'reviews': (validate_reviews(report, reviews) if reviews is not None else
                    {'schema_version': 1, 'report_signature': review_signature(report),
                     'groups': {}}),
        'groups': [],
    }
    for group in report['groups']:
        display['groups'].append({
            'id': group['id'], 'source_ids': group['source_ids'],
            'constraints': group['constraints'], 'summary': group['summary'],
            'contracts': group['contracts'],
            'sampling_warning': group.get('sampling_warning'),
            'source_checks': group['source_checks'],
            'deals': [{key: deal[key] for key in DEAL_FIELDS if key in deal}
                      for deal in group['deals']],
        })
    payload = json.dumps(display, ensure_ascii=False, separators=(',', ':'))
    payload = (payload.replace('&', r'\u0026')
               .replace('<', r'\u003c').replace('>', r'\u003e')
               .replace('\u2028', r'\u2028').replace('\u2029', r'\u2029'))
    template = TEMPLATE.read_text(encoding='utf-8')
    if template.count(PLACEHOLDER) != 1:
        raise RuntimeError('resampling template needs one data placeholder')
    return template.replace(PLACEHOLDER, payload)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Render an editable resampling review')
    parser.add_argument('report', type=Path)
    parser.add_argument('--reviews', type=Path, help='Optional proposed reviews JSON')
    parser.add_argument('--output', type=Path, help='HTML path; defaults beside report')
    args = parser.parse_args(argv)
    report = json.loads(args.report.read_text(encoding='utf-8'))
    reviews = (json.loads(args.reviews.read_text(encoding='utf-8'))
               if args.reviews else None)
    output = args.output or args.report.with_suffix('.html')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_html(report, reviews=reviews), encoding='utf-8')
    print(f'Review report: {output}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
