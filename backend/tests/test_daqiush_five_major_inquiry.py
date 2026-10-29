import unittest

from engine.cards import Hand
from engine.five_major_inquiry_policy import deterministic_after_singleton
from engine.hand_quality import minor_game_control_points


class DaqiushFiveMajorInquiryPolicyTests(unittest.TestCase):
    def decide(self, cards, singleton_major):
        return deterministic_after_singleton(
            Hand.parse(cards), singleton_major=singleton_major)

    def test_both_minor_route_sets_diamonds_for_either_singleton_major(self):
        examples = (
            ('SAJ4HA2DKQ76CQJ84', 'H'),
            ('SA2HAJ4DKQ76CQJ84', 'S'),
        )
        for cards, singleton_major in examples:
            with self.subTest(singleton_major=singleton_major):
                decision = self.decide(cards, singleton_major)
                self.assertEqual(decision.call, '4' + singleton_major)
                self.assertEqual(decision.agreed_suit, 'D')
                self.assertEqual(decision.source, 'deterministic')

    def test_five_four_minor_orientations_accept_exact_control_boundary(self):
        examples = (
            ('SAQH28D8AQ3KC2374', 'H', 5, 4),
            ('S6THAQDA5J83C643A', 'S', 5, 4),
            ('SAQH46DJK95CT87AJ', 'H', 4, 5),
            ('S84HQAD453JCKA9J2', 'S', 4, 5),
        )
        for cards, singleton_major, diamonds, clubs in examples:
            with self.subTest(singleton_major=singleton_major,
                              minors=(diamonds, clubs)):
                hand = Hand.parse(cards)
                self.assertEqual((hand.length('D'), hand.length('C')),
                                 (diamonds, clubs))
                self.assertFalse(any(rank in hand.holding(singleton_major)
                                     for rank in 'KQJ'))
                self.assertEqual(minor_game_control_points(
                    hand, 'D', partner_long_suits=('C',)), 14.5)
                decision = deterministic_after_singleton(
                    hand, singleton_major=singleton_major)
                self.assertEqual((decision.call, decision.agreed_suit),
                                 ('4' + singleton_major, 'D'))

    def test_five_four_minor_route_rejects_just_below_control_boundary(self):
        hand = Hand.parse('SQJH78DAKJ25CQJK7')
        self.assertEqual((hand.length('D'), hand.length('C')), (5, 4))
        self.assertFalse(any(rank in hand.holding('H') for rank in 'KQJ'))
        self.assertAlmostEqual(minor_game_control_points(
            hand, 'D', partner_long_suits=('C',)), 14.4)
        decision = deterministic_after_singleton(hand, singleton_major='H')
        self.assertIsNone(decision.call)
        self.assertEqual(decision.source, 'inconclusive')

    def test_both_minor_route_allows_ace_king_in_reported_major(self):
        decision = self.decide('S432HAKDKQ76CAJ84', 'H')
        self.assertEqual((decision.call, decision.agreed_suit), ('4H', 'D'))

    def test_both_minor_route_rejects_major_waste(self):
        decision = self.decide('S432HK2DAKQ7CAQJ8', 'H')
        self.assertIsNone(decision.call)
        self.assertEqual(decision.source, 'inconclusive')

    def test_both_minor_route_rejects_controls_below_fourteen_and_a_half(self):
        decision = self.decide('SAK4H32D8765C9842', 'H')
        self.assertIsNone(decision.call)
        self.assertEqual(decision.source, 'inconclusive')

    def test_two_four_card_minors_without_special_route_are_ambiguous(self):
        decision = self.decide('SAK4HJ2DQ876CJ842', 'H')
        self.assertIsNone(decision.call)
        self.assertEqual(decision.source, 'inconclusive')

    def test_unique_four_card_minor_is_selected_symmetrically(self):
        examples = (
            ('SAK4H732DAQ76C842', 'H', '4D', 'D'),
            ('S732HAK4D842CAQ76', 'S', '4C', 'C'),
        )
        for cards, singleton_major, call, agreed_suit in examples:
            with self.subTest(call=call):
                decision = self.decide(cards, singleton_major)
                self.assertEqual((decision.call, decision.agreed_suit),
                                 (call, agreed_suit))

    def test_unique_four_three_other_major_candidate_is_selected(self):
        examples = (
            ('SAK76HJ32D842C963', 'H', '4S', 'S'),
            ('SJ32HAK76D842C963', 'S', '4H', 'H'),
        )
        for cards, singleton_major, call, agreed_suit in examples:
            with self.subTest(call=call):
                decision = self.decide(cards, singleton_major)
                self.assertEqual((decision.call, decision.agreed_suit),
                                 (call, agreed_suit))

    def test_exact_three_three_minors_uses_artificial_four_notrump(self):
        decision = self.decide('S876HJ942DAK3CQ76', 'H')
        self.assertEqual(decision.call, '4NT')
        self.assertIsNone(decision.agreed_suit)
        self.assertFalse(decision.final)

    def test_stopper_without_structural_suit_candidate_selects_three_notrump(self):
        decision = self.decide('S876HAKQ32D842C96', 'H')
        self.assertEqual(decision.call, '3NT')
        self.assertTrue(decision.final)

    def test_bare_queen_is_not_an_inquiry_stopper_in_either_major(self):
        for cards, singleton_major in (
                ('S876HQ9865D84C963', 'H'),
                ('SQ9865H876D84C963', 'S')):
            with self.subTest(singleton_major=singleton_major):
                decision = self.decide(cards, singleton_major)
                self.assertIsNone(decision.call)
                self.assertEqual(decision.source, 'inconclusive')

    def test_bare_king_does_not_conflict_with_unique_minor_route(self):
        decision = self.decide('S98765HKD842CAQ76', 'H')
        self.assertEqual((decision.call, decision.agreed_suit), ('4C', 'C'))

    def test_stopper_and_structural_suit_candidate_requires_simulation(self):
        decision = self.decide('SAK4HA32DQ876C842', 'H')
        self.assertIsNone(decision.call)
        self.assertEqual(decision.source, 'inconclusive')

    def test_no_stopper_and_no_structural_route_never_guesses(self):
        decision = self.decide('S876HJ9842D84C963', 'H')
        self.assertIsNone(decision.call)
        self.assertEqual(decision.source, 'inconclusive')


if __name__ == '__main__':
    unittest.main()
