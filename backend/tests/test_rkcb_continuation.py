import unittest

from engine.auction import Auction
from engine.cards import Hand
from engine.rkcb_continuation import (
    OrdinaryRKCBFrame, five_spade_role, five_trump_available,
    lowest_showable_side_king, naturally_shown_long_suits,
    ordinary_response, ordinary_rkcb_frame, public_minimum_length,
    queen_ask_call, useful_voids,
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


class RelayGeometryTests(unittest.TestCase):
    def _frame(self, category, trump='H'):
        trace = AuctionTrace()
        add_context(trace, method='rkcb_1430', status='answered',
                    trump_suit=trump, answer_category=category,
                    keycard_counts=[1, 4] if category == '1/4' else [0, 3])
        return ordinary_rkcb_frame(trace)

    def test_five_spades_is_the_queen_ask_after_five_diamonds_in_hearts(self):
        auction = Auction.parse('1NP4CP4HP4NP5DP')
        frame = self._frame('0/3')
        self.assertEqual(queen_ask_call(auction, frame), '5S')
        self.assertEqual(five_spade_role(auction, frame), 'queen_ask')

    def test_five_spades_is_a_relay_after_five_clubs_in_hearts(self):
        auction = Auction.parse('1NP4CP4HP4NP5CP')
        frame = self._frame('1/4')
        self.assertEqual(queen_ask_call(auction, frame), '5D')
        self.assertEqual(five_spade_role(auction, frame), 'relay')

    def test_relay_is_available_after_five_hearts_when_five_hearts_is_gone(self):
        auction = Auction.parse('1NP4CP4HP4NP5HP')
        frame = self._frame('2/no_q')
        self.assertFalse(five_trump_available(auction, 'H'))
        self.assertEqual(five_spade_role(auction, frame), 'relay')

    def test_spade_trumps_never_treat_five_spades_as_a_relay(self):
        auction = Auction.parse('1NP4CP4HP4NP5DP')
        frame = self._frame('0/3', 'S')
        self.assertEqual(queen_ask_call(auction, frame), '5H')
        self.assertEqual(five_spade_role(auction, frame), 'unavailable')

    def test_lowest_showable_side_king_stays_below_six_trumps(self):
        auction = Auction.parse('1NP4CP4HP4NP5CP5SP5NP')
        hand = Hand.parse('SA2HKQ976DK432C42')
        self.assertEqual(lowest_showable_side_king(hand, 'H', auction), '6D')
        self.assertIsNone(lowest_showable_side_king(
            hand, 'H', auction, denied=('D',)))
        self.assertIsNone(lowest_showable_side_king(hand, 'C', auction))


class RescueSimulationTests(unittest.TestCase):
    def test_sampling_chooses_the_relay_when_it_is_not_worse(self):
        from engine.rkcb_simulation import compare_rescue_routes
        from engine.trace import AuctionTrace

        auction = Auction.parse('1NP4CP4HP4NP5HP')
        trace = AuctionTrace()
        frame = OrdinaryRKCBFrame(trump='H', status='answered',
                                  answer_category='2/no_q', keycard_counts=(2,))
        decision = compare_rescue_routes(
            None, auction, trace, Hand.parse('S32HQ98765D432C32'), 'H',
            frame, evaluator=lambda *args: '5S')
        self.assertEqual((decision.call, decision.unavailable), ('5S', False))

    def test_unavailable_comparison_is_typed(self):
        from engine.dds_adapter import DDSUnavailableError
        from engine.rkcb_simulation import compare_rescue_routes
        from engine.trace import AuctionTrace

        auction = Auction.parse('1NP4CP4HP4NP5HP')
        frame = OrdinaryRKCBFrame(trump='H', status='answered',
                                  answer_category='2/no_q', keycard_counts=(2,))

        def unavailable(*args):
            raise DDSUnavailableError('no solver')

        decision = compare_rescue_routes(
            object(), auction, AuctionTrace(), Hand.parse('S32HQ98765D432C32'),
            'H', frame, evaluator=unavailable)
        self.assertTrue(decision.unavailable)
        self.assertIsNone(decision.call)

    def test_only_legal_route_is_deterministic(self):
        from engine.rkcb_simulation import compare_rescue_routes
        from engine.trace import AuctionTrace

        auction = Auction.parse('1NP4CP4HP4NP5SP')
        frame = OrdinaryRKCBFrame(trump='H', status='answered',
                                  answer_category='2/q', keycard_counts=(2,))
        decision = compare_rescue_routes(
            None, auction, AuctionTrace(), Hand.parse('S32HQ98765D432C32'),
            'H', frame, evaluator=lambda *args: self.fail('must not sample'))
        self.assertEqual(decision.call, '6H')


class AmbiguousMixtureTests(unittest.TestCase):
    def test_possible_counts_are_pruned_by_the_askers_cards(self):
        from engine.rkcb_continuation import possible_partner_counts
        frame = OrdinaryRKCBFrame(trump='H', status='answered',
                                  answer_category='0/2/4/void',
                                  keycard_counts=(0, 2, 4))
        self.assertEqual(possible_partner_counts(frame, 4), (0,))
        self.assertEqual(possible_partner_counts(frame, 3), (0, 2))

    def test_mixture_compares_the_complete_category(self):
        from engine.rkcb_simulation import compare_ambiguous_continuations
        zero = Hand.parse('S32HQ8765D432C432')
        two = Hand.parse('SA2HKQ8765D432C32')
        deals = ({'n': zero, 's': Hand.parse('S32HQ8765D432C432')},
                 {'n': two, 's': Hand.parse('S32HQ8765D432C432')})

        def fake_solver(deal):
            two_keycards = deal['n'].keycard_count('H') == 2
            return {'H': {'s': 12 if two_keycards else 11},
                    'NT': {'n': 11}}

        frame = OrdinaryRKCBFrame(
            trump='H', status='answered', answer_category='0/2/4/void',
            keycard_counts=(0, 2, 4), useful_void_category='unspecified')
        decision = compare_ambiguous_continuations(
            None, Auction.parse('1NP4CP4HP4NP5NP'),
            AuctionTrace(), Hand.parse('SA2HKQ976D432C432'), frame,
            ('P', '6H'), deals=deals, solve=fake_solver)
        self.assertEqual((decision.call, decision.unavailable), ('P', False))

    def test_one_exposed_call_is_deterministic_without_a_solver(self):
        from engine.rkcb_simulation import compare_ambiguous_continuations
        frame = OrdinaryRKCBFrame(trump='H', status='answered',
                                  answer_category='1/4', keycard_counts=(1, 4))
        decision = compare_ambiguous_continuations(
            None, Auction.parse('1NP4CP4HP4NP5CP'), AuctionTrace(),
            Hand.parse('SA2HKQ976D432C432'), frame, ('6H',),
            evaluator=lambda calls: self.fail('solver must not run'))
        self.assertEqual(decision.call, '6H')


class HighAnswerGeometryTests(unittest.TestCase):
    def test_skipped_lower_kings_only_count_calls_between_the_answer_and_invite(self):
        from engine.rkcb_continuation import skipped_lower_kings
        legal = ['6C', '6D', '6H', '6S']
        self.assertEqual(skipped_lower_kings('5N', '6C', 'H', legal), ())
        self.assertEqual(skipped_lower_kings('5N', '6D', 'H', legal), ('C',))
        self.assertEqual(skipped_lower_kings('6C', '6D', 'H', legal), ())
        self.assertEqual(skipped_lower_kings('5N', '6H', 'H', legal), ('C', 'D'))

    def test_high_answer_invitations_stay_below_six_trumps(self):
        from engine.rkcb_continuation import high_answer_invitations
        trace = AuctionTrace()
        add_context(trace, method='rkcb_1430', status='answered',
                    trump_suit='H', answer_category='0/2/4/void',
                    answer_call='5N', keycard_counts=[0, 2, 4],
                    useful_void_category='unspecified')
        frame = ordinary_rkcb_frame(trace)
        auction = Auction.parse('1NP4CP4HP4NP5NP')
        self.assertEqual(high_answer_invitations(auction, frame),
                         ('6C', '6D'))

    def test_lowest_counterinvite_king_skips_unnecessary_kings(self):
        from engine.rkcb_continuation import lowest_counterinvite_king
        trace = AuctionTrace()
        add_context(trace, method='rkcb_1430', status='answered',
                    trump_suit='H', answer_category='0/2/4/void',
                    answer_call='5N', keycard_counts=[0, 2, 4],
                    not_required_kings=['C'])
        frame = ordinary_rkcb_frame(trace)
        auction = Auction.parse('1NP4CP4HP4NP5NP6CP')
        hand = Hand.parse('SA2HKQ976DK432C42')
        self.assertEqual(lowest_counterinvite_king(hand, frame, auction), '6D')


class MethodIsolationTests(unittest.TestCase):
    def test_other_keycard_methods_are_never_ordinary(self):
        for method in ('voidwood', 'nfrkcb_offer', 'nfrkcb_answered'):
            with self.subTest(method=method):
                trace = AuctionTrace()
                add_context(trace, method=method, status='answered',
                            trump_suit='H')
                self.assertIsNone(ordinary_rkcb_frame(trace))

    def test_completed_and_disrupted_frames_are_inactive(self):
        for status in ('completed', 'disrupted'):
            with self.subTest(status=status):
                trace = AuctionTrace()
                add_context(trace, method='rkcb_1430', status=status,
                            trump_suit='H')
                frame = ordinary_rkcb_frame(trace)
                self.assertIsNotNone(frame)
                self.assertFalse(frame.active)

    def test_no_keycard_frame_means_no_ordinary_continuation(self):
        self.assertIsNone(ordinary_rkcb_frame(AuctionTrace()))


if __name__ == '__main__':
    unittest.main()
