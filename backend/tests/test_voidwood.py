import unittest
from types import SimpleNamespace

from engine.auction import Auction
from engine.cards import Hand
from engine.voidwood import (
    answer_bids, context_validation, effective_keycards,
    is_safe_voidwood_ask, voidwood_jump,
)


class VoidwoodJumpTests(unittest.TestCase):
    def test_diamond_trump_club_void_jump_is_five_clubs(self):
        auction = Auction.parse('1NP2HP2SP3DP3HP')
        self.assertEqual(voidwood_jump(auction, trump='D', void='C'), '5C')
        self.assertEqual(answer_bids('5C'),
                         ('5D', '5H', '5S', '5N', '6C'))

    def test_answer_map_boundaries(self):
        self.assertEqual(answer_bids('4S'),
                         ('4N', '5C', '5D', '5H', '5S'))
        self.assertEqual(answer_bids('5D'),
                         ('5H', '5S', '5N', '6C', '6D'))
        self.assertEqual(answer_bids('6S'),
                         ('6N', '7C', '7D', '7H', '7S'))
        self.assertEqual(answer_bids('7C'), ())

    def test_rejections(self):
        low = Auction.parse('1NP')
        self.assertIsNone(voidwood_jump(low, trump='D', void='C'))
        auction = Auction.parse('1NP2HP2SP3DP3HP')
        self.assertIsNone(voidwood_jump(auction, trump='D', void='D'))
        self.assertIsNone(voidwood_jump(auction, trump='D', void='N'))
        # The cheapest club call is 4C; the jump alone is Voidwood.
        self.assertEqual(voidwood_jump(auction, trump='D', void='C'), '5C')

    def test_reject_when_fewer_than_five_answers_remain(self):
        auction = Auction.parse('1NP2HP2SP3DP3HP4NP5CP')
        self.assertIsNone(voidwood_jump(auction, trump='D', void='C'))


class VoidwoodContextTests(unittest.TestCase):
    def test_confirmed_trump_is_required(self):
        hand = Hand.parse('SAKQJ2H3DAKQJ543C-')
        self.assertIsNone(context_validation(
            trump_state=SimpleNamespace(status='agreed', suit='D'),
            keycard_pending=False, hand=hand, trump='D', void='C'))
        self.assertEqual(context_validation(
            trump_state=None, keycard_pending=False, hand=hand,
            trump='D', void='C'), 'No confirmed trump suit')
        self.assertEqual(context_validation(
            trump_state=SimpleNamespace(status='provisional', suit='D'),
            keycard_pending=False, hand=hand, trump='D', void='C'),
            'No confirmed trump suit')
        self.assertEqual(context_validation(
            trump_state=SimpleNamespace(status='agreed', suit='H'),
            keycard_pending=False, hand=hand, trump='D', void='C'),
            'Confirmed trump conflicts with the requested trump')

    def test_pending_keycard_trump_void_and_shape(self):
        hand = Hand.parse('SAKQJ2H3DAKQJ543C-')
        state = SimpleNamespace(status='agreed', suit='D')
        self.assertEqual(context_validation(
            trump_state=state, keycard_pending=True, hand=hand,
            trump='D', void='C'), 'A keycard inquiry is already pending')
        self.assertEqual(context_validation(
            trump_state=state, keycard_pending=False, hand=hand,
            trump='D', void='D'), 'The void suit cannot be trumps')
        self.assertEqual(context_validation(
            trump_state=state, keycard_pending=False,
            hand=Hand.parse('SAKQJ2H3DAKQJ4C32'),
            trump='D', void='C'), 'The asker is not void in the bid suit')


class VoidwoodSafetyTests(unittest.TestCase):
    def test_five_club_ask_requires_enough_own_keycards(self):
        for own, safe in ((0, False), (1, False), (2, True),
                          (3, True), (4, True)):
            with self.subTest(own=own):
                verdict = is_safe_voidwood_ask(
                    '5C', trump='D', own_effective_keycards=own)
                self.assertEqual(verdict.safe, safe)
        verdict = is_safe_voidwood_ask(
            '5C', trump='D', own_effective_keycards=0)
        self.assertIn('5H', verdict.forced_six_answers)
        self.assertFalse(verdict.safe)

    def test_lower_ask_can_still_stop_at_five_of_trumps(self):
        verdict = is_safe_voidwood_ask(
            '4S', trump='D', own_effective_keycards=1)
        self.assertTrue(verdict.safe)
        self.assertIn('5H', verdict.forced_six_answers)

    def test_effective_keycards_exclude_the_void_ace(self):
        hand = Hand.parse('SAKQJ2H3DAKQJ4C32')
        self.assertEqual(effective_keycards(hand, 'D', 'C'), 3)


class VoidwoodProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from engine.loader import load_profile
        cls.profile = load_profile('daqiush_2over1')

    def bid(self, auction, cards):
        from engine.selector import choose_bid
        return choose_bid(self.profile, Auction.parse(auction),
                          Hand.parse(cards)).call

    def test_profile_registers_only_voidwood(self):
        ids = [gadget.id for gadget in self.profile.gadgets]
        self.assertIn('voidwood', ids)
        self.assertNotIn('exclusion_keycard', ids)
        gadget = next(g for g in self.profile.gadgets if g.id == 'voidwood')
        self.assertEqual(gadget.name, 'Voidwood（缺门关键张）')

    def test_confirmed_diamond_state_from_two_auction_families(self):
        spade_route = '1NP2HP2SP3DP3HP'
        heart_route = '1NP2DP2HP3DP3SP'
        self.assertEqual(
            self.bid(spade_route, 'SAQJ76HKQ5DAKQJ4C-'), '5C')
        self.assertEqual(
            self.bid(heart_route, 'SKQ5HAQJ76DAJ954C-'), '5C')
        self.assertEqual(
            self.bid(spade_route + '5CP', 'S987HKJ4D9876CQJ2'), '5D')
        self.assertEqual(
            self.bid(heart_route + '5CP', 'S987H432DQ876CQJ2'), '5D')

    def test_transfer_regression_still_works(self):
        self.assertEqual(
            self.bid('1NP2HP2SP', 'SAQJ76HKQ5DKQ764C-'), '5C')
        self.assertEqual(
            self.bid('1NP2DP2HP', 'S-HAQJ76DKQ5CKQ765'), '4S')


if __name__ == '__main__':
    unittest.main()
