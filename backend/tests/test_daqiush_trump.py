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

    def test_diamond_agreement_persists_through_natural_four_hearts_and_keycard_ask(self):
        agreed = replay_auction(self.profile, Auction.parse('1NP2DP2HP3DP3S'))
        self.assertEqual(agreed.trump_state('ns').suit, 'D')
        natural = replay_auction(self.profile, Auction.parse('1NP2DP2HP3DP3SP4H'))
        self.assertEqual(natural.trump_state('ns').suit, 'D')
        ask = replay_auction(self.profile, Auction.parse('1NP2DP2HP3DP3SP4HP4N'))
        self.assertTrue(ask.state_exists({'key': 'keycard_context', 'trump_suit': 'D'}))
        self.assertEqual(ask.trump_state('ns').suit, 'D')


if __name__ == '__main__':
    unittest.main()
