import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from engine.block_scout import scan_blocks, main
from engine.cards import Hand
from engine.model import Author, Gadget, PartnershipProfile


def incomplete_profile(with_response=False):
    specs = [{'id': 'opening', 'context': {'auction_pattern': ''},
              'call': '1C', 'meaning': {'action_type': 'opening'}}]
    if with_response:
        specs.append({'id': 'response', 'context': {'auction_pattern': '1CP'},
                      'call': '1D', 'meaning': {'action_type': 'response'}})
    gadget = Gadget.from_parts({'id': 'toy', 'author': {'name': 'Test'}}, specs)
    return PartnershipProfile('toy', 'Toy', '1', Author('Test'), (gadget,),
                              missing_call_behavior='block')


class BlockScoutTests(unittest.TestCase):
    def test_seeded_scan_collects_full_deals_blocked_auction_and_diagnostics(self):
        profile = incomplete_profile()
        options = {'attempts': 12, 'dealer': 'n', 'opening': '1C', 'seed': 19,
                   'max_seconds': 10}
        report = scan_blocks(profile, **options)
        self.assertEqual(report, scan_blocks(profile, **options))
        self.assertEqual(report['summary']['attempts'], 12)
        self.assertEqual(report['summary']['auction_matches'], 12)
        self.assertEqual(report['summary']['blocked'], 12)
        self.assertEqual(report['block_points'][0]['auction'], '1CP')
        self.assertEqual(report['block_points'][0]['seat'], 's')
        self.assertEqual(report['block_points'][0]['count'], 12)
        first = report['cases'][0]
        self.assertEqual(first['calls'], ['1C', 'P'])
        self.assertEqual(first['blocked']['seat'], 's')
        self.assertTrue(first['blocked']['diagnostics'])
        self.assertEqual(set(first['hands']), set('nesw'))
        cards = {(suit, rank) for holding in first['hands'].values()
                 for suit in 'SHDC' for rank in Hand.parse(holding).holding(suit)}
        self.assertEqual(len(cards), 52)

    def test_hand_constraints_and_response_filter_use_actual_auction(self):
        profile = incomplete_profile(with_response=True)
        report = scan_blocks(profile, attempts=30, dealer='ns', opening='1C',
                             response='1D', seed=4, max_seconds=10,
                             hand_constraints={'n': {'min_hcp': 13}},
                             max_cases=2)
        self.assertGreater(report['summary']['auction_matches'], 0)
        self.assertLess(report['summary']['auction_matches'], 30)
        self.assertEqual(report['summary']['blocked'], report['summary']['auction_matches'])
        self.assertEqual(len(report['cases']), 2)
        for case in report['cases']:
            self.assertEqual(case['calls'][:3], ['1C', 'P', '1D'])
            self.assertGreaterEqual(Hand.parse(case['hands']['n']).hcp, 13)
            self.assertIn(case['dealer'], ('n', 's'))

    def test_rare_hcp_share_is_explicit_and_cases_keep_stratum_label(self):
        options = {'attempts': 20, 'dealer': 'ns', 'opening': '1C',
                   'seed': 31, 'max_seconds': 10, 'max_cases': 20,
                   'rare_hcp': {'share': 0.5, 'opener': (16, 16),
                                'responder': (21, 21)}}
        report = scan_blocks(incomplete_profile(), **options)
        self.assertEqual(report, scan_blocks(incomplete_profile(), **options))
        self.assertEqual(report['summary']['strata']['natural']['attempts'], 10)
        self.assertEqual(report['summary']['strata']['rare_hcp']['attempts'], 10)
        self.assertEqual(report['summary']['blocked'], 20)
        rare_cases = [case for case in report['cases'] if case['stratum'] == 'rare_hcp']
        self.assertEqual(len(rare_cases), 10)
        for case in rare_cases:
            partner = {'n': 's', 's': 'n'}[case['dealer']]
            self.assertEqual(Hand.parse(case['hands'][case['dealer']]).hcp, 16)
            self.assertEqual(Hand.parse(case['hands'][partner]).hcp, 21)

    def test_cli_writes_report_for_later_review(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            constraints = root / 'constraints.json'
            output = root / 'scan.json'
            constraints.write_text(json.dumps({'n': {'min_hcp': 10}}), encoding='utf-8')
            code = main(['--profile', 'daqiush_2over1', '--dealer', 'n',
                         '--opening', '1NT', '--attempts', '2', '--seed', '11',
                         '--max-seconds', '10', '--constraints', str(constraints),
                         '--rare-share', '0.5', '--rare-opener-hcp', '16:16',
                         '--rare-responder-hcp', '21:21',
                         '--output', str(output)])
            self.assertEqual(code, 0)
            report = json.loads(output.read_text(encoding='utf-8'))
            self.assertEqual(report['profile']['id'], 'daqiush_2over1')
            self.assertEqual(report['filters']['opening'], '1N')
            self.assertEqual(report['filters']['rare_hcp']['share'], 0.5)
            self.assertEqual(report['summary']['strata']['rare_hcp']['attempts'], 1)
            self.assertEqual(report['summary']['attempts'], 2)

    def test_invalid_criteria_are_rejected(self):
        profile = incomplete_profile()
        for options in ({'response': '1D'}, {'attempts': 0},
                        {'dealer': 'bad'}, {'hand_constraints': {'n': {'min_hcp': 41}}},
                        {'max_cases': -1}, {'response': '1D', 'opening': '1C', 'max_calls': 2},
                        {'rare_hcp': {'share': 1.5, 'opener': (16, 16), 'responder': (21, 21)}},
                        {'rare_hcp': {'share': 0.5, 'opener': (30, 30), 'responder': (21, 21)}}):
            with self.subTest(options=options), self.assertRaises(ValueError):
                scan_blocks(profile, **options)


if __name__ == '__main__':
    unittest.main()
