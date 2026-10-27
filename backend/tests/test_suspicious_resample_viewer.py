import unittest
import json
import re

from engine.suspicious_resample_viewer import render_html
from engine.outcome_metrics import RULE_ID


class SuspiciousResampleViewerTests(unittest.TestCase):
    def test_explains_wrong_game_alert_and_alternative_games(self):
        report = {
            'seed': 41, 'source_seed': 23,
            'summary': {'source_groups': 1, 'resampled_groups': 1,
                        'pairs': 1, 'complete': 1, 'blocked': 0,
                        'dds_boards': 2, 'source_flags': 1, 'retained_flags': 1},
            'budget': {'pairs_per_group': 1, 'ew_samples': 2},
            'groups': [{
                'id': 'G001', 'source_ids': [12],
                'constraints': {'north': {'shape': [4, 3, 3, 3], 'hcp': [15, 17], 'kr': [14, 16]},
                                'south': {'shape': [6, 3, 2, 2], 'hcp': [9, 11], 'kr': [10, 12]}},
                'summary': {'requested_pairs': 1, 'pairs': 1, 'complete': 1,
                            'blocked': 0, 'dds_boards': 2},
                'contracts': {'4S': 1},
                'source_checks': [{'source_id': 12, 'auction': '1N P 4S P P P',
                                   'contract': '4S', 'declarer': 'n',
                                   'original_boards': 10, 'new_boards': 2,
                                   'original_flags': ['wrong_game'],
                                   'original_rates': {'wrong_game': .4},
                                   'new_rates': {'wrong_game': .5},
                                   'retained_flags': ['wrong_game']}],
                'deals': [{'id': 'G001-001', 'hands': {'n': 'AKQ.JT.32.65432',
                                                     's': 'T98.KQJ.32.A54'},
                           'calls': ['1N', 'P', '4S', 'P', 'P', 'P'],
                           'status': 'complete', 'contract': '4S',
                           'chosen_contract_rates': {
                               'contract_failure': .5, 'wrong_game': .5,
                               'alternative_game_rates': {'3NT': .5, '4H': 0,
                                                          '5D': 0, '5C': 0}}}],
            }],
        }
        html = render_html(report)
        self.assertIn('打错局', html)
        self.assertIn('alternative_game_rates', html)
        self.assertIn('const wrongGame=flag==="wrong_game";', html)
        self.assertIn('"RATIO "+Number(v).toFixed(2)', html)
        self.assertIn('const track=(v,kind)=>wrongGame?"":', html)
        self.assertIn('track(old,"")', html)
        self.assertIn('track(now,"fresh")', html)
        self.assertIn('success probability ratio', html)
        self.assertIn('SET > 60%', html)
        self.assertIn(RULE_ID, html)
        self.assertNotIn('odds ratio', html)
        self.assertNotIn('Down > 50%', html)

    def test_shows_source_comparison_and_numbered_fresh_deals_safely(self):
        report = {
            'seed': 41, 'source_seed': 23,
            'summary': {'source_groups': 1, 'resampled_groups': 1,
                        'pairs': 1, 'complete': 1, 'blocked': 0,
                        'dds_boards': 2, 'source_flags': 1, 'retained_flags': 0},
            'budget': {'pairs_per_group': 1, 'ew_samples': 2},
            'groups': [{
                'id': 'G001', 'source_ids': [12],
                'constraints': {'north': {'shape': [4, 3, 3, 3], 'hcp': [15, 17], 'kr': [14, 18]},
                                'south': {'shape': [6, 3, 2, 2], 'hcp': [9, 11], 'kr': [10, 14]}},
                'summary': {'requested_pairs': 1, 'pairs': 1, 'complete': 1, 'blocked': 0,
                            'dds_boards': 2},
                'contracts': {'4S': 1},
                'source_checks': [{'source_id': 12, 'auction': '1N P 2C',
                                   'contract': '4S', 'declarer': 'n',
                                   'original_boards': 20, 'new_boards': 2,
                                   'original_flags': ['missed_small_slam'],
                                   'original_rates': {'missed_small_slam': .4},
                                   'new_rates': {'missed_small_slam': .2},
                                   'retained_flags': []}],
                'deals': [{'id': 'G001-001', 'hands': {'n': 'AKQ.JT.32.65432',
                                                     's': '<unsafe>.KQJ.32.54'},
                           'calls': ['1N', 'P', '2C', 'P', '4S', 'P', 'P', 'P'],
                           'status': 'complete', 'contract': '4S',
                           'chosen_contract_rates': {'contract_failure': .5},
                           'dds_tables': [{'S': {'n': 10}}]}],
            }],
        }
        html = render_html(report)
        for expected in ('lang="zh-CN"', 'id="group-search"',
                         'id="status-filter"', 'id="group-list"',
                         'id="group-detail"', 'id="report-data"'):
            self.assertIn(expected, html)
        self.assertIn(r'\u003cunsafe\u003e', html)
        self.assertNotIn('<unsafe>', html)
        payload = re.search(r'<script id="report-data" type="application/json">(.*?)</script>',
                            html, flags=re.S)
        self.assertIsNotNone(payload)
        data = json.loads(payload.group(1))
        self.assertEqual(data['groups'][0]['deals'][0]['hands']['s'], '<unsafe>.KQJ.32.54')
        self.assertNotIn('dds_tables', data['groups'][0]['deals'][0])
        self.assertEqual(data['groups'][0]['source_checks'][0]['original_boards'], 20)


if __name__ == '__main__':
    unittest.main()
