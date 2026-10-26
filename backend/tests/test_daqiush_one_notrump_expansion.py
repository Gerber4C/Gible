import unittest

from engine.auction import Auction
from engine.cards import Hand
from engine.loader import load_profile
from engine.selector import choose_bid
from engine.simulator import simulate_auction


class DaqiushOneNotrumpExpansionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = load_profile('daqiush_2over1')

    def bid(self, auction, cards):
        return choose_bid(self.profile, Auction.parse(auction), Hand.parse(cards)).call

    def test_featureless_game_placement(self):
        responder = 'SQ3HA6DKJ92C98754'
        self.assertEqual(self.bid('1NP', responder), '3N')
        self.assertEqual(self.bid('1NP3NP', 'SAJ65H96DAQ3CKQJ3'), 'P')

    def test_five_card_major_inquiry_keeps_4333_in_notrump_without_four_card_support(self):
        responder = 'SQ32HA64DKJ92C987'
        self.assertEqual(self.bid('1NP', responder), '3C')
        self.assertEqual(self.bid('1NP3CP', 'SAQ4HKJ872DA63CQ7'), '3H')
        self.assertEqual(self.bid('1NP3CP3HP', responder), '3N')
        self.assertEqual(self.bid('1NP3CP', 'SAJ65H96DAQ3CKQJ3'), '3D')
        self.assertEqual(self.bid('1NP3CP3DP', responder), '3N')

    def test_five_card_major_inquiry_shows_singleton_after_denial(self):
        responder = 'SKQ3H9DA9754CKQ76'
        self.assertEqual(self.bid('1NP', responder), '3C')
        self.assertEqual(self.bid('1NP3CP3DP', responder), '3H')
        self.assertEqual(self.bid('1NP3CP3DP3HP', 'SAJ65HK96DQ73CKQ8'), '3N')

    def test_heart_stayman_invitation(self):
        responder = 'S932HKQ72DA43C862'
        self.assertEqual(self.bid('1NP', responder), '2C')
        self.assertEqual(self.bid('1NP2CP2HP', responder), '3H')
        self.assertEqual(self.bid('1NP2CP2HP3HP', 'SAJ65HK762DQ73CKQ'), 'P')
        self.assertEqual(self.bid('1NP2CP2HP3HP', 'SAJ65HK762DAQ3CK3'), '4H')

    def test_seven_minor_four_major_eight_effective_points_checks_fit_then_minor_game(self):
        for responder, minor in (
            ('SA872H3D4CKJ97654', 'C'),
            ('SA872H3DKJ97654C4', 'D'),
            ('SA872H3D4CK976543', 'C'),
        ):
            with self.subTest(minor=minor):
                self.assertEqual(self.bid('1NP', responder), '2C')
                self.assertEqual(self.bid('1NP2CP2DP', responder), '5' + minor)
                self.assertEqual(self.bid('1NP2CP2HP', responder), '5' + minor)
                self.assertEqual(self.bid('1NP2CP2SP', responder), '4S')

    def test_exact_five_five_minors_find_three_notrump_with_stoppers(self):
        responder = 'ST2H9DAK543CQJ876'
        self.assertEqual(self.bid('1NP', responder), '3D')
        self.assertEqual(self.bid('1NP3DP', 'SAQ5HK96DQ73CKJ82'), '3N')
        self.assertEqual(self.bid('1NP3DP3NP', responder), 'P')

    def test_minor_two_suiter_uses_partner_stopper_after_three_hearts(self):
        responder = 'SQTH9DAK543CQJ876'
        self.assertEqual(self.bid('1NP', responder), '3D')
        self.assertEqual(self.bid('1NP3DP', 'S865HAK9DAQ3CQJ82'), '3H')
        self.assertEqual(self.bid('1NP3DP3HP', responder), '3N')

    def test_five_five_minor_shortage_invitation_uses_control_quality(self):
        responder = 'SK2H9DQJ543CQ8765'
        self.assertEqual(self.bid('1NP', responder), '3H')
        self.assertEqual(self.bid('1NP3HP', 'SAK5HA96DQ73CKJ82'), '3N')
        self.assertEqual(self.bid('1NP3HP', 'SQJ5HQ96DKQ3CKJ82'), '4C')
        self.assertEqual(self.bid('1NP3HP4CP', responder), 'P')

    def test_five_five_minor_invitation_keeps_both_known_suits_at_raw_hcp(self):
        # The responder's 3H describes five cards in each minor. The opener's
        # diamond honors stay at raw HCP even when clubs is the chosen trump.
        opener = 'SA432HKDKQJ5CQJ43'
        self.assertEqual(self.bid('1NP3HP', opener), '5C')

    def test_exceptionally_good_nine_with_five_five_minors_forces_game(self):
        self.assertEqual(self.bid('1NP', 'SK2H9DKJ543CQ8765'), '3D')

    def test_weak_five_or_six_heart_transfer_can_stop(self):
        for responder in ('S632HKJ763D842C76', 'S82HKJ7632D842C76'):
            with self.subTest(responder=responder):
                self.assertEqual(self.bid('1NP', responder), '2D')
                self.assertEqual(self.bid('1NP2DP2HP', responder), 'P')

    def test_five_heart_transfer_invites_or_places_game(self):
        invite = 'SQ32HKJ763DQ42C76'
        game = 'SA32HKQJ76D432C76'
        self.assertEqual(self.bid('1NP2DP2HP', invite), '2N')
        self.assertEqual(self.bid('1NP2DP2HP2NP', 'SAQ7HKJ8DA762CQ54'), '4H')
        self.assertEqual(self.bid('1NP2DP2HP2NP', 'SAJ65HK762DQ73CKQ'), '3H')
        self.assertEqual(self.bid('1NP2DP2HP', game), '3N')
        self.assertEqual(self.bid('1NP2DP2HP3NP', 'SAQ7HKJ8DA762CQ54'), '4H')

    def test_five_card_major_superaccept_retransfer_and_game(self):
        weak_hearts = 'S632HKJ763D842C76'
        self.assertEqual(self.bid('1NP2DP2SP', weak_hearts), '3D')
        self.assertEqual(self.bid('1NP2DP2SP3DP', 'S97HKQ32DAK76CA76'), '3H')
        self.assertEqual(self.bid('1NP2DP2SP3DP3HP', weak_hearts), 'P')
        self.assertEqual(self.bid('1NP2DP2SP', 'SA32HKQJ76D432C76'), '4H')

        weak_spades = 'SKJ763H632D842C76'
        self.assertEqual(self.bid('1NP2HP2NP', weak_spades), '3H')
        self.assertEqual(self.bid('1NP2HP2NP3HP', 'SKQ32H97DAK76CA76'), '3S')
        self.assertEqual(self.bid('1NP2HP2NP3HP3SP', weak_spades), 'P')

    def test_stayman_then_natural_minor_slam_probe(self):
        responder = 'SA3HK2DAKJ76CQJ84'
        self.assertEqual(self.bid('1NP', responder), '2C')
        self.assertEqual(self.bid('1NP2CP2DP', responder), '3D')
        self.assertEqual(self.bid('1NP2CP2DP3DP', 'SAJ6HK83DQ92CAK72'), '3H')
        self.assertEqual(self.bid('1NP2CP2DP3DP', 'SAJ6HK83D92CAKQ72'), '3N')

    def test_jacoby_then_second_minor_is_natural_game_force(self):
        responder = 'S82HAQJ76D83CKQ74'
        self.assertEqual(self.bid('1NP', responder), '2D')
        self.assertEqual(self.bid('1NP2DP2HP', responder), '3C')
        self.assertEqual(self.bid('1NP2DP2HP3CP', 'SAK5HK8DA72CA9765'), '3D')
        self.assertEqual(self.bid('1NP2DP2HP3CP', 'SAK5HK8DQ72CA9765'), '3H')
        self.assertEqual(self.bid('1NP2DP2HP3CP', 'SAK54HK832DQ72CA9'), '3N')

    def test_four_minor_stayman_after_major_denial(self):
        responder = 'SA32HK8DAQJ7CKJ87'
        self.assertEqual(self.bid('1NP', responder), '2C')
        self.assertEqual(self.bid('1NP2CP2DP', responder), '4C')
        self.assertEqual(self.bid('1NP2CP2DP4CP', 'SAJ6HK83DQ97CAK72'), '4D')
        self.assertEqual(self.bid('1NP2CP2DP4CP', 'SAJ6HK83DAQ97CK72'), '4H')

    def test_good_fourteen_or_fifteen_5422_minor_hand_probes_slam(self):
        for responder in ('SA2H32DAJ76CKQT84', 'SA2H32DAJ76CKQJ84'):
            with self.subTest(responder=responder):
                self.assertEqual(self.bid('1NP', responder), '3C')
                decision = choose_bid(self.profile, Auction.parse('1NP3CP3DP'),
                                      Hand.parse(responder))
                self.assertEqual(decision.call, '4N')
                self.assertEqual(decision.selected_candidate.public_meaning['action_type'],
                                 'minor_slam_probe')
                self.assertEqual(decision.selected_candidate.public_meaning['hcp_min'], 14)
                self.assertEqual(decision.selected_candidate.public_meaning['hcp_max'], 15)
        self.assertNotEqual(self.bid('1NP3CP3DP', 'SA2HK2DAQ76CKJ984'), '4N')

    def test_six_five_minors_after_diamond_transfer_use_effective_point_split(self):
        strong = 'SAKDAKQJ76CKQJ32'
        weak = 'S2H3D987654CQJ432'
        self.assertEqual(self.bid('1NP2NTP3DP', strong), '4N')
        self.assertEqual(self.bid('1NP2NTP3DP', weak), '3H')


if __name__ == '__main__':
    unittest.main()
