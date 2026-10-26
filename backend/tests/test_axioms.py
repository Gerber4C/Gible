import unittest
from dataclasses import replace

from engine.auction import Auction
from engine.cards import Hand
from engine.context import CallCandidate
from engine.trace import AuctionTrace
from engine.axioms import evaluate_axioms, invitation_action


def candidate(call, *tags, **meaning):
    return CallCandidate(call, {"qualified_id": "test:" + call},
                         {"axiom_tags": list(tags), **meaning}, "test", call, 0, ())


def trace_of(*entries):
    trace = AuctionTrace()
    for index, seat, call, meaning in entries:
        trace.add_applied_meaning({"index": index, "seat": seat, "call": call,
                                  "origin": {"qualified_id": "test:" + str(index)},
                                  "public_meaning": meaning, "effects": []})
    return trace


class AxiomTests(unittest.TestCase):
    hand = Hand.parse("SKJT5HATDAQ92C652")

    def check(self, auction, trace, candidates, config=None):
        return evaluate_axioms(Auction.parse(auction), self.hand, trace, tuple(candidates), config or {})

    def test_invitation_boundaries(self):
        for own, low, high, expected in [(11,13,14,'invite'), (11,12,14,'invite'),
                                         (11,11,14,None), (11,12,13,'signoff'), (12,13,14,'game')]:
            self.assertEqual(invitation_action(own, low, high, 25), expected)

    def test_forcing_and_invitation_pass_require_rho_action(self):
        for tag in ('forcing', 'invite', 'invite_plus', 'invite_minus'):
            allowed, report = self.check('1CP', AuctionTrace(), [candidate('P', tag)])
            self.assertFalse(allowed)
            self.assertEqual(report['errors'][0]['code'], 'PASS_SEMANTICS')
            allowed, report = self.check('1C1D', AuctionTrace(), [candidate('P', tag)])
            self.assertEqual(allowed[0].call, 'P')

    def test_forced_actor_cannot_pass_but_can_return_to_trump(self):
        trace = trace_of((0,'n','1C',{'axiom_tags':['forcing']}))
        allowed, report = self.check('1CP', trace, [candidate('P','signoff'), candidate('1N','signoff')])
        self.assertEqual([c.call for c in allowed], ['1N'])
        self.assertIn('forcing', [o['kind'] for o in report['obligations']])
        self.assertTrue(report['errors'])
        allowed, _ = self.check('1C1D', trace, [candidate('P','signoff')])
        self.assertTrue(allowed)

    def test_forcing_pass_after_interference_is_relayed_to_partner(self):
        trace = trace_of((2,'s','P',{'axiom_tags':['forcing']}))
        allowed, _ = self.check('1C1DPP', trace, [candidate('P','signoff')])
        self.assertFalse(allowed)

    def test_game_force_is_side_scoped_and_not_satisfied_by_artificial_game(self):
        trace = trace_of((0,'n','1C',{'axiom_tags':['game_forcing']}),
                         (4,'n','3N',{'nature_labels':['artificial'], 'axiom_tags':['forcing']}))
        allowed, _ = self.check('1CP1SP3NP', trace, [candidate('P','signoff')])
        self.assertFalse(allowed)
        allowed, _ = self.check('1C', trace_of((0,'n','1C',{'axiom_tags':['game_forcing']})), [candidate('P')])
        self.assertTrue(allowed)  # E/W has no N/S obligation.

    def test_four_minor_exception_is_explicit_and_source_scoped(self):
        trace = trace_of((0,'n','1C',{'axiom_tags':['game_forcing']}),
                         (4,'n','4C',{'nature_labels':['natural'], 'axiom_tags':['signoff']}))
        config = {'four_minor_exceptions':[{'source':'test:0', 'auction':'1CP2CP4CP', 'calls':['4C']}]}
        allowed, _ = self.check('1CP2CP4CP',trace,[candidate('P','signoff')])
        self.assertFalse(allowed)
        allowed, _ = self.check('1CP2CP4CP',trace,[candidate('P','signoff')],config)
        self.assertTrue(allowed)
        config['four_minor_exceptions'][0]['source'] = 'other'
        allowed, _ = self.check('1CP2CP4CP',trace,[candidate('P')],config)
        self.assertFalse(allowed)

    def test_invitation_accept_and_reject_use_own_public_range(self):
        for width, expected in [(1,'accept'), (2,'accept'), (3,'accept'), (5,'accept')]:
            trace = trace_of((0,'n','1C',{'hcp_range':[12 if width != 1 else 13, 12 + width if width != 1 else 14]}),
                             (2,'s','2N',{'axiom_tags':['invite']}))
            allowed, report = self.check('1CP2NP',trace,[candidate('3N','accept'),candidate('P','reject')])
            self.assertEqual([c.call for c in allowed],['3N'])
        trace = trace_of((0,'n','1C',{'hcp_range':[14,17]}),(2,'s','2N',{'axiom_tags':['invite_plus']}))
        allowed, _ = self.check('1CP2NP',trace,[candidate('3N','accept'),candidate('P','reject')])
        self.assertEqual([c.call for c in allowed],['P'])

    def test_missing_invitation_range_blocks_instead_of_inventing_pass(self):
        trace = trace_of((2,'s','2N',{'axiom_tags':['invite']}))
        allowed, report = self.check('1CP2NP',trace,[candidate('P','reject')])
        self.assertFalse(allowed)
        self.assertIn('UNKNOWN_INVITATION_RANGE',[e['code'] for e in report['errors']])

    def test_public_partner_range_controls_game_invite_and_signoff(self):
        for limits, expected in [([11,12],'game'),([9,11],'invite'),([6,8],'signoff')]:
            trace = trace_of((0,'n','1C',{'hcp_range':limits}))
            allowed, report = self.check('1CP',trace,[candidate('3N','accept',nature_labels=['natural']),
                                                     candidate('2N','invite'),candidate('P','signoff')])
            self.assertEqual(report['obligations'][-1]['kind'],expected)
            self.assertEqual(len(allowed),1)

    def test_game_forcing_route_can_supersede_hcp_invitation_when_quality_upgrades(self):
        trace = trace_of((0,'n','1N',{'hcp_range':[14,17]}))
        strong_route = candidate('4C','game_forcing',nature_labels=['artificial'])
        allowed, report = evaluate_axioms(Auction.parse('1NP'),
            Hand.parse('ST2HAQT976D53CKJ2'), trace, (strong_route,))
        self.assertEqual(report['obligations'][-1]['kind'], 'invite')
        self.assertEqual([item.call for item in allowed], ['4C'])

    def test_preparatory_transfer_defers_but_does_not_erase_strength_obligation(self):
        opening = trace_of((0, 'n', '1N', {'hcp_range': [14, 18]}))
        transfer = candidate('2D', 'directive', nature_labels=['artificial'])
        allowed, report = evaluate_axioms(Auction.parse('1NP'),
            Hand.parse('SA62HAQJT72DJ7CJ4'), opening, (transfer,))
        self.assertEqual(report['obligations'][-1]['kind'], 'game')
        self.assertEqual([item.call for item in allowed], ['2D'])

        answered = trace_of((0, 'n', '1N', {'hcp_range': [14, 18]}),
                            (2, 's', '2D', {'axiom_tags': ['directive']}),
                            (4, 'n', '2H', {'axiom_tags': ['descriptive']}))
        allowed, report = evaluate_axioms(Auction.parse('1NP2DP2HP'),
            Hand.parse('SA62HAQJT72DJ7CJ4'), answered,
            (candidate('P', 'signoff'), candidate('4H', 'signoff', nature_labels=['natural'])))
        self.assertEqual(report['obligations'][-1]['kind'], 'game')
        self.assertEqual([item.call for item in allowed], ['4H'])

    def test_unlabelled_nonterminal_calls_need_no_strength_exception_capability(self):
        opening = trace_of((0, 'n', '1N', {'hcp_range': [14, 18]}))
        candidates = [candidate('2D', nature_labels=['artificial']),
                      candidate('P', 'directive')]
        allowed, _ = evaluate_axioms(Auction.parse('1NP'),
            Hand.parse('SA62HAQJT72DJ7CJ4'), opening, candidates)
        self.assertEqual([item.call for item in allowed], ['2D'])

    def test_unlabelled_opening_needs_no_strength_action_tag(self):
        hand = Hand.parse('SAKQJHAKQDAKQCAKQ')
        allowed, _ = evaluate_axioms(Auction.parse(''), hand, AuctionTrace(),
            (candidate('1C', nature_labels=['natural']), candidate('P', 'signoff')))
        self.assertEqual([item.call for item in allowed], ['1C'])

    def test_invitation_and_signoff_strength_do_not_label_every_intermediate_call(self):
        inviting = trace_of((0, 'n', '1N', {'hcp_range': [13, 14]}))
        allowed, report = evaluate_axioms(Auction.parse('1NP'),
            Hand.parse('SA73HK82D954CKJ62'), inviting,
            (candidate('2C', nature_labels=['artificial']),
             candidate('2N', 'invite'), candidate('P', 'signoff')))
        self.assertEqual(report['obligations'][-1]['kind'], 'invite')
        self.assertEqual([item.call for item in allowed], ['2C', '2N'])

        weak = trace_of((0, 'n', '1N', {'hcp_range': [14, 17]}))
        allowed, report = evaluate_axioms(Auction.parse('1NP'),
            Hand.parse('S8765H876D876C876'), weak,
            (candidate('2C', nature_labels=['artificial']),
             candidate('2N', 'invite'), candidate('P', 'signoff')))
        self.assertEqual(report['obligations'][-1]['kind'], 'signoff')
        self.assertEqual([item.call for item in allowed], ['2C', 'P'])

    def test_existing_game_does_not_invite_again(self):
        trace = trace_of((0,'n','3N',{'hcp_range':[9,11], 'nature_labels':['natural']}))
        allowed, report = self.check('3NP',trace,[candidate('P','signoff')])
        self.assertTrue(allowed)
        self.assertFalse(report['obligations'])

    def test_current_invitation_is_consumed_after_response(self):
        trace = trace_of((0,'n','1C',{'hcp_range':[12,14]}),(2,'s','2N',{'axiom_tags':['invite']}),
                         (4,'n','3N',{'axiom_tags':['accept'], 'nature_labels':['natural']}))
        allowed, report = self.check('1CP2NP3NP',trace,[candidate('P','signoff')])
        self.assertTrue(allowed)
        self.assertFalse(report['obligations'])

    def test_range_conflict_is_reported(self):
        trace = trace_of((0,'n','1C',{'hcp_range':[12,14]}),(4,'n','2N',{'hcp_range':[18,19]}))
        allowed, report = self.check('1CP1SP2NP',trace,[candidate('P')])
        self.assertFalse(allowed)
        self.assertIn('CONFLICTING_RANGE',[e['code'] for e in report['errors']])

    def test_accepting_invitation_cannot_sign_off_below_game(self):
        trace = trace_of((0,'n','1C',{'hcp_range':[12,14]}),(2,'s','2N',{'axiom_tags':['invite']}))
        allowed, report = self.check('1CP2NP', trace, [candidate('3C','accept','signoff'), candidate('3N','accept',nature_labels=['natural'])])
        self.assertEqual([c.call for c in allowed],['3N'])

    def test_good_middle_accepts_bad_middle_rejects(self):
        trace = trace_of((0,'n','1C',{'hcp_range':[9,11]}),(2,'s','2N',{'axiom_tags':['invite']}))
        choices = (candidate('3N','accept',nature_labels=['natural']), candidate('P','reject'))
        for hand, expected in [('SAKxxxHKxxDxxCxxx','3N'),('SQJxxHQJxDQxxCQxx','P')]:
            allowed, report = evaluate_axioms(Auction.parse('1CP2NP'),Hand.parse(hand),trace,choices)
            self.assertEqual([c.call for c in allowed],[expected])

    def test_contradictory_semantic_tags_are_errors(self):
        allowed, report = self.check('1CP',AuctionTrace(),[candidate('1N','accept','reject')])
        self.assertFalse(allowed)
        self.assertIn('CONFLICTING_TAGS',[e['code'] for e in report['errors']])

    def test_malformed_settings_report_error_instead_of_crashing(self):
        for config in ({'game_hcp':[]}, {'quality':{'unknown':1}}, {'four_minor_exceptions':[{}]}):
            allowed,report=self.check('1CP',AuctionTrace(),[candidate('P')],config)
            self.assertFalse(allowed)
            self.assertEqual(report['errors'][0]['code'],'INVALID_AXIOM_CONFIGURATION')

    def test_own_strength_can_guarantee_game_without_partner_range(self):
        hand=Hand.parse('SAKQJHAKQDAKQCAKQ')
        allowed,report=evaluate_axioms(Auction.parse('1CP'),hand,AuctionTrace(),(candidate('P','signoff'),candidate('3N',nature_labels=['natural'])))
        self.assertEqual([c.call for c in allowed],['3N'])

    def test_game_goal_cannot_pass_opening_turn_to_partner(self):
        hand=Hand.parse('SAKQJHAKQDAKQCAKQ')
        allowed,report=evaluate_axioms(Auction.parse(''),hand,AuctionTrace(),(candidate('P','signoff'),candidate('2C','forcing')))
        self.assertEqual([c.call for c in allowed],['2C'])

    def test_replay_diagnoses_forcing_pass_after_rho_pass(self):
        trace=trace_of((2,'s','P',{'axiom_tags':['forcing']}))
        allowed,report=self.check('1CPP1D',trace,[candidate('P')])
        self.assertFalse(allowed)
        self.assertIn('INVALID_PRIOR_PASS',[e['code'] for e in report['errors']])


if __name__ == '__main__':
    unittest.main()
