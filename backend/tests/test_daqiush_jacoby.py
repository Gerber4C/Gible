import unittest

from engine.auction import Auction
from engine.cards import Hand
from engine.loader import load_profile
from engine.replay import replay_auction
from engine.selector import choose_bid


class DaqiushJacobyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = load_profile('daqiush_2over1')

    def bid(self, auction, cards):
        return choose_bid(self.profile, Auction.parse(auction), Hand.parse(cards)).call

    def test_exactly_five_major_with_at_most_three_other_major_transfers(self):
        self.assertEqual(self.bid('1NP', 'SA32HKQJ76D432C76'), '2D')
        self.assertEqual(self.bid('1NP', 'SKQJ76HA32D432C76'), '2H')
        self.assertEqual(self.bid('1NP', 'SKQJ76HA432D42C76'), '2C')

    def test_weak_two_major_hand_transfers_longer_or_better_suit_and_stops(self):
        for hand, transfer, accept in (
            ('S98765H5432DQJ8C6', '2H', '2S'),
            ('S5432H98765DQJ8C6', '2D', '2H'),
            ('S98765H5432DQJ86C-', '2H', '2S'),
            ('SQT987HJ9765D43C2', '2H', '2S'),
            ('SJ9765HQT987D43C2', '2D', '2H'),
        ):
            with self.subTest(hand=hand):
                self.assertEqual(self.bid('1NP', hand), transfer)
                self.assertEqual(self.bid('1NP' + transfer + 'P' + accept + 'P', hand), 'P')
                for answer in (('2N', '3C', '3D', '3S') if transfer == '2H'
                               else ('2S', '2N', '3C', '3H')):
                    with self.subTest(answer=answer):
                        prefix = '1NP' + transfer + 'P' + answer + 'P'
                        if answer == '3' + accept[-1]:
                            self.assertEqual(self.bid(prefix, hand), 'P')
                        else:
                            self.assertEqual(self.bid(prefix, hand),
                                             '3H' if transfer == '2H' else '3D')

    def test_five_invitation_other_major_acceptance_shows_fifth_major(self):
        hearts = choose_bid(self.profile,
                            Auction.parse('1NP2DP2HP2NP'),
                            Hand.parse('SAKQJ2H32DKQ4CQ32'))
        self.assertEqual(hearts.call, '3S')
        self.assertEqual(
            hearts.selected_candidate.public_meaning['action_type'],
            'jacoby_five_invitation_accept_other')

        spades = choose_bid(self.profile,
                            Auction.parse('1NP2HP2SP2NP'),
                            Hand.parse('SA2HKQJ76DKQ4CQ32'))
        self.assertEqual(spades.call, '3H')
        self.assertEqual(
            spades.selected_candidate.public_meaning['action_type'],
            'jacoby_five_invitation_accept_other')

    def test_six_minor_five_major_invite_uses_description_proxy(self):
        self.assertEqual(self.bid('1NP2DP2HP', 'S3HKQJ76D4CQ98765'), '3H')

    def test_three_notrump_choice_keeps_flat_4333_without_major_support(self):
        self.assertEqual(self.bid('1NP2HP2SP3NP', 'SAKQHJT98DAK2C432'), 'P')
        self.assertEqual(self.bid('1NP2HP2SP3NP', 'SAKQHJT98DAK32C42'), '4S')
        self.assertEqual(self.bid('1NP2DP2HP3NP', 'SAKQJHJT9DAK2C432'), 'P')
        self.assertEqual(self.bid('1NP2DP2HP3NP', 'SAKQJHJT9DAK32C42'), '4H')
        self.assertEqual(self.bid('1NP2HP2SP3NP', 'SAKHJT98DAK32C432'), 'P')

    def test_second_minor_continuation_supports_the_transferred_major(self):
        self.assertEqual(self.bid('1NP2HP2SP3DP', 'SAKQHJT98DAK2C432'), '3S')
        self.assertEqual(self.bid('1NP2HP2SP3DP', 'SAKQHJT98DAK32C42'), '3S')
        self.assertEqual(self.bid('1NP2DP2HP3CP', 'SAKQJHJT9DAK2C432'), '3H')
        self.assertEqual(self.bid('1NP2HP2SP3DP3SP', 'SAKQJ9H432D9876C2'), '4C')
        self.assertEqual(self.bid('1NP2HP2SP3DP3SP4CP', 'SAK5HKQ4DQ7654C32'), '4S')
        self.assertEqual(self.bid('1NP2DP2HP3CP3HP', 'S2HAKQJ9D432C9876'), '3N')
        self.assertEqual(
            self.bid('1NP2DP2HP3CP3HP3NTP', 'SAK5HKQ4DQ7654C32'), '4H')

    def test_six_card_slam_interest_uses_texas_before_keycard(self):
        self.assertEqual(self.bid('1NP', 'SA62HAQJT72DJ7CJ4'), '4C')
        self.assertEqual(self.bid('1NP', 'SAQJT72HA62DJ7CJ4'), '4D')
        self.assertEqual(self.bid('1NP', 'ST2HAQT976D53CKJ2'), '4C')
        for auction in ('1NP4CP4DP', '1NP4CP4HP'):
            with self.subTest(auction=auction):
                self.assertEqual(
                    self.bid(auction, 'SA62HAQJT72DJ7CJ4'), '4N')

    def test_three_level_support_cues_do_not_require_control(self):
        # A sole cue is available without control.
        self.assertEqual(
            self.bid('1NP2DP2HP3DP', 'SQJ2HAKDQJ54CQJ32'), '3S')
        # With two cues, neither controlled: cue the lowest.
        self.assertEqual(
            self.bid('1NP2DP2HP3CP', 'SQJ2HQJDQJ54CAQ32'), '3D')
        # With one controlled, show that one.
        self.assertEqual(
            self.bid('1NP2DP2HP3CP', 'SAK2HQJDQJ54CQJ32'), '3S')
        self.assertEqual(
            self.bid('1NP2DP2HP3CP', 'SQJ2HQJDAK54CQJ32'), '3D')

    def test_five_card_major_with_side_void_uses_natural_second_minor(self):
        self.assertEqual(
            self.bid('1NP2HP2SP', 'SA9542HAK6D-CAKQ94'), '3C')
        self.assertEqual(
            self.bid('1NP2DP2HP', 'S-HA9542DAKQ94CAK6'), '3D')

    def test_diamond_fit_support_cue_offers_four_heart_and_denial_choices(self):
        north = 'SAK9HQ9DK754CA973'
        south = 'S4HAKJT53DQJT8CQ5'
        self.assertEqual(self.bid('1NP2DP2HP3DP', north), '3S')
        self.assertEqual(self.bid('1NP2DP2HP3DP3SP', south), '4H')
        self.assertEqual(self.bid('1NP2DP2HP3DP3SP4HP', north), '4N')
        self.assertEqual(
            self.bid('1NP2DP2HP3DP3SP4HP4NP', south), '5C')

        # The other offered calls are available for the appropriate hands.
        self.assertEqual(
            self.bid('1NP2DP2HP3DP3SP', 'S4HAKJT5DQJT8CA54'), '4C')
        self.assertEqual(
            self.bid('1NP2DP2HP3DP3SP', 'S4HAKJT5DQJT8CQ54'), '4S')
        self.assertEqual(
            self.bid('1NP2DP2HP3DP3SP', 'S43HAKJT5DQJT8CQ5'), '4D')

    def test_strong_nine_five_five_major_minor_forces_second_minor(self):
        spades = 'SQJ865HJ5D6CKQ754'
        hearts = 'S2HKQJ76DQJ854C32'
        self.assertEqual(self.bid('1NP2HP2SP', spades), '3C')
        self.assertEqual(self.bid('1NP2HP2SP', 'SQJ865HJD6CKQ7543'), '3C')
        self.assertEqual(self.bid('1NP2DP2HP', hearts), '3D')
        self.assertEqual(
            self.bid('1NP2HP2SP3CP', 'SA97HK4DK984CAJT3'), '3S')
        self.assertEqual(self.bid('1NP2HP2SP3CP3SP', spades), '4C')
        # A weaker nine in the same shape remains an invitation.
        self.assertEqual(self.bid('1NP2HP2SP', 'SQJ865HQJD6CQJT54'), '2N')

    def test_five_four_after_second_minor_three_notrump_invites(self):
        self.assertEqual(
            self.bid('1NP2HP2SP3DP3NTP', 'SAK982H9DQJT3CK64'), '4N')

    def test_absolute_maximum_superaccept_shows_the_specified_doubleton(self):
        cases = (
            ('2D', 'S97HKQ32DAK76CA76', '2S', 'S'),
            ('2D', 'SAK76HKQ32D97CA76', '2N', 'D'),
            ('2D', 'SA76HKQ32DAK76C97', '3C', 'C'),
            ('2H', 'SKQ32H97DAK76CA76', '2N', 'H'),
            ('2H', 'SKQ32HAK76DA76C97', '3C', 'C'),
            ('2H', 'SKQ32HAK76D97CA76', '3D', 'D'),
        )
        for transfer, cards, answer, doubleton in cases:
            with self.subTest(transfer=transfer, answer=answer):
                prefix = '1NP' + transfer + 'P'
                self.assertEqual(self.bid(prefix, cards), answer)
                trace = replay_auction(self.profile, Auction.parse(prefix + answer))
                self.assertEqual(trace.applied_meanings[-1]['public_meaning']['doubleton_suit'], doubleton)

    def test_absolute_maximum_four_card_major_4333_uses_three_major(self):
        self.assertEqual(self.bid('1NP2DP', 'SA76HKQ32DAK7C976'), '3H')
        self.assertEqual(self.bid('1NP2HP', 'SKQ32HAK7DA76C976'), '3S')

    def test_non_maximum_or_less_than_four_support_uses_ordinary_acceptance(self):
        self.assertEqual(self.bid('1NP2DP', 'SAQ7HKJ8DA762CQ54'), '2H')
        self.assertEqual(self.bid('1NP2HP', 'SAQ7HKJ8DA762CQ54'), '2S')

    def test_confirmed_slam_hands_retransfer_then_ask_keycards(self):
        for transfer, trump, responder, answers in (
            ('2D', 'H', 'SA62HAQJT72DJ7CJ4', ('2S', '2N', '3C', '3H')),
            ('2H', 'S', 'SAQJT72HA62DJ7CJ4', ('2N', '3C', '3D', '3S')),
        ):
            retransfer = '3D' if trump == 'H' else '3H'
            for answer in answers:
                with self.subTest(transfer=transfer, answer=answer):
                    prefix = '1NP' + transfer + 'P' + answer + 'P'
                    if answer == '3' + trump:
                        ask_prefix = prefix
                    else:
                        first = choose_bid(self.profile, Auction.parse(prefix),
                                           Hand.parse(responder))
                        self.assertEqual(first.call, retransfer)
                        ask_prefix = prefix + retransfer + 'P3' + trump + 'P'
                    decision = choose_bid(self.profile, Auction.parse(ask_prefix),
                                          Hand.parse(responder))
                    self.assertEqual(decision.call, '4N')
                    self.assertEqual(decision.private_memory.purposes[-1].kind, 'keycard_slam')
                    self.assertEqual(decision.private_memory.purposes[-1].trump, trump)
                    trace = replay_auction(self.profile, Auction.parse(ask_prefix + '4N'))
                    self.assertTrue(trace.state_exists({'key': 'keycard_context', 'trump_suit': trump}))

    def test_superaccept_keycard_answer_and_non_slam_responder_limit(self):
        self.assertEqual(
            self.bid('1NP2DP2SP3DP3HP4NP', 'S97HKQ32DAK76CA76'), '5D')
        self.assertEqual(
            self.bid('1NP2DP2SP', 'ST2HAQT976D53CKJ2'), '3D')
        # The ordinary transfer acceptance's 4NT is quantitative only; a
        # six-card slam-interest major uses Texas first (4C/4D) and then 4NT
        # asks keycards, so this synthetic state has no ordinary keycard.
        self.assertIsNone(self.bid('1NP2DP2HP', 'SA62HAQJT72DJ7CJ4'))


if __name__ == '__main__':
    unittest.main()
