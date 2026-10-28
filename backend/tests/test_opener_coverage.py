import dataclasses
import hashlib
import time
import unittest
from collections import Counter
from unittest.mock import patch

from engine.opener_coverage import (
    OpenerAllocationError,
    OpenerStratum,
    _hcp_feasible,
    allocate_opener_strata,
    normal_named_shapes,
    required_opener_strata,
    rotate_responder_shape,
    stratum_key,
    validate_cell_identity,
    validate_explicit_coverage_cell,
)


COVERAGE_SHAPES = (
    (4, 4, 3, 2), (5, 3, 3, 2), (5, 4, 3, 1), (5, 4, 2, 2),
    (4, 3, 3, 3), (6, 3, 2, 2), (6, 4, 2, 1), (6, 3, 3, 1),
    (5, 5, 2, 1), (4, 4, 4, 1), (7, 3, 2, 1), (6, 4, 3, 0),
    (5, 4, 4, 0), (5, 5, 3, 0), (6, 5, 1, 1), (6, 5, 2, 0),
    (7, 2, 2, 2), (7, 4, 1, 1), (7, 4, 2, 0), (7, 3, 3, 0),
    (8, 2, 2, 1), (8, 3, 1, 1), (8, 3, 2, 0),
)


def default_cells():
    return [
        {'target_hcp': hcp, 'base_shape_index': index, 'base_shape': shape}
        for hcp in range(23)
        for index, shape in enumerate(COVERAGE_SHAPES)
    ]


class OpenerShapeTests(unittest.TestCase):
    def test_stratum_is_immutable_ordered_and_has_a_stable_key(self):
        lower = OpenerStratum((4, 3, 3, 3), 'normal')
        higher = OpenerStratum((5, 3, 3, 2), 'normal')

        self.assertLess(lower, higher)
        self.assertEqual(stratum_key(lower), 'normal:4-3-3-3')
        with self.assertRaises(dataclasses.FrozenInstanceError):
            lower.mode = 'soft_18'

    def test_normal_shapes_have_exact_filtered_family_counts(self):
        shapes = normal_named_shapes()

        self.assertEqual(len(shapes), 68)
        self.assertEqual(len(set(shapes)), 68)
        self.assertEqual(Counter(tuple(sorted(shape, reverse=True))
                                 for shape in shapes), {
            (4, 3, 3, 3): 4,
            (4, 4, 3, 2): 12,
            (5, 3, 3, 2): 12,
            (6, 3, 2, 2): 6,
            (5, 4, 2, 2): 10,
            (4, 4, 4, 1): 4,
            (5, 4, 3, 1): 20,
        })
        for spades, hearts, diamonds, clubs in shapes:
            self.assertEqual(spades + hearts + diamonds + clubs, 13)
            self.assertLess(spades, 6)
            self.assertLess(hearts, 6)
            self.assertFalse(spades >= 5 and hearts >= 4)
            self.assertFalse(hearts >= 5 and spades >= 4)

    def test_required_strata_have_stable_mode_quotas(self):
        first = required_opener_strata()
        second = required_opener_strata()

        self.assertEqual(first, second)
        self.assertEqual(len(first), 92)
        self.assertEqual(Counter(item.mode for item in first), {
            'normal': 68, 'upgrade_14': 12, 'soft_18': 12,
        })
        self.assertEqual(
            {item.shape for item in first if item.mode == 'upgrade_14'},
            {shape for shape in normal_named_shapes()
             if sorted(shape, reverse=True) == [5, 3, 3, 2]},
        )
        self.assertEqual(
            {item.shape for item in first if item.mode == 'soft_18'},
            {shape for shape in normal_named_shapes()
             if sorted(shape, reverse=True) == [4, 4, 3, 2]},
        )

    def test_required_strata_follow_exact_integer_normalized_rank_merge(self):
        shapes = normal_named_shapes()
        normal = [OpenerStratum(shape, 'normal') for shape in shapes]
        upgrades = [OpenerStratum(shape, 'upgrade_14') for shape in shapes
                    if sorted(shape, reverse=True) == [5, 3, 3, 2]]
        soft = [OpenerStratum(shape, 'soft_18') for shape in shapes
                if sorted(shape, reverse=True) == [4, 4, 3, 2]]
        exceptional = [item for pair in zip(upgrades, soft) for item in pair]
        expected = []
        normal_index = exceptional_index = 0
        while normal_index < len(normal) and exceptional_index < len(exceptional):
            normal_rank = (2 * normal_index + 1) * len(exceptional)
            exceptional_rank = (2 * exceptional_index + 1) * len(normal)
            if normal_rank <= exceptional_rank:
                expected.append(normal[normal_index])
                normal_index += 1
            else:
                expected.append(exceptional[exceptional_index])
                exceptional_index += 1
        expected.extend(normal[normal_index:])
        expected.extend(exceptional[exceptional_index:])

        self.assertEqual(required_opener_strata(), tuple(expected))

    def test_responder_shape_uses_the_shared_left_rotation_rule(self):
        shape = (8, 3, 2, 0)
        self.assertEqual(rotate_responder_shape(shape, 10, 1), (0, 8, 3, 2))
        self.assertEqual(rotate_responder_shape(shape, 11, 1), shape)


class CoverageCellValidationTests(unittest.TestCase):
    def test_identity_accepts_exactly_two_non_boolean_integer_fields(self):
        cell = {'target_hcp': 10, 'base_shape_index': 4}
        self.assertEqual(validate_cell_identity(cell), cell)

        bad_values = (
            ({'target_hcp': True, 'base_shape_index': 4}, 'target_hcp'),
            ({'target_hcp': 10}, 'base_shape_index'),
            ({**cell, 'base_shape': [4, 3, 3, 3]}, 'unknown fields'),
            ({**cell, 7: 'unexpected'}, 'unknown fields'),
        )
        for bad, field in bad_values:
            with self.subTest(bad=bad):
                with self.assertRaisesRegex(ValueError, field):
                    validate_cell_identity(bad)

    def test_explicit_cell_validates_full_metadata_and_siblings(self):
        cell = {
            'target_hcp': 10,
            'base_shape_index': 4,
            'base_shape': [4, 3, 3, 3],
            'pair_slot': 0,
            'opener_shape': [5, 3, 3, 2],
            'opener_mode': 'normal',
        }
        sibling = {**cell, 'pair_slot': 1}

        validated = validate_explicit_coverage_cell(cell, siblings=[sibling])
        self.assertEqual(validated['base_shape'], (4, 3, 3, 3))
        self.assertEqual(validated['opener_shape'], (5, 3, 3, 2))

        bad_cells = (
            ({key: value for key, value in cell.items() if key != 'pair_slot'},
             'pair_slot'),
            ({**cell, 'pair_slot': False}, 'pair_slot'),
            ({**cell, 'opener_mode': 'rare'}, 'opener_mode'),
            ({**cell, 'opener_mode': ['normal']}, 'opener_mode'),
            ({**cell, 'opener_shape': [5, 3, 3]}, 'opener_shape'),
            ({**cell, 'base_shape': [4, 3, 3, 2]}, 'base_shape'),
        )
        for bad, field in bad_cells:
            with self.subTest(field=field):
                with self.assertRaisesRegex(ValueError, field):
                    validate_explicit_coverage_cell(bad)

        inconsistent = {**sibling, 'opener_mode': 'upgrade_14'}
        with self.assertRaisesRegex(ValueError, 'opener_mode'):
            validate_explicit_coverage_cell(cell, siblings=[inconsistent])


class OpenerAllocationTests(unittest.TestCase):
    @staticmethod
    def counts(allocation):
        return Counter(allocation['assignments'].values())

    def test_quota_boundaries_report_completeness_and_omissions(self):
        cells = default_cells()
        for available, expected_omitted, expected_complete in (
                (24, 68, False), (91, 1, False), (92, 0, True)):
            with self.subTest(available=available):
                allocation = allocate_opener_strata(cells[:available])
                self.assertEqual(allocation['available_cells'], available)
                self.assertEqual(allocation['required_cells'], 92)
                self.assertEqual(allocation['complete'], expected_complete)
                self.assertEqual(len(allocation['assignments']), available)
                self.assertEqual(len(allocation['ungenerated_strata']),
                                 expected_omitted)
                self.assertTrue(all(
                    item['cell'] is None
                    and item['reason'] == 'insufficient_cells'
                    for item in allocation['ungenerated_strata']))

        self.assertEqual(
            set(allocate_opener_strata(cells[:92])['assignments'].values()),
            set(required_opener_strata()),
        )

    def test_default_grid_preserves_exceptional_and_normal_quotas(self):
        started = time.perf_counter()
        allocation = allocate_opener_strata(default_cells())
        elapsed = time.perf_counter() - started
        counts = self.counts(allocation)

        self.assertLess(elapsed, 1.0)
        self.assertTrue(allocation['complete'])
        exceptional_counts = [count for stratum, count in counts.items()
                              if stratum.mode != 'normal']
        normal_counts = [count for stratum, count in counts.items()
                         if stratum.mode == 'normal']
        self.assertEqual(exceptional_counts, [1] * 24)
        self.assertEqual(Counter(normal_counts), {7: 39, 8: 29})

    def test_allocator_reassigns_hcp_impossible_honor_singleton_edge(self):
        allocation = allocate_opener_strata(default_cells())
        impossible = OpenerStratum((1, 4, 5, 3), 'normal')

        self.assertNotEqual(
            allocation['assignments'][(22, 13)],
            impossible,
        )
        self.assertFalse(_hcp_feasible(impossible, (0, 5, 5, 3), 22))

    def test_allocator_reassigns_hcp_impossible_soft_18_doubleton_edge(self):
        allocation = allocate_opener_strata(default_cells())
        impossible = OpenerStratum((4, 3, 4, 2), 'soft_18')

        self.assertNotEqual(
            allocation['assignments'][(16, 12)],
            impossible,
        )
        self.assertFalse(_hcp_feasible(impossible, (5, 4, 4, 0), 16))

    def test_mapping_is_independent_of_input_and_execution_order(self):
        cells = default_cells()[:120]
        expected = allocate_opener_strata(cells)['assignments']

        self.assertEqual(
            allocate_opener_strata(list(reversed(cells)))['assignments'],
            expected,
        )
        odds_then_evens = cells[1::2] + cells[::2]
        self.assertEqual(
            allocate_opener_strata(odds_then_evens)['assignments'], expected)

    def test_every_default_assignment_is_suit_and_hcp_compatible(self):
        cells = default_cells()
        allocation = allocate_opener_strata(cells)
        by_identity = {
            (cell['target_hcp'], cell['base_shape_index']): cell
            for cell in cells
        }

        for identity, stratum in allocation['assignments'].items():
            cell = by_identity[identity]
            south_shape = rotate_responder_shape(
                cell['base_shape'], cell['target_hcp'],
                cell['base_shape_index'])
            self.assertTrue(all(north + south <= 13 for north, south in zip(
                stratum.shape, south_shape)))
            north_min = {'normal': 15, 'upgrade_14': 14,
                         'soft_18': 18}[stratum.mode]
            self.assertLessEqual(north_min + cell['target_hcp'], 40)
            self.assertTrue(_hcp_feasible(
                stratum, south_shape, cell['target_hcp']))

    def test_impossible_matching_raises_typed_diagnostics(self):
        cell = {'target_hcp': 40, 'base_shape_index': 0,
                'base_shape': (13, 0, 0, 0)}
        with self.assertRaises(OpenerAllocationError) as caught:
            allocate_opener_strata([cell])

        self.assertEqual(caught.exception.available_cells, 1)
        self.assertEqual(caught.exception.required_cells, 92)
        self.assertEqual(len(caught.exception.unmatched_slots), 1)

    def test_matching_reassigns_an_earlier_slot_when_greedy_would_fail(self):
        cells = default_cells()[:3]
        identities = [(cell['target_hcp'], cell['base_shape_index'])
                      for cell in cells]
        stable_identities = sorted(
            identities,
            key=lambda identity: (
                hashlib.sha256(
                    f'north-stratum-v1:{identity[0]}:{identity[1]}'.encode(
                        'ascii')).digest(),
                identity,
            ),
        )
        first, second, third = stable_identities
        selected = required_opener_strata()[:3]
        by_key = {stratum_key(stratum): stratum for stratum in selected}
        first_key, second_key, third_key = sorted(by_key)
        edges = {
            first_key: {first, second},
            second_key: {first, third},
            third_key: {first, third},
        }

        def compatible(slot, cell):
            return cell.identity in edges[stratum_key(slot.stratum)]

        with patch('engine.opener_coverage._compatible', side_effect=compatible):
            allocation = allocate_opener_strata(cells)

        self.assertEqual(set(allocation['assignments'].values()), set(selected))
        self.assertEqual(allocation['assignments'][second], by_key[first_key])


if __name__ == '__main__':
    unittest.main()
