import json
import re
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from engine.block_report_viewer import group_suspicious_cases, main, render_html


class BlockReportViewerTests(unittest.TestCase):
    def report(self):
        return {
            'schema_version': 1,
            'profile': {'id': 'daqiush_2over1', 'name': 'Daqiush 2Over1', 'version': '1'},
            'seed': 23,
            'filters': {'opening': '1N', 'rare_hcp': None},
            'summary': {'attempts': 10, 'auction_matches': 2, 'blocked': 1,
                        'strata': {'natural': {'attempts': 10, 'blocked': 1}}},
            'block_points': [{'auction': '1NP', 'seat': 's', 'count': 1,
                              'strata': {'natural': 1}}],
            'cases': [{
                'trial': 4, 'stratum': 'natural', 'dealer': 'n',
                'hands': {'n': 'SAKQHJT98DAKQJC2', 'e': 'SJT98HAKQDJT9CAKQ',
                          's': 'S7654H7654D765C3', 'w': 'S32H32D32CJT98765'},
                'calls': ['1N', 'P'], 'auction': '1NP',
                'history': [{'seat': 'n', 'call': '1N', 'source_id': 'open_1nt'},
                            {'seat': 'e', 'call': 'P', 'source_id': None}],
                'blocked': {'seat': 's', 'auction': '1NP',
                            'diagnostics': ['No call </script><script>alert(1)</script>'],
                            'axioms': {'errors': [{'code': 'NO_COMPLIANT_CALL',
                                                   'message': 'No candidate'}]}},
            }],
        }

    def test_self_contained_html_embeds_report_without_script_breakout(self):
        html = render_html(self.report())
        self.assertIn('<!doctype html>', html.lower())
        self.assertIn('data-testid="case-detail"', html)
        self.assertNotIn('</script><script>alert(1)</script>', html)
        payload = re.search(r'const REPORT = (.*?);\n', html).group(1)
        embedded = json.loads(payload)
        self.assertEqual(embedded['cases'][0]['hands']['n'], 'SAKQHJT98DAKQJC2')
        self.assertEqual(embedded['block_points'][0]['auction'], '1NP')

    def test_cli_writes_viewer_next_to_report(self):
        with TemporaryDirectory() as directory:
            source = Path(directory) / 'scan.json'
            source.write_text(json.dumps(self.report()), encoding='utf-8')
            self.assertEqual(main([str(source)]), 0)
            self.assertTrue(source.with_suffix('.html').exists())
            self.assertIn('Block report', source.with_suffix('.html').read_text(encoding='utf-8'))

    def test_empty_cases_are_valid(self):
        report = self.report()
        report['cases'] = []
        self.assertIn('const REPORT = ', render_html(report))

    def test_coverage_report_embeds_suspicious_cases_for_browsing(self):
        report = self.report()
        report['schema_version'] = 2
        report['summary'] = {'pairs': 2, 'complete': 1, 'blocked': 1,
                             'suspicious': 1, 'dds_boards': 10}
        report['coverage'] = {'responder_hcp': [0, 22], 'longest_suit': [4, 8],
                              'top_two_suits': [7, 11]}
        suspicious = {
            'id': 2, 'trial': 2, 'dealer': 'n', 'stratum': 'coverage',
            'hands': report['cases'][0]['hands'], 'calls': ['1N', 'P', 'P', 'P'],
            'history': report['cases'][0]['history'], 'auction': '1NPPP',
            'contract': '1NT', 'declarer': 'n', 'north_hcp': 16,
            'south_hcp': 0, 'north_kr': 16.0, 'south_kr': 2.5,
            'north_shape': [4, 3, 3, 3], 'south_shape': [8, 3, 1, 1],
            'analysis': {'status': 'assessed', 'class_pairs': 1, 'dds_boards': 10,
                         'flags': ['contract_failure'],
                         'rates': {'contract_failure': .8, 'missed_game': 0,
                                   'missed_small_slam': 0, 'missed_grand_slam': 0}},
        }
        report['complete_cases'] = [suspicious]
        report['suspicious_cases'] = [suspicious]
        html = render_html(report)
        payload = re.search(r'const REPORT = (.*?);\n', html).group(1)
        self.assertEqual(json.loads(payload)['suspicious_cases'][0]['contract'], '1NT')
        self.assertIn('data-mode="suspicious"', html)

    def test_suspicious_groups_require_pairwise_shape_hcp_and_kr_match(self):
        base = {'north_shape': [4, 3, 3, 3], 'south_shape': [6, 3, 2, 2],
                'north_hcp': 16, 'south_hcp': 11,
                'north_kr': 16.0, 'south_kr': 12.0}
        cases = [
            {'id': 1, **base},
            {'id': 2, **base, 'north_kr': 17.8},
            {'id': 3, **base, 'north_kr': 19.6},
            {'id': 4, **base, 'south_shape': [5, 4, 2, 2]},
            {'id': 5, **base, 'south_hcp': 14},
        ]
        self.assertEqual(group_suspicious_cases(cases), [[1, 2], [3], [4], [5]])

    def test_coverage_viewer_embeds_suspicious_group_members(self):
        report = self.report()
        report['schema_version'] = 2
        case = {'id': 1, 'north_shape': [4, 3, 3, 3],
                'south_shape': [6, 3, 2, 2], 'north_hcp': 16,
                'south_hcp': 11, 'north_kr': 16.0, 'south_kr': 12.0}
        report['complete_cases'] = []
        report['suspicious_cases'] = [case, {**case, 'id': 2, 'north_hcp': 17}]
        html = render_html(report)
        payload = re.search(r'const REPORT = (.*?);\n', html).group(1)
        self.assertEqual(json.loads(payload)['suspicious_groups'], [[1, 2]])

    def test_constrained_auction_report_keeps_completed_and_limited_cases(self):
        report = self.report()
        report.update(schema_version=2,
                      filters={'mode': 'constrained', 'dealer': 'n',
                               'vulnerability': 'none', 'opening': None},
                      constraints={'north': {'shape': [4, 3, 3, 3],
                                             'hcp': [15, 17], 'kr': [14.5, 19]},
                                   'south': {'shape': [6, 3, 2, 2],
                                             'hcp': [8, 11], 'kr': [8, 15]}},
                      complete_cases=[{'id': 2, 'status': 'complete', 'contract': '4H'}],
                      limit_cases=[{'id': 3, 'status': 'limit'}],
                      suspicious_cases=[])
        html = render_html(report)
        payload = re.search(r'const REPORT = (.*?);\n', html).group(1)
        embedded = json.loads(payload)
        self.assertEqual(embedded['filters']['mode'], 'constrained')
        self.assertEqual(embedded['complete_cases'][0]['contract'], '4H')
        self.assertEqual(embedded['limit_cases'][0]['status'], 'limit')


if __name__ == '__main__':
    unittest.main()
