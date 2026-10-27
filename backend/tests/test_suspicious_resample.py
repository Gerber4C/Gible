import unittest
from copy import deepcopy

from engine.model import Author, Gadget, PartnershipProfile
from engine.suspicious_resample import (
    _rates_for_contract, _retained_flags, constraints_for_group,
    extend_ew_samples, resample_groups,
)
from engine.outcome_metrics import RULE_ID
from engine.suspicious_review_workflow import review_signature


class SuspiciousResampleTests(unittest.TestCase):
    def test_resampled_source_contract_rechecks_wrong_game_event(self):
        table = {strain: {seat: 6 for seat in 'ns'}
                 for strain in ('S', 'H', 'D', 'C', 'NT')}
        table['S']['n'] = 9
        table['NT']['s'] = 9
        rates = _rates_for_contract('4S', 'n', [table] * 2)
        self.assertEqual(rates['wrong_game'], 0.0)
        self.assertEqual(rates['alternative_game_rates']['3NT'], 1.0)

    def test_shared_set_wrong_and_best_other_boundaries_are_used(self):
        self.assertEqual(
            _retained_flags('4S', ['contract_failure'], {
                'contract_failure': .60, 'alternative_game_rates': {}}), [])
        self.assertEqual(
            _retained_flags('4S', ['contract_failure'], {
                'contract_failure': .600001, 'alternative_game_rates': {}}),
            ['contract_failure'])
        self.assertEqual(
            _retained_flags('4S', ['wrong_game'], {
                'wrong_game': .79, 'alternative_game_rates': {'3NT': .40}}), [])
        self.assertEqual(
            _retained_flags('4S', ['wrong_game'], {
                'wrong_game': .80, 'alternative_game_rates': {'3NT': .9}}), [])
        self.assertEqual(
            _retained_flags('4S', ['wrong_game'], {
                'wrong_game': .79, 'alternative_game_rates': {'3NT': .400001}}),
            ['wrong_game'])

    def test_wrong_game_source_alert_is_retained_below_success_ratio_threshold(self):
        opening = Gadget.from_parts(
            {'id': 'test', 'author': {'name': 'Test'}},
            [{'id': 'opening', 'context': {'auction_pattern': ''},
              'call': '1N', 'meaning': {'action_type': 'opening'}}],
        )
        profile = PartnershipProfile('test', 'Test', '1', Author('Test'),
                                     (opening,), missing_call_behavior='block')
        source_case = self.source_case(1)
        source_case['analysis'] = {'flags': ['wrong_game'],
                                   'rates': {'wrong_game': .4}, 'dds_boards': 10}
        source = {'schema_version': 2, 'seed': 23,
                  'suspicious_cases': [source_case]}
        table = {strain: {seat: 6 for seat in 'ns'}
                 for strain in ('S', 'H', 'D', 'C', 'NT')}
        table['NT']['s'] = 9
        result = resample_groups(source, profile, seed=101,
                                 pairs_per_group=1, ew_samples=2,
                                 solve_table=lambda hands: table)
        check = result['groups'][0]['source_checks'][0]
        self.assertEqual(check['new_rates']['wrong_game'], 0.0)
        self.assertEqual(check['retained_flags'], ['wrong_game'])
        self.assertEqual(result['wrong_game_rule'], RULE_ID)

    def test_legacy_source_flags_are_reclassified_before_grouping_without_mutation(self):
        opening = Gadget.from_parts(
            {'id': 'test', 'author': {'name': 'Test'}},
            [{'id': 'opening', 'context': {'auction_pattern': ''},
              'call': '1N', 'meaning': {'action_type': 'opening'}}],
        )
        profile = PartnershipProfile('test', 'Test', '1', Author('Test'),
                                     (opening,), missing_call_behavior='block')
        stale_wrong = self.source_case(1)
        stale_wrong['analysis'] = {
            'flags': ['wrong_game'],
            'rates': {'contract_failure': .30, 'wrong_game': .20},
            'alternative_game_rates': {'3NT': .75},
            'dds_boards': 10,
        }
        preserved_missed = self.source_case(2)
        preserved_missed['south_shape'] = [5, 4, 2, 2]
        preserved_missed['analysis'] = {
            'flags': ['wrong_game', 'missed_small_slam'],
            'rates': {'contract_failure': .30, 'wrong_game': .20,
                      'missed_small_slam': .40},
            'alternative_game_rates': {'3NT': .75},
            'dds_boards': 10,
        }
        source = {
            'schema_version': 2, 'seed': 23,
            'summary': {'suspicious': 2},
            'complete_cases': [stale_wrong, preserved_missed],
            'suspicious_cases': [stale_wrong, preserved_missed],
        }
        original = deepcopy(source)
        table = {strain: {seat: 6 for seat in 'ns'}
                 for strain in ('S', 'H', 'D', 'C', 'NT')}

        result = resample_groups(source, profile, seed=101,
                                 pairs_per_group=1, ew_samples=1,
                                 solve_table=lambda hands: table)

        self.assertEqual(result['summary']['source_groups'], 1)
        self.assertEqual(result['groups'][0]['source_ids'], [2])
        self.assertEqual(result['groups'][0]['source_checks'][0]['original_flags'],
                         ['missed_small_slam'])
        self.assertEqual(source, original)

    def source_case(self, case_id, *, north_hcp=16, north_kr=16.0):
        return {
            'id': case_id, 'trial': case_id, 'north_shape': [4, 3, 3, 3],
            'south_shape': [6, 3, 2, 2], 'north_hcp': north_hcp,
            'south_hcp': 10, 'north_kr': north_kr, 'south_kr': 11.0,
            'contract': '4S', 'declarer': 'n', 'auction': '1NPPP',
            'analysis': {'flags': ['contract_failure'],
                         'rates': {'contract_failure': .7}},
        }

    def test_group_constraints_keep_full_hcp_and_kr_span_within_two(self):
        north, south = constraints_for_group([
            self.source_case(1), self.source_case(2, north_hcp=17,
                                                  north_kr=17.5),
        ])
        self.assertEqual(north.shape, (4, 3, 3, 3))
        self.assertEqual(north.hcp, (16, 18))
        self.assertEqual(north.kr, (15.75, 17.75))
        self.assertEqual(south.shape, (6, 3, 2, 2))
        self.assertEqual(south.hcp, (9, 11))
        self.assertEqual(south.kr, (10.0, 12.0))

    def test_source_spanning_exactly_two_points_leaves_no_wider_sampling_window(self):
        north, _ = constraints_for_group([
            self.source_case(1, north_hcp=15, north_kr=15.5),
            self.source_case(2, north_hcp=17, north_kr=17.5),
        ])
        self.assertEqual(north.hcp, (15, 17))
        self.assertEqual(north.kr, (15.5, 17.5))
        with self.assertRaisesRegex(ValueError, 'two-point class span'):
            constraints_for_group([
                self.source_case(1, north_hcp=15),
                self.source_case(2, north_hcp=18),
            ])

    def test_each_small_group_gets_new_deals_bids_and_dds_evidence(self):
        opening = Gadget.from_parts(
            {'id': 'test', 'author': {'name': 'Test'}},
            [{'id': 'opening', 'context': {'auction_pattern': ''},
              'call': '1N', 'meaning': {'action_type': 'opening'}}],
        )
        profile = PartnershipProfile('test', 'Test', '1', Author('Test'),
                                     (opening,), missing_call_behavior='block')
        source = {'schema_version': 2, 'seed': 23,
                  'profile': {'id': 'test'},
                  'suspicious_cases': [self.source_case(1), self.source_case(2)]}
        table = {strain: {seat: 7 for seat in 'ns'}
                 for strain in ('S', 'H', 'D', 'C', 'NT')}
        result = resample_groups(
            source, profile, seed=101, pairs_per_group=2, ew_samples=2,
            solve_table=lambda hands: table,
        )
        self.assertEqual(len(result['groups']), 1)
        group = result['groups'][0]
        self.assertEqual(group['source_ids'], [1, 2])
        self.assertEqual(group['summary']['pairs'], 2)
        self.assertEqual(group['summary']['blocked'], 2)
        self.assertEqual(group['summary']['dds_boards'], 4)
        self.assertEqual(group['source_checks'][0]['new_rates']['contract_failure'], 1.0)
        self.assertEqual(group['source_checks'][0]['new_boards'], 4)
        self.assertEqual(len(group['deals']), 2)
        self.assertEqual(group['deals'][0]['calls'], ['1N', 'P'])
        self.assertTrue(all(item['north_shape'] == [4, 3, 3, 3]
                            for item in group['deals']))
        for seat in ('north', 'south'):
            old_hcp = [case[f'{seat}_hcp'] for case in source['suspicious_cases']]
            new_hcp = [case[f'{seat}_hcp'] for case in group['deals']]
            old_kr = [case[f'{seat}_kr'] for case in source['suspicious_cases']]
            new_kr = [case[f'{seat}_kr'] for case in group['deals']]
            self.assertLessEqual(max(old_hcp + new_hcp) - min(old_hcp + new_hcp), 2)
            self.assertLessEqual(max(old_kr + new_kr) - min(old_kr + new_kr), 2.000001)

    def test_existing_pairs_can_gain_ten_ew_boards_without_changing_auctions(self):
        opening = Gadget.from_parts(
            {'id': 'test', 'author': {'name': 'Test'}},
            [{'id': 'opening', 'context': {'auction_pattern': ''},
              'call': '1N', 'meaning': {'action_type': 'opening'}}],
        )
        profile = PartnershipProfile('test', 'Test', '1', Author('Test'),
                                     (opening,), missing_call_behavior='block')
        source = {'schema_version': 2, 'seed': 23,
                  'suspicious_cases': [self.source_case(1)]}
        table = {strain: {seat: 7 for seat in 'ns'}
                 for strain in ('S', 'H', 'D', 'C', 'NT')}
        old = resample_groups(source, profile, seed=101,
                              pairs_per_group=1, ew_samples=2,
                              solve_table=lambda hands: table)
        old_case = old['groups'][0]['deals'][0]
        expanded = extend_ew_samples(
            old, ew_samples=10, workers=1, solve_table=lambda hands: table)
        new_case = expanded['groups'][0]['deals'][0]
        self.assertEqual(expanded['budget']['ew_samples'], 10)
        self.assertEqual(old['wrong_game_rule'], RULE_ID)
        self.assertEqual(expanded['wrong_game_rule'], RULE_ID)
        self.assertEqual(expanded['summary']['dds_boards'], 10)
        self.assertEqual(expanded['groups'][0]['source_checks'][0]['new_boards'], 10)
        self.assertEqual(new_case['id'], old_case['id'])
        self.assertEqual(new_case['hands'], old_case['hands'])
        self.assertEqual(new_case['auction'], old_case['auction'])
        self.assertEqual(new_case['dds_tables'][:2], old_case['dds_tables'])
        self.assertEqual(len(new_case['dds_tables']), 10)
        self.assertEqual(old['budget']['ew_samples'], 2)
        self.assertEqual(review_signature(expanded), review_signature(old))

    def test_groups_larger_than_limit_are_not_resampled(self):
        source = {'schema_version': 2, 'seed': 23,
                  'suspicious_cases': [self.source_case(i) for i in range(1, 12)]}
        profile = PartnershipProfile('test', 'Test', '1', Author('Test'),
                                     (), missing_call_behavior='block')
        result = resample_groups(source, profile, seed=3, max_source_cases=10,
                                 pairs_per_group=1, ew_samples=1,
                                 solve_table=lambda hands: {})
        self.assertEqual(result['groups'], [])
        self.assertEqual(result['summary']['skipped_large_groups'], 1)


if __name__ == '__main__':
    unittest.main()
