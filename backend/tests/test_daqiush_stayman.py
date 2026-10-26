import unittest
from unittest.mock import patch
from types import SimpleNamespace

from engine.auction import Auction
from engine.cards import Hand
from engine.loader import load_profile
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


if __name__ == '__main__':
    unittest.main()
