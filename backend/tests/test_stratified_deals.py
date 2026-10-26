import random
import unittest

from engine.cards import Hand
from engine.stratified_deals import HcpPairSampler


class StratifiedDealsTests(unittest.TestCase):
    def test_generates_complete_reproducible_high_point_partnership_deals(self):
        first = HcpPairSampler((16, 16), (21, 21))
        second = HcpPairSampler((16, 16), (21, 21))
        left_rng, right_rng = random.Random(71), random.Random(71)
        for dealer in ('n', 's', 'e', 'w'):
            for _ in range(8):
                left = first.deal(left_rng, dealer)
                right = second.deal(right_rng, dealer)
                self.assertEqual(left, right)
                partner = {'n': 's', 's': 'n', 'e': 'w', 'w': 'e'}[dealer]
                self.assertEqual(left[dealer].hcp, 16)
                self.assertEqual(left[partner].hcp, 21)
                self.assertEqual(set(left), set('nesw'))
                cards = {(suit, rank) for hand in left.values()
                         for suit in 'SHDC' for rank in hand.holding(suit)}
                self.assertEqual(len(cards), 52)
                for hand in left.values():
                    self.assertIsInstance(hand, Hand)
                    hand.validate(validate_count=True)

    def test_impossible_combined_strength_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'no feasible'):
            HcpPairSampler((25, 25), (20, 20))


if __name__ == '__main__':
    unittest.main()
