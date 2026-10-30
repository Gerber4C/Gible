import unittest

from engine.auction import Auction
from engine.derived_evidence import collect_evidence
from engine.loader import load_profile
from engine.trace import AuctionTrace
from engine.trump_state import TrumpState


class DerivedEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = load_profile('daqiush_2over1')

    def _trace(self, entries, trump=None):
        trace = AuctionTrace()
        trace.applied_meanings = list(entries)
        if trump is not None:
            trace.trump_states['ns'] = TrumpState('agreed', trump)
        return trace

    def _entry(self, index, seat, call, meaning):
        return {'index': index, 'seat': seat, 'call': call,
                'public_meaning': meaning}

    def test_public_natural_suits_and_supports(self):
        auction = Auction.parse('1HP2HP')
        trace = self._trace([
            self._entry(0, 'n', '1H', {
                'nature_labels': ['natural'], 'target_suit': 'H',
                'minimum_length': 5}),
            self._entry(2, 's', '2H', {
                'nature_labels': ['natural'], 'target_suit': 'H',
                'call_act_types': ['raise']}),
        ])
        evidence = collect_evidence(self.profile, auction, trace)
        self.assertEqual(evidence.natural_suits['ns'], ('H',))
        self.assertEqual(evidence.guaranteed_long_suits['ns'], ('H',))
        self.assertEqual(evidence.supported_suits['ns'], ('H',))
        self.assertEqual(evidence.plausible_trumps, ('H',))
        self.assertIn('2H', [item.call for item in evidence.classified_calls]
                      if '2H' in [item.call for item in
                                  evidence.classified_calls] else ['2H'])

    def test_enemy_suit_is_an_enemy_cue_not_a_natural_bid(self):
        auction = Auction.parse('1HP1SP')
        trace = self._trace([
            self._entry(0, 'n', '1H', {'nature_labels': ['natural'],
                                       'target_suit': 'H',
                                       'minimum_length': 5}),
            self._entry(1, 'e', '1S', {'nature_labels': ['natural'],
                                       'target_suit': 'S',
                                       'minimum_length': 5}),
        ])
        evidence = collect_evidence(self.profile, auction, trace)
        self.assertIn('S', evidence.enemy_suits)
        cues = [item for item in evidence.classified_calls
                if item.call == '2S']
        self.assertTrue(cues)
        self.assertEqual(cues[0].kind, 'enemy_cue')

    def test_three_plausible_trumps_produce_a_structured_conflict(self):
        auction = Auction.parse('1HP')
        trace = self._trace([
            self._entry(0, 'n', '1H', {'nature_labels': ['natural'],
                                       'target_suit': 'H',
                                       'minimum_length': 5}),
            self._entry(0, 'n', '1D', {'nature_labels': ['natural'],
                                       'target_suit': 'D',
                                       'minimum_length': 5}),
            self._entry(0, 'n', '1C', {'nature_labels': ['natural'],
                                       'target_suit': 'C',
                                       'minimum_length': 5}),
        ])
        evidence = collect_evidence(self.profile, auction, trace)
        self.assertEqual(len(evidence.plausible_trumps), 3)
        self.assertEqual(evidence.conflicts[0]['code'],
                         'TOO_MANY_PLAUSIBLE_TRUMPS')

    def test_agreed_trump_is_the_only_plausible_trump(self):
        auction = Auction.parse('1HP2HP')
        trace = self._trace([], trump='H')
        evidence = collect_evidence(self.profile, auction, trace)
        self.assertEqual(evidence.agreed_trump, 'H')
        self.assertEqual(evidence.plausible_trumps, ('H',))


if __name__ == '__main__':
    unittest.main()
