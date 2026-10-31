import unittest

from engine.auction import Auction
from engine.cards import Hand
from engine.loader import load_profile
from engine.memory import Purpose, SeatMemory
from engine.purpose_axiom import resolve_purpose
from engine.selector import choose_bid
from engine.trace import AuctionTrace, StateRecord


class PurposeAxiomTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = load_profile('daqiush_2over1')

    def choose(self, auction, hand, purpose):
        return choose_bid(self.profile, Auction.parse(auction), Hand.parse(hand),
                          private_memory={'purposes': [purpose]})

    def test_game_only_texas_plan_follows_both_opener_replies(self):
        purpose = {'kind': 'response_plan', 'owner': 's', 'source_index': 2,
                   'source_call': '4C', 'trump': 'H', 'status': 'active',
                   'responses': {'4D': '4H', '4H': 'P'}}
        hand = 'ST2HAQT976D53CKJ2'
        self.assertEqual(self.choose('1NP4CP4HP', hand, purpose).call, 'P')
        self.assertEqual(self.choose('1NP4CP4DP', hand, purpose).call, '4H')

    def test_explicit_terminal_purpose_produces_global_pass(self):
        from engine.model import Author, Gadget, PartnershipProfile
        author = Author('test')
        gadget = Gadget.from_parts({'id': 'terminal', 'namespace': 'test',
                                    'name': 'Terminal', 'author': {'name': 'test'}}, [{
            'id': 'place', 'context': {'auction_pattern': ''}, 'call': '1C',
            'meaning': {'nature_labels': ['natural'], 'call_act_types': ['final_placement'],
                        'purpose_completed': True},
        }])
        profile = PartnershipProfile('terminal', 'Terminal', '0.1', author, (gadget,),
                                     missing_call_behavior='block')
        hand = Hand.parse('SA2HKQ876D432CA32')
        self.assertEqual(choose_bid(profile, Auction.parse('1CP'), hand).call, 'P')
        self.assertIsNone(choose_bid(profile, Auction.parse('1C1D'), hand).call)

    def test_enemy_bid_disrupts_saved_game_only_plan(self):
        purpose = {'kind': 'response_plan', 'owner': 's', 'source_index': 2,
                   'source_call': '4C', 'trump': 'H', 'status': 'active',
                   'responses': {'4D': '4H', '4H': 'P'}}
        decision = self.choose('1NP4C4D4HP', 'ST2HAQT976D53CKJ2', purpose)
        self.assertEqual(decision.call, '4N')
        self.assertEqual(decision.private_memory.purposes[0].status, 'disrupted')

    def test_selected_keycard_ask_saves_private_slam_purpose(self):
        hand = Hand.parse('SAKJHKQ8DA762C954')
        decision = choose_bid(self.profile, Auction.parse('1NP2DP2HP4CP'), hand)
        self.assertEqual(decision.call, '4N')
        self.assertEqual(decision.private_memory.purposes[0].kind, 'keycard_slam')
        self.assertEqual(decision.private_memory.purposes[0].trump, 'H')
        self.assertEqual(decision.private_memory.purposes[0].own_keycards,
                         hand.keycard_count('H'))
        continuation = choose_bid(self.profile, Auction.parse('1NP2DP2HP4CP4NP5CP'),
                                  hand, private_memory=decision.private_memory.to_dict())
        self.assertEqual(continuation.call, '6H')
        self.assertEqual(continuation.private_memory.purposes[0].status, 'completed')

    def test_keycard_plan_signs_off_when_two_keycards_are_missing(self):
        purpose = {'kind': 'keycard_slam', 'owner': 's', 'source_index': 6,
                   'source_call': '4N', 'trump': 'H', 'own_keycards': 2,
                   'owns_trump_queen': False, 'status': 'active'}
        decision = self.choose('1NP4CP4HP4NP5CP', 'SA2HAJ9876D432CK2', purpose)
        self.assertEqual(decision.call, '5H')

    def test_keycard_plan_bids_slam_when_all_keycards_are_present(self):
        purpose = {'kind': 'keycard_slam', 'owner': 's', 'source_index': 6,
                   'source_call': '4N', 'trump': 'H', 'own_keycards': 4,
                   'owns_trump_queen': True, 'status': 'active'}
        decision = self.choose('1NP4CP4HP4NP5CP', 'SA2HAKQ976DA32C42', purpose)
        self.assertEqual(decision.call, '6H')

    def test_keycard_plan_places_seven_with_a_grand_candidate(self):
        purpose = {'kind': 'keycard_slam', 'owner': 's', 'source_index': 6,
                   'source_call': '4N', 'trump': 'H', 'own_keycards': 4,
                   'owns_trump_queen': True, 'grand_candidate': True,
                   'combined_min': 37, 'status': 'active'}
        decision = self.choose('1NP4CP4HP4NP5CP', 'SA2HAKQ976DA32C42', purpose)
        self.assertEqual(decision.call, '7H')

    def test_five_spades_after_five_diamonds_is_the_queen_ask(self):
        purpose = {'kind': 'keycard_slam', 'owner': 's', 'source_index': 6,
                   'source_call': '4N', 'trump': 'H', 'own_keycards': 4,
                   'owns_trump_queen': False, 'status': 'active'}
        decision = self.choose('1NP4CP4HP4NP5DP', 'SA2HAKJ976DA32C42', purpose)
        self.assertEqual(decision.call, '5S')
        self.assertEqual(decision.private_memory.purposes[0].status, 'active')

    def test_zero_or_three_answer_uses_sampling_when_counts_are_ambiguous(self):
        from unittest.mock import patch
        from engine.rkcb_simulation import AmbiguousDecision
        purpose = {'kind': 'keycard_slam', 'owner': 's', 'source_index': 6,
                   'source_call': '4N', 'trump': 'H', 'own_keycards': 2,
                   'owns_trump_queen': False, 'status': 'active'}
        with patch('engine.purpose_axiom.compare_ambiguous_continuations',
                   return_value=AmbiguousDecision('6H', 'test mixture')):
            sampled = self.choose('1NP4CP4HP4NP5DP',
                                  'SA2HAJ9876D432C42', purpose)
        self.assertEqual(sampled.call, '6H')
        purpose['own_keycards'] = 3
        deterministic = self.choose('1NP4CP4HP4NP5DP',
                                    'SA2HKJ9876DA32C42', purpose)
        self.assertEqual(deterministic.call, '5H')

    def test_ambiguous_answer_tds_when_sampling_is_unavailable(self):
        from unittest.mock import patch
        from engine.rkcb_simulation import AmbiguousDecision
        purpose = {'kind': 'keycard_slam', 'owner': 's', 'source_index': 6,
                   'source_call': '4N', 'trump': 'H', 'own_keycards': 2,
                   'owns_trump_queen': False, 'status': 'active'}
        with patch('engine.purpose_axiom.compare_ambiguous_continuations',
                   return_value=AmbiguousDecision(
                       None, 'test unavailable', unavailable=True)):
            decision = self.choose(
                '1NP4CP4HP4NP5DP', 'SA2HAJ9876D432C42', purpose)
        self.assertIsNone(decision.call)
        self.assertTrue(any('ambiguous' in item.lower()
                            for item in decision.trace.diagnostics))

    def test_five_heart_answer_stop_is_a_pass_not_a_rescue_relay(self):
        hand = 'SKQHA98765DKQJCQJ'
        base = {'kind': 'keycard_slam', 'owner': 's', 'source_index': 6,
                'source_call': '4N', 'trump': 'H',
                'owns_trump_queen': False, 'status': 'active'}
        for own, expected in ((1, 'P'), (2, 'P'), (3, '6H')):
            with self.subTest(own_keycards=own):
                purpose = dict(base, own_keycards=own)
                decision = self.choose(
                    '1NP4CP4HP4NP5HP', hand, purpose)
                self.assertEqual(decision.call, expected)

    def test_queen_ask_is_authored_but_its_answer_table_is_not(self):
        purpose = {'kind': 'keycard_slam', 'owner': 's', 'source_index': 6,
                   'source_call': '4N', 'trump': 'H', 'own_keycards': 3,
                   'owns_trump_queen': False, 'status': 'active'}
        decision = self.choose('1NP4CP4HP4NP5CP', 'SA2HAJ9876DA32CK2', purpose)
        self.assertEqual(decision.call, '5D')
        self.assertEqual(decision.private_memory.purposes[0].status, 'active')
        continuation = choose_bid(
            self.profile, Auction.parse('1NP4CP4HP4NP5CP5DPPP'),
            Hand.parse('SA2HAJ9876DA32CK2'),
            private_memory=decision.private_memory.to_dict())
        self.assertIsNone(continuation.call)
        self.assertTrue(any('QUEEN_ASK_CONTINUATION_UNAUTHORED' in item
                            for item in continuation.trace.diagnostics))

    def test_keycard_plan_uses_public_answer_not_partner_cards(self):
        purpose = {'kind': 'keycard_slam', 'owner': 's', 'source_index': 6,
                   'source_call': '4N', 'trump': 'H', 'own_keycards': 4,
                   'owns_trump_queen': True, 'status': 'active'}
        auction = Auction.parse('1NP4CP4HP4NP5CP')
        calls = [choose_bid(self.profile, auction, Hand.parse('SA2HAKQ976DA32C42'),
                            environment={'partner_hand': other},
                            private_memory={'purposes': [purpose]}).call
                 for other in ('S987H543D9876CK87', 'S987H543D9876CA87')]
        self.assertEqual(calls, ['6H', '6H'])

    def test_new_rkcb_purpose_fields_round_trip_with_legacy_defaults(self):
        purpose = Purpose(
            kind='keycard_slam', owner='s', source_index=6,
            source_call='4N', trump='H', own_keycards=3,
            owns_trump_queen=True,
            rkcb_stage='await_relay_completion',
            relay_intent='show_lowest_king',
            answer_category='0/2/4/void',
            not_required_kings=('C', 'D'))
        self.assertEqual(Purpose.from_dict(purpose.to_dict()), purpose)
        legacy = Purpose.from_dict({
            'kind': 'keycard_slam', 'owner': 's', 'source_index': 6,
            'source_call': '4N', 'trump': 'H', 'own_keycards': 3,
            'owns_trump_queen': True})
        self.assertIsNone(legacy.rkcb_stage)
        self.assertIsNone(legacy.relay_intent)
        self.assertEqual(legacy.not_required_kings, ())

    def test_terminal_keycard_placement_replaces_the_purpose_once(self):
        hand = Hand.parse('SAKJHKQ8DA762C954')
        decision = choose_bid(self.profile, Auction.parse('1NP2DP2HP4CP'), hand)
        self.assertEqual(decision.call, '4N')
        continuation = choose_bid(
            self.profile, Auction.parse('1NP2DP2HP4CP4NP5CP'), hand,
            private_memory=decision.private_memory.to_dict())
        self.assertEqual(continuation.call, '6H')
        self.assertEqual(len(continuation.private_memory.purposes), 1)
        saved = continuation.private_memory.purposes[0]
        self.assertEqual((saved.status, saved.rkcb_stage),
                         ('completed', 'choose_continuation'))

    def test_queen_ask_keeps_the_purpose_active_for_the_next_turn(self):
        purpose = {'kind': 'keycard_slam', 'owner': 's', 'source_index': 6,
                   'source_call': '4N', 'trump': 'H', 'own_keycards': 3,
                   'owns_trump_queen': False, 'status': 'active'}
        decision = self.choose('1NP4CP4HP4NP5CP', 'SA2HAJ9876DA32CK2', purpose)
        self.assertEqual(decision.call, '5D')
        self.assertEqual(len(decision.private_memory.purposes), 1)
        saved = decision.private_memory.purposes[0]
        self.assertEqual((saved.status, saved.rkcb_stage),
                         ('active', 'choose_continuation'))

    def _relay_trace(self, status='relay_completed'):
        trace = AuctionTrace()
        trace.add_state(StateRecord('keycard_context', {
            'method': 'rkcb_1430', 'status': status,
            'trump_suit': 'H', 'answer_category': '0/2/4/void',
            'keycard_counts': [0, 2, 4]}, {}))
        return trace

    def _relay_purpose(self, intent):
        return Purpose(kind='keycard_slam', owner='s', source_index=6,
                       source_call='4N', trump='H', own_keycards=3,
                       owns_trump_queen=True, status='active',
                       rkcb_stage='await_relay_completion',
                       relay_intent=intent)

    def test_rescue_relay_passes_after_the_forced_five_notrump(self):
        auction = Auction.parse('1NP4CP4HP4NP5CP5SP5NP')
        purpose = self._relay_purpose('rescue')
        result = resolve_purpose(auction, self._relay_trace(),
                                 SeatMemory(purposes=(purpose,)),
                                 Hand.parse('SA2HKQ976D432CK42'))
        self.assertIsNone(result.error)
        self.assertEqual(result.candidate.call, 'P')
        self.assertEqual(result.purpose.status, 'completed')
        self.assertEqual(result.purpose.rkcb_stage, 'place_after_5nt')
        self.assertEqual(len(result.memory.purposes), 1)

    def test_grand_relay_shows_the_lowest_legal_side_king(self):
        auction = Auction.parse('1NP4CP4HP4NP5CP5SP5NP')
        purpose = self._relay_purpose('show_lowest_king')
        result = resolve_purpose(auction, self._relay_trace(),
                                 SeatMemory(purposes=(purpose,)),
                                 Hand.parse('SA2HKQ976D432CK42'))
        self.assertIsNone(result.error)
        self.assertEqual(result.candidate.call, '6C')
        self.assertEqual(result.purpose.status, 'completed')

    def test_relay_completion_is_required_after_the_relay(self):
        auction = Auction.parse('1NP4CP4HP4NP5CP5SP5NP')
        purpose = self._relay_purpose('rescue')
        result = resolve_purpose(auction, self._relay_trace('relay_pending'),
                                 SeatMemory(purposes=(purpose,)),
                                 Hand.parse('SA2HKQ976D432CK42'))
        self.assertIsNone(result.candidate)
        self.assertIn('not completed', result.error)
        self.assertEqual(result.purpose.status, 'active')

    def test_five_heart_answer_with_two_missing_keycards_stops(self):
        purpose = {'kind': 'keycard_slam', 'owner': 's', 'source_index': 6,
                   'source_call': '4N', 'trump': 'H', 'own_keycards': 0,
                   'owns_trump_queen': False, 'status': 'active'}
        decision = self.choose(
            '1NP4CP4HP4NP5HP', 'S32HQ98765D432C32', purpose)
        self.assertEqual(decision.call, 'P')
        self.assertEqual(decision.private_memory.purposes[0].status,
                         'completed')

    def test_purpose_selects_an_authored_continuation_and_keeps_its_meaning(self):
        from engine.model import Author, Gadget, PartnershipProfile
        author = Author('test')
        gadget = Gadget.from_parts(
            {'id': 'continuation', 'namespace': 'test',
             'name': 'Continuation', 'author': {'name': 'test'}},
            [{'id': 'answer_five_clubs', 'context': {'auction_pattern': '*'},
              'call': '5C',
              'meaning': {'call_act_types': ['keycard_answer'],
                          'keycard_counts': [1, 4]}},
             {'id': 'authored_heart_place', 'context': {'auction_pattern': '*'},
              'call': '6H',
              'meaning': {'nature_labels': ['natural'],
                          'call_act_types': ['final_placement'],
                          'action_type': 'authored_heart_place'}}])
        profile = PartnershipProfile('continuation', 'Continuation', '0.1',
                                     author, (gadget,),
                                     missing_call_behavior='block')
        purpose = {'kind': 'keycard_slam', 'owner': 's', 'source_index': 6,
                   'source_call': '4N', 'trump': 'H', 'own_keycards': 4,
                   'owns_trump_queen': True, 'status': 'active'}
        decision = choose_bid(
            profile, Auction.parse('1NP4CP4HP4NP5CP'),
            Hand.parse('SA2HAKQ976DA32C42'),
            private_memory={'purposes': [purpose]})
        self.assertEqual(decision.call, '6H')
        self.assertEqual(
            decision.selected_candidate.public_meaning['action_type'],
            'authored_heart_place')
        self.assertEqual(
            decision.selected_candidate.origin['object_id'],
            'authored_heart_place')

    def test_mutually_exclusive_same_call_requirements_avoid_replay_ambiguity(self):
        from engine.model import Author, Gadget, PartnershipProfile
        from engine.replay import replay_auction
        author = Author('test')

        def requires_agreed(suit):
            return {'expr': {'op': 'state_exists',
                             'query': {'key': 'agreed_suit', 'suit': suit}}}

        gadget = Gadget.from_parts(
            {'id': 'same_call', 'namespace': 'test',
             'name': 'Same call', 'author': {'name': 'test'}},
            [
                {'id': 'agree_hearts', 'context': {'auction_pattern': ''},
                 'call': '1H',
                 'meaning': {'nature_labels': ['natural'], 'target_suit': 'H'},
                 'effects': [{'key': 'agreed_suit', 'suit': 'H'}]},
                {'id': 'heart_relay', 'context': {'auction_pattern': '*'},
                 'call': '5S', 'requires': requires_agreed('H'),
                 'meaning': {'action_type': 'heart_relay'}},
                {'id': 'spade_relay', 'context': {'auction_pattern': '*'},
                 'call': '5S', 'requires': requires_agreed('S'),
                 'meaning': {'action_type': 'spade_relay'}},
            ])
        profile = PartnershipProfile('same_call', 'Same call', '0.1', author,
                                     (gadget,), missing_call_behavior='block')
        trace = replay_auction(profile, Auction.parse('1HP5S'))
        entries = [entry for entry in trace.applied_meanings
                   if entry['call'] == '5S']
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]['public_meaning']['action_type'],
                         'heart_relay')
        self.assertFalse(any('Ambiguous prior call 5S' in item
                             for item in trace.diagnostics))

    def test_keycard_plan_does_not_override_enemy_interference(self):
        purpose = {'kind': 'keycard_slam', 'owner': 's', 'source_index': 6,
                   'source_call': '4N', 'trump': 'H', 'own_keycards': 4,
                   'owns_trump_queen': True, 'status': 'active'}
        decision = self.choose('1NP4CP4HP4N5C5D5H',
                               'SA2HAKQ976DA32C42', purpose)
        self.assertIsNone(decision.call)
        self.assertEqual(decision.private_memory.purposes[0].status, 'disrupted')

    def test_keycard_ask_is_not_retriggered_by_quantitative_four_notrump(self):
        from engine.context import CallCandidate
        from engine.memory import SeatMemory
        from engine.purpose_axiom import remember_selected_purpose
        candidate = CallCandidate('4N', {'qualified_id': 'test'},
                                  {'call_act_types': ['quantitative_invite'], 'target_suit': 'N'},
                                  'test', 'test', 0, ())
        memory = remember_selected_purpose(SeatMemory(), Auction.parse('1NP'),
                                           Hand.parse('SA2HAKQ976DA32C42'), candidate)
        self.assertEqual(memory.purposes, ())

    def test_keycard_ask_without_explicit_trump_leaves_existing_route_alone(self):
        from engine.context import CallCandidate
        from engine.memory import SeatMemory
        from engine.purpose_axiom import remember_selected_purpose

        candidate = CallCandidate('4N', {'qualified_id': 'legacy'},
                                  {'call_act_types': ['keycard_asking']},
                                  'test', 'test', 0, ())
        memory = remember_selected_purpose(SeatMemory(), Auction.parse('1SP2SP'),
                                           Hand.parse('SA2HAKQ976DA32C42'), candidate)
        self.assertEqual(memory.purposes, ())

    def test_profile_can_attach_private_plan_without_revealing_it_as_call_meaning(self):
        from engine.model import Author, Gadget, PartnershipProfile
        author = Author('test')
        gadget = Gadget.from_parts({'id': 'plan', 'namespace': 'test',
                                    'name': 'Plan', 'author': {'name': 'test'}}, [{
            'id': 'start', 'context': {'auction_pattern': ''}, 'call': '1C',
            'meaning': {'nature_labels': ['natural']},
            'private_purpose': lambda ctx: {
                'kind': 'response_plan', 'trump': 'H',
                'responses': {'4D': '4H', '4H': 'P'}},
        }])
        profile = PartnershipProfile('test', 'Test', '0.1', author, (gadget,),
                                     missing_call_behavior='block')
        selected = choose_bid(profile, Auction.parse(''),
                              Hand.parse('ST2HAQT976D53CKJ2'))
        self.assertEqual(selected.call, '1C')
        self.assertEqual(selected.private_memory.purposes[0].responses,
                         {'4D': '4H', '4H': 'P'})
        self.assertNotIn('private_purpose', selected.selected_candidate.public_meaning)

    def test_invalid_static_purpose_is_reported_as_axiom_definition_error(self):
        from engine.axiom_validation import AxiomDefinitionError, validate_profile_axioms
        from engine.model import Author, Gadget, PartnershipProfile

        author = Author('test')
        gadget = Gadget.from_parts({'id': 'invalid_plan', 'namespace': 'test',
                                    'name': 'Invalid plan', 'author': {'name': 'test'}}, [{
            'id': 'start', 'context': {'auction_pattern': ''}, 'call': '1C',
            'meaning': {},
            'private_purpose': {'kind': 'response_plan', 'trump': 'H',
                                'responses': {'NOT_A_CALL': '4H'}},
        }])
        profile = PartnershipProfile('test', 'Test', '0.1', author, (gadget,))
        # Invalid call notation must fail while the profile is loaded, before bidding.
        with self.assertRaises(AxiomDefinitionError) as raised:
            validate_profile_axioms(profile)
        self.assertEqual(raised.exception.errors[0]['code'], 'INVALID_PURPOSE')

    def test_high_answer_purpose_passes_when_the_grand_is_impossible(self):
        purpose = {'kind': 'keycard_slam', 'owner': 's', 'source_index': 6,
                   'source_call': '4N', 'trump': 'H', 'own_keycards': 4,
                   'owns_trump_queen': True, 'grand_candidate': True,
                   'status': 'active'}
        decision = self.choose('1NP4CP4HP4NP5NP',
                               'SA2HAKQ976DA32C42', purpose)
        self.assertEqual(decision.call, 'P')
        self.assertEqual(decision.private_memory.purposes[0].status,
                         'completed')

    def test_high_answer_purpose_invites_grand_when_all_keycards_are_possible(self):
        purpose = {'kind': 'keycard_slam', 'owner': 's', 'source_index': 6,
                   'source_call': '4N', 'trump': 'H', 'own_keycards': 1,
                   'owns_trump_queen': True, 'grand_candidate': True,
                   'status': 'active'}
        decision = self.choose('1NP4CP4HP4NP5NP',
                               'S32HKQ97654D432C2', purpose)
        self.assertEqual(decision.call, '6C')
        saved = decision.private_memory.purposes[0]
        self.assertEqual((saved.status, saved.rkcb_stage),
                         ('active', 'choose_continuation'))

    def test_grand_responder_rejects_or_counterinvites_without_a_private_purpose(self):
        invite = Auction.parse('1NP4CP4HP4NP5NP6CP')
        rejected = choose_bid(self.profile, invite,
                              Hand.parse('SAQ2HQJ976DQJ2CQJ'))
        self.assertEqual(rejected.call, '6H')
        countered = choose_bid(self.profile, invite,
                               Hand.parse('SAQ2HQJ976DKQ2CQJ'))
        self.assertEqual(countered.call, '6D')

    def test_asker_chooses_after_the_single_counterinvitation(self):
        from unittest.mock import patch
        from engine.rkcb_simulation import GrandDecision
        purpose = {'kind': 'keycard_slam', 'owner': 's', 'source_index': 6,
                   'source_call': '4N', 'trump': 'H', 'own_keycards': 1,
                   'owns_trump_queen': True, 'grand_candidate': True,
                   'status': 'active', 'rkcb_stage': 'choose_continuation',
                   'answer_category': '0/2/4/void'}
        auction = Auction.parse('1NP4CP4HP4NP5NP6CP6DP')
        with patch('engine.purpose_axiom.compare_grand_routes',
                   return_value=GrandDecision('7H', 'test')):
            decision = self.choose(
                '1NP4CP4HP4NP5NP6CP6DP', 'S32HKQ97654D432C2', purpose)
        self.assertEqual(decision.call, '7H')
        self.assertEqual(decision.private_memory.purposes[0].status,
                         'completed')


if __name__ == '__main__':
    unittest.main()
