import unittest

from engine.cards import Hand
from engine.keycard_queen_table import (
    RELAY_AVAILABLE, RELAY_UNAVAILABLE, RELAY_USUALLY_UNNECESSARY,
    five_spade_relay_status, queen_answer_call, queen_answer_facts,
    queen_answer_geometry, queen_ask,
)


class QueenTableTests(unittest.TestCase):
    def test_queen_ask_calls(self):
        self.assertEqual(queen_ask('C', '1/4'), '5D')
        self.assertEqual(queen_ask('C', '0/3'), '5H')
        self.assertEqual(queen_ask('D', '1/4'), '5H')
        self.assertEqual(queen_ask('D', '0/3'), '5H')
        self.assertEqual(queen_ask('H', '1/4'), '5D')
        self.assertEqual(queen_ask('H', '0/3'), '5S')
        self.assertEqual(queen_ask('S', '1/4'), '5D')
        self.assertEqual(queen_ask('S', '0/3'), '5H')

    def test_queen_answer_geometry(self):
        c = queen_answer_geometry('C', '1/4')
        self.assertEqual((c.queen_ask, c.no_queen), ('5D', '6C'))
        self.assertEqual(c.side_king_answers, ())
        self.assertEqual(c.queen_no_king_answers, ('5N',))

        d = queen_answer_geometry('D', '0/3')
        self.assertEqual((d.queen_ask, d.no_queen), ('5H', '6D'))
        self.assertEqual(d.side_king_answers, ('6C',))
        self.assertEqual(d.queen_no_king_answers, ('5N',))

        h_14 = queen_answer_geometry('H', '1/4')
        self.assertEqual((h_14.queen_ask, h_14.no_queen), ('5D', '5H'))
        self.assertEqual(h_14.queen_no_king_answers, ('6H', '5N'))

        h_03 = queen_answer_geometry('H', '0/3')
        self.assertEqual((h_03.queen_ask, h_03.no_queen), ('5S', '6H'))
        self.assertEqual(h_03.side_king_answers, ('6C', '6D'))
        self.assertEqual(h_03.queen_no_king_answers, ('5N',))

        s = queen_answer_geometry('S', '1/4')
        self.assertEqual((s.queen_ask, s.no_queen), ('5D', '5S'))
        self.assertEqual(s.side_king_answers, ('6C', '6D', '6H'))
        self.assertEqual(s.queen_no_king_answers, ('6S', '5N'))

    def test_five_spade_relay_status(self):
        table = {
            ('C', '5C'): RELAY_USUALLY_UNNECESSARY,
            ('C', '5D'): RELAY_AVAILABLE,
            ('C', '5H'): RELAY_AVAILABLE,
            ('C', '5S'): RELAY_UNAVAILABLE,
            ('D', '5C'): RELAY_USUALLY_UNNECESSARY,
            ('D', '5D'): RELAY_USUALLY_UNNECESSARY,
            ('D', '5H'): RELAY_AVAILABLE,
            ('D', '5S'): RELAY_UNAVAILABLE,
            ('H', '5C'): RELAY_USUALLY_UNNECESSARY,
            ('H', '5D'): RELAY_UNAVAILABLE,
            ('H', '5H'): RELAY_USUALLY_UNNECESSARY,
            ('H', '5S'): RELAY_UNAVAILABLE,
            ('S', '5C'): RELAY_UNAVAILABLE,
            ('S', '5D'): RELAY_UNAVAILABLE,
            ('S', '5H'): RELAY_UNAVAILABLE,
            ('S', '5S'): RELAY_UNAVAILABLE,
        }
        five_trump_available = {
            ('C', '5C'): True,
            ('C', '5D'): False,
            ('C', '5H'): False,
            ('C', '5S'): False,
            ('D', '5C'): True,
            ('D', '5D'): True,
            ('D', '5H'): False,
            ('D', '5S'): False,
            ('H', '5C'): True,
            ('H', '5D'): True,
            ('H', '5H'): True,
            ('H', '5S'): False,
            ('S', '5C'): True,
            ('S', '5D'): True,
            ('S', '5H'): True,
            ('S', '5S'): True,
        }
        for (trump, answer), expected in table.items():
            with self.subTest(trump=trump, answer=answer):
                self.assertEqual(
                    five_spade_relay_status(
                        answer, trump, five_trump_available[(trump, answer)]),
                    expected)

    def test_queen_answer_call_uses_the_nearest_available_fact(self):
        no_queen = Hand.parse('SA2HAJ9876D432CK2')
        club_king = Hand.parse('SA2HQJ9876D432CK2')
        diamond_king = Hand.parse('SA2HQJ9876DK32C42')
        both_kings = Hand.parse('SA2HQJ9876DK32CK2')
        no_side_king = Hand.parse('SA2HQJ9876D432C43')

        self.assertEqual(queen_answer_call(no_queen, 'H', '1/4'), '5H')
        self.assertEqual(queen_answer_call(club_king, 'H', '1/4'), '6C')
        self.assertEqual(queen_answer_call(diamond_king, 'H', '1/4'), '6D')
        self.assertEqual(queen_answer_call(both_kings, 'H', '1/4'), '6C')
        self.assertEqual(queen_answer_call(no_side_king, 'H', '1/4'), '6H')
        self.assertEqual(
            queen_answer_call(no_side_king, 'H', '1/4', high=True), '5N')

    def test_queen_answer_without_space_for_side_kings(self):
        with_queen = Hand.parse('SA2HQJ9876D432CQ2')
        self.assertEqual(queen_answer_call(with_queen, 'C', '1/4'), '5N')
        self.assertEqual(
            queen_answer_facts('5N', 'C', '1/4'),
            {'trump_queen': True, 'side_king': None,
             'queen_answer_category': 'queen_no_side_king'})

    def test_queen_answer_facts(self):
        self.assertEqual(
            queen_answer_facts('5H', 'H', '1/4'),
            {'trump_queen': False, 'side_king': None,
             'queen_answer_category': 'no_queen'})
        self.assertEqual(
            queen_answer_facts('6C', 'H', '1/4'),
            {'trump_queen': True, 'side_king': 'C',
             'queen_answer_category': 'queen_side_king'})
        self.assertEqual(
            queen_answer_facts('5N', 'H', '1/4'),
            {'trump_queen': True, 'side_king': None,
             'queen_answer_category': 'queen_no_side_king'})
        self.assertIsNone(queen_answer_facts('7H', 'H', '1/4'))


if __name__ == '__main__':
    unittest.main()
