import unittest

from engine.constrained_deals import (
    ConstrainedDealSampler, HandConstraints, bid_constrained_deals,
)
from engine.coverage_scan import hand_kr
from engine.dds_adapter import deal_to_pbn
from engine.model import Author, Gadget, PartnershipProfile


class ConstrainedDealSamplerTests(unittest.TestCase):
    def test_generated_deals_run_auto_auction_and_retain_block_diagnostics(self):
        opening = Gadget.from_parts(
            {'id': 'test', 'author': {'name': 'Test'}},
            [{'id': 'opening', 'context': {'auction_pattern': ''},
              'call': '1N', 'meaning': {'action_type': 'opening'}}],
        )
        profile = PartnershipProfile('test', 'Test', '1', Author('Test'),
                                     (opening,), missing_call_behavior='block')
        north = HandConstraints((4, 3, 3, 3), (15, 17), (14.5, 19))
        south = HandConstraints((6, 3, 2, 2), (8, 11), (8, 15))
        sampler = ConstrainedDealSampler(north, south, seed=21)
        report = bid_constrained_deals(sampler, profile, 3)
        self.assertEqual(report['summary']['pairs'], 3)
        self.assertEqual(report['summary']['blocked'], 3)
        self.assertEqual(report['summary']['complete'], 0)
        self.assertEqual([case['id'] for case in report['cases']], [1, 2, 3])
        for case in report['cases']:
            self.assertEqual(case['calls'], ['1N', 'P'])
            self.assertEqual(case['blocked']['seat'], 's')
            self.assertEqual(case['history'][0]['source_id'], 'opening')
            deal_to_pbn(case['hands'])

    def test_many_deals_match_both_partners_shape_hcp_and_kr_ranges(self):
        north = HandConstraints((4, 3, 3, 3), (15, 17), (14.5, 19.0))
        south = HandConstraints((6, 3, 2, 2), (8, 11), (8.0, 15.0))
        deals = ConstrainedDealSampler(north, south, seed=73).sample(20)
        self.assertEqual(len(deals), 20)
        self.assertEqual(deals, ConstrainedDealSampler(north, south, seed=73).sample(20))
        for deal in deals:
            deal_to_pbn(deal)
            for seat, rule in (('n', north), ('s', south)):
                hand = deal[seat]
                self.assertEqual(tuple(hand.length(suit) for suit in 'SHDC'), rule.shape)
                self.assertGreaterEqual(hand.hcp, rule.hcp[0])
                self.assertLessEqual(hand.hcp, rule.hcp[1])
                self.assertGreaterEqual(hand_kr(hand), rule.kr[0])
                self.assertLessEqual(hand_kr(hand), rule.kr[1])

    def test_narrow_kr_interval_still_returns_exactly_eligible_hands(self):
        north = HandConstraints((4, 3, 3, 3), (16, 16), (16.0, 16.1))
        south = HandConstraints((4, 4, 3, 2), (9, 11), (9.0, 14.0))
        deals = ConstrainedDealSampler(north, south, seed=19).sample(3)
        self.assertEqual(len(deals), 3)
        self.assertTrue(all(16.0 <= hand_kr(deal['n']) <= 16.1 for deal in deals))

    def test_invalid_or_conflicting_constraints_fail_before_sampling(self):
        with self.assertRaisesRegex(ValueError, 'shape'):
            HandConstraints((4, 4, 4, 4), (10, 12), (9.0, 13.0))
        with self.assertRaisesRegex(ValueError, 'HCP'):
            HandConstraints((4, 3, 3, 3), (17, 15), (15.0, 18.0))
        with self.assertRaisesRegex(ValueError, 'K-R'):
            HandConstraints((4, 3, 3, 3), (15, 17), (18.0, 15.0))
        with self.assertRaisesRegex(ValueError, 'suit'):
            ConstrainedDealSampler(
                HandConstraints((8, 2, 2, 1), (15, 17), (10.0, 25.0)),
                HandConstraints((6, 3, 2, 2), (8, 10), (5.0, 15.0)),
            )
        with self.assertRaisesRegex(ValueError, '40'):
            ConstrainedDealSampler(
                HandConstraints((4, 3, 3, 3), (25, 30), (0.0, 40.0)),
                HandConstraints((4, 3, 3, 3), (20, 25), (0.0, 40.0)),
            )


if __name__ == '__main__':
    unittest.main()
