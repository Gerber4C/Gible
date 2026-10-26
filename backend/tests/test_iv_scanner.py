import json
import tempfile
import unittest
from pathlib import Path

from engine.iv_scanner import list_reports, project_report, read_report, scan_options


class IVScannerTests(unittest.TestCase):
    def sample_report(self):
        base = {
            'hands': {'n': 'SAKQJH432D432C432', 's': 'S432HAKQJDAKQJC32'},
            'north_hcp': 10, 'south_hcp': 18,
            'north_kr': 10.5, 'south_kr': 18.2,
            'north_shape': [4, 3, 3, 3], 'south_shape': [3, 4, 4, 2],
            'auction': '1NP3NPPP', 'calls': ['1N', 'P', '3N', 'P', 'P', 'P'],
        }
        return {
            'schema_version': 2, 'profile': {'id': 'daqiush_2over1'},
            'seed': 23, 'summary': {'pairs': 3, 'dds_boards': 20},
            'budget': {'ew_samples': 10}, 'filters': {'opening': '1N'},
            'cases': [
                dict(base, id=1, blocked={'seat': 's', 'diagnostics': ['No call']}),
            ],
            'complete_cases': [
                dict(base, id=2, contract='3NT', declarer='n',
                     dds_tables=[{'large': 'payload'}],
                     analysis={'flags': ['wrong_game', 'contract_failure'],
                               'rates': {'wrong_game': .4, 'contract_failure': .6},
                               'alternative_game_rates': {'4S': .4},
                               'class_pairs': 2, 'dds_boards': 20}),
                dict(base, id=3, contract='2S', declarer='s',
                     analysis={'flags': ['missed_game', 'missed_small_slam'],
                               'rates': {'missed_game': .5, 'missed_small_slam': .4}}),
            ],
        }

    def test_report_projects_four_categories_without_dds_tables(self):
        projected = project_report(self.sample_report(), 'sample.json')
        self.assertEqual(projected['counts'],
                         {'block': 1, 'missed': 1, 'down': 1, 'wrong': 1})
        self.assertEqual([case['id'] for case in projected['cases']], [1, 2, 3])
        self.assertEqual(projected['cases'][1]['categories'], ['down', 'wrong'])
        self.assertEqual(projected['cases'][1]['alternative_game_rates']['4S'], .4)
        self.assertNotIn('dds_tables', json.dumps(projected))

    def test_scan_options_are_bounded_and_north_one_notrump(self):
        settings = scan_options({})
        self.assertEqual(settings['planned_pairs'], 23 * 23 * 2)
        self.assertEqual(settings['ew_samples'], 10)
        self.assertEqual(len(settings['shapes']), 23)
        self.assertIn((8, 3, 2, 0), settings['shapes'])
        self.assertNotIn((7, 5, 1, 0), settings['shapes'])
        for invalid in ({'hcp_min': 10, 'hcp_max': 9}, {'ew_samples': 21},
                        {'pairs_per_cell': 0}, {'pairs_per_cell': 21},
                        {'seed': True}, {'scope': 'full'},
                        {'profile': '../private'}, {'unexpected': 1}):
            with self.assertRaises(ValueError):
                scan_options(invalid)

    def test_reports_are_read_only_from_bounded_report_ids(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / 'iv-scan-demo.json'
            path.write_text(json.dumps(self.sample_report()), encoding='utf-8')
            self.assertEqual(list_reports(root)[0]['counts']['wrong'], 1)
            self.assertEqual(read_report(path.name, root)['id'], path.name)
            with self.assertRaises(ValueError):
                read_report('../other.json', root)


if __name__ == '__main__':
    unittest.main()
