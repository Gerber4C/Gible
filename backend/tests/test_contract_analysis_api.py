import unittest

from app import contract_analysis


class ContractAnalysisApiTests(unittest.TestCase):
    def setUp(self):
        self.request = {
            'profile': {'id': 'daqiush_2over1'}, 'auction': '1NP',
            'dealer': 'n', 'vulnerability': 'none', 'seat': 's',
            'hand': 'SAKQJHAT987D432C2', 'seed': 9, 'sample_count': 2,
            'targets': [{'level': 3, 'strain': 'NT', 'declarer': 'n'}],
        }

    def test_analysis_reports_explicit_contract_success_without_making_a_bid(self):
        def fake_solver(_deal):
            return {'NT': {'n': 9}}
        result = contract_analysis(self.request, solve_table=fake_solver)
        self.assertEqual(result['mode'], 'analysis_only')
        self.assertEqual(result['estimates'][0]['contract'], '3NT')
        self.assertEqual(result['estimates'][0]['completion_rate'], 1.0)
        self.assertEqual(result['estimates'][0]['sample_count'], 2)
        self.assertNotIn('chosen_call', result)
        self.assertNotIn('deals', result)

    def test_hidden_deal_or_client_meanings_are_not_accepted(self):
        for key, value in (('hands', {'n': 'secret'}),
                           ('public_meanings', [{'hcp_min': 0}]),
                           ('partner_hand', 'secret')):
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'Unsupported analysis field'):
                contract_analysis({**self.request, key: value}, solve_table=lambda deal: {})

    def test_targets_must_be_on_acting_side_and_reachable(self):
        bad = [
            ({'level': 3, 'strain': 'NT', 'declarer': 'e'}, 'declarer'),
            ({'level': 3, 'strain': 'NT', 'declarer': 's'}, 'declarer'),
            ({'level': 1, 'strain': 'C', 'declarer': 'n'}, 'below'),
        ]
        for target, message in bad:
            with self.subTest(target=target), self.assertRaisesRegex(ValueError, message):
                contract_analysis({**self.request, 'targets': [target]}, solve_table=lambda deal: {})

    def test_actor_must_match_auction_turn(self):
        with self.assertRaisesRegex(ValueError, 'acting seat'):
            contract_analysis({**self.request, 'seat': 'n'}, solve_table=lambda deal: {})

    def test_texas_natural_acceptance_makes_opener_the_heart_declarer(self):
        scenario = {**self.request, 'auction': '1NP4CP4HP',
                    'hand': 'ST2HAQT976D53CKJ2', 'sample_count': 1,
                    'targets': [{'level': 4, 'strain': 'H', 'declarer': 's'}]}
        with self.assertRaisesRegex(ValueError, 'Target declarer'):
            contract_analysis(scenario, solve_table=lambda deal: {})


if __name__ == '__main__':
    unittest.main()
