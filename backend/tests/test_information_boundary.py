import unittest
from dataclasses import replace
from unittest.mock import patch

import app
from engine.auction import Auction
from engine.cards import Hand
from engine.evaluator import evaluate_expression
from engine.explanation import explain
from engine.model import Author, Gadget, PartnershipProfile, PolicyFunction
from engine.replay import replay_auction
from engine.selector import choose_bid
from engine.simulator import simulate_auction
from engine.trace import AuctionTrace


class InformationBoundaryTests(unittest.TestCase):
    actor = Hand.parse('SKJT5HATDAQ92C652')
    partners = ('SAQ83H743DJ84CAJ8', 'SAQ83H743DJ84C987')

    def profile(self, observer=None):
        def choose(ctx, pool):
            if observer:
                observer(ctx)
            # Deliberately exploit the old leak, so removing it changes behavior.
            return pool.get('1D' if ctx.environment.get('partner_hand') else '1C')

        gadget = Gadget.from_parts({'id': 'boundary', 'author': {'name': 'Test'}}, [
            {'id': 'clubs', 'context': {'auction_pattern': ''}, 'call': '1C',
             'meaning': {'hcp_range': [12, 14]}},
            {'id': 'diamonds', 'context': {'auction_pattern': ''}, 'call': '1D',
             'meaning': {'hcp_range': [12, 14]}},
        ])
        profile = PartnershipProfile('boundary', 'Boundary', '1', Author('Test'), (gadget,))
        return replace(profile, policy_functions=(
            PolicyFunction('choose', choose, profile.source_info, profile.author),
        ))

    def test_simulation_hides_partner_for_every_dealer(self):
        for actor, partner in [('n', 's'), ('e', 'w'), ('s', 'n'), ('w', 'e')]:
            for hidden in self.partners:
                with self.subTest(actor=actor, partner=hidden):
                    seen = []
                    result = simulate_auction(self.profile(seen.append),
                        {actor: self.actor, partner: hidden}, dealer=actor, max_calls=1)
                    self.assertEqual(result.calls, ('1C',))
                    self.assertEqual(seen[0].hand, self.actor)
                    self.assertEqual(seen[0].environment['seat'], actor)
                    self.assertNotIn('partner_hand', seen[0].environment)

    def test_direct_decisions_ignore_injected_partner_and_preserve_public_options(self):
        baseline = explain(choose_bid(self.profile(), Auction.parse(''), self.actor,
                                     {'scoring': 'IMP', 'style': 'test'}))
        for hidden in self.partners:
            environment = {'partner_hand': hidden, 'scoring': 'IMP', 'style': 'test'}
            seen = []
            result = explain(choose_bid(self.profile(seen.append), Auction.parse(''),
                                        self.actor, environment))
            self.assertEqual(result, baseline)
            self.assertNotIn('partner_hand', seen[0].environment)
            self.assertEqual(seen[0].environment['scoring'], 'IMP')
            self.assertEqual(seen[0].environment['style'], 'test')
            self.assertEqual(environment['partner_hand'], hidden)

    def test_simulation_ignores_caller_injected_partner(self):
        result = simulate_auction(self.profile(), {'n': self.actor},
            environment={'partner_hand': self.partners[0]}, max_calls=1)
        self.assertEqual(result.calls, ('1C',))

    def test_replay_and_candidate_conditions_cannot_read_injected_partner(self):
        seen = []
        def requires(ctx):
            seen.append(dict(ctx.environment))
            return True
        gadget = Gadget.from_parts({'id': 'condition', 'author': {'name': 'Test'}}, [
            {'id': 'open', 'context': {'auction_pattern': ''}, 'call': '1C',
             'requires': requires, 'meaning': {'hcp_range': [12, 14]}}
        ])
        profile = PartnershipProfile('condition', 'Condition', '1', Author('Test'), (gadget,))
        environment = {'partner_hand': self.partners[0]}
        choose_bid(profile, Auction.parse(''), self.actor, environment)
        trace = replay_auction(profile, Auction.parse('1CP'), self.actor, environment)
        self.assertEqual(len(seen), 2)
        self.assertTrue(all('partner_hand' not in env for env in seen))
        self.assertEqual(trace.applied_meanings[0]['public_meaning']['hcp_range'], [12, 14])

    def test_legacy_partner_expressions_fail_even_with_injected_hand(self):
        expressions = [
            {'var': 'partner.hcp'}, {'var': 'partner.S.length'},
            {'op': 'length', 'hand': 'partner', 'suit': 'S'},
        ]
        for expr in expressions:
            with self.subTest(expr=expr):
                with self.assertRaisesRegex(ValueError, 'hidden.*partner|partner.*hidden'):
                    evaluate_expression(expr, self.actor, AuctionTrace(),
                                        {'partner_hand': self.partners[0]})

    def test_public_bid_and_simulate_entry_points(self):
        with patch('app.load_profile', return_value=self.profile()):
            request = {'profile': {'id': 'boundary'}, 'auction': '',
                       'hand': 'SKJT5HATDAQ92C652',
                       'environment': {'partner_hand': self.partners[0]}}
            self.assertEqual(app.bid(request)['call'], '1C')
            request.update(hands={'n': request['hand'], 's': self.partners[0]}, max_calls=1)
            self.assertEqual(app.simulate(request)['calls'], ['1C'])


if __name__ == '__main__':
    unittest.main()
