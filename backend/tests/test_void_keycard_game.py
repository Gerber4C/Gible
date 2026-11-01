import unittest
from types import SimpleNamespace
from unittest.mock import patch

from engine.auction import Auction
from engine.cards import Hand
from engine.loader import load_profile
from engine.replay import replay_auction
from engine.selector import choose_bid
from engine.void_keycard_game import (
    choose_void_keycard_continuation, is_void_keycard_continuation,
)


class VoidKeycardGameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = load_profile('daqiush_2over1')
        cls.hand = Hand.parse('SAKQ76HKJ5DA43CQ7')

    def _trace(self, auction):
        return replay_auction(self.profile, Auction.parse(auction), self.hand)

    def test_only_void_answers_start_the_game_tree(self):
        cases = {
            '1NP4CP4HP4NP5NP': True,
            '1NP4CP4HP4NP6CP': True,
            '1NP4CP4HP4NP6DP': True,
            '1NP4CP4HP4NP6HP': True,
            '1NP4CP4HP4NP5SP': False,
            '1NP4CP4HP4NP5DP': False,
        }
        for auction, expected in cases.items():
            with self.subTest(auction=auction):
                parsed = Auction.parse(auction)
                self.assertEqual(
                    is_void_keycard_continuation(
                        self.profile.id, parsed, self._trace(auction),
                        self.hand),
                    expected)

    def test_invitation_keeps_partner_reaction_branch(self):
        auction = Auction.parse('1NP4CP4HP4NP5NP')
        trace = self._trace('1NP4CP4HP4NP5NP')
        deals = (
            {'n': self.hand, 'e': self.hand, 's': self.hand, 'w': self.hand},
        )
        completion = {'6C': 1.0, '6D': 1.0, '7H': 0.05}

        def compare(_deals, targets, *, solve_table):
            return tuple(
                SimpleNamespace(completion_rate=completion.get(
                    target.contract, 0.0))
                for target in targets)

        with patch('engine.cue_slam_policy.sample_process_hands',
                   return_value=deals), \
             patch('engine.void_keycard_game.compare_contract_targets',
                   side_effect=compare), \
             patch('engine.void_keycard_game.calculate_available_table',
                   return_value={}):
            result = choose_void_keycard_continuation(
                self.profile, auction, trace, self.hand, ('6C', '6D', '7H'))

        self.assertIsNotNone(result)
        self.assertEqual(result['call'], '6C')
        self.assertEqual(
            [(reaction['response'], reaction['final'])
             for reaction in result['reactions']],
            [('P', '6C')])

    def test_selector_uses_the_void_game_tree(self):
        auction = Auction.parse('1NP4CP4HP4NP5NP')
        simulated = {
            'call': '7H', 'expected_score': 1510.0, 'sample_count': 1,
            'reactions': [{'partner': 'sample', 'response': 'P',
                           'final': '7H'}],
        }
        with patch('engine.selector.choose_void_keycard_continuation',
                   return_value=simulated) as chooser:
            decision = choose_bid(self.profile, auction, self.hand)

        chooser.assert_called_once()
        self.assertEqual(decision.call, '7H')
        self.assertEqual(decision.trace.simulation_decision, simulated)

    def test_selector_does_not_simulate_an_ordinary_queen_answer(self):
        auction = Auction.parse('1NP4CP4HP4NP5SP')
        with patch('engine.selector.choose_void_keycard_continuation',
                   return_value=None) as chooser:
            choose_bid(self.profile, auction, self.hand)

        chooser.assert_not_called()


if __name__ == '__main__':
    unittest.main()
