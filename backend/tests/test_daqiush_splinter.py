import unittest

from engine.auction import Auction
from engine.cards import Hand
from engine.loader import load_profile
from engine.replay import replay_auction
from engine.selector import choose_bid


class DaqiushSplinterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = load_profile('daqiush_2over1')

    def test_six_historical_single_jumps_immediately_agree_transferred_major(self):
        for transfer, accept, trump, splinters in (
            ('2D', '2H', 'H', ('3S', '4C', '4D')),
            ('2H', '2S', 'S', ('4C', '4D', '4H')),
        ):
            for bid in splinters:
                with self.subTest(transfer=transfer, splinter=bid):
                    auction = Auction.parse(('1N', 'P', transfer, 'P', accept, 'P', bid, 'P'))
                    trace = replay_auction(self.profile, auction)
                    self.assertTrue(trace.state_exists({'key': 'agreed_suit', 'suit': trump}))
                    meaning = [item for item in trace.applied_meanings if item['call'] == bid][-1]
                    self.assertEqual(meaning['public_meaning']['agreed_suit'], trump)
                    self.assertEqual(meaning['public_meaning']['short_suit'], bid[1])

    def test_retained_honor_values_adjust_raw_hcp(self):
        from engine.short_suit_valuation import splinter_adjusted_hcp

        for holding, retained in (
            ('A', 4), ('AJ', 4), ('AQ', 5), ('AQJ', 5), ('AK', 6),
            ('AKJ', 6), ('AKQ', 7), ('AKQJ', 7), ('K', 1), ('KJ', 1),
            ('KQ', 1.5), ('KQJ', 1.5), ('Q', 0), ('QJ', 0), ('J', 0),
            ('987', 0),
        ):
            with self.subTest(holding=holding):
                hand = Hand.from_dict({'clubs': holding})
                self.assertEqual(splinter_adjusted_hcp(hand, 'C'), retained)

    def test_opener_weak_mid_and_strong_responses_after_heart_splinter(self):
        auction = Auction.parse('1NP2DP2HP4CP')
        cases = (
            ('SAQ7HKJ8DA762CQ54', '4H'),
            ('SAQJHKQ8DA762C954', '4D'),
            ('SAKJHKQ8DA762C954', '4N'),
        )
        for cards, expected in cases:
            with self.subTest(cards=cards):
                decision = choose_bid(self.profile, auction, Hand.parse(cards))
                self.assertEqual(decision.call, expected)
                self.assertTrue(decision.trace.state_exists({'key': 'agreed_suit', 'suit': 'H'}))
                if expected == '4N':
                    self.assertEqual(decision.selected_candidate.public_meaning['target_suit'], 'H')

    def test_weak_reply_after_spade_splinter(self):
        decision = choose_bid(
            self.profile, Auction.parse('1NP2HP2SP4HP'), Hand.parse('SAQ7HKJ8DA762CQ54'))
        self.assertEqual(decision.call, '4S')
        self.assertTrue(decision.trace.state_exists({'key': 'agreed_suit', 'suit': 'S'}))

    def test_medium_reply_can_cue_above_game_and_strong_ask_keeps_spade_trump(self):
        auction = Auction.parse('1NP2HP2SP4HP')
        medium = choose_bid(self.profile, auction, Hand.parse('SAQJH987DA762CKQ4'))
        self.assertEqual(medium.call, '5C')
        strong = choose_bid(self.profile, auction, Hand.parse('SAKJH987DA762CKQ4'))
        self.assertEqual(strong.call, '4N')
        self.assertEqual(strong.selected_candidate.public_meaning['target_suit'], 'S')
        trace = replay_auction(self.profile, Auction.parse('1NP2HP2SP4HP4N'))
        self.assertTrue(trace.state_exists({'key': 'keycard_context', 'trump_suit': 'S'}))

    def test_shortage_with_a_second_minor_uses_natural_minor_route(self):
        hand = Hand.parse('SAQT976H2D53CKJ42')
        decision = choose_bid(self.profile, Auction.parse('1NP2HP2SP'), hand)
        self.assertEqual(decision.call, '3C')

    def test_no_shortage_jacoby_jump_to_four_major_is_slam_invitation(self):
        for transfer, accept, game, trump in (('2D', '2H', '4H', 'H'),
                                               ('2H', '2S', '4S', 'S')):
            with self.subTest(trump=trump):
                trace = replay_auction(self.profile,
                                       Auction.parse(('1N', 'P', transfer, 'P',
                                                      accept, 'P', game)))
                meaning = trace.applied_meanings[-1]['public_meaning']
                self.assertIn('slam_try', meaning['call_act_types'])
                self.assertEqual(trace.trump_state('ns').suit, trump)


if __name__ == '__main__':
    unittest.main()
