import unittest

from engine.auction import Auction
from engine.cards import Hand
from engine.loader import load_profile
from engine.replay import replay_auction
from engine.selector import choose_bid


class DaqiushKeycardPrefixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = load_profile('daqiush_2over1')

    def test_texas_four_notrump_is_heart_keycard_ask_not_a_new_simulation_decision(self):
        prefix = Auction.parse('1NP4CP4HP4N')
        trace = replay_auction(self.profile, prefix)
        self.assertTrue(trace.state_exists({'key': 'keycard_context', 'trump_suit': 'H'}))
        self.assertEqual(trace.trump_state('ns').suit, 'H')
        self.assertEqual(choose_bid(self.profile, Auction.parse('1NP4CP4HP'),
                                    Hand.parse('SA765HQJ9876D43C2')).call, None)

    def test_four_ordinary_1430_answers_after_confirmed_texas_ask(self):
        prefix = Auction.parse('1NP4CP4HP4NP')
        cases = (
            ('SA765HQJ9876D43C2', '5C'),  # one keycard
            ('S9765HQJ9876D43C2', '5D'),  # zero
            ('SA765HKJ9876D43C2', '5H'),  # two, no trump queen
            ('SA765HKQ9876D43C2', '5S'), # two, with trump queen
        )
        for cards, call in cases:
            with self.subTest(call=call):
                self.assertEqual(choose_bid(self.profile, prefix, Hand.parse(cards)).call, call)

    def test_void_response_uses_the_useful_void_answer(self):
        hand = Hand.parse('SA765HKQ9876D432C-')
        decision = choose_bid(self.profile, Auction.parse('1NP4CP4HP4NP'), hand)
        self.assertEqual(decision.call, '5N')
        trace = replay_auction(self.profile, Auction.parse('1NP4CP4HP4NP5NP'))
        self.assertTrue(trace.state_exists({'key': 'keycard_context',
                                            'method': 'rkcb_1430',
                                            'status': 'answered',
                                            'trump_suit': 'H'}))

    def test_diamond_trump_and_splinter_trump_are_used_by_responses(self):
        diamond = choose_bid(self.profile, Auction.parse('1NP2DP2HP3DP3SP4HP4NP'),
                             Hand.parse('SA765HQJ9876D43C2'))
        # One ace and no diamond king: 5C despite the intervening natural 4H.
        self.assertEqual(diamond.call, '5C')
        splinter = choose_bid(self.profile, Auction.parse('1NP2DP2HP4CP4NP'),
                              Hand.parse('SA765HQJ9876D43C2'))
        self.assertEqual(splinter.call, '5C')

    def test_refused_no_shortage_try_can_be_reopened_and_answered(self):
        prefix = Auction.parse('1NP2CP2SP4DP4SP4NP')
        self.assertEqual(
            choose_bid(self.profile, prefix,
                       Hand.parse('SA765HQJ9876D43C2')).call,
            '5C')

    def test_undesignated_four_notrump_does_not_replay_as_keycard(self):
        trace = replay_auction(self.profile, Auction.parse('1NP4N'))
        self.assertFalse(trace.state_exists({'key': 'keycard_context'}))


if __name__ == '__main__':
    unittest.main()
