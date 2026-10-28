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

    @staticmethod
    def pair(case_id, slot, *, hcp=10, shape=(6, 3, 2, 2), cell=0):
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

    @staticmethod
    def in_cell(case, *, hcp, shape, cell):
        case['coverage_cell'].update(
            target_hcp=hcp, base_shape_index=cell, base_shape=list(shape))
        case['south_hcp'] = hcp
        case['south_shape'] = list(shape)
        return case

    def sample_report(self):
        calls_a = ('1N', 'P', '3N', 'P', 'P', 'P')
        calls_b = ('1N', 'P', '2H', 'P', '2S', 'P', '4S', 'P', 'P', 'P')
        calls_c = ('1N', 'P', '2D', 'P', '2H', 'P')
        calls_d = ('1N', 'P', '2D', 'P', '2H', 'P', '4H', 'P', 'P', 'P')
        calls_e = ('1N', 'P', '2H', 'P', '2S', 'P', '3D')

        clean_a1 = dict(self.pair(1, 0), calls=list(calls_a), auction='1NP3NPPP',
                        contract='3NT', declarer='n',
                        dds_tables=[self.table() for _ in range(3)])
        clean_a2 = dict(self.pair(2, 1), calls=list(calls_a), auction='1NP3NPPP',
                        contract='3NT', declarer='n',
                        dds_tables=[self.table() for _ in range(3)])
        warned = dict(self.pair(3, 2), calls=list(calls_b),
                      auction='1NP2HP2SP4SPPP', contract='4S', declarer='n',
                      dds_tables=([self.table(spades=9, nt=6)] * 9
                                  + [self.table(spades=9, nt=6, hearts=12)]))
        limit = dict(self.pair(4, 3), calls=list(calls_c),
                     auction='1NP2DP2HPPP', status='limit')
        clean_b = [
            self.in_cell(dict(self.pair(case_id, slot), calls=list(calls_d),
                              auction='1NP2DP2HP4HPPP', contract='4H',
                              declarer='s', dds_tables=[self.table(hearts=10)]),
                         hcp=11, shape=(5, 4, 3, 1), cell=1)
            for case_id, slot in ((5, 0), (6, 1), (7, 2))
        ]
        blocked = self.in_cell(
            dict(self.pair(8, 3), calls=list(calls_e),
                 auction='1NP2HP2SP3DP',
                 blocked={'seat': 's', 'diagnostics': ['No call']}),
            hcp=11, shape=(5, 4, 3, 1), cell=1)
        return {
            'schema_version': 2, 'profile': {'id': 'daqiush_2over1'},
            'seed': 23,
            'summary': {'pairs': 8, 'complete': 6, 'blocked': 1,
                        'limit': 1, 'dds_boards': 19, 'suspicious': 99},
            'budget': {'pairs_per_cell': 4, 'ew_samples': 3,
                       'min_class_boards': 2, 'min_class_pairs': 1},
            'filters': {'opening': '1N'},
            'wrong_game_rule': 'legacy_joint_failure_30pct',
            'cases': [blocked],
            'complete_cases': [clean_a1, clean_a2, warned, *clean_b],
            'limit_cases': [limit],
        }

    def test_report_splits_every_cell_by_auction_process_and_keeps_siblings(self):
        projected = project_report(self.sample_report(), 'sample.json')

        self.assertNotIn('cases', projected)
        self.assertEqual(len(projected['groups']), 5)
        group = projected['groups'][0]
        self.assertEqual(set(group), {
            'id', 'parent_id', 'south_hcp', 'south_shape', 'auction',
            'warning_counts', 'actual_pair_count', 'parent_pair_count',
            'expected_pair_count', 'incomplete', 'pairs',
        })
        self.assertEqual(group['id'], '10:0|1NP3NPPP')
        self.assertEqual(group['parent_id'], '10:0')
        self.assertEqual(group['south_hcp'], 10)
        self.assertEqual(group['south_shape'], [6, 3, 2, 2])
        self.assertEqual(group['auction'], '1NP3NPPP')
        self.assertEqual(group['warning_counts'],
                         {'block': 0, 'missed': 0, 'down': 0, 'wrong': 0})
        self.assertEqual(group['actual_pair_count'], 2)
        self.assertEqual(group['parent_pair_count'], 4)
        self.assertEqual(group['expected_pair_count'], 4)
        self.assertFalse(group['incomplete'])
        self.assertEqual([pair['id'] for pair in group['pairs']], [1, 2])
        self.assertEqual([pair['pair_slot'] for pair in group['pairs']], [0, 1])

        down = projected['groups'][1]
        self.assertEqual(down['id'], '10:0|1NP2HP2SP4SPPP')
        self.assertEqual([pair['id'] for pair in down['pairs']], [3])
        self.assertEqual(down['pairs'][0]['flags'], ['contract_failure'])
        self.assertEqual(down['pairs'][0]['class_pairs'], 1)
        self.assertEqual(down['pairs'][0]['dds_boards'], 10)
        self.assertEqual(down['warning_counts']['down'], 1)
        self.assertEqual(projected['counts'],
                         {'block': 1, 'missed': 0, 'down': 1, 'wrong': 0})
        self.assertEqual(projected['summary']['suspicious'], 2)
        self.assertEqual(projected['wrong_game_rule'], RULE_ID)
        self.assertNotIn('dds_tables', json.dumps(projected))

    def test_blocked_and_limit_processes_stay_their_own_cells(self):
        projected = project_report(self.sample_report(), 'sample.json')

        limit_group = projected['groups'][2]
        self.assertEqual(limit_group['id'], '10:0|1NP2DP2HPPP')
        self.assertEqual(limit_group['pairs'][0]['status'], 'limit')
        self.assertNotIn('contract', limit_group['pairs'][0])
        self.assertNotIn('ew_results', limit_group['pairs'][0])

        blocked_group = projected['groups'][4]
        self.assertEqual(blocked_group['pairs'][0]['status'], 'blocked')
        self.assertEqual(blocked_group['warning_counts']['block'], 1)
        self.assertEqual(projected['counts']['block'], 1)

    def test_ew_results_keep_make_set_and_independent_missed_target(self):
        projected = project_report(self.sample_report(), 'sample.json')
        results = projected['groups'][1]['pairs'][0]['ew_results']

        self.assertEqual(len(results), 10)
        self.assertEqual(results[0],
                         {'outcome': 'SET', 'lose': False, 'missed_target': None})
        self.assertEqual(results[-1],
                         {'outcome': 'SET', 'lose': True,
                          'missed_target': 'small slam'})

    def test_legacy_cases_split_by_stored_cell_and_call_sequence(self):
        report = self.sample_report()
        legacy = [self.pair(3, 0), self.pair(8, 1)]
        for case, calls in zip(legacy, (('1N', 'P', '3N', 'P', 'P', 'P'),
                                        ('1N', 'P', '2N', 'P', 'P', 'P'))):
            case.pop('coverage_cell')
            case.update(calls=list(calls), auction=' '.join(calls),
                        contract='4S', declarer='n',
                        analysis={'flags': ['contract_failure', 'wrong_game',
                                            'missed_small_slam'],
                                  'rates': {'contract_failure': .6,
                                            'wrong_game': float('inf'),
                                            'missed_small_slam': .4},
                                  'alternative_game_rates': {'3NT': .5}})
        report.update(cases=[], complete_cases=legacy, limit_cases=[])

        projected = project_report(report, 'legacy.json')

        self.assertEqual(len(projected['groups']), 2)
        first, second = projected['groups']
        self.assertEqual(first['id'], 'legacy:10:6-3-2-2|1N P 3N P P P')
        self.assertEqual(second['id'], 'legacy:10:6-3-2-2|1N P 2N P P P')
        self.assertEqual([pair['id'] for pair in first['pairs']], [3])
        self.assertEqual([pair['id'] for pair in second['pairs']], [8])
        self.assertEqual([pair['pair_slot'] for pair in first['pairs']], [0])
        self.assertEqual([pair['pair_slot'] for pair in second['pairs']], [1])
        self.assertEqual(first['actual_pair_count'], 1)
        self.assertEqual(first['parent_pair_count'], 2)
        self.assertEqual(first['expected_pair_count'], 4)
        self.assertTrue(first['incomplete'])
        self.assertEqual(first['pairs'][0]['flags'], ['missed_small_slam'])
        self.assertEqual(projected['counts']['missed'], 2)
        self.assertEqual(projected['counts']['down'], 0)
        self.assertEqual(projected['counts']['wrong'], 0)
        json.dumps(projected, allow_nan=False)

    def test_invalid_legacy_identity_is_retained_as_incomplete_fallback(self):
        report = self.sample_report()
        broken = self.pair(77, 0)
        broken.pop('coverage_cell')
        broken.pop('south_hcp')
        broken['south_shape'] = [6, 3, 2]
        broken.update(contract='4S', declarer='n',
                      calls=['1N', 'P', '4S', 'P', 'P', 'P'],
                      auction='1NP4SPPP',
                      analysis={'flags': ['contract_failure'],
                                'rates': {'contract_failure': 1.0},
                                'alternative_game_rates': {}})
        report.update(cases=[], complete_cases=[broken], limit_cases=[])

        projected = project_report(report, 'legacy.json')

        group = projected['groups'][0]
        self.assertEqual(group['id'], 'legacy-fallback:77|1NP4SPPP')
        self.assertEqual(group['actual_pair_count'], 1)
        self.assertEqual(group['parent_pair_count'], 1)
        self.assertEqual(group['expected_pair_count'], 4)
        self.assertTrue(group['incomplete'])
        self.assertEqual(group['warning_counts']['down'], 1)

    def test_process_pair_target_marks_process_groups_incomplete(self):
        report = self.sample_report()
        report['budget']['pairs_per_process_cell'] = 2

        projected = project_report(report, 'sample.json')

        clean = projected['groups'][0]
        self.assertEqual(clean['actual_pair_count'], 2)
        self.assertEqual(clean['expected_pair_count'], 2)
        self.assertFalse(clean['incomplete'])
        down = projected['groups'][1]
        self.assertEqual(down['actual_pair_count'], 1)
        self.assertEqual(down['expected_pair_count'], 2)
        self.assertTrue(down['incomplete'])

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


    def test_explicit_opener_metadata_flows_through_projection(self):
        report = self.sample_report()
        for case in report['complete_cases'] + report['cases'] + report['limit_cases']:
            cell = dict(case['coverage_cell'])
            cell['opener_shape'] = [4, 3, 3, 3]
            cell['opener_mode'] = 'normal'
            case['coverage_cell'] = cell
        report['coverage'] = {'north': {
            'schema_status': 'explicit', 'required_cells': 92,
            'available_cells': 4, 'complete': False,
        }}

        projected = project_report(report, 'sample.json')

        self.assertEqual(projected['coverage']['north']['schema_status'], 'explicit')
        self.assertEqual(projected['groups'][0]['opener_shape'], [4, 3, 3, 3])
        self.assertEqual(projected['groups'][0]['opener_mode'], 'normal')
        self.assertEqual(
            projected['groups'][0]['pairs'][0]['coverage_cell']['opener_mode'],
            'normal')

    def test_legacy_report_has_a_strict_legacy_north_marker(self):
        projected = project_report(self.sample_report(), 'sample.json')
        self.assertEqual(projected['coverage'],
                         {'north': {'schema_status': 'legacy'}})


if __name__ == '__main__':
    unittest.main()
