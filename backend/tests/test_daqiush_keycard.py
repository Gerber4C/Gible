import unittest

from engine.auction import Auction
from engine.cards import Hand
from engine.loader import load_profile
from engine.replay import replay_auction
from engine.rkcb_continuation import ordinary_rkcb_frame
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

    def test_queen_ask_after_five_clubs_keeps_the_public_answer(self):
        trace = replay_auction(
            self.profile, Auction.parse('1NP4CP4HP4NP5CP5DP'))
        frame = ordinary_rkcb_frame(trace)
        self.assertEqual((frame.status, frame.trump, frame.answer_category,
                          frame.keycard_counts, frame.continuation_stage),
                         ('answered', 'H', '1/4', (1, 4), 'queen_ask'))

    def test_five_spades_after_five_diamonds_is_the_queen_ask(self):
        trace = replay_auction(
            self.profile, Auction.parse('1NP4CP4HP4NP5DP5SP'))
        frame = ordinary_rkcb_frame(trace)
        self.assertEqual((frame.answer_category, frame.continuation_stage),
                         ('0/3', 'queen_ask'))
        entry = next(item for item in trace.applied_meanings
                     if item['index'] == 10)
        self.assertEqual(entry['public_meaning']['action_type'],
                         'rkcb_1430_queen_ask')

    def test_five_spade_relay_then_forced_five_notrump_completes(self):
        relay = replay_auction(
            self.profile, Auction.parse('1NP4CP4HP4NP5CP5SP'))
        self.assertEqual(ordinary_rkcb_frame(relay).status, 'relay_pending')
        completed = replay_auction(
            self.profile, Auction.parse('1NP4CP4HP4NP5CP5SP5NP'))
        frame = ordinary_rkcb_frame(completed)
        self.assertEqual((frame.status, frame.continuation_stage),
                         ('relay_completed', 'relay'))
        self.assertEqual(frame.keycard_counts, (1, 4))

    def test_relay_king_show_and_small_slam_close_the_frame(self):
        shown = replay_auction(
            self.profile, Auction.parse('1NP4CP4HP4NP5CP5SP5NP6CP'))
        frame = ordinary_rkcb_frame(shown)
        self.assertEqual((frame.status, frame.continuation_stage),
                         ('answered', 'relay'))
        finished = replay_auction(
            self.profile, Auction.parse('1NP4CP4HP4NP5CP5SP5NP6HP'))
        self.assertEqual(ordinary_rkcb_frame(finished).status, 'completed')


if __name__ == '__main__':
    unittest.main()
