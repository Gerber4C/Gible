import unittest

from engine.auction import Auction
from engine.cards import Hand
from engine.hand_quality import minor_game_control_points
from engine.loader import load_profile
from engine.selector import choose_bid
from engine.simulator import simulate_auction


class DaqiushMinorInvitationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = load_profile('daqiush_2over1')

    def bid(self, auction, cards):
        return choose_bid(self.profile, Auction.parse(auction), Hand.parse(cards)).call

    def test_side_suit_controls_use_reviewed_g033_values(self):
        examples = {
            'AKQJ': 9, 'AKQ': 8.4, 'AKJ': 7.3, 'AQJ': 5.8,
            'KQJ': 4.7, 'AK': 7, 'AQ': 5.5,
            'AJ2': 4.4, 'AJ': 4.1, 'KQ2': 4.4, 'KQ': 4.1,
            'KJ2': 3.1, 'KJ': 2.9, 'QJ2': 1.5, 'QJ': 0.4,
            'A': 4, 'K2': 2.6, 'K': 1.5,
            'Q32': 1.3, 'Q2': 1, 'Q': 0.3,
            'J32': 0.5, 'J2': 0.2, 'J': 0.1,
        }
        for holding, points in examples.items():
            with self.subTest(holding=holding):
                hand = Hand.from_dict({'spades': holding})
                self.assertEqual(minor_game_control_points(hand, 'C'), points)
        self.assertEqual(minor_game_control_points(Hand.from_dict({'clubs': 'AQJ'}), 'C'), 7)

    def test_reviewed_control_table_can_reject_a_raw_sixteen_count(self):
        cards = 'SAQ963HT86DAQJCK2'
        self.assertEqual(minor_game_control_points(Hand.parse(cards), 'C'), 14.3)
        self.assertEqual(self.bid('1NP2SP2NP4CP', cards), 'P')

    def test_known_second_long_suit_keeps_raw_hcp_even_when_not_trump(self):
        hand = Hand.parse('SKQJ4HA76DKQJ3C84')
        clubs_only = minor_game_control_points(hand, 'C')
        both_minors = minor_game_control_points(hand, 'C', partner_long_suits=('D',))
        self.assertAlmostEqual(both_minors - clubs_only, 6.0 - 4.7)
        self.assertEqual(minor_game_control_points(hand, 'D', partner_long_suits=('C',)),
                         minor_game_control_points(hand, 'D'))

    def test_featureless_invitation_ignores_four_card_minor(self):
        responder = 'SK432H86D982CAJ75'
        self.assertEqual(self.bid('1NP', responder), '2C')
        self.assertEqual(self.bid('1NP2CP', 'SAQ7HKJ8DA762CQ54'), '2D')
        self.assertEqual(self.bid('1NP2CP2DP', responder), '2N')
        self.assertEqual(self.bid('1NP2CP2DP2NP', 'SAQ7HKJ8DA762CJ54'), 'P')
        self.assertEqual(self.bid('1NP2CP2DP2NP', 'SAQ7HKJ8DA762CQ54'), '3N')
        self.assertEqual(self.bid('1NP2CP2DP2NP3NP', responder), 'P')

    def test_very_poor_eight_stops_and_very_good_nine_bids_game(self):
        self.assertEqual(self.bid('1NP', 'SQJH432DQJ4CQT987'), 'P')
        self.assertEqual(self.bid('1NP', 'S83THTK9D652CT7QA'), '3N')

    def test_reviewed_eight_point_4333_stops_but_other_eights_invite(self):
        self.assertEqual(self.bid('1NP', 'SA432HQ83DQ76C987'), 'P')
        cards = 'SAQ82HQ832DT98C86'
        self.assertEqual(self.bid('1NP', cards), '2C')
        self.assertEqual(self.bid('1NP2CP2DP', cards), '2N')
        self.assertEqual(self.bid('1NP2CP2HP', cards), '3H')
        self.assertEqual(self.bid('1NP2CP2SP', cards), '3S')

    def test_good_six_card_minor_invites_three_notrump_by_transfer(self):
        self.assertEqual(self.bid('1NP', 'S874H63D82CAKJ754'), '2S')
        self.assertEqual(self.bid('1NP', 'SJ74H63DAQJ754C82'), '2N')

    def test_weak_minor_transfer_stops_in_three_minor(self):
        self.assertEqual(self.bid('1NP', 'S874H63D82CKJ9754'), '2S')
        self.assertEqual(self.bid('1NP2SP', 'SAQ7HKJ8DA762CQ54'), '2N')
        self.assertEqual(self.bid('1NP2SP2NP', 'S874H63D82CKJ9754'), '3C')
        self.assertEqual(self.bid('1NP2SP2NP3CP', 'SAQ7HKJ8DA762CQ54'), 'P')

    def test_good_minor_invite_accepts_superaccept_at_three_notrump(self):
        self.assertEqual(self.bid('1NP2SP2NP', 'S874H63D82CAKJ754'), '3N')
        self.assertEqual(self.bid('1NP2NP', 'SAQ7HKJ8DA762CQ54'), '3C')
        self.assertEqual(self.bid('1NP2NP3CP', 'SJ74H63DAQJ754C82'), '3N')

    def test_six_clubs_with_ca_kq_and_a_spade_uses_direct_three_clubs(self):
        self.assertEqual(self.bid('1NP', 'SAK2HQ3D42CAKQ987'), '3C')

    def test_seven_clubs_with_eight_effective_points_places_five_clubs(self):
        self.assertEqual(self.bid('1NP', 'SAHQ3D42JCAKQ9876'), '5C')

    def test_good_minor_private_plan_survives_normalized_notrump_calls(self):
        result = simulate_auction(self.profile, {
            'n': 'SKQ59HTAD9TJAC98Q',
            's': 'S874H63D82CAKJ754',
        })
        self.assertEqual(result.status, 'complete')
        self.assertEqual(result.calls, ('1N', 'P', '2S', 'P', '2N', 'P', '3N', 'P', 'P', 'P'))

    def test_shapely_seven_card_minor_invites_five_minor(self):
        self.assertEqual(self.bid('1NP', 'S84H632D8CKQJ9754'), '2S')
        self.assertEqual(self.bid('1NP2SP3CP', 'S84H632D8CKQJ9754'), '4C')
        self.assertEqual(self.bid('1NP2SP3CP', 'SQ6H5DK93C4T6Q873'), 'P')

    def test_shapely_invitation_acceptance_uses_controls_not_raw_hcp(self):
        self.assertEqual(self.bid('1NP2SP3CP4CP', 'SAK7HK82DA762CQ54'), '5C')
        self.assertEqual(self.bid('1NP2SP3CP4CP', 'SKQJHKQJDA987C654'), 'P')

    def test_shapely_invitation_can_finish_five_clubs(self):
        result = simulate_auction(self.profile, {
            'n': 'SAK7HAK5DQ432CT86',
            's': 'S84H632D8CKQJ9754',
        })
        self.assertEqual(result.status, 'complete')
        self.assertEqual(result.calls,
                         ('1N', 'P', '2S', 'P', '3C', 'P', '4C', 'P', '5C', 'P', 'P', 'P'))


if __name__ == '__main__':
    unittest.main()
