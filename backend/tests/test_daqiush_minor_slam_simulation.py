import unittest
from types import SimpleNamespace
from unittest.mock import patch

from engine.auction import Auction
from engine.cards import Hand
from engine.dds_adapter import DDSUnavailableError
from engine.explanation import explain
from engine.loader import load_profile
from engine.selector import choose_bid


AUCTION = Auction.parse('1NP3CP3DP4NP')
OPENER = Hand.parse('SKQ7HAK6DKQ8C9532')
GOOD_RESPONDER = Hand.parse('SA2H32DAJ76CKQT84')


def sampled_deals(*args, **kwargs):
    return SimpleNamespace(deals=tuple({'n': OPENER, 's': GOOD_RESPONDER}
                                       for _ in range(16)), attempts=16, seed=1)


def table(club_tricks):
    return {'C': {'n': club_tricks}, 'D': {'n': 10}}


class DaqiushMinorSlamSimulationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = load_profile('daqiush_2over1')

    @patch('engine.simulation_decision.sample_deals', side_effect=sampled_deals)
    @patch('engine.simulation_decision.calculate_available_table')
    def test_slam_is_selected_only_when_target_is_made_often_enough(self, solver, _sample):
        solver.return_value = table(12)
        decision = choose_bid(self.profile, AUCTION, OPENER,
                              {'partner_hand': 'SAKQJHAKQDAKQCAKQ'})
        self.assertEqual(decision.call, '6C')
        self.assertEqual(explain(decision)['simulation']['call'], '6C')
        self.assertEqual(_sample.call_args.kwargs['public_constraints']['s']['min_hcp'], 14)
        self.assertEqual(_sample.call_args.kwargs['public_constraints']['s']['max_hcp'], 15)
        self.assertEqual(choose_bid(self.profile, Auction.parse('1NP3CP3DP4NP6CP'),
                                    GOOD_RESPONDER).call, 'P')
        solver.return_value = table(11)
        self.assertEqual(choose_bid(self.profile, AUCTION, OPENER).call, '5C')
        self.assertEqual(choose_bid(self.profile, Auction.parse('1NP3CP3DP4NP5CP'),
                                    GOOD_RESPONDER).call, 'P')

    @patch('engine.simulation_decision.sample_deals', side_effect=sampled_deals)
    @patch('engine.simulation_decision.calculate_available_table',
           side_effect=DDSUnavailableError('DDS unavailable'))
    def test_missing_solver_blocks_instead_of_guessing(self, _solver, _sample):
        decision = choose_bid(self.profile, AUCTION, OPENER)
        self.assertIsNone(decision.call)
        self.assertTrue(any('DDS unavailable' in item for item in decision.trace.diagnostics))


if __name__ == '__main__':
    unittest.main()
