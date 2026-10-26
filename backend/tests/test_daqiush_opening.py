import unittest
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory

import server
from engine.auction import Auction
from engine.cards import Hand
from engine.context import BridgeContext, StateView
from engine.explanation import explain
from engine.loader import load_profile
from engine.model import Author, PartnershipProfile
from engine.replay import replay_auction
from engine.selector import choose_bid
from engine.simulator import simulate_auction


EXAMPLES = [
    ('A', 'SA83HK72D94CAQJ87', True),
    ('B', 'SQ83HK72DJ4CAKJ87', False),
    ('C', 'SAQJ87HA72DK83C94', True),
    ('D', 'SKQ987HQ72DA83CK4', False),
    ('E', 'SAKQ87HK72DA4CJ83', False),
    ('F', 'SKJ987HAQ2DKQ4CQ8', True),
    ('G', 'SKQ987HQJDKQCQJ76', True),
    ('H', 'SAKJ87HA2D94CKJ76', False),
    ('I', 'SAJ76HKQ83DKJ76CQ', True),
    ('J', 'SAJ76HKQ83DQJ76CK', True),
    ('K', 'SKJ76HKQ83DQJ76CA', True),
    ('L', 'SKJ76HKQ3DQCAJ876', True),
    ('M', 'SAJ876HKQ3DKJ76CQ', True),
]


class DaqiushOpeningTests(unittest.TestCase):
    def profile(self):
        try:
            return load_profile('daqiush_2over1')
        except FileNotFoundError:
            self.fail('Executable Daqiush profile is missing')

    def context(self, cards):
        return BridgeContext('selection', Auction.parse(''), 'n', Hand.parse(cards), {}, StateView())

    def assessment(self, cards):
        evaluator = next(item for item in self.profile().all_evaluator_specs
                         if item.id == 'opening_assessment')
        return evaluator.definition(self.context(cards))

    def test_all_owner_examples_through_actual_selection(self):
        profile = self.profile()
        for label, cards, opens in EXAMPLES:
            with self.subTest(label=label):
                selection = choose_bid(profile, Auction.parse(''), Hand.parse(cards))
                self.assertEqual(selection.call, '1N' if opens else None)
                self.assertEqual(self.assessment(cards)['eligible'], opens)
                if not opens:
                    self.assertTrue(explain(selection)['diagnostics'])

    def test_shape_constraints_are_independent_of_points(self):
        hands = [
            ('SAKxxx HQxxx DKx CQx', 'two_majors'),
            ('SAKxxx HQxxx DKQx CJ', 'two_majors'),
            ('SAKxxxx HQxx DKx CQx', 'shape'),
            ('SAJxx HKQx DKJxxxx C-', 'shape'),
            ('SAJxx HKQx DKQxxx CJ', 'singleton'),
            ('SAJxx HKQx DKJxxx C2', 'singleton'),
            ('SAJxx HKQx DQ CQxxxx', 'upgrade_shape'),
        ]
        for cards, reason in hands:
            with self.subTest(cards=cards):
                report = self.assessment(cards)
                self.assertFalse(report['eligible'])
                self.assertIn(reason, report['reasons'])

    def test_supported_nonstandard_shapes_and_regular_balanced_hand(self):
        for cards in ['SAKx HQJx DKx CQxxxx', 'SAKx HQJ DKx CQxxxxx',
                      'SAKxx HQJxx DKx CQxx']:
            with self.subTest(cards=cards):
                self.assertTrue(self.assessment(cards)['eligible'])

    def test_approved_boundary_operators(self):
        # Isolate cutoffs from the K-R arithmetic, tested independently.
        evaluator = next(item for item in self.profile().all_evaluator_specs
                         if item.id == 'opening_assessment').definition
        class Context:
            pass
        cases = [
            (EXAMPLES[0][1], 'kr_points', [(14.95, False), (15, True)]),
            (EXAMPLES[4][1], 'kr_points', [(16.95, True), (17, False)]),
            (EXAMPLES[6][1], 'kr_delta', [(-1.5, True), (-1.45, False)]),
            (EXAMPLES[12][1], 'kr_delta', [(-.5, True), (-.45, False)]),
        ]
        for cards, key, boundaries in cases:
            for value, expected in boundaries:
                with self.subTest(cards=cards, value=value):
                    real = self.context(cards)
                    ctx = Context()
                    ctx.hand = real.hand
                    ctx.hand_quality = {**real.hand_quality, key: value}
                    self.assertEqual(evaluator(ctx)['eligible'], expected)

    def test_hcp_limits_and_seventeen_point_minor_do_not_use_global_kr_cap(self):
        for cards in ['SAxx HKxx Dxx CAQxxx', 'SAxx HKxx DKJ CAQJxx']:
            self.assertIn('hcp_range', self.assessment(cards)['reasons'])
        self.assertTrue(self.assessment('SKxx HAxx DJx CAKQxx')['eligible'])

    def test_very_soft_eighteen_point_4432_exception(self):
        examples = [
            ('SAQJ9HQJDQJ4CKQ74', True),       # A, K-R 15.50
            ('SKQ8HQJDKQ76CKQ72', True),       # H, K-R 15.60
            ('SAK7HQJDQ952CAQ54', False),     # I, K-R 16.15
            ('SK754HQJDAQ6CAQ42', False),     # J, K-R 16.50
            ('SAK96HQJDK72CKQ84', False),     # K, K-R 17.00
            ('SKJ7HQJDAQ972CKQ2', False),     # five-card suit excluded
        ]
        profile = self.profile()
        for cards, expected in examples:
            with self.subTest(cards=cards):
                self.assertEqual(self.assessment(cards)['eligible'], expected)
                self.assertEqual(choose_bid(profile, Auction.parse(''), Hand.parse(cards)).call,
                                 '1N' if expected else None)

    def test_opens_after_passes_and_with_every_dealer(self):
        profile = self.profile()
        hand = Hand.parse(EXAMPLES[0][1])
        for dealer in 'nesw':
            for passes in range(4):
                self.assertEqual(choose_bid(profile, Auction.parse(['P'] * passes, dealer=dealer), hand).call, '1N')

    def test_replay_announces_range_not_private_quality_or_balanced_shape(self):
        profile = self.profile()
        trace = replay_auction(profile, Auction.parse('1NP'), Hand.parse(EXAMPLES[0][1]))
        meaning = trace.applied_meanings[0]['public_meaning']
        self.assertEqual((meaning['hcp_min'], meaning['hcp_max']), (14, 18))
        self.assertNotEqual(meaning.get('shape_class'), 'balanced')
        self.assertNotIn('kr_points', meaning)
        self.assertTrue(trace.matching_state({'key': 'notrump_opening'}))

    def test_missing_continuations_and_competition_block(self):
        profile = self.profile()
        hand = Hand.parse(EXAMPLES[0][1])
        self.assertEqual(choose_bid(profile, Auction.parse('1NP'),
                                    Hand.parse('SK32HQ32DAJ3CKQJ8')).call, '3C')
        for auction, cards in [('1CP', hand), ('1N2D', hand)]:
            with self.subTest(auction=auction):
                report = explain(choose_bid(profile, Auction.parse(auction), cards))
                self.assertIsNone(report['call'])
                self.assertEqual(report['status'], 'blocked')
                self.assertTrue(any('No authored call' in line for line in report['diagnostics']))
        result = simulate_auction(profile, {'n': hand, 's': Hand.parse(EXAMPLES[6][1])})
        self.assertEqual(result.calls[:7], ('1N', 'P', '2H', 'P', '2S', 'P', '3C'))
        self.assertEqual(result.status, 'blocked')

    def test_profile_is_discoverable_and_uses_only_actor_cards(self):
        self.profile()
        self.assertIn('daqiush_2over1', [item['id'] for item in server._profile_summaries()])
        baseline = choose_bid(self.profile(), Auction.parse(''), Hand.parse(EXAMPLES[0][1]))
        injected = choose_bid(self.profile(), Auction.parse(''), Hand.parse(EXAMPLES[0][1]),
                              {'partner_hand': EXAMPLES[6][1]})
        self.assertEqual(explain(injected), explain(baseline))

    def test_absolute_maximum_requires_explicit_four_or_five_card_support(self):
        evaluators = {item.id: item.definition for item in self.profile().all_evaluator_specs}
        for cards, expected in [('SA76HKQ32DAK76C97', True),
                                 ('SA86HKJ872DAK3C73', True),
                                 ('SA76HKQ32DK876CQJ', False)]:
            ctx = self.context(cards)
            self.assertEqual(evaluators['absolute_maximum_H'](ctx), expected)
            self.assertIsNone(evaluators['absolute_maximum_S'](ctx))


class MissingCallBehaviorTests(unittest.TestCase):
    def test_default_fallback_is_unchanged_and_block_is_opt_in(self):
        profile = PartnershipProfile('empty', 'Empty', '1', Author('Test'), ())
        self.assertTrue(hasattr(profile, 'missing_call_behavior'), 'Missing profile coverage setting')
        hand = Hand.parse(EXAMPLES[0][1])
        self.assertEqual(choose_bid(profile, Auction.parse(''), hand).call, 'P')
        self.assertIsNone(choose_bid(replace(profile, missing_call_behavior='block'),
                                     Auction.parse(''), hand).call)

    def test_invalid_setting_is_rejected_on_load(self):
        with TemporaryDirectory() as root:
            path = Path(root) / 'partnership_profiles' / 'invalid'
            path.mkdir(parents=True)
            (path / 'profile.bsl.py').write_text(
                "Profile('invalid', gadgets=[], missing_call_behavior='blok')", encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'missing_call_behavior'):
                load_profile('invalid', Path(root))


if __name__ == '__main__':
    unittest.main()
