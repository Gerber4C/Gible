import math
import unittest

from engine.outcome_metrics import (
    RULE_ID,
    board_result,
    classify_rates,
    game_success_ratio,
    reclassify_analysis,
)


class OutcomeMetricTests(unittest.TestCase):
    @staticmethod
    def table(*, spades=6, hearts=6, diamonds=6, clubs=6, nt=6):
        return {
            'S': {'n': spades, 's': spades},
            'H': {'n': hearts, 's': hearts},
            'D': {'n': diamonds, 's': diamonds},
            'C': {'n': clubs, 's': clubs},
            'NT': {'n': nt, 's': nt},
        }

    @classmethod
    def boards(cls, *, chosen, nt, total):
        return ([cls.table(spades=10, nt=9)] * min(chosen, nt)
                + [cls.table(spades=10)] * max(0, chosen - nt)
                + [cls.table(nt=9)] * max(0, nt - chosen)
                + [cls.table()] * (total - max(chosen, nt)))

    def test_wrong_uses_success_probability_ratio(self):
        ratio, alternatives = game_success_ratio(
            '4S', 'n', self.boards(chosen=4, nt=6, total=10))

        self.assertAlmostEqual(ratio, 2 / 3)
        self.assertEqual(alternatives['3NT'], .6)

    def test_best_other_at_floor_suppresses_wrong(self):
        ratio, alternatives = game_success_ratio(
            '4S', 'n', self.boards(chosen=3, nt=4, total=10))

        self.assertIsNone(ratio)
        self.assertEqual(alternatives['3NT'], .4)

    def test_success_ratio_can_be_finite_and_greater_than_one(self):
        ratio, alternatives = game_success_ratio(
            '4S', 'n', self.boards(chosen=10, nt=5, total=10))

        self.assertEqual(ratio, 2.0)
        self.assertTrue(math.isfinite(ratio))
        self.assertEqual(alternatives['3NT'], .5)

    def test_ratio_is_unavailable_without_selected_game_boards_or_positive_other(self):
        self.assertEqual(game_success_ratio('2S', 'n', [self.table()]),
                         (None, {}))
        self.assertEqual(game_success_ratio('4S', 'n', []), (None, {}))
        ratio, alternatives = game_success_ratio(
            '4S', 'n', [self.table(spades=10)])
        self.assertIsNone(ratio)
        self.assertTrue(all(rate == 0 for rate in alternatives.values()))

    def test_set_is_strictly_above_sixty_percent(self):
        self.assertNotIn('contract_failure', classify_rates(
            '4S', {'contract_failure': .6, 'wrong_game': None}, {}))
        self.assertIn('contract_failure', classify_rates(
            '4S', {'contract_failure': .61, 'wrong_game': None}, {}))

    def test_wrong_ratio_and_best_other_boundaries_are_strict(self):
        self.assertNotIn('wrong_game', classify_rates(
            '4S', {'contract_failure': .2, 'wrong_game': .8}, {'3NT': .5}))
        self.assertNotIn('wrong_game', classify_rates(
            '4S', {'contract_failure': .2, 'wrong_game': .5}, {'3NT': .4}))
        self.assertIn('wrong_game', classify_rates(
            '4S', {'contract_failure': .2, 'wrong_game': .79}, {'3NT': .41}))

    def test_each_missed_threshold_is_strict_and_recomputed(self):
        equal_rates = {
            'contract_failure': 0,
            'wrong_game': None,
            'missed_game': .30,
            'missed_small_slam': .30,
            'missed_grand_slam': .30,
        }
        high_rates = {**equal_rates, 'missed_game': .31,
                      'missed_small_slam': .31, 'missed_grand_slam': .31}

        self.assertEqual(classify_rates('2S', equal_rates, {}), [])
        self.assertEqual(classify_rates('2S', high_rates, {}), [
            'missed_game', 'missed_small_slam', 'missed_grand_slam'])

    def test_new_classification_replaces_stale_computed_flags_but_keeps_other_flags(self):
        flags = classify_rates(
            '7NT',
            {'contract_failure': .2, 'wrong_game': None,
             'missed_game': 1, 'missed_small_slam': 1,
             'missed_grand_slam': 1},
            {},
            existing_flags=('manual_review', 'contract_failure', 'missed_game'),
        )

        self.assertEqual(flags, ['manual_review'])

    def test_legacy_reclassification_preserves_missed_and_replaces_set_wrong(self):
        result = reclassify_analysis('4S', {
            'flags': ['missed_game', 'contract_failure', 'wrong_game', 'manual_review'],
            'rates': {'contract_failure': .2, 'wrong_game': float('inf')},
            'alternative_game_rates': {'3NT': .5},
        })

        self.assertEqual(result['rates']['wrong_game'], 1.6)
        self.assertEqual(result['flags'], ['missed_game', 'manual_review'])

    def test_invalid_probability_and_infinite_ratio_do_not_warn(self):
        flags = classify_rates(
            '4S',
            {'contract_failure': float('inf'), 'wrong_game': float('inf')},
            {'3NT': float('inf')},
        )
        result = reclassify_analysis('4S', {
            'flags': ['contract_failure', 'wrong_game'],
            'rates': {'contract_failure': float('inf')},
            'alternative_game_rates': {'3NT': .9},
        })

        self.assertEqual(flags, [])
        self.assertIsNone(result['rates']['contract_failure'])
        self.assertIsNone(result['rates']['wrong_game'])
        self.assertEqual(result['flags'], [])

    def test_matrix_result_keeps_outcome_and_highest_missed_target(self):
        table = self.table(spades=7, nt=9, hearts=12)

        self.assertEqual(board_result('2S', 'n', table), {
            'outcome': 'SET', 'lose': True, 'missed_target': 'small slam',
        })
        self.assertEqual(board_result('2S', 'n', self.table(spades=8)), {
            'outcome': 'MAKE', 'lose': False, 'missed_target': None,
        })

    def test_rule_identifier_is_stable(self):
        self.assertEqual(
            RULE_ID,
            'success_probability_ratio_0.8_best_above_0.4_set_above_0.6',
        )


if __name__ == '__main__':
    unittest.main()
