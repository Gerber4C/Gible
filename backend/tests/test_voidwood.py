import unittest
from types import SimpleNamespace

from engine.auction import Auction
from engine.cards import Hand
from engine.loader import load_profile
from engine.selector import choose_bid
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
            self.bid(spade_route, 'SAQJ76HKQDAKQJ45C-'), '5C')
        self.assertEqual(
            self.bid(heart_route, 'SKQHAQJ76DAJ9543C-'), '5C')
        self.assertEqual(
            self.bid(spade_route + '5CP', 'S987HKJ4D9876CQJ2'), '5D')
        self.assertEqual(
            self.bid(heart_route + '5CP', 'S987H432DQ876CQJ2'), '5D')

    def test_generic_voidwood_requires_five_trumps(self):
        auction = Auction.parse('1NP2HP2SP3DP3HP')
        decision = choose_bid(
            self.profile, auction, Hand.parse('SAQJ765HKQ5DAKQJC-'))
        self.assertFalse(any(
            candidate.call == '5C'
            and candidate.public_meaning.get('action_type') == 'voidwood_ask'
            for candidate in decision.candidate_pool.candidates))

    def test_undefined_jump_derives_voidwood_with_inferred_trump(self):
        decision = choose_bid(
            self.profile, Auction.parse('1NP2CP2HP3CP'),
            Hand.parse('S-HKQ32DAKQ5CA5432'))
        asks = [
            candidate for candidate in decision.candidate_pool.candidates
            if candidate.public_meaning.get('action_type') == 'voidwood_ask']
        self.assertEqual(len(asks), 1)
        self.assertEqual(asks[0].call, '4S')
        self.assertEqual(asks[0].public_meaning.get('agreed_suit'), 'C')
        self.assertEqual(asks[0].public_meaning.get('void_suit'), 'S')

    def test_transfer_regression_still_works(self):
        self.assertEqual(
            self.bid('1NP2HP2SP', 'SAQJ765HKQDKQ764C-'), '5C')
        self.assertEqual(
            self.bid('1NP2DP2HP', 'S-HAQJ765DKQCKQ765'), '4S')

    def test_legacy_and_state_voidwood_answers_publish_effective_queen(self):
        from engine.replay import replay_auction

        legacy = replay_auction(
            self.profile, Auction.parse('1NP2DP2HP4SP5DP'))
        state_driven = replay_auction(
            self.profile, Auction.parse('1NP2HP2SP3DP3HP4SP5DP'))
        for trace in (legacy, state_driven):
            self.assertTrue(trace.state_exists({
                'key': 'voidwood_answer', 'effective_trump_queen': True,
            }))

    def test_public_nine_fit_requires_ten_cards_for_effective_queen(self):
        class Record:
            def __init__(self, **attributes):
                self.attributes = attributes

            def attribute(self, name):
                return self.attributes.get(name)

        class State:
            def __init__(self, records):
                self.records = records

            def records_matching(self, key, **attributes):
                return tuple(record for record in self.records
                             if all(record.attribute(name) == value
                                    for name, value in attributes.items()))

            def exists(self, key, **attributes):
                return bool(self.records_matching(key, **attributes))

        predicate = next(
            call.applicability.__globals__['has_effective_trump_queen']
            for call in self.profile.call_specifications
            if call.origin_dict()['gadget_id'] == 'voidwood')
        direct_fit = Record(suit='H', asker_min_length=6, min_total=9,
                            voidwood_direct_fit=True)
        public_nine = Record(suit='H', min_total=9)
        three_hearts = Hand.parse('SAKH843DK76542CAJ')
        four_hearts = Hand.parse('SAKH8432DK765CAJ3')
        self.assertTrue(predicate(SimpleNamespace(hand=three_hearts,
                                                   state=State((direct_fit,))), 'H'))
        self.assertFalse(predicate(SimpleNamespace(hand=three_hearts,
                                                    state=State((direct_fit, public_nine))), 'H'))
        self.assertTrue(predicate(SimpleNamespace(hand=four_hearts,
                                                   state=State((direct_fit, public_nine))), 'H'))


if __name__ == '__main__':
    unittest.main()
