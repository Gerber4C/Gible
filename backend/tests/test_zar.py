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


class ZarPrimaryFitTests(unittest.TestCase):
    def test_primary_fit_points_scale_with_extra_trumps_and_side_shortness(self):
        cases = (
            ("SAKQ2H8765432D32C-", 8, 0),
            ("SAKQ2H8765432D32C-", 9, 2),
            ("SAKQ2H8765432D32C-", 10, 4),
            ("SAKQ2H876543D32C4", 9, 1),
            ("SAKQ2H876543D32C4", 10, 2),
            ("SAKQ2H8765D432C32", 9, 0),
            ("SAKQ2H8765D432C32", 10, 0),
        )

        for compact_hand, combined_trumps, expected_points in cases:
            with self.subTest(
                compact_hand=compact_hand,
                combined_trumps=combined_trumps,
            ):
                result = evaluate_zar(
                    Hand.parse(compact_hand),
                    ZarFitContext("H", combined_trumps),
                )
                self.assertEqual(result.primary_fit_points, expected_points)
                self.assertEqual(result.secondary_fit_points, 0)
                self.assertEqual(
                    result.total_points,
                    result.base_points
                    + result.primary_fit_points
                    + result.secondary_fit_points,
                )

    def test_primary_fit_shortness_excludes_trump_suit(self):
        hand = Hand.parse("S2HAKQJ98D432C543")

        self.assertEqual(
            tuple(
                hand.length(suit)
                for suit in ("spades", "hearts", "diamonds", "clubs")
            ),
            (1, 6, 3, 3),
        )
        result = evaluate_zar(hand, ZarFitContext("spades", 9))

        self.assertEqual(result.primary_fit_points, 0)

    def test_primary_fit_rejects_unknown_trump(self):
        with self.assertRaisesRegex(ValueError, "Unknown suit"):
            evaluate_zar(
                Hand.parse("SAKQ2H8765D432C32"),
                ZarFitContext("stars", 9),
            )

    def test_primary_fit_rejects_invalid_combined_trump_counts(self):
        hand = Hand.parse("SAKQ2H8765D432C32")

        for combined_trumps in (True, 8.5, -1, 14, 7):
            with self.subTest(combined_trumps=combined_trumps):
                with self.assertRaisesRegex(ValueError, "combined_trumps"):
                    evaluate_zar(
                        hand,
                        ZarFitContext("hearts", combined_trumps),
                    )

    def test_primary_fit_rejects_count_shorter_than_own_trumps(self):
        with self.assertRaisesRegex(ValueError, "own trump"):
            evaluate_zar(
                Hand.parse("SAHQJT987654D32C2"),
                ZarFitContext("hearts", 8),
            )


class ZarSecondaryFitTests(unittest.TestCase):
    def test_absent_secondary_fields_add_no_secondary_points(self):
        result = evaluate_zar(
            Hand.parse("SAKQ2H8765432D32C-"),
            ZarFitContext("hearts", 9),
        )

        self.assertEqual(result.primary_fit_points, 2)
        self.assertEqual(result.secondary_fit_points, 0)

    def test_secondary_fit_points_depend_on_combined_length(self):
        cases = (
            ("SAKQ2H876D432C543", 8, 0),
            ("SAKQ2H876D432C543", 9, 1),
            ("SAKQ2H876D432C543", 10, 2),
            ("SAKQ2H87654D32C43", 13, 2),
        )

        for compact_hand, combined_secondary, expected_points in cases:
            with self.subTest(combined_secondary=combined_secondary):
                result = evaluate_zar(
                    Hand.parse(compact_hand),
                    ZarFitContext("spades", 9, "H", combined_secondary),
                )
                self.assertEqual(result.secondary_fit_points, expected_points)
                self.assertEqual(
                    result.total_points,
                    result.base_points
                    + result.primary_fit_points
                    + result.secondary_fit_points,
                )

    def test_secondary_fields_must_be_supplied_together(self):
        hand = Hand.parse("SAKQ2H876D432C543")

        for secondary_suit, combined_secondary in (("hearts", None), (None, 8)):
            with self.subTest(
                secondary_suit=secondary_suit,
                combined_secondary=combined_secondary,
            ):
                with self.assertRaisesRegex(ValueError, "supplied together"):
                    evaluate_zar(
                        hand,
                        ZarFitContext(
                            "spades",
                            9,
                            secondary_suit,
                            combined_secondary,
                        ),
                    )

    def test_secondary_suit_must_be_known_and_differ_from_trump(self):
        hand = Hand.parse("SAKQ2H876D432C543")

        with self.assertRaisesRegex(ValueError, "Unknown suit"):
            evaluate_zar(
                hand,
                ZarFitContext("spades", 9, "stars", 8),
            )
        with self.assertRaisesRegex(ValueError, "differ"):
            evaluate_zar(
                hand,
                ZarFitContext("S", 9, "spades", 8),
            )

    def test_secondary_fit_rejects_invalid_combined_counts(self):
        hand = Hand.parse("SAKQ2H876D432C543")

        for combined_secondary in (True, 7, 14):
            with self.subTest(combined_secondary=combined_secondary):
                with self.assertRaisesRegex(ValueError, "combined_secondary"):
                    evaluate_zar(
                        hand,
                        ZarFitContext(
                            "spades",
                            9,
                            "hearts",
                            combined_secondary,
                        ),
                    )

    def test_secondary_fit_rejects_count_shorter_than_own_holding(self):
        with self.assertRaisesRegex(ValueError, "own secondary"):
            evaluate_zar(
                Hand.parse("SAKQJT9876H32D2C2"),
                ZarFitContext("hearts", 8, "spades", 8),
            )

    def test_secondary_fit_requires_three_cards_in_own_hand(self):
        with self.assertRaisesRegex(ValueError, "own secondary"):
            evaluate_zar(
                Hand.parse("SAKQ2H8765D432C32"),
                ZarFitContext("spades", 9, "clubs", 8),
            )

    def test_secondary_fit_requires_three_cards_in_partner_hand(self):
        with self.assertRaisesRegex(ValueError, "partner secondary"):
            evaluate_zar(
                Hand.parse("SAKQJT98H876D32C4"),
                ZarFitContext("hearts", 8, "spades", 8),
            )

    def test_implied_partner_lengths_must_fit_in_thirteen_cards(self):
        with self.assertRaisesRegex(ValueError, "implied partner.*13 cards"):
            evaluate_zar(
                Hand.parse("SAKQ2H876D432C543"),
                ZarFitContext("spades", 13, "hearts", 10),
            )


if __name__ == "__main__":
    unittest.main()
