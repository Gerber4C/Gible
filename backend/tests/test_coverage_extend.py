import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from engine.coverage_extend import extend_ns_pairs, extend_process_pairs, main
from engine.model import Author, Gadget, PartnershipProfile
from engine.outcome_metrics import case_cell_key


def table(*, spades=6, nt=6):
    values = {strain: {seat: 6 for seat in 'ns'}
              for strain in ('S', 'H', 'D', 'C', 'NT')}
    values['S'].update(n=spades, s=spades)
    values['NT'].update(n=nt, s=nt)
    return values


def blocking_profile():
    gadget = Gadget.from_parts(
        {'id': 'opening', 'author': {'name': 'Test'}},
        [{'id': 'opening', 'context': {'auction_pattern': ''},
          'call': '1N', 'meaning': {'action_type': 'opening'}}],
    )
    return PartnershipProfile('test', 'Test', '1', Author('Test'),
                              (gadget,), missing_call_behavior='block')


def base_case(case_id, *, south_hcp=10, south_shape=(6, 3, 2, 2),
              north_hcp=15, north_shape=(4, 3, 3, 3),
              north_kr=15.0, south_kr=10.0, coverage_cell=None,
              contract=None, declarer=None, dds_tables=None):
    case = {
        'id': case_id, 'trial': case_id, 'dealer': 'n',
        'hands': {'n': 'SAKQJH432D432C432', 's': 'S432HAKQJDAKQJC32',
                  'e': 'S2H2D2C2', 'w': 'S3H3D3C3'},
        'north_hcp': north_hcp, 'south_hcp': south_hcp,
        'north_kr': north_kr, 'south_kr': south_kr,
        'north_shape': list(north_shape),
        'south_shape': list(south_shape),
        'calls': ['1N', 'P'], 'auction': '1NP',
    }
    if contract is not None:
        case.update(contract=contract, declarer=declarer,
                    dds_tables=list(dds_tables or []))
    if coverage_cell is not None:
        case['coverage_cell'] = coverage_cell
    return case


def report_with(*, complete=(), blocked=(), limit=(), budget=None):
    return {
        'schema_version': 2,
        'profile': {'id': 'test', 'name': 'Test', 'version': '1'},
        'seed': 23,
        'summary': {'pairs': len(complete) + len(blocked) + len(limit)},
        'budget': budget or {'pairs_per_cell': 1, 'ew_samples': 1,
                             'min_class_boards': 1, 'min_class_pairs': 1},
        'filters': {'opening': '1N'},
        'wrong_game_rule': 'legacy',
        'coverage': {},
        'cases': list(blocked),
        'complete_cases': list(complete),
        'limit_cases': list(limit),
        'suspicious_cases': [],
        'block_points': [],
    }


class CoverageExtendTests(unittest.TestCase):
    def legacy_report(self):
        complete = base_case(1, contract='4S', declarer='n',
                             dds_tables=[table(spades=9)])
        complete['calls'] = ['1N', 'P', '2H', 'P', '2S', 'P', '4S', 'P', 'P', 'P']
        complete['auction'] = '1NP2HP2SP4SPPP'
        return report_with(complete=[complete])

    def test_legacy_cell_is_topped_up_with_matching_pairs(self):
        updated = extend_ns_pairs(self.legacy_report(), blocking_profile(),
                                  target_pairs=3, seed=5)

        pairs = updated['cases'] + updated['complete_cases']
        self.assertEqual(len(pairs), 3)
        self.assertEqual(updated['budget']['pairs_per_cell'], 3)
        self.assertEqual(updated['extension']['added_pairs'], 2)
        self.assertEqual(updated['summary']['pairs'], 3)
        self.assertEqual(updated['summary']['blocked'], 2)
        self.assertEqual(updated['summary']['complete'], 1)
        self.assertEqual(sorted(case['id'] for case in pairs), [1, 2, 3])
        for case in updated['cases']:
            self.assertNotIn('coverage_cell', case)
            self.assertEqual(case_cell_key(case), 'legacy:10:6-3-2-2')
            self.assertEqual(case['south_hcp'], 10)
            self.assertEqual(case['south_shape'], [6, 3, 2, 2])
            self.assertEqual(case['north_shape'], [4, 3, 3, 3])
            self.assertEqual(case['north_hcp'], 15)
            self.assertLessEqual(abs(case['north_kr'] - 15.0), 2)
            self.assertLessEqual(abs(case['south_kr'] - 10.0), 2)
            self.assertEqual(case['calls'][:2], ['1N', 'P'])
            self.assertIn('blocked', case)

    def test_existing_cell_at_target_is_untouched(self):
        source = self.legacy_report()
        first = extend_ns_pairs(source, blocking_profile(), target_pairs=3, seed=5)
        second = extend_ns_pairs(first, blocking_profile(), target_pairs=3, seed=9)

        self.assertEqual(second['extension']['added_pairs'], 0)
        self.assertEqual(second['summary']['pairs'], 3)
        self.assertEqual([case['id'] for case in second['cases']],
                         [case['id'] for case in first['cases']])

    def test_explicit_coverage_cell_is_copied_and_next_slot_is_used(self):
        cell = {'target_hcp': 10, 'base_shape_index': 0,
                'base_shape': [6, 3, 2, 2], 'pair_slot': 0}
        existing = base_case(4, coverage_cell=cell)
        existing['blocked'] = {'seat': 's', 'diagnostics': ['No call']}
        report = report_with(blocked=[existing])

        updated = extend_ns_pairs(report, blocking_profile(),
                                  target_pairs=2, seed=7)

        self.assertEqual(len(updated['cases']), 2)
        new_case = max(updated['cases'], key=lambda case: case['id'])
        self.assertEqual(case_cell_key(new_case), '10:0')
        self.assertEqual(new_case['coverage_cell']['target_hcp'], 10)
        self.assertEqual(new_case['coverage_cell']['pair_slot'], 1)
        self.assertEqual(new_case['south_shape'], [6, 3, 2, 2])

    def test_invalid_cell_is_skipped_and_reported(self):
        broken = base_case(1)
        broken.pop('south_hcp')
        broken['north_shape'] = [4, 3, 3]
        report = report_with(blocked=[broken])

        updated = extend_ns_pairs(report, blocking_profile(),
                                  target_pairs=2, seed=3)

        self.assertEqual(updated['extension']['added_pairs'], 0)
        self.assertEqual(len(updated['extension']['skipped_cells']), 1)
        self.assertEqual(updated['extension']['skipped_cells'][0],
                         'legacy-fallback:1')

    def test_real_profile_can_add_a_complete_pair_with_injected_dds(self):
        from engine.loader import load_profile
        cell = {'target_hcp': 10, 'base_shape_index': 0,
                'base_shape': [6, 3, 2, 2], 'pair_slot': 0}
        existing = base_case(1, coverage_cell=cell)
        existing['blocked'] = {'seat': 's', 'diagnostics': ['No call']}
        report = report_with(blocked=[existing], budget={
            'pairs_per_cell': 1, 'ew_samples': 1,
            'min_class_boards': 1, 'min_class_pairs': 1})

        updated = extend_ns_pairs(
            report, load_profile('daqiush_2over1'), target_pairs=2, seed=11,
            solve_table=lambda deal: table(spades=10, nt=9))

        self.assertEqual(updated['extension']['added_pairs'], 1)
        new_case = max(updated['cases'] + updated['complete_cases'],
                       key=lambda case: case['id'])
        self.assertEqual(new_case['coverage_cell']['pair_slot'], 1)
        self.assertEqual(new_case['south_shape'], [6, 3, 2, 2])
        if 'contract' in new_case:
            self.assertEqual(len(new_case['dds_tables']), 1)

    def test_process_mode_fills_existing_processes_before_discovery(self):
        first = base_case(1)
        first.update(calls=['1N', 'P'], auction='1NP',
                     blocked={'seat': 's', 'diagnostics': ['No call']})
        second = base_case(2)
        second.update(calls=['1N', 'P', '2C'], auction='1NP2C',
                      blocked={'seat': 's', 'diagnostics': ['No call']})
        report = report_with(blocked=[first, second])

        updated = extend_process_pairs(
            report, blocking_profile(), target_pairs=2, seed=17,
            max_attempts_per_cell=50)

        by_calls = {}
        for case in updated['cases']:
            by_calls.setdefault(tuple(case['calls']), []).append(case)
        self.assertEqual(len(by_calls[('1N', 'P')]), 2)
        self.assertEqual(len(by_calls[('1N', 'P', '2C')]), 1)
        for cases in by_calls.values():
            for case in cases:
                self.assertEqual(case_cell_key(case), 'legacy:10:6-3-2-2')
        self.assertEqual(updated['extension']['kind'], 'process_pair_topup')
        self.assertEqual(updated['extension']['added_pairs'], 1)
        self.assertGreaterEqual(updated['extension']['attempted_pairs'], 1)
        self.assertEqual(updated['extension']['new_process_groups'], 0)
        self.assertEqual(len(updated['extension']['unreached_groups']), 1)
        self.assertEqual(updated['extension']['unreached_groups'][0]['auction'],
                         '1NP2C')
        self.assertEqual(updated['budget']['pairs_per_process_cell'], 2)

    def test_process_mode_opens_new_sub_cells_for_unseen_auctions(self):
        from types import SimpleNamespace
        from unittest.mock import patch
        from engine.cards import Hand

        existing = base_case(1)
        existing.update(calls=['1N', 'P'], auction='1NP',
                        blocked={'seat': 's', 'diagnostics': ['No call']})
        report = report_with(blocked=[existing])
        north = Hand.parse('SAKQJHKQJD432C432')
        south = Hand.parse('SAKQJ98H432D43C32')
        hands = {'n': north, 's': south, 'e': north, 'w': south}
        sequences = [('1N', 'P'), ('1N', 'P', '2C'), ('1N', 'P', '2C')]
        simulations = [
            SimpleNamespace(
                calls=calls, status='blocked',
                compact_sequence=(lambda calls=calls: ' '.join(calls)),
                blocked={'seat': 's', 'diagnostics': ['No call']},
                call_records=(),
            )
            for calls in sequences
        ]

        with patch('engine.coverage_extend.sample_partnership',
                   return_value=hands), patch(
                       'engine.coverage_extend.simulate_auction',
                       side_effect=simulations):
            updated = extend_process_pairs(
                report, blocking_profile(), target_pairs=2, seed=1,
                max_attempts_per_cell=3)

        by_calls = {}
        for case in updated['cases']:
            by_calls.setdefault(tuple(case['calls']), []).append(case)
        self.assertEqual(len(by_calls[('1N', 'P')]), 2)
        self.assertEqual(len(by_calls[('1N', 'P', '2C')]), 2)
        self.assertEqual(updated['extension']['added_pairs'], 3)
        self.assertEqual(updated['extension']['attempted_pairs'], 3)
        self.assertEqual(updated['extension']['new_process_groups'], 1)
        discovered = updated['extension']['discovered_processes'][0]
        self.assertEqual(discovered['auction'], '1N P 2C')
        self.assertEqual(discovered['pairs_added'], 2)
        self.assertEqual(discovered['remaining'], 0)
        self.assertEqual(updated['summary']['pairs'], 4)
        for case in updated['cases']:
            self.assertEqual(case_cell_key(case), 'legacy:10:6-3-2-2')

    def test_process_mode_is_noop_when_every_group_is_full(self):
        existing = base_case(1)
        existing.update(calls=['1N', 'P'], auction='1NP',
                        blocked={'seat': 's', 'diagnostics': ['No call']})
        updated = extend_process_pairs(
            report_with(blocked=[existing]), blocking_profile(),
            target_pairs=1, seed=1)

        self.assertEqual(updated['extension']['added_pairs'], 0)
        self.assertEqual(updated['extension']['attempted_pairs'], 0)

    def test_process_discovery_stops_after_idle_limit(self):
        from types import SimpleNamespace
        from unittest.mock import patch
        from engine.cards import Hand

        existing = base_case(1)
        existing.update(calls=['1N', 'P'], auction='1NP',
                        blocked={'seat': 's', 'diagnostics': ['No call']})
        report = report_with(blocked=[existing])
        north = Hand.parse('SAKQJHKQJD432C432')
        south = Hand.parse('SAKQJ98H432D43C32')
        hands = {'n': north, 's': south, 'e': north, 'w': south}
        simulations = [
            SimpleNamespace(
                calls=('1N', 'P'), status='blocked',
                compact_sequence=lambda: '1N P',
                blocked={'seat': 's', 'diagnostics': ['No call']},
                call_records=(),
            )
            for _ in range(10)
        ]

        with patch('engine.coverage_extend.sample_partnership',
                   return_value=hands), patch(
                       'engine.coverage_extend.simulate_auction',
                       side_effect=simulations):
            updated = extend_process_pairs(
                report, blocking_profile(), target_pairs=2, seed=1,
                max_attempts_per_cell=200, discovery_idle_limit=5)

        self.assertEqual(updated['extension']['added_pairs'], 1)
        self.assertEqual(updated['extension']['attempted_pairs'], 6)
        self.assertEqual(updated['extension']['new_process_groups'], 0)
        self.assertEqual(updated['extension']['discovery_idle_limit'], 5)

    def test_process_mode_reuses_the_parent_slot_allocator(self):
        cell = {'target_hcp': 10, 'base_shape_index': 0,
                'base_shape': [6, 3, 2, 2], 'pair_slot': 0}
        existing = base_case(3, coverage_cell=cell)
        existing.update(calls=['1N', 'P'], auction='1NP',
                        blocked={'seat': 's', 'diagnostics': ['No call']})

        updated = extend_process_pairs(
            report_with(blocked=[existing]), blocking_profile(),
            target_pairs=2, seed=2, max_attempts_per_cell=20)

        new_case = max(updated['cases'], key=lambda case: case['id'])
        self.assertEqual(case_cell_key(new_case), '10:0')
        self.assertEqual(new_case['coverage_cell']['pair_slot'], 1)

    def test_process_mode_cli_writes_a_topup_report(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            existing = base_case(1)
            existing.update(calls=['1N', 'P'], auction='1NP',
                            blocked={'seat': 's', 'diagnostics': ['No call']})
            source = root / 'old-report.json'
            source.write_text(
                json.dumps(report_with(blocked=[existing])), encoding='utf-8')
            output = root / 'old-report-process-topup.json'
            with patch('engine.loader.load_profile',
                       return_value=blocking_profile()):
                self.assertEqual(main([
                    str(source), '--profile', 'test', '--scope', 'process',
                    '--target-pairs', '2', '--max-attempts-per-cell', '20',
                    '--seed', '19', '--output', str(output),
                ]), 0)
            written = json.loads(output.read_text(encoding='utf-8'))
            self.assertEqual(written['extension']['kind'],
                             'process_pair_topup')
            self.assertEqual(written['extension']['added_pairs'], 1)
            self.assertTrue(output.with_suffix('.html').exists())

    def test_cli_writes_json_and_html_beside_output(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'old-report.json'
            source.write_text(json.dumps(self.legacy_report()), encoding='utf-8')
            output = root / 'old-report-topup.json'
            with patch('engine.loader.load_profile',
                       return_value=blocking_profile()):
                self.assertEqual(main([
                    str(source), '--profile', 'test', '--scope', 'sampling',
                    '--target-pairs', '2', '--seed', '13', '--output', str(output),
                ]), 0)
            written = json.loads(output.read_text(encoding='utf-8'))
            self.assertEqual(written['extension']['added_pairs'], 1)
            self.assertTrue(output.with_suffix('.html').exists())


    def explicit_report(self):
        cell = {'target_hcp': 10, 'base_shape_index': 0,
                'base_shape': [2, 2, 6, 3], 'pair_slot': 0,
                'opener_shape': [4, 3, 3, 3], 'opener_mode': 'normal'}
        existing = base_case(1, coverage_cell=cell)
        existing.update(calls=['1N', 'P'], auction='1NP',
                        blocked={'seat': 's', 'diagnostics': ['No call']})
        report = report_with(blocked=[existing])
        report['filters']['shapes'] = [[2, 2, 6, 3]]
        report['coverage'] = {'north': {
            'schema_status': 'explicit', 'required_cells': 92,
            'available_cells': 1, 'complete': False,
            'requested_strata': [{
                'shape': [4, 3, 3, 3], 'mode': 'normal',
                'cell': {'target_hcp': 10, 'base_shape_index': 0},
                'status': 'generated',
            }],
            'cell_failures': [],
        }}
        return report

    def test_explicit_extension_uses_the_joint_sampler_and_keeps_mode(self):
        from engine.loader import load_profile
        updated = extend_ns_pairs(
            self.explicit_report(), load_profile('daqiush_2over1'),
            target_pairs=2, seed=5, ew_samples=1,
            solve_table=lambda deal: table(spades=10, nt=9))

        self.assertEqual(updated['extension']['added_pairs'], 1)
        new_case = max(updated['cases'] + updated['complete_cases'],
                       key=lambda case: case['id'])
        self.assertEqual(new_case['coverage_cell']['opener_mode'], 'normal')
        self.assertEqual(new_case['coverage_cell']['opener_shape'],
                         [4, 3, 3, 3])
        self.assertTrue(15 <= new_case['north_hcp'] <= 17)
        self.assertLessEqual(abs(new_case['north_kr']
                                 - updated['cases'][0]['north_kr']), 2)
        north = updated['coverage']['north']
        self.assertEqual(north['schema_status'], 'explicit')
        self.assertEqual(north['pair_counts']['normal:4-3-3-3'], 2)
        self.assertFalse(north['cell_failures'])

    def test_conflicting_explicit_sibling_metadata_raises(self):
        from engine.loader import load_profile
        report = self.explicit_report()
        other = dict(report['cases'][0])
        other['id'] = 2
        other['coverage_cell'] = dict(other['coverage_cell'],
                                      opener_mode='upgrade_14')
        report['cases'].append(other)

        with self.assertRaises(ValueError):
            extend_ns_pairs(report, load_profile('daqiush_2over1'),
                            target_pairs=3, seed=6)


    def explicit_failure_report(self, *, existing=None, missing_slots=(0,)):
        report = report_with(
            blocked=[existing] if existing else [],
            budget={'pairs_per_cell': 1, 'ew_samples': 1,
                    'min_class_boards': 1, 'min_class_pairs': 1})
        report['filters']['shapes'] = [[2, 2, 6, 3]]
        status = 'partial' if existing else 'failed'
        report['coverage'] = {'north': {
            'schema_status': 'explicit', 'required_cells': 92,
            'available_cells': 1, 'complete': False,
            'requested_strata': [{
                'shape': [4, 3, 3, 3], 'mode': 'normal',
                'cell': {'target_hcp': 10, 'base_shape_index': 0},
                'status': status,
            }],
            'cell_failures': [{
                'shape': [4, 3, 3, 3], 'mode': 'normal',
                'cell': {'target_hcp': 10, 'base_shape_index': 0},
                'missing_pair_slots': list(missing_slots),
                'reason': 'generation_error: injected',
            }],
        }}
        return report

    def test_zero_case_failure_is_repaired_from_requested_schedule(self):
        from engine.loader import load_profile
        updated = extend_ns_pairs(
            self.explicit_failure_report(), load_profile('daqiush_2over1'),
            target_pairs=1, seed=8, solve_table=lambda deal: table(spades=10, nt=9))

        cases = updated['cases'] + updated['complete_cases']
        self.assertEqual(len(cases), 1)
        self.assertEqual(cases[0]['coverage_cell']['opener_mode'], 'normal')
        self.assertEqual(updated['coverage']['north']['cell_failures'], [])
        self.assertEqual(
            updated['coverage']['north']['pair_counts']['normal:4-3-3-3'], 1)
        self.assertEqual(
            updated['coverage']['north']['requested_strata'][0]['status'],
            'generated')

    def test_partial_failure_slot_is_repaired_and_record_cleared(self):
        from engine.loader import load_profile
        cell = {'target_hcp': 10, 'base_shape_index': 0,
                'base_shape': [2, 2, 6, 3], 'pair_slot': 0,
                'opener_shape': [4, 3, 3, 3], 'opener_mode': 'normal'}
        existing = base_case(1, coverage_cell=cell)
        existing.update(calls=['1N', 'P'], auction='1NP',
                        blocked={'seat': 's', 'diagnostics': ['No call']})
        updated = extend_ns_pairs(
            self.explicit_failure_report(existing=existing, missing_slots=(1,)),
            load_profile('daqiush_2over1'),
            target_pairs=1, seed=9, solve_table=lambda deal: table(spades=10, nt=9))

        cases = updated['cases'] + updated['complete_cases']
        self.assertEqual(len(cases), 2)
        self.assertEqual([case['coverage_cell']['pair_slot'] for case in cases],
                         [0, 1])
        self.assertEqual(updated['coverage']['north']['cell_failures'], [])
        self.assertEqual(
            updated['coverage']['north']['pair_counts']['normal:4-3-3-3'], 2)

    def test_zero_case_repair_requires_filters_shapes(self):
        report = self.explicit_failure_report()
        report['filters'].pop('shapes')

        with self.assertRaisesRegex(ValueError, r'filters\.shapes'):
            extend_ns_pairs(report, blocking_profile(), target_pairs=1)

    def test_zero_case_repair_rejects_malformed_filters_shape(self):
        report = self.explicit_failure_report()
        report['filters']['shapes'] = [[6, 3, 2]]

        with self.assertRaisesRegex(ValueError, r'filters\.shapes\[0\]'):
            extend_ns_pairs(report, blocking_profile(), target_pairs=1)

    def test_zero_case_repair_rejects_out_of_range_shape_index(self):
        report = self.explicit_failure_report()
        failure = report['coverage']['north']['cell_failures'][0]
        failure['cell']['base_shape_index'] = 1
        report['coverage']['north']['requested_strata'][0][
            'cell']['base_shape_index'] = 1

        with self.assertRaisesRegex(ValueError, 'base_shape_index'):
            extend_ns_pairs(report, blocking_profile(), target_pairs=1)

    def test_explicit_case_south_metadata_conflict_names_base_shape(self):
        report = self.explicit_report()
        report['cases'][0]['coverage_cell']['base_shape'] = [5, 3, 3, 2]

        with self.assertRaisesRegex(ValueError, r'10:0.*base_shape'):
            extend_ns_pairs(report, blocking_profile(), target_pairs=2)

    def test_explicit_case_requested_conflict_names_opener_mode(self):
        report = self.explicit_report()
        report['cases'][0]['coverage_cell']['opener_shape'] = [5, 3, 3, 2]
        report['cases'][0]['north_shape'] = [5, 3, 3, 2]
        report['coverage']['north']['requested_strata'][0][
            'shape'] = [5, 3, 3, 2]
        report['coverage']['north']['requested_strata'][0][
            'mode'] = 'upgrade_14'

        with self.assertRaisesRegex(ValueError, r'10:0.*opener_mode'):
            extend_ns_pairs(report, blocking_profile(), target_pairs=2)

    def test_failed_repair_keeps_only_missing_slots_with_new_reason(self):
        from engine.joint_deal_sampler import JointConstraintError
        from engine.loader import load_profile

        report = self.explicit_failure_report(missing_slots=(2, 4))
        with patch('engine.coverage_extend.sample_conditioned_partnership',
                   side_effect=JointConstraintError('still impossible')):
            updated = extend_ns_pairs(
                report, load_profile('daqiush_2over1'), target_pairs=1, seed=3)

        failures = updated['coverage']['north']['cell_failures']
        self.assertEqual(len(failures), 1)
        self.assertEqual(failures[0]['missing_pair_slots'], [2, 4])
        self.assertEqual(failures[0]['reason'],
                         'generation_error: still impossible')
        self.assertEqual(updated['summary']['pairs'], 0)

    def test_process_scope_keeps_authoritative_repair_when_discovery_disabled(self):
        from engine.loader import load_profile

        updated = extend_process_pairs(
            self.explicit_failure_report(), load_profile('daqiush_2over1'),
            target_pairs=1, seed=8, allow_new_processes=False,
            solve_table=lambda deal: table(spades=10, nt=9))

        pairs = updated['cases'] + updated['complete_cases']
        self.assertEqual(len(pairs), 1)
        self.assertEqual(updated['extension']['added_pairs'], 1)
        self.assertEqual(updated['coverage']['north']['cell_failures'], [])

    def test_repair_samples_exactly_the_persisted_missing_slots(self):
        from engine.loader import load_profile

        updated = extend_ns_pairs(
            self.explicit_failure_report(missing_slots=(2, 5)),
            load_profile('daqiush_2over1'), target_pairs=1, seed=12,
            solve_table=lambda deal: table(spades=10, nt=9))

        pairs = updated['cases'] + updated['complete_cases']
        self.assertEqual(len(pairs), 2)
        self.assertEqual(
            sorted(case['coverage_cell']['pair_slot'] for case in pairs),
            [2, 5])
        self.assertEqual(updated['extension']['added_pairs'], 2)

    def test_both_scopes_recompute_exact_kr_envelope_after_each_pair(self):
        from types import SimpleNamespace
        from engine.cards import Hand

        north = Hand.parse('SAKQJH432D432C432')
        south = Hand.parse('SAKQJ98H432D43C32')
        hands = {'n': north, 's': south, 'e': north, 'w': south}
        simulation = SimpleNamespace(
            calls=('1N', 'P'), status='blocked', call_records=(),
            compact_sequence=lambda: '1N P',
            blocked={'seat': 's', 'diagnostics': ['No call']})

        for scope in (extend_ns_pairs, extend_process_pairs):
            with self.subTest(scope=scope.__name__):
                plans = []

                def sampled(plan, **kwargs):
                    plans.append(plan)
                    return hands

                kwargs = ({'allow_new_processes': False,
                           'max_attempts_per_cell': 2}
                          if scope is extend_process_pairs else {})
                with patch(
                        'engine.coverage_extend.sample_conditioned_partnership',
                        side_effect=sampled), patch(
                        'engine.coverage_extend._opening_assessment',
                        return_value=object()), patch(
                        'engine.coverage_extend.simulate_auction',
                        return_value=simulation), patch(
                        'engine.coverage_extend.hand_kr',
                        side_effect=(16.0, 9.0, 14.0, 11.0)):
                    updated = scope(
                        self.explicit_report(), blocking_profile(),
                        target_pairs=3, **kwargs)

                self.assertEqual(updated['extension']['added_pairs'], 2)
                self.assertEqual([plan.north.kr for plan in plans],
                                 [(13.0, 17.0), (14.0, 17.0)])
                self.assertEqual([plan.south_kr for plan in plans],
                                 [(8.0, 12.0), (8.0, 11.0)])
                north_values = [case['north_kr'] for case in updated['cases']]
                south_values = [case['south_kr'] for case in updated['cases']]
                self.assertLessEqual(max(north_values) - min(north_values), 4)
                self.assertLessEqual(max(south_values) - min(south_values), 4)

    def test_explicit_summary_is_rebuilt_without_stale_counts(self):
        report = self.explicit_report()
        north = report['coverage']['north']
        north.update(
            observed_strata=[{'shape': [9, 2, 1, 1], 'mode': 'normal'}],
            cell_counts={'stale': 99}, pair_counts={'stale': 88},
            hcp_by_mode={'normal': [99]},
            ungenerated_strata=[{'reason': 'stale'}])

        updated = extend_ns_pairs(
            report, blocking_profile(), target_pairs=1)
        summary = updated['coverage']['north']

        self.assertNotIn('stale', summary['cell_counts'])
        self.assertNotIn('stale', summary['pair_counts'])
        self.assertEqual(len(summary['cell_counts']), 92)
        self.assertEqual(len(summary['pair_counts']), 92)
        self.assertEqual(summary['hcp_by_mode']['normal'], [15])
        self.assertEqual(summary['requested_strata'][0]['status'], 'generated')

    def test_explicit_stored_kr_span_over_four_names_cell_and_field(self):
        report = self.explicit_report()
        sibling = dict(report['cases'][0])
        sibling['id'] = 2
        sibling['north_kr'] = 20.0
        sibling['coverage_cell'] = dict(sibling['coverage_cell'], pair_slot=1)
        report['cases'].append(sibling)

        with self.assertRaisesRegex(ValueError, r'10:0.*north_kr'):
            extend_ns_pairs(report, blocking_profile(), target_pairs=3)

    def test_failed_authoritative_repair_is_not_retried_by_later_topup(self):
        from engine.joint_deal_sampler import JointConstraintError
        from engine.loader import load_profile

        cell = {'target_hcp': 10, 'base_shape_index': 0,
                'base_shape': [2, 2, 6, 3], 'pair_slot': 0,
                'opener_shape': [4, 3, 3, 3], 'opener_mode': 'normal'}
        existing = base_case(1, coverage_cell=cell)
        existing.update(calls=['1N', 'P'], auction='1NP',
                        blocked={'seat': 's', 'diagnostics': ['No call']})

        for scope in (extend_ns_pairs, extend_process_pairs):
            with self.subTest(scope=scope.__name__), patch(
                    'engine.coverage_extend.sample_conditioned_partnership',
                    side_effect=JointConstraintError('still impossible')) as sample:
                kwargs = ({'allow_new_processes': True,
                           'max_attempts_per_cell': 10}
                          if scope is extend_process_pairs else {})
                updated = scope(
                    self.explicit_failure_report(
                        existing=existing, missing_slots=(1,)),
                    load_profile('daqiush_2over1'), target_pairs=2, **kwargs)

            self.assertEqual(sample.call_count, 1)
            self.assertEqual(updated['summary']['pairs'], 1)
            failure = updated['coverage']['north']['cell_failures'][0]
            self.assertEqual(failure['missing_pair_slots'], [1])
            self.assertEqual(failure['reason'],
                             'generation_error: still impossible')

    def test_at_target_explicit_cell_rejects_target_hcp_over_37(self):
        report = self.explicit_report()
        for location in (
                report['cases'][0]['coverage_cell'],
                report['coverage']['north']['requested_strata'][0]['cell']):
            location['target_hcp'] = 38
        report['cases'][0]['south_hcp'] = 38

        with self.assertRaisesRegex(ValueError, r'cell 38:0.*target_hcp'):
            extend_ns_pairs(report, blocking_profile(), target_pairs=1)

    def test_case_metadata_target_hcp_over_37_is_field_specific(self):
        report = self.explicit_report()
        report['cases'][0]['coverage_cell']['target_hcp'] = 38
        report['cases'][0]['south_hcp'] = 38

        with self.assertRaisesRegex(ValueError, r'cell 38:0.*target_hcp'):
            extend_ns_pairs(report, blocking_profile(), target_pairs=1)

    def test_duplicate_cell_failure_identity_is_rejected(self):
        report = self.explicit_failure_report()
        report['coverage']['north']['cell_failures'].append(
            dict(report['coverage']['north']['cell_failures'][0]))

        with self.assertRaisesRegex(ValueError, r'duplicate.*10:0'):
            extend_ns_pairs(report, blocking_profile(), target_pairs=1)

    def test_missing_pair_slots_must_not_overlap_stored_pair_slots(self):
        cell = {'target_hcp': 10, 'base_shape_index': 0,
                'base_shape': [2, 2, 6, 3], 'pair_slot': 0,
                'opener_shape': [4, 3, 3, 3], 'opener_mode': 'normal'}
        existing = base_case(1, coverage_cell=cell)
        existing.update(blocked={'seat': 's', 'diagnostics': ['No call']})
        report = self.explicit_failure_report(
            existing=existing, missing_slots=(0,))

        with self.assertRaisesRegex(
                ValueError, r'cell 10:0.*missing_pair_slots.*pair_slot 0'):
            extend_ns_pairs(report, blocking_profile(), target_pairs=1)

    def test_missing_pair_slots_reject_bool_negative_and_duplicate_values(self):
        for slots in ([True], [-1], [2, 2]):
            with self.subTest(slots=slots):
                report = self.explicit_failure_report()
                report['coverage']['north']['cell_failures'][0][
                    'missing_pair_slots'] = slots
                with self.assertRaisesRegex(ValueError, 'missing_pair_slots'):
                    extend_ns_pairs(report, blocking_profile(), target_pairs=1)

    def test_both_scopes_reject_duplicate_stored_pair_slots(self):
        report = self.explicit_report()
        sibling = dict(report['cases'][0])
        sibling['id'] = 2
        sibling['coverage_cell'] = dict(sibling['coverage_cell'])
        report['cases'].append(sibling)

        for scope in (extend_ns_pairs, extend_process_pairs):
            with self.subTest(scope=scope.__name__):
                with self.assertRaisesRegex(
                        ValueError, r'cell 10:0.*pair_slot 0.*duplicate'):
                    scope(report, blocking_profile(), target_pairs=2)

    def test_zero_case_process_repair_enters_bounded_discovery(self):
        from types import SimpleNamespace
        from engine.cards import Hand

        north = Hand.parse('SAKQJH432D432C432')
        south = Hand.parse('SAKQJ98H432D43C32')
        hands = {'n': north, 's': south, 'e': north, 'w': south}

        def simulation(calls):
            return SimpleNamespace(
                calls=calls, status='blocked', call_records=(),
                compact_sequence=lambda: ' '.join(calls),
                blocked={'seat': 's', 'diagnostics': ['No call']})

        simulations = [
            simulation(('1N', 'P')),
            simulation(('1N', 'P', '2C')),
            simulation(('1N', 'P', '2C')),
        ]
        with patch(
                'engine.coverage_extend.sample_conditioned_partnership',
                return_value=hands), patch(
                'engine.coverage_extend._opening_assessment',
                return_value=object()), patch(
                'engine.coverage_extend.simulate_auction',
                side_effect=simulations):
            updated = extend_process_pairs(
                self.explicit_failure_report(), blocking_profile(),
                target_pairs=1, allow_new_processes=True,
                discovery_idle_limit=1, max_attempts_per_cell=3)

        by_calls = {}
        for case in updated['cases']:
            by_calls.setdefault(tuple(case['calls']), []).append(case)
        self.assertEqual(len(by_calls[('1N', 'P')]), 1)
        self.assertEqual(len(by_calls[('1N', 'P', '2C')]), 1)
        self.assertEqual(updated['extension']['added_pairs'], 2)
        self.assertEqual(updated['extension']['attempted_pairs'], 2)
        self.assertEqual(updated['extension']['new_process_groups'], 1)

    def test_exceptional_modes_reconstruct_then_extend_with_exact_hcp(self):
        from types import SimpleNamespace
        from engine.cards import Hand

        south = Hand.parse('SAKQJ98H432D43C32')
        exceptional = (
            ('upgrade_14', [5, 3, 3, 2],
             Hand.parse('SAKQJ9HK32DJ32C32'), 14),
            ('soft_18', [4, 4, 3, 2],
             Hand.parse('SAKQJHAQJ2DJ32C32'), 18),
        )
        simulation = SimpleNamespace(
            calls=('1N', 'P'), status='blocked', call_records=(),
            compact_sequence=lambda: '1N P',
            blocked={'seat': 's', 'diagnostics': ['No call']})

        for mode, shape, north, expected_hcp in exceptional:
            with self.subTest(mode=mode):
                report = self.explicit_failure_report()
                requested = report['coverage']['north']['requested_strata'][0]
                failure = report['coverage']['north']['cell_failures'][0]
                requested.update(shape=shape, mode=mode)
                failure.update(shape=shape, mode=mode)
                plans = []

                def sampled(plan, **kwargs):
                    plans.append(plan)
                    return {'n': north, 's': south,
                            'e': north, 'w': south}

                with patch(
                        'engine.coverage_extend.sample_conditioned_partnership',
                        side_effect=sampled), patch(
                        'engine.coverage_extend._opening_assessment',
                        return_value=object()), patch(
                        'engine.coverage_extend.simulate_auction',
                        return_value=simulation):
                    updated = extend_ns_pairs(
                        report, blocking_profile(), target_pairs=2)

                pairs = updated['cases'] + updated['complete_cases']
                self.assertEqual(len(pairs), 2)
                self.assertEqual([plan.north.mode for plan in plans],
                                 [mode, mode])
                self.assertTrue(all(case['north_hcp'] == expected_hcp
                                    for case in pairs))
                self.assertTrue(all(
                    case['coverage_cell']['opener_mode'] == mode
                    and case['coverage_cell']['opener_shape'] == shape
                    for case in pairs))
                self.assertEqual(
                    updated['coverage']['north']['hcp_by_mode'][mode],
                    [expected_hcp])

    def test_summary_rebuilds_all_fields_and_stably_deduplicates_strata(self):
        report = self.explicit_report()
        second_cell = {
            'target_hcp': 11, 'base_shape_index': 1,
            'base_shape': [3, 2, 2, 6], 'pair_slot': 0,
            'opener_shape': [4, 3, 3, 3], 'opener_mode': 'normal',
        }
        second = base_case(
            2, south_hcp=11, south_shape=(3, 2, 2, 6), north_hcp=17,
            coverage_cell=second_cell)
        second.update(blocked={'seat': 's', 'diagnostics': ['No call']})
        report['cases'].append(second)
        report['filters']['shapes'].append([3, 2, 2, 6])
        report['coverage']['north']['requested_strata'].append({
            'shape': [4, 3, 3, 3], 'mode': 'normal',
            'cell': {'target_hcp': 11, 'base_shape_index': 1},
            'status': 'failed',
        })

        summary = extend_ns_pairs(
            report, blocking_profile(), target_pairs=1)['coverage']['north']

        self.assertEqual(summary['required_cells'], 92)
        self.assertEqual(summary['available_cells'], 2)
        self.assertFalse(summary['complete'])
        self.assertEqual(summary['observed_strata'], [
            {'shape': [4, 3, 3, 3], 'mode': 'normal'}])
        self.assertEqual(len(summary['cell_counts']), 92)
        self.assertEqual(len(summary['pair_counts']), 92)
        self.assertEqual(summary['cell_counts']['normal:4-3-3-3'], 2)
        self.assertEqual(summary['pair_counts']['normal:4-3-3-3'], 2)
        self.assertEqual(summary['hcp_by_mode'], {
            'normal': [15, 17], 'upgrade_14': [], 'soft_18': []})
        self.assertEqual(
            [item['status'] for item in summary['requested_strata']],
            ['generated', 'generated'])
        omissions = summary['ungenerated_strata']
        self.assertEqual(len(omissions), 91)
        self.assertTrue(all(item['reason'] == 'insufficient_cells'
                            for item in omissions))

    def test_summary_retains_concrete_failure_beside_insufficient_omissions(self):
        from engine.joint_deal_sampler import JointConstraintError
        from engine.loader import load_profile

        with patch('engine.coverage_extend.sample_conditioned_partnership',
                   side_effect=JointConstraintError('still impossible')):
            summary = extend_ns_pairs(
                self.explicit_failure_report(),
                load_profile('daqiush_2over1'), target_pairs=1,
            )['coverage']['north']

        self.assertEqual(summary['required_cells'], 92)
        self.assertEqual(summary['available_cells'], 1)
        self.assertFalse(summary['complete'])
        self.assertEqual(summary['requested_strata'][0]['status'], 'failed')
        self.assertEqual(summary['pair_counts']['normal:4-3-3-3'], 0)
        self.assertEqual(summary['hcp_by_mode']['normal'], [])
        concrete = [item for item in summary['ungenerated_strata']
                    if item['cell'] is not None]
        omitted = [item for item in summary['ungenerated_strata']
                   if item['reason'] == 'insufficient_cells']
        self.assertEqual(len(concrete), 1)
        self.assertEqual(concrete[0]['reason'],
                         'generation_error: still impossible')
        self.assertEqual(len(omitted), 91)


if __name__ == '__main__':
    unittest.main()
