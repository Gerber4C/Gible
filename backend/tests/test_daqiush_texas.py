import unittest

from engine.auction import Auction
from engine.cards import Hand
from engine.loader import load_profile
from engine.selector import choose_bid
from engine.simulator import simulate_auction


class DaqiushTexasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = load_profile('daqiush_2over1')

    def bid(self, auction, cards):
        return choose_bid(self.profile, Auction.parse(auction), Hand.parse(cards)).call

    def test_screenshot_responds_four_clubs_not_jacoby(self):
        self.assertEqual(self.bid('1NP', 'ST2HAQT976D53CKJ2'), '4C')
        decision = choose_bid(self.profile, Auction.parse('1NP'),
                              Hand.parse('ST2HAQT976D53CKJ2'))
        self.assertEqual(decision.private_memory.purposes[0].responses,
                         {'4D': '4H', '4H': 'P'})

    def test_owner_labelled_game_only_hands_choose_texas(self):
        for cards in ('SJ98HAK7532DT7CK3', 'SA53HAQ8543DJ4CJ9',
                      'SJT8HAKQJ73DJ4C62', 'S432HAKQJ74DT95CT',
                      'SJ64HAKQ975DJ97C2', 'SAQ9HK98753DQ72C6'):
            with self.subTest(cards=cards):
                self.assertEqual(self.bid('1NP', cards), '4C')

    def test_owner_labelled_slam_interest_hands_use_texas(self):
        for cards in ('SA62HAQJT72DJ7CJ4', 'SK53HKQT962DJ8CA4',
                      'SA74HKQ9765D42CA9', 'SKT3HAK8532DJT5C8',
                      'SJ84HAQJT95DKT7C9', 'SQT4HAJT943DA76C6',
                      'S762HAKJ982DK83C8'):
            with self.subTest(cards=cards):
                self.assertEqual(self.bid('1NP', cards), '4C')

    def test_screenshot_opener_has_two_unprotected_kq_and_wants_declarer(self):
        self.assertEqual(self.bid('1NP4CP', 'SAQ7HKJ8DA762CQ54'), '4H')

    def test_spade_texas_is_four_diamonds_and_accepts_at_four_spades(self):
        self.assertEqual(self.bid('1NP', 'SAQT976HT2D53CKJ2'), '4D')
        self.assertEqual(self.bid('1NP4DP', 'SAQ7HKJ8DA762CQ54'), '4S')

    def test_one_unprotected_kq_uses_lower_answer(self):
        self.assertEqual(self.bid('1NP4CP', 'SAQ7HAK8DA762C754'), '4D')
        self.assertEqual(self.bid('1NP4DP', 'SAQ7HAK8DA762C754'), '4H')

    def test_eight_card_majors_use_texas_and_reach_keycard(self):
        south_hearts = 'S4HAQJ98765DKQCAK'
        north = 'SAK7HKT4DAT864CQ2'
        self.assertEqual(self.bid('1NP', south_hearts), '4C')
        self.assertEqual(self.bid('1NP4CP', north), '4H')
        self.assertEqual(self.bid('1NP4CP4HP', south_hearts), '4N')
        self.assertEqual(self.bid('1NP4CP4HP4NP', north), '5D')

        south_spades = 'SAQJ98765H4DKQCAK'
        self.assertEqual(self.bid('1NP', south_spades), '4D')

    def test_simulation_advances_past_screenshot_block(self):
        result = simulate_auction(self.profile, {
            'n': 'SAQ7HKJ8DA762CQ54',
            's': 'ST2HAQT976D53CKJ2',
        })
        self.assertEqual(result.status, 'complete')
        self.assertEqual(result.calls, ('1N', 'P', '4C', 'P', '4H', 'P', 'P', 'P'))

    def test_lower_texas_answer_then_responder_game_signoff_completes(self):
        result = simulate_auction(self.profile, {
            'n': 'SAKJ7HJ83DQJ72CA9',
            's': 'ST2HAQT976D53CKJ2',
        })
        self.assertEqual(result.status, 'complete')
        self.assertEqual(result.calls,
                         ('1N', 'P', '4C', 'P', '4D', 'P', '4H', 'P', 'P', 'P'))


if __name__ == '__main__':
    unittest.main()
