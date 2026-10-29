import unittest

from engine.cards import Hand


class HandQualityTests(unittest.TestCase):
    def assess(self, hand, **kwargs):
        # Deferred import makes the missing implementation a clear test failure.
        try:
            from engine.hand_quality import assess_quality
        except ImportError as exc:
            self.fail(f"Hand quality model has not been implemented: {exc}")
        return assess_quality(Hand.parse(hand), **kwargs)

    def test_shapely_description_proxy_preserves_real_hand(self):
        from engine.hand_quality import (shapely_combined_effective_points,
                                         shapely_description_proxy)
        hand = Hand.parse('S4HJ9752DAQ7432C8')
        proxy = shapely_description_proxy(hand, 'D')
        self.assertEqual(proxy['actual_length'], 6)
        self.assertEqual(proxy['described_length'], 5)
        self.assertEqual(proxy['effective_points'],
                         shapely_combined_effective_points(hand) + 2)
        self.assertEqual(hand.length('D'), 6)

    def test_minor_slam_interest_uses_shared_kr_threshold(self):
        from engine.hand_quality import MINOR_SLAM_KR, minor_slam_interest

        self.assertEqual(MINOR_SLAM_KR, 14.0)
        self.assertFalse(minor_slam_interest(Hand.parse('SKQ5H2DAJ954C8765')))
        self.assertTrue(minor_slam_interest(Hand.parse('SAK5H2DKQJ54C8765')))
        self.assertFalse(minor_slam_interest(Hand.parse('SKQ5H2D8765CAJ954')))
        self.assertTrue(minor_slam_interest(Hand.parse('SAK5H2D8765CKQJ54')))

    def test_equal_hcp_controls_and_long_honors_outperform_scattered_queens_jacks(self):
        strong_hand = "SAKxxx HKxx Dxx Cxxx"
        weak_hand = "SQJxx HQJx DQxx CQxx"
        self.assertEqual(Hand.parse(strong_hand).hcp, Hand.parse(weak_hand).hcp)
        strong, weak = self.assess(strong_hand), self.assess(weak_hand)
        self.assertGreater(strong["score"], weak["score"])
        self.assertTrue(strong["good"])
        self.assertFalse(weak["good"])

    def test_concentration_in_supported_suits_improves_equal_hcp_hand(self):
        concentrated = self.assess("SAKxx Hxxx Dxxx Cxxx")
        scattered = self.assess("SAxxx HKxx Dxxx Cxxx")
        self.assertGreater(concentrated["score"], scattered["score"])

    def test_short_isolated_queens_jacks_are_penalized(self):
        short = self.assess("SQ HJx Dxxxxx Cxxxxx")
        supported = self.assess("Sx Hxx DQxxxx CJxxxx")
        self.assertEqual(short["features"]["short_unsupported_honors"], 2)
        self.assertGreater(supported["score"], short["score"])

    def test_optional_context_changes_quality_but_never_pure_kr(self):
        hand = "SAQxxx HKxx Dxx Cxxx"
        neutral = self.assess(hand)
        partner = self.assess(hand, partner_suits=("S",), weights={"partner_honors": 0.5})
        opponent = self.assess(hand, opponent_suits=("S",), weights={"opponent_honors": -0.5})
        self.assertGreater(partner["score"], neutral["score"])
        self.assertLess(opponent["score"], neutral["score"])
        self.assertEqual(partner["kr_points"], neutral["kr_points"])
        self.assertEqual(opponent["kr_points"], neutral["kr_points"])
        self.assertEqual(self.assess(hand, partner_suits=("S",))["score"], neutral["score"])
        self.assertEqual(partner, self.assess(hand, partner_suits=("spades", "S"), weights={"partner_honors": 0.5}))

    def test_shortage_requires_trump_support_and_excludes_trump(self):
        hand = "SAxxxx HKxx DQxxx CJ"
        self.assertEqual(self.assess(hand)["features"]["fit_shortage"], 0)
        self.assertEqual(self.assess(hand, trump="C")["features"]["fit_shortage"], 0)
        supported = self.assess(hand, trump="S", weights={"fit_shortage": 0.5})
        self.assertEqual(supported["features"]["fit_shortage"], 2)
        self.assertGreater(supported["score"], self.assess(hand)["score"])
        self.assertEqual(supported["kr_points"], self.assess(hand)["kr_points"])

    def test_deterministic_complete_evidence_and_overrides_do_not_add_hcp(self):
        hand = "SAKxx Hxxx Dxxx Cxxx"
        result = self.assess(hand)
        self.assertEqual(result, self.assess(hand))
        self.assertEqual(result["model"], "kaplan_rubens")
        expected_features = {
            "control_balance", "honor_concentration", "long_suit_honors",
            "short_unsupported_honors", "partner_honors", "opponent_honors",
            "long_suit", "fit_shortage",
        }
        self.assertEqual(set(result["features"]), expected_features)
        self.assertTrue(all(isinstance(reason, str) for reason in result["reasons"]))
        self.assertEqual(result["score"], result["kr_delta"])
        self.assertAlmostEqual(result["score"], result["kr_points"] - Hand.parse(hand).hcp)
        boundary = self.assess(hand, weights={"threshold": result["score"]})
        self.assertTrue(boundary["good"])
        self.assertFalse(self.assess(hand, weights={"threshold": result["score"] + 0.05})["good"])

    def test_invalid_weights_raise_value_error(self):
        hand = "SAKxx Hxxx Dxxx Cxxx"
        for weights in (
            {"unknown": 1}, {"threshold": "1"}, {"partner_honors": None},
            {"threshold": float("nan")}, {"opponent_honors": float("inf")},
            {"fit_shortage": float("-inf")}, {"threshold": True}, [],
        ):
            with self.subTest(weights=weights):
                with self.assertRaises(ValueError):
                    self.assess(hand, weights=weights)

    def test_published_minimum_and_maximum(self):
        # Source: https://rpbridge.net/8j19.htm, minimum 4333 Yarborough
        # and maximum 37-HCP seven-notrump claimer.
        self.assertEqual(self.assess("S8765 H876 D876 C876")["kr_points"], -0.5)
        self.assertEqual(self.assess("SAKQJ HAKQ DAKQ CAKQ")["kr_points"], 35.6)

    def test_nine_card_suit_applies_all_three_length_corrections(self):
        # Steps 1-11: 7 + .5 + 1 + 1 + 1 = 10.5;
        # step 12: 9.45; steps 13,14,22: 5.25; sides 5; adjustment -1.
        result = self.assess("SAKT987654 H32 D2 C2")
        self.assertEqual(result["kr_points"], 18.7)
        steps = result["suit_evaluations"]["S"]["steps"]
        self.assertEqual([steps[str(n)] for n in (6, 7, 8)], [0, 0, 0])
        self.assertEqual([steps[str(n)] for n in (9, 10, 11)], [1, 1, 1])

    def test_guarded_and_singleton_honor_suit_values(self):
        # Independently calculated from steps 12-26 in the published table.
        expected = {
            "K": 2.8, "K2": 3.6, "Q": 2.2, "Q2": 1.65,
            "AQ": 5.7, "Q32": 1.35, "AQ2": 5.8,
            "AKJ": 7.9, "AJ": 5.25, "AJT": 5.3, "AT9": 4.75,
            "AKQ9": 9.8,
        }
        for holding, points in expected.items():
            with self.subTest(holding=holding):
                hand = f"S{holding} Hxxx Dxxx C{'x' * (7 - len(holding))}"
                result = self.assess(hand)
                self.assertEqual(result["suit_evaluations"]["S"]["points"], points)

    def test_step_eight_requires_four_cards_and_exactly_three_high_honors(self):
        for holding, expected in (("AKQ9", 0.5), ("AKQJ9", 0), ("AKQ98", 0), ("AKQ9xxx", 0)):
            with self.subTest(holding=holding):
                hand = f"S{holding} Hxx Dxx C{'x' * (9 - len(holding))}"
                steps = self.assess(hand)["suit_evaluations"]["S"]["steps"]
                self.assertEqual(steps["8"], expected)

    def test_scores_have_twentieth_point_precision_and_full_step_evidence(self):
        import random
        rng = random.Random(238)
        deck = [(suit, rank) for suit in "SHDC" for rank in "AKQJT98765432"]
        for _ in range(100):
            cards = rng.sample(deck, 13)
            compact = " ".join(suit + "".join(rank for card_suit, rank in cards if card_suit == suit) for suit in "SHDC")
            result = self.assess(compact)
            self.assertAlmostEqual(result["kr_points"] * 20, round(result["kr_points"] * 20))
            for suit in "SHDC":
                self.assertEqual(set(result["suit_evaluations"][suit]["steps"]), {str(n) for n in range(1, 27)})


if __name__ == "__main__":
    unittest.main()
