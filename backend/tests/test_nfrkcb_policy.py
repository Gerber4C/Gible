import unittest

from engine.auction import Auction
from engine.cards import Hand
from engine.derived_evidence import DerivedEvidence
from engine.derived_replay import derive_historical_call
from engine.loader import load_profile
from engine.nfrkcb_policy import decide_offer, single_suit_offer
from engine.trace import AuctionTrace, StateRecord


def evidence(partner_suits=('C',), provisional='C', side='ns'):
    return DerivedEvidence(
        actor='s', side=side, contract='4N', contract_level=4,
        contract_strain='NT', agreed_trump=None, provisional_trump=provisional,
        plausible_trumps=(provisional,) if provisional else (),
        guaranteed_long_suits={'ns': partner_suits if side == 'ns' else (),
                               'ew': partner_suits if side == 'ew' else ()})


class NFRKCBPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = load_profile('daqiush_2over1')

    def test_single_suit_offer_requires_one_guaranteed_partner_suit(self):
        self.assertEqual(single_suit_offer(evidence(('C',))), 'C')
        self.assertIsNone(single_suit_offer(evidence(('C', 'D'))))
        self.assertIsNone(single_suit_offer(evidence(('C',), provisional='D')))

    def test_weak_responder_passes_the_four_notrump_suggestion(self):
        decision = decide_offer(self.profile, Auction.parse('1NP'), None,
                                Hand.parse('S32H432D432C65432'), 'C')
        self.assertEqual(decision.call, 'P')

    def test_responder_holding_every_keycard_continues(self):
        hand = Hand.parse('SA2HAKQ97DA32CA32')
        decision = decide_offer(self.profile, Auction.parse('1NP'), None,
                                hand, 'H')
        self.assertEqual(decision.call, '5S')

    def test_unavailable_sampling_is_typed(self):
        hand = Hand.parse('SAQ2HAQ2DQJ2C5432')
        decision = decide_offer(self.profile, Auction.parse('1NP'), None,
                                hand, 'C')
        self.assertTrue(decision.unavailable)
        self.assertIsNone(decision.call)

    def _offer_trace(self):
        trace = AuctionTrace()
        trace.add_state(StateRecord('nfrkcb', {
            'method': 'nfrkcb_offer', 'trump_suit': 'C', 'offerer': 'n'}, {}))
        return trace

    def test_hand_free_replay_reconstructs_accept_and_answer(self):
        auction = Auction.parse('1NP')
        accepted = derive_historical_call(self.profile, auction, 'P',
                                          self._offer_trace())
        self.assertEqual(accepted.rule, 'nfrkcb_accept')
        self.assertEqual(accepted.public_meaning['action_type'],
                         'nfrkcb_accept')
        answered = derive_historical_call(self.profile, auction, '5C',
                                          self._offer_trace())
        self.assertEqual(answered.rule, 'nfrkcb_answer')
        self.assertEqual(answered.public_meaning['keycard_counts'], [1, 4])
        self.assertEqual(answered.effects[0]['method'], 'nfrkcb_answered')

    def test_two_suit_auction_does_not_create_an_offer(self):
        ev = evidence(('C', 'D'), provisional=None)
        self.assertIsNone(single_suit_offer(ev))


if __name__ == '__main__':
    unittest.main()
