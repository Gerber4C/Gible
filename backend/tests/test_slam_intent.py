import unittest

from engine.cards import Hand
from engine.slam_intent import detect_slam_intent


class SlamIntentTests(unittest.TestCase):
    def test_notrump_small_and_grand_thresholds(self):
        small = detect_slam_intent(Hand.parse('SAKQJHKJ98DA2C543'), 15)
        self.assertEqual((small.strain, small.level, small.grand), ('N', 6, False))
        self.assertEqual(small.combined_min, 33)

        good_32 = detect_slam_intent(Hand.parse('SAKQJ2HAQJD432C32'), 15)
        self.assertEqual((good_32.strain, good_32.level), ('N', 6))
        self.assertEqual(good_32.combined_min, 32)

        grand = detect_slam_intent(Hand.parse('SAKQJHKQ8DAK2C543'), 15)
        self.assertEqual((grand.strain, grand.level, grand.grand), ('N', 7, True))
        self.assertEqual(grand.combined_min, 37)

        below = detect_slam_intent(Hand.parse('SAKQJHKQ8D432C432'), 15)
        self.assertEqual((below.level, below.grand), (None, False))

    def test_suit_small_and_grand_thresholds(self):
        small_seven = detect_slam_intent(
            Hand.parse('SAKQJ987HKQ8D43C2'), 15, strain='S')
        self.assertEqual((small_seven.level, small_seven.grand), (6, False))

        small_six = detect_slam_intent(
            Hand.parse('SAKQJ98HKQ8D43C32'), 15, strain='S')
        self.assertEqual((small_six.level, small_six.grand), (6, False))

        grand = detect_slam_intent(
            Hand.parse('SAKQJ987HAKJD43C2'), 15, strain='S')
        self.assertEqual((grand.level, grand.grand), (7, True))

    def test_partner_minimum_defaults_to_one_notrump_floor(self):
        hand = Hand.parse('SAKQJHKJ98DA2C543')
        self.assertEqual(detect_slam_intent(hand).combined_min, hand.hcp + 15)


if __name__ == '__main__':
    unittest.main()
