import unittest

from engine.auction import Auction
from engine.cards import Hand
from engine.context import BridgeContext, StateView
from engine.hand_quality import assess_quality


class HonorQualityTests(unittest.TestCase):
    def assess(self, cards):
        try:
            from engine.honor_quality import assess_honor_texture
        except ImportError:
            self.fail('Reusable honor texture evaluator is not implemented')
        return assess_honor_texture(Hand.parse(cards))

    def test_doubleton_qj_deducts_both_even_with_protection(self):
        result = self.assess('SAKxxx HKxx Dxxx CQJ')
        self.assertEqual(result['deduction'], 2.5)
        self.assertEqual(result['adjusted_hcp'], 10.5)
        self.assertEqual(result['suits']['C']['deduction'], 2.5)

    def test_longer_suits_protect_only_with_a_higher_honor(self):
        for holding, deduction in [('Qxx', .5), ('Jxx', .5), ('QJxx', .5),
                                   ('KJxx', 0), ('AKQJ', 0)]:
            with self.subTest(holding=holding):
                hand = Hand.from_dict({'spades': holding,
                                      'hearts': 'X' * (13-len(holding))})
                result = self.assess('S' + hand.spades + 'H' + hand.hearts + 'D-C-')
                self.assertEqual(result['deduction'], deduction)

    def test_singletons_have_no_invented_deduction(self):
        self.assertEqual(self.assess('SQ HKxxx DAxxx Cxxxx')['deduction'], 0)

    def test_both_confirmed_absolute_maximum_examples_preserve_points(self):
        for cards, points in [('SA76HKQ32DAK76C97', 16),
                              ('SA86HKJ872DAK3C73', 15)]:
            with self.subTest(cards=cards):
                hand = Hand.parse(cards)
                before = assess_quality(hand)
                result = self.assess(cards)
                self.assertEqual(result['hcp'], points)
                self.assertEqual(result['adjusted_hcp'], points)
                self.assertEqual(assess_quality(hand), before)
                self.assertEqual(hand.hcp, points)

    def test_hard_soft_evidence_is_reported_without_universal_classification(self):
        hard = self.assess('SAKJ87HA2D94CKJ76')
        soft = self.assess('SKQ987HQJDKQCQJ76')
        self.assertEqual(hard['ak_count'], 4)
        self.assertEqual(soft['ak_count'], 2)
        self.assertEqual(hard['qj_count'], 2)
        self.assertEqual(soft['qj_count'], 6)
        self.assertNotIn('hard', hard)
        self.assertEqual(hard['suits']['S']['honors'], 'AKJ')

    def test_context_exposes_only_actor_evidence_and_handles_replay_without_hand(self):
        hand = Hand.parse('SA83HK72D94CAQJ87')
        context = BridgeContext('selection', Auction.parse(''), 'n', hand,
                                {'partner_hand': 'SAKQJHT98D765C432'}, StateView())
        self.assertTrue(hasattr(context, 'hand_quality'), 'Missing BSL hand-quality access')
        self.assertEqual(context.hand_quality['kr_points'], 15.1)
        self.assertEqual(context.honor_texture['hcp'], 14)
        empty = BridgeContext('replay', Auction.parse(''), 'n', None, {}, StateView())
        self.assertIsNone(empty.hand_quality)
        self.assertIsNone(empty.honor_texture)


if __name__ == '__main__':
    unittest.main()
