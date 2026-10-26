import unittest

from engine.cards import Hand
from engine.deal_sampler import SamplingExhausted, sample_deals
from engine.auction import Auction
from engine.loader import load_profile
from engine.public_evidence import derive_public_evidence
from pathlib import Path


ACTING_HAND = Hand.parse('SAKQJHAT987D432C2')


class DealSamplerTests(unittest.TestCase):
    def test_daqiush_opening_samples_satisfy_published_opening_assessment(self):
        profile = load_profile('daqiush_2over1', Path(__file__).resolve().parents[1])
        auction = Auction.parse('1N', dealer='n')
        evidence = derive_public_evidence(profile, auction)
        result = sample_deals('s', ACTING_HAND, public_evidence=evidence,
                              sample_count=2, seed=91, max_attempts=5000)
        self.assertEqual(len(result.deals), 2)
        self.assertTrue(all(evidence.accepts(deal) for deal in result.deals))
        self.assertEqual(evidence.constraints['n']['min_hcp'], 14)
        self.assertEqual(evidence.constraints['n']['max_hcp'], 18)

    def test_daqiush_texas_public_evidence_includes_major_length_and_opener_reply(self):
        profile = load_profile('daqiush_2over1', Path(__file__).resolve().parents[1])
        evidence = derive_public_evidence(profile, Auction.parse('1NP4CP4H', dealer='n'))
        self.assertEqual(evidence.constraints['s']['min_lengths']['H'], 6)
        self.assertEqual(evidence.constraints['n']['min_hcp'], 14)
        self.assertIn('unprotected_kq_count', evidence.labels)

    def test_unmodelled_nonpass_auction_evidence_blocks_public_sampling(self):
        profile = load_profile('daqiush_2over1', Path(__file__).resolve().parents[1])
        with self.assertRaisesRegex(ValueError, 'sampling evidence'):
            derive_public_evidence(profile, Auction.parse('1NP3NP', dealer='n'))
    def test_complete_deals_preserve_acting_hand_and_all_cards(self):
        result = sample_deals('n', ACTING_HAND, sample_count=3, seed=17)
        self.assertEqual(len(result.deals), 3)
        for deal in result.deals:
            self.assertEqual(set(deal), set('nesw'))
            self.assertEqual(deal['n'], ACTING_HAND)
            cards = [(suit, rank) for hand in deal.values()
                     for suit in 'SHDC' for rank in hand.holding(suit)]
            self.assertEqual(len(cards), 52)
            self.assertEqual(len(set(cards)), 52)

    def test_seed_repeats_the_same_samples(self):
        first = sample_deals('w', ACTING_HAND, sample_count=2, seed=431)
        second = sample_deals('w', ACTING_HAND, sample_count=2, seed=431)
        self.assertEqual(first, second)

    def test_every_sample_honors_explicit_public_hcp_and_length_bounds(self):
        constraints = {
            'e': {'min_hcp': 10, 'max_hcp': 16},
            's': {'min_lengths': {'hearts': 6}, 'max_lengths': {'clubs': 4}},
        }
        result = sample_deals('n', ACTING_HAND, public_constraints=constraints,
                              sample_count=2, seed=30, max_attempts=20000)
        for deal in result.deals:
            self.assertTrue(10 <= deal['e'].hcp <= 16)
            self.assertGreaterEqual(deal['s'].length('H'), 6)
            self.assertLessEqual(deal['s'].length('C'), 4)

    def test_auction_and_hidden_hands_are_not_sampler_inputs(self):
        with self.assertRaises(TypeError):
            sample_deals('n', ACTING_HAND, auction='1N')
        with self.assertRaises(TypeError):
            sample_deals('n', ACTING_HAND, partner_hand=ACTING_HAND)
        with self.assertRaisesRegex(ValueError, 'unsupported public constraint'):
            sample_deals('n', ACTING_HAND,
                         public_constraints={'s': {'applies': 'private'}})

    def test_rejects_contradictory_constraints_before_search(self):
        cases = [
            {'e': {'min_hcp': 20}, 's': {'min_hcp': 20}},
            {'e': {'min_lengths': {'spades': 10}}},
            {'n': {'max_hcp': 13}},
            {'e': {'min_lengths': {'clubs': 10}},
             's': {'min_lengths': {'clubs': 10}}},
            {'e': {'min_hcp': 15, 'max_hcp': 14}},
        ]
        for constraints in cases:
            with self.subTest(constraints=constraints), self.assertRaisesRegex(ValueError, 'contradict'):
                sample_deals('n', ACTING_HAND, public_constraints=constraints)

    def test_attempt_and_time_limits_are_enforced(self):
        hard = {'e': {'min_lengths': {'spades': 9}}}
        with self.assertRaises(SamplingExhausted) as caught:
            sample_deals('n', ACTING_HAND, public_constraints=hard,
                         seed=9, max_attempts=1)
        self.assertEqual(caught.exception.attempts, 1)
        with self.assertRaises(SamplingExhausted) as caught:
            sample_deals('n', ACTING_HAND, seed=9, max_seconds=1e-12)
        self.assertLessEqual(caught.exception.attempts, 1)

    def test_rejects_bad_hand_and_budget_inputs(self):
        for options in ({'seed': True}, {'sample_count': 0}, {'max_attempts': 0},
                        {'max_seconds': 0}, {'max_attempts': 50001}):
            with self.subTest(options=options), self.assertRaises(ValueError):
                sample_deals('n', ACTING_HAND, **options)
        with self.assertRaises(ValueError):
            sample_deals('q', ACTING_HAND)
        with self.assertRaises(ValueError):
            sample_deals('n', Hand.parse('SXXXXXXXXXXXXX'))

    def test_rejects_direct_hand_with_nonstandard_rank(self):
        hand = Hand('AKQJT9876543Z', '', '', '')
        with self.assertRaisesRegex(ValueError, 'standard 52-card deck'):
            sample_deals('n', hand, seed=9)


if __name__ == '__main__':
    unittest.main()
