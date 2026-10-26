import importlib.util
import unittest

from engine.cards import Hand
from engine.dds_adapter import calculate_available_table, calculate_endplay_table


RANKS = 'AKQJT98765432'
SIMPLE_DEAL = {
    'n': Hand(RANKS, '', '', ''),
    'e': Hand('', RANKS, '', ''),
    's': Hand('', '', RANKS, ''),
    'w': Hand('', '', '', RANKS),
}


@unittest.skipUnless(importlib.util.find_spec('endplay'), 'optional endplay is not installed')
class EndplayAdapterTests(unittest.TestCase):
    def test_known_deal_real_double_dummy_table(self):
        table = calculate_endplay_table(SIMPLE_DEAL)
        self.assertEqual([table['S'][seat] for seat in 'nesw'], [13, 0, 13, 0])
        self.assertEqual([table['H'][seat] for seat in 'nesw'], [0, 13, 0, 13])
        self.assertEqual([table['D'][seat] for seat in 'nesw'], [13, 0, 13, 0])
        self.assertEqual([table['C'][seat] for seat in 'nesw'], [0, 13, 0, 13])
        self.assertEqual([table['NT'][seat] for seat in 'nesw'], [0, 0, 0, 0])

    def test_available_solver_is_real_and_has_same_contract_coordinates(self):
        table = calculate_available_table(SIMPLE_DEAL)
        self.assertEqual(table['S']['n'], 13)
        self.assertEqual(table['H']['e'], 13)


if __name__ == '__main__':
    unittest.main()
