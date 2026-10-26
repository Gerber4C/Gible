"""Portable evidence and editable decisions for suspicious resampling reports.

The scanner produces observations. A model or a human writes proposed changes
in a separate file; neither step mutates a bidding profile.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Mapping


DECISIONS = frozenset({'pending', 'approved', 'needs_changes', 'rejected'})
IMPLEMENTATIONS = frozenset({'not_started', 'partial', 'complete', 'accepted_no_change'})
KINDS = frozenset({'change', 'keep', 'investigate'})
REVIEW_FIELDS = frozenset({'title', 'diagnosis', 'kind', 'target_auction',
                           'proposed_call', 'proposal', 'basis', 'decision',
                           'implementation', 'reviewer_note'})


def review_signature(report: Mapping) -> str:
    """Bind a review file to the sampled classes, not to transient DDS tables."""
    identity = {
        'profile': report.get('profile', {}).get('id'),
        'source_seed': report.get('source_seed'), 'seed': report.get('seed'),
        'groups': [
            {'id': group['id'], 'source_ids': group['source_ids'],
             'constraints': group['constraints']}
            for group in report['groups']
        ],
    }
    encoded = json.dumps(identity, ensure_ascii=False, sort_keys=True,
                         separators=(',', ':')).encode('utf-8')
    return hashlib.sha256(encoded).hexdigest()[:20]


def validate_reviews(report: Mapping, reviews: Mapping) -> dict:
    """Validate an imported review before it can be shown or re-exported."""
    if not isinstance(reviews, Mapping) or reviews.get('schema_version') != 1:
        raise ValueError('reviews require schema_version 1')
    if reviews.get('report_signature') != review_signature(report):
        raise ValueError('review report signature does not match this report')
    entries = reviews.get('groups')
    if not isinstance(entries, Mapping):
        raise ValueError('reviews require a groups object')
    known = {group['id'] for group in report['groups']}
    result = {}
    for group_id, item in entries.items():
        if group_id not in known:
            raise ValueError(f'unknown group in reviews: {group_id}')
        if not isinstance(item, Mapping):
            raise ValueError(f'{group_id}: review must be an object')
        if set(item) - REVIEW_FIELDS:
            raise ValueError(f'{group_id}: unrecognized review field')
        for field in ('title', 'diagnosis', 'target_auction', 'proposed_call',
                      'proposal', 'reviewer_note'):
            if not isinstance(item.get(field, ''), str):
                raise ValueError(f'{group_id}: {field} must be text')
        basis = item.get('basis', [])
        if not isinstance(basis, list) or any(not isinstance(source, str) for source in basis):
            raise ValueError(f'{group_id}: basis must be a list of text')
        decision = item.get('decision', 'pending')
        implementation = item.get('implementation', 'not_started')
        kind = item.get('kind', 'investigate')
        if decision not in DECISIONS or implementation not in IMPLEMENTATIONS or kind not in KINDS:
            raise ValueError(f'{group_id}: invalid decision or implementation')
        if kind == 'change' and not item.get('proposed_call'):
            raise ValueError(f'{group_id}: a concrete change needs proposed_call')
        result[group_id] = {
            'title': item.get('title', ''),
            'diagnosis': item.get('diagnosis', ''),
            'kind': kind,
            'target_auction': item.get('target_auction', ''),
            'proposed_call': item.get('proposed_call', ''),
            'proposal': item.get('proposal', ''),
            'basis': basis,
            'decision': decision,
            'implementation': implementation,
            'reviewer_note': item.get('reviewer_note', ''),
        }
    return {'schema_version': 1, 'report_signature': review_signature(report),
            'groups': result}


def review_brief(report: Mapping) -> dict:
    """Small, repeatable input for a local or chat-based suggestion writer."""
    groups = []
    for group in report['groups']:
        examples = group['deals']
        blocked = [deal for deal in examples if deal['status'] == 'blocked']
        sample = (blocked[:2] + [deal for deal in examples if deal not in blocked][:2])[:4]
        groups.append({
            'id': group['id'], 'source_ids': group['source_ids'],
            'constraints': group['constraints'], 'summary': group['summary'],
            'source_checks': [{key: check[key] for key in (
                'auction', 'original_flags', 'retained_flags', 'original_rates',
                'new_rates') if key in check} for check in group['source_checks']],
            'sample_hands': sample[0]['hands'] if sample else {},
            'examples': [{key: deal[key] for key in ('id', 'hands', 'calls', 'status',
                                                     'blocked', 'contract') if key in deal}
                         for deal in sample],
        })
    return {
        'schema_version': 1, 'report_signature': review_signature(report),
        'authority': 'Daqiush 2/1 overrides conflicting CBB/Newrui agreements.',
        'references': ['docs/13_daqiush_2over1.md', 'docs/15_daqiush_slam.md',
                       r'D:\A0_bridge\bid\bid\bidproductCN-cbb-260721.txt'],
        'instruction': ('For every group, first compare the current auction with the Daqiush '
                        'and CBB/Newrui agreements. If an agreement supports a change, name '
                        'the exact auction, next call, hand conditions, and follow-up calls; '
                        'do not offer only a general direction. If no agreement supports a '
                        'specific call, mark investigate and identify the missing definition. '
                        'Otherwise explain why the current rule should stay. Cite the actual '
                        'agreement key, not a generic system name. Daqiush overrides conflicts. '
                        'Do not infer single-dummy success directly from DDS or modify code.'),
        'review_schema': {'schema_version': 1, 'report_signature': review_signature(report),
                          'groups': {'G001': {'title': '...', 'diagnosis': '...',
                                              'kind': 'change', 'target_auction': '1N P ...',
                                              'proposed_call': '3H',
                                              'proposal': '...', 'basis': ['...'],
                                              'decision': 'pending',
                                              'implementation': 'not_started',
                                              'reviewer_note': ''}}},
        'groups': groups,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Prepare evidence for review suggestions')
    parser.add_argument('report', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    report = json.loads(args.report.read_text(encoding='utf-8'))
    brief = review_brief(report)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(brief, ensure_ascii=False, indent=2) + '\n',
                           encoding='utf-8')
    print(f"Prepared {len(brief['groups'])} groups: {args.output}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
