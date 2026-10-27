import json
import tempfile
import unittest
from pathlib import Path

from engine.iv_scanner import list_reports, project_report, read_report, scan_options
from engine.outcome_metrics import RULE_ID


class IVScannerTests(unittest.TestCase):
    @staticmethod
    def table(*, spades=10, hearts=6, diamonds=6, clubs=6, nt=9):
        return {
            'S': {'n': spades, 's': spades},
            'H': {'n': hearts, 's': hearts},
            'D': {'n': diamonds, 's': diamonds},
            'C': {'n': clubs, 's': clubs},
            'NT': {'n': nt, 's': nt},
        }

    def pair(self, case_id, slot, *, hcp=10, shape=(6, 3, 2, 2), cell=0):
        return {
            'id': case_id,
            'hands': {'n': f'SAKQJH432D432C{case_id}',
                      's': f'S432HAKQJDAKQJC{case_id}',
                      'e': 'S2H2D2C2', 'w': 'S3H3D3C3'},
            'north_hcp': 16, 'south_hcp': hcp,
            'north_kr': 16.0, 'south_kr': 10.0,
            'north_shape': [4, 3, 3, 3], 'south_shape': list(shape),
            'auction': f'1NP{case_id}', 'calls': ['1N', 'P'],
            'coverage_cell': {
                'target_hcp': hcp, 'base_shape_index': cell,
                'base_shape': list(shape), 'pair_slot': slot,
            },
        }

    def sample_report(self):
        warned = self.pair(2, 1)
        warned.update(
            contract='4S', declarer='n',
            dds_tables=[self.table(spades=10), self.table(spades=9),
                        self.table(spades=9, hearts=12)],
            analysis={'flags': ['contract_failure'],
                      'rates': {'contract_failure': 2 / 3, 'wrong_game': None},
                      'alternative_game_rates': {'3NT': 0.0, '4H': 1 / 3},
                      'class_pairs': 3, 'dds_boards': 3},
        )
        clean = self.pair(1, 0)
        clean.update(contract='4S', declarer='n', dds_tables=[self.table()],
                     analysis={'flags': [],
                               'rates': {'contract_failure': 0.0},
                               'alternative_game_rates': {'3NT': 0.0}})
        limit = self.pair(3, 2)
        limit['status'] = 'limit'
        clean_cell = []
        for case_id, slot in ((4, 0), (5, 1), (6, 2)):
            case = self.pair(case_id, slot, hcp=11, shape=(5, 4, 3, 1), cell=1)
            case.update(contract='3NT', declarer='n', dds_tables=[self.table()],
                        analysis={'flags': [],
                                  'rates': {'contract_failure': 0.0},
                                  'alternative_game_rates': {'4S': 0.0}})
            clean_cell.append(case)
        return {
            'schema_version': 2, 'profile': {'id': 'daqiush_2over1'},
            'seed': 23,
            'summary': {'pairs': 6, 'complete': 5, 'blocked': 0,
                        'limit': 1, 'dds_boards': 7, 'suspicious': 99},
            'budget': {'pairs_per_cell': 3, 'ew_samples': 3},
            'filters': {'opening': '1N'},
            'wrong_game_rule': 'legacy_joint_failure_30pct',
            'cases': [],
            'complete_cases': [clean, warned, *clean_cell],
            'limit_cases': [limit],
        }

    def test_report_projects_warned_cell_with_all_siblings_and_explicit_schema(self):
        projected = project_report(self.sample_report(), 'sample.json')

        self.assertNotIn('cases', projected)
        self.assertEqual(len(projected['groups']), 1)
        group = projected['groups'][0]
        self.assertEqual(set(group), {
            'id', 'south_hcp', 'south_shape', 'warning_counts',
            'actual_pair_count', 'expected_pair_count', 'incomplete', 'pairs',
        })
        self.assertEqual(group['id'], '10:0')
        self.assertEqual(group['south_hcp'], 10)
        self.assertEqual(group['south_shape'], [6, 3, 2, 2])
        self.assertEqual(group['warning_counts'],
                         {'block': 0, 'missed': 0, 'down': 1, 'wrong': 0})
        self.assertEqual(group['actual_pair_count'], 3)
        self.assertEqual(group['expected_pair_count'], 3)
        self.assertFalse(group['incomplete'])
        self.assertEqual([pair['id'] for pair in group['pairs']], [1, 2, 3])
        self.assertEqual(group['pairs'][0]['categories'], [])
        self.assertEqual(group['pairs'][0]['pair_slot'], 0)
        self.assertEqual(group['pairs'][0]['status'], 'complete')
        self.assertEqual(group['pairs'][2]['status'], 'limit')
        self.assertNotIn('contract', group['pairs'][2])
        self.assertNotIn('ew_results', group['pairs'][2])
        self.assertEqual(projected['counts'],
                         {'block': 0, 'missed': 0, 'down': 1, 'wrong': 0})
        self.assertEqual(projected['summary']['suspicious'], 1)
        self.assertEqual(projected['wrong_game_rule'], RULE_ID)
        self.assertNotIn('dds_tables', json.dumps(projected))

    def test_blocked_sibling_is_retained_and_counted(self):
        report = self.sample_report()
        blocked = report['complete_cases'].pop(0)
        for field in ('contract', 'declarer', 'dds_tables', 'analysis'):
            blocked.pop(field)
        blocked['blocked'] = {'seat': 's', 'diagnostics': ['No call']}
        report['cases'].append(blocked)

        projected = project_report(report, 'sample.json')

        self.assertEqual(projected['groups'][0]['pairs'][0]['status'], 'blocked')
        self.assertEqual(projected['groups'][0]['warning_counts']['block'], 1)
        self.assertEqual(projected['counts']['block'], 1)

    def test_ew_results_keep_make_set_and_independent_missed_target(self):
        projected = project_report(self.sample_report(), 'sample.json')
        results = projected['groups'][0]['pairs'][1]['ew_results']

        self.assertEqual([result['outcome'] for result in results],
                         ['MAKE', 'SET', 'SET'])
        self.assertEqual(results[0],
                         {'outcome': 'MAKE', 'lose': False, 'missed_target': None})
        self.assertEqual(results[2],
                         {'outcome': 'SET', 'lose': True,
                          'missed_target': 'small slam'})

    def test_legacy_cases_group_by_stored_south_identity_and_reclassify_stale_flags(self):
        report = self.sample_report()
        legacy = [self.pair(8, 0), self.pair(3, 1)]
        for case in legacy:
            case.pop('coverage_cell')
            case.update(contract='4S', declarer='n', dds_tables=[self.table()],
                        analysis={'flags': ['contract_failure', 'wrong_game',
                                            'missed_small_slam'],
                                  'rates': {'contract_failure': .6,
                                            'wrong_game': float('inf'),
                                            'missed_small_slam': .4},
                                  'alternative_game_rates': {'3NT': .5}})
        report.update(cases=[], complete_cases=legacy, limit_cases=[])

        projected = project_report(report, 'legacy.json')

        group = projected['groups'][0]
        self.assertEqual(group['id'], 'legacy:10:6-3-2-2')
        self.assertEqual([pair['id'] for pair in group['pairs']], [3, 8])
        self.assertEqual([pair['pair_slot'] for pair in group['pairs']], [0, 1])
        self.assertEqual(group['actual_pair_count'], 2)
        self.assertEqual(group['expected_pair_count'], 3)
        self.assertTrue(group['incomplete'])
        self.assertEqual(group['pairs'][0]['flags'], ['missed_small_slam'])
        self.assertEqual(group['warning_counts']['missed'], 2)
        self.assertEqual(group['warning_counts']['down'], 0)
        self.assertEqual(group['warning_counts']['wrong'], 0)
        json.dumps(projected, allow_nan=False)

    def test_invalid_legacy_identity_is_retained_as_incomplete_fallback(self):
        report = self.sample_report()
        broken = self.pair(77, 0)
        broken.pop('coverage_cell')
        broken.pop('south_hcp')
        broken['south_shape'] = [6, 3, 2]
        broken.update(contract='4S', declarer='n', dds_tables=[self.table(spades=9)],
                      analysis={'flags': ['contract_failure'],
                                'rates': {'contract_failure': 1.0},
                                'alternative_game_rates': {}})
        report.update(cases=[], complete_cases=[broken], limit_cases=[])

        projected = project_report(report, 'legacy.json')

        group = projected['groups'][0]
        self.assertEqual(group['id'], 'legacy-fallback:77')
        self.assertEqual(group['actual_pair_count'], 1)
        self.assertEqual(group['expected_pair_count'], 3)
        self.assertTrue(group['incomplete'])

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
            self.assertEqual(list_reports(root)[0]['counts']['down'], 1)
            self.assertEqual(read_report(path.name, root)['id'], path.name)
            with self.assertRaises(ValueError):
                read_report('../other.json', root)

    def test_malformed_reports_are_skipped_without_hiding_valid_reports(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            good = root / 'iv-scan-good.json'
            good.write_text(json.dumps(self.sample_report()), encoding='utf-8')
            malformed = [
                {**self.sample_report(), 'budget': []},
                {**self.sample_report(), 'cases': [7]},
                {**self.sample_report(), 'complete_cases': [None]},
                {**self.sample_report(), 'limit_cases': ['bad']},
            ]
            for index, report in enumerate(malformed):
                (root / f'iv-scan-bad-{index}.json').write_text(
                    json.dumps(report), encoding='utf-8')
                with self.assertRaises(ValueError):
                    project_report(report, f'bad-{index}.json')
            (root / 'iv-scan-bad-root.json').write_text('[]', encoding='utf-8')
            with self.assertRaises(ValueError):
                project_report([], 'bad-root.json')

            self.assertEqual([item['id'] for item in list_reports(root)],
                             ['iv-scan-good.json'])


if __name__ == '__main__':
    unittest.main()
