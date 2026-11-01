import unittest

from engine.keycard_queen_table import (
    RELAY_AVAILABLE, RELAY_UNAVAILABLE, RELAY_USUALLY_UNNECESSARY,
    five_spade_relay_status, queen_answer_geometry, queen_ask,
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


if __name__ == '__main__':
    unittest.main()
