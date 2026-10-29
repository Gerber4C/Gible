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
        self.assertEqual(self.bid('1NP2HP2SP3DP3SP', 'SAKQJ9H432D9876C2'), '4S')
        self.assertEqual(self.bid('1NP2DP2HP3CP3HP', 'S2HAKQJ9D432C9876'), '4H')

    def test_six_card_slam_interest_uses_texas_before_keycard(self):
        self.assertEqual(self.bid('1NP', 'SA62HAQJT72DJ7CJ4'), '4C')
        self.assertEqual(self.bid('1NP', 'SAQJT72HA62DJ7CJ4'), '4D')
        self.assertEqual(self.bid('1NP', 'ST2HAQT976D53CKJ2'), '4C')
        for auction in ('1NP4CP4DP', '1NP4CP4HP'):
            with self.subTest(auction=auction):
                self.assertEqual(
                    self.bid(auction, 'SA62HAQJT72DJ7CJ4'), '4N')

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
