import random
import unittest

from engine.cards import Hand
from engine.coverage_scan import (
    COVERAGE_SHAPES, _contract, classify_suspicious, sample_partnership, scan_coverage,
)
from engine.dds_adapter import deal_to_pbn
from engine.hand_quality import assess_quality
from engine.model import Author, Gadget, PartnershipProfile


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
                               shapes=((6, 3, 2, 2),), pairs_per_cell=2,
                               ew_samples=1)
        first, second = report['cases']
        self.assertNotEqual((first['hands']['n'], first['hands']['s']),
                            (second['hands']['n'], second['hands']['s']))
        for field in ('north_shape', 'south_shape', 'north_hcp', 'south_hcp'):
            self.assertEqual(first[field], second[field])
        self.assertLessEqual(abs(first['north_kr'] - second['north_kr']), 2)
        self.assertLessEqual(abs(first['south_kr'] - second['south_kr']), 2)


class SuspicionTests(unittest.TestCase):
    def test_wrong_game_requires_failed_chosen_game_and_a_different_made_game(self):
        subject = {'id': 1, 'north_shape': (4, 3, 3, 3),
                   'south_shape': (6, 3, 2, 2), 'north_hcp': 16,
                   'south_hcp': 11, 'north_kr': 16.0, 'south_kr': 12.0,
                   'contract': '4S', 'declarer': 'n'}
        neighbor = {**subject, 'id': 2}

        def table(spade_n, nt_n=8, heart_n=8):
            values = {strain: {seat: 6 for seat in 'ns'}
                      for strain in ('S', 'H', 'D', 'C', 'NT')}
            values['S']['n'] = spade_n
            values['NT']['n'] = nt_n
            values['H']['n'] = heart_n
            return values

        # 4S succeeds on 4/10 boards while 3NT succeeds on 6/10. The selected
        # game's success odds are therefore 0.4/0.6, versus 0.6/0.4 for 3NT.
        boards = ([table(10)] * 4
                  + [table(9, nt_n=9, heart_n=10)] * 6)
        result = classify_suspicious(subject, [subject, neighbor],
                                     {1: boards[:5], 2: boards[5:]},
                                     min_boards=10)
        self.assertAlmostEqual(result['rates']['wrong_game'], 4 / 9)
        self.assertIn('wrong_game', result['flags'])
        self.assertEqual(result['alternative_game_rates']['3NT'], .6)
        self.assertEqual(result['alternative_game_rates']['4H'], .6)

    def test_wrong_game_does_not_apply_to_partscore_or_slam(self):
        base = {'id': 1, 'north_shape': (4, 3, 3, 3),
                'south_shape': (6, 3, 2, 2), 'north_hcp': 16,
                'south_hcp': 11, 'north_kr': 16.0, 'south_kr': 12.0,
                'declarer': 'n'}
        table = {strain: {seat: 13 for seat in 'ns'}
                 for strain in ('S', 'H', 'D', 'C', 'NT')}
        for contract in ('2S', '6S'):
            with self.subTest(contract=contract):
                subject = {**base, 'contract': contract}
                result = classify_suspicious(subject, [subject],
                                             {1: [table]}, min_pairs=1,
                                             min_boards=1)
                self.assertIsNone(result['rates']['wrong_game'])
                self.assertNotIn('wrong_game', result['flags'])

    def test_class_span_is_at_most_two_not_two_either_side_of_subject(self):
        subject = {'id': 1, 'north_shape': (4, 3, 3, 3),
                   'south_shape': (6, 3, 2, 2), 'north_hcp': 16,
                   'south_hcp': 11, 'north_kr': 16.0, 'south_kr': 12.0,
                   'contract': '4S', 'declarer': 'n'}
        low = {**subject, 'id': 2, 'north_hcp': 14, 'north_kr': 14.0}
        high = {**subject, 'id': 3, 'north_hcp': 18, 'north_kr': 18.0}
        table = {strain: {seat: 9 for seat in 'ns'}
                 for strain in ('S', 'H', 'D', 'C', 'NT')}
        result = classify_suspicious(subject, [subject, low, high],
                                     {1: [table], 2: [table], 3: [table]},
                                     min_boards=1, min_pairs=1)
        self.assertEqual(result['class_pairs'], 2)

    def test_final_declarer_is_first_partner_to_bid_final_strain(self):
        self.assertEqual(_contract(('1N', 'P', '2D', 'P', '2H', 'P', 'P', 'P')),
                         ('2H', 'n'))

    def test_final_declarer_respects_non_north_dealer(self):
        self.assertEqual(_contract(('1H', 'P', 'P', 'P'), dealer='s'), ('1H', 's'))

    def test_flags_failed_contract_and_missed_game_from_nearby_class(self):
        first = {'id': 1, 'north_shape': (4, 3, 3, 3),
                 'south_shape': (6, 3, 2, 2), 'north_hcp': 16,
                 'south_hcp': 11, 'north_kr': 16.0, 'south_kr': 12.0,
                 'contract': '2H', 'declarer': 's'}
        nearby = {**first, 'id': 2, 'north_hcp': 18, 'south_hcp': 9,
                  'north_kr': 17.9, 'south_kr': 10.1}
        far = {**first, 'id': 3, 'north_hcp': 19, 'north_kr': 17.0}
        far_kr = {**first, 'id': 4, 'south_kr': 14.1}
        far_south_hcp = {**first, 'id': 5, 'south_hcp': 14}
        records = [first, nearby, far, far_kr, far_south_hcp]
        tables = {
            1: [{'H': {'s': 7, 'n': 7}, 'NT': {'n': 9, 's': 8},
                 'S': {'n': 8, 's': 8}, 'D': {'n': 9, 's': 9}, 'C': {'n': 9, 's': 9}}],
            2: [{'H': {'s': 7, 'n': 7}, 'NT': {'n': 9, 's': 8},
                 'S': {'n': 8, 's': 8}, 'D': {'n': 9, 's': 9}, 'C': {'n': 9, 's': 9}}],
            3: [{'H': {'s': 8, 'n': 8}, 'NT': {'n': 6, 's': 6},
                 'S': {'n': 8, 's': 8}, 'D': {'n': 9, 's': 9}, 'C': {'n': 9, 's': 9}}],
            4: [{'H': {'s': 8, 'n': 8}, 'NT': {'n': 6, 's': 6},
                 'S': {'n': 8, 's': 8}, 'D': {'n': 9, 's': 9}, 'C': {'n': 9, 's': 9}}],
            5: [{'H': {'s': 8, 'n': 8}, 'NT': {'n': 6, 's': 6},
                 'S': {'n': 8, 's': 8}, 'D': {'n': 9, 's': 9}, 'C': {'n': 9, 's': 9}}],
        }
        result = classify_suspicious(first, records, tables, min_boards=2)
        self.assertEqual(result['class_pairs'], 2)
        self.assertEqual(result['dds_boards'], 2)
        self.assertIn('contract_failure', result['flags'])
        self.assertIn('missed_game', result['flags'])
        self.assertEqual(result['rates']['contract_failure'], 1.0)
        self.assertEqual(result['rates']['missed_game'], 1.0)

    def test_insufficient_boards_are_unassessed_not_suspicious(self):
        record = {'id': 1, 'north_shape': (4, 3, 3, 3),
                  'south_shape': (6, 3, 2, 2), 'north_hcp': 16,
                  'south_hcp': 11, 'north_kr': 16.0, 'south_kr': 12.0,
                  'contract': '2H', 'declarer': 's'}
        table = {strain: {seat: 13 for seat in 'ns'}
                 for strain in ('S', 'H', 'D', 'C', 'NT')}
        result = classify_suspicious(record, [record], {1: [table]}, min_boards=5)
        self.assertEqual(result['status'], 'insufficient_data')
        self.assertEqual(result['flags'], [])
        result = classify_suspicious(record, [record], {1: [table] * 10},
                                     min_boards=10)
        self.assertEqual(result['status'], 'insufficient_data')


if __name__ == '__main__':
    unittest.main()
