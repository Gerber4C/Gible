import unittest

from engine.auction import Auction
from engine.cards import Hand
from engine.loader import load_profile
from engine.selector import choose_bid


class QuantitativeInquiryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = load_profile('daqiush_2over1')

    def bid(self, auction, cards):
        return choose_bid(self.profile, Auction.parse(auction),
                          Hand.parse(cards)).call

    def test_good_16_17_three_club_family(self):
        for cards in ('SAT8HA6DKT63CAJ95',   # 3-2-4-4
                      'SAKT5HA52DA74CJ94',   # 4-3-3-3
                      'SATHQ54DA952CAK85',   # 2-3-4-4
                      'ST43HAT8DAT8CAKJ7'):  # 3-3-3-4
            with self.subTest(cards=cards):
                self.assertEqual(self.bid('1NP', cards), '3C')
        self.assertEqual(self.bid('1NP', 'S9852HAK9D54CAKQ2'), '2C')

    def test_three_club_after_denial_quantitative_and_fit_shows(self):
        four_three_two_four = 'SAT8HA6DKT63CAJ95'
        flat_spade_four = 'SAKT5HA52DA74CJ94'
        self.assertEqual(self.bid('1NP3CP3DP', four_three_two_four), '4N')
        self.assertEqual(self.bid('1NP3CP3HP', flat_spade_four), '3S')
        self.assertEqual(self.bid('1NP3CP3SP', flat_spade_four), '4H')
        self.assertEqual(self.bid('1NP3CP3HP', four_three_two_four), '4N')

    def test_stayman_4324_quantitative_after_2d_and_2h(self):
        cards = 'S9852HAK9D54CAKQ2'
        self.assertEqual(self.bid('1NP', cards), '2C')
        self.assertEqual(self.bid('1NP2CP2DP', cards), '4N')
        self.assertEqual(self.bid('1NP2CP2HP', cards), '4N')
        self.assertNotEqual(self.bid('1NP2CP2SP', cards), '4N')

    def test_five_clubs_is_limited_to_the_three_prefixes(self):
        opener = 'SKQ2HQJ2DKQJ32C32'
        self.assertEqual(self.bid('1NP2CP2DP4NP', opener), '5C')
        self.assertEqual(self.bid('1NP3CP3DP4NP', opener), '5C')
        self.assertNotEqual(self.bid('1NP2CP2SP4NP', opener), '5C')

    def test_ace_answers_use_ordinary_aces(self):
        for cards, answer in (
                ('SKQ2HQJ2DKQJ2CQJ2', '5H'),   # zero
                ('SAQ2HQJ2DKQJ2CQJ2', '5D'),   # one
                ('SAQ2HAJ2DKQJ2CQJ2', '5S'),   # two
                ('SAQ2HAJ2DAQJ2CQJ2', '5H'),   # three
                ('SAQ2HAJ2DAQJ2CAJ2', '5D')):  # four
            with self.subTest(answer=answer):
                self.assertEqual(
                    self.bid('1NP2CP2DP4NP5CP', cards), answer)

    def test_missing_two_aces_stops_in_five_notrump(self):
        opener = 'SKQ2HQJ2DKQJ32C32'  # zero aces
        self.assertEqual(
            self.bid('1NP2CP2DP4NP5CP5SP', opener), '5N')

    def test_known_spade_fit_stops_in_five_spades(self):
        from unittest.mock import patch
        opener = 'SKQ32HQJ2DKQJ2C32'  # zero aces, four spades
        self.assertEqual(
            self.bid('1NP2CP2HP4NP5CP5SP', opener), 'P')
        one_ace = {'s': Hand.parse('SA2HQJ2DKQJ2CQJ32')}
        with patch('engine.five_major_inquiry_policy.sample_process_hands',
                   return_value=(one_ace, one_ace)):
            self.assertEqual(
                self.bid('1NP2CP2HP4NP5CP5DP', opener), '5S')
        four_aces = {'s': Hand.parse('SAQ2HAJ2DAQJ2CAJ2')}
        with patch('engine.five_major_inquiry_policy.sample_process_hands',
                   return_value=(four_aces, four_aces)):
            self.assertEqual(
                self.bid('1NP2CP2HP4NP5CP5DP', opener), '6S')

    def test_not_missing_two_aces_describes_six_card_strain(self):
        opener = 'SAQ2HQJ2DKQJ32C32'  # one ace, five diamonds
        self.assertEqual(
            self.bid('1NP2CP2DP4NP5CP5SP', opener), '6D')
        opener_spades = 'SAQ32HQJ2DKQJ2C32'
        self.assertEqual(
            self.bid('1NP2CP2HP4NP5CP5SP', opener_spades), '6S')
        opener_hearts = 'SA2HQJ432DKQJ2C32'
        self.assertEqual(
            self.bid('1NP2CP2HP4NP5CP5SP', opener_hearts), '6H')
        opener_clubs = 'SAQ2HAQ2DK2CQJ432'
        self.assertEqual(
            self.bid('1NP2CP2DP4NP5CP5DP', opener_clubs), '6C')

    def test_five_clubs_does_not_promise_four_spades(self):
        opener = 'SKQ2HQJ2DKQJ32C32'
        decision = choose_bid(
            self.profile, Auction.parse('1NP2CP2DP4NP'),
            Hand.parse(opener))
        self.assertEqual(decision.call, '5C')
        meaning = decision.selected_candidate.public_meaning
        self.assertNotIn('S', meaning.get('min_lengths', {}))


if __name__ == '__main__':
    unittest.main()
