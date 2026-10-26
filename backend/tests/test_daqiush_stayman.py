import unittest

from engine.auction import Auction
from engine.cards import Hand
from engine.loader import load_profile
from engine.selector import choose_bid
from engine.simulator import simulate_auction


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
                self.assertEqual(self.bid('1NP2CP2DP' + bid + 'P', 'SA87HKJ8DQ762CKQ4'), 'P')

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


if __name__ == '__main__':
    unittest.main()
