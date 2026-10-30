import unittest
from unittest.mock import patch

from engine.auction import Auction
from engine.cards import Hand
from engine.grand_slam_policy import (
    GRAND_INVITE_QUANTILE, QUANTITATIVE_QUANTILE, accept_grand,
    in_top_quantile, top_quantile_threshold,
)
from engine.loader import load_profile
from engine.selector import choose_bid
from engine.simulator import simulate_auction


class OwnerRouteTests(unittest.TestCase):
    """Owner-reported 1NT responder routes (2026-10-27)."""

    @classmethod
    def setUpClass(cls):
        cls.profile = load_profile('daqiush_2over1')

    def bid(self, auction, cards):
        hand = Hand.parse(cards)
        self.assertEqual(sum(hand.length(s) for s in 'SHDC'), 13, cards)
        return choose_bid(self.profile, Auction.parse(auction), hand).call

    # Bug 1: seven-card major strength is K-R based.
    def test_seven_card_major_uses_kr_bands(self):
        # Game strength, no slam interest: Texas.
        self.assertEqual(self.bid('1NP', 'SKQJT987H43D52C76'), '4D')
        # Invitational: Jacoby, then three of the major.
        self.assertEqual(self.bid('1NP2HP2SP', 'SKJT9876H43D52C76'), '3S')
        # Weaker: Jacoby, then pass.
        self.assertEqual(self.bid('1NP2HP2SP', 'SJT98765H43D52C76'), 'P')

    def test_five_card_332_slam_routes(self):
        self.assertEqual(self.bid('1NP2HP2SP', 'SAKQ76HKJ5DA43CQ7'), '5N')
        self.assertEqual(self.bid('1NP2HP2SP', 'SAQJ76HAKJD43CQ76'), '6C')
        self.assertEqual(self.bid('1NP2HP2SP', 'SAQJ76HAKJDQ43C76'), '6D')

    # Bug 2: strong seven-card minor transfers before cueing.
    def test_strong_seven_club_transfers_and_cues(self):
        hand = 'SA4H2DAK2CAKQJT72'
        self.assertEqual(self.bid('1NP', hand), '2S')
        self.assertEqual(self.bid('1NP2SP3CP', hand), '3H')

    # Bug 3: six-four minors transfer, then show the other minor.
    def test_six_four_minors_transfer_then_show_other_minor(self):
        clubs = 'S32H4DAKQ2CKQJ987'
        self.assertEqual(self.bid('1NP', clubs), '2S')
        self.assertEqual(self.bid('1NP2SP3CP', clubs), '3D')
        diamonds = 'S32H4DAKQJ98CKQJ9'
        self.assertEqual(self.bid('1NP', diamonds), '2N')
        self.assertEqual(self.bid('1NP2NTP3DP', diamonds), '4C')

    def test_superaccept_other_minor_is_a_cue(self):
        decision = choose_bid(
            self.profile, Auction.parse('1NP2SP2NTP'),
            Hand.parse('S32H4DAKQ2CKQJ987'))
        self.assertEqual(decision.call, '3D')
        self.assertEqual(decision.selected_candidate.public_meaning['agreed_suit'], 'C')

    # Bug 4: continuation table after opener's natural 3NT.
    def test_second_minor_three_notrump_continuations(self):
        self.assertEqual(self.bid('1NP2HP2SP3CP3NTP',
                                  'SKQJ76HA5D43CQ765'), 'P')
        self.assertEqual(self.bid('1NP2HP2SP3CP3NTP',
                                  'SAQJ76HAK5D4CQJ76'), '6N')
        self.assertEqual(self.bid('1NP2HP2SP3CP3NTP',
                                  'SAQJ765HK5D4CQJ76'), '4D')
        self.assertEqual(self.bid('1NP2HP2SP3CP3NTP',
                                  'SAQJ76HK5D4CQJ765'), '4C')

    def test_two_suiter_reaches_game(self):
        result = simulate_auction(self.profile, {
            'n': 'SQ5HKQ4DAKQJ76C32',
            's': 'SAQJ76HK5D4CQJ765',
        })
        self.assertEqual(result.status, 'complete')
        self.assertIn('4C', result.calls)
        self.assertEqual(result.calls[-1], 'P')

    def test_minor_serious_3nt_forced_cue_ladder_clubs(self):
        serious = 'SQJHQJDAKQCAQJxxx'
        self.assertEqual(self.bid('1NP2SP3CP', serious), '3N')

        # Partner's first cue is forced and carries no extra-strength promise.
        decision = choose_bid(self.profile,
                              Auction.parse('1NP2SP3CP3NTP'),
                              Hand.parse('SAK5HKQ4DAKQ76C32'))
        self.assertEqual(decision.call, '4D')
        self.assertEqual(
            decision.selected_candidate.public_meaning['action_type'],
            'serious_forced_control_cue')
        self.assertTrue(
            decision.selected_candidate.public_meaning['forced_control_cue'])

        # No side control: return to the minor game, not four clubs.
        self.assertEqual(
            self.bid('1NP2SP3CP3NTP', 'SQJHQJ3DQJ4CAKQJ5'), '5C')
        # Cues may cross four of the agreed minor; game remains five.
        self.assertEqual(
            self.bid('1NP2SP3CP3NTP', 'SAKQHQJ4D765CQJ32'), '4S')

        # After the forced cue, an eligible serious hand asks keycards.
        self.assertEqual(
            self.bid('1NP2SP3CP3NTP4DP', serious), '4N')
        # Three keycards without grand-slam intent must cue/game, not ask.
        self.assertEqual(
            self.bid('1NP2SP3CP3NTP4DP', 'SQJHQJDAKQCAKQJxx'), '5C')

        # Ordinary 1430 answers continue to work after the ladder.
        self.assertEqual(
            self.bid('1NP2SP3CP3NTP4DP4NP',
                     'SAK5HKQ4DAKQ76C32'), '5H')
        self.assertEqual(
            self.bid('1NP2SP3CP3NTP4DP4NP',
                     'SAK5HKQ4DAKQ76CQ3'), '5S')
        self.assertEqual(
            self.bid('1NP2SP3CP3NTP4DP5CP',
                     'SAK5HKQ4DAKQ76C32'), 'P')
        # Six of the agreed minor is a final small slam; partner passes.
        self.assertEqual(
            self.bid('1NP2SP3CP3NTP4DP4NP5HP5SP5NP6CP',
                     'SAK5HKQ4DAKQ76C32'), 'P')

        # A skipped side suit plus no control in the serious hand confirms a
        # missing control, so the ladder stops in game instead of asking.
        self.assertEqual(
            self.bid('1NP2SP3CP3NTP', 'SAKQHKQD7654CAJT9'), '4H')
        self.assertEqual(
            self.bid('1NP2SP3CP3NTP4HP', 'SQJHQJDQJ2CAKQJxx'), '5C')

    def test_minor_serious_3nt_forced_cue_ladder_diamonds(self):
        serious = 'SQJHQJDAKQJxxCQJx'
        self.assertEqual(self.bid('1NP2NTP3DP', serious), '3N')
        self.assertEqual(
            self.bid('1NP2NTP3DP3NTP', 'SAK5HKQ4DQ765CA32'), '4C')
        self.assertEqual(
            self.bid('1NP2NTP3DP3NTP', 'SQJHQJ3CQJ4DAKQJT'), '5D')
        self.assertEqual(
            self.bid('1NP2NTP3DP3NTP4CP', serious), '4N')
        self.assertEqual(
            self.bid('1NP2NTP3DP3NTP4CP5DP',
                     'SAK5HKQ4DQ765CA32'), 'P')

    def test_voidwood_two_keycard_answer_offers_king_ask_and_placement(self):
        south = 'S-HKQJT864DK85CAK8'
        north = 'SA754HA752DACQJ43'
        self.assertEqual(
            self.bid('1NP2DP2HP4SP5HP', south), '5S')
        self.assertEqual(
            self.bid('1NP2DP2HP4SP5HP5SP', north), '5N')
        self.assertEqual(
            self.bid('1NP2DP2HP4SP5HP5SP5NP', south), '7H')
        self.assertEqual(
            self.bid('1NP2DP2HP4SP5HP5SP5NP7HP', north), 'P')


class ExclusionKeycardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = load_profile('daqiush_2over1')

    def bid(self, auction, cards):
        return choose_bid(self.profile, Auction.parse(auction),
                          Hand.parse(cards)).call

    def test_asks_show_a_void(self):
        self.assertEqual(self.bid('1NP2HP2SP', 'SAQJ76HKQ5DKQ764C-'), '5C')
        self.assertEqual(self.bid('1NP2DP2HP', 'S-HAQJ76DKQ5CKQ765'), '4S')

    def test_five_step_answers_and_followups(self):
        opener = 'SAK5HKQ4DKQ765C32'
        self.assertEqual(self.bid('1NP2HP2SP5CP', opener), '5N')
        zero = 'SQJ5HQJ4DQJ765C32'
        self.assertEqual(self.bid('1NP2HP2SP5CP', zero), '5D')
        self.assertEqual(self.bid('1NP2HP2SP5CP5DP5HP', zero), '5N')
        self.assertEqual(self.bid('1NP2HP2SP5CP5DP5HP',
                                  'SJ95HQJ4DQJ765C32'), '5S')
        self.assertEqual(self.bid('1NP2HP2SP5CP5HP5SP', opener), '6D')


class GrandSlamPolicyTests(unittest.TestCase):
    def test_quantiles(self):
        self.assertAlmostEqual(top_quantile_threshold(15, 17, 0.15), 16.7)
        hand = Hand.parse('SAKQ76HKJ5DA43CQ7')  # 19 HCP
        self.assertTrue(in_top_quantile(hand, 15, 17, GRAND_INVITE_QUANTILE))
        seventeen = Hand.parse('SAQJ76HAKJD43CQ76')  # 17 HCP
        sixteen = Hand.parse('SAQJ76HAK5D43CQ76')  # 16 HCP
        fifteen = Hand.parse('SAQJ76HKJ5DQ4CQ76')  # 15 HCP
        self.assertTrue(in_top_quantile(seventeen, 15, 17, GRAND_INVITE_QUANTILE))
        self.assertFalse(in_top_quantile(sixteen, 15, 17, GRAND_INVITE_QUANTILE))
        self.assertTrue(in_top_quantile(sixteen, 15, 17, QUANTITATIVE_QUANTILE))
        self.assertFalse(in_top_quantile(fifteen, 15, 17, QUANTITATIVE_QUANTILE))

    def test_accept_grand_uses_15_percent_and_50_percent(self):
        seventeen = Hand.parse('SAQJ76HAKJD43CQ76')
        sixteen = Hand.parse('SAQJ76HAK5D43CQ76')
        fifteen = Hand.parse('SAQJ76HKJ5DQ4CQ76')
        self.assertTrue(accept_grand(seventeen, quantitative=False))
        self.assertFalse(accept_grand(sixteen, quantitative=False))
        self.assertTrue(accept_grand(sixteen, quantitative=True))
        self.assertFalse(accept_grand(fifteen, quantitative=True))

    def test_missing_solver_falls_back_to_deterministic(self):
        from engine.dds_adapter import DDSUnavailableError

        seventeen = Hand.parse('SAQJ76HAKJD43CQ76')
        with patch('engine.grand_slam_policy.compare_contract_targets',
                   side_effect=DDSUnavailableError('no solver')):
            self.assertTrue(accept_grand(
                seventeen, deals=({'n': seventeen},), trump='S', declarer='s',
                solve_table=lambda deal: None))


if __name__ == '__main__':
    unittest.main()
