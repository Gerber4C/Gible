import unittest

from app import route_analysis


class RouteAnalysisTests(unittest.TestCase):
    def setUp(self):
        self.request = {
            'profile': {'id': 'daqiush_2over1'}, 'auction': '1NP',
            'dealer': 'n', 'vulnerability': 'none', 'seat': 's',
            'hand': 'ST2HAQT976D53CKJ2', 'seed': 15,
            'sample_count': 2, 'max_attempts': 5000,
            'first_calls': ['4C', '2D'],
        }

    def test_same_sampled_deals_report_completed_and_unavailable_routes(self):
        solved = []

        def solver(deal):
            solved.append(deal)
            return {'H': {'n': 10, 's': 10}}

        report = route_analysis(self.request, solve_table=solver)
        self.assertEqual(report['mode'], 'route_experiment')
        self.assertEqual(report['sample_count'], 2)
        self.assertEqual(report['opponent_model'], 'pass')
        self.assertEqual(len(solved), 2)
        self.assertEqual([route['first_call'] for route in report['routes']], ['4C', '2D'])
        texas, jacoby = report['routes']
        self.assertEqual((texas['completed'], texas['blocked'], texas['made']), (2, 0, 2))
        self.assertEqual(texas['coverage_rate'], 1.0)
        self.assertEqual(texas['completion_rate'], 1.0)
        self.assertEqual(jacoby['status'], 'unavailable')
        self.assertEqual(jacoby['completed'], 0)
        self.assertEqual(jacoby['blocked'], 2)
        self.assertNotIn('deals', report)
        self.assertNotIn('hands', report)
        self.assertNotIn('chosen_call', report)

    def test_reproducible_seed_and_failed_contract_are_reported(self):
        def solver(_deal):
            return {'H': {'n': 9, 's': 9}}

        request = {**self.request, 'first_calls': ['4C']}
        first = route_analysis(request, solve_table=solver)
        second = route_analysis(request, solve_table=solver)
        self.assertEqual(first, second)
        self.assertEqual(first['routes'][0]['failed'], 2)
        self.assertEqual(first['routes'][0]['completion_rate'], 0.0)
        self.assertEqual(first['routes'][0]['contracts'][0]['contract'], '4H')

    def test_hidden_hands_and_undefined_route_meanings_are_rejected(self):
        for key, value in (('hands', {'n': 'secret'}),
                           ('partner_hand', 'secret'),
                           ('route_meanings', {'2D': 'secret'})):
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'Unsupported route analysis field'):
                route_analysis({**self.request, key: value}, solve_table=lambda _: {})
        for calls in ([], ['4C', '4C'], ['4H']):
            with self.subTest(calls=calls), self.assertRaises(ValueError):
                route_analysis({**self.request, 'first_calls': calls}, solve_table=lambda _: {})

    def test_experiment_is_limited_to_first_one_notrump_response(self):
        with self.assertRaisesRegex(ValueError, 'first response'):
            route_analysis({**self.request, 'auction': '1NP4CP4HP'},
                           solve_table=lambda _: {})

    def test_two_authored_routes_use_the_same_deal_for_distinct_contracts(self):
        from engine.auction import Auction
        from engine.cards import Hand
        from engine.deal_sampler import sample_deals
        from engine.model import Author, Gadget, PartnershipProfile
        from engine.route_evaluation import compare_authored_routes

        gadget = Gadget.from_parts({'id': 'paired', 'namespace': 'test',
                                    'author': {'name': 'test'}}, [
            {'id': 'open', 'context': {'auction_pattern': ''}, 'call': '1N',
             'meaning': {'nature_labels': ['natural']}},
            {'id': 'clubs', 'context': {'auction_pattern': '1NP'}, 'call': '2C',
             'meaning': {'nature_labels': ['natural']}},
            {'id': 'diamonds', 'context': {'auction_pattern': '1NP'}, 'call': '2D',
             'meaning': {'nature_labels': ['natural']}},
        ])
        profile = PartnershipProfile('paired', 'Paired routes', '1', Author('test'), (gadget,))
        hand = Hand.parse('ST2HAQT976D53CKJ2')
        deals = sample_deals('s', hand, sample_count=1, seed=19).deals
        solved = []

        def solver(deal):
            solved.append(deal)
            return {'C': {'s': 8}, 'D': {'s': 7}}

        routes = compare_authored_routes(profile, Auction.parse('1NP'), hand,
                                         deals, ['2C', '2D'], solve_table=solver)
        self.assertEqual(len(solved), 1)
        self.assertEqual([(route['completed'], route['made'], route['failed'])
                          for route in routes], [(1, 1, 0), (1, 0, 1)])
        self.assertEqual([route['contracts'][0]['contract'] for route in routes],
                         ['2C', '2D'])


if __name__ == '__main__':
    unittest.main()
