import unittest

from engine.auction import Auction
from engine.candidate_generation import agreed_trump_fallback
from engine.trace import AuctionTrace, StateRecord


class AgreedTrumpFallbackTests(unittest.TestCase):
    def trace(self, *suits):
        trace = AuctionTrace()
        for suit in suits:
            trace.add_state(StateRecord.from_dict({"key": "agreed_suit", "suit": suit}, {}))
        return trace

    def test_lowest_legal_level_for_each_suit(self):
        for suit, expected in (("C", "4C"), ("D", "4D"), ("H", None), ("S", "3S")):
            with self.subTest(suit=suit):
                candidate = agreed_trump_fallback(Auction.parse("3HP"), self.trace(suit))
                if expected is None:
                    self.assertIsNone(candidate)  # Our contract is already hearts.
                else:
                    self.assertEqual(candidate.call, expected)

    def test_returns_above_notrump(self):
        self.assertEqual(agreed_trump_fallback(Auction.parse("3NP"), self.trace("H")).call, "4H")

    def test_no_agreement_or_no_legal_return(self):
        self.assertIsNone(agreed_trump_fallback(Auction.parse("3HP"), self.trace()))
        self.assertIsNone(agreed_trump_fallback(Auction.parse("3HP"), self.trace("N")))
        self.assertIsNone(agreed_trump_fallback(Auction.parse("7NP"), self.trace("S")))
        self.assertIsNone(agreed_trump_fallback(Auction.parse("3HPPP"), self.trace("S")))

    def test_latest_agreement_is_used(self):
        self.assertEqual(agreed_trump_fallback(Auction.parse("3NP"), self.trace("H", "S")).call, "4S")

    def test_our_trump_contract_is_not_raised_even_after_double(self):
        self.assertIsNone(agreed_trump_fallback(Auction.parse("3SX"), self.trace("S")))

    def test_opponents_contract_does_not_count_as_our_placement(self):
        self.assertEqual(agreed_trump_fallback(Auction.parse("3S"), self.trace("S")).call, "4S")
