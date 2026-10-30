import unittest

from engine.cards import Hand
from engine.rkcb_continuation import (
    OrdinaryRKCBFrame, naturally_shown_long_suits, ordinary_response,
    ordinary_rkcb_frame, public_minimum_length, useful_voids,
)
from engine.trace import AuctionTrace, StateRecord


def add_context(trace, **attributes):
    trace.add_state(StateRecord('keycard_context', attributes, {}))


class OrdinaryFrameTests(unittest.TestCase):
    def test_latest_ordinary_frame_ignores_stale_pending_record(self):
        trace = AuctionTrace()
        add_context(trace, method='rkcb_1430', status='pending_answer', trump_suit='H')
        add_context(trace, method='rkcb_1430', status='answered', trump_suit='H')
        frame = ordinary_rkcb_frame(trace)
        self.assertEqual((frame.status, frame.trump), ('answered', 'H'))

    def test_nonordinary_method_is_never_read_as_ordinary_rkcb(self):
        trace = AuctionTrace()
        add_context(trace, method='voidwood', status='pending_answer', trump_suit='H')
        self.assertIsNone(ordinary_rkcb_frame(trace))

    def test_frame_parses_counts_queen_void_and_kings(self):
        trace = AuctionTrace()
        add_context(trace, method='rkcb_1430', status='answered', trump_suit='D',
                    answer_category='1/3/void', keycard_counts=[1, 3],
                    useful_void='C', useful_void_category='exact',
                    not_required_kings=['C', 'H'])
        frame = ordinary_rkcb_frame(trace)
        self.assertEqual(frame.keycard_counts, (1, 3))
        self.assertEqual(frame.useful_void, 'C')
        self.assertEqual(frame.not_required_kings, ('C', 'H'))
        self.assertTrue(frame.active)


class UsefulVoidTests(unittest.TestCase):
    def _trace(self):
        trace = AuctionTrace()
        trace.applied_meanings = [
            {'seat': 'n', 'call': '1S',
             'public_meaning': {'nature_labels': ['natural'],
                                'target_suit': 'S', 'minimum_length': 4}},
            {'seat': 'n', 'call': '1H',
             'public_meaning': {'nature_labels': ['artificial'],
                                'target_suit': 'H', 'minimum_length': 5}},
            {'seat': 'n', 'call': '2C',
             'public_meaning': {'nature_labels': ['natural'],
                                'target_suit': 'C', 'minimum_length': 3}},
        ]
        return trace

    def test_partner_natural_long_suit_excludes_a_void(self):
        self.assertEqual(naturally_shown_long_suits(self._trace(), 'n'),
                         frozenset({'S'}))
        self.assertEqual(public_minimum_length(
            {'target_suit': 'S', 'minimum_length': 4}, 'S'), 4)
        self.assertEqual(public_minimum_length(
            {'suit_length_minimums': {'D': 5}}, 'D'), 5)

    def test_voids_ignore_trump_and_partner_long_suits(self):
        trace = self._trace()
        hand = Hand.parse('SA765HKQ9876D432C-')  # C void, H trump
        self.assertEqual(useful_voids(trace, 's', hand, 'H'), ('C',))
        spade_void = Hand.from_dict({'spades': '',
                                     'hearts': 'KQ9876543',
                                     'diamonds': '432', 'clubs': '2'})
        self.assertEqual(useful_voids(trace, 's', spade_void, 'H'), ())

    def test_two_useful_voids_choose_the_lowest(self):
        trace = AuctionTrace()
        hand = Hand.parse('SA76543HKQ98765D-C-')
        # D and C both void; H trump; partner has no natural long suit.
        self.assertEqual(useful_voids(trace, 's', hand, 'H'), ('C', 'D'))


class OrdinaryResponseTests(unittest.TestCase):
    def test_four_ordinary_answers(self):
        for cards, call in (
            ('SA765HQJ9876D43C2', '5C'),
            ('S9765HQJ9876D43C2', '5D'),
            ('SA765HKJ9876D43C2', '5H'),
            ('SA765HKQ9876D43C2', '5S'),
        ):
            with self.subTest(call=call):
                response = ordinary_response(Hand.parse(cards), 'H')
                self.assertEqual(response.call, call)

    def test_high_answers(self):
        # Zero/two/four with a useful void -> 5NT, no exact void published.
        response = ordinary_response(
            Hand.parse('SA765HKQ9876D432C-'), 'H', ('C',))
        self.assertEqual((response.call, response.keycard_counts,
                          response.void_suit, response.void_category),
                         ('5N', (0, 2, 4), None, 'unspecified'))
        # One/three with a lower void -> six of the void.
        lower = ordinary_response(
            Hand.parse('S97654HKJ9876D43C-'), 'H', ('C',))
        self.assertEqual((lower.call, lower.keycard_counts,
                          lower.void_suit), ('6C', (1, 3), 'C'))
        # One/three with a void higher than trumps -> six of trumps.
        higher = ordinary_response(
            Hand.from_dict({'spades': 'A7654', 'hearts': '',
                            'diamonds': 'QJ9763', 'clubs': '32'}), 'D', ('H',))
        self.assertEqual((higher.call, higher.void_category),
                         ('6D', 'higher_than_trump'))

    def test_unusable_void_falls_back_to_the_ordinary_answer(self):
        # The caller passes no useful void when partner showed the suit.
        response = ordinary_response(Hand.parse('SA765HKQ9876D432C-'), 'H')
        self.assertEqual(response.call, '5S')  # two keycards with the queen


if __name__ == '__main__':
    unittest.main()
