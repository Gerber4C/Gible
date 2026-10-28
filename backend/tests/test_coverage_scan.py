import math
import random
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from engine.cards import Hand
from engine.coverage_scan import (
    COVERAGE_SHAPES, _contract, sample_partnership, scan_coverage,
    wrong_game_rates,
)
from engine.dds_adapter import deal_to_pbn
from engine.hand_quality import assess_quality
from engine.model import Author, Gadget, PartnershipProfile
from engine.outcome_metrics import RULE_ID, assess_auction_groups


class CoverageSamplingTests(unittest.TestCase):
    def test_extreme_responder_hcp_and_shapes_are_constructed_as_full_deals(self):
        rng = random.Random(64)
        for hcp, shape in ((0, (4, 3, 3, 3)), (22, (8, 3, 1, 1)),
                           (11, (6, 4, 2, 1))):
            with self.subTest(hcp=hcp, shape=shape):
                hands = sample_partnership(
                    rng, hcp, shape,
                    opener_eligible=lambda hand: 15 <= hand.hcp <= 17,
                )
                self.assertEqual(hands['s'].hcp, hcp)
                self.assertEqual(tuple(hands['s'].length(s) for s in 'SHDC'), shape)
                self.assertIn(hands['n'].hcp, (14, 15, 16, 17, 18))
                deal_to_pbn(hands)

    def test_representative_shapes_cover_all_requested_margins(self):
        self.assertEqual(len(COVERAGE_SHAPES), 23)
        self.assertEqual(len(set(COVERAGE_SHAPES)), 23)
        self.assertIn((8, 3, 2, 0), COVERAGE_SHAPES)
        self.assertNotIn((7, 5, 1, 0), COVERAGE_SHAPES)
        self.assertEqual({max(shape) for shape in COVERAGE_SHAPES}, set(range(4, 9)))
        self.assertEqual({sum(sorted(shape, reverse=True)[:2])
                          for shape in COVERAGE_SHAPES}, set(range(7, 12)))
        self.assertTrue(all(sum(shape) == 13 for shape in COVERAGE_SHAPES))
        self.assertEqual(
            {(max(shape), sum(sorted(shape, reverse=True)[:2]))
             for shape in COVERAGE_SHAPES},
            {(4, 7), (4, 8), (5, 8), (5, 9), (5, 10),
             (6, 9), (6, 10), (6, 11), (7, 9), (7, 10),
             (7, 11), (8, 10), (8, 11)},
        )

    def test_north_opener_is_not_fixed_to_one_shape(self):
        rng = random.Random(12)
        north_shapes = set()
        for _ in range(24):
            hands = sample_partnership(
                rng, 10, (5, 3, 3, 2),
                opener_eligible=lambda hand: 15 <= hand.hcp <= 17,
            )
            north_shapes.add(tuple(hands['n'].length(s) for s in 'SHDC'))
        self.assertGreater(len(north_shapes), 1)

    def test_second_independent_pair_matches_both_hcp_and_kr_within_two(self):
        rng = random.Random(84)
        options = {'opener_eligible': lambda hand: hand.hcp == 16,
                   'opener_shape': (4, 3, 3, 3), 'opener_hcp': 16}
        first = sample_partnership(rng, 11, (6, 3, 2, 2), **options)
        reference = (assess_quality(first['n'])['kr_points'],
                     assess_quality(first['s'])['kr_points'])
        second = sample_partnership(rng, 11, (6, 3, 2, 2),
                                    reference=reference, **options)
        for seat, desired_shape, target_hcp, target_kr in (
                ('n', (4, 3, 3, 3), 16, reference[0]),
                ('s', (6, 3, 2, 2), 11, reference[1])):
            self.assertEqual(tuple(second[seat].length(s) for s in 'SHDC'),
                             desired_shape)
            self.assertEqual(second[seat].hcp, target_hcp)
            self.assertLessEqual(abs(assess_quality(second[seat])['kr_points']
                                     - target_kr), 2)
        self.assertNotEqual((first['n'], first['s']), (second['n'], second['s']))

    def test_scan_fixes_north_1nt_and_records_coverage_even_when_responses_block(self):
        gadget = Gadget.from_parts(
            {'id': 'test', 'author': {'name': 'Test'}},
            [{'id': 'opening', 'context': {'auction_pattern': ''},
              'call': '1N', 'meaning': {'action_type': 'opening'}}],
        )
        profile = PartnershipProfile('test', 'Test', '1', Author('Test'),
                                     (gadget,), missing_call_behavior='block')
        options = {'seed': 5, 'hcp_targets': (0, 22),
                   'shapes': ((4, 3, 3, 3), (8, 3, 1, 1)),
                   'pairs_per_cell': 1, 'ew_samples': 2}
        report = scan_coverage(profile, **options)
        self.assertEqual(report, scan_coverage(profile, **options))
        self.assertEqual(report['summary']['pairs'], 4)
        self.assertEqual(report['summary']['blocked'], 4)
        self.assertEqual(report['wrong_game_rule'], RULE_ID)
        self.assertEqual(report['coverage']['responder_hcp'], [0, 22])
        self.assertEqual(report['coverage']['longest_suit'], [4, 8])
        self.assertEqual(len(report['coverage']['cells']), 4)
        for case in report['cases']:
            self.assertEqual(case['dealer'], 'n')
            self.assertEqual(case['calls'][:2], ['1N', 'P'])
            self.assertEqual(case['blocked']['seat'], 's')
            deal_to_pbn(case['hands'])

    def test_pairs_within_one_quota_cell_are_independent_but_same_class(self):
        gadget = Gadget.from_parts(
            {'id': 'test', 'author': {'name': 'Test'}},
            [{'id': 'opening', 'context': {'auction_pattern': ''},
              'call': '1N', 'meaning': {'action_type': 'opening'}}],
        )
        profile = PartnershipProfile('test', 'Test', '1', Author('Test'),
                                     (gadget,), missing_call_behavior='block')
        report = scan_coverage(profile, seed=41, hcp_targets=(10,),
                               shapes=((6, 3, 2, 2),), pairs_per_cell=3,
                               ew_samples=1)
        first, second, third = report['cases']
        self.assertNotEqual((first['hands']['n'], first['hands']['s']),
                            (second['hands']['n'], second['hands']['s']))
        for other in (second, third):
            for field in ('north_shape', 'south_shape', 'north_hcp', 'south_hcp'):
                self.assertEqual(first[field], other[field])
            self.assertLessEqual(abs(first['north_kr'] - other['north_kr']), 2)
            self.assertLessEqual(abs(first['south_kr'] - other['south_kr']), 2)
        self.assertEqual([case['coverage_cell'] for case in report['cases']], [
            {'target_hcp': 10, 'base_shape_index': 0,
             'base_shape': [6, 3, 2, 2], 'pair_slot': slot}
            for slot in range(3)
        ])
        all_cases = (report['cases'] + report['complete_cases']
                     + report['limit_cases'])
        self.assertEqual(sorted(case['id'] for case in all_cases), [1, 2, 3])

    def test_call_limit_case_is_retained_and_does_not_run_dds(self):
        gadget = Gadget.from_parts(
            {'id': 'test', 'author': {'name': 'Test'}},
            [{'id': 'opening', 'context': {'auction_pattern': ''},
              'call': '1N', 'meaning': {'action_type': 'opening'}}],
        )
        profile = PartnershipProfile('test', 'Test', '1', Author('Test'),
                                     (gadget,), missing_call_behavior='block')
        simulation = SimpleNamespace(
            calls=('1N', 'P'), status='limit', call_records=(), blocked=None,
            compact_sequence=lambda: '1N P',
        )
        dds_calls = []

        with patch('engine.coverage_scan.simulate_auction', return_value=simulation):
            report = scan_coverage(
                profile, seed=42, hcp_targets=(10,),
                shapes=((6, 3, 2, 2),), pairs_per_cell=1, ew_samples=2,
                solve_table=lambda deal: dds_calls.append(deal),
            )

        self.assertEqual(dds_calls, [])
        self.assertEqual(report['cases'], [])
        self.assertEqual(report['complete_cases'], [])
        self.assertEqual(len(report['limit_cases']), 1)
        case = report['limit_cases'][0]
        self.assertEqual(case['status'], 'limit')
        self.assertEqual(case['calls'], ['1N', 'P'])
        self.assertEqual(case['auction'], '1N P')
        self.assertIn('hands', case)
        self.assertEqual(case['coverage_cell'], {
            'target_hcp': 10, 'base_shape_index': 0,
            'base_shape': [6, 3, 2, 2], 'pair_slot': 0,
        })


class AuctionGroupTests(unittest.TestCase):
    @staticmethod
    def table(*, spades=6, nt=6, hearts=6):
        values = {strain: {seat: 6 for seat in 'ns'}
                  for strain in ('S', 'H', 'D', 'C', 'NT')}
        values['S'].update(n=spades, s=spades)
        values['NT'].update(n=nt, s=nt)
        values['H'].update(n=hearts, s=hearts)
        return values

    @staticmethod
    def case(case_id, *, boards, calls=('1N', 'P', '2H', 'P', '2S', 'P', 'P', 'P'),
             contract='2S', declarer='s', hcp=11, shape=(6, 3, 2, 2),
             cell_index=0, pair_slot=0):
        return {
            'id': case_id,
            'coverage_cell': {'target_hcp': hcp, 'base_shape_index': cell_index,
                              'base_shape': list(shape), 'pair_slot': pair_slot},
            'south_hcp': hcp, 'south_shape': list(shape),
            'contract': contract, 'declarer': declarer,
            'calls': list(calls), 'auction': ' '.join(calls),
            'dds_tables': boards,
        }

    @classmethod
    def analysis_for(cls, cases, case_id, **options):
        for members, analysis in assess_auction_groups(cases, **options):
            if any(member['id'] == case_id for member in members):
                return analysis
        raise AssertionError('case missing from auction groups')

    def test_perfect_chosen_game_has_finite_completion_ratio(self):
        ratio, alternatives = wrong_game_rates(
            '4S', 'n', [self.table(spades=10, nt=9), self.table(spades=10, nt=8)])

        self.assertEqual(ratio, 2.0)
        self.assertTrue(math.isfinite(ratio))
        self.assertEqual(alternatives['3NT'], .5)

    def test_same_cell_and_same_auction_pool_boards_and_share_flags(self):
        failing = self.table(spades=9)
        making = self.table(spades=10)
        calls = ('1N', 'P', '2H', 'P', '2S', 'P', '4S', 'P', 'P', 'P')
        first = self.case(1, boards=[failing] * 5, contract='4S',
                          declarer='n', calls=calls)
        second = self.case(2, boards=[failing] * 2 + [making] * 3,
                           contract='4S', declarer='n', calls=calls,
                           pair_slot=1)

        first_analysis = self.analysis_for([first, second], 1)
        second_analysis = self.analysis_for([first, second], 2)

        self.assertEqual(first_analysis['class_pairs'], 2)
        self.assertEqual(first_analysis['dds_boards'], 10)
        self.assertEqual(first_analysis['rates']['contract_failure'], .7)
        self.assertIn('contract_failure', first_analysis['flags'])
        self.assertEqual(first_analysis, second_analysis)

    def test_different_auctions_split_one_sampling_cell(self):
        calls_a = ('1N', 'P', '2H', 'P', '2S', 'P', '4S', 'P', 'P', 'P')
        calls_b = ('1N', 'P', '3N', 'P', 'P', 'P')
        first = self.case(1, boards=[self.table(spades=9)] * 10,
                          contract='4S', declarer='n', calls=calls_a)
        second = self.case(2, boards=[self.table(spades=10, nt=9)] * 10,
                           contract='3NT', declarer='s', calls=calls_b,
                           pair_slot=1)

        groups = assess_auction_groups([first, second], min_boards=10)

        self.assertEqual(len(groups), 2)
        self.assertEqual([len(members) for members, _ in groups], [1, 1])
        self.assertIn('contract_failure',
                      self.analysis_for([first, second], 1)['flags'])
        self.assertEqual(self.analysis_for([first, second], 2)['flags'], [])

    def test_same_auction_in_different_cells_is_not_merged(self):
        first = self.case(1, boards=[self.table()] * 10, cell_index=0)
        second = self.case(2, boards=[self.table()] * 10, cell_index=1,
                           pair_slot=1)

        groups = assess_auction_groups([first, second], min_boards=10)

        self.assertEqual(len(groups), 2)
        self.assertEqual([group['class_pairs'] for _, group in groups], [1, 1])

    def test_single_pair_group_is_assessed_when_boards_are_sufficient(self):
        case = self.case(1, boards=[self.table()] * 10)

        assessed = self.analysis_for([case], 1, min_boards=10)
        self.assertEqual(assessed['status'], 'assessed')
        self.assertEqual(assessed['class_pairs'], 1)
        self.assertEqual(assessed['dds_boards'], 10)

        unassessed = self.analysis_for([case], 1, min_boards=11)
        self.assertEqual(unassessed['status'], 'insufficient_data')
        self.assertEqual(unassessed['flags'], [])

    def test_wrong_game_uses_group_completion_ratio(self):
        chosen_make = self.table(spades=10, nt=8)
        other_make = self.table(spades=9, nt=9)
        boards = [chosen_make] * 4 + [other_make] * 6
        calls = ('1N', 'P', '2H', 'P', '2S', 'P', '4S', 'P', 'P', 'P')
        first = self.case(1, boards=boards[:5], contract='4S',
                          declarer='n', calls=calls)
        second = self.case(2, boards=boards[5:], contract='4S',
                           declarer='n', calls=calls, pair_slot=1)

        analysis = self.analysis_for([first, second], 1, min_boards=10)

        self.assertAlmostEqual(analysis['rates']['wrong_game'], 2 / 3)
        self.assertIn('wrong_game', analysis['flags'])
        self.assertEqual(analysis['alternative_game_rates']['3NT'], .6)

    def test_wrong_game_does_not_apply_to_partscore_or_slam(self):
        table = self.table(spades=13, nt=13, hearts=13)
        for contract in ('2S', '6S'):
            with self.subTest(contract=contract):
                case = self.case(1, boards=[table], contract=contract,
                                 declarer='n')
                analysis = self.analysis_for([case], 1, min_boards=1)
                self.assertIsNone(analysis['rates']['wrong_game'])
                self.assertNotIn('wrong_game', analysis['flags'])

    def test_final_declarer_is_first_partner_to_bid_final_strain(self):
        self.assertEqual(_contract(('1N', 'P', '2D', 'P', '2H', 'P', 'P', 'P')),
                         ('2H', 'n'))

    def test_final_declarer_respects_non_north_dealer(self):
        self.assertEqual(_contract(('1H', 'P', 'P', 'P'), dealer='s'), ('1H', 's'))

    def test_group_flags_failed_contract_and_missed_game(self):
        table = {'H': {'s': 7, 'n': 7}, 'NT': {'n': 9, 's': 8},
                 'S': {'n': 8, 's': 8}, 'D': {'n': 9, 's': 9},
                 'C': {'n': 9, 's': 9}}
        calls = ('1N', 'P', '2D', 'P', '2H', 'P', 'P', 'P')
        first = self.case(1, boards=[table], contract='2H',
                          declarer='s', calls=calls)
        second = self.case(2, boards=[table], contract='2H',
                           declarer='s', calls=calls, pair_slot=1)

        analysis = self.analysis_for([first, second], 1, min_boards=2)

        self.assertEqual(analysis['class_pairs'], 2)
        self.assertEqual(analysis['dds_boards'], 2)
        self.assertIn('contract_failure', analysis['flags'])
        self.assertIn('missed_game', analysis['flags'])
        self.assertEqual(analysis['rates']['contract_failure'], 1.0)
        self.assertEqual(analysis['rates']['missed_game'], 1.0)


class OpenerScheduleTests(unittest.TestCase):
    def test_complete_opener_schedule_assigns_every_stratum(self):
        from engine.coverage_scan import build_coverage_schedule
        schedule = build_coverage_schedule(range(23), COVERAGE_SHAPES, 2)

        self.assertEqual(schedule['available_cells'], 529)
        self.assertEqual(schedule['required_cells'], 92)
        self.assertTrue(schedule['complete'])
        self.assertEqual(len(schedule['entries']), 1058)
        self.assertEqual(len({tuple(entry['opener_shape'])
                             for entry in schedule['entries']}), 68)
        upgrade = sum(entry['opener_mode'] == 'upgrade_14'
                      for entry in schedule['entries'])
        soft = sum(entry['opener_mode'] == 'soft_18'
                   for entry in schedule['entries'])
        self.assertEqual((upgrade, soft), (24, 24))

    def test_partial_schedule_reports_incomplete_north_coverage(self):
        from engine.coverage_scan import build_coverage_schedule
        schedule = build_coverage_schedule(range(10), COVERAGE_SHAPES[:3], 1)

        self.assertEqual(schedule['available_cells'], 30)
        self.assertEqual(schedule['required_cells'], 92)
        self.assertFalse(schedule['complete'])
        self.assertEqual(len(schedule['entries']), 30)
        self.assertGreater(len(schedule['ungenerated_strata']), 0)


if __name__ == '__main__':
    unittest.main()
