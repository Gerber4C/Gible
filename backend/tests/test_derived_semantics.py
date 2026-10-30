import unittest

from engine.auction import Auction
from engine.cards import Hand
from engine.derived_evidence import DerivedEvidence
from engine.derived_semantics import derived_candidate, reserved_calls
from engine.derived_terminals import derive_six_notrump, derive_terminal_pass
from engine.loader import load_profile
from engine.replay import replay_auction
from engine.trace import AuctionTrace


def evidence(**overrides):
    values = dict(
        actor='n', side='ns', contract='1N', contract_level=1,
        contract_strain='NT', agreed_trump=None, provisional_trump=None,
        plausible_trumps=(), forcing=False, three_notrump_available=True,
        supported_suits={'ns': (), 'ew': ()}, classified_calls=())
    values.update(overrides)
    return DerivedEvidence(**values)


def trace_with(hcp_min=15, seat='s', acts=('descriptive',)):
    trace = AuctionTrace()
    trace.applied_meanings = [{
        'index': 0, 'seat': seat, 'call': '1N',
        'public_meaning': {'hcp_min': hcp_min,
                           'call_act_types': list(acts),
                           'nature_labels': ['natural'],
                           'target_suit': 'N'}}]
    return trace


class SixNotrumpTests(unittest.TestCase):
    def test_33_to_35_hcp_without_a_fit_places_6nt(self):
        for hcp in (18, 19, 20):
            with self.subTest(hcp=hcp):
                hand = Hand.from_dict({'spades': 'AKQ2', 'hearts': 'K32',
                                       'diamonds': 'K432', 'clubs': '32'})
                if hand.hcp != hcp:
                    continue
                result = derive_six_notrump(
                    None, Auction.parse('1NP'), trace_with(),
                    evidence(), {'6N'}, hand)
                self.assertEqual(result.calls, ('6N',))

    def test_32_needs_a_good_five_card_suit(self):
        good = Hand.parse('SAKQJ2HK32D432C32')
        result = derive_six_notrump(
            None, Auction.parse('1NP'), trace_with(15), evidence(), {'6N'},
            good)
        self.assertEqual(result.calls, ())
        # 17 + 15 = 32 without a good five-card suit.
        flat = Hand.parse('SAKQ2HK32DQJ2C432')
        result = derive_six_notrump(
            None, Auction.parse('1NP'), trace_with(15), evidence(), {'6N'},
            flat)
        self.assertEqual(result.calls, ())

    def test_known_fit_suppresses_6nt(self):
        result = derive_six_notrump(
            None, Auction.parse('1NP'), trace_with(15),
            evidence(agreed_trump='H'), {'6N'},
            Hand.parse('SAKQ2HK32DQJ2C432'))
        self.assertEqual(result.calls, ())


class DerivedPassTests(unittest.TestCase):
    def test_pass_after_partners_natural_call(self):
        result = derive_terminal_pass(
            None, Auction.parse('1NP'), trace_with(15), evidence(), {'P'})
        self.assertEqual(result.calls, ('P',))

    def test_pass_is_not_derived_after_an_opponent_call(self):
        result = derive_terminal_pass(
            None, Auction.parse('1NP'), trace_with(15, seat='e'),
            evidence(), {'P'})
        self.assertEqual(result.calls, ())

    def test_forcing_or_pending_trump_suppresses_pass(self):
        self.assertEqual(derive_terminal_pass(
            None, Auction.parse('1NP'), trace_with(15),
            evidence(forcing=True), {'P'}).calls, ())
        self.assertEqual(derive_terminal_pass(
            None, Auction.parse('1NP'), trace_with(15),
            evidence(provisional_trump='H'), {'P'}).calls, ())

    def test_unresolved_inquiry_suppresses_pass(self):
        result = derive_terminal_pass(
            None, Auction.parse('1NP'),
            trace_with(15, acts=('inquiry',)), evidence(), {'P'})
        self.assertEqual(result.calls, ())


class ReservationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = load_profile('daqiush_2over1')

    def test_explicit_wildcard_call_is_reserved(self):
        trace = AuctionTrace()
        auction = Auction.parse('1NP')
        reserved = reserved_calls(self.profile, auction, trace)
        self.assertIn('4N', reserved)


class DispatcherIntegrationTests(unittest.TestCase):
    def _profile(self, explicit_four_notrump=False):
        from engine.model import Author, Gadget, PartnershipProfile
        specs = [
            {'id': 'open_heart', 'context': {'auction_pattern': ''},
             'call': '1H',
             'meaning': {'nature_labels': ['natural'], 'target_suit': 'H',
                         'minimum_length': 5}},
            {'id': 'raise_heart', 'context': {'auction_pattern': '1HP'},
             'call': '2H',
             'meaning': {'nature_labels': ['natural'], 'target_suit': 'H',
                         'call_act_types': ['raise']},
             'effects': [{'key': 'agreed_suit', 'suit': 'H'}]},
        ]
        if explicit_four_notrump:
            specs.append({
                'id': 'explicit_four_notrump',
                'context': {'auction_pattern': '1HP2HP'},
                'call': '4N',
                'meaning': {'nature_labels': ['artificial'],
                            'call_act_types': ['keycard_asking'],
                            'action_type': 'explicit_wins',
                            'target_suit': 'H', 'agreed_suit': 'H'}})
        gadget = Gadget.from_parts(
            {'id': 'derived_fixture', 'namespace': 'test',
             'name': 'Derived fixture', 'author': {'name': 'test'}}, specs)
        return PartnershipProfile('derived_fixture', 'Derived fixture', '0.1',
                                  Author('test'), (gadget,),
                                  missing_call_behavior='block',
                                  derived_semantics=True)

    def test_derived_keycard_four_notrump_is_selected_and_replayed(self):
        from engine.selector import choose_bid
        profile = self._profile()
        hand = Hand.parse('SAK2HKQ976D432C32')
        decision = choose_bid(profile, Auction.parse('1HP2HP'), hand)
        self.assertEqual(decision.call, '4N')
        trace = replay_auction(profile, Auction.parse('1HP2HP4NP'))
        self.assertTrue(trace.state_exists({'key': 'keycard_context',
                                            'trump_suit': 'H',
                                            'method': 'rkcb_1430'}))

    def test_explicit_four_notrump_reserves_the_call_from_derivation(self):
        from engine.derived_evidence import collect_evidence
        from engine.derived_semantics import derive_candidates, reserved_calls
        profile = self._profile(explicit_four_notrump=True)
        auction = Auction.parse('1HP2HP')
        trace = replay_auction(profile, auction)
        reserved = reserved_calls(profile, auction, trace)
        self.assertIn('4N', reserved)
        result = derive_candidates(profile, auction, trace,
                                   collect_evidence(profile, auction, trace),
                                   reserved)
        self.assertNotIn('4N', result.calls)


    def test_replay_reconstructs_fit_cue_and_terminal_pass(self):
        profile = self._profile()
        cue = replay_auction(profile, Auction.parse('1HP2HP4CP'))
        entry = next(item for item in cue.applied_meanings
                     if item['call'] == '4C')
        self.assertIn(entry['public_meaning']['action_type'],
                      ('derived_major_control_cue', 'derived_control_cue'))
        passed = replay_auction(profile, Auction.parse('1HP2HPP'))
        entry = next(item for item in passed.applied_meanings
                     if item['index'] == 4)
        self.assertEqual(entry['public_meaning']['action_type'],
                         'derived_terminal_pass')

    def test_derived_cue_is_added_beside_authored_candidates(self):
        from engine.selector import choose_bid
        profile = load_profile('daqiush_2over1')
        decision = choose_bid(
            profile, Auction.parse('1NP2SP3CP3NTP4CP'),
            Hand.parse('SQJHQJDAKQCAQJxxx'))
        rules = {item['rule']
                 for item in decision.trace.derivation['candidates']}
        self.assertIn('derive_control_cue', rules)
        self.assertEqual(decision.call, '4N')

    def test_trace_derivation_contains_no_private_cards(self):
        import json
        from engine.selector import choose_bid
        profile = self._profile()
        decision = choose_bid(profile, Auction.parse('1HP2HP'),
                              Hand.parse('SAK2HKQ976D432C32'))
        payload = json.dumps(decision.trace.derivation)
        self.assertNotIn('hand', payload.lower())
        self.assertNotIn('private', payload.lower())


if __name__ == '__main__':
    unittest.main()
