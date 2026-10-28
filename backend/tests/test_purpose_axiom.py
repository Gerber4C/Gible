import unittest

from engine.auction import Auction
from engine.cards import Hand
from engine.loader import load_profile
from engine.selector import choose_bid


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
        self.assertIsNone(decision.call)
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

    def test_keycard_plan_assumes_queen_when_no_below_game_ask_fits(self):
        purpose = {'kind': 'keycard_slam', 'owner': 's', 'source_index': 6,
                   'source_call': '4N', 'trump': 'H', 'own_keycards': 4,
                   'owns_trump_queen': False, 'status': 'active'}
        decision = self.choose('1NP4CP4HP4NP5DP', 'SA2HAKJ976DA32C42', purpose)
        self.assertEqual(decision.call, '6H')

    def test_reviewed_zero_or_three_answer_defaults_to_three_unless_asker_has_three(self):
        for own_count, cards, expected in (
            (2, 'SA2HAJ9876D432C42', '6H'),
            (3, 'SA2HKJ9876DA32C42', '5H'),
        ):
            with self.subTest(own_count=own_count):
                purpose = {'kind': 'keycard_slam', 'owner': 's', 'source_index': 6,
                           'source_call': '4N', 'trump': 'H', 'own_keycards': own_count,
                           'owns_trump_queen': False, 'status': 'active'}
                decision = self.choose('1NP4CP4HP4NP5DP', cards, purpose)
                self.assertEqual(decision.call, expected)

    def test_keycard_plan_blocks_when_queen_ask_has_space_but_no_rule(self):
        purpose = {'kind': 'keycard_slam', 'owner': 's', 'source_index': 6,
                   'source_call': '4N', 'trump': 'H', 'own_keycards': 3,
                   'owns_trump_queen': False, 'status': 'active'}
        decision = self.choose('1NP4CP4HP4NP5CP', 'SA2HAJ9876DA32CK2', purpose)
        self.assertIsNone(decision.call)
        self.assertTrue(any('queen' in item.lower() for item in decision.trace.diagnostics))

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


if __name__ == '__main__':
    unittest.main()
