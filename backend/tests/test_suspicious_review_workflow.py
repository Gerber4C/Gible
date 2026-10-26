import json
import unittest
from pathlib import Path

from engine.suspicious_review_workflow import (
    review_brief,
    review_signature,
    validate_reviews,
)
from engine.suspicious_resample_viewer import render_html


class SuspiciousReviewWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.report = {
            'kind': 'suspicious_resample', 'seed': 41, 'source_seed': 23,
            'profile': {'id': 'daqiush_2over1'},
            'budget': {'pairs_per_group': 1},
            'summary': {'resampled_groups': 1, 'pairs': 1, 'blocked': 1,
                        'dds_boards': 2},
            'groups': [{
                'id': 'G012', 'source_ids': [27],
                'constraints': {
                    'north': {'shape': [4, 4, 3, 2], 'hcp': [15, 17], 'kr': [15, 17]},
                    'south': {'shape': [5, 3, 3, 2], 'hcp': [13, 15], 'kr': [12, 14]},
                },
                'summary': {'pairs': 1, 'complete': 0, 'blocked': 1,
                            'dds_boards': 2},
                'contracts': {},
                'source_checks': [{'source_id': 27, 'auction': '1NP2HP3CP4SPPP',
                                   'contract': '4S', 'declarer': 's',
                                   'original_flags': ['missed_small_slam'],
                                   'retained_flags': [], 'original_rates': {},
                                   'new_rates': {}}],
                'deals': [{'id': 'G012-001', 'hands': {'n': 'SAKJ4HAJ87DKT6C85',
                                                    's': 'SQT873HKQTDAJ5CQJ'},
                           'status': 'blocked', 'calls': ['1N', 'P', '2H', 'P', '3C'],
                           'north_hcp': 16, 'south_hcp': 13,
                           'north_kr': 16.2, 'south_kr': 12.3}],
            }],
        }

    def test_signature_binds_review_to_group_constraints(self):
        old = review_signature(self.report)
        altered = json.loads(json.dumps(self.report))
        altered['groups'][0]['constraints']['south']['shape'] = [6, 2, 3, 2]
        self.assertNotEqual(old, review_signature(altered))

    def test_validated_review_is_included_in_offline_viewer(self):
        reviews = {
            'schema_version': 1, 'report_signature': review_signature(self.report),
            'groups': {'G012': {
                'title': '超转后的续叫缺失', 'diagnosis': '2♥–3♣ 后停住',
                'kind': 'investigate', 'target_auction': '1N P 2H P 3C P',
                'proposed_call': '',
                'proposal': '先核对 Daqiush 超转约定，再补续叫。',
                'basis': ['Daqiush: 雅可比超转'], 'decision': 'pending',
                'implementation': 'not_started', 'reviewer_note': '',
            }},
        }
        validated = validate_reviews(self.report, reviews)
        html = render_html(self.report, reviews=validated)
        self.assertIn('id="review-proposal"', html)
        self.assertIn('id="review-export"', html)
        self.assertIn('id="review-import"', html)
        self.assertIn('超转后的续叫缺失', html)
        self.assertNotIn('dds_tables', html)

    def test_rejects_review_for_another_report_or_unknown_group(self):
        reviews = {'schema_version': 1, 'report_signature': 'wrong',
                   'groups': {'G012': {'title': 'x', 'proposal': 'y'}}}
        with self.assertRaisesRegex(ValueError, 'signature'):
            validate_reviews(self.report, reviews)
        reviews['report_signature'] = review_signature(self.report)
        reviews['groups'] = {'G999': {'title': 'x', 'proposal': 'y'}}
        with self.assertRaisesRegex(ValueError, 'unknown group'):
            validate_reviews(self.report, reviews)

    def test_brief_contains_evidence_and_review_schema_but_not_dds_tables(self):
        self.report['groups'][0]['deals'][0]['dds_tables'] = [{'S': {'n': 12}}]
        brief = review_brief(self.report)
        self.assertEqual(brief['report_signature'], review_signature(self.report))
        self.assertEqual(brief['groups'][0]['id'], 'G012')
        self.assertEqual(brief['groups'][0]['sample_hands']['s'], 'SQT873HKQTDAJ5CQJ')
        self.assertNotIn('dds_tables', json.dumps(brief))

    def test_seed41_review_records_owner_decisions_and_concrete_fit_calls(self):
        path = Path(__file__).resolve().parents[2] / 'docs' / 'reviews' / 'daqiush-1nt-seed41.json'
        proposals = json.loads(path.read_text(encoding='utf-8'))['groups']
        self.assertEqual(len(proposals), 88)
        self.assertEqual(proposals['G009']['proposed_call'], '4♦')
        self.assertTrue(proposals['G022']['proposed_call'].startswith('4NT'))
        self.assertTrue(proposals['G032']['proposed_call'].startswith('4NT'))
        self.assertTrue(proposals['G013']['proposed_call'].startswith('4NT'))
        self.assertEqual(proposals['G073']['kind'], 'investigate')
        self.assertEqual(proposals['G081']['proposed_call'], '4♥')
        self.assertEqual(proposals['G010']['implementation'], 'accepted_no_change')
        self.assertEqual(proposals['G011']['decision'], 'approved')
        self.assertTrue(all(item['proposed_call'] for item in proposals.values()
                            if item['kind'] == 'change'))


if __name__ == '__main__':
    unittest.main()
