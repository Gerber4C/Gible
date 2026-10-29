import unittest
from types import SimpleNamespace
from unittest.mock import patch

from engine.auction import Auction
from engine.cards import Hand
from engine.five_major_inquiry_policy import deterministic_after_singleton
from engine.hand_quality import minor_game_control_points
from engine.loader import load_profile
from engine.replay import replay_auction
from engine.selector import choose_bid


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

    def test_five_four_minor_orientations_reject_just_below_control_boundary(self):
        examples = (
            ('SQJH78DAKJ25CQJK7', 'H', 5, 4),
            ('SA8HJQD83TAQC75KJ', 'S', 5, 4),
            ('SQJH82DQ9A6C5KJA9', 'H', 4, 5),
            ('SA6HJQD7K58CJ36QA', 'S', 4, 5),
        )
        for cards, singleton_major, diamonds, clubs in examples:
            with self.subTest(singleton_major=singleton_major,
                              minors=(diamonds, clubs)):
                hand = Hand.parse(cards)
                self.assertEqual((hand.length('D'), hand.length('C')),
                                 (diamonds, clubs))
                self.assertFalse(any(rank in hand.holding(singleton_major)
                                     for rank in 'KQJ'))
                self.assertAlmostEqual(minor_game_control_points(
                    hand, 'D', partner_long_suits=('C',)), 14.4)
                decision = deterministic_after_singleton(
                    hand, singleton_major=singleton_major)
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


class DaqiushFiveMajorInquiryEndToEndTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = load_profile('daqiush_2over1')

    def decision(self, auction, cards):
        return choose_bid(
            self.profile, Auction.parse(auction), Hand.parse(cards))

    def bid(self, auction, cards):
        return self.decision(auction, cards).call

    def meaning(self, auction, call):
        trace = replay_auction(self.profile, Auction.parse(auction))
        matches = [item['public_meaning'] for item in trace.applied_meanings
                   if item['call'] == call]
        self.assertTrue(matches, (auction, call, trace.diagnostics))
        return matches[-1]

    def assert_agreed(self, auction, suit):
        state = replay_auction(
            self.profile, Auction.parse(auction)).trump_state('ns')
        self.assertEqual((state.status, state.suit), ('agreed', suit))

    def assert_final(self, auction, call):
        meaning = self.meaning(auction, call)
        self.assertIn('final_placement', meaning['call_act_types'])
        self.assertTrue(meaning['purpose_completed'])

    def test_singleton_reports_remain_symmetric(self):
        for shortage, cards in (
                ('H', 'SKQ3H9DA9754CKQ76'),
                ('S', 'S9HKQ3DA9754CKQ76')):
            with self.subTest(shortage=shortage):
                self.assertEqual(self.bid('1NP3CP3DP', cards), '3' + shortage)
                meaning = self.meaning('1NP3CP3DP3' + shortage, '3' + shortage)
                self.assertEqual(meaning['short_suit'], shortage)

    def test_singleton_stopper_only_signs_off_but_overlap_remains_td(self):
        for shortage, no_route, overlap in (
                ('H', 'S876HAKQ32D842C96', 'SAK4HA32DQ876C842'),
                ('S', 'SAKQ32H876D842C96', 'SA32HAK4DQ876C842')):
            prefix = '1NP3CP3DP3' + shortage + 'P'
            with self.subTest(shortage=shortage, route='notrump'):
                self.assertEqual(self.bid(prefix, no_route), '3N')
                self.assert_final(prefix + '3N', '3N')
            with self.subTest(shortage=shortage, route='overlap'):
                self.assertIsNone(self.bid(prefix, overlap))

    def test_singleton_structural_routes_and_trump_effects_are_symmetric(self):
        cases = (
            ('H', 'SAJ4HA2DKQ76CQJ84', '4H', 'D'),
            ('S', 'SA2HAJ4DKQ76CQJ84', '4S', 'D'),
            ('H', 'S732H92D842CAKQJ7', '4C', 'C'),
            ('S', 'S92H732DAKQJ7C842', '4D', 'D'),
        )
        for shortage, cards, call, trump in cases:
            prefix = '1NP3CP3DP3' + shortage + 'P'
            with self.subTest(shortage=shortage, call=call):
                self.assertEqual(self.bid(prefix, cards), call)
                self.assert_agreed(prefix + call, trump)

    def test_other_major_route_can_stop_or_name_lowest_five_card_minor(self):
        cases = (
            ('H', 'SAK76HJ32D842C963', '4S',
             'SQJ3H2DAJ954CK876', 'SKQ3H9DKQ76CA9754', '5C'),
            ('S', 'SJ32HAK76D842C963', '4H',
             'S2HQJ3DAJ954CK876', 'S9HKQ3DA9754CKQ76', '5D'),
        )
        for shortage, opener, game, weak, strong, minor_call in cases:
            opener_prefix = '1NP3CP3DP3' + shortage + 'P'
            responder_prefix = opener_prefix + game + 'P'
            with self.subTest(shortage=shortage, strength='weak'):
                decision = self.decision(responder_prefix, weak)
                self.assertEqual(decision.call, 'P')
                self.assert_agreed(opener_prefix + game, game[1])
                meaning = decision.selected_candidate.public_meaning
                self.assertIn('final_placement', meaning['call_act_types'])
                self.assertTrue(meaning['purpose_completed'])
            with self.subTest(shortage=shortage, strength='strong'):
                self.assertEqual(self.bid(responder_prefix, strong), minor_call)
                meaning = self.meaning(responder_prefix + minor_call, minor_call)
                self.assertNotIn('final_placement', meaning['call_act_types'])

    def test_exact_three_three_minor_route_falls_back_to_five_card_minor(self):
        cases = (
            ('H', 'S876HJ942DAK3CQ76', 'SKQ3H9DKQ76CA9754', '5C'),
            ('S', 'SJ942H876DAK3CQ76', 'S9HKQ3DA9754CKQ76', '5D'),
        )
        for shortage, opener, responder, expected in cases:
            opener_prefix = '1NP3CP3DP3' + shortage + 'P'
            responder_prefix = opener_prefix + '4N' + 'P'
            with self.subTest(shortage=shortage):
                self.assertEqual(self.bid(opener_prefix, opener), '4N')
                self.assertEqual(self.bid(responder_prefix, responder), expected)
                self.assert_agreed(responder_prefix + expected, expected[1])
                self.assert_final(responder_prefix + expected, expected)

    def test_five_card_major_fit_and_singleton_routes_are_symmetric(self):
        cases = (
            ('H', 'S2HQJ3DAJ954CK876', 'S9HKQ3DA9754CKQ76', '3S',
             'SQJ3H2DK876CAJ954', 'SKQ3H9DKQ76CA9754', '4C'),
            ('S', 'SQJ3H2DAJ954CK876', 'SKQ3H9DA9754CKQ76', '4H',
             'S2HQJ3DK876CAJ954', 'S9HKQ3DKQ76CA9754', '4C'),
        )
        for major, weak_fit, strong_fit, strength_call, weak_singleton, strong_singleton, minor_call in cases:
            prefix = '1NP3CP3' + major + 'P'
            with self.subTest(major=major, shape='fit', strength='weak'):
                self.assertEqual(self.bid(prefix, weak_fit), '4' + major)
                self.assert_agreed(prefix + '4' + major, major)
                self.assert_final(prefix + '4' + major, '4' + major)
            with self.subTest(major=major, shape='fit', strength='strong'):
                self.assertEqual(self.bid(prefix, strong_fit), strength_call)
                self.assert_agreed(prefix + strength_call, major)
                meaning = self.meaning(prefix + strength_call, strength_call)
                self.assertNotIn('final_placement', meaning['call_act_types'])
            with self.subTest(major=major, shape='singleton', strength='weak'):
                self.assertEqual(self.bid(prefix, weak_singleton), '3N')
                self.assert_final(prefix + '3N', '3N')
            with self.subTest(major=major, shape='singleton', strength='strong'):
                self.assertEqual(self.bid(prefix, strong_singleton), minor_call)
                meaning = self.meaning(prefix + minor_call, minor_call)
                self.assertNotIn('final_placement', meaning['call_act_types'])

    def test_responder_minor_calls_publish_exact_five_four_shapes(self):
        for major in 'HS':
            prefix = '1NP3CP3' + major + 'P'
            for call, five, four in (('4C', 'C', 'D'), ('4D', 'D', 'C')):
                with self.subTest(major=major, call=call):
                    meaning = self.meaning(prefix + call, call)
                    self.assertEqual(meaning['five_card_suit'], five)
                    self.assertEqual(meaning['four_card_suit'], four)
                    self.assertEqual((meaning.get('min_lengths') or {}).get(five), 5)
                    self.assertEqual((meaning.get('max_lengths') or {}).get(five), 5)
                    self.assertEqual((meaning.get('min_lengths') or {}).get(four), 4)
                    self.assertEqual((meaning.get('max_lengths') or {}).get(four), 4)

    def test_minor_shape_opener_selectors_set_trump_without_showing_control(self):
        continuations = (
            ('4C', '4D', 'D', False),
            ('4C', '4H', 'C', False),
            ('4C', '4S', 'C', False),
            ('4C', '5C', 'C', True),
            ('4D', '4H', 'C', False),
            ('4D', '4S', 'D', False),
        )
        for major in 'HS':
            base = '1NP3CP3' + major + 'P'
            for shown, call, trump, final in continuations:
                auction = base + shown + 'P' + call
                with self.subTest(major=major, shown=shown, call=call):
                    self.assert_agreed(auction, trump)
                    meaning = self.meaning(auction, call)
                    self.assertNotIn('control_showing', meaning['call_act_types'])
                    if final:
                        self.assertIn('final_placement', meaning['call_act_types'])
                        self.assertTrue(meaning['purpose_completed'])


class DaqiushFiveMajorInquirySelectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = load_profile('daqiush_2over1')

    def decision(self, auction, cards, estimates=None):
        if estimates is None:
            return choose_bid(self.profile, Auction.parse(auction),
                              Hand.parse(cards))
        with patch('engine.five_major_inquiry_policy._sampled_best',
                   return_value=tuple(
                       SimpleNamespace(contract=contract,
                                       completion_rate=rate)
                       for contract, rate in estimates)):
            return choose_bid(self.profile, Auction.parse(auction),
                              Hand.parse(cards))

    def test_deterministic_source_when_dds_is_unavailable(self):
        decision = self.decision('1NP3CP3DP3HP', 'S876HAKQ32D842C96')
        self.assertEqual(decision.call, '3N')
        self.assertEqual(decision.trace.simulation_decision['source'],
                         'deterministic')

    def test_dds_can_choose_an_authored_other_major_route(self):
        decision = self.decision(
            '1NP3CP3DP3HP', 'SAK76HJ32D842C963',
            estimates=(('3NT', 0.0), ('5C', 0.0), ('5D', 0.0),
                       ('4S', 1.0)))
        self.assertEqual(decision.call, '4S')
        self.assertEqual(decision.trace.simulation_decision['source'], 'dds')

    def test_unauthored_dds_result_falls_back_to_deterministic(self):
        decision = self.decision(
            '1NP3CP3DP3HP', 'SAK76HJ32D842C963',
            estimates=(('5H', 1.0),))
        self.assertEqual(decision.call, '4S')
        self.assertEqual(decision.trace.simulation_decision['source'],
                         'deterministic')

    def test_inconclusive_overlap_returns_td(self):
        decision = self.decision('1NP3CP3DP3HP', 'SAK4HA32DQ876C842')
        self.assertIsNone(decision.call)
        self.assertEqual(decision.trace.simulation_decision['source'],
                         'inconclusive')

    def test_responder_slam_classification_uses_dds_then_fallback(self):
        strong_fit = 'S9HKQ3DA9754CKQ76'
        weak_fit = 'S2HQJ3DAJ954CK876'
        decision = self.decision(
            '1NP3CP3HP', strong_fit,
            estimates=(('4H', 0.0), ('6H', 1.0)))
        self.assertEqual(decision.call, '3S')
        self.assertEqual(decision.trace.simulation_decision['source'], 'dds')
        fallback = self.decision('1NP3CP3HP', weak_fit)
        self.assertEqual(fallback.call, '4H')
        self.assertEqual(fallback.trace.simulation_decision['source'],
                         'deterministic')


if __name__ == '__main__':
    unittest.main()
