import unittest
from types import SimpleNamespace
from unittest.mock import patch

from engine.auction import Auction
from engine.cards import Hand
from engine.loader import load_profile
from engine.replay import replay_auction
from engine.selector import choose_bid
from engine.simulation_decision import decide_minor_major_74
from engine.simulator import simulate_auction


class DaqiushResampleFollowupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = load_profile('daqiush_2over1')

    def bid(self, auction, cards):
        return choose_bid(self.profile, Auction.parse(auction), Hand.parse(cards)).call

    def test_two_major_superaccept_retransfers_then_decides(self):
        cards = 'SAQT75HJT532DATCA'
        decision = choose_bid(self.profile, Auction.parse('1NP2HP3CP'),
                              Hand.parse(cards))
        self.assertEqual(decision.call, '3H')
        decision = choose_bid(self.profile,
                              Auction.parse('1NP2HP3CP3HP3SP'),
                              Hand.parse(cards))
        self.assertIn(decision.call, ('4S', '4N'))

    def test_stayman_fit_with_shortage_starts_slam_probe(self):
        for cards in ('SA852HK76DQCAKJ32', 'SK874HK7DACKJT986'):
            with self.subTest(cards=cards):
                self.assertEqual(self.bid('1NP', cards), '2C')
                self.assertEqual(self.bid('1NP2CP2SP', cards), '3H')
        self.assertEqual(self.bid('1NP2CP2SP3HP', 'SKQ96HA43DAT3CQT8'), '3N')
        self.assertEqual(self.bid('1NP2CP2SP3HP3NTP', 'SA852HK76DQCAKJ32'), '4D')

    def test_heart_trump_four_hearts_answer_shows_spade_shortage(self):
        cards = 'S2HAKT9DQJ54CK832'
        self.assertEqual(self.bid('1NP2CP2HP', cards), '3S')
        self.assertEqual(self.bid('1NP2CP2HP3SP3NTP', cards), '4H')

    def test_shortage_answers_use_same_suit_and_heart_trump_uses_four_hearts_for_spades(self):
        for auction, cards, expected in (
            ('1NP2CP2SP3HP3NTP', 'SAK82HK76DQJ954C2', '4C'),
            ('1NP2CP2SP3HP3NTP', 'SA852HK76DQCAKJ32', '4D'),
            ('1NP2CP2SP3HP3NTP', 'SAK82H2DQJ954CK76', '4H'),
            ('1NP2CP2HP3SP3NTP', 'SA74HKQJ98DQ954C2', '4C'),
            ('1NP2CP2HP3SP3NTP', 'SA74HKQJ98D2CQ954', '4D'),
            ('1NP2CP2HP3SP3NTP', 'S2HAKT9DQJ54CK832', '4H'),
        ):
            with self.subTest(auction=auction, cards=cards):
                self.assertEqual(self.bid(auction, cards), expected)

    def test_diamond_shortage_publicly_revalues_to_major_game(self):
        decision = choose_bid(
            self.profile,
            Auction.parse('1NP2CP2SP3HP3NTP4DP'),
            Hand.parse('SKQ96HA43DATCQT82'),
        )
        self.assertEqual(decision.call, '4S')
        self.assertEqual(
            decision.selected_candidate.public_meaning['action_type'],
            'shortage_adjusted_game_signoff',
        )

    def test_two_short_suits_show_lower_available_answer(self):
        cards = 'SA743H7DACAKQJ852'
        self.assertEqual(self.bid('1NP2CP2SP3HP3NTP', cards), '4D')

    def test_reviewed_shortage_answer_revalues_opener_before_slam_decision(self):
        prefix = '1NP2CP2SP3HP3NTP4CP'
        self.assertEqual(self.bid(prefix, 'SKQ96HA43DAT3CQT8'), '4S')
        self.assertEqual(self.bid(prefix, 'SAKT5HAQ3DKT8C862'), '4D')
        strong = choose_bid(self.profile, Auction.parse(prefix),
                            Hand.parse('SAKT5HAQ3DKJ8C862'))
        self.assertEqual(strong.call, '4N')
        self.assertEqual(strong.selected_candidate.public_meaning['agreed_suit'], 'S')
        self.assertIn('keycard_asking', strong.selected_candidate.public_meaning['call_act_types'])

    def test_shortage_followup_keycard_answers_use_the_agreed_major(self):
        prefix = Auction.parse('1NP2CP2SP3HP3NTP4DP4NP')
        for cards, expected in (
            ('SA765HQJ9876D43C2', '5C'),
            ('S9765HQJ9876D43C2', '5D'),
        ):
            with self.subTest(cards=cards):
                decision = choose_bid(self.profile, prefix, Hand.parse(cards))
                self.assertEqual(decision.call, expected)
                self.assertEqual(
                    decision.selected_candidate.public_meaning['agreed_suit'], 'S')

    def test_heart_game_can_stop_after_four_hearts_shows_spade_shortage(self):
        self.assertEqual(self.bid('1NP2CP2HP3SP3NTP4HP',
                                  'SAQ3HAKT9DK76C862'), 'P')

    def test_stayman_fit_without_shortage_uses_four_diamonds(self):
        cards = 'SAQT4HQ93DK5CA873'
        self.assertEqual(self.bid('1NP2CP2SP', cards), '4D')
        self.assertEqual(self.bid('1NP2CP2SP4DP', 'SKJ982HAK6DA76CQ2'), '4N')
        # The roll-out gate finds cueing above game is not +EV for the
        # minimum opener: rolling 5C scores worse than settling in 4S.
        self.assertEqual(self.bid('1NP2CP2SP4DP', 'SAQT4HQ93DK5CA873'), '4S')

    def test_five_card_spade_reply_does_not_infer_four_heart_slam_trigger(self):
        # G016 rejected the 4NT proposal: 3S does not publicly establish a
        # trump fit, and the review's proposed artificial 4H continuation has
        # no complete public trigger or defined follow-up.
        trace = replay_auction(self.profile, Auction.parse('1NP3CP3S'))
        self.assertEqual(trace.trump_state('ns').status, 'unset')
        self.assertFalse(trace.state_exists({'key': 'keycard_context'}))

        three_spade_fit = 'SAQ4HKQJ9DAKQC876'
        decision = choose_bid(
            self.profile,
            Auction.parse('1NP3CP3SP'),
            Hand.parse(three_spade_fit),
        )
        self.assertIsNone(decision.call)

    def test_strong_responder_can_continue_after_no_shortage_slam_try_is_refused(self):
        auction = Auction.parse('1NP2CP2SP4DP4SP')
        strong = 'SAKQ4HKQJ9DAKQC87'
        weak = 'SAQT4HQ93DK5CA873'

        self.assertEqual(self.bid('1NP2CP2SP4DP4SP', strong), '4N')
        self.assertEqual(self.bid('1NP2CP2HP4DP4HP', strong), '4N')
        self.assertEqual(self.bid('1NP2CP2SP4DP4SP', weak), 'P')
        trace = replay_auction(self.profile, auction)
        self.assertEqual(trace.trump_state('ns').suit, 'S')
        asked = replay_auction(self.profile, Auction.parse(
            '1NP2CP2SP4DP4SP4NP'))
        self.assertTrue(asked.state_exists(
            {'key': 'keycard_context', 'trump_suit': 'S'}))

    def test_no_shortage_probe_can_reach_spade_slam(self):
        result = simulate_auction(self.profile, {
            'n': 'SKJ982HAK6DA76CQ2',
            's': 'SAQT4HQ93DK5CA873',
        })
        self.assertEqual(result.status, 'complete')
        self.assertEqual(result.calls[-6:], ('5S', 'P', '6S', 'P', 'P', 'P'))

    def test_no_shortage_probe_also_reaches_heart_slam(self):
        result = simulate_auction(self.profile, {
            'n': 'SAK6HKJ982DA76CQ2',
            's': 'SQ93HAQT4DK5CA873',
        })
        self.assertEqual(result.status, 'complete')
        self.assertEqual(result.calls[:9],
                         ('1N', 'P', '2C', 'P', '2H', 'P', '4D', 'P', '4N'))
        self.assertEqual(result.calls[-4:], ('6H', 'P', 'P', 'P'))

    def test_slam_texas_asks_hearts_keycards_after_either_answer(self):
        cards = 'SAQHKJ9864DA52CK8'
        self.assertEqual(self.bid('1NP', cards), '4C')
        for answer in ('4D', '4H'):
            with self.subTest(answer=answer):
                decision = choose_bid(self.profile, Auction.parse('1NP4CP' + answer + 'P'), Hand.parse(cards))
                self.assertEqual(decision.call, '4N')
                self.assertEqual(decision.private_memory.purposes[-1].kind, 'keycard_slam')

    def test_slam_texas_keycard_purpose_places_six_hearts(self):
        result = simulate_auction(self.profile, {
            'n': 'SK9874HAQ3DKT3CA5',
            's': 'SAQHKJ9864DA52CK8',
        })
        self.assertEqual(result.status, 'complete')
        self.assertEqual(result.calls[-6:], ('5S', 'P', '6H', 'P', 'P', 'P'))

    def test_slam_texas_keycard_purpose_also_places_six_spades(self):
        result = simulate_auction(self.profile, {
            'n': 'SAQ3HK9874DKT3CA5',
            's': 'SKJ9864HAQDA52CK8',
        })
        self.assertEqual(result.status, 'complete')
        self.assertEqual(result.calls[:9],
                         ('1N', 'P', '4D', 'P', '4S', 'P', '4N', 'P', '5S'))
        self.assertEqual(result.calls[-4:], ('6S', 'P', 'P', 'P'))

    def test_game_only_texas_still_stops_at_four_hearts(self):
        result = simulate_auction(self.profile, {
            'n': 'SAQ7HKJ8DA762CQ54',
            's': 'ST2HAQT976D53CKJ2',
        })
        self.assertEqual(result.status, 'complete')
        self.assertEqual(result.calls[-4:], ('4H', 'P', 'P', 'P'))

    def test_six_five_major_minor_values_second_suit(self):
        cards = 'S2HKQJT98DQJ954C2'
        self.assertEqual(self.bid('1NP', cards), '2D')
        self.assertEqual(self.bid('1NP2DP2HP', cards), '3D')
        result = simulate_auction(self.profile, {
            'n': 'SJ853HA75DAK3CKT8',
            's': cards,
        })
        self.assertEqual(result.status, 'complete')
        self.assertEqual(result.calls[-6:], ('3H', 'P', '4H', 'P', 'P', 'P'))

    def test_six_five_spade_minor_also_values_second_suit(self):
        cards = 'SKQJT98H2DQJ954C2'
        self.assertEqual(self.bid('1NP', cards), '2H')
        self.assertEqual(self.bid('1NP2HP2SP', cards), '3D')
        result = simulate_auction(self.profile, {
            'n': 'SJ853HA75DAK3CKT8',
            's': cards,
        })
        self.assertEqual(result.status, 'complete')
        self.assertEqual(result.calls[-6:], ('3S', 'P', '4S', 'P', 'P', 'P'))

    def test_seven_retained_points_six_five_major_minor_invites_in_major(self):
        heart_cards = 'S2HKQJT98DJ9543C2'
        spade_cards = 'SKQJT98H2DJ9543C2'
        self.assertEqual(self.bid('1NP', heart_cards), '2D')
        self.assertEqual(self.bid('1NP2DP2HP', heart_cards), '3H')
        self.assertEqual(self.bid('1NP', spade_cards), '2H')
        self.assertEqual(self.bid('1NP2HP2SP', spade_cards), '3S')

    def test_six_four_major_invite_and_game_only_texas_are_distinct(self):
        inviter = 'SKJT987HJ876D32C2'  # five effective points
        game_force = 'SKQJ987HJ876D32C2'  # seven effective points
        heart_force = 'SJ876HKQJ987D32C2'
        opener = 'SA83HK87DQJ43CAJ8'
        self.assertEqual(self.bid('1NP', inviter), '2C')
        self.assertEqual(self.bid('1NP2CP2DP', inviter), '2S')
        self.assertEqual(self.bid('1NP2CP2DP2SP', opener), '2N')
        self.assertEqual(self.bid('1NP2CP2DP2SP2NTP', inviter), '3S')
        self.assertEqual(self.bid('1NP', game_force), '4D')
        self.assertEqual(self.bid('1NP', heart_force), '4C')
        five_four_inviter = 'SKJ987HQJ87DQ2C32'
        self.assertEqual(self.bid('1NP2CP2DP2SP2NTP', five_four_inviter), 'P')
        self.assertEqual(self.bid('1NP2CP2DP2SP3NTP', five_four_inviter), 'P')
        self.assertEqual(self.bid('1NP2CP2DP2SP3NTP', inviter), '4S')

    def test_shapely_five_six_two_suit_invitation_thresholds(self):
        # 6♣–5♠ describes the spades as a six-card invite at six effective
        # points, while a weaker instance stops at 2♠.
        strong_minor = 'SKJT98H2D2CQJT987'
        weak_minor = 'ST9876H2D2CKJT987'
        self.assertEqual(self.bid('1NP', strong_minor), '2H')
        self.assertEqual(self.bid('1NP2HP2SP', strong_minor), '3S')
        self.assertEqual(self.bid('1NP', weak_minor), '2H')
        self.assertEqual(self.bid('1NP2HP2SP', weak_minor), 'P')
        # 6♠–5♥ crosses into the two-major invitation at five effective
        # points; the weaker hand transfers to its longer spade suit.
        strong_majors = 'SKJT987HJ8765D2C2'
        weak_majors = 'SJ98765HJ8765D2C2'
        self.assertEqual(self.bid('1NP', strong_majors), '2D')
        self.assertEqual(self.bid('1NP2DP2HP', strong_majors), '2S')
        self.assertEqual(self.bid('1NP', weak_majors), '2H')
        self.assertEqual(self.bid('1NP2HP2SP', weak_majors), 'P')

    def test_lower_retained_strength_six_five_uses_game_only_texas(self):
        cards = 'S2HKQJ987D98765C3'
        self.assertEqual(self.bid('1NP', cards), '4C')
        # The explicit 6M–5m game-only route also covers a soft five-point
        # hand whose K–R score alone falls just short of the generic gate.
        self.assertEqual(self.bid('1NP', 'S2HKJT987DJ8765C3'), '4C')

    def test_seven_four_uses_public_deal_comparison(self):
        cards = 'SA743H7DACAKQJ852'
        with patch('engine.selector.decide_minor_major_74', return_value={
            'call': '3C', 'completion_rates': {'6C': 0.8, '6S': 0.5},
            'sample_count': 20,
        }) as compare:
            self.assertEqual(self.bid('1NP2CP2SP', cards), '3C')
            self.assertTrue(compare.called)
        with patch('engine.selector.decide_minor_major_74', return_value={
            'call': '3H', 'completion_rates': {'6C': 0.5, '6S': 0.8},
            'sample_count': 20,
        }):
            self.assertEqual(self.bid('1NP2CP2SP', cards), '3H')

    @patch('engine.simulation_decision.sample_deals')
    @patch('engine.simulation_decision.calculate_available_table')
    def test_seven_four_sampling_fixes_only_responder_hand(self, solve, sample):
        responder = Hand.parse('SA743H7DACAKQJ852')
        opener = Hand.parse('SKQJ62HAKQDQ92C94')
        sample.return_value = SimpleNamespace(
            deals=tuple({'n': opener, 's': responder} for _ in range(16)),
            attempts=16, seed=1)
        solve.return_value = {'C': {'s': 12}, 'S': {'n': 11}}
        result = decide_minor_major_74(self.profile, Auction.parse('1NP2CP2SP'), responder)
        self.assertEqual(result['call'], '3C')
        self.assertEqual(sample.call_args.args[:2], ('s', responder))
        self.assertEqual(sample.call_args.kwargs['public_constraints']['n']['min_lengths']['S'], 4)
        self.assertEqual(sample.call_args.kwargs['public_constraints']['n']['max_lengths']['H'], 3)


if __name__ == '__main__':
    unittest.main()
