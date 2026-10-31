import unittest

from engine.auction import Auction
from engine.cards import Hand
from engine.loader import load_profile
from engine.selector import choose_bid


class KeycardStopTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = load_profile('daqiush_2over1')

    def bid(self, auction, cards):
        return choose_bid(
            self.profile, Auction.parse(auction), Hand.parse(cards))

    def test_five_heart_answer_stops_with_two_missing_keycards(self):
        decision = self.bid(
            '1NP4CP4HP4NP5HP', 'SKQHA98765DKQJCQJ')
        self.assertEqual(decision.call, 'P')
        self.assertEqual(
            decision.selected_candidate.public_meaning['action_type'],
            'keycard_five_of_trump_signoff')
        self.assertEqual(
            decision.selected_candidate.public_meaning['target_suit'], 'H')

    def test_five_heart_answer_stops_with_one_keycard_and_no_queen(self):
        decision = self.bid(
            '1NP4CP4HP4NP5HP', 'SA2HK98765DQJCQJ2')
        self.assertEqual(decision.call, 'P')
        self.assertEqual(
            decision.selected_candidate.public_meaning['action_type'],
            'keycard_five_of_trump_signoff')

    def test_five_heart_answer_continues_with_all_keycards(self):
        decision = self.bid(
            '1NP4CP4HP4NP5HP', 'SAHAK98765DQJCQJ2')
        self.assertEqual(decision.call, '6H')
        self.assertEqual(
            decision.selected_candidate.public_meaning['action_type'],
            'keycard_small_slam_placement')

    def test_five_diamond_answer_stops_at_five_hearts_not_pass(self):
        decision = self.bid(
            '1NP4CP4HP4NP5DP', 'SAHAK98765DQJCQJ2')
        self.assertEqual(decision.call, '5H')
        self.assertEqual(
            decision.selected_candidate.public_meaning['action_type'],
            'keycard_five_of_trump_signoff')

    def test_voidwood_five_diamond_answer_never_passes_out_diamond(self):
        strong = self.bid(
            '1NP2DP2HP4SP5DP', 'S-HAKQ7532DKQ53CAK')
        self.assertEqual(strong.call, '6H')
        self.assertEqual(
            strong.selected_candidate.public_meaning['action_type'],
            'keycard_small_slam_placement')

        weak = self.bid(
            '1NP2DP2HP4SP5DP', 'S-HAQJ7532DKQ53CQJ')
        self.assertEqual(weak.call, '5H')
        self.assertEqual(
            weak.selected_candidate.public_meaning['action_type'],
            'keycard_five_of_trump_signoff')


if __name__ == '__main__':
    unittest.main()
