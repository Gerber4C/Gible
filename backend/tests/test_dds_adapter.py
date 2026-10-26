"""Contract tests for the optional, analysis-only DDS bridge."""

import importlib
import unittest
from unittest.mock import patch

from engine.cards import Hand


RANKS = 'AKQJT98765432'
COMPLETE_DEAL = {
    'w': Hand('', '', '', RANKS),
    's': Hand('', '', RANKS, ''),
    'e': Hand('', RANKS, '', ''),
    'n': Hand(RANKS, '', '', ''),
}
PBN = f'N:{RANKS}... .{RANKS}.. ..{RANKS}. ...{RANKS}'


class FakeDDS:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def calc_all_tables_pbn(self, deals_pbn, mode=-1):
        self.calls.append((deals_pbn, mode))
        return self.result


class DDSAdapterTests(unittest.TestCase):
    def adapter(self):
        return importlib.import_module('engine.dds_adapter')

    def test_pbn_uses_north_east_south_west_and_spades_hearts_diamonds_clubs(self):
        self.assertEqual(self.adapter().deal_to_pbn(COMPLETE_DEAL), PBN)

    def test_compact_hands_are_accepted_and_ranks_are_canonicalized(self):
        compact = {
            seat: ''.join(suit + (hand.holding(suit)[::-1] or '-')
                          for suit in 'SHDC')
            for seat, hand in COMPLETE_DEAL.items()
        }
        self.assertEqual(self.adapter().deal_to_pbn(compact), PBN)

    def test_table_maps_official_strain_and_seat_order(self):
        matrix = [[(row * 4 + column) % 14 for column in range(4)] for row in range(5)]
        fake = FakeDDS({'no_of_boards': 1, 'tables': [{'res_table': matrix}], 'par_results': []})

        table = self.adapter().calculate_double_dummy_table(COMPLETE_DEAL, dds_module=fake)

        self.assertEqual(fake.calls, [([PBN], -1)])
        self.assertEqual(table, {
            strain: {seat: matrix[row][column] for column, seat in enumerate('nesw')}
            for row, strain in enumerate(('S', 'H', 'D', 'C', 'NT'))
        })

    def test_rejects_missing_seat_and_duplicate_card(self):
        adapter = self.adapter()
        with self.assertRaisesRegex(ValueError, 'exactly.*n.*e.*s.*w'):
            adapter.deal_to_pbn({'n': COMPLETE_DEAL['n']})
        duplicate = dict(COMPLETE_DEAL)
        duplicate['e'] = Hand(RANKS, '', '', '')
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            adapter.deal_to_pbn(duplicate)

    def test_rejects_unknown_card_and_incomplete_hand(self):
        adapter = self.adapter()
        unknown = dict(COMPLETE_DEAL)
        unknown['n'] = Hand('AKQJT9876543X', '', '', '')
        with self.assertRaisesRegex(ValueError, 'unknown|invalid'):
            adapter.deal_to_pbn(unknown)
        short = dict(COMPLETE_DEAL)
        short['n'] = Hand(RANKS[:-1], '', '', '')
        with self.assertRaisesRegex(ValueError, '13'):
            adapter.deal_to_pbn(short)

    def test_missing_package_has_clear_error(self):
        adapter = self.adapter()
        with patch.object(adapter.importlib, 'import_module', side_effect=ModuleNotFoundError("No module named 'dds3'")):
            with self.assertRaisesRegex(adapter.DDSUnavailableError, 'dds3.*Git'):
                adapter.calculate_double_dummy_table(COMPLETE_DEAL)

    def test_malformed_dds_result_is_reported(self):
        fake = FakeDDS({'no_of_boards': 1, 'tables': [{'res_table': [[0] * 4]}]})
        with self.assertRaisesRegex(RuntimeError, '5x4'):
            self.adapter().calculate_double_dummy_table(COMPLETE_DEAL, dds_module=fake)


if __name__ == '__main__':
    unittest.main()
