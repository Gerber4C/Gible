import unittest

from engine.auction import Auction
from engine.derived_evidence import DerivedEvidence
from engine.derived_fit_calls import derive
from engine.trace import AuctionTrace


def evidence(**overrides):
    values = dict(
        actor='n', side='ns', contract='3H', contract_level=3,
        contract_strain='H', agreed_trump='H', provisional_trump=None,
        plausible_trumps=('H',), forcing=True,
        three_notrump_available=True, enemy_suits=(), classified_calls=())
    values.update(overrides)
    return DerivedEvidence(**values)


def serious_trace(call, trump):
    trace = AuctionTrace()
    trace.applied_meanings = [{
        'index': 0, 'seat': 's', 'call': call,
        'public_meaning': {
            'action_type': 'derived_serious_relay',
            'agreed_suit': trump,
            'target_suit': trump,
        },
    }]
    return trace


class MajorFitTests(unittest.TestCase):
    def test_hearts_use_three_spades_as_the_serious_relay(self):
        result = derive(None, Auction.parse('3HP'), None,
                        evidence(), {'3S', '3NT', '4C', '4D'})
        calls = {c.call: c for c in result.candidates}
        self.assertEqual(calls['3S'].public_meaning['action_type'],
                         'derived_serious_relay')
        self.assertEqual(calls['3NT'].public_meaning['control_suit'], 'S')
        self.assertIn('control_showing',
                      calls['4C'].public_meaning['call_act_types'])

    def test_hearts_keep_three_spades_when_three_notrump_is_reserved(self):
        result = derive(None, Auction.parse('3HP'), None,
                        evidence(), {'3S', '4C'})
        calls = {c.call: c for c in result.candidates}
        self.assertEqual(calls['3S'].public_meaning['action_type'],
                         'derived_serious_relay')

    def test_spades_use_the_same_algorithm(self):
        result = derive(None, Auction.parse('3SP'), None,
                        evidence(agreed_trump='S', plausible_trumps=('S',),
                                 contract='3S', contract_strain='S'),
                        {'3NT', '4C', '4D'})
        calls = {c.call: c for c in result.candidates}
        self.assertEqual(calls['3NT'].public_meaning['action_type'],
                         'derived_serious_relay')
        self.assertEqual(calls['4D'].public_meaning['control_suit'], 'D')

    def test_serious_relay_forces_cues_below_game(self):
        hearts = derive(None, Auction.parse('3SP'), serious_trace('3S', 'H'),
                        evidence(contract='3S', contract_strain='S'),
                        {'3NT', '4C', '4D', '4H'})
        calls = {c.call: c for c in hearts.candidates}
        self.assertEqual(calls['3NT'].public_meaning['control_suit'], 'S')
        self.assertEqual(calls['4C'].public_meaning['control_suit'], 'C')
        self.assertEqual(calls['4H'].public_meaning['action_type'],
                         'derived_serious_response_game')

        spades = derive(None, Auction.parse('3NP'), serious_trace('3NT', 'S'),
                        evidence(agreed_trump='S', plausible_trumps=('S',),
                                 contract='3N', contract_strain='NT'),
                        {'4C', '4D', '4H', '4S'})
        calls = {c.call: c for c in spades.candidates}
        self.assertEqual(calls['4H'].public_meaning['control_suit'], 'H')
        self.assertEqual(calls['4S'].public_meaning['action_type'],
                         'derived_serious_response_game')

    def test_cue_does_not_promise_control_when_used_as_a_selector(self):
        result = derive(None, Auction.parse('3HP'), None,
                        evidence(), {'4C'})
        meaning = result.candidates[0].public_meaning
        self.assertIn('control_showing', meaning['call_act_types'])


class MinorFitTests(unittest.TestCase):
    def test_live_three_notrump_turns_enemy_suit_into_a_stopper_inquiry(self):
        result = derive(None, Auction.parse('3CP'), None,
                        evidence(agreed_trump='C', contract='3C',
                                 contract_strain='C', enemy_suits=('S',),
                                 plausible_trumps=('C',)),
                        {'3S'})
        self.assertEqual(result.candidates[0].public_meaning['action_type'],
                         'derived_minor_stopper_inquiry')

    def test_no_three_notrump_space_turns_new_suit_into_a_control_cue(self):
        result = derive(None, Auction.parse('3CP'), None,
                        evidence(agreed_trump='C', contract='3C',
                                 contract_strain='C',
                                 plausible_trumps=('C',),
                                 three_notrump_available=False),
                        {'3D'})
        self.assertEqual(result.candidates[0].public_meaning['action_type'],
                         'derived_minor_control_cue')


if __name__ == '__main__':
    unittest.main()
