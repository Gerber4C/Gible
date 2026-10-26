import unittest
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory

from engine.auction import Auction
from engine.cards import Hand
from engine.explanation import explain
from engine.model import Author, Gadget, PartnershipProfile, PolicyFunction
from engine.replay import replay_auction
from engine.selector import choose_bid
from engine.simulator import simulate_auction
from engine.loader import load_profile


def profile(*specs):
    gadget = Gadget.from_parts({'id':'test','author':{'name':'Test'}}, list(specs))
    return PartnershipProfile('test','Test','1',Author('Test'),(gadget,))


def spec(id, when, call, **meaning):
    return {'id':id,'context':{'auction_pattern':when},'call':call,'meaning':meaning}


class AxiomIntegrationTests(unittest.TestCase):
    hand = Hand.parse('SKJT5HATDAQ92C652')

    def test_unlabelled_opening_is_selectable_without_invitation_or_force_tags(self):
        p = profile(spec('ordinary_opening', '', '1C', nature_labels=['natural']))
        hand = Hand.parse('SAKQJHAKQDAKQCAKQ')
        decision = choose_bid(p, Auction.parse(''), hand)
        self.assertEqual(decision.call, '1C')
        self.assertNotIn('axiom_tags', decision.selected_candidate.public_meaning)

    def test_blocked_simulation_preserves_history_without_fake_pass(self):
        p = profile(spec('open','','1C',axiom_tags=['forcing']))
        result = simulate_auction(p, {'n':self.hand,'s':self.hand})
        self.assertEqual(result.calls, ('1C','P'))
        self.assertEqual(result.status,'blocked')
        self.assertEqual(result.blocked['seat'],'s')
        self.assertIn('FORCING_PASS',[e['code'] for e in result.blocked['axioms']['errors']])

    def test_policy_sees_only_compliant_candidates(self):
        p = profile(spec('open','','1C',axiom_tags=['forcing']),
                    spec('bad','1CP','P',axiom_tags=['signoff']),
                    spec('answer','1CP','1N',axiom_tags=['signoff']))
        seen = []
        def choose(ctx,pool):
            seen.extend(pool.calls)
            return pool.get('P') or pool.get('1N')
        p = replace(p,policy_functions=(PolicyFunction('test',choose,p.source_info,p.author),))
        result = explain(choose_bid(p,Auction.parse('1CP'),self.hand))
        self.assertEqual(result['call'],'1N')
        self.assertEqual(seen,['1N'])
        self.assertTrue(result['axioms']['errors'])

    def test_meaningful_pass_is_replayed_and_rotated_seats_work(self):
        p = profile(spec('open','','1C'),spec('forcing_pass','1C1D','P',axiom_tags=['forcing']))
        auction = Auction.parse('1C1DPP',dealer='e')
        trace = replay_auction(p,auction,self.hand)
        self.assertEqual(trace.applied_meanings[-1]['seat'],'w')
        self.assertEqual(trace.applied_meanings[-1]['call'],'P')
        self.assertIsNone(choose_bid(p,auction,self.hand).call)

    def test_actual_partner_hand_cannot_change_axiom_decision(self):
        p = profile(spec('open','','1C',hcp_range=[13,14]),spec('invite','1CP','2N',axiom_tags=['invite']),
                    spec('pass','1CP','P',axiom_tags=['signoff']))
        hand = Hand.parse('SA73HK82D954CKJ62') # 11 HCP
        results = [explain(choose_bid(p,Auction.parse('1CP'),hand,{'partner_hand':other}))
                   for other in (self.hand,Hand.parse('S9876H876D876C876'))]
        self.assertEqual(results[0]['call'],'2N')
        self.assertEqual(results[0]['axioms'],results[1]['axioms'])

    def test_pass_after_artificial_game_is_not_accepted_as_game(self):
        p = profile(spec('gf','','1C',axiom_tags=['game_forcing']),
                    spec('artificial','1CP1SP','3N',nature_labels=['artificial']))
        self.assertIsNone(choose_bid(p,Auction.parse('1CP1SP3NP'),self.hand).call)

    def test_profile_bsl_config_and_definition_validation(self):
        with TemporaryDirectory() as directory:
            root=Path(directory)
            base=root/'test_profiles'/'axiom_test'
            gadget=base/'gadgets'/'example'
            gadget.mkdir(parents=True)
            (base/'profile.bsl.py').write_text("class Test(Profile):\n    id='axiom_test'\n    gadgets=['example']\n    axioms={'game_hcp': {'N': 26}, 'quality': {'threshold': 0.75}}\n",encoding='utf-8')
            source="class Example(Gadget):\n    id='example'\n    def build(self):\n        c=self.call('forcing_pass')\n        c.when='1C1D'\n        c.bid='P'\n        c.meaning.axiom_tags=['forcing']\n"
            (gadget/'gadget.bsl.py').write_text(source,encoding='utf-8')
            loaded=load_profile('axiom_test',root)
            self.assertEqual(loaded.axioms['game_hcp']['N'],26)
            self.assertEqual(loaded.axioms['quality']['threshold'],0.75)
            (gadget/'gadget.bsl.py').write_text(source.replace("1C1D","1CP"),encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'PASS_SEMANTICS'):
                load_profile('axiom_test',root)
