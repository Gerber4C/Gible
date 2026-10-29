from dataclasses import FrozenInstanceError, fields
from pathlib import Path
import subprocess
import sys
import unittest

from engine.cards import Hand
from engine.zar import ZarEvaluation, ZarFitContext, evaluate_zar


class ZarEvaluationTests(unittest.TestCase):
    def test_module_imports_from_repository_root(self):
        repository_root = Path(__file__).resolve().parents[2]

        result = subprocess.run(
            [sys.executable, "-c", "import backend.engine.zar"],
            cwd=repository_root,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_evaluates_base_zar_points(self):
        result = evaluate_zar(Hand.parse("SAJ975HK864DQ32C4"))

        self.assertEqual(
            result,
            ZarEvaluation(
                version="conservative",
                hcp=10,
                controls=3,
                shape_points=13,
                base_points=26,
                primary_fit_points=0,
                secondary_fit_points=0,
                total_points=26,
            ),
        )

    def test_shape_points_for_representative_distributions(self):
        cases = {
            "SXXXXHXXXDXXXCXXX": 8,
            "SXXXXHXXXXDXXXCXX": 10,
            "SXXXXXHXXXDXXXCXX": 11,
            "SXXXXXHXXXXDXXCXX": 12,
            "SXXXXXHXXXXDXXXCX": 13,
            "SAKQJT98765432H-D-C-": 26,
        }

        for compact_hand, expected_shape in cases.items():
            with self.subTest(compact_hand=compact_hand):
                self.assertEqual(
                    evaluate_zar(Hand.parse(compact_hand)).shape_points,
                    expected_shape,
                )

    def test_suit_permutations_do_not_change_base_evaluation(self):
        hands = (
            "SAJ975HK864DQ32C4",
            "SK864HAJ975D4CQ32",
            "SQ32H4DAJ975CK864",
            "S4HQ32DK864CAJ975",
        )

        evaluations = [evaluate_zar(Hand.parse(compact_hand)) for compact_hand in hands]

        for evaluation in evaluations[1:]:
            self.assertEqual(evaluation, evaluations[0])

    def test_controls_weight_aces_twice_and_kings_once(self):
        self.assertEqual(
            evaluate_zar(Hand.parse("SA432HA432D432C32")).controls,
            4,
        )
        self.assertEqual(
            evaluate_zar(Hand.parse("SK432HK432D432C32")).controls,
            2,
        )

    def test_public_dataclasses_have_ordered_fields_and_are_frozen(self):
        self.assertEqual(
            [field.name for field in fields(ZarEvaluation)],
            [
                "version",
                "hcp",
                "controls",
                "shape_points",
                "base_points",
                "primary_fit_points",
                "secondary_fit_points",
                "total_points",
            ],
        )
        self.assertEqual(
            [field.name for field in fields(ZarFitContext)],
            [
                "trump_suit",
                "combined_trumps",
                "secondary_suit",
                "combined_secondary",
            ],
        )

        evaluation = ZarEvaluation("conservative", 0, 0, 0, 0, 0, 0, 0)
        fit = ZarFitContext("spades", 8)
        with self.assertRaises(FrozenInstanceError):
            evaluation.total_points = 1
        with self.assertRaises(FrozenInstanceError):
            fit.combined_trumps = 9

    def test_fit_evaluation_is_deferred(self):
        hand = Hand.parse("SAJ975HK864DQ32C4")

        with self.assertRaises(NotImplementedError):
            evaluate_zar(hand, ZarFitContext("spades", 9))


if __name__ == "__main__":
    unittest.main()
