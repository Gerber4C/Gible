import unittest
from unittest.mock import patch
from types import SimpleNamespace

from engine.auction import Auction
from engine.cards import Hand
from engine.loader import load_profile
from engine.replay import replay_auction
from engine.selector import choose_bid
from engine.simulator import simulate_auction
from engine.simulation_decision import decide_six_four_major_after_three_notrump


class DaqiushStaymanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = load_profile('daqiush_2over1')

    def bid(self, auction, cards):
        return choose_bid(self.profile, Auction.parse(auction), Hand.parse(cards)).call

    def test_screenshot_game_hand_finds_four_spades(self):
        result = simulate_auction(self.profile, {
            'n': 'SAJ65H96DAQ3CKQJ3',
            's': 'SKQT2HQJ3DK942C94',
        })
        self.assertEqual(result.status, 'complete')
        self.assertEqual(result.calls, ('1N', 'P', '2C', 'P', '2S', 'P', '4S', 'P', 'P', 'P'))

    def test_game_stayman_continuations(self):
        south = 'SKQT2HQJ3DK942C94'
        self.assertEqual(self.bid('1NP', south), '2C')
        self.assertEqual(self.bid('1NP2CP2DP', south), '3N')
        self.assertEqual(self.bid('1NP2CP2HP', south), '3N')
        self.assertEqual(self.bid('1NP2CP2SP', south), '4S')
        self.assertEqual(self.bid('1NP2CP2HP3NP', 'SAJ65HK762DAQ3CK3'), '4S')
        self.assertEqual(self.bid('1NP2CP2HP3NP', 'SAQ7HKJ83DA762CQ5'), 'P')

    def test_game_forcing_3nt_covers_major_denial_boundary_hands(self):
        # 10 HCP with 4-0-5-4 and 9 HCP strong-nine with 4-4-0-5 have no
        # natural 2NT invitation; their 3NT is the game-forcing route.
        self.assertEqual(
            self.bid('1NP2CP2DP', 'S7432H-DKQJ93CKJ76'), '3N')
        self.assertEqual(
            self.bid('1NP2CP2DP', 'SA643HK854DCQ7532'), '3N')

    def test_shortage_game_is_a_suggestion_not_a_forced_signoff(self):
        auction = '1NP2CP2HP3SP3NP4CP4HP'
        self.assertEqual(
            self.bid(auction, 'SAJ83HAKT3D2CKQ54'), '4N')
        self.assertEqual(
            self.bid(auction, 'SJ832HQT32D2CQ432'), 'P')

    def test_weak_4441_after_spade_reply_plays_3nt(self):
        # 4C is the strong 4441 minor probe; 10 HCP with no fit is 3NT.
        self.assertEqual(
            self.bid('1NP2CP2SP', 'S2H9654DA432CAQT8'), '3N')

    def test_three_level_high_suit_meanings_after_stayman(self):
        # 2D denied a major: 3S is a cue with spade control; without it,
        # 3H remains the minor-support cue.
        for auction in ('1NP2CP2DP3CP', '1NP2CP2DP3DP'):
            with self.subTest(auction=auction):
                self.assertEqual(
                    self.bid(auction, 'SAK2HQJDQJ54CQJ32'), '3S')
        self.assertEqual(
            self.bid('1NP2CP2DP3CP', 'SQJ2HQJDQJ54CAQ32'), '3H')

        # 2S showed four spades: 3S is natural and shows the fifth spade.
        for auction in ('1NP2CP2SP3CP', '1NP2CP2SP3DP'):
            with self.subTest(auction=auction):
                self.assertEqual(
                    self.bid(auction, 'SAKQ76HQJDQ5CQ432'), '3S')
        natural = replay_auction(
            self.profile, Auction.parse('1NP2CP2SP3CP3S'))
        self.assertEqual(natural.trump_state('ns').status, 'unset')
        self.assertEqual(
            self.bid('1NP2CP2SP3CP', 'SAKQ2HQJ2DQJ5CQ32'), '3D')
        self.assertEqual(
            self.bid('1NP2CP2SP3DP', 'SAKQ2HQJ2DQJ5CQ32'), '3H')

        # 2H also makes 3S natural; 3H is natural only with five hearts
        # and a 3D cue available, otherwise 3H is the sole cue.
        self.assertEqual(
            self.bid('1NP2CP2HP3DP', 'SAKQ2HKQ32DQJ5CQ3'), '3S')
        self.assertEqual(
            self.bid('1NP2CP2HP3CP', 'SQJ2HKQT83DAKCQ32'), '3H')
        self.assertEqual(
            self.bid('1NP2CP2HP3DP', 'SQJ2HKQ32DAK5CQ32'), '3H')

    def test_natural_minor_probe_shows_fifth_heart_and_passes_three_notrump(self):
        south = 'SJ963HA64D-CAJT852'
        north = 'SA87HKQT83DQJ75CK'
        self.assertEqual(self.bid('1NP2CP2HP3CP', north), '3H')
        self.assertEqual(self.bid('1NP2CP2HP3CP3NP', south), 'P')
        self.assertEqual(self.bid('1NP2CP2HP3CP3HP', south), '3N')
        self.assertEqual(self.bid('1NP2CP2HP3CP3HP3NP', north), 'P')

        # With four spades, 3S has priority over showing the fifth heart.
        self.assertEqual(
            self.bid('1NP2CP2HP3CP', 'SAK87HKQT83DQJ7C5'), '3S')

    def test_seven_card_club_slam_after_natural_heart_reply(self):
        south = 'SA964H9DKCAKQ8652'
        north = 'SA42HAK875DA73CT3'
        self.assertEqual(self.bid('1NP2CP2HP3CP3HP', south), '6C')
        self.assertEqual(
            self.bid('1NP2CP2HP3CP3HP6CP', north), 'P')

    def test_natural_two_notrump_invite_accept_shows_five_card_major(self):
        # After 1NT-2C-2H-2NT, a maximum with five hearts accepts via 3H,
        # showing the fifth heart; four hearts accepts with 3NT.
        self.assertEqual(self.bid('1NP2CP2HP2NTP', 'SAKQH98765DAKC432'), '3H')
        self.assertEqual(self.bid('1NP2CP2HP2NTP', 'SAKQHQJ98DA32C432'), '3N')
        self.assertEqual(self.bid('1NP2CP2HP2NTP', 'SAKQH98765DAQC432'), 'P')
        # Spades are symmetric after 1NT-2C-2S-2NT.
        self.assertEqual(self.bid('1NP2CP2SP2NTP', 'SAKQJ9H432DKQJC54'), '3S')
        # Responder then chooses the final game.
        self.assertEqual(self.bid('1NP2CP2HP2NTP3HP', 'S432H432DAKQC5432'), '4H')
        self.assertEqual(self.bid('1NP2CP2HP2NTP3HP', 'S5432H43DAKQJC432'), '3N')

    def test_inviting_four_spades_after_heart_reply_is_nonforcing(self):
        responder = 'SKQ72H932DA43C862'
        self.assertEqual(self.bid('1NP', responder), '2C')
        self.assertEqual(self.bid('1NP2CP2HP', responder), '2S')
        self.assertEqual(self.bid('1NP2CP2HP2SP', 'SAJ65HK762DAQ3CK3'), '4S')
        self.assertEqual(self.bid('1NP2CP2HP2SP', 'SAJ65HK762DQ73CKQ'), 'P')
        self.assertEqual(self.bid('1NP2CP2HP2SP', 'SA7HKJ83DAJ62CQ53'), '2N')
        self.assertEqual(self.bid('1NP2CP2HP2SP2NP', responder), 'P')

    def test_five_four_major_invitations_can_stop_after_diamond_reply(self):
        hearts = 'SKQ32HQJ763D84C76'
        spades = 'SQJ762HKQ32D84C76'
        for hand, bid in ((hearts, '2H'), (spades, '2S')):
            with self.subTest(bid=bid):
                self.assertEqual(self.bid('1NP', hand), '2C')
                self.assertEqual(self.bid('1NP2CP2DP', hand), bid)
                # 2M may also conceal a six-card suit with game-going shape
                # strength, so opener's low reply leaves responder another turn.
                self.assertEqual(self.bid('1NP2CP2DP' + bid + 'P', 'SA87HKJ8DQ762CKQ4'), '2N')
                self.assertEqual(self.bid('1NP2CP2DP' + bid + 'P2NP', hand), 'P')

    def test_four_spade_invitation_after_spade_stayman_answer(self):
        responder = 'SKQ72H932DA43C862'
        self.assertEqual(self.bid('1NP2CP2SP', responder), '3S')
        self.assertEqual(self.bid('1NP2CP2SP3SP', 'SAJ65HK762DQ73CKQ'), 'P')
        self.assertEqual(self.bid('1NP2CP2SP3SP', 'SAJ65HK762DAQ3CK3'), '4S')

    def test_weak_hand_without_transfer_or_garbage_stayman_passes_one_notrump(self):
        north = 'SJ743H964DA976C85'
        self.assertEqual(self.bid('1NP', north), 'P')
        auction = simulate_auction(self.profile, {
            'n': north, 's': 'SAQ5HKQJ72DK3CQ73',
        }, dealer='s')
        self.assertEqual(auction.status, 'complete')
        self.assertEqual(auction.calls, ('1N', 'P', 'P', 'P'))

    def test_weak_club_shortage_three_suiter_uses_garbage_stayman(self):
        for responder in ('S9876H5432DQJ86C2', 'S987H5432DQJ876C2',
                          'S9876H543DQJ876C2', 'S9876H5432DQJ876C-'):
            with self.subTest(responder=responder):
                self.assertEqual(self.bid('1NP', responder), '2C')
                for answer in ('2D', '2H', '2S'):
                    with self.subTest(answer=answer):
                        self.assertEqual(self.bid('1NP2CP' + answer + 'P', responder), 'P')

    def test_weak_five_four_four_zero_uses_major_transfer_not_garbage_stayman(self):
        self.assertEqual(self.bid('1NP', 'S98765H5432DQJ86C-'), '2H')

    def test_six_four_major_strength_routes_are_symmetric(self):
        # The effective-point examples have the same holdings with H/S swapped.
        for long_suit, short_suit, game, weak, moderate, strong in (
            ('H', 'S', 'SQJ32HAJ8765D84C7', 'SKQ32HAJ8765D84C7',
             'SKQ32HAK8765D84C7', 'SAK32HAK8765D84C7'),
            ('S', 'H', 'SAJ8765HQJ32D84C7', 'SAJ8765HKQ32D84C7',
             'SAK8765HKQ32D84C7', 'SAK8765HAK32D84C7'),
        ):
            with self.subTest(long_suit=long_suit):
                self.assertEqual(self.bid('1NP', game), '4C' if long_suit == 'H' else '4D')
                for hand in (weak, moderate, strong):
                    self.assertEqual(self.bid('1NP', hand), '2C')

                denied = '1NP2CP2DP'
                self.assertEqual(self.bid(denied, weak), '4D' if long_suit == 'H' else '4H')
                self.assertEqual(self.bid(denied, moderate), '3' + short_suit)
                self.assertEqual(self.bid(denied, strong), '3' + short_suit)

                four_four_answer = '2' + short_suit
                six_four_answer = '2' + long_suit
                for hand in (weak, moderate, strong):
                    self.assertEqual(self.bid('1NP2CP' + four_four_answer + 'P', hand),
                                     '3' + long_suit)
                self.assertEqual(self.bid('1NP2CP' + six_four_answer + 'P', weak),
                                 '4' + long_suit)
                for hand in (moderate, strong):
                    self.assertEqual(self.bid('1NP2CP' + six_four_answer + 'P', hand),
                                     '3' + short_suit)

                self.assertEqual(self.bid(denied + '3' + short_suit + 'P',
                                          'SA73HKJ8DAQ3CKQ54'), '3N')
                with patch('engine.selector.decide_six_four_major_after_three_notrump',
                           return_value={'call': '4' + long_suit}):
                    self.assertEqual(self.bid(denied + '3' + short_suit + 'P3NP', moderate),
                                     '4' + long_suit)
                with patch('engine.selector.decide_six_four_major_after_three_notrump',
                           return_value={'call': '4C'}):
                    self.assertEqual(self.bid(denied + '3' + short_suit + 'P3NP', moderate),
                                     '4C')
                self.assertEqual(self.bid(denied + '3' + short_suit + 'P3NP', strong), '4C')

    def test_six_four_major_simulation_uses_public_opener_constraints(self):
        responder = Hand.parse('SKQ32HAK8765D84C7')
        opener = Hand.parse('SA73HQJ2DAT3CKQ54')
        auction = Auction.parse('1NP2CP2DP3SP3NTP')
        sampled = SimpleNamespace(deals=tuple({'n': opener, 's': responder}
                                               for _ in range(10)), attempts=10, seed=41)
        with patch('engine.simulation_decision.sample_deals', return_value=sampled) as sampler, \
             patch('engine.simulation_decision.compare_contract_targets') as compare:
            compare.return_value = (SimpleNamespace(contract='4H', completion_rate=0.9),
                                    SimpleNamespace(contract='6H', completion_rate=0.1))
            self.assertEqual(decide_six_four_major_after_three_notrump(
                self.profile, auction, responder)['call'], '4H')
            self.assertEqual(sampler.call_args.kwargs['public_constraints']['n'],
                             {'min_hcp': 14, 'max_hcp': 18,
                              'max_lengths': {'H': 3, 'S': 3}})
            compare.return_value = (SimpleNamespace(contract='4H', completion_rate=0.95),
                                    SimpleNamespace(contract='6H', completion_rate=0.8))
            self.assertEqual(decide_six_four_major_after_three_notrump(
                self.profile, auction, responder)['call'], '4C')

    def test_six_four_boundary_keeps_weak_and_invitational_routes(self):
        self.assertEqual(self.bid('1NP', 'S9872HKJ8765D84C7'), '2D')
        self.assertEqual(self.bid('1NP', 'SJ932HAJ8765D84C7'), '2C')
        self.assertEqual(self.bid('1NP2CP2HP', 'SJ932HAJ8765D84C7'), '3H')
        self.assertEqual(self.bid('1NP', 'SJ932HAQ8765D84C7'), '4C')
        self.assertEqual(self.bid('1NP', 'SQ932HAK8765D84C7'), '4C')

    def test_six_four_weak_slam_transfer_is_completed_without_ambiguity(self):
        opener = 'SA73HQJ2DAT3CKQ54'
        self.assertEqual(self.bid('1NP2CP2DP4DP', opener), '4H')
        self.assertEqual(self.bid('1NP2CP2DP4HP', opener), '4S')

    def test_six_four_game_only_texas_reaches_game(self):
        result = simulate_auction(self.profile, {
            'n': 'SAT4HQT2DAT3CKQ54',
            's': 'SQJ32HAJ8765D84C7',
        })
        self.assertEqual(result.status, 'complete')
        self.assertEqual(result.calls, ('1N', 'P', '4C', 'P', '4H', 'P', 'P', 'P'))


    def test_four_four_four_one_asks_minors_after_any_stayman_answer(self):
        # 2D denial: the 21-count 4-4-4-1 now asks minors instead of 3NT.
        self.assertEqual(
            self.bid('1NP2CP2DP', 'SKQ98HAKQ3DKT82CA'), '4C')
        # 2H: singleton heart, no fit -> 4C; four hearts -> major-fit route.
        self.assertEqual(
            self.bid('1NP2CP2HP', 'SKQ98H8DAKQ3CKT82'), '4C')
        self.assertNotEqual(
            self.bid('1NP2CP2HP', 'S8HKQ98DAKQ3CKT82'), '4C')
        # 2S: one spade, no fit -> 4C; four spades -> major-fit route.
        self.assertEqual(
            self.bid('1NP2CP2SP', 'S8HKQ98DAKQ3CKT82'), '4C')
        self.assertNotEqual(
            self.bid('1NP2CP2SP', 'SKQ98H8DAKQ3CKT82'), '4C')
        # The answer scheme is unchanged.
        self.assertEqual(
            self.bid('1NP2CP2DP4CP', 'SAT2HJ8DAQ4CKJ542'), '4D')

if __name__ == '__main__':
    unittest.main()
