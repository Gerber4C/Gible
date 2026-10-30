import unittest

from engine.auction import Auction
from engine.loader import load_profile
from engine.replay import replay_auction


class DaqiushTrumpPrefixes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = load_profile('daqiush_2over1')

    def test_minor_stayman_club_fit_only_when_responder_shows_four_clubs(self):
        partial = replay_auction(self.profile, Auction.parse('1NP2CP2DP4CP4D'))
        self.assertEqual(partial.trump_state('ns').suit, 'C')
        self.assertEqual(partial.trump_state('ns').status, 'agreed')
        found = replay_auction(self.profile, Auction.parse('1NP2CP2DP4CP4DP4S'))
        self.assertEqual(found.trump_state('ns').suit, 'C')
        self.assertEqual(found.trump_state('ns').status, 'agreed')

    def test_minor_stayman_diamond_fit_after_four_hearts_and_four_spades(self):
        partial = replay_auction(self.profile, Auction.parse('1NP2CP2DP4CP4DP4H'))
        self.assertEqual(partial.trump_state('ns').suit, 'C')
        found = replay_auction(self.profile, Auction.parse('1NP2CP2DP4CP4DP4HP4S'))
        self.assertEqual(found.trump_state('ns').suit, 'D')

    def test_provisional_diamond_then_heart_flip_then_keycard_diamond(self):
        natural_second = replay_auction(
            self.profile, Auction.parse('1NP2DP2HP3DP'))
        self.assertEqual(natural_second.trump_state('ns').suit, 'H')
        self.assertEqual(natural_second.trump_state('ns').status, 'agreed')

        provisional = replay_auction(
            self.profile, Auction.parse('1NP2DP2HP3DP3S'))
        self.assertEqual(provisional.trump_state('ns').suit, 'D')
        self.assertEqual(provisional.trump_state('ns').status, 'provisional')

        flipped = replay_auction(
            self.profile, Auction.parse('1NP2DP2HP3DP3SP4H'))
        self.assertEqual(flipped.trump_state('ns').suit, 'H')
        self.assertEqual(flipped.trump_state('ns').status, 'provisional')

        accepted = replay_auction(
            self.profile, Auction.parse('1NP2DP2HP3DP3SP4HPP'))
        self.assertEqual(accepted.trump_state('ns').suit, 'H')
        self.assertEqual(accepted.trump_state('ns').status, 'agreed')

        ask = replay_auction(
            self.profile, Auction.parse('1NP2DP2HP3DP3SP4HP4N'))
        self.assertTrue(ask.state_exists({'key': 'keycard_context', 'trump_suit': 'D'}))
        self.assertEqual(ask.trump_state('ns').suit, 'D')
        self.assertEqual(ask.trump_state('ns').status, 'agreed')


if __name__ == '__main__':
    unittest.main()
