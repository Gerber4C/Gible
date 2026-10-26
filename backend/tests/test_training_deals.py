import unittest
from dataclasses import replace

import app
from engine.auction import Auction
from engine.cards import Hand
from engine.loader import load_profile
from engine.model import Author, Gadget, PartnershipProfile, PolicyFunction
from engine.selector import choose_bid


class TrainingDealTests(unittest.TestCase):
    def generate(self, profile, **kwargs):
        from engine.training_deals import generate_training_deal
        return generate_training_deal(profile, **kwargs)

    def test_opening_uses_actual_profile_selection_and_complete_deal(self):
        profile = load_profile('daqiush_2over1')
        outcome = self.generate(profile, opening='1NT', opener='n', seed=15, max_attempts=500)
        self.assertEqual(outcome['status'], 'matched')
        self.assertEqual(outcome['opening'], '1N')
        self.assertEqual(outcome['opener'], 'n')
        self.assertGreater(outcome['attempts'], 0)
        hands = {seat: Hand.parse(cards) for seat, cards in outcome['hands'].items()}
        self.assertEqual(set(hands), set('nesw'))
        cards = [(suit, rank) for hand in hands.values() for suit in 'SHDC'
                 for rank in hand.holding(suit)]
        self.assertEqual(len(cards), 52)
        self.assertEqual(len(set(cards)), 52)
        self.assertEqual(choose_bid(profile, Auction.parse('', dealer='n'), hands['n']).call, '1N')
        self.assertEqual(outcome, self.generate(profile, opening='1N', opener='n', seed=15, max_attempts=500))

    def test_random_opener_is_reproducible_and_first_call_matches(self):
        profile = load_profile('daqiush_2over1')
        outcome = self.generate(profile, opening='1N', opener='random', seed=9, max_attempts=500)
        self.assertIn(outcome['opener'], 'nesw')
        self.assertEqual(outcome['dealer'], outcome['opener'])
        hand = Hand.parse(outcome['hands'][outcome['opener']])
        self.assertEqual(choose_bid(profile, Auction.parse('', dealer=outcome['dealer']), hand).call, '1N')
        self.assertEqual(outcome, self.generate(profile, opening='1N', opener='random', seed=9, max_attempts=500))

    def test_partnership_opener_is_one_of_requested_pair_and_reproducible(self):
        profile = load_profile('daqiush_2over1')
        for requested, allowed in (('ns', {'n', 's'}), ('ew', {'e', 'w'})):
            with self.subTest(requested=requested):
                outcome = self.generate(profile, opening='1NT', opener=requested,
                                        seed=15, max_attempts=500)
                self.assertEqual(outcome['status'], 'matched')
                self.assertIn(outcome['opener'], allowed)
                self.assertEqual(outcome['dealer'], outcome['opener'])
                hand = Hand.parse(outcome['hands'][outcome['opener']])
                self.assertEqual(choose_bid(profile,
                    Auction.parse('', dealer=outcome['opener']), hand).call, '1N')
                self.assertEqual(outcome, self.generate(profile, opening='1NT',
                    opener=requested, seed=15, max_attempts=500))

    def test_omitted_opener_defaults_to_north_south(self):
        profile = load_profile('daqiush_2over1')
        outcome = self.generate(profile, opening='1NT', seed=15, max_attempts=500)
        self.assertIn(outcome['opener'], {'n', 's'})
        self.assertEqual(outcome, self.generate(profile, opening='1NT', opener='ns',
                                                 seed=15, max_attempts=500))
        api_outcome = app.training_deal({'profile': {'id': 'daqiush_2over1'},
                                         'opening': '1NT', 'seed': 15,
                                         'max_attempts': 500})
        self.assertEqual(api_outcome, outcome)

    def test_app_api_exposes_seeded_training_deal(self):
        outcome = app.training_deal({
            'profile': {'id': 'daqiush_2over1'}, 'opening': '1NT',
            'opener': 's', 'vulnerability': 'ew', 'seed': 15, 'max_attempts': 500,
        })
        self.assertEqual(outcome['status'], 'matched')
        self.assertEqual(outcome['opener'], 's')
        self.assertEqual(outcome['vulnerability'], 'ew')

    def test_response_matches_actual_selection_with_public_opening_only(self):
        # Candidate 1D exists, but policy picks 1H for hearts. Search must
        # inspect the real selector's final answer rather than mere eligibility.
        gadget = Gadget.from_parts({'id': 'toy', 'author': {'name': 'Test'}}, [
            {'id': 'opening', 'context': {'auction_pattern': ''}, 'call': '1C',
             'meaning': {'hcp_range': [0, 40]}},
            {'id': 'diamond', 'context': {'auction_pattern': '1CP'}, 'call': '1D',
             'meaning': {'action_type': 'response'}},
            {'id': 'heart', 'context': {'auction_pattern': '1CP'}, 'call': '1H',
             'meaning': {'action_type': 'response'}},
        ])
        def choose(ctx, pool):
            if ctx.auction.calls == ('1C', 'P'):
                return pool.get('1H') if ctx.hand.length('H') >= 5 else pool.get('1D')
            return None
        profile = PartnershipProfile('toy', 'Toy', '1', Author('Test'), (gadget,))
        profile = replace(profile, policy_functions=(PolicyFunction(
            'choose', choose, profile.source_info, profile.author),))
        outcome = self.generate(profile, opening='1C', response='1D', opener='e',
                                seed=18, max_attempts=100)
        self.assertEqual(outcome['status'], 'matched')
        self.assertEqual(outcome['response'], '1D')
        partner = 'w'
        response = choose_bid(profile, Auction.parse('1CP', dealer='e'),
                              Hand.parse(outcome['hands'][partner])).call
        self.assertEqual(response, '1D')
        self.assertEqual(outcome['calls'], ['1C', 'P', '1D'])

    def test_unsupported_response_is_reported_before_search(self):
        profile = load_profile('daqiush_2over1')
        with self.assertRaisesRegex(ValueError, 'unsupported response'):
            self.generate(profile, opening='1N', response='4S', max_attempts=1)

    def test_daqiush_texas_response_is_selected_for_both_partnership_directions(self):
        profile = load_profile('daqiush_2over1')
        for opener in ('n', 'e'):
            with self.subTest(opener=opener):
                outcome = self.generate(profile, opening='1NT', response='4C',
                                        opener=opener, seed=15 if opener == 'n' else 16,
                                        max_attempts=1000)
                self.assertEqual(outcome['status'], 'matched')
                self.assertEqual(outcome['calls'], ['1N', 'P', '4C'])
                partner = {'n': 's', 'e': 'w'}[opener]
                self.assertEqual(choose_bid(profile, Auction.parse('1NP', dealer=opener),
                    Hand.parse(outcome['hands'][partner])).call, '4C')

    def test_unsupported_opening_and_bad_inputs_are_rejected(self):
        profile = load_profile('daqiush_2over1')
        for opening in ['1C', 'P']:
            with self.subTest(opening=opening), self.assertRaisesRegex(ValueError, 'unsupported opening|opening must'):
                self.generate(profile, opening=opening, max_attempts=1)
        for options in [{'opener': 'q'}, {'max_attempts': 0}, {'max_attempts': 999999},
                        {'seed': True}, {'vulnerability': 'wrong'}]:
            with self.subTest(options=options), self.assertRaises(ValueError):
                self.generate(profile, opening='1N', **options)

    def test_bounded_failure_does_not_relax_target(self):
        profile = load_profile('daqiush_2over1')
        outcome = self.generate(profile, opening='1N', seed=15, max_attempts=1)
        self.assertEqual(outcome['status'], 'not_found')
        self.assertIsNone(outcome['hands'])
        self.assertEqual(outcome['attempts'], 1)


if __name__ == '__main__':
    unittest.main()
